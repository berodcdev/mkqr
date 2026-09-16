# PYTHON_ARGCOMPLETE_OK
"""CLI do mkqr."""

from __future__ import annotations

import argparse
import io
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import argcomplete
import segno
from argcomplete.completers import ChoicesCompleter, FilesCompleter
from segno import helpers

from . import __version__
from . import ui

RASTER = {".png", ".jpg", ".jpeg", ".webp"}
ALPHA = {".png", ".webp", ".svg"}  # formatos com transparência: saem sem margem e sem fundo
FORMATS = RASTER | {".svg", ".pdf", ".eps", ".txt", ".ans", ".pbm", ".pam", ".ppm", ".xpm", ".tex"}
DEFAULT_EXT = ".png"
COMMANDS = ("mkqr",)
NO_SUGGESTIONS = ChoicesCompleter(())  # sugere o flag, mas nenhum valor (evita listar arquivos)
COLORS = ("black", "white", "transparent", "#000", "#fff", "#0a2540", "#1e40af", "#166534", "#b91c1c")


# ---------------------------------------------------------------- nomes/caminhos

def slugify(text: str) -> str:
    """Transforma o conteúdo em um nome de arquivo razoável."""
    s = re.sub(r"^[a-z][a-z0-9+.-]*://", "", text.strip(), flags=re.I)  # tira o esquema (https://)
    s = re.sub(r"^www\.", "", s, flags=re.I)
    s = re.sub(r"[^A-Za-z0-9._-]+", "-", s).strip("-.")
    return (s[:60] or "qrcode") + "-qrcode"


def resolve_output(raw: str | None, label: str) -> Path | None:
    """Decide o caminho final do arquivo. None significa imprimir no terminal."""
    if raw is None:
        return None
    path = Path(raw).expanduser()
    if raw.endswith(("/", "\\")) or path.is_dir():
        return path / f"{slugify(label)}{DEFAULT_EXT}"
    if path.suffix.lower() not in FORMATS:
        return path.with_name(path.name + DEFAULT_EXT)
    return path


# ---------------------------------------------------------------- autocomplete

def wifi_ssid_completer(prefix: str, **_: object) -> list[str]:
    """Sugere as redes Wi-Fi visíveis (via nmcli), se disponível."""
    tool = shutil.which("nmcli")
    if tool is None:
        return []
    try:
        out = subprocess.run(
            [tool, "-t", "-f", "SSID", "dev", "wifi", "list"],
            capture_output=True, text=True, timeout=3, check=False,
        ).stdout
    except (OSError, subprocess.TimeoutExpired):
        return []
    seen: dict[str, None] = {}
    for line in out.splitlines():
        ssid = line.replace("\\:", ":").strip()
        if ssid and ssid.startswith(prefix):
            seen[ssid] = None
    return list(seen)


def completion_dir() -> Path:
    base = os.environ.get("BASH_COMPLETION_USER_DIR")
    if base:
        return Path(base) / "completions"
    xdg = os.environ.get("XDG_DATA_HOME") or str(Path.home() / ".local" / "share")
    return Path(xdg) / "bash-completion" / "completions"


def install_completion() -> int:
    """Grava o arquivo de completion do bash para o mkqr."""
    target = completion_dir()
    target.mkdir(parents=True, exist_ok=True)
    for cmd in COMMANDS:
        code = argcomplete.shellcode([cmd], shell="bash")
        (target / cmd).write_text(code)
        print(target / cmd)
    print("pronto: abra um novo terminal (ou rode `exec bash`) e use Tab depois de mkqr")
    return 0


# ---------------------------------------------------------------- parser

