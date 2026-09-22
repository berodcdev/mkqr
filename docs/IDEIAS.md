# Ideias — mkqr

Gerado pela skill `sugerir`. Status: proposta · aceita · descartada · feita.
Ideia descartada não volta a ser sugerida; o motivo fica registrado.

## 2026-09-22 · a partir de "Segurança do repositório e sugestões"
- [x] **Atestados de proveniência no release** (P) — já estavam ligados: a `gh-action-pypi-publish` tem `attestations` com `default: 'true'`, então todas as publicações desde a 0.1.0 têm PEP 740; documentado no SECURITY.md com o comando de conferência · `.github/workflows/release.yml` · _feita: já existia_
- [x] **`install.sh` deixar o pipx na origem do PyPI** (P) — trocar a origem instalaria o código errado para quem clona um fork ou branch; em vez disso o script passou a dizer de onde instalou e como trocar · `install.sh` · _feita: resolvida por outro caminho_
- [x] **QR do banner apontando para o repo** (P) — descartada por medição: o QR do banner sai claro sobre escuro e sem zona de silêncio, então não decodifica nem apontando para a URL; a versão escaneável precisa de bloco branco com 15 linhas e o guia deixa de caber numa tela. A URL clicável no rodapé já resolve · `src/mkqr/ui.py` · _descartada: custo de 15 linhas no banner para algo que o link em texto já entrega_

## 2026-09-21 · a partir de "GIF de demonstração no README"
- [ ] **Social preview do repositório** (P) — `usesCustomOpenGraphImage` é `false`: todo link do mkqr colado em Slack, X ou LinkedIn mostra o cartão genérico do GitHub; e a ferramenta gera a própria arte (`mkqr ... --logo`) num PNG 1280x640 · Settings → Social preview · _proposta_
- [ ] **Uma imagem do `--logo`** (P) — `--logo` aparece 6 vezes no README e 0 vezes em imagem; `docs/img/` tem 3 arquivos e nenhum mostra o recurso mais visual da CLI, que é justamente o que faz alguém querer usar · `docs/img/` · _proposta_
- [ ] **Tab completando no GIF** (M) — `docs/demo.tape` tem 0 comandos `Tab`, mas o guia rápido anuncia `--install-completion` como um dos dois destaques; o VHS script `Tab`, falta registrar a completion no shell da gravação · `docs/demo.tape` · _proposta_

## 2026-09-21 · a partir de "Abertura do mkqr como open source"
- [ ] **Dar um giro de teste no release.yml** (P) — o workflow tem 4 jobs e 0 execuções: a tag v0.1.0 foi criada à mão antes de ele ser religado, então o caminho tag → testes → build → Release nunca rodou de verdade; um `workflow_dispatch` valida antes da v0.2.0 · `.github/workflows/release.yml` · _proposta_

## 2026-09-17 · a partir de "mkqr multiplataforma: Linux, macOS e Windows com CI"
- [ ] **Autocomplete no PowerShell** (P) — Windows é a única célula com "—" na matriz do README para Tab; o argcomplete já gera o código de PowerShell (19 linhas), falta gravar no $PROFILE · `src/mkqr/platform.py` · _proposta_
- [ ] **install.ps1 para Windows** (P) — hoje o Windows é o único sistema sem instalador: o README manda rodar `pipx install .` à mão; um .ps1 espelhando o install.sh fecha a matriz e pode entrar no CI windows-latest · `install.ps1` · _proposta_

## 2026-09-16 · a partir de "repo privado no GitHub com LICENSE, testes, CI e screenshot"
- [x] **Release v0.1.0** (P) — o repo tem 0 tags; `gh release create v0.1.0` com o wheel anexado dá um ponto de instalação estável sem clone · `.git` · _feita_

## 2026-09-16 · a partir de "mkqr: nome definitivo, menu colorido e install/uninstall.sh" (estacionadas até organizar o repo para o GitHub)
- [x] **Arquivo LICENSE** (P) — o pyproject declara MIT mas não existe LICENSE no repo (0 arquivos); GitHub e PyPI mostram "sem licença" · `pyproject.toml` · _feita_
- [x] **Versão em um lugar só** (P) — `0.1.0` está duplicado em `pyproject.toml` e `src/mkqr/__init__.py`; hatch lê de `__version__` com `dynamic = ["version"]` · `pyproject.toml` · _feita_
- [x] **Testes das 3 funções puras** (P) — `slugify`, `resolve_output` e `build_content` não têm I/O e não têm teste (pasta tests/ inexistente); base para um CI no GitHub · `src/mkqr/cli.py` · _feita_

## 2026-09-16 · a partir de "mkqr: --logo, git init, autocomplete bash e PNG transparente recortado"
- [ ] **Ler QR de imagem (`mkqr --read foto.png`)** (P) — operação inversa usando o `zbarimg` já instalado; útil pra conferir o que um QR recebido contém · `src/mkqr/cli.py` · _proposta_
- [ ] **Lote (`--batch urls.txt -O pasta/`)** (P) — uma linha por QR, reaproveitando o nome automático por conteúdo que já existe · `src/mkqr/cli.py` · _proposta_
- [x] **Publicar no GitHub** (P) — repo tem 1 commit e 0 remotes; `gh` está instalado mas sem login · `.git` · _feita_
