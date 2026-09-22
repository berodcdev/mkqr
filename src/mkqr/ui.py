"""Cores, banner e formatação da ajuda do mkqr."""

from __future__ import annotations

import argparse
import io
import os
import re
import sys

import segno

from . import __url__, __version__

# ---------------------------------------------------------------- cores

_FORCE: bool | None = None


def set_color(enabled: bool | None) -> None:
    """Força cor ligada/desligada (None = automático)."""
    global _FORCE
    _FORCE = enabled


def use_color() -> bool:
    if _FORCE is not None:
        return _FORCE
    if os.environ.get("NO_COLOR"):
        return False
    if os.environ.get("FORCE_COLOR"):
        return True
    return sys.stdout.isatty() and os.environ.get("TERM", "") != "dumb"


class C:
    """Paleta. Cada atributo vira '' quando a cor está desligada."""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    TITLE = "\033[1;38;5;213m"   # rosa: títulos de seção
    FLAG = "\033[38;5;80m"       # ciano: flags
    META = "\033[38;5;221m"      # amarelo: metavars / valores
    CMD = "\033[1;38;5;114m"     # verde: comandos nos exemplos
    URL = "\033[4;38;5;111m"     # azul sublinhado: urls
    BANNER = ("\033[38;5;207m", "\033[38;5;171m", "\033[38;5;135m",
              "\033[38;5;99m", "\033[38;5;63m", "\033[38;5;69m")  # gradiente
    QR = "\033[38;5;255m"
    RED = "\033[31m"


def paint(text: str, *codes: str) -> str:
    if not use_color() or not codes:
        return text
    return "".join(codes) + text + C.RESET


# ---------------------------------------------------------------- banner

_LOGO = (
    "███╗   ███╗██╗  ██╗ ██████╗ ██████╗ ",
    "████╗ ████║██║ ██╔╝██╔═══██╗██╔══██╗",
    "██╔████╔██║█████╔╝ ██║   ██║██████╔╝",
    "██║╚██╔╝██║██╔═██╗ ██║▄▄ ██║██╔══██╗",
    "██║ ╚═╝ ██║██║  ██╗╚██████╔╝██║  ██║",
    "╚═╝     ╚═╝╚═╝  ╚═╝ ╚══▀▀═╝ ╚═╝  ╚═╝",
)
TAGLINE = "QR codes pela linha de comando, sem fricção."


def _mini_qr() -> list[str]:
    """Um QR de verdade (micro) com o texto 'mkqr', em blocos compactos.

    É decorativo: sai claro sobre escuro e sem zona de silêncio, então nenhum
    leitor decodifica. Já tentamos apontá-lo para o repositório; para escanear
    de fato ele teria que virar um bloco branco com margem, de 15 linhas, e o
    guia rápido deixaria de caber numa tela. A URL clicável no rodapé do guia
    resolve a descoberta sem esse custo.
    """
    buf = io.StringIO()
    try:
        segno.make("mkqr", micro=True, error="L").terminal(out=buf, compact=True, border=0)
    except Exception:  # noqa: BLE001 - o banner nunca pode quebrar o programa
        return []
    return [ln for ln in buf.getvalue().splitlines() if ln.strip()]


