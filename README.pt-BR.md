# mkqr

**QR codes pela linha de comando, sem fricção.** PNG, SVG, PDF, Wi-Fi, vCard, logo, clipboard.

[![CI](https://github.com/berodcdev/mkqr/actions/workflows/ci.yml/badge.svg)](https://github.com/berodcdev/mkqr/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/mkqr.svg)](https://pypi.org/project/mkqr/)
[![Python](https://img.shields.io/pypi/pyversions/mkqr.svg)](https://pypi.org/project/mkqr/)
[![Licença: MIT](https://img.shields.io/badge/licen%C3%A7a-MIT-blue.svg)](LICENSE)

🇺🇸 [Read in English](README.md)

<img src="docs/img/demo.gif" alt="mkqr gerando QR codes no terminal" width="820">

Digite `mkqr` sem argumentos para ver o guia rápido, ou `mkqr -h` para tudo.

## Instalação

```sh
pipx install mkqr        # recomendado: isolado e no PATH
pip install mkqr         # ou no ambiente atual
```

Depois, se quiser o Tab completando flags, cores, arquivos e redes Wi-Fi:

```sh
mkqr --install-completion
```

### Não tem `pipx`?

O `pipx` instala cada CLI no seu próprio virtualenv, então as dependências do
mkqr nunca se misturam com as dos seus projetos. Se aparecer
`pipx: command not found`:

| | |
|---|---|
| macOS | `brew install pipx` |
| Debian / Ubuntu | `sudo apt install pipx` |
| Fedora | `sudo dnf install pipx` |
| Arch | `sudo pacman -S python-pipx` |
| openSUSE | `sudo zypper install python3-pipx` |
| qualquer outro | `python3 -m pip install --user pipx` |

Depois rode `pipx ensurepath` uma vez e abra um terminal novo — é ele que põe o
`~/.local/bin` no seu `PATH`, que é onde o comando `mkqr` vai parar.

Com pressa? O `pip install mkqr` não precisa de nada disso.

### Sem o PyPI

Direto do GitHub — mesmo pacote, sem passar pelo PyPI. Serve se o PyPI estiver
fora do ar, bloqueado na sua rede, ou se você quiser o commit mais recente:

```sh
pipx install git+https://github.com/berodcdev/mkqr.git          # o que está no main
pipx install git+https://github.com/berodcdev/mkqr.git@v0.1.1   # uma versão específica
```

Cada [release](https://github.com/berodcdev/mkqr/releases) também traz o wheel
pronto anexado, se você preferir não compilar do fonte.

Ou a partir de um clone, que já instala e configura o autocomplete de uma vez:

```sh
git clone https://github.com/berodcdev/mkqr.git && cd mkqr
./install.sh              # pipx + autocomplete do seu shell; use -e para modo editável
./uninstall.sh            # remove tudo
```

No Windows (sem bash): `pipx install .` e pronto.

## Atualizar

```sh
pipx upgrade mkqr        # se instalou com pipx
pip install -U mkqr      # se instalou com pip
mkqr -V                  # confere em qual versão você está
```

O `pipx upgrade-all` atualiza o mkqr junto com todas as outras ferramentas que o
pipx gerencia.

<details>
<summary>Instalou pelo GitHub, e não pelo PyPI?</summary>

O `pipx upgrade` reconsulta a origem original — então ele só vai ao PyPI se foi
de lá que veio. Para uma instalação vinda do GitHub, reinstale por cima:

```sh
pipx install --force git+https://github.com/berodcdev/mkqr.git
```

A partir de um clone, atualize o clone antes; o `install.sh` reinstala por cima
do que estiver lá:

```sh
git pull && ./install.sh
```

Se instalou de um clone e quiser passar a receber atualizações normais, troque a
origem uma vez com `pipx install --force mkqr`. Depois disso o
`pipx upgrade mkqr` funciona.
</details>

As versões estão listadas no [CHANGELOG.md](CHANGELOG.md).

## Uso

```sh
mkqr https://example.com                          # mostra no terminal
mkqr https://example.com -O ~/Documents/example-qrcode.png
mkqr https://example.com -O ~/Documents/          # nome automático: example.com-qrcode.png
mkqr https://example.com -c                       # copia o PNG para o clipboard
mkqr https://example.com -O site.png --open       # salva e abre no visualizador
mkqr https://example.com -O site.png --logo logo.png   # logo no centro
mkqr 'texto' -O card.svg --dark '#0a2540'
mkqr --wifi MinhaRede -p senha123 -O ./             # QR que conecta na rede
mkqr --vcard 'Ana Lima' --phone +5511999999999 --email ana@x.com --org Acme -O ./
echo -n 'lido do stdin' | mkqr - -O out.pdf
```

Formato de saída pelo sufixo: `.png .jpg .webp .svg .pdf .eps .txt`. Sem `-O`, imprime no terminal.

**PNG, WebP e SVG saem recortados e com fundo transparente** (sem margem), prontos para colocar em
qualquer layout. Para a versão clássica com margem branca: `-b 4 --light white`.
JPG, PDF e EPS não têm transparência e saem com fundo branco e margem 4.

## Plataformas

| | Linux | macOS | Windows |
|---|---|---|---|
| gerar QR (png, svg, pdf, terminal, Wi-Fi, vCard, logo) | ✓ | ✓ | ✓ |
| `-c` clipboard | `wl-copy` (Wayland) ou `xclip` (X11) | nativo (`osascript`) | nativo (PowerShell) |
| `--open` | `xdg-open` | nativo (`open`) | nativo |
| autocomplete | bash, zsh, fish | bash, zsh, fish | — |
| Tab lista redes Wi-Fi | `nmcli` | — | — |
| `install.sh` / `uninstall.sh` | ✓ | ✓ (bash 3.2 ok) | via `pipx install .` |

`mkqr --install-completion` detecta o seu `$SHELL`; force com `--shell zsh` (ou `bash`, `fish`, `all`).
`mkqr --uninstall-completion` desfaz tudo. O CI roda em Ubuntu, macOS e Windows, do Python 3.10 ao 3.14.

## Opções

| flag | descrição | padrão |
|---|---|---|
| `-O, --output` | arquivo ou diretório de saída | terminal |
| `-s, --scale` | px por módulo | 10 |
| `-b, --border` | margem em módulos | 0 (png/svg/webp), 4 (demais) |
| `-e, --error` | correção de erro L/M/Q/H | M (H com `--logo`) |
| `--dark`, `--light` | cores; `--light white` para fundo branco | #000 / transparente |
| `--logo IMAGEM` | imagem no centro (png/jpg/webp); `--logo-size` 0.1 a 0.3 | 0.22 |
| `-c, --copy` | copia o QR (PNG) para o clipboard | |
| `--open` | abre o arquivo gerado no visualizador padrão | |
| `--wifi SSID` | QR de rede Wi-Fi; com `-p SENHA`, `--security WPA/WEP/nopass`, `--hidden` | |
| `--vcard NOME` | QR de contato; com `--phone`, `--email`, `--url`, `--org`, `--title` | |
| `--micro` | permite Micro QR quando o conteúdo couber | |
| `-f, --force` | sobrescreve arquivo existente | |
| `-q, --quiet` | não imprime o caminho | |
| `--install-completion` | instala o autocomplete do seu shell; `--shell bash/zsh/fish/all` | |
| `--uninstall-completion` | remove o autocomplete de todos os shells | |
| `--no-color` | desliga as cores (ou defina `NO_COLOR`) | |

A ajuda completa (`mkqr -h`) também está em imagem: [docs/img/mkqr-help.svg](docs/img/mkqr-help.svg),
e o guia rápido em [docs/img/mkqr.svg](docs/img/mkqr.svg).

## Construído sobre

[segno](https://github.com/heuer/segno) (geração do QR),
[qrcode-artistic](https://github.com/heuer/qrcode-artistic)/Pillow (logo, jpg/webp),
[argcomplete](https://github.com/kislyuk/argcomplete) (autocomplete).

## Desenvolvimento

```sh
git clone https://github.com/berodcdev/mkqr.git && cd mkqr
python -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"
pytest
```

Veja [CONTRIBUTING.md](CONTRIBUTING.md) para o fluxo completo e
[CHANGELOG.md](CHANGELOG.md) para o que mudou entre as versões.

## Licença

MIT — veja [LICENSE](LICENSE).
