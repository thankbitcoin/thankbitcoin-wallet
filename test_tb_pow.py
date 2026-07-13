import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import electrum.blockchain as bc
from electrum.blockchain import Blockchain, MAX_TARGET, CHUNK_SIZE, POW_TARGET_TIMESPAN, EMERGENCY_GAP

# ---- Part 1: consistency against real thankbitcoind headers (heights 0..2999) ----
# We only need height/time/bits to recompute the per-block target and compare to actual bits.
# Build a fake Blockchain-like object exposing read_header + bits_to_target/target_to_bits +
# _tb_get_target (all pure). We reuse the real methods via a lightweight stub.

class HeaderStore:
    def __init__(self, rows):
        # rows: list of (height, time, bits)
        self.by_height = {h: {'block_height': h, 'timestamp': t, 'bits': b} for (h, t, b) in rows}
    def read_header(self, height):
        return self.by_height.get(height)

# bind the real methods onto the stub
HeaderStore.bits_to_target = Blockchain.bits_to_target
HeaderStore.target_to_bits = Blockchain.target_to_bits
HeaderStore._tb_get_target = Blockchain._tb_get_target

rows = []
with open('/tmp/tb_headers.txt') as f:
    for line in f:
        p = line.split()
        if len(p) != 3:
            continue
        rows.append((int(p[0]), int(p[1]), int(p[2], 16)))
rows.sort()
store = HeaderStore(rows)

fails = 0
emergency_hits = 0
termfirst_seen = 0
retarget_seen = 0
for (h, t, bits) in rows:
    if h == 0:
        continue
    prev = store.read_header(h - 1)
    target = store._tb_get_target(h, prev, t)
    computed_bits = store.target_to_bits(target)
    # track which code paths we exercised
    if h % 1000 == 0:
        termfirst_seen += 1
    if h % CHUNK_SIZE == 0:
        retarget_seen += 1
    if h % 1000 != 0 and t > prev['timestamp'] + EMERGENCY_GAP:
        emergency_hits += 1
    if computed_bits != bits:
        fails += 1
        if fails <= 10:
            print(f"  MISMATCH h={h} computed=0x{computed_bits:08x} actual=0x{bits:08x} "
                  f"gap={t-prev['timestamp']}s termfirst={h%1000==0} retarget={h%CHUNK_SIZE==0}")

print(f"Part 1 (real chain consistency, {len(rows)} headers):")
print(f"  bits mismatches: {fails}")
print(f"  emergency-gap blocks exercised: {emergency_hits}")
print(f"  term-first blocks exercised: {termfirst_seen}")
print(f"  retarget-boundary blocks exercised: {retarget_seen}")
assert fails == 0, "PER-BLOCK TARGET DOES NOT MATCH REAL CHAIN"
print("  PASS: every recomputed bits matches actual chain bits\n")

# ---- Part 2: retarget math vs pow.cpp formula (launch-truth powLimit) ----
# Emulate CalculateNextWorkRequired: base=prev bits, clamp actual to [T/4, 4T],
# new = min(powLimit, base_target * actual / T), with overflow guard.
LAUNCH_POWLIMIT = MAX_TARGET  # 0x1e27fffd on this fork
T = POW_TARGET_TIMESPAN

