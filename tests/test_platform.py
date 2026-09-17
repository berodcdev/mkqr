"""Testes do módulo de plataforma: clipboard, abrir, completion. Sem tocar no sistema real."""

from pathlib import Path

import pytest

from mkqr import platform as plat


@pytest.fixture
def fake_home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    for var in ("XDG_DATA_HOME", "XDG_CONFIG_HOME", "BASH_COMPLETION_USER_DIR", "ZDOTDIR"):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setattr(plat.Path, "home", staticmethod(lambda: home))
    return home


# ---------------------------------------------------------------- completion

def test_fish_completion_autoload(fake_home: Path) -> None:
    report = plat.install_completion("fish")
    target = fake_home / ".config" / "fish" / "completions" / "mkqr.fish"
    assert target.is_file() and "complete --command mkqr" in target.read_text()
    assert "fish" in report[0]


def test_zsh_completion_bloco_no_zshrc_idempotente(fake_home: Path) -> None:
    plat.install_completion("zsh")
    plat.install_completion("zsh")
    zshrc = (fake_home / ".zshrc").read_text()
    assert zshrc.count(plat.MARK_BEGIN) == 1 and zshrc.count(plat.MARK_END) == 1
    assert "compinit" in zshrc and 'source "$HOME/.local/share/mkqr/completion.zsh"' in zshrc
    assert (fake_home / ".local/share/mkqr/completion.zsh").read_text().startswith("#compdef mkqr")


def test_zsh_respeita_zdotdir(fake_home: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    zdot = fake_home / "zdot"
    monkeypatch.setenv("ZDOTDIR", str(zdot))
    plat.install_completion("zsh")
    assert (zdot / ".zshrc").is_file()


def test_bash_com_bash_completion_usa_diretorio_xdg(fake_home: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(plat, "bash_completion_available", lambda: True)
    plat.install_completion("bash")
    assert (fake_home / ".local/share/bash-completion/completions/mkqr").is_file()
    assert not (fake_home / ".bashrc").exists()


def test_bash_sem_bash_completion_usa_bashrc(fake_home: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(plat, "bash_completion_available", lambda: False)
    monkeypatch.setattr(plat, "IS_MAC", True)
    plat.install_completion("bash")
    for rc in (".bashrc", ".bash_profile"):
        text = (fake_home / rc).read_text()
        assert plat.MARK_BEGIN in text and 'source "$HOME/.local/share/mkqr/completion.bash"' in text


def test_bloco_preserva_conteudo_existente(fake_home: Path) -> None:
    zshrc = fake_home / ".zshrc"
    zshrc.write_text("export A=1\n# meu alias\nalias ll='ls -l'\n")
    plat.install_completion("zsh")
    removed = plat.uninstall_completion()
    assert any(".zshrc" in r for r in removed)
    assert zshrc.read_text() == "export A=1\n# meu alias\nalias ll='ls -l'\n"


def test_uninstall_remove_tudo(fake_home: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(plat, "bash_completion_available", lambda: True)
    for sh in plat.SHELLS:
        plat.install_completion(sh)
    removed = plat.uninstall_completion()
    assert len(removed) == 4  # bash file, fish file, zsh file, bloco no .zshrc
    assert not (fake_home / ".local/share/mkqr").exists()
    assert plat.uninstall_completion() == []


def test_current_shell(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SHELL", "/opt/homebrew/bin/zsh")
    assert plat.current_shell() == "zsh"
    monkeypatch.setenv("SHELL", "/bin/ksh")
    assert plat.current_shell() is None


# ---------------------------------------------------------------- clipboard

class FakeRun:
    def __init__(self) -> None:
        self.calls: list[list[str]] = []

    def __call__(self, cmd, **kw):  # noqa: ANN001
        self.calls.append(list(cmd))
        return None


@pytest.mark.parametrize(
    ("platform", "which", "expected"),
    [
        ("linux", {"wl-copy": "/usr/bin/wl-copy", "xclip": None}, "wl-copy"),
        ("linux", {"wl-copy": None, "xclip": "/usr/bin/xclip"}, "xclip"),
        ("darwin", {"osascript": "/usr/bin/osascript"}, "osascript"),
        ("win32", {"powershell": "C:/powershell.exe", "pwsh": None}, "powershell"),
    ],
)
def test_copy_png_escolhe_backend(monkeypatch: pytest.MonkeyPatch, platform: str, which: dict, expected: str) -> None:
    monkeypatch.setattr(plat, "IS_MAC", platform == "darwin")
    monkeypatch.setattr(plat, "IS_WIN", platform == "win32")
    monkeypatch.setattr(plat, "IS_LINUX", platform == "linux")
    monkeypatch.setattr(plat.shutil, "which", lambda name: which.get(name))
    run = FakeRun()
    monkeypatch.setattr(plat.subprocess, "run", run)
    ok, info = plat.copy_png(b"\x89PNG")
    assert ok and info == expected
    assert run.calls and Path(run.calls[0][0]).name.startswith(expected.split(".")[0])


def test_copy_png_x11_prefere_xclip(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(plat, "IS_MAC", False)
    monkeypatch.setattr(plat, "IS_WIN", False)
    monkeypatch.setattr(plat, "IS_LINUX", True)
    monkeypatch.delenv("WAYLAND_DISPLAY", raising=False)
    monkeypatch.setenv("DISPLAY", ":0")
    monkeypatch.setattr(plat.shutil, "which", lambda name: f"/usr/bin/{name}")
    monkeypatch.setattr(plat.subprocess, "run", FakeRun())
    assert plat.copy_png(b"x") == (True, "xclip")


def test_copy_png_sem_backend_explica(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(plat, "IS_MAC", False)
    monkeypatch.setattr(plat, "IS_WIN", False)
    monkeypatch.setattr(plat, "IS_LINUX", True)
    monkeypatch.setattr(plat.shutil, "which", lambda name: None)
    ok, info = plat.copy_png(b"x")
    assert not ok and "wl-clipboard" in info and "xclip" in info


# ---------------------------------------------------------------- abrir

def test_open_path_por_sistema(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    calls: list[list[str]] = []

    class FakePopen:
        def __init__(self, cmd, **kw):  # noqa: ANN001
            calls.append(list(cmd))

    monkeypatch.setattr(plat.subprocess, "Popen", FakePopen)
    monkeypatch.setattr(plat.shutil, "which", lambda name: f"/usr/bin/{name}")
    monkeypatch.setattr(plat, "IS_WIN", False)

    monkeypatch.setattr(plat, "IS_MAC", True)
    assert plat.open_path(tmp_path / "a.png") is None and calls[-1][0].endswith("open")
    monkeypatch.setattr(plat, "IS_MAC", False)
    assert plat.open_path(tmp_path / "a.png") is None and calls[-1][0].endswith("xdg-open")

    monkeypatch.setattr(plat.shutil, "which", lambda name: None)
    assert "xdg-utils" in (plat.open_path(tmp_path / "a.png") or "")


def test_uninstall_apaga_rc_que_so_tinha_nosso_bloco(fake_home: Path) -> None:
    plat.install_completion("zsh")
    assert (fake_home / ".zshrc").is_file()
    plat.uninstall_completion()
    assert not (fake_home / ".zshrc").exists()
