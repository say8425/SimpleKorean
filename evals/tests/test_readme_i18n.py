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


SCENARIOS = [{"id": "readme-intro", "type": "descriptive"}]
EMPTY = "<!-- example:start -->\n\n<!-- example:end -->\n\n<!-- benchmark:start x -->\n\n<!-- benchmark:end -->\n"


def _results(d):
    """ROOT 아래 임시 결과 디렉터리에 답변 두 개, 판정 하나, 문서 세 개를 쓴다."""
    root = Path(d)
    (root / "reply").mkdir()
    (root / "reply" / "baseline__oom__r1.txt").write_text("**네** — 메모리가 부족합니다.\n\n- 한도\n", encoding="utf-8")
    (root / "reply" / "plain__oom__r1.txt").write_text("메모리 한도를 넘어서 파드가 끝났습니다.", encoding="utf-8")
    (root / "judge").mkdir()
    (root / "judge" / "oom__r1.json").write_text(json.dumps({"winner": "plain"}), encoding="utf-8")
    (root / "docs").mkdir()
    for cond, text in (("baseline", "메세지를 보냅니다."), ("plain", "메시지를 보냅니다."), ("strict", "메시지를 보냅니다.")):
        record = {"condition": cond, "scenario": "readme-intro", "text": text}
        (root / "docs" / f"{cond}__readme-intro__r1.json").write_text(json.dumps(record, ensure_ascii=False),
                                                                        encoding="utf-8")
    return root


def _site(d):
    """README 다섯 개가 빈 블록 표시만 가진 임시 레포 뼈대."""
    site = Path(d) / "site"
    for lang in i18n.LANGS:
        path = site / i18n.README[lang]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(EMPTY, encoding="utf-8")
    return site


def _exit_message(call):
    """call이 SystemExit로 끝나면 그 메시지를 돌려주고, 아니면 시험을 실패시킨다."""
    try:
        call()
    except SystemExit as err:
        return str(err)
    raise AssertionError("SystemExit가 나야 합니다")


def test_benchmark_blocks_link_from_each_readme_folder():
    with tempfile.TemporaryDirectory(dir=str(ROOT / "evals")) as d:
        root = _results(d)
        rel = root.resolve().relative_to(ROOT).as_posix()
        stats = report.benchmark_stats(root, SCENARIOS)
        ko = report.render_readme_block(stats, "ko")
        assert ko == report.readme_block(root, SCENARIOS)
        assert f"[`{rel}/RESULTS.md`]({rel}/RESULTS.md)" in ko and "| 엄격 모드 |" in ko
        for lang in i18n.LANGS[1:]:
            block = report.render_readme_block(stats, lang)
            assert f"[`{rel}/RESULTS.md`](../{rel}/RESULTS.md)" in block, lang
            assert f"| {i18n.TEXT[lang]['labels']['strict']} |" in block, lang
        assert "100 %" in report.render_readme_block(stats, "es")


def test_example_blocks_keep_the_korean_outputs():
    with tempfile.TemporaryDirectory(dir=str(ROOT / "evals")) as d:
        root = _results(d)
        ko = mx.readme_example(root, "ko")
        assert ko == mx.readme_example(root)
        for lang in i18n.LANGS[1:]:
            body = mx.readme_example(root, lang)
            assert mx.SOURCE_BLOCK.findall(body) == mx.SOURCE_BLOCK.findall(ko), lang
            assert "](../examples/before-after.md)" in body, lang


def test_update_readmes_fills_every_language():
    with tempfile.TemporaryDirectory(dir=str(ROOT / "evals")) as d:
        root, site = _results(d), _site(d)
        rel = root.resolve().relative_to(ROOT).as_posix()
        mx.update_readmes(root, root=site)
        report.update_readmes(root, SCENARIOS, root=site)
        for lang in i18n.LANGS:
            text = (site / i18n.README[lang]).read_text(encoding="utf-8")
            assert f"<!-- benchmark:start {rel} -->" in text, lang
            assert mx.EXAMPLE_BLOCK.search(text).group(1) == mx.readme_example(root, lang), lang
            assert report.README_BLOCK.search(text).group(2) == report.readme_block(root, SCENARIOS, lang), lang


def test_update_readmes_stops_before_writing_when_a_readme_is_broken():
    with tempfile.TemporaryDirectory(dir=str(ROOT / "evals")) as d:
        root, site = _results(d), _site(d)
        (site / "docs/README.ja.md").write_text("블록 없음\n", encoding="utf-8")
        assert "docs/README.ja.md" in _exit_message(lambda: mx.update_readmes(root, root=site))
        assert "docs/README.ja.md" in _exit_message(lambda: report.update_readmes(root, SCENARIOS, root=site))
        assert (site / "README.md").read_text(encoding="utf-8") == EMPTY
        (site / "docs/README.ja.md").unlink()
        assert "docs/README.ja.md" in _exit_message(lambda: mx.update_readmes(root, root=site))
        assert "docs/README.ja.md" in _exit_message(lambda: report.update_readmes(root, SCENARIOS, root=site))
