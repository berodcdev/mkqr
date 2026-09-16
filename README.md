# getqrcode / mkqr

Gere QR codes pela linha de comando com facilidade. `mkqr` e `getqrcode` são o mesmo comando.

```sh
mkqr https://nodetp.com.br -O ~/Documents/nodetp-qrcode.png
mkqr https://nodetp.com.br -O ~/Documents/          # nome automático: nodetp.com.br-qrcode.png
mkqr https://nodetp.com.br                          # mostra no terminal
mkqr https://nodetp.com.br -c                       # copia o PNG para o clipboard
mkqr https://nodetp.com.br -O site.png --open       # salva e abre no visualizador
mkqr https://nodetp.com.br -O site.png --logo logo.png   # logo no centro
mkqr 'texto' -O card.svg --dark '#0a2540'
mkqr --wifi MinhaRede -p senha123 -O ./             # QR que conecta na rede
mkqr --vcard 'Bernardo Silva' --phone +5511999999999 --email b@x.com --org NodeTP -O ./
echo -n 'lido do stdin' | mkqr - -O out.pdf
```

Formato de saída pelo sufixo: `.png .jpg .webp .svg .pdf .eps .txt`. Sem `-O`, imprime no terminal.

**PNG, WebP e SVG saem recortados e com fundo transparente** (sem margem), prontos para colocar em
qualquer layout. Para a versão clássica com margem branca: `-b 4 --light white`.
JPG, PDF e EPS não têm transparência e saem com fundo branco e margem 4.

## Instalação

```sh
pipx install .            # ou: pipx install -e .  para editar e usar direto
mkqr --install-completion # habilita Tab no bash (flags, L/M/Q/H, cores, arquivos, redes Wi-Fi)
```

Dependências: [segno](https://github.com/heuer/segno) (QR), qrcode-artistic/Pillow (logo, jpg/webp),
argcomplete (autocomplete). O clipboard usa `wl-copy` (wl-clipboard) e `--open` usa `xdg-open`.

## Opções

| flag | descrição | padrão |
|---|---|---|
| `-O, --output` | arquivo ou diretório de saída | terminal |
| `-s, --scale` | px por módulo | 10 |
| `-b, --border` | margem em módulos | 0 (png/svg/webp), 4 (demais) |
| `-e, --error` | correção de erro L/M/Q/H | M (H com `--logo`) |
| `--dark`, `--light` | cores; `--light white` para fundo branco | #000 / transparente |
| `--logo IMAGEM` | imagem no centro (png/jpg/webp); `--logo-size` 0.1 a 0.3 | 0.22 |
| `-c, --copy` | copia o QR (PNG) para o clipboard via `wl-copy` | |
| `--open` | abre o arquivo gerado com `xdg-open` | |
| `--wifi SSID` | QR de rede Wi-Fi; com `-p SENHA`, `--security WPA/WEP/nopass`, `--hidden` | |
| `--vcard NOME` | QR de contato; com `--phone`, `--email`, `--url`, `--org`, `--title` | |
| `-f, --force` | sobrescreve arquivo existente | |
| `-q, --quiet` | não imprime o caminho | |
| `--install-completion` | grava o autocomplete do bash em `~/.local/share/bash-completion/completions/` | |