def build_parser() -> argparse.ArgumentParser:
    p = ui.Parser(
        prog="mkqr",
        usage=(
            "mkqr TEXTO_OU_URL [-O ARQUIVO] [opções]\n"
            "       mkqr --wifi SSID [-p SENHA] [-O ARQUIVO]\n"
            "       mkqr --vcard NOME [--phone TEL] [--email EMAIL] [-O ARQUIVO]\n"
            "       mkqr - [-O ARQUIVO]              (lê o conteúdo do stdin)"
        ),
        description="Gera um QR code a partir de um texto, URL, rede Wi-Fi ou contato.",
        epilog=(
            "exemplos:\n"
            "  mkqr https://nodetp.com.br                        # mostra no terminal\n"
            "  mkqr https://nodetp.com.br -O ~/Documents/site.png\n"
            "  mkqr https://nodetp.com.br -O ~/Documents/        # nome automático pelo conteúdo\n"
            "  mkqr https://nodetp.com.br -c                     # copia PNG para o clipboard\n"
            "  mkqr https://nodetp.com.br -O site.png --open     # salva e abre\n"
            "  mkqr https://nodetp.com.br -O site.png --logo logo.png\n"
            "  mkqr 'texto qualquer' -O card.svg --dark '#0a2540'\n"
            "  mkqr https://nodetp.com.br -O site.png -b 4 --light white   # clássico, com margem\n"
            "  mkqr --wifi MinhaRede -p senha123 -O wifi.png\n"
            "  mkqr --vcard 'Ana Lima' --phone +5511999999999 --email ana@x.com -O ./\n"
            "  echo -n 'lido do stdin' | mkqr - -O out.pdf\n"
            "\n"
            "formatos: .png .jpg .webp .svg .pdf .eps .txt (pelo sufixo de -O)\n"
            "png/webp/svg saem recortados e transparentes; jpg/pdf/eps com fundo branco e margem."
        ),
        formatter_class=ui.HelpFormatter,
        add_help=False,
    )
    p._positionals.title = "conteúdo"

    data = p.add_argument("data", nargs="?", metavar="TEXTO_OU_URL", help="conteúdo do QR code. Use '-' para ler do stdin")
    data.completer = NO_SUGGESTIONS  # type: ignore[attr-defined]

    wifi = p.add_argument_group("wi-fi", "gera um QR que conecta à rede ao ser lido")
    ssid = wifi.add_argument("--wifi", metavar="SSID", help="nome da rede Wi-Fi (Tab lista as redes visíveis)")
    ssid.completer = wifi_ssid_completer  # type: ignore[attr-defined]
    pw = wifi.add_argument("-p", "--password", metavar="SENHA", help="senha da rede (omita para rede aberta)")
    pw.completer = NO_SUGGESTIONS  # type: ignore[attr-defined]
    wifi.add_argument(
        "--security", choices=["WPA", "WEP", "nopass"],
        help="tipo de segurança (padrão: WPA se houver senha, nopass se não)",
    )
    wifi.add_argument("--hidden", action="store_true", help="rede oculta")

    card = p.add_argument_group("contato (vCard)", "gera um QR que salva o contato ao ser lido")
    for flag, meta, hlp in (
        ("--vcard", "NOME", "nome completo do contato, ex.: 'Ana Lima'"),
        ("--phone", "TEL", "telefone, ex.: +5511999999999"),
        ("--email", "EMAIL", "e-mail"),
        ("--url", "URL", "site"),
        ("--org", "EMPRESA", "empresa/organização"),
        ("--title", "CARGO", "cargo"),
    ):
        a = card.add_argument(flag, metavar=meta, help=hlp)
        a.completer = NO_SUGGESTIONS  # type: ignore[attr-defined]

    saida = p.add_argument_group("saída")
    out = saida.add_argument(
        "-O", "--output", metavar="ARQUIVO",
        help="arquivo de saída; o formato vem do sufixo. Se for um diretório, o nome é gerado "
             "a partir do conteúdo. Sem -O, mostra no terminal",
    )
    out.completer = FilesCompleter()  # type: ignore[attr-defined]
    saida.add_argument("-c", "--copy", action="store_true", help="copia o QR (PNG) para o clipboard via wl-copy")
    saida.add_argument("--open", action="store_true", help="abre o arquivo gerado com xdg-open")
    saida.add_argument("-f", "--force", action="store_true", help="sobrescreve o arquivo se já existir")
    saida.add_argument("-q", "--quiet", action="store_true", help="não imprime o caminho gerado")

    ap = p.add_argument_group("aparência")
    ap.add_argument("-s", "--scale", type=int, default=10, metavar="PX", help="tamanho de cada módulo em px (padrão: 10)")
    ap.add_argument(
        "-b", "--border", type=int, default=None, metavar="N",
        help="margem em módulos (padrão: 0 em png/svg/webp, 4 nos demais e no terminal)",
    )
    ap.add_argument(
        "-e", "--error", choices=["L", "M", "Q", "H"], default=None,
        help="correção de erro: L 7%%, M 15%% (padrão), Q 25%%, H 30%% (padrão com --logo)",
    )
    dark = ap.add_argument("--dark", default="#000", metavar="COR", help="cor dos módulos (padrão: #000)")
    dark.completer = ChoicesCompleter(COLORS)  # type: ignore[attr-defined]
    light = ap.add_argument(
        "--light", default=None, metavar="COR",
        help="cor de fundo (padrão: transparente em png/svg/webp, branco nos demais). Ex.: --light white",
    )
    light.completer = ChoicesCompleter(COLORS)  # type: ignore[attr-defined]
    logo = ap.add_argument("--logo", metavar="IMAGEM", help="imagem (png/jpg/webp) no centro do QR; só saída raster")
    logo.completer = FilesCompleter(allowednames=("png", "jpg", "jpeg", "webp", "gif"))  # type: ignore[attr-defined]
    ap.add_argument(
        "--logo-size", type=float, default=0.22, metavar="FRAÇÃO",
        help="fração da largura ocupada pelo logo, 0.1 a 0.3 (padrão: 0.22)",
    )
    ap.add_argument("--micro", action="store_true", help="permite Micro QR quando o conteúdo couber")

    outros = p.add_argument_group("outros")
    outros.add_argument("-h", "--help", action="help", help="mostra esta ajuda e sai")
    outros.add_argument("-V", "--version", action="version", version=f"%(prog)s {__version__}", help="mostra a versão e sai")
    outros.add_argument("--install-completion", action="store_true", help="instala o autocomplete do bash e sai")
    outros.add_argument("--no-color", action="store_true", help="desliga as cores (ou defina NO_COLOR)")
    return p


