# mkqr

**QR codes from the command line, without friction.** PNG, SVG, PDF, Wi-Fi, vCard, logo, clipboard.

[![CI](https://github.com/berodcdev/mkqr/actions/workflows/ci.yml/badge.svg)](https://github.com/berodcdev/mkqr/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/mkqr.svg)](https://pypi.org/project/mkqr/)
[![Python](https://img.shields.io/pypi/pyversions/mkqr.svg)](https://pypi.org/project/mkqr/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/berodcdev/mkqr/blob/main/LICENSE)

🇧🇷 [Leia em português](https://github.com/berodcdev/mkqr/blob/main/README.pt-BR.md)

<img src="https://raw.githubusercontent.com/berodcdev/mkqr/main/docs/img/demo.gif" alt="mkqr generating QR codes in a terminal" width="820">

> **Note:** mkqr's help text and messages are in Brazilian Portuguese. Flags and
> output formats are the usual English ones, so the examples below work as-is.

## Install

```sh
pipx install mkqr        # recommended: isolated, on your PATH
pip install mkqr         # or into the current environment
```

Then, optionally, enable Tab completion for your shell:

```sh
mkqr --install-completion
```

### No `pipx`?

`pipx` installs each CLI into its own virtualenv, so mkqr's dependencies never
collide with your projects. If you get `pipx: command not found`:

| | |
|---|---|
| macOS | `brew install pipx` |
| Debian / Ubuntu | `sudo apt install pipx` |
| Fedora | `sudo dnf install pipx` |
| Arch | `sudo pacman -S python-pipx` |
| openSUSE | `sudo zypper install python3-pipx` |
| anywhere else | `python3 -m pip install --user pipx` |

Then `pipx ensurepath` once, and open a new terminal — it adds `~/.local/bin`
to your `PATH`, which is where the `mkqr` command lands.

In a hurry? `pip install mkqr` needs none of this.

### Without PyPI

Straight from GitHub — same package, no PyPI involved. Useful if PyPI is
unreachable, blocked on your network, or you want the latest commit:

```sh
pipx install git+https://github.com/berodcdev/mkqr.git          # latest from main
pipx install git+https://github.com/berodcdev/mkqr.git@v0.1.1   # a specific release
```

Prebuilt wheels are attached to every
[release](https://github.com/berodcdev/mkqr/releases) if you'd rather not build
from source.

Or from a clone, which installs and wires up completion in one go:

```sh
git clone https://github.com/berodcdev/mkqr.git && cd mkqr
./install.sh              # pipx + shell completion; -e for editable mode
./uninstall.sh            # removes everything
```

On Windows without bash, `pipx install .` is enough.

## Update

```sh
pipx upgrade mkqr        # if you installed with pipx
pip install -U mkqr      # if you installed with pip
mkqr -V                  # check which version you're on
```

`pipx upgrade-all` updates mkqr along with every other tool pipx manages.

<details>
<summary>Installed from GitHub instead?</summary>

`pipx upgrade` re-resolves the original source, so it only reaches PyPI if that's
where it came from. For a GitHub install, reinstall over it:

```sh
pipx install --force git+https://github.com/berodcdev/mkqr.git
```

From a clone, pull first — `install.sh` reinstalls over whatever is there:

```sh
git pull && ./install.sh
```

If you installed from a clone and later want normal upgrades, switch the source
once with `pipx install --force mkqr`; after that `pipx upgrade mkqr` works.
</details>

Releases are listed in [CHANGELOG.md](https://github.com/berodcdev/mkqr/blob/main/CHANGELOG.md).

## Usage

Type `mkqr` with no arguments for a quick guide, or `mkqr -h` for everything.

```sh
mkqr https://example.com                          # print the QR in the terminal
mkqr https://example.com -O qr.png                # save to a file
mkqr https://example.com -O ~/Documents/          # auto-name: example.com-qrcode.png
mkqr https://example.com -c                       # copy the PNG to the clipboard
mkqr https://example.com -O qr.png --open         # save and open in the default viewer
mkqr https://example.com -O qr.png --logo logo.png    # logo in the center
mkqr 'any text' -O card.svg --dark '#0a2540'      # custom color
mkqr --wifi MyNetwork -p hunter2 -O ./            # QR that joins the network
mkqr --vcard 'Ana Lima' --phone +15551234567 --email ana@example.com -O ./
echo -n 'read from stdin' | mkqr - -O out.pdf
```

The output format comes from the suffix of `-O`: `.png .jpg .webp .svg .pdf .eps .txt`.
Without `-O`, the QR is printed to the terminal.

**PNG, WebP and SVG come out cropped and transparent** (no quiet zone), ready to drop
into any layout. For the classic look with a white margin, use `-b 4 --light white`.
JPG, PDF and EPS have no alpha channel, so they get a white background and a margin of 4.

## Platform support

| | Linux | macOS | Windows |
|---|---|---|---|
| generate QR (png, svg, pdf, terminal, Wi-Fi, vCard, logo) | ✓ | ✓ | ✓ |
| `-c` clipboard | `wl-copy` (Wayland) or `xclip` (X11) | native (`osascript`) | native (PowerShell) |
| `--open` | `xdg-open` | native (`open`) | native |
| shell completion | bash, zsh, fish | bash, zsh, fish | — |
| Tab lists nearby Wi-Fi networks | `nmcli` | — | — |
| `install.sh` / `uninstall.sh` | ✓ | ✓ (bash 3.2 ok) | use `pipx install .` |

`mkqr --install-completion` detects your `$SHELL`; override it with `--shell zsh`
(or `bash`, `fish`, `all`). `mkqr --uninstall-completion` reverses it.
CI runs the test suite on Ubuntu, macOS and Windows, from Python 3.10 to 3.14.

## Options

| flag | description | default |
|---|---|---|
| `-O, --output` | output file or directory | terminal |
| `-s, --scale` | pixels per module | 10 |
| `-b, --border` | quiet zone in modules | 0 (png/svg/webp), 4 (others) |
| `-e, --error` | error correction L/M/Q/H | M (H with `--logo`) |
| `--dark`, `--light` | colors; `--light white` for a white background | `#000` / transparent |
| `--logo IMAGE` | image in the center (png/jpg/webp); `--logo-size` 0.1–0.3 | 0.22 |
| `-c, --copy` | copy the QR (as PNG) to the clipboard | |
| `--open` | open the generated file in the default viewer | |
| `--wifi SSID` | Wi-Fi QR; with `-p PASSWORD`, `--security WPA/WEP/nopass`, `--hidden` | |
| `--vcard NAME` | contact QR; with `--phone`, `--email`, `--url`, `--org`, `--title` | |
| `--micro` | allow Micro QR when the content fits | |
| `-f, --force` | overwrite an existing file | |
| `-q, --quiet` | don't print the output path | |
| `--install-completion` | install shell completion; `--shell bash/zsh/fish/all` | |
| `--uninstall-completion` | remove completion from every shell | |
| `--no-color` | disable colors (or set `NO_COLOR`) | |

The full help (`mkqr -h`) is also available as an image: [docs/img/mkqr-help.svg](https://github.com/berodcdev/mkqr/blob/main/docs/img/mkqr-help.svg),
and the quick guide as [docs/img/mkqr.svg](https://github.com/berodcdev/mkqr/blob/main/docs/img/mkqr.svg).

## Built on

[segno](https://github.com/heuer/segno) for QR generation,
[qrcode-artistic](https://github.com/heuer/qrcode-artistic)/Pillow for logos and jpg/webp,
[argcomplete](https://github.com/kislyuk/argcomplete) for shell completion.

## Development

```sh
git clone https://github.com/berodcdev/mkqr.git && cd mkqr
python -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"
pytest
```

See [CONTRIBUTING.md](https://github.com/berodcdev/mkqr/blob/main/CONTRIBUTING.md) for the full workflow, and
[CHANGELOG.md](https://github.com/berodcdev/mkqr/blob/main/CHANGELOG.md) for what changed between releases.

## License

MIT — see [LICENSE](https://github.com/berodcdev/mkqr/blob/main/LICENSE).