def expected_retarget(base_bits, actual):
    tgt = Blockchain.bits_to_target(base_bits)
    a = max(actual, T // 4); a = min(a, T * 4)
    if tgt != 0 and tgt > ((1 << 256) - 1) // a:
        return LAUNCH_POWLIMIT
    nt = min(LAUNCH_POWLIMIT, (tgt * a) // T)
    return Blockchain.bits_to_target(Blockchain.target_to_bits(nt))

# Build a synthetic store where a retarget boundary block can change difficulty.
# Use a mid-range base target (not powLimit) so "harder" is representable.
base_bits = 0x1d00ffff  # a Bitcoin-ish difficulty (target << powLimit) so retarget can move
first_ts = 1000000
# case A: blocks came in TOO FAST (actual << T) -> target should get SMALLER (harder)
prev_ts_fast = first_ts + T // 8  # way under target => clamped to T/4
# case B: blocks came in TOO SLOW (actual >> T) -> target should get BIGGER (easier), capped at powLimit
prev_ts_slow = first_ts + T * 100  # clamped to 4T

for label, prev_ts in [("fast/harder", prev_ts_fast), ("slow/easier", prev_ts_slow)]:
    h = CHUNK_SIZE  # a retarget boundary
    rows2 = {
        0: {'block_height': 0, 'timestamp': first_ts, 'bits': base_bits},
        h - CHUNK_SIZE: {'block_height': h - CHUNK_SIZE, 'timestamp': first_ts, 'bits': base_bits},
        h - 1: {'block_height': h - 1, 'timestamp': prev_ts, 'bits': base_bits},
    }
    s2 = HeaderStore([(hh, r['timestamp'], r['bits']) for hh, r in rows2.items()])
    prev = s2.read_header(h - 1)
    got = s2._tb_get_target(h, prev, prev_ts + 60)
    exp = expected_retarget(base_bits, prev_ts - first_ts)
    ok = (got == exp)
    print(f"Part 2 retarget [{label}]: got=0x{Blockchain.target_to_bits(got):08x} "
          f"exp=0x{Blockchain.target_to_bits(exp):08x} {'PASS' if ok else 'FAIL'}")
    assert ok

# ---- Part 3: overflow guard triggers at high powLimit ----
# With base target = powLimit (~2^237) and max actual (4T), product overflows 2^256.
h = CHUNK_SIZE
big_bits = 0x1e27fffd  # powLimit
s3 = HeaderStore([
    (0, 0, big_bits),
    (h - CHUNK_SIZE, 0, big_bits),
    (h - 1, T * 4, big_bits),  # actual clamps to 4T (max)
])
prev = s3.read_header(h - 1)
got = s3._tb_get_target(h, prev, T * 4 + 60)
print(f"Part 3 overflow-guard: got=0x{Blockchain.target_to_bits(got):08x} exp=0x1e27fffd "
      f"{'PASS' if got == MAX_TARGET else 'FAIL'}")
assert got == MAX_TARGET

# ---- Part 4: term-first block is EXEMPT from emergency min-difficulty ----
# A term-first block (h % 1000 == 0) with a huge gap must NOT reset to powLimit;
# it carries forward prev.bits (since h % 2016 != 0 for h=1000/2000/3000).
h = 1000
prev = {'block_height': 999, 'timestamp': 5000, 'bits': 0x1d00ffff}
got = Blockchain._tb_get_target.__get__(HeaderStore([]))(h, prev, 5000 + EMERGENCY_GAP + 99999)
exp = Blockchain.bits_to_target(0x1d00ffff)
print(f"Part 4 term-first exemption: got=0x{Blockchain.target_to_bits(got):08x} "
      f"exp=0x1d00ffff (carry-forward, NOT powLimit) {'PASS' if got == exp else 'FAIL'}")
assert got == exp, "term-first block wrongly got emergency min-difficulty"

# ---- Part 5: normal block WITH big gap DOES get emergency min-difficulty ----
h = 1500  # not term-first, not retarget boundary
prev = {'block_height': 1499, 'timestamp': 5000, 'bits': 0x1d00ffff}
got = Blockchain._tb_get_target.__get__(HeaderStore([]))(h, prev, 5000 + EMERGENCY_GAP + 1)
print(f"Part 5 emergency on normal block: got=0x{Blockchain.target_to_bits(got):08x} "
      f"exp=0x1e27fffd (powLimit) {'PASS' if got == MAX_TARGET else 'FAIL'}")
assert got == MAX_TARGET

print("\nALL POW PORT TESTS PASSED")
