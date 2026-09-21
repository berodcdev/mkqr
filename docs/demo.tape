# Demonstração do mkqr para o README.
#
#   brew install vhs        # traz ttyd e ffmpeg junto
#   vhs docs/demo.tape      # regera docs/img/demo.gif
#
# Precisa do mkqr no PATH (`./install.sh` ou `pipx install .`).
# A gravação roda num diretório temporário, então não suja o repositório.

Output docs/img/demo.gif

Require mkqr

Set Shell bash
Set FontFamily "Menlo"
Set FontSize 16
Set LineHeight 1.0
Set Width 1120
Set Height 600
Set Padding 26
Set Margin 0
Set BorderRadius 10
Set TypingSpeed 35ms
Set Framerate 24
Set PlaybackSpeed 1.0

Set Theme { "name": "mkqr", "background": "#1b1d23", "foreground": "#e6e6e6", "cursor": "#e6e6e6", "selection": "#2c2f38", "black": "#1b1d23", "red": "#ff5f57", "green": "#87d787", "yellow": "#ffd75f", "blue": "#5f87ff", "magenta": "#d75fd7", "cyan": "#5fd7d7", "white": "#e6e6e6", "brightBlack": "#5c6370", "brightRed": "#ff7b72", "brightGreen": "#a6e3a1", "brightYellow": "#ffe08a", "brightBlue": "#87afff", "brightMagenta": "#ff87ff", "brightCyan": "#87d7d7", "brightWhite": "#ffffff" }

# --- preparo, fora da gravação -------------------------------------------
Hide
Type `export PS1='\[\e[38;5;114m\]❯\[\e[0m\] ' PROMPT_COMMAND= HISTFILE=/dev/null`
Enter
Type "cd $(mktemp -d)"
Enter
Type "clear"
Enter
Sleep 500ms
Show

# --- 1. guia rápido: o que é ---------------------------------------------
Sleep 500ms
Type "mkqr"
Sleep 400ms
Enter
Sleep 3s

Type "clear"
Enter
Sleep 300ms

# --- 2. salvar arquivos, com nome automático ------------------------------
Type "mkqr https://github.com/berodcdev/mkqr -O qr.png"
Sleep 250ms
Enter
Sleep 1.1s

Type "mkqr --wifi CafeDaEsquina -p mkqr2026 -O ./"
Sleep 250ms
Enter
Sleep 1.2s

Type "mkqr --vcard 'Ana Lima' --phone +5511999999999 -O ./"
Sleep 250ms
Enter
Sleep 1.2s

Type "ls"
Sleep 250ms
Enter
Sleep 2.2s

Type "clear"
Enter
Sleep 300ms

# --- 3. fecha no QR desenhado no próprio terminal -------------------------
Type "mkqr https://github.com/berodcdev/mkqr"
Sleep 400ms
Enter
Sleep 4s
