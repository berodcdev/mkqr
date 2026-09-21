# Contribuindo com o mkqr

Obrigado pelo interesse! Issues e pull requests são bem-vindos.

> Contributions in English are welcome too — open the issue or PR in whichever
> language you're comfortable with. The codebase and the CLI are in Portuguese.

## Antes de abrir um PR grande

Abra uma issue primeiro descrevendo o que você quer fazer. Isso evita trabalho
jogado fora se a ideia não couber no escopo do projeto.

Correções pequenas (bug óbvio, erro de digitação, ajuste na documentação) podem
ir direto para o PR.

## Ambiente

Python 3.10 ou superior. Nenhuma ferramenta além do `pip` é necessária.

```sh
git clone https://github.com/berodcdev/mkqr.git && cd mkqr
python -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"
pytest
```

Para usar o `mkqr` do repositório no seu shell enquanto desenvolve:

```sh
./install.sh -e          # pipx em modo editável: mudanças em src/ valem na hora
```

## Rodando os testes

```sh
pytest                   # tudo
pytest -q tests/test_cli.py
pytest -k slugify        # um caso só
```

Os testes não tocam no seu `~/.bashrc`, `~/.zshrc` nem em nada fora do `tmp_path`
do pytest — eles redirecionam `HOME`, `XDG_DATA_HOME` e `XDG_CONFIG_HOME`. Se você
escrever um teste novo que mexe em arquivos do usuário, siga o mesmo padrão.

## Layout do projeto

```
src/mkqr/cli.py         parser, conteúdo do QR, renderização e main()
src/mkqr/platform.py    tudo que depende do SO ou do shell: clipboard, --open, completion
src/mkqr/ui.py          cores, banner e formatação da ajuda
tests/                  pytest
docs/make_screenshots.py  regera docs/img/*.svg
.github/workflows/      CI e release
```

A separação importa: qualquer coisa que chame `subprocess`, leia variáveis de
ambiente do sistema ou escreva em `~` mora em `platform.py`. Assim o `cli.py`
continua testável sem mocks de sistema operacional.

## Mexeu na ajuda, no banner ou nas cores?

Os screenshots da documentação são gerados a partir da saída real da CLI. Depois
de qualquer mudança visível em `mkqr` ou `mkqr -h`, regere:

```sh
python docs/make_screenshots.py
```

e inclua os `docs/img/*.svg` atualizados no commit. O script é determinístico:
se nada mudou, ele imprime `=` e os arquivos ficam idênticos.

O CI tem um job (`screenshots em dia`) que regera e falha se o resultado diferir
do que está commitado. Ele usa **Python 3.13** — se o seu diff só aparece em outra
versão, é a formatação do argparse que mudou, não o seu código.

O `docs/img/mkqr.png` (usado no README em inglês, porque o PyPI não renderiza
o SVG) é regerado com Chrome headless — o próprio script imprime o comando.

## Estilo

Não há linter obrigatório no CI. Siga o que já está no arquivo que você está
editando:

- Type hints em funções públicas, com `from __future__ import annotations`.
- Docstring de uma linha explicando o *porquê*, não o *o quê*.
- Comentários em português, e só onde a intenção não é óbvia pelo código.
- Nada de dependência nova sem uma boa razão — o projeto tem três.
- Linhas até ~110 colunas.

## Commits

Mensagem no imperativo, descrevendo o efeito para quem usa:

```
Caminho POSIX no bloco de completion (corrige testes no Windows)
docs: ideias pós-multiplataforma
```

Prefixo `docs:` para mudanças só de documentação. O resto vai sem prefixo.

## Plataformas

O CI roda em Ubuntu, macOS e Windows. Se a sua mudança toca em `platform.py`,
diga no PR em quais sistemas você testou de verdade — o CI cobre bastante coisa,
mas clipboard e abertura de arquivo dependem de sessão gráfica e não são
exercitados lá.

## Lançando uma versão (mantenedores)

1. Atualize `__version__` em `src/mkqr/__init__.py`.
2. Mova as entradas de `[Não lançado]` para a nova seção do `CHANGELOG.md`, com a data.
3. Commit, e então:

```sh
git tag -a v0.2.0 -m "v0.2.0"
git push origin main --tags
```

A tag dispara `.github/workflows/release.yml`, que roda os testes, monta o wheel e
o sdist, cria o GitHub Release e publica no PyPI via Trusted Publishing.

## Código de conduta

Este projeto segue o [Código de Conduta](CODE_OF_CONDUCT.md).
