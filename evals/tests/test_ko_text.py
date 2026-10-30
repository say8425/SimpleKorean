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


def test_digit_runs_and_unclosed_comments_take_linear_time():
    start = time.time()
    assert ko_text.eojeol_count("1" * 40_000 + "번 시도합니다.") == 2
    assert ko_text.mask("<!--" * 20_000 + "끝").endswith("끝")
    elapsed = time.time() - start
    assert elapsed < 0.5, elapsed


def test_a_long_unterminated_backtick_line_takes_linear_time():
    start = time.time()
    assert ko_text.mask("본문입니다.\n" + "`" * 100_000).startswith("본문입니다.")
    elapsed = time.time() - start
    assert elapsed < 0.5, elapsed


def test_fence_masking_is_unchanged():
    masked = {"```\n코드\n```\n본문": "   \n  \n   \n본문",
              "````\n```\n안\n````\n밖": "    \n   \n \n    \n밖",
              "~~~\n코드\n": "   \n  \n",
              "```js\n코드\n```\n뒤": "     \n  \n   \n뒤",
              "본문\n```": "본문\n```",
              "  ```\n코드\n  ```\n뒤": "     \n  \n     \n뒤",
              "````` \n 안\n": "      \n  \n",
              "``\n본문": "``\n본문",
              "```\n코드\n~~~\n뒤\n```\n끝": "   \n  \n   \n \n   \n끝"}
    assert {t: ko_text.mask(t) for t in masked} == masked


def test_number_unit_merging_and_comment_masking_are_unchanged():
    counts = {"버전 1,234 개를 받았습니다.": 3, "간격은 .5 초입니다.": 2, "값 1 2 개를 봅니다.": 4,
              "v1.2.3 초 뒤": 2, "1,2,3 개": 1, "가격 ,5 원": 2, "... 개": 2}
    assert {s: ko_text.eojeol_count(s) for s in counts} == counts
    masked = {"앞 <!-- 숨김 --> 가운데 <!-- 안 닫힘 끝": "앞             가운데 <!-- 안 닫힘 끝",
              "<!-- a <!-- b --> c -->": "                  c -->",
              "<!---->x<!-->y": "       x<!-->y",
              "x <!--\n줄\n--> y": "x     \n \n    y"}
    assert {t: ko_text.mask(t) for t in masked} == masked


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


def test_anida_is_haera_and_bieup_nida_is_hapsyo():
    for sentence in ("변화의 방향은 한쪽이 아니다.", "그는 \"원인이 아니다.\"", "버그가 아니다(재현 안 됨).", "이건 오류가 아니다!"):
        assert ko_text.register(sentence) == "haera", sentence
    for sentence in ("이것은 버그가 아닙니다.", "확인했습니까?", "서버로 갑니다.", "답을 압니다.",
                     "어디로 가십니까?", "확인하겠습니다."):
        assert ko_text.register(sentence) == "hapsyo", sentence
    assert ko_text.register("서버가 죽었으니까.") is None
    assert ko_text.register("니다") == "haera"


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


def test_units_split_at_br_tags():
    text = ("| 항목 | 설명 |\n|---|---|\n| 설치 | 패키지를 받으세요.<br>설정을 여세요.<br/>값을 넣으세요. |\n\n"
            "- 첫 항목을 엽니다.<BR />둘째 항목을 닫습니다.\n\n첫 문장입니다.<br>둘째 문장입니다.\n")
    got = [(u.text, u.line, u.kind) for u in ko_text.units(text)]
    assert ("패키지를 받으세요.", 3, "table") in got and ("값을 넣으세요.", 3, "table") in got, got
    assert ("둘째 항목을 닫습니다.", 5, "list") in got, got
    assert ("첫 문장입니다.", 7, "prose") in got and ("둘째 문장입니다.", 7, "prose") in got, got


def test_units_split_br_variants_and_br_after_a_url():
    text = ("| 칸 | https://example.com<br>설정 파일을 엽니다.<br/ >값을 넣습니다.<br class=\"x\">파일을 저장합니다. |\n\n"
            "첫째 줄 설명입니다<br>둘째 줄 설명입니다\n")
    got = [u.text for u in ko_text.units(text)]
    assert {"URL 설정 파일을 엽니다.", "값을 넣습니다.", "파일을 저장합니다."} <= set(got), got
    assert "첫째 줄 설명입니다" in got and "둘째 줄 설명입니다" in got, got


def test_units_join_br_in_the_middle_of_a_sentence():
    long = ("세션 시작 훅은 사용자가 따로 설정하지 않아도 모든 세션의 처음에 같은 규칙 블록을<br>모델의 문맥에 넣어서 "
            "스킬 이름을 말하지 않은 대화에서도 모델이 규칙을 따르게 만드는 장치입니다.")
    for text in (long, "| 칸 | " + long + " |", "- " + long):
        [unit] = ko_text.units(text + "\n")
        assert ko_text.eojeol_count(unit.text) == 26, unit
    [cell] = [u.text for u in ko_text.units("| 포트 | 이 설정은<br>필수다. |\n")]
    assert cell == "이 설정은 필수다.", cell


def test_units_keep_text_that_only_looks_like_br():
    text = "HTML의 <br 태그는 줄을 바꾸는 태그입니다. 순서는 설치 -> 설정 -> 실행입니다.\n"
    assert [u.text for u in ko_text.units(text)] == ["HTML의 <br 태그는 줄을 바꾸는 태그입니다.", "순서는 설치 -> 설정 -> 실행입니다."]
    assert [u.text for u in ko_text.units("첫 문장입니다.\\<br\\>둘째 문장입니다.\n")] == ["첫 문장입니다.\\<br\\>둘째 문장입니다."]


def _best_time(fn, arg, runs=3):
    """runs번 잰 시간 가운데 가장 짧은 값. 다른 작업이 끼어든 측정을 버린다."""
    import time
    best = float("inf")
    for _ in range(runs):
        start = time.perf_counter()
        fn(arg)
        best = min(best, time.perf_counter() - start)
    return best


def test_units_br_split_takes_linear_time():
    # 절대 시간 대신 입력을 4배로 늘렸을 때 걸리는 시간의 비율을 본다. CI 러너가 느려도 비율은 그대로다.
    # 선형이면 약 4배, 제곱이면 약 16배가 된다. 그래서 10배를 넘으면 실패한다.
    # 아주 짧은 측정은 잡음이 크므로 작은 입력의 시간을 2ms보다 짧게 보지 않는다.
    cases = (
        lambda n: "# 제목\n\n" + "가<br " * (20000 * n),
        lambda n: "| 칸 | " + "가<br a=b " * (10000 * n) + " |",
        lambda n: "값<br a" + " " * (5000 * n) + "끝입니다.",
        lambda n: "값<br a/" + " " * (5000 * n) + "끝입니다.",
        lambda n: "가<br>" * (2500 * n),
        lambda n: "| 칸 | " + "가<br>" * (2500 * n) + " |",
    )
    for i, make in enumerate(cases):
        small = max(_best_time(ko_text.units, make(1)), 0.002)
        large = _best_time(ko_text.units, make(4))
        assert large < 10 * small, (i, small, large)
