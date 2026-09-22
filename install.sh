#!/usr/bin/env bash
# Instala o mkqr com pipx e habilita o autocomplete do seu shell.
# Funciona em Linux e macOS (bash 3.2+). No Windows use: pipx install .
#
#   ./install.sh                 instala (ou reinstala) a partir deste diretório
#   ./install.sh -e              modo editável: alterações em src/ valem na hora
#   ./install.sh --shell zsh     força o shell do autocomplete (bash|zsh|fish|all)
#   ./install.sh --no-completion
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EDITABLE=0
COMPLETION=1
SHELL_OPT=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    -e|--editable) EDITABLE=1 ;;
    --no-completion) COMPLETION=0 ;;
    --shell) shift; SHELL_OPT="${1:-}"; [[ -n "$SHELL_OPT" ]] || { echo "--shell precisa de um valor" >&2; exit 2; } ;;
    --shell=*) SHELL_OPT="${1#--shell=}" ;;
    -h|--help) sed -n '2,9p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "opção desconhecida: $1" >&2; exit 2 ;;
  esac
  shift
done

if [[ -t 1 && -z "${NO_COLOR:-}" ]]; then
  B=$'\033[1m'; G=$'\033[32m'; Y=$'\033[33m'; R=$'\033[31m'; D=$'\033[2m'; N=$'\033[0m'
else
  B=""; G=""; Y=""; R=""; D=""; N=""
fi
ok()   { echo "  ${G}✓${N} $*"; }
warn() { echo "  ${Y}!${N} $*"; }
fail() { echo "  ${R}✗${N} $*" >&2; exit 1; }
step() { echo; echo "${B}$*${N}"; }

OS="$(uname -s)"
case "$OS" in
  Linux)  OS_NAME="Linux" ;;
  Darwin) OS_NAME="macOS" ;;
  MINGW*|MSYS*|CYGWIN*) OS_NAME="Windows (bash)"; warn "no Windows, prefira: pipx install $REPO" ;;
  *) OS_NAME="$OS" ;;
esac

pipx_hint() {
  case "$OS" in
    Darwin) echo "      brew install pipx && pipx ensurepath" ;;
    Linux)
      if command -v pacman >/dev/null; then echo "      sudo pacman -S python-pipx"
      elif command -v apt-get >/dev/null; then echo "      sudo apt install pipx"
      elif command -v dnf >/dev/null; then echo "      sudo dnf install pipx"
      elif command -v zypper >/dev/null; then echo "      sudo zypper install python3-pipx"
      else echo "      python3 -m pip install --user pipx && python3 -m pipx ensurepath"; fi ;;
    *) echo "      python3 -m pip install --user pipx && python3 -m pipx ensurepath" ;;
  esac
}

step "1/4 Python ($OS_NAME)"
command -v python3 >/dev/null || fail "python3 não encontrado. Instale o Python 3.10 ou superior.$( [[ $OS == Darwin ]] && echo " (brew install python)" )"
PYV="$(python3 -c 'import sys; print(f"{sys.version_info[0]}.{sys.version_info[1]}")')"
python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' \
  || fail "Python $PYV encontrado, mas o mkqr precisa de 3.10 ou superior."
ok "python3 $PYV"

step "2/4 pipx"
if ! command -v pipx >/dev/null; then
  warn "pipx não encontrado; tentando instalar com pip --user..."
  if python3 -m pip install --user --quiet pipx 2>/dev/null; then
    python3 -m pipx ensurepath >/dev/null 2>&1 || true
    export PATH="$HOME/.local/bin:$PATH"
  fi
  command -v pipx >/dev/null || fail "não consegui instalar o pipx. Instale com:
$(pipx_hint)
    e rode este script de novo."
fi
ok "pipx $(pipx --version 2>/dev/null)"

step "3/4 mkqr"
PIPX_ARGS=(install --force)
[[ $EDITABLE -eq 1 ]] && PIPX_ARGS+=(--editable)
pipx "${PIPX_ARGS[@]}" "$REPO" >/dev/null 2>&1 || pipx "${PIPX_ARGS[@]}" "$REPO"
BIN_DIR="$(pipx environment --value PIPX_BIN_DIR 2>/dev/null || echo "$HOME/.local/bin")"
MKQR="$BIN_DIR/mkqr"
[[ -x "$MKQR" ]] || fail "instalação terminou mas $MKQR não existe."
ok "$("$MKQR" --version) instalado em $MKQR$([[ $EDITABLE -eq 1 ]] && echo " ${D}(editável → $REPO)${N}")"

# O pipx guarda a origem da instalação. Instalando desta pasta — que é o certo,
# porque é o código que você clonou —, um `pipx upgrade mkqr` reconstrói daqui e
# nunca consulta o PyPI. Quem não souber disso fica numa versão velha achando
# que está atualizado.
if [[ $EDITABLE -eq 0 ]]; then
  echo "    ${D}origem: esta pasta. 'pipx upgrade mkqr' reconstrói daqui, não do PyPI.${N}"
  echo "    ${D}para seguir as versões publicadas: pipx install --force mkqr${N}"
fi

step "4/4 autocomplete e extras"
if [[ $COMPLETION -eq 1 ]]; then
  COMP_ARGS=(--install-completion)
  [[ -n "$SHELL_OPT" ]] && COMP_ARGS+=(--shell "$SHELL_OPT")
  if OUT="$("$MKQR" "${COMP_ARGS[@]}" 2>&1)"; then
    echo "$OUT" | sed -n 's/^  //p' | while IFS= read -r line; do ok "autocomplete $line"; done
  else
    warn "autocomplete não instalado: $OUT"
  fi
else
  warn "autocomplete pulado (--no-completion)"
fi

case "$OS" in
  Darwin)
    ok "clipboard (mkqr -c) via osascript e abrir (--open) via open: nativos do macOS" ;;
  Linux)
    if command -v wl-copy >/dev/null || command -v xclip >/dev/null; then
      ok "clipboard (mkqr -c) via $(command -v wl-copy >/dev/null && echo wl-copy || echo xclip)"
    else
      warn "sem wl-copy nem xclip: 'mkqr -c' não vai funcionar (pacotes wl-clipboard ou xclip)"
    fi
    command -v xdg-open >/dev/null && ok "abrir (mkqr --open) via xdg-open" || warn "xdg-open ausente: 'mkqr --open' não vai funcionar (pacote xdg-utils)"
    command -v nmcli >/dev/null && ok "nmcli: Tab lista redes Wi-Fi" || warn "nmcli ausente: Tab não lista redes Wi-Fi (opcional)" ;;
esac

echo
case ":$PATH:" in
  *":$BIN_DIR:"*) ;;
  *) warn "$BIN_DIR não está no PATH. Rode ${B}pipx ensurepath${N} e abra um novo terminal." ;;
esac
echo "${G}${B}Pronto!${N} Abra um novo terminal e digite ${B}mkqr${N}."
