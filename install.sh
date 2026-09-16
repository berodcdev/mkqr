#!/usr/bin/env bash
# Instala o mkqr com pipx e habilita o autocomplete do bash.
#
#   ./install.sh               instala (ou reinstala) a partir deste diretório
#   ./install.sh -e            modo editável: alterações em src/ valem na hora
#   ./install.sh --no-completion
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EDITABLE=0
COMPLETION=1

for arg in "$@"; do
  case "$arg" in
    -e|--editable) EDITABLE=1 ;;
    --no-completion) COMPLETION=0 ;;
    -h|--help) sed -n '2,6p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "opção desconhecida: $arg" >&2; exit 2 ;;
  esac
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

step "1/4 Python"
command -v python3 >/dev/null || fail "python3 não encontrado. Instale o Python 3.10 ou superior."
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
  command -v pipx >/dev/null || fail "não consegui instalar o pipx. Instale pelo seu gerenciador:
      Arch:          sudo pacman -S python-pipx
      Debian/Ubuntu: sudo apt install pipx
      Fedora:        sudo dnf install pipx
      macOS:         brew install pipx
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

step "4/4 autocomplete e extras"
if [[ $COMPLETION -eq 1 ]]; then
  if [[ -r /usr/share/bash-completion/bash_completion || -r /etc/bash_completion ]]; then
    COMP_FILE="$("$MKQR" --install-completion | head -1)"
    ok "autocomplete do bash em $COMP_FILE"
  else
    warn "pacote bash-completion não encontrado; autocomplete não instalado (Arch: sudo pacman -S bash-completion)"
  fi
else
  warn "autocomplete pulado (--no-completion)"
fi
command -v wl-copy  >/dev/null && ok "wl-copy disponível (mkqr -c)"        || warn "wl-copy ausente: 'mkqr -c' não vai funcionar (pacote wl-clipboard)"
command -v xdg-open >/dev/null && ok "xdg-open disponível (mkqr --open)"   || warn "xdg-open ausente: 'mkqr --open' não vai funcionar (pacote xdg-utils)"
command -v nmcli    >/dev/null && ok "nmcli disponível (Tab lista redes Wi-Fi)" || warn "nmcli ausente: Tab não lista redes Wi-Fi (opcional)"

echo
case ":$PATH:" in
  *":$BIN_DIR:"*) ;;
  *) warn "$BIN_DIR não está no PATH. Rode ${B}pipx ensurepath${N} e abra um novo terminal." ;;
esac
echo "${G}${B}Pronto!${N} Abra um novo terminal (ou rode ${B}exec bash${N}) e digite ${B}mkqr${N}."
