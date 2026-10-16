import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE.parent))
import make_examples as mx  # noqa: E402
import readme_i18n as i18n  # noqa: E402
import report  # noqa: E402


def test_every_language_has_every_template():
    keys = set(i18n.TEXT["ko"])
    for lang in i18n.LANGS:
        assert set(i18n.TEXT[lang]) == keys, lang
        assert set(i18n.TEXT[lang]["labels"]) == {"baseline", "reply_plain", "plain", "strict"}, lang
    assert set(i18n.README) == set(i18n.NAMES) == set(i18n.LANGS)


def test_korean_templates_keep_the_current_sentences():
    ko = i18n.TEXT["ko"]
    assert ko["block_size"].format(n=i18n.grouped(2271, "ko")) == "규칙 블록 2,271자"
    assert ko["longest"].format(n=18) == "18어절"
    assert ko["example_docs"].format(href="examples/before-after.md") == \
        "문서 예시는 [`examples/before-after.md`](examples/before-after.md)에 있습니다."


def test_numbers_follow_each_language():
    assert [i18n.grouped(2271, lang) for lang in i18n.LANGS] == ["2,271", "2,271", "2,271", "2,271", "2271"]
    assert i18n.grouped(12345, "es") == "12 345" and i18n.grouped(12345, "en") == "12,345"
    assert i18n.grouped(999, "es") == "999"
    assert i18n.percent("95.0", "ko") == "95.0%" and i18n.percent("95.0", "es") == "95.0 %"
    assert i18n.percent(100, "zh") == "100%"


def test_language_line_links_every_other_language():
    assert i18n.language_line("ko") == (
        '<p align="center">\n  한국어 | <a href="docs/README.en.md">English</a> | '
        '<a href="docs/README.ja.md">日本語</a> | <a href="docs/README.zh.md">中文</a> | '
        '<a href="docs/README.es.md">Español</a>\n</p>')
    en = i18n.language_line("en")
    assert '<a href="../README.md">한국어</a> | English | <a href="README.ja.md">日本語</a>' in en
    assert ">English</a>" not in en


def test_links_get_the_language_prefix():
    assert i18n.link("ko", "examples/before-after.md") == "examples/before-after.md"
    assert i18n.link("ja", "examples/before-after.md") == "../examples/before-after.md"
