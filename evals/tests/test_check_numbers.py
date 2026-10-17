import json
import re
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import check_numbers as cn  # noqa: E402
import hits  # noqa: E402  check_numbers가 evals/calibration을 경로에 넣는다
import make_examples as mx  # noqa: E402
import readme_i18n as i18n  # noqa: E402
import report  # noqa: E402

BLOCK = '서술형으로 쓰세요. em-dash를 쓰지 마세요. 첫 문장에 답을 쓰세요. 코드는 바꾸지 마세요. "확인하다" 하나로 쓰세요. 레포지토리. 굵은 글씨와 표는 쓰지 마세요.'
SKILL = f'---\nname: simple-korean\nmetadata:\n  version: "1.0.0"\n---\n{BLOCK}\n'
ISO = {"found": True, "claude_code_version": "2.1.294", "model": "m", "mcp_servers": [], "plugins": [],
       "output_style": "default", "memory_paths": []}


def test_quote_round_trip_keeps_blank_lines_and_markers():
    text = "첫 줄\n\n> 이미 인용\n  들여쓴 줄\n- 목록 **굵게**\n"
    assert mx.unquote(mx.quote(text)) == text.rstrip("\n")
    assert mx.quote("a\n\nb") == "> a\n>\n> b"


def test_check_rule_block_flags_drift_and_missing_phrases():
    prompt = f"# 시스템 프롬프트\n\n---\n{BLOCK}\n---\n\n짧은 판본\n"
    style = f"---\nname: x\n---\n{BLOCK}\n"
    assert cn.check_rule_block(prompt, style, SKILL) == []
    assert any("규칙 블록이 다릅니다" in p for p in cn.check_rule_block(prompt, style + "더함\n", SKILL))
    missing = cn.check_rule_block(prompt, style, SKILL.replace("레포지토리", "저장소"))
    assert missing == ["SKILL.md에 핵심 문구가 없습니다: 레포지토리"]


def test_check_triggers_reads_every_phrase_from_the_description():
    phrases = ", ".join(f'"{t}"' for t in cn.SKILL_TRIGGERS).replace("Simple Korean", "Simple\n  Korean")
    full = f"---\nname: x\ndescription: |\n  설명입니다.\n  {phrases}\nlicense: MIT\n---\n본문\n"
    assert cn.check_triggers(full) == []
    body_only = "---\nname: x\ndescription: 짧습니다.\n---\n" + " ".join(cn.SKILL_TRIGGERS) + "\n"
    assert len(cn.check_triggers(body_only)) == len(cn.SKILL_TRIGGERS)
    assert {"문서 다듬어 줘", "Simple Korean", "controlled language"} <= set(cn.SKILL_TRIGGERS)


def test_check_versions_requires_one_value_everywhere():
    texts = {
        "skills/simple-korean/SKILL.md": SKILL,
        ".claude-plugin/plugin.json": '{"version": "1.0.0"}',
        ".claude-plugin/marketplace.json": '{"plugins": [{"version": "1.0.0"}]}',
        ".codex-plugin/plugin.json": '{"version": "1.0.0"}',
        ".release-please-manifest.json": '{\n  ".": "1.0.0"\n}\n',
        "CHANGELOG.md": "# 변경 기록\n\n## 1.0.0, 2026-10-09\n",
    }
    assert "README.md" not in cn.VERSION_PATTERNS
    assert cn.check_versions(texts) == []
    assert cn.check_versions({**texts, "CHANGELOG.md": "## 1.0.1, 2026-10-10\n"}) != []
    assert cn.check_versions({**texts, ".release-please-manifest.json": '{".": "1.0.1"}'}) != []
    bumped = {name: text.replace("1.0.0", "1.0.1") for name, text in texts.items()}
    released = ("# 변경 기록\n\n## [1.0.1](https://github.com/say8425/SimpleKorean/compare/v1.0.0...v1.0.1) (2026-10-20)\n\n"
                "### 고친 것\n\n* 고친다\n\n## 1.0.0, 2026-10-09\n")
    assert cn.check_versions({**bumped, "CHANGELOG.md": released}) == []


