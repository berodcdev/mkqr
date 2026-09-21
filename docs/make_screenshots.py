#!/usr/bin/env python3
"""Regera docs/img/*.svg a partir da saída real da CLI.

Rode depois de mexer na ajuda, no banner ou nas cores:

    python docs/make_screenshots.py

Usa sempre o código de src/, não o mkqr instalado, para que o screenshot
reflita o que está no repositório. Nada além da stdlib é necessário.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
IMG = REPO / "docs" / "img"

FONT = "JetBrains Mono, Fira Code, DejaVu Sans Mono, Menlo, monospace"
SIZE = 14
LINE = 19          # entrelinha
PAD_X = 18         # margem esquerda/direita
BASE_Y = 58        # linha de base da primeira linha (abaixo dos "semáforos")
PAD_BOTTOM = 25
# Avanço por caractere com folga: a fonte ideal ocupa 0.60em, mas quem não tiver
# nenhuma das fontes da lista cai num fallback mais largo. Sem essa folga o texto
# vaza do viewBox e aparece cortado.
ADVANCE = 9.6

BG = "#1b1d23"
FG = "#e6e6e6"
DIM_OPACITY = "0.55"

SGR = re.compile(r"\x1b\[([0-9;]*)m")


def xterm256(n: int) -> str:
    """Código de cor 256 -> hex, pela tabela padrão do xterm."""
    if n < 16:
        base = [
            (0, 0, 0), (205, 0, 0), (0, 205, 0), (205, 205, 0),
            (0, 0, 238), (205, 0, 205), (0, 205, 205), (229, 229, 229),
            (127, 127, 127), (255, 0, 0), (0, 255, 0), (255, 255, 0),
            (92, 92, 255), (255, 0, 255), (0, 255, 255), (255, 255, 255),
        ]
        r, g, b = base[n]
    elif n < 232:
        steps = (0, 95, 135, 175, 215, 255)
        i = n - 16
        r, g, b = steps[i // 36], steps[(i // 6) % 6], steps[i % 6]
    else:
        r = g = b = 8 + 10 * (n - 232)
    return f"#{r:02x}{g:02x}{b:02x}"


class Style:
    __slots__ = ("fg", "bold", "dim", "italic", "underline")

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.fg = FG
        self.bold = self.dim = self.italic = self.underline = False

    def copy(self) -> "Style":
        s = Style()
        s.fg, s.bold, s.dim = self.fg, self.bold, self.dim
        s.italic, s.underline = self.italic, self.underline
        return s

    def apply(self, params: str) -> None:
        codes = [int(c or 0) for c in params.split(";")] if params else [0]
        i = 0
        while i < len(codes):
            c = codes[i]
            if c == 0:
                self.reset()
            elif c == 1:
                self.bold = True
            elif c == 2:
                self.dim = True
            elif c == 3:
                self.italic = True
            elif c == 4:
                self.underline = True
            elif c == 38 and codes[i + 1 : i + 2] == [5]:
                self.fg = xterm256(codes[i + 2])
                i += 2
            elif c == 39:
                self.fg = FG
            elif 30 <= c <= 37:
                self.fg = xterm256(c - 30)
            elif 90 <= c <= 97:
                self.fg = xterm256(c - 90 + 8)
            i += 1


def escape(text: str) -> str:
    return (text.replace("&", "&amp;").replace("<", "&lt;")
                .replace(">", "&gt;").replace("'", "&#x27;"))


def parse(output: str) -> list[list[tuple[str, Style]]]:
    """Texto com ANSI -> linhas de trechos (texto, estilo)."""
    style = Style()
    linhas: list[list[tuple[str, Style]]] = []
    for raw in output.split("\n"):
        trechos: list[tuple[str, Style]] = []
        pos = 0
        for m in SGR.finditer(raw):
            if m.start() > pos:
                trechos.append((raw[pos : m.start()], style.copy()))
            style.apply(m.group(1))
            pos = m.end()
        if pos < len(raw):
            trechos.append((raw[pos:], style.copy()))
        linhas.append(trechos)
    while linhas and not any(t.strip() for t, _ in linhas[-1]):
        linhas.pop()
    return linhas


def to_svg(linhas: list[list[tuple[str, Style]]]) -> str:
    largura_chars = max((sum(len(t) for t, _ in ln) for ln in linhas), default=0)
    w = round(2 * PAD_X + largura_chars * ADVANCE)
    h = BASE_Y + (len(linhas) - 1) * LINE + PAD_BOTTOM

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" font-family="{FONT}" font-size="{SIZE}">',
        f'<rect width="{w}" height="{h}" rx="10" fill="{BG}"/>',
        '<circle cx="20" cy="18" r="6" fill="#ff5f57"/>'
        '<circle cx="40" cy="18" r="6" fill="#febc2e"/>'
        '<circle cx="60" cy="18" r="6" fill="#28c840"/>',
    ]
    for i, linha in enumerate(linhas):
        if not any(t for t, _ in linha):
            continue
        y = BASE_Y + i * LINE
        spans = []
        for texto, st in linha:
            if not texto:
                continue
            attrs = [f'fill="{st.fg}"']
            if st.bold:
                attrs.append('font-weight="bold"')
            if st.dim:
                attrs.append(f'opacity="{DIM_OPACITY}"')
            if st.italic:
                attrs.append('font-style="italic"')
            if st.underline:
                attrs.append('text-decoration="underline"')
            attrs.append('xml:space="preserve"')
            spans.append(f'<tspan {" ".join(attrs)}>{escape(texto)}</tspan>')
        out.append(f'<text x="{PAD_X}" y="{y}" xml:space="preserve">{"".join(spans)}</text>')
    out.append("</svg>")
    return "\n".join(out) + "\n"


def run(args: list[str]) -> str:
    """Roda a CLI a partir de src/, com cor ligada e largura fixa."""
    code = (
        "import sys; sys.path.insert(0, 'src');"
        "from mkqr.cli import main; sys.exit(main())"
    )
    r = subprocess.run(
        [sys.executable, "-c", code, *args],
        cwd=REPO, capture_output=True, text=True,
        env={"FORCE_COLOR": "1", "COLUMNS": "200", "PATH": "/usr/bin:/bin",
             "PYTHONIOENCODING": "utf-8", "LC_ALL": "en_US.UTF-8"},
    )
    if r.returncode not in (0,):
        sys.exit(f"`mkqr {' '.join(args)}` saiu com {r.returncode}:\n{r.stderr}")
    return r.stdout


def main() -> int:
    IMG.mkdir(parents=True, exist_ok=True)
    for nome, args in (("mkqr.svg", []), ("mkqr-help.svg", ["-h"])):
        svg = to_svg(parse(run(args)))
        destino = IMG / nome
        antes = destino.read_text() if destino.exists() else ""
        destino.write_text(svg)
        w, h = re.search(r'width="(\d+)" height="(\d+)"', svg).groups()
        print(f"{'=' if svg == antes else '~'} {destino.relative_to(REPO)} ({w}x{h})")
    print("\nPNG para o PyPI (opcional, precisa do Chrome):")
    print('  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \\')
    print("    --headless --screenshot=docs/img/mkqr.png --force-device-scale-factor=2 \\")
    print("    --default-background-color=00000000 --window-size=W,H file://$PWD/docs/img/mkqr.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