def banner() -> str:
    qr = _mini_qr()
    logo = list(_LOGO)
    height = max(len(qr), len(logo))
    # centraliza verticalmente o bloco mais baixo
    qr = [""] * ((height - len(qr)) // 2) + qr
    logo = [""] * ((height - len(logo)) // 2) + logo
    qr_w = max((len(ln) for ln in qr), default=0)

    lines = []
    for i in range(height):
        left = qr[i] if i < len(qr) else ""
        right = logo[i] if i < len(logo) else ""
        color = C.BANNER[min(i, len(C.BANNER) - 1)] if right else ""
        lines.append(f"  {paint(left.ljust(qr_w), C.QR)}   {paint(right, color)}")
    lines.append("")
    lines.append(f"  {paint(TAGLINE, C.BOLD)}  {paint('v' + __version__, C.DIM)}")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------- ajuda colorida

_RE_HEADING = re.compile(r"^(\S[^\n]*?):$", re.M)
_RE_USAGE = re.compile(r"^(uso|usage): ", re.M)
_RE_FLAG_META = re.compile(r"(?<![\w/#-])(-{1,2}[A-Za-z][\w-]*)((?:[ =](?:[A-ZÇÃÕÉ][A-ZÇÃÕÉ_/.-]+|\{[^}]+\}))?)")
_RE_URL = re.compile(r"(https?://[^\s'\"]+)")
_RE_COMMENT = re.compile(r"(\s#.*)$", re.M)


def colorize_help(text: str, prog: str) -> str:
    if not use_color():
        return text

    def flag_meta(m: re.Match[str]) -> str:
        return paint(m.group(1), C.FLAG) + (paint(m.group(2), C.META) if m.group(2) else "")

    out = _RE_HEADING.sub(lambda m: paint(m.group(1), C.TITLE) + ":", text)
    out = _RE_USAGE.sub(lambda m: paint(m.group(1), C.TITLE) + ": ", out)
    out = _RE_COMMENT.sub(lambda m: paint(m.group(1), C.DIM), out)
    out = _RE_FLAG_META.sub(flag_meta, out)
    out = _RE_URL.sub(lambda m: paint(m.group(1), C.URL), out)
    # o nome do programa no início dos exemplos
    out = re.sub(rf"^(\s+)({re.escape(prog)})(?=\s|$)", lambda m: m.group(1) + paint(m.group(2), C.CMD), out, flags=re.M)
    return out


class HelpFormatter(argparse.RawDescriptionHelpFormatter):
    def __init__(self, prog: str, **kw: object) -> None:
        width = min(shutil_width(), 100)
        super().__init__(prog, max_help_position=30, width=width, **kw)  # type: ignore[arg-type]

    def _format_usage(self, usage, actions, groups, prefix):  # type: ignore[override]
        return super()._format_usage(usage, actions, groups, "uso: " if prefix is None else prefix)


def shutil_width() -> int:
    try:
        return os.get_terminal_size().columns
    except OSError:
        return 100


class Parser(argparse.ArgumentParser):
    """ArgumentParser com banner e ajuda colorida."""

    def __init__(self, *a: object, **kw: object) -> None:
        if sys.version_info >= (3, 14):
            kw.setdefault("color", False)  # a coloração é nossa, não a do argparse 3.14
        super().__init__(*a, **kw)  # type: ignore[arg-type]

    def format_help(self) -> str:
        return banner() + "\n" + colorize_help(super().format_help(), self.prog)

    def format_usage(self) -> str:
        return colorize_help(super().format_usage(), self.prog)

    def error(self, message: str) -> None:  # type: ignore[override]
        self.print_usage(sys.stderr)
        erro = paint("erro", C.BOLD, C.RED)
        self.exit(2, f"{self.prog}: {erro}: {message}\n")


QUICK = [
    ("https://example.com", "mostra o QR aqui no terminal"),
    ("https://example.com -O site.png", "salva PNG recortado e transparente"),
    ("https://example.com -O ~/Documents/", "salva com nome automático"),
    ("https://example.com -c", "copia PNG para o clipboard"),
    ("https://example.com -O site.png --logo logo.png", "logo no centro"),
    ("--wifi MinhaRede -p senha -O ./", "QR que conecta no Wi-Fi"),
    ("--vcard 'Ana Lima' --phone +55...", "QR de contato"),
]
MORE = [
    ("-h", "todas as opções: cores, SVG/PDF, vCard, margem..."),
    ("--install-completion", "Tab completa flags, cores, arquivos e redes Wi-Fi"),
]


def _table(prog: str, rows: list[tuple[str, str]]) -> str:
    width = max(len(a) for a, _ in rows) + 2
    lines = []
    for a, c in rows:
        pad = " " * (width - len(a))
        style = C.FLAG if a.startswith("-") and " " not in a else C.META
        lines.append(f"    {paint(prog, C.CMD)} {paint(a, style)}{pad}{paint('# ' + c, C.DIM)}")
    return "\n".join(lines)


def quickstart(prog: str) -> str:
    return (
        banner()
        + "\n  " + paint("Uso rápido", C.TITLE) + "\n"
        + _table(prog, QUICK) + "\n\n"
        + "  " + paint("Mais", C.TITLE) + "\n"
        + _table(prog, MORE) + "\n\n"
        # quem descobre o mkqr pelo terminal não tem outro caminho até o repositório
        + "  " + paint(__url__, C.URL) + "\n"
    )