def _jsonpath(data, path):
    """'$.plugins[0].version' 같은 단순한 JSONPath를 따라간다."""
    for key, index in re.findall(r"\.(\w+)|\[(\d+)\]", path[1:]):
        data = data[key] if key else data[int(index)]
    return data


def test_release_config_bumps_every_versioned_file():
    config = json.loads((cn.ROOT / "release-please-config.json").read_text(encoding="utf-8"))
    package = config["packages"]["."]
    assert package["release-type"] == "simple" and config["include-component-in-tag"] is False
    version = json.loads((cn.ROOT / ".release-please-manifest.json").read_text(encoding="utf-8"))["."]
    bumped = set()
    for item in package["extra-files"]:
        if isinstance(item, str):
            bumped.add(item)
            continue
        bumped.add(item["path"])
        data = json.loads((cn.ROOT / item["path"]).read_text(encoding="utf-8"))
        assert _jsonpath(data, item["jsonpath"]) == version, item
    assert bumped == set(cn.VERSION_PATTERNS) - {"CHANGELOG.md", ".release-please-manifest.json"}
    skill = (cn.ROOT / "skills/simple-korean/SKILL.md").read_text(encoding="utf-8")
    assert f'  version: "{version}" # x-release-please-version\n' in skill


def _results(d):
    """ROOT 아래 임시 결과 디렉터리에 답변, 판정, 문서, meta.json을 쓴다."""
    root = Path(d)
    (root / "reply").mkdir()
    (root / "reply" / "baseline__oom__r1.txt").write_text("**네** — 메모리가 부족합니다.\n\n- 한도\n", encoding="utf-8")
    (root / "reply" / "plain__oom__r1.txt").write_text("메모리 한도를 넘어서 파드가 끝났습니다.", encoding="utf-8")
    (root / "judge").mkdir()
    (root / "judge" / "oom__r1.json").write_text(json.dumps({"winner": "plain"}), encoding="utf-8")
    (root / "docs").mkdir()
    for cond in ("baseline", "plain", "strict"):
        record = {"condition": cond, "scenario": "readme-intro", "text": "메세지를 보냅니다. 서버에 대해 설명합니다."}
        (root / "docs" / f"{cond}__readme-intro__r1.json").write_text(json.dumps(record, ensure_ascii=False), encoding="utf-8")
    trouble = {"baseline": "## 문제 해결\n\n**연결 타임아웃**\n방화벽을 확인해 보세요.",
               "plain": "## 연결 타임아웃\n\n1. 방화벽 규칙을 확인하세요.", "strict": "## 연결 타임아웃\n\n1. 방화벽 규칙을 확인해야 합니다."}
    for cond, text in trouble.items():
        record = {"condition": cond, "scenario": "troubleshooting", "text": text}
        (root / "docs" / f"{cond}__troubleshooting__r1.json").write_text(json.dumps(record, ensure_ascii=False),
                                                                           encoding="utf-8")
    meta = {"date": "2099-01-01", "model": "m", "effort": "low", "judge_model": "j", "isolation": ISO, "isolation_problems": []}
    (root / "meta.json").write_text(json.dumps(meta), encoding="utf-8")
    return root


def test_readme_example_is_verbatim_and_edits_are_caught():
    with tempfile.TemporaryDirectory(dir=str(cn.ROOT / "evals")) as d:
        readme = mx.replace_example_block("앞\n<!-- example:start -->\n\n<!-- example:end -->\n", mx.readme_example(_results(d)))
        assert cn.check_examples(readme, "") == []
        assert "<!-- simple-korean: off -->\n> ## 문제 해결\n>\n> **연결 타임아웃**" in readme
        edited = readme.replace("방화벽 규칙을 확인하세요", "방화벽 규칙을 확인해요")
        assert any("인용한 글이 원본과 다릅니다" in p for p in cn.check_examples(edited, ""))
    assert cn.check_examples("빈 README", "") == ["README.md에 원본 인용 블록이 없습니다"]


