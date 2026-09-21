# Política de segurança

## Versões suportadas

Correções de segurança saem sempre na versão mais recente. Não há backport para
versões anteriores.

| Versão | Suportada |
|---|---|
| 0.1.x | ✓ |

## Reportando uma vulnerabilidade

**Não abra uma issue pública para relatar uma vulnerabilidade.**

Use o canal privado do GitHub:
[Security → Report a vulnerability](https://github.com/berodcdev/mkqr/security/advisories/new).
Se preferir, mande um e-mail para **dev@bernardorodc.com**.

Inclua no relato:

- a versão do mkqr (`mkqr -V`), o sistema operacional e o shell;
- os passos para reproduzir, de preferência com o comando exato;
- o impacto que você consegue demonstrar.

Você recebe uma confirmação em até 7 dias. Se o problema for confirmado,
combinamos uma data de divulgação e o crédito no aviso, se você quiser.

## Superfície de risco do mkqr

O mkqr é uma ferramenta local de linha de comando. Não abre portas, não faz
requisições de rede e não envia telemetria. As áreas onde um problema de
segurança faria sentido são:

- **Escrita de arquivos.** `-O` grava no caminho indicado e cria diretórios pais.
  Sem `-f`, o mkqr se recusa a sobrescrever um arquivo existente.
- **Clipboard e `--open`.** Chamam programas do sistema (`wl-copy`, `xclip`,
  `osascript`, PowerShell, `xdg-open`, `open`). São sempre invocados com lista de
  argumentos, nunca por shell.
- **Autocomplete.** `--install-completion` escreve em `~/.bashrc`, `~/.zshrc` e nos
  diretórios de completion do shell, sempre dentro de um bloco delimitado que o
  `--uninstall-completion` remove.
- **`--logo`.** Abre uma imagem que você indicou usando o Pillow. Falhas de parsing
  de imagem são do Pillow; mantenha-o atualizado.
- **Conteúdo do QR.** O mkqr codifica o que você mandar, sem validar. Um QR gerado
  a partir de conteúdo não confiável carrega esse conteúdo para quem o ler.

## Escopo

Está fora de escopo: vulnerabilidades em dependências que já tenham aviso
publicado (reporte no projeto de origem), e comportamento que dependa de o
atacante já ter execução de código na sua máquina.
