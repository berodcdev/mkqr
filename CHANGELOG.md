# Changelog

Todas as mudanças relevantes deste projeto são registradas aqui.

O formato segue [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/)
e o versionamento segue [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [Não lançado]

## [0.1.0] — 2026-09-21

Primeira versão pública.

### Adicionado

- CLI `mkqr`: gera QR code a partir de um texto, URL, `--wifi SSID` ou `--vcard NOME`,
  além de ler o conteúdo do stdin com `-`.
- Saída em `.png`, `.jpg`, `.webp`, `.svg`, `.pdf`, `.eps` e `.txt`, escolhida pelo
  sufixo de `-O`. Sem `-O`, o QR é desenhado no próprio terminal.
- Nome de arquivo automático a partir do conteúdo quando `-O` aponta para um diretório
  (`mkqr https://exemplo.com -O ./` → `exemplo.com-qrcode.png`).
- PNG, WebP e SVG saem recortados e com fundo transparente por padrão; JPG, PDF e EPS
  saem com fundo branco e margem 4.
- Aparência: `-s/--scale`, `-b/--border`, `-e/--error`, `--dark`, `--light` e `--micro`.
- `--logo IMAGEM` coloca uma imagem no centro do QR, com caixa de respiro automática e
  correção de erro elevada para H; `--logo-size` ajusta a proporção.
- `-c/--copy` copia o QR como PNG para o clipboard.
- `--open` abre o arquivo gerado no visualizador padrão do sistema.
- Ajuda colorida com banner e um guia rápido quando `mkqr` roda sem argumentos;
  respeita `NO_COLOR`, `FORCE_COLOR` e `--no-color`.
- Autocomplete para bash, zsh e fish via `mkqr --install-completion` (com `--shell`
  para forçar o alvo) e `mkqr --uninstall-completion` para desfazer. O Tab completa
  flags, valores, arquivos e — no Linux com `nmcli` — as redes Wi-Fi visíveis.
- `install.sh` e `uninstall.sh` para Linux e macOS (bash 3.2+), com detecção de pipx,
  do shell e das dependências opcionais de clipboard.
- Suporte a Linux, macOS e Windows: clipboard via `wl-copy`/`xclip`, `osascript` ou
  PowerShell, e abertura de arquivo via `xdg-open`, `open` ou `os.startfile`.
- Suíte de testes com 42 casos, e workflows de CI para Ubuntu, macOS e Windows do
  Python 3.10 ao 3.14, com testes de fumaça da CLI, do protocolo de autocomplete e
  dos instaladores. Os workflows estão desativados nesta versão; os testes rodam
  com `pytest`.
- `docs/make_screenshots.py` regera os screenshots da documentação a partir da saída
  real da CLI.

[Não lançado]: https://github.com/berodcdev/mkqr/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/berodcdev/mkqr/releases/tag/v0.1.0
