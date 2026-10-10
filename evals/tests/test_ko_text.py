import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import ko_text  # noqa: E402


def test_nfc_joins_decomposed_hangul_and_normalizes_newlines():
    assert ko_text.nfc("가") == "가"
    assert ko_text.nfc("가\r\n나\r다") == "가\n나\n다"


def test_nfc_strips_a_leading_bom():
    assert ko_text.nfc("﻿가\r\n") == "가\n"
    text = ko_text.nfc("﻿---\nname: x\n---\n본문입니다.\n")
    assert "name" not in ko_text.strip_frontmatter(text)


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


def test_mask_blanks_html_entities_but_not_a_real_semicolon():
    text = "칸에 A&nbsp;B, &#124;, &#x2014;, &amp;를 씁니다. R&D; 다음"
    masked = ko_text.mask(text)
    assert len(masked) == len(text)
    assert masked.count(";") == 1 and "nbsp" not in masked and "#124" not in masked


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


def test_line_of_is_fast_on_a_long_text():
    text = "첫째 줄입니다\n" * 150_000
    step = len(text) // 10_000
    positions = range(0, len(text), step)
    start = time.time()
    lines = [ko_text.line_of(text, p) for p in positions]
    elapsed = time.time() - start
    assert lines[:3] == [1, text.count("\n", 0, step) + 1, text.count("\n", 0, 2 * step) + 1]
    assert ko_text.line_of(text, text.index("\n")) == 1 and ko_text.line_of(text, text.index("\n") + 1) == 2
    assert elapsed < 0.5, elapsed


def test_hangul_ratio_ignores_code():
    assert ko_text.hangul_ratio("이 문서는 한국어로 씁니다.") > 0.9
    assert ko_text.hangul_ratio("This document is written in English.") == 0.0
    assert ko_text.hangul_ratio("```\nprint('hello world')\n```\n한국어 설명입니다.") > 0.9
    assert ko_text.hangul_ratio("") == 0.0


def test_split_sentences_on_terminal_punctuation():
    got = [s for s, _ in ko_text.split_sentences('로그를 읽으세요. 그다음 "멈춤."이라고 적습니다! 끝?')]
    assert got == ["로그를 읽으세요.", '그다음 "멈춤."이라고 적습니다!', "끝?"]


def test_split_keeps_version_numbers():
    got = [s for s, _ in ko_text.split_sentences("v2.0 버전을 설치하세요. 다음은 1.5초입니다.")]
    assert got == ["v2.0 버전을 설치하세요.", "다음은 1.5초입니다."]


def test_units_split_list_table_and_prose():
    text = ("# 제목은 세지 않습니다\n\n"
            "첫 문장입니다. 둘째 문장은\n줄을 넘어갑니다.\n\n"
            "- 목록 항목 하나\n- 목록 항목 둘입니다.\n\n"
            "| 칸 하나 | 칸 둘입니다 |\n|---|---|\n| 셋째 칸 | 넷째 칸 |\n\n"
            "```\n코드 블록 안의 문장입니다.\n```\n")
    got = [(u.text, u.line, u.kind) for u in ko_text.units(text)]
    assert got == [
        ("첫 문장입니다.", 3, "prose"),
        ("둘째 문장은 줄을 넘어갑니다.", 3, "prose"),
        ("목록 항목 하나", 6, "list"),
        ("목록 항목 둘입니다.", 7, "list"),
        ("칸 하나", 9, "table"),
        ("칸 둘입니다", 9, "table"),
        ("셋째 칸", 11, "table"),
        ("넷째 칸", 11, "table"),
    ], got


def test_units_count_code_url_quote_as_one_token():
    got = ko_text.units("`sqlpipe run`을 https://x.dev 에서 \"빠르게\" 실행하세요.")
    assert got[0].text == "CODE을 URL 에서 QUOTE 실행하세요.", got


def test_units_skip_blockquote_marker_and_headings_inside():
    got = [(u.text, u.kind) for u in ko_text.units("> ## 예시\n>\n> 인용 안의 문장입니다.\n")]
    assert got == [("인용 안의 문장입니다.", "prose")], got


def test_eojeol_count_merges_parentheses_and_units():
    assert ko_text.eojeol_count("Postgres 포트(기본값 5432)에 연결하지 못하면 멈춥니다.") == 5
    assert ko_text.eojeol_count("디스크를 5 GB 비우고 10 분 기다리세요.") == 5


def test_sentence_kind_by_ending():
    assert ko_text.sentence_kind("로그를 읽으세요.") == "procedural"
    assert ko_text.sentence_kind("전원을 끄십시오.") == "procedural"
    assert ko_text.sentence_kind("실행하자.") == "procedural"
    assert ko_text.sentence_kind("서버가 응답합니다.") == "descriptive"
    assert ko_text.sentence_kind("설정 변경 필요.") is None
    assert ko_text.sentence_kind("결과 목록") is None


def test_register_classes():
    assert ko_text.register("서버가 응답합니다.") == "hapsyo"
    assert ko_text.register("서버가 응답합니까?") == "hapsyo"
    assert ko_text.register("전원을 끄십시오.") == "hapsyo_imp"
    assert ko_text.register("로그를 읽으세요.") == "haeyo_imp"
    assert ko_text.register("서버가 응답해요.") == "haeyo"
    assert ko_text.register("서버가 응답한다.") == "haera"
    assert ko_text.register("설정 변경 필요.") is None
    assert ko_text.register("대상: 사용자.") is None


def test_trailing_parenthetical_is_not_the_sentence_ending():
    assert ko_text.sentence_kind('"-되어지다"를 쓰지 마세요(예: 변경되어지다).') == "procedural"
    assert ko_text.register('"-되어지다"를 쓰지 마세요(예: 변경되어지다).') == "haeyo_imp"
    assert ko_text.register("설정 파일을 엽니다(경로는 플랫폼마다 다르다).") == "hapsyo"
    assert ko_text.tail("로그를 확인하세요(선택 사항임).") == "로그를 확인하세요"
    assert ko_text.register("(이 값은 실행할 때마다 바뀝니다.)") == "hapsyo"


def test_noun_phrases_ending_in_ra_or_yo_have_no_register():
    for phrase in ("클라우드 인프라", "환경에 따라", "약 5분 소요", "필요", "데이터 수요", "문서 개요"):
        assert ko_text.register(phrase) is None, phrase
        assert ko_text.sentence_kind(phrase) is None, phrase
    for sentence, style in (("파드가 메모리 때문에 죽었어요", "haeyo"), ("내일 다시 확인할게요", "haeyo"),
                            ("벌써 끝났군요", "haeyo"), ("버전이 다르거든요", "haeyo"), ("이건 버그죠", "haeyo"),
                            ("설정을 바꿔요", "haeyo"), ("서버가 멈춰요", "haeyo"), ("로그를 확인하라", "haera"),
                            ("값을 바꾼다", "haera"), ("두 값이 같은가", None)):
        assert ko_text.register(sentence) == style, (sentence, ko_text.register(sentence))
