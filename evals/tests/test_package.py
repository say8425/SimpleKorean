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


def _variant_texts():
    return {f"prompts/{sk.VARIANTS[v]}.{lang}.md": sk.prompt_block(v, lang) for v in sk.VARIANTS for lang in sk.LANGS}


def test_variants_split_the_reply_section_of_the_rule_block():
    prompt = (cn.ROOT / "prompts" / "system-prompt.md").read_text(encoding="utf-8")
    assert cn.check_prompt_variants(prompt, _variant_texts()) == []
    sentences, fmt = sk.prompt_block("sentences", "ko"), sk.prompt_block("format", "ko")
    assert "굵은 글씨와 표" in fmt and "굵은 글씨" not in sentences and "첫 문장에 답" in sentences


def test_check_prompt_variants_flags_drift():
    prompt = (cn.ROOT / "prompts" / "system-prompt.md").read_text(encoding="utf-8")
    texts = _variant_texts()
    ko, en = "prompts/sentence-rules.ko.md", "prompts/sentence-rules.en.md"
    dropped = {**texts, ko: texts[ko].replace("질문을 되풀이하지 마세요.\n", "")}
    problems = cn.check_prompt_variants(prompt, dropped)
    assert "답변 판본에 규칙 블록의 답변 절 문장이 없습니다: 질문을 되풀이하지 마세요." in problems
    assert f"{en}의 줄 구조가 {ko}와 다릅니다" in problems
    added = {**texts, ko: texts[ko].replace("질문을 되풀이하지 마세요.", "질문을 되풀이하지 마세요. 짧게 쓰세요.")}
    assert cn.check_prompt_variants(prompt, added) == [
        "답변 판본에 규칙 블록의 답변 절 문장이 없습니다: 질문을 되풀이하지 마세요.",
        "답변 판본의 문장이 규칙 블록의 답변 절에 없습니다: 질문을 되풀이하지 마세요. 짧게 쓰세요."]
    extra = '사실을 담지 않은 말("원활하게", "강력한", "손쉽게")과 번역투("~에 대해", "~를 통해", "~로 인해")를 지우세요.'
    assert extra in cn.REPLY_EXTRA and extra in texts[ko]
    no_slop = {**texts, ko: texts[ko].replace(extra + "\n", "")}
    assert f"답변 판본에 규칙 블록의 답변 절 문장이 없습니다: {extra}" in cn.check_prompt_variants(prompt, no_slop)
    assert cn.check_prompt_variants(prompt.replace(extra, "슬롭을 지우세요."), texts)[0] == (
        f"규칙 블록에 답변에도 적용하는 문장이 없습니다: {extra}")
    quoted = {**texts, en: texts[en].replace('"하지만", ', "")}
    assert cn.check_prompt_variants(prompt, quoted) == [f"{en} 5번 줄의 따옴표 안 한국어가 {ko}와 다릅니다"]


def test_variants_mapping_is_read_only():
    try:
        sk.VARIANTS["full"] = "system-prompt"
    except TypeError:
        return
    raise AssertionError("VARIANTS는 바꿀 수 없어야 합니다")


def test_package_exports_the_linter():
    assert sk.lint_detail("배포를 진행합니다.\n", config={})[0]["category"] == "light_verb"
    assert sk.lint is sk.ko_lint.lint and sk.reader_check is sk.ko_lint.reader_check
    reply = sk.lint_detail("**네** 됩니다.\n", "reply", config={}, formatting=False)
    assert [h["category"] for h in reply] == []


def test_old_evals_path_gives_the_package_module():
    import ko_lint
    import ko_rules
    assert ko_lint is sk.ko_lint and ko_rules is sk.ko_rules
    assert sk.ko_terms.TERMS_JSON.is_file() and sk.ko_rules.SLOP_TSV.is_file()
