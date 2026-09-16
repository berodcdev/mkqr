# Ideias — mkqr

Gerado pela skill `sugerir`. Status: proposta · aceita · descartada · feita.
Ideia descartada não volta a ser sugerida; o motivo fica registrado.

## 2026-09-16 · a partir de "mkqr: nome definitivo, menu colorido e install/uninstall.sh" (estacionadas até organizar o repo para o GitHub)
- [ ] **Arquivo LICENSE** (P) — o pyproject declara MIT mas não existe LICENSE no repo (0 arquivos); GitHub e PyPI mostram "sem licença" · `pyproject.toml` · _proposta_
- [ ] **Versão em um lugar só** (P) — `0.1.0` está duplicado em `pyproject.toml` e `src/mkqr/__init__.py`; hatch lê de `__version__` com `dynamic = ["version"]` · `pyproject.toml` · _proposta_
- [ ] **Testes das 3 funções puras** (P) — `slugify`, `resolve_output` e `build_content` não têm I/O e não têm teste (pasta tests/ inexistente); base para um CI no GitHub · `src/mkqr/cli.py` · _proposta_

## 2026-09-16 · a partir de "mkqr: --logo, git init, autocomplete bash e PNG transparente recortado"
- [ ] **Ler QR de imagem (`mkqr --read foto.png`)** (P) — operação inversa usando o `zbarimg` já instalado; útil pra conferir o que um QR recebido contém · `src/mkqr/cli.py` · _proposta_
- [ ] **Lote (`--batch urls.txt -O pasta/`)** (P) — uma linha por QR, reaproveitando o nome automático por conteúdo que já existe · `src/mkqr/cli.py` · _proposta_
- [ ] **Publicar no GitHub** (P) — repo tem 1 commit e 0 remotes; `gh` está instalado mas sem login · `.git` · _proposta_
