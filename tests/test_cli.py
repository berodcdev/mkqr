"""Testes das funções puras do mkqr e do fluxo principal em disco."""

from pathlib import Path

import pytest

import mkqr
from mkqr import cli


# ---------------------------------------------------------------- slugify

@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("https://example.com", "example.com-qrcode"),
        ("http://www.exemplo.com/a/b?c=1", "exemplo.com-a-b-c-1-qrcode"),
        ("texto com espaços e ação", "texto-com-espa-os-e-a-o-qrcode"),
        ("   ", "qrcode-qrcode"),
        ("wifi-MinhaRede", "wifi-MinhaRede-qrcode"),
    ],
)
def test_slugify(text: str, expected: str) -> None:
    assert cli.slugify(text) == expected


def test_slugify_limita_tamanho() -> None:
    assert len(cli.slugify("a" * 200)) == 60 + len("-qrcode")


# ---------------------------------------------------------------- resolve_output

def test_resolve_output_none_e_terminal() -> None:
    assert cli.resolve_output(None, "x") is None


def test_resolve_output_diretorio_gera_nome(tmp_path: Path) -> None:
    out = cli.resolve_output(str(tmp_path), "https://example.com")
    assert out == tmp_path / "example.com-qrcode.png"


def test_resolve_output_barra_final_e_diretorio_mesmo_sem_existir(tmp_path: Path) -> None:
    out = cli.resolve_output(str(tmp_path / "nova") + "/", "abc")
    assert out == tmp_path / "nova" / "abc-qrcode.png"


def test_resolve_output_sem_sufixo_vira_png(tmp_path: Path) -> None:
    assert cli.resolve_output(str(tmp_path / "site"), "x") == tmp_path / "site.png"


@pytest.mark.parametrize("ext", [".png", ".svg", ".pdf", ".jpg", ".txt"])
def test_resolve_output_mantem_sufixo_conhecido(tmp_path: Path, ext: str) -> None:
    assert cli.resolve_output(str(tmp_path / f"a{ext}"), "x") == tmp_path / f"a{ext}"


# ---------------------------------------------------------------- build_content

def parse(*argv: str):
    parser = cli.build_parser()
    return parser, parser.parse_args(list(argv))


def test_build_content_texto() -> None:
    parser, args = parse("https://example.com")
    data, label = cli.build_content(args, parser)
    assert data == label == "https://example.com"


def test_build_content_wifi_wpa() -> None:
    parser, args = parse("--wifi", "MinhaRede", "-p", "senha123")
    data, label = cli.build_content(args, parser)
    assert data == "WIFI:T:WPA;S:MinhaRede;P:senha123;;"
    assert label == "wifi-MinhaRede"


def test_build_content_wifi_aberta_e_oculta() -> None:
    parser, args = parse("--wifi", "Aberta", "--hidden")
    data, _ = cli.build_content(args, parser)
    assert data.startswith("WIFI:S:Aberta;") and "H:true" in data


def test_build_content_wifi_seguranca_sem_senha_falha() -> None:
    parser, args = parse("--wifi", "X", "--security", "WPA")
    with pytest.raises(SystemExit):
        cli.build_content(args, parser)


def test_build_content_vcard_separa_sobrenome() -> None:
    parser, args = parse("--vcard", "Ana Paula Lima", "--phone", "+5511999999999", "--org", "NodeTP")
    data, label = cli.build_content(args, parser)
    assert "N:Lima;Ana Paula" in data
    assert "FN:Ana Paula Lima" in data
    assert "TEL:+5511999999999" in data
    assert "ORG:NodeTP" in data
    assert label == "contato-Ana Paula Lima"


def test_build_content_exige_uma_fonte() -> None:
    parser, args = parse("texto", "--wifi", "X")
    with pytest.raises(SystemExit):
        cli.build_content(args, parser)
    parser, args = parse()
    with pytest.raises(SystemExit):
        cli.build_content(args, parser)


# ---------------------------------------------------------------- main em disco

def test_main_gera_png_transparente_sem_margem(tmp_path: Path) -> None:
    from PIL import Image

    out = tmp_path / "a.png"
    assert cli.main(["https://example.com", "-O", str(out), "-q"]) == 0
    im = Image.open(out).convert("RGBA")
    assert im.size == (250, 250)                   # 25 módulos × 10 px, sem margem
    assert im.getpixel((0, 0))[3] == 255           # módulo escuro do canto
    assert im.getpixel((75, 5))[3] == 0            # módulo claro é transparente


def test_main_jpg_tem_fundo_branco_e_margem(tmp_path: Path) -> None:
    from PIL import Image

    out = tmp_path / "a.jpg"
    assert cli.main(["https://example.com", "-O", str(out), "-q"]) == 0
    im = Image.open(out)
    assert im.size == (330, 330)                   # (25 + 2×4) × 10
    assert im.getpixel((0, 0)) == (255, 255, 255)


def test_main_nao_sobrescreve_sem_force(tmp_path: Path) -> None:
    out = tmp_path / "a.png"
    assert cli.main(["x", "-O", str(out), "-q"]) == 0
    assert cli.main(["x", "-O", str(out), "-q"]) == 1
    assert cli.main(["x", "-O", str(out), "-q", "-f"]) == 0


def test_main_logo_exige_raster(tmp_path: Path) -> None:
    logo = tmp_path / "logo.png"
    from PIL import Image

    Image.new("RGBA", (50, 50), "red").save(logo)
    assert cli.main(["x", "-O", str(tmp_path / "a.svg"), "--logo", str(logo), "-q"]) == 1
    assert cli.main(["x", "-O", str(tmp_path / "a.png"), "--logo", str(logo), "-q"]) == 0


def test_main_sem_args_mostra_guia(capsys: pytest.CaptureFixture[str]) -> None:
    assert cli.main([]) == 0
    assert "Uso rápido" in capsys.readouterr().out


def test_guia_mostra_o_repositorio(capsys: pytest.CaptureFixture[str]) -> None:
    """Quem descobre o mkqr pelo terminal precisa de um caminho até o projeto."""
    assert cli.main([]) == 0
    assert mkqr.__url__ in capsys.readouterr().out


def test_url_do_projeto_bate_com_o_pyproject() -> None:
    """A URL do guia e a do pacote não podem divergir."""
    import re

    raiz = Path(__file__).resolve().parent.parent
    pyproject = (raiz / "pyproject.toml").read_text()
    homepage = re.search(r'^Homepage = "([^"]+)"', pyproject, re.M)
    if homepage is None:  # pacote instalado sem o pyproject por perto
        pytest.skip("pyproject.toml não disponível")
    assert mkqr.__url__ == homepage.group(1)
