import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import ko_text  # noqa: E402


def test_nfc_joins_decomposed_hangul_and_normalizes_newlines():
    assert ko_text.nfc("가") == "가"
    assert ko_text.nfc("가\r\n나\r다") == "가\n나\n다"


def test_jongseong_reads_final_consonant():
    assert ko_text.jongseong("가") == 0
    assert ko_text.jongseong("갈") == ko_text.JONG_RIEUL
    assert ko_text.jongseong("될") == ko_text.JONG_RIEUL
    assert ko_text.jongseong("는") == 4
    assert ko_text.jongseong("a") == -1


def test_mask_keeps_length_and_lines():
    text = "앞 `코드` 뒤\n```\n블록 안\n```\n\"인용\" 끝 https://example.com/x\n"
    masked = ko_text.mask(text)
    assert len(masked) == len(text)
    assert masked.count("\n") == text.count("\n")
    assert "코드" not in masked and "블록 안" not in masked
    assert "인용" not in masked and "example" not in masked
    assert "앞" in masked and "끝" in masked


def test_mask_off_region_and_comments():
    text = "보임\n<!-- simple-korean: off -->\n숨김 — 대시\n<!-- simple-korean: on -->\n다시 보임\n"
    masked = ko_text.mask(text)
    assert "숨김" not in masked and "—" not in masked
    assert "보임" in masked and "다시 보임" in masked


def test_mask_unclosed_off_region_runs_to_end():
    masked = ko_text.mask("앞\n<!-- simple-korean: off -->\n끝까지 숨김\n")
    assert "끝까지" not in masked and "앞" in masked


def test_mask_quotes_optional():
    text = '그는 "멈춰"라고 했습니다.'
    assert "멈춰" not in ko_text.mask(text)
    assert "멈춰" in ko_text.mask(text, quotes=False)


def test_single_quote_does_not_eat_english_contractions():
    text = "it's fine and don't worry"
    assert ko_text.mask(text) == text


def test_strip_frontmatter_keeps_line_count():
    text = "---\nname: x\n설명: 강력한\n---\n본문입니다.\n"
    stripped = ko_text.strip_frontmatter(text)
    assert stripped.count("\n") == text.count("\n")
    assert "강력한" not in stripped and "본문입니다." in stripped


def test_line_of_counts_from_one():
    text = "첫째\n둘째\n셋째"
    assert ko_text.line_of(text, 0) == 1
    assert ko_text.line_of(text, text.index("셋째")) == 3


def test_hangul_ratio_ignores_code():
    assert ko_text.hangul_ratio("이 문서는 한국어로 씁니다.") > 0.9
    assert ko_text.hangul_ratio("This document is written in English.") == 0.0
    assert ko_text.hangul_ratio("```\nprint('hello world')\n```\n한국어 설명입니다.") > 0.9
    assert ko_text.hangul_ratio("") == 0.0
