"""Tudo que depende do sistema operacional ou do shell: clipboard, abrir arquivo, completion."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import argcomplete

PROG = "mkqr"
SHELLS = ("bash", "zsh", "fish")
MARK_BEGIN = f"# >>> {PROG} completion >>>"
MARK_END = f"# <<< {PROG} completion <<<"

IS_MAC = sys.platform == "darwin"
IS_WIN = sys.platform.startswith("win")
IS_LINUX = sys.platform.startswith("linux")


def home() -> Path:
    return Path(os.environ.get("HOME") or Path.home())


def data_dir() -> Path:
    xdg = os.environ.get("XDG_DATA_HOME")
    return Path(xdg) if xdg else home() / ".local" / "share"


def config_dir() -> Path:
    xdg = os.environ.get("XDG_CONFIG_HOME")
    return Path(xdg) if xdg else home() / ".config"


# ---------------------------------------------------------------- clipboard

def clipboard_backends() -> list[tuple[str, str | None]]:
    """Backends de clipboard em ordem de preferência: (nome, caminho ou None)."""
    if IS_MAC:
        return [("osascript", shutil.which("osascript"))]
    if IS_WIN:
        return [("powershell", shutil.which("powershell") or shutil.which("pwsh"))]
    wl = shutil.which("wl-copy")
    xclip = shutil.which("xclip")
    order = [("wl-copy", wl), ("xclip", xclip)]
    if not os.environ.get("WAYLAND_DISPLAY") and os.environ.get("DISPLAY"):
        order.reverse()  # sessão X11: xclip primeiro
    return order


def clipboard_hint() -> str:
    if IS_MAC:
        return "osascript não encontrado (faz parte do macOS)"
    if IS_WIN:
        return "PowerShell não encontrado"
    return "instale wl-clipboard (Wayland) ou xclip (X11)"


def copy_png(data: bytes) -> tuple[bool, str]:
    """Coloca um PNG no clipboard. Retorna (ok, nome do backend ou mensagem de erro)."""
    for name, tool in clipboard_backends():
        if not tool:
            continue
        try:
            if name == "wl-copy":
                subprocess.run([tool, "--type", "image/png"], input=data, check=True, timeout=10)
            elif name == "xclip":
                subprocess.run([tool, "-selection", "clipboard", "-t", "image/png", "-i"],
                               input=data, check=True, timeout=10)
            else:
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                    tmp.write(data)
                    path = tmp.name
                try:
                    if name == "osascript":
                        script = f'set the clipboard to (read (POSIX file "{path}") as «class PNGf»)'
                        subprocess.run([tool, "-e", script], check=True, timeout=15, capture_output=True)
                    else:  # powershell
                        ps = (
                            "Add-Type -AssemblyName System.Windows.Forms; "
                            "Add-Type -AssemblyName System.Drawing; "
                            f"$img = [System.Drawing.Image]::FromFile('{path}'); "
                            "[System.Windows.Forms.Clipboard]::SetImage($img); $img.Dispose()"
                        )
                        subprocess.run([tool, "-NoProfile", "-STA", "-Command", ps],
                                       check=True, timeout=30, capture_output=True)
                finally:
                    try:
                        os.unlink(path)
                    except OSError:
                        pass
            return True, name
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError) as exc:
            return False, f"{name} falhou: {exc}"
    return False, f"nenhum programa de clipboard disponível; {clipboard_hint()}"


# ---------------------------------------------------------------- abrir arquivo

def open_path(path: Path) -> str | None:
    """Abre o arquivo no visualizador padrão. Retorna mensagem de erro ou None."""
    if IS_WIN:
        try:
            os.startfile(str(path))  # type: ignore[attr-defined]
        except OSError as exc:
            return f"não foi possível abrir: {exc}"
        return None
    tool = shutil.which("open") if IS_MAC else shutil.which("xdg-open")
    if tool is None:
        return "xdg-open não encontrado (pacote xdg-utils)" if not IS_MAC else "comando open não encontrado"
    subprocess.Popen([tool, str(path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                     start_new_session=True)
    return None


# ---------------------------------------------------------------- redes wi-fi (completion)

def wifi_ssids(prefix: str = "") -> list[str]:
    """SSIDs visíveis, quando o sistema oferece um jeito rápido de listar (Linux/nmcli)."""
    tool = shutil.which("nmcli") if IS_LINUX else None
    if tool is None:
        return []
    try:
        out = subprocess.run([tool, "-t", "-f", "SSID", "dev", "wifi", "list"],
                             capture_output=True, text=True, timeout=3, check=False).stdout
    except (OSError, subprocess.TimeoutExpired):
        return []
    seen: dict[str, None] = {}
    for line in out.splitlines():
        ssid = line.replace("\\:", ":").strip()
        if ssid and ssid.startswith(prefix):
            seen[ssid] = None
    return list(seen)


# ---------------------------------------------------------------- completion

def current_shell() -> str | None:
    name = Path(os.environ.get("SHELL", "")).name
    return name if name in SHELLS else None


def bash_completion_available() -> bool:
    """O pacote bash-completion (2.x) carrega ~/.local/share/bash-completion/completions/ sozinho."""
    candidates = [
        "/usr/share/bash-completion/bash_completion",
        "/etc/bash_completion",
        "/opt/homebrew/etc/profile.d/bash_completion.sh",
        "/usr/local/etc/profile.d/bash_completion.sh",
        "/opt/local/etc/profile.d/bash_completion.sh",
    ]
    return any(Path(c).is_file() for c in candidates)


def bash_completion_dir() -> Path:
    base = os.environ.get("BASH_COMPLETION_USER_DIR")
    return Path(base) / "completions" if base else data_dir() / "bash-completion" / "completions"


def rc_files(shell: str) -> list[Path]:
    if shell == "bash":
        files = [home() / ".bashrc"]
        if IS_MAC:  # no macOS, terminais abrem login shells e leem .bash_profile
            files.append(home() / ".bash_profile")
        return files
    if shell == "zsh":
        zdot = os.environ.get("ZDOTDIR")
        return [(Path(zdot) if zdot else home()) / ".zshrc"]
    return []


def _upsert_block(rc: Path, block: str) -> None:
    text = rc.read_text() if rc.exists() else ""
    if MARK_BEGIN in text and MARK_END in text:
        before = text[: text.index(MARK_BEGIN)]
        after = text[text.index(MARK_END) + len(MARK_END):].lstrip("\n")
        text = before + block + "\n" + after
    else:
        text = text.rstrip("\n") + ("\n\n" if text.strip() else "") + block + "\n"
    rc.parent.mkdir(parents=True, exist_ok=True)
    rc.write_text(text)


def _remove_block(rc: Path) -> bool:
    if not rc.exists():
        return False
    text = rc.read_text()
    if MARK_BEGIN not in text or MARK_END not in text:
        return False
    before = text[: text.index(MARK_BEGIN)].rstrip("\n")
    after = text[text.index(MARK_END) + len(MARK_END):].lstrip("\n")
    rest = (before + "\n\n" + after) if before and after else (before + "\n" if before else after)
    if rest.strip():
        rc.write_text(rest)
    else:
        rc.unlink()  # o arquivo só existia por nossa causa
    return True


def install_completion(shell: str) -> list[str]:
    """Instala a completion para um shell. Retorna linhas de relatório."""
    code = argcomplete.shellcode([PROG], shell=shell)
    report: list[str] = []

    if shell == "fish":
        target = config_dir() / "fish" / "completions" / f"{PROG}.fish"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(code)
        report.append(f"fish: {target} (carregado automaticamente)")
        return report

    if shell == "bash" and bash_completion_available():
        target = bash_completion_dir() / PROG
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(code)
        report.append(f"bash: {target} (carregado pelo bash-completion)")
        return report

    # bash sem bash-completion, ou zsh: arquivo próprio + bloco no rc
    target = data_dir() / PROG / f"completion.{shell}"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(code)
    # sempre em forma POSIX: é o que bash/zsh entendem, inclusive no Git Bash do Windows
    quoted = target.as_posix().replace(home().as_posix(), "$HOME", 1)
    if shell == "zsh":
        block = (
            f"{MARK_BEGIN}\n"
            f'if [ -f "{quoted}" ]; then\n'
            "  (( $+functions[compdef] )) || { autoload -Uz compinit && compinit; }\n"
            f'  source "{quoted}"\n'
            "fi\n"
            f"{MARK_END}"
        )
    else:
        block = f'{MARK_BEGIN}\n[ -f "{quoted}" ] && source "{quoted}"\n{MARK_END}'
    for rc in rc_files(shell):
        _upsert_block(rc, block)
        report.append(f"{shell}: {target}, carregado por {rc}")
    return report


def uninstall_completion() -> list[str]:
    """Remove tudo que install_completion pode ter criado, em qualquer shell."""
    removed: list[str] = []
    paths = [
        bash_completion_dir() / PROG,
        bash_completion_dir() / "getqrcode",  # nome antigo
        config_dir() / "fish" / "completions" / f"{PROG}.fish",
        data_dir() / PROG / "completion.bash",
        data_dir() / PROG / "completion.zsh",
    ]
    for p in paths:
        if p.is_file():
            p.unlink()
            removed.append(str(p))
    own_dir = data_dir() / PROG
    if own_dir.is_dir() and not any(own_dir.iterdir()):
        own_dir.rmdir()
    for shell in ("bash", "zsh"):
        for rc in rc_files(shell):
            if _remove_block(rc):
                removed.append(f"bloco em {rc}")
    return removed
