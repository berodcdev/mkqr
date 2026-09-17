#!/usr/bin/env bash
# Remove o mkqr (pipx) e o autocomplete de bash, zsh e fish. Seguro rodar mais de uma vez.
set -euo pipefail

if [[ -t 1 && -z "${NO_COLOR:-}" ]]; then
  B=$'\033[1m'; G=$'\033[32m'; Y=$'\033[33m'; N=$'\033[0m'
else
  B=""; G=""; Y=""; N=""
fi
ok()   { echo "  ${G}✓${N} $*"; }
skip() { echo "  ${Y}-${N} $*"; }

echo "${B}Removendo mkqr${N}"

BIN_DIR="$(pipx environment --value PIPX_BIN_DIR 2>/dev/null || echo "$HOME/.local/bin")"
MKQR="$BIN_DIR/mkqr"

# 1) autocomplete: o próprio mkqr sabe tudo que criou
if [[ -x "$MKQR" ]]; then
  "$MKQR" --uninstall-completion | sed 's/^  removido: //' | while IFS= read -r line; do
    case "$line" in
      "nada para remover") skip "nenhum autocomplete para remover" ;;
      *) ok "autocomplete removido: $line" ;;
    esac
  done
else
  # mkqr já não existe: limpa os caminhos conhecidos à mão
  DATA="${XDG_DATA_HOME:-$HOME/.local/share}"
  CONF="${XDG_CONFIG_HOME:-$HOME/.config}"
  found=0
  for f in "${BASH_COMPLETION_USER_DIR:-$DATA/bash-completion}/completions/mkqr" \
           "${BASH_COMPLETION_USER_DIR:-$DATA/bash-completion}/completions/getqrcode" \
           "$CONF/fish/completions/mkqr.fish" "$DATA/mkqr/completion.bash" "$DATA/mkqr/completion.zsh"; do
    [[ -f "$f" ]] && { rm -f "$f"; ok "autocomplete removido: $f"; found=1; }
  done
  rmdir "$DATA/mkqr" 2>/dev/null || true
  for rc in "$HOME/.bashrc" "$HOME/.bash_profile" "${ZDOTDIR:-$HOME}/.zshrc"; do
    if [[ -f "$rc" ]] && grep -q '# >>> mkqr completion >>>' "$rc"; then
      tmp="$(mktemp)"
      sed '/# >>> mkqr completion >>>/,/# <<< mkqr completion <<</d' "$rc" > "$tmp" && cat "$tmp" > "$rc" && rm -f "$tmp"
      ok "autocomplete removido: bloco em $rc"; found=1
    fi
  done
  [[ $found -eq 0 ]] && skip "nenhum autocomplete para remover"
fi

# 2) pacote
if command -v pipx >/dev/null && pipx list --short 2>/dev/null | grep -q '^mkqr '; then
  pipx uninstall mkqr >/dev/null
  ok "pacote mkqr removido do pipx"
else
  skip "mkqr não estava instalado no pipx"
fi

echo
echo "${G}${B}Pronto.${N} Abra um novo terminal (ou rode ${B}hash -r${N}) para o comando sumir do atual."
