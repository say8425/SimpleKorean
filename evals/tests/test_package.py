import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent.parent / "src"))
import check_numbers as cn  # noqa: E402
import simple_korean as sk  # noqa: E402


def test_prompt_block_reads_every_variant_with_version_line():
    for variant in sk.VARIANTS:
        for lang in sk.LANGS:
            text = sk.prompt_block(variant=variant, lang=lang)
            first = text.split("\n", 1)[0]
            assert first == f"<!-- simple-korean {sk.VARIANTS[variant]} {lang} {sk.__version__} x-release-please-version -->"
            assert len(text.split("\n", 1)[1].strip()) > 0


def test_prompt_block_defaults_to_korean_sentence_rules():
    assert sk.prompt_block() == sk.prompt_block(variant="sentences", lang="ko")


def test_prompt_block_rejects_unknown_variant_and_lang():
    for kwargs in ({"variant": "full"}, {"lang": "ja"}):
        try:
            sk.prompt_block(**kwargs)
        except ValueError as err:
            assert repr(next(iter(kwargs.values()))) in str(err)
        else:
            raise AssertionError(kwargs)


def test_sentence_rules_leave_out_format_rules():
    sentences, fmt = sk.prompt_block("sentences", "ko"), sk.prompt_block("format", "ko")
    for phrase in cn.FORMAT_PHRASES:
        assert phrase in fmt and phrase not in sentences, phrase
    for phrase in cn.SENTENCE_PHRASES:
        assert phrase in sentences, phrase
    assert "**" not in sentences and "|" not in sentences


def test_check_prompt_variants_flags_missing_phrase():
    texts = {"sentences": sk.prompt_block("sentences", "ko"), "format": sk.prompt_block("format", "ko")}
    assert cn.check_prompt_variants(texts) == []
    broken = {**texts, "sentences": texts["sentences"].replace("레포지토리", "저장소")}
    assert cn.check_prompt_variants(broken) == ["prompts/sentence-rules.ko.md에 핵심 문구가 없습니다: 레포지토리"]
    leaked = {**texts, "sentences": texts["sentences"] + "굵은 글씨와 표를 쓰지 마세요.\n"}
    assert cn.check_prompt_variants(leaked) == ["prompts/sentence-rules.ko.md에 서식 문구가 있습니다: 굵은 글씨와 표"]
