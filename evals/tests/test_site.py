import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "site"))
import build_site as bs  # noqa: E402


def test_every_language_page_fills_every_hole():
    pages = bs.build()
    assert sorted(p.as_posix() for p in pages) == sorted(
        ["site/index.html"] + [f"site/{lang}/index.html" for lang in ("en", "ja", "zh", "es")])
    for path, text in pages.items():
        assert not re.search(r"\{\{\w+\}\}", text), path
        lang = "ko" if path.parent.name == "site" else path.parent.name
        assert f'<html lang="{lang}">' in text
        assert f'<link rel="canonical" href="{bs.page_url(lang)}">' in text
        assert text.count('rel="alternate" hreflang=') == len(bs.LANGS) + 1
        assert 'aria-current="page"' in text


def test_links_between_pages_are_relative():
    assert bs.link("ko", "ko") == "./"
    assert bs.link("ko", "en") == "en/"
    assert bs.link("en", "ko") == "../"
    assert bs.link("en", "ja") == "../ja/"
    assert '<link rel="stylesheet" href="../style.css">' in bs.build()[Path("site/en/index.html")]


def test_render_rejects_missing_and_unused_strings():
    strings = {"ko": {"title": "제목"}}
    for template, word in (("{{title}} {{lead}}", "lead"), ("{{lang}}", "title")):
        try:
            bs.render(template, strings, "ko")
        except ValueError as err:
            assert word in str(err)
        else:
            raise AssertionError("ValueError가 나야 합니다")


def test_check_reports_a_page_that_differs_from_the_build():
    with tempfile.TemporaryDirectory() as tmp:
        for rel, text in bs.build().items():
            (Path(tmp) / rel).parent.mkdir(parents=True, exist_ok=True)
            (Path(tmp) / rel).write_text(text, encoding="utf-8")
        assert bs.check(tmp) == []
        (Path(tmp) / "site/ja/index.html").write_text("손으로 고친 글", encoding="utf-8")
        assert [p.split(":")[0] for p in bs.check(tmp)] == ["site/ja/index.html"]
