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


def test_table_headers_have_as_many_columns_as_their_separators():
    for lang in i18n.LANGS:
        for key, sep in (("reply_header", report.REPLY_SEP), ("doc_header", report.DOC_SEP),
                         ("polish_header", report.POLISH_SEP)):
            assert i18n.TEXT[lang][key].count("|") == sep.count("|"), (lang, key)


def test_korean_templates_keep_the_current_sentences():
    ko = i18n.TEXT["ko"]
    assert ko["block_size"].format(n=i18n.grouped(2271, "ko")) == "규칙 블록 2,271자"
    assert ko["longest"].format(n=18) == "18어절"
    assert ko["example_docs"].format(href="examples/before-after.md", diff="URL") == \
        "답변 예시와 나머지 문서 예시는 [`examples/before-after.md`](examples/before-after.md)에 있습니다. " \
        "예시마다 바뀐 곳은 [이 커밋의 diff](URL)에서 볼 수 있습니다."


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


PICK = mx.README_PICK[0]
SCENARIOS = [{"id": "readme-intro", "type": "descriptive"},
             {"id": PICK, "type": "procedural", "draft": "**초안** — 방화벽·보안 그룹을 확인해 보세요."}]
EMPTY = "<!-- example:start -->\n\n<!-- example:end -->\n\n<!-- benchmark:start x -->\n\n<!-- benchmark:end -->\n"


def _results(d):
    """ROOT 아래 임시 결과 디렉터리에 답변 두 개, 판정 하나, 문서 여섯 개를 쓴다."""
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
    trouble = {"baseline": "## 문제 해결\n\n**연결 타임아웃**\n방화벽을 확인해 보세요.",
               "plain": "## 연결 타임아웃\n\n1. 방화벽 규칙을 확인하세요.", "strict": "## 연결 타임아웃\n\n1. 방화벽 규칙을 확인해야 합니다."}
    for cond, text in trouble.items():
        record = {"condition": cond, "scenario": PICK, "text": text}
        (root / "docs" / f"{cond}__{PICK}__r1.json").write_text(json.dumps(record, ensure_ascii=False),
                                                                           encoding="utf-8")
    # 보기 표의 첫째 칸은 측정할 때 복사한 입력의 초안이다
    (root / "inputs").mkdir()
    (root / "inputs" / "scenarios.json").write_text(json.dumps(SCENARIOS, ensure_ascii=False), encoding="utf-8")
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


def test_example_block_is_a_three_column_table():
    with tempfile.TemporaryDirectory(dir=str(ROOT / "evals")) as d:
        root = _results(d)
        rel = root.resolve().relative_to(ROOT).as_posix()
        for lang in i18n.LANGS:
            body = mx.readme_example(root, lang)
            assert body.startswith("<table>\n<tr>\n<th width=\"34%\">"), lang
            labels = i18n.TEXT[lang]
            heads = [labels[k] for k in ("example_draft_head", "example_before", "example_after")]
            spots = [body.index(h) for h in heads]
            assert spots == sorted(spots) and spots[-1] < body.index("<td"), lang
            assert body.count('<td valign="top">\n\n<!-- draft: ') == 1, lang
            assert body.count('<td valign="top">\n\n<!-- source: ') == 2, lang
            assert body.count("<!-- simple-korean: on -->\n\n</td>") == 3, lang
            sources = [m[0] for m in mx.SOURCE_BLOCK.findall(body)]
            assert sources == [f"{rel}/docs/baseline__{PICK}__r1.json", f"{rel}/docs/plain__{PICK}__r1.json"], lang
            after_table = body.split("</table>", 1)[1]
            assert f"`{sources[0]}`" in after_table and f"`{sources[1]}`" in after_table, lang


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


def test_readme_pick_is_a_polish_task_with_a_draft():
    # README의 보기 설명과 칸 이름(다듬은 문서)은 보기 예시가 다듬기 과제라고 가정한다
    scenarios = json.loads((ROOT / "evals" / "scenarios.json").read_text(encoding="utf-8"))
    pick = next(s for s in scenarios if s["id"] == PICK)
    assert pick.get("draft"), pick


def test_example_table_puts_the_saved_draft_in_the_first_column():
    with tempfile.TemporaryDirectory(dir=str(ROOT / "evals")) as d:
        root = _results(d)
        draft = "**연결** — 방화벽·보안 그룹을 확인해 보세요."
        (root / "inputs" / "scenarios.json").write_text(
            json.dumps([{"id": PICK, "type": "procedural", "prompt": "다듬으세요.", "draft": draft}], ensure_ascii=False),
            encoding="utf-8")
        rel = mx.inputs_rel(root)
        for lang in i18n.LANGS:
            body = mx.readme_example(root, lang)
            assert i18n.TEXT[lang]["example_draft"].format(src=rel, href=i18n.link(lang, rel), id=PICK) in body, lang
            # 초안은 표의 첫째 칸이다. 표 밖에 따로 인용하지 않는다
            table = body[body.index("<table>"):body.index("</table>")]
            assert table.index(f"<!-- draft: {rel}#{PICK} -->") < table.index("<!-- source: "), lang
            assert body.count("<!-- draft: ") == 1 and table.count("<th ") == 3, lang
        body = mx.readme_example(root)
        assert mx.check_sources(body) == []
        assert mx.check_sources(body.replace("> **연결** —", "> 연결:")) == [f"{rel}#{PICK}: 인용한 초안이 원본과 다릅니다"]
        assert mx.pick_problems(root) == []
        before, after = (f"{root.resolve().relative_to(ROOT).as_posix()}/docs/{c}__{PICK}__r1.json" for c in ("baseline", "plain"))
        section = mx._section("초안 다듬기", before, after, "기본 모드", (rel, PICK))
        assert section.index(f"<!-- draft: {rel}#{PICK} -->") < section.index("전: 스킬 없음") and mx.check_sources(section) == []
        assert "> **연결** — 방화벽·보안 그룹을 확인해 보세요." in section
        assert mx.check_sources(section.replace("> **연결** —", "> 연결:")) == [f"{rel}#{PICK}: 인용한 초안이 원본과 다릅니다"]
        # 보기 과제에 초안이 없으면 보기 설명과 맞지 않는다
        (root / "inputs" / "scenarios.json").write_text(json.dumps([{"id": PICK, "type": "procedural"}]), encoding="utf-8")
        assert any("초안이 없습니다" in p for p in mx.pick_problems(root))
