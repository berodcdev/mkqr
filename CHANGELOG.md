# Changelog

Todas as mudanças relevantes deste projeto são registradas aqui.

O formato segue [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/)
e o versionamento segue [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [Não lançado]

## [0.1.3] — 2026-09-22

### Adicionado

- Seção "Atualizar" nos READMEs: `pipx upgrade mkqr`, `pip install -U mkqr` e o
  caso de quem instalou pelo GitHub ou de um clone, em que o `pipx upgrade`
  reconsulta a origem original e não vai ao PyPI. Quem usou o `install.sh` fica
  com o pipx apontando para a pasta do clone, então nunca enxerga versão nova
  sem trocar a origem — a seção mostra como.

## [0.1.2] — 2026-09-22

### Adicionado

- O guia rápido (`mkqr` sem argumentos) termina com o endereço do repositório.
  Quem descobre a ferramenta pelo terminal não tinha nenhum caminho até o
  projeto. A URL vive em `mkqr.__url__`, e um teste garante que ela não diverge
  da `Homepage` do `pyproject.toml`.

### Alterado

- Os exemplos da ajuda, do guia rápido e do README usam `example.com`, o domínio
  que a RFC 2606 reserva para documentação. Antes apontavam para um site real,
  que não tem relação com o projeto e virava propaganda involuntária.

## [0.1.1] — 2026-09-22

Só documentação: o código é idêntico ao da 0.1.0.

### Corrigido

- Os READMEs explicam como instalar o `pipx` em cada sistema, com os mesmos
  comandos que o `install.sh` já sugeria. Quem não tinha o `pipx` batia num
  `command not found` sem saída, porque a instalação recomendada começava por ele.
- Os links do README em inglês, que é o `long_description` do pacote, agora são
  absolutos. O PyPI resolve link relativo contra `pypi.org/project/mkqr/`, então
  LICENSE, CONTRIBUTING, CHANGELOG, o README em português e os dois SVGs davam
  404 na página publicada.

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
- Suíte de testes com 42 casos e CI em Ubuntu, macOS e Windows, do Python 3.10 ao 3.14,
  incluindo testes de fumaça da CLI, do protocolo de autocomplete e dos instaladores.
- `docs/make_screenshots.py` regera os screenshots da documentação a partir da saída
  real da CLI.

[Não lançado]: https://github.com/berodcdev/mkqr/compare/v0.1.3...HEAD
[0.1.3]: https://github.com/berodcdev/mkqr/compare/v0.1.2...v0.1.3
[0.1.2]: https://github.com/berodcdev/mkqr/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/berodcdev/mkqr/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/berodcdev/mkqr/releases/tag/v0.1.0
