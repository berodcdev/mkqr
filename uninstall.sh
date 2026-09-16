#!/usr/bin/env bash
# Remove o mkqr (pipx) e o autocomplete do bash. Seguro rodar mais de uma vez.
set -euo pipefail

if [[ -t 1 && -z "${NO_COLOR:-}" ]]; then
  B=$'\033[1m'; G=$'\033[32m'; Y=$'\033[33m'; N=$'\033[0m'
else
  B=""; G=""; Y=""; N=""
fi
ok()   { echo "  ${G}✓${N} $*"; }
skip() { echo "  ${Y}-${N} $*"; }

echo "${B}Removendo mkqr${N}"

if command -v pipx >/dev/null && pipx list --short 2>/dev/null | grep -q '^mkqr '; then
  pipx uninstall mkqr >/dev/null
  ok "pacote mkqr removido do pipx"
else
  skip "mkqr não estava instalado no pipx"
fi

if [[ -n "${BASH_COMPLETION_USER_DIR:-}" ]]; then
  COMP_DIR="$BASH_COMPLETION_USER_DIR/completions"
else
  COMP_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/bash-completion/completions"
fi
removed=0
for name in mkqr getqrcode; do
  if [[ -f "$COMP_DIR/$name" ]]; then
    rm -f "$COMP_DIR/$name"
    ok "autocomplete removido: $COMP_DIR/$name"
    removed=1
  fi
done
[[ $removed -eq 0 ]] && skip "nenhum arquivo de autocomplete para remover"

echo
echo "${G}${B}Pronto.${N} O comando some dos terminais novos; no atual, rode ${B}hash -r${N}."