def test_reply_sources_are_checked_verbatim_too():
    with tempfile.TemporaryDirectory(dir=str(cn.ROOT / "evals")) as d:
        rel = (_results(d) / "reply" / "baseline__oom__r1.txt").resolve().relative_to(cn.ROOT).as_posix()
        block = mx.source_block(rel)
        assert "> **네** — 메모리가 부족합니다.\n>\n> - 한도" in block
        assert mx.check_sources(block) == []
        assert mx.check_sources(block.replace("**네**", "네")) == [f"{rel}: 인용한 글이 원본과 다릅니다"]


def test_readme_pick_is_pre_registered_and_has_no_wide_code_line():
    assert mx.README_PICK in {pick[:2] for pick in mx.DOC_PICKS}
    with tempfile.TemporaryDirectory(dir=str(cn.ROOT / "evals")) as d:
        root = _results(d)
        assert mx.pick_problems(root) == []
        path = root / "docs" / "plain__troubleshooting__r1.json"
        record = json.loads(path.read_text(encoding="utf-8"))
        def with_code(line):
            text = record["text"] + f"\n\n```bash\n{line}\n```"
            path.write_text(json.dumps({**record, "text": text}, ensure_ascii=False), encoding="utf-8")
            return [p for p in mx.pick_problems(root) if "넓은 줄" in p]
        # 칸 안에 드는 짧은 코드 줄은 괜찮다
        assert with_code("sqlpipe run --timeout 30s ...") == []
        assert with_code("x" * mx.CELL_CODE_COLUMNS) == []
        assert with_code("x" * (mx.CELL_CODE_COLUMNS + 1)) != []
        # 한글은 두 칸으로 센다
        assert with_code("가" * (mx.CELL_CODE_COLUMNS // 2 + 1)) != []
        assert mx.wide_code_lines("~~~\n" + "x" * 60 + "\n```\n" + "y" * 60 + "\n~~~\n" + "z" * 60) == ["x" * 60, "y" * 60]
        # 네 개짜리 울타리 안의 세 개짜리 울타리는 닫지 않는다
        assert mx.wide_code_lines("````\n```\n" + "a" * 60 + "\n```\n````\n" + "b" * 60) == ["a" * 60]


def test_check_benchmark_catches_stale_numbers_and_missing_changelog_path():
    scenarios = [{"id": "readme-intro", "type": "descriptive"}, {"id": "troubleshooting", "type": "procedural"}]
    with tempfile.TemporaryDirectory(dir=str(cn.ROOT / "evals")) as d:
        root = _results(d)
        rel = root.resolve().relative_to(cn.ROOT).as_posix()
        readme = report.replace_readme_block("문서와 답변은 `m`이 쓰고 판정은 `j`가 했습니다.\n"
                                             "<!-- benchmark:start x -->\n\n<!-- benchmark:end -->\n", root,
                                             report.readme_block(root, scenarios))
        (root / "RESULTS.md").write_text(report.results_md(root, scenarios), encoding="utf-8")
        changelog = f"결과는 {rel}/RESULTS.md에 있습니다."
        assert cn.check_benchmark(readme, changelog, scenarios, require_easy=False) == []
        stale = readme.replace("| 스킬 없음 | 1 |", "| 스킬 없음 | 2 |", 1)
        assert any("README.md 벤치마크 블록" in p for p in cn.check_benchmark(stale, changelog, scenarios, require_easy=False))
        assert any("CHANGELOG.md가 측정 결과" in p for p in cn.check_benchmark(readme, "", scenarios, require_easy=False))
        no_judge = readme.replace("`j`", "Claude")
        assert any("판정 모델 `j`" in p for p in cn.check_benchmark(no_judge, changelog, scenarios, require_easy=False))
    assert cn.check_benchmark("블록 없음", "", scenarios) == ["README.md에 벤치마크 블록이 없습니다"]


def test_latest_release_date_reads_the_first_entry_in_either_form():
    old = "# 변경 기록\n\n항목마다 적습니다.\n\n## 1.0.0, 2026-10-10\n\n- 처음\n\n### 보정\n\n- 줄\n"
    assert cn.latest_release_date(old) == "2026-10-10"
    new = old.replace("## 1.0.0, 2026-10-10", "## [1.1.0](https://github.com/say8425/SimpleKorean/compare/v1.0.0...v1.1.0)"
                      " (2026-11-20)\n\n### 기능\n\n* 더한다 ([#4](https://github.com/say8425/SimpleKorean/issues/4))\n\n"
                      "## 1.0.0, 2026-10-10")
    assert cn.latest_release_date(new) == "2026-11-20"
    assert cn.latest_release_date("# 변경 기록\n") is None


def test_unreleased_means_strictly_after_the_latest_release():
    changelog = "# 변경 기록\n\n## 1.0.0, 2026-10-10\n"
    assert cn.unreleased("2026-10-11", changelog)
    assert not cn.unreleased("2026-10-10", changelog)
    assert not cn.unreleased("2026-10-08", changelog)
    assert not cn.unreleased("2026-10-11", "# 변경 기록\n")


def test_check_benchmark_skips_the_changelog_path_for_unreleased_results():
    scenarios = [{"id": "readme-intro", "type": "descriptive"}, {"id": "troubleshooting", "type": "procedural"}]
    with tempfile.TemporaryDirectory(dir=str(cn.ROOT / "evals")) as d:
        root = _results(d)
        readme = report.replace_readme_block("문서와 답변은 `m`이 쓰고 판정은 `j`가 했습니다.\n"
                                             "<!-- benchmark:start x -->\n\n<!-- benchmark:end -->\n", root,
                                             report.readme_block(root, scenarios))
        (root / "RESULTS.md").write_text(report.results_md(root, scenarios), encoding="utf-8")
        same_day = "# 변경 기록\n\n## 1.0.0, 2099-01-01\n"
        earlier = "# 변경 기록\n\n## 1.0.0, 2098-12-31\n"
        found = cn.check_benchmark(readme, same_day, scenarios, require_easy=False)
        assert any("CHANGELOG.md가 측정 결과" in p and "릴리스 항목" in p for p in found)
        assert cn.check_benchmark(readme, earlier, scenarios, require_easy=False) == []


def _calibration(d, date="2026-10-09"):
    """임시 보정 디렉터리에 기준선 문서 하나, hits.tsv, RECORD.md를 쓰고 (디렉터리, RECORD.md 본문)을 돌려준다."""
    cal, base = Path(d), Path(d) / "baseline"
    (base / "docs").mkdir(parents=True)
    (base / "reply").mkdir()
    record = {"text": "이 문서는 sqlpipe에 대해 설명합니다.\n", "condition": "baseline", "scenario": "x",
              "type": "descriptive", "run": 1}
    (base / "docs" / "baseline__x__r1.json").write_text(json.dumps(record, ensure_ascii=False), encoding="utf-8")
    (base / "meta.json").write_text(json.dumps({"date": date, "model": "m", "effort": "low"}), encoding="utf-8")
    rows = [{**r, "label": "TP"} for r in hits.doc_rows(base) + hits.reply_rows(base)]
    (cal / "hits.tsv").write_text(hits.to_tsv(rows), encoding="utf-8")
    text = hits.record_md(base, rows)
    (cal / "RECORD.md").write_text(text, encoding="utf-8")
    return cal, text


def test_check_calibration_rebuilds_record_and_needs_changelog_lines():
    with tempfile.TemporaryDirectory() as d:
        cal, text = _calibration(d)
        lines = text.split("## CHANGELOG에 옮길 줄", 1)[1].strip()
        assert cn.check_calibration(lines, cal) == []
        assert any("CHANGELOG.md에 보정 줄이 없습니다" in p for p in cn.check_calibration("", cal))
        (cal / "RECORD.md").write_text(text.replace("그대로입니다", "바뀌었습니다"), encoding="utf-8")
        assert any(p.startswith("evals/calibration/RECORD.md:") for p in cn.check_calibration(lines, cal))


def test_check_calibration_skips_changelog_lines_for_an_unreleased_record():
    with tempfile.TemporaryDirectory() as d:
        cal, _ = _calibration(d, date="2026-10-09")
        found = cn.check_calibration("# 변경 기록\n\n## 1.0.0, 2026-10-09\n", cal)
        assert any("CHANGELOG.md에 보정 줄이 없습니다" in p for p in found)
        assert cn.check_calibration("# 변경 기록\n\n## 1.0.0, 2026-10-08\n", cal) == []


def test_main_reports_missing_files():
    old = cn.ROOT
    with tempfile.TemporaryDirectory() as d:
        cn.ROOT = Path(d)
        try:
            assert cn.main() == 1
        finally:
            cn.ROOT = old


def test_check_block_size_matches_the_rule_block():
    prompt = f"# 시스템 프롬프트\n\n---\n{BLOCK}\n---\n"
    n = len(BLOCK)
    assert cn.check_block_size(f"훅은 세션마다 규칙 블록 {n:,}자를 넣습니다.", prompt) == []
    assert cn.check_block_size(f"훅은 세션마다 규칙 블록 {n + 1:,}자를 넣습니다.", prompt) != []


def _readme(lang, body):
    """언어 선택 줄, 본문, 빈 블록 표시로 된 작은 README."""
    return (f"{i18n.language_line(lang)}\n\n{body}\n\n"
            "<!-- example:start -->\n\n<!-- example:end -->\n\n"
            "<!-- benchmark:start x -->\n\n<!-- benchmark:end -->\n")


def test_structure_matches_headings_and_links():
    ko = _readme("ko", '## 설치\n\n[`SKILL.md`](skills/simple-korean/SKILL.md)와 <a href="LICENSE">MIT</a>\n\n## 기여\n')
    en = _readme("en", '## Install\n\n[`SKILL.md`](../skills/simple-korean/SKILL.md) and <a href="../LICENSE">MIT</a>\n\n'
                       '## Contributing\n')
    assert cn.check_readme_structure(ko, "ko", ko) == []
    assert cn.check_readme_structure(ko, "en", en) == []
    assert any("제목 수준" in p for p in cn.check_readme_structure(ko, "en", en.replace("## Contributing\n", "")))
    no_prefix = en.replace("](../skills", "](skills")
    assert any("../가 없습니다" in p and "skills/simple-korean/SKILL.md" in p
               for p in cn.check_readme_structure(ko, "en", no_prefix))
    found = cn.check_readme_structure(ko, "en", en.replace("simple-korean/SKILL.md", "simple-korean/NOPE.md"))
    assert any("레포 링크가 한국어판과 다릅니다" in p for p in found)
    assert any("링크한 파일이 없습니다" in p for p in found)


def test_structure_ignores_code_quotes_external_links_and_anchors():
    body = ("## 설치\n\n```bash\n# 주석은 제목이 아니다\n[가짜](nope.md)\n```\n\n> ## 인용 안의 제목\n> [인용](nope.md)\n\n"
            "`[코드](nope.md)`와 [웹](https://example.com)과 [앵커](#설치)\n\n[규칙](skills/simple-korean/SKILL.md#규칙)\n")
    ko = _readme("ko", body)
    assert cn.readme_outline(ko, "ko")[:2] == ([2], ["skills/simple-korean/SKILL.md#규칙"])
    assert cn.check_readme_structure(ko, "ko", ko) == []


def test_structure_needs_the_exact_language_line_and_single_markers():
    ko = _readme("ko", "## 설치\n")
    spaced = ko.replace(" | ", "|", 1)
    assert any("언어 선택 줄" in p and i18n.language_line("ko") in p for p in cn.check_readme_structure(ko, "ko", spaced))
    doubled = ko + "<!-- example:start -->\n"
    assert any("example:start" in p for p in cn.check_readme_structure(ko, "ko", doubled))


def test_check_block_size_uses_each_language_phrase():
    big = "\n".join([BLOCK] * 40)
    prompt = f"# 시스템 프롬프트\n\n---\n{big}\n---\n"
    n = len(big)
    assert n >= 1000
    assert cn.check_block_size(f"It adds a rule block of {n:,} characters.", prompt, "en") == []
    assert cn.check_block_size(f"Añade un bloque de reglas de {n} caracteres.", prompt, "es") == []
    assert cn.check_block_size(f"Añade un bloque de reglas de {n:,} caracteres.", prompt, "es") != []


def test_check_example_block_compares_the_sentences_too():
    with tempfile.TemporaryDirectory(dir=str(cn.ROOT / "evals")) as d:
        root = _results(d)
        empty = "<!-- example:start -->\n\n<!-- example:end -->\n"
        for lang in i18n.LANGS:
            assert cn.check_example_block(mx.replace_example_block(empty, mx.readme_example(root, lang)), lang, root) == []
        ko = mx.replace_example_block(empty, mx.readme_example(root, "ko"))
        edited = ko.replace("스킬 없이 쓴 문서", "스킬 없이 만든 문서")
        assert any("README.md 보기 블록" in p for p in cn.check_example_block(edited, "ko", root))
        assert cn.check_example_block("블록 없음", "en", root) == ["docs/README.en.md에 보기 블록이 없습니다"]


def test_check_translation_passes_a_generated_translation():
    scenarios = [{"id": "readme-intro", "type": "descriptive"}, {"id": "troubleshooting", "type": "procedural"}]
    prompt = f"---\n{BLOCK}\n---\n"
    with tempfile.TemporaryDirectory(dir=str(cn.ROOT / "evals")) as d:
        root = _results(d)
        (root / "RESULTS.md").write_text("결과\n", encoding="utf-8")
        rel = root.resolve().relative_to(cn.ROOT).as_posix()
        stats = report.benchmark_stats(root, scenarios)

        def page(lang):
            size = i18n.TEXT[lang]["block_size"].format(n=i18n.grouped(len(BLOCK), lang))
            text = (f"{i18n.language_line(lang)}\n\n`m`, `j`, {size}\n\n## A\n\n"
                    "<!-- example:start -->\n\n<!-- example:end -->\n\n"
                    f"<!-- benchmark:start {rel} -->\n\n<!-- benchmark:end -->\n")
            text = mx.replace_example_block(text, mx.readme_example(root, lang))
            return report.replace_readme_block(text, root, report.render_readme_block(stats, lang))

        ko, en = page("ko"), page("en")
        assert cn.check_translation("en", en, ko, scenarios, prompt, stats) == []
        stale = en.replace(f"benchmark:start {rel}", "benchmark:start evals/results/2026-10-08")
        assert any("결과 경로" in p for p in cn.check_translation("en", stale, ko, scenarios, prompt, stats))


def test_check_translation_reports_missing_korean_block_without_crashing():
    scenarios = [{"id": "readme-intro", "type": "descriptive"}, {"id": "troubleshooting", "type": "procedural"}]
    en = "<!-- benchmark:start evals/results/x -->\n\n<!-- benchmark:end -->\n"
    assert cn.check_translation("en", en, "한국어판에 블록 없음", scenarios, "") == ["README.md에 벤치마크 블록이 없습니다"]


def test_translation_problems_names_missing_files():
    old = cn.ROOT
    with tempfile.TemporaryDirectory() as d:
        cn.ROOT = Path(d)
        try:
            assert cn.translation_problems("en") == ["파일이 없습니다: README.md", "파일이 없습니다: docs/README.en.md"]
        finally:
            cn.ROOT = old


def test_main_requires_every_readme():
    assert {i18n.README[lang] for lang in i18n.LANGS} <= set(cn.REQUIRED)