# ---------------------------------------------------------------- conteúdo

def build_content(args: argparse.Namespace, parser: argparse.ArgumentParser) -> tuple[str, str]:
    """Retorna (conteúdo do QR, rótulo para nome de arquivo automático)."""
    sources = [x for x in (args.data, args.wifi, args.vcard) if x]
    if len(sources) != 1:
        parser.error("informe exatamente um: um texto/URL, --wifi ou --vcard")

    if args.wifi:
        security = args.security or ("WPA" if args.password else "nopass")
        if security != "nopass" and not args.password:
            parser.error(f"--security {security} exige -p/--password")
        data = helpers.make_wifi_data(
            ssid=args.wifi,
            password=args.password if security != "nopass" else None,
            security=None if security == "nopass" else security,
            hidden=args.hidden,
        )
        return data, f"wifi-{args.wifi}"

    if args.vcard:
        parts = args.vcard.strip().split()
        # vCard N: Sobrenome;Nome — o último token vira sobrenome
        name = f"{parts[-1]};{' '.join(parts[:-1])}" if len(parts) > 1 else parts[0]
        data = helpers.make_vcard_data(
            name=name,
            displayname=args.vcard.strip(),
            email=args.email,
            phone=args.phone,
            url=args.url,
            org=args.org,
            title=args.title,
        )
        return data, f"contato-{args.vcard}"

    data = sys.stdin.read() if args.data == "-" else args.data
    if not data.strip():
        parser.error("conteúdo vazio")
    return data, data


# ---------------------------------------------------------------- renderização

def render_pil(qr: segno.QRCode, args: argparse.Namespace, light: str | None):
    """Renderiza como imagem PIL, com o logo no centro se pedido."""
    from PIL import Image  # via qrcode-artistic

    img = qr.to_pil(scale=args.scale, border=args.border, dark=args.dark, light=light)
    img = img.convert("RGBA")
    if not args.logo:
        return img

    logo_path = Path(args.logo).expanduser()
    if not logo_path.is_file():
        raise FileNotFoundError(f"logo não encontrado: {logo_path}")
    logo = Image.open(logo_path).convert("RGBA")

    ratio = min(max(args.logo_size, 0.1), 0.3)
    side = int(img.width * ratio)
    logo.thumbnail((side, side), Image.LANCZOS)

    # caixa de respiro atrás do logo: na cor de fundo, ou "furada" se o fundo é transparente
    pad = max(args.scale, 4)
    box = Image.new("RGBA", (logo.width + 2 * pad, logo.height + 2 * pad), light or (0, 0, 0, 0))
    bx = (img.width - box.width) // 2
    by = (img.height - box.height) // 2
    img.paste(box, (bx, by))
    img.alpha_composite(logo, (bx + pad, by + pad))
    return img


