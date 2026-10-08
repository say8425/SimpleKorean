import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import ko_rules  # noqa: E402
from ko_text import mask, units  # noqa: E402

CORE = ko_rules.slop_pattern(ko_rules.SLOP_CORE)


def cats(text, strict=False):
    return sorted(h.category for h in ko_rules.lexical_hits(mask(text), strict=strict, slop_rx=CORE))


def test_hedge_patterns():
    for s in ("실패할 수도 있습니다.", "원인인 것 같습니다.", "재시작하는 것이 좋습니다.",
              "확인하시기 바랍니다.", "원인인 것으로 보입니다.", "아마 캐시 문제입니다."):
        assert cats(s) == ["hedge"], (s, cats(s))
    assert cats("아마존 S3에 올립니다.") == []
    assert cats("수도 서울에 있습니다.") == []


def test_will_calque_needs_rieul_batchim():
    assert cats("다음 버전에서 제거될 것입니다.") == ["will_calque"]
    assert cats("값이 남아 있을 것이다.") == ["will_calque"]
    assert cats("중요한 것은 순서입니다.") == []
    assert cats("이것은 캐시를 지우는 것입니다.") == []


def test_double_passive():
    assert cats("값이 변경되어졌습니다.") == ["double_passive"]
    assert cats("화면에 보여집니다.") == ["double_passive"]
    assert cats("돼지 저금통입니다.") == []
    assert cats("파일이 만들어집니다.") == []


def test_translationese_patterns():
    for s in ("설정에 대해 설명합니다.", "API를 통해 요청합니다.", "스케줄러에 의해 실행됩니다.",
              "배포에 있어서 중요합니다.", "필드를 가지고 있습니다.", "타임아웃으로 인해 실패했습니다.",
              "만약 실패하면 멈춥니다.", "세 형식을 지원하고 있습니다.", "서버로부터 응답을 받습니다."):
        assert "translationese" in cats(s), (s, cats(s))
    assert cats("서버에 있어요.") == []
    assert cats("두 서비스를 통합합니다.") == []


def test_light_verb_colloquial_latin():
    assert cats("배포를 진행합니다.") == ["light_verb"]
    assert cats("진행 상황을 봅니다.") == []
    assert cats("근데 이건 바뀔 겁니다.") == ["colloquial", "colloquial"]
    assert cats("로그, 지표 등등을 봅니다.") == ["latin_abbrev"]
    assert cats("e.g. 로그를 봅니다.") == ["latin_abbrev"]


def test_dashes_and_semicolons():
    assert cats("배포가 실패했습니다 — 디스크가 찼습니다.") == ["em_dash"]
    assert cats("범위는 5–10분입니다.") == []
    assert cats("`--force`를 쓰지 마세요.") == []
    assert cats("첫째; 둘째") == ["semicolon"]
    assert cats("코드 `a; b`는 그대로입니다.") == []


def test_slop_core_and_negative_parallel():
    assert cats("강력한 도구로 원활하게 처리합니다.") == ["slop_word", "slop_word"]
    assert cats("이것은 단순히 캐시가 아니라 저장소입니다.") == ["slop_word"]
    assert cats('"강력한"이라는 말을 지우세요.') == []


def test_slop_terms_file_with_comments_and_spaces():
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        p = Path(d, "slop.tsv")
        p.write_text("# 주석\n중요한 역할\t3\t(지우세요)\n다양한\t4\t여러\n", encoding="utf-8")
        terms = ko_rules.load_slop_terms(p)
        assert "중요한 역할" in terms and "다양한" in terms and "# 주석" not in terms
        rx = ko_rules.slop_pattern(terms)
        assert rx.search("핵심이 중요한  역할을 합니다") and not rx.search("불중요한 역할")


def test_rotation_prefers_designated_word():
    hits = ko_rules.rotation_hits(mask("키를 검증하세요. 값을 확인하세요. 다시 확인합니다."))
    assert [h.text for h in hits] == ["검증 (확인)"]
    hits = ko_rules.rotation_hits(mask("구성 파일을 엽니다. 설정 파일을 저장합니다."))
    assert [h.text for h in hits] == ["구성 파일 (설정)"]
    assert ko_rules.rotation_hits(mask("키를 검증하고 값을 점검합니다.")) and True


def test_strict_only_patterns():
    text = "백업을 반드시 확인해야 합니다. 서버나 클라이언트를 다시 시작하세요. 실패할 경우 로그를 보세요."
    assert cats(text) == []
    assert cats(text, strict=True) == ["strict_condition", "strict_connective", "strict_ending"]
    assert cats("하나 이상을 고르세요. 실행하거나 멈추세요. 그러나 끝납니다.", strict=True) == []


def scats(text, text_type="descriptive"):
    us = units(text)
    return sorted(h.category for h in ko_rules.sentence_hits(us, text_type) + ko_rules.register_hits(us))


def test_length_limits_follow_sentence_kind():
    assert scats("가 " * 15 + "하세요.") == ["sentence_over_limit"]
    assert scats("가 " * 19 + "합니다.") == []
    assert scats("가 " * 20 + "합니다.") == ["sentence_over_limit"]


def test_untyped_sentence_uses_text_type():
    fragment = "가 " * 17 + "끝"
    assert scats(fragment, "procedural") == ["sentence_over_limit"]
    assert scats(fragment, "descriptive") == []


def test_trailing_condition():
    assert "trailing_condition" in scats("로그를 확인하세요. 단, 빌드가 실패한 경우에만 확인합니다.")
    assert "trailing_condition" in scats("로그를 확인하세요(빌드가 실패한 경우).")
    assert scats("빌드가 실패하면 로그를 확인하세요.") == []


def test_noun_ending_only_in_prose():
    assert scats("설정 변경 필요.") == ["noun_ending"]
    assert scats("- 설정 변경 필요\n- 로그 확인 완료\n") == []
    assert scats("백업이 있음.") == ["noun_ending"]


def test_register_mix_flags_minority():
    hits = ko_rules.register_hits(units("서버가 응답합니다. 로그를 읽으세요. 이 값은 기본값이다. 캐시를 지웁니다."))
    assert [h.text for h in hits] == ["이 값은 기본값이다."]


def test_register_accepts_single_styles():
    assert ko_rules.register_hits(units("값이 바뀐다. 로그를 본다. 다시 시작하라.")) == []
    assert ko_rules.register_hits(units("값이 바뀌어요. 로그를 보세요.")) == []
    assert ko_rules.register_hits(units("전원을 끕니다. 커버를 여십시오.")) == []
    assert len(ko_rules.register_hits(units("로그를 보세요. 커버를 여십시오. 값을 봅니다. 값을 엽니다."))) == 1
