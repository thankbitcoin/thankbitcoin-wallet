# ThankBitcoin-Electrum — lightweight wallet for ThankBitcoin (TBC)

A fork of [Electrum](https://electrum.org/) adapted to the **ThankBitcoin (TBC)** chain.
It is a standard send/receive light wallet: it talks to ElectrumX servers and
**self-verifies the chain's proof of work** (the ThankBitcoin difficulty algorithm is
ported into `electrum/blockchain.py`, so headers are validated, not trusted).

> **Experimental / educational software.** ThankBitcoin is an experimental protocol
> research project. This wallet is provided as-is for study and experimentation, and
> makes **no** claims of value, price, investment, or return of any kind. Keep your own
> keys; understand what you run.

**What changed vs. upstream Electrum**
- ThankBitcoin proof-of-work difficulty algorithm ported to `blockchain.py` (real header self-verification, no testnet skip)
- Genesis hash / network parameters for the ThankBitcoin mainnet
- Currency unit shown as **TBC**; block explorer points to the ThankBitcoin explorer
- Default ElectrumX servers: `electrum.thankbitcoin.com` / `electrum2.thankbitcoin.com`
- Lightning tab hidden (this first release covers standard send/receive only)

Addresses and keys are byte-for-byte identical to Bitcoin mainnet (bech32 `bc1q…`,
same WIF/xpub, BIP44 coin type 0); the chains are separated by network magic + ports.

**Links**
- ThankBitcoin source (full node): https://github.com/thankbitcoin/thankbitcoin
- Block explorer: https://thankbitcoin.com/
- Whitepaper: https://thankbitcoin.com/whitepaper

This wallet builds on the work of the Electrum developers (Thomas Voegtlin and
contributors) under the MIT License. The original Electrum documentation follows below.

---

# Electrum - Lightweight Bitcoin client

```
Licence: MIT Licence
Author: Thomas Voegtlin
Language: Python (>= 3.10)
Homepage: https://electrum.org/
```

## Getting started

_(If you've come here looking to simply run Electrum,
[you may download it here](https://electrum.org/#download).)_

Electrum itself is pure Python, and so are most of the required dependencies,
but not everything. The following sections describe how to run from source, but here
is a TL;DR:

```
$ sudo apt-get install libsecp256k1-dev
$ ELECTRUM_ECC_DONT_COMPILE=1 python3 -m pip install --user ".[gui,crypto]"
```

### Not pure-python dependencies

#### Qt GUI

If you want to use the Qt interface, install the Qt dependencies:
```
$ sudo apt-get install python3-pyqt6
```

#### libsecp256k1

For elliptic curve operations,
[libsecp256k1](https://github.com/bitcoin-core/secp256k1)
is a required dependency.

If you "pip install" Electrum, by default libsecp will get compiled locally,
as part of the `electrum-ecc` dependency. This can be opted-out of,
by setting the `ELECTRUM_ECC_DONT_COMPILE=1` environment variable.
For the compilation to work, besides a C compiler, you need at least:
```
$ sudo apt-get install automake libtool
```
If you opt out of the compilation, you need to provide libsecp in another way, e.g.:
```
$ sudo apt-get install libsecp256k1-dev
```

#### cryptography

Due to the need for fast symmetric ciphers,
[cryptography](https://github.com/pyca/cryptography) is required.
Install from your package manager (or from pip):
```
$ sudo apt-get install python3-cryptography
```

#### hardware-wallet support

If you would like hardware wallet support,
[see this](https://github.com/spesmilo/electrum-docs/blob/master/hardware-linux.rst).


### Running from tar.gz

If you downloaded the official package (tar.gz), you can run
Electrum from its root directory without installing it on your
system; all the pure python dependencies are included in the 'packages'
directory. To run Electrum from its root directory, just do:
```
$ ./run_electrum
```

You can also install Electrum on your system, by running this command:
```
$ sudo apt-get install python3-setuptools python3-pip
$ python3 -m pip install --user .
```

This will download and install the Python dependencies used by
Electrum instead of using the 'packages' directory.
It will also place an executable named `electrum` in `~/.local/bin`,
so make sure that is on your `PATH` variable.


### Development version (git clone)

_(For OS-specific instructions, see [here for Windows](contrib/build-wine/README_windows.md),
and [for macOS](contrib/osx/README_macos.md))_

Check out the code from GitHub:
```
$ git clone https://github.com/spesmilo/electrum.git
$ cd electrum
$ git submodule update --init
```

Run install (this should install dependencies):
```
$ python3 -m pip install --user -e .
```

Create translations (optional):
```
$ sudo apt-get install gettext
$ ./contrib/locale/build_locale.sh electrum/locale/locale electrum/locale/locale
```

Finally, to start Electrum:
```
$ ./run_electrum
```

### Run tests

Run unit tests with `pytest`:
```
$ pytest tests -v
```
(can be parallelized with `-n auto` option, using [`pytest-xdist`](https://github.com/pytest-dev/pytest-xdist) plugin)

To run a single file, specify it directly like this:
```
$ pytest tests/test_bitcoin.py -v
```

## Creating Binaries

- [Linux (tarball)](contrib/build-linux/sdist/README.md)
- [Linux (AppImage)](contrib/build-linux/appimage/README.md)
- [macOS](contrib/osx/README.md)
- [Windows](contrib/build-wine/README.md)
- [Android](contrib/android/Readme.md)


## Contributing

Any help testing the software, reporting or fixing bugs, reviewing pull requests
and recent changes, writing tests, or helping with outstanding issues is very welcome.
Implementing new features, or improving/refactoring the codebase, is of course
also welcome, but to avoid wasted effort, especially for larger changes,
we encourage discussing these on the issue tracker or IRC first.

Besides [GitHub](https://github.com/spesmilo/electrum),
most communication about Electrum development happens on IRC, in the
`#electrum` channel on Libera Chat. The easiest way to participate on IRC is
with the web client, [web.libera.chat](https://web.libera.chat/#electrum).

Please improve translations on [Crowdin](https://crowdin.com/project/electrum).