def png_bytes(qr: segno.QRCode, args: argparse.Namespace, light: str | None) -> bytes:
    buf = io.BytesIO()
    if args.logo:
        render_pil(qr, args, light).save(buf, format="PNG")
    else:
        qr.save(buf, kind="png", scale=args.scale, border=args.border, dark=args.dark, light=light)
    return buf.getvalue()


def copy_to_clipboard(data: bytes) -> bool:
    tool = shutil.which("wl-copy")
    if tool is None:
        print("erro: wl-copy não encontrado (instale wl-clipboard)", file=sys.stderr)
        return False
    try:
        subprocess.run([tool, "--type", "image/png"], input=data, check=True, timeout=10)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError) as exc:
        print(f"erro ao copiar para o clipboard: {exc}", file=sys.stderr)
        return False
    return True


def open_file(path: Path) -> None:
    tool = shutil.which("xdg-open")
    if tool is None:
        print("aviso: xdg-open não encontrado, não foi possível abrir", file=sys.stderr)
        return
    subprocess.Popen(
        [tool, str(path)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )


def save(qr: segno.QRCode, out: Path, args: argparse.Namespace, light: str | None) -> None:
    suffix = out.suffix.lower()
    if args.logo or suffix in RASTER - {".png"}:
        if suffix not in RASTER:
            raise ValueError(f"--logo só funciona com saída raster ({', '.join(sorted(RASTER))}), não {suffix}")
        img = render_pil(qr, args, light)
        if suffix in {".jpg", ".jpeg"}:
            img = img.convert("RGB")
        img.save(out)
        return
    if suffix in {".txt", ".ans"}:
        qr.save(str(out), border=args.border)
        return
    qr.save(str(out), scale=args.scale, border=args.border, dark=args.dark, light=light)


# ---------------------------------------------------------------- main

def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    argcomplete.autocomplete(parser, default_completer=NO_SUGGESTIONS)
    raw = sys.argv[1:] if argv is None else argv
    if "--no-color" in raw:
        ui.set_color(False)
    if not [a for a in raw if a != "--no-color"]:
        print(ui.quickstart(parser.prog))
        return 0
    args = parser.parse_args(argv)

    if args.install_completion:
        return install_completion()

    data, label = build_content(args, parser)
    error = args.error or ("H" if args.logo else "M")

    try:
        qr = segno.make(data, error=error, micro=args.micro)
    except (ValueError, segno.DataOverflowError) as exc:
        print(f"erro: {exc}", file=sys.stderr)
        return 2

    out = resolve_output(args.output, label)

    # padrões dependem do formato: png/svg/webp saem recortados e transparentes
    alpha = out is None or out.suffix.lower() in ALPHA
    if args.border is None:
        args.border = 0 if (alpha and (out is not None or args.copy)) else 4
    if args.light is None:
        light = None if alpha else "#fff"
    else:
        light = None if args.light.lower() in {"transparent", "none"} else args.light
    if light is None and not alpha:
        print(f"aviso: {out.suffix} não suporta transparência; usando fundo branco", file=sys.stderr)
        light = "#fff"

    try:
        if args.copy:
            if not copy_to_clipboard(png_bytes(qr, args, light)):
                return 1
            if not args.quiet:
                print("QR copiado para o clipboard (PNG)")

        if out is None:
            if args.open:
                print("aviso: --open precisa de -O para ter um arquivo a abrir", file=sys.stderr)
            if not args.copy:
                if args.logo:
                    print("aviso: --logo não aparece no terminal; use -O ou -c", file=sys.stderr)
                qr.terminal(compact=True, border=min(args.border, 2))
            return 0

        if out.exists() and not args.force:
            print(f"erro: {out} já existe (use -f para sobrescrever)", file=sys.stderr)
            return 1

        out.parent.mkdir(parents=True, exist_ok=True)
        save(qr, out, args, light)
    except (ValueError, OSError) as exc:
        print(f"erro: {exc}", file=sys.stderr)
        return 1

    if not args.quiet:
        print(out)
    if args.open:
        open_file(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
