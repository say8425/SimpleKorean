import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import check_numbers as cn  # noqa: E402
import hits  # noqa: E402  check_numbers가 evals/calibration을 경로에 넣는다
import make_examples as mx  # noqa: E402
import report  # noqa: E402

BLOCK = '서술형으로 답하세요. em-dash를 쓰지 마세요. 첫 문장에 답을 쓰세요. 코드는 바꾸지 마세요. "확인하다" 하나로 쓰세요. 레포지토리.'
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


def test_check_versions_requires_one_value_everywhere():
    texts = {
        "skills/simple-korean/SKILL.md": SKILL,
        ".claude-plugin/plugin.json": '{"version": "1.0.0"}',
        ".claude-plugin/marketplace.json": '{"plugins": [{"version": "1.0.0"}]}',
        ".codex-plugin/plugin.json": '{"version": "1.0.0"}',
        "README.md": "badge/version-1.0.0-blue",
        "CHANGELOG.md": "# 변경 기록\n\n## 1.0.0, 2026-10-09\n",
    }
    assert cn.check_versions(texts) == []
    assert cn.check_versions({**texts, "CHANGELOG.md": "## 1.0.1, 2026-10-10\n"}) != []
    assert cn.check_versions({**texts, "README.md": "배지 없음"}) != []


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
    meta = {"date": "2099-01-01", "model": "m", "effort": "low", "judge_model": "j", "isolation": ISO, "isolation_problems": []}
    (root / "meta.json").write_text(json.dumps(meta), encoding="utf-8")
    return root


def test_readme_example_is_verbatim_and_edits_are_caught():
    with tempfile.TemporaryDirectory(dir=str(cn.ROOT / "evals")) as d:
        readme = mx.replace_example_block("앞\n<!-- example:start -->\n\n<!-- example:end -->\n", mx.readme_example(_results(d)))
        assert cn.check_examples(readme, "") == []
        assert "<!-- simple-korean: off -->\n> **네** — 메모리가 부족합니다.\n>\n> - 한도" in readme
        edited = readme.replace("파드가 끝났습니다", "파드가 끝났어요")
        assert any("인용한 글이 원본과 다릅니다" in p for p in cn.check_examples(edited, ""))
    assert cn.check_examples("빈 README", "") == ["README.md에 원본 인용 블록이 없습니다"]


def test_check_benchmark_catches_stale_numbers_and_missing_changelog_path():
    scenarios = [{"id": "readme-intro", "type": "descriptive"}]
    with tempfile.TemporaryDirectory(dir=str(cn.ROOT / "evals")) as d:
        root = _results(d)
        rel = root.resolve().relative_to(cn.ROOT).as_posix()
        readme = report.replace_readme_block("<!-- benchmark:start x -->\n\n<!-- benchmark:end -->\n", root,
                                             report.readme_block(root, scenarios))
        (root / "RESULTS.md").write_text(report.results_md(root, scenarios), encoding="utf-8")
        changelog = f"결과는 {rel}/RESULTS.md에 있습니다."
        assert cn.check_benchmark(readme, changelog, scenarios, require_easy=False) == []
        stale = readme.replace("| 스킬 없음 | 1 |", "| 스킬 없음 | 2 |", 1)
        assert any("README 벤치마크 블록" in p for p in cn.check_benchmark(stale, changelog, scenarios, require_easy=False))
        assert any("CHANGELOG.md가 측정 결과" in p for p in cn.check_benchmark(readme, "", scenarios, require_easy=False))
    assert cn.check_benchmark("블록 없음", "", scenarios) == ["README.md에 벤치마크 블록이 없습니다"]


def test_check_calibration_rebuilds_record_and_needs_changelog_lines():
    with tempfile.TemporaryDirectory() as d:
        cal, base = Path(d), Path(d) / "baseline"
        (base / "docs").mkdir(parents=True)
        (base / "reply").mkdir()
        record = {"text": "이 문서는 sqlpipe에 대해 설명합니다.\n", "condition": "baseline", "scenario": "x",
                  "type": "descriptive", "run": 1}
        (base / "docs" / "baseline__x__r1.json").write_text(json.dumps(record, ensure_ascii=False), encoding="utf-8")
        (base / "meta.json").write_text(json.dumps({"date": "2026-10-09", "model": "m", "effort": "low"}), encoding="utf-8")
        rows = [{**r, "label": "TP"} for r in hits.doc_rows(base) + hits.reply_rows(base)]
        (cal / "hits.tsv").write_text(hits.to_tsv(rows), encoding="utf-8")
        text = hits.record_md(base, rows)
        (cal / "RECORD.md").write_text(text, encoding="utf-8")
        lines = text.split("## CHANGELOG에 옮길 줄", 1)[1].strip()
        assert cn.check_calibration(lines, cal) == []
        assert any("CHANGELOG.md에 보정 줄이 없습니다" in p for p in cn.check_calibration("", cal))
        (cal / "RECORD.md").write_text(text.replace("그대로입니다", "바뀌었습니다"), encoding="utf-8")
        assert any(p.startswith("evals/calibration/RECORD.md:") for p in cn.check_calibration(lines, cal))


def test_main_reports_missing_files():
    old = cn.ROOT
    with tempfile.TemporaryDirectory() as d:
        cn.ROOT = Path(d)
        try:
            assert cn.main() == 1
        finally:
            cn.ROOT = old
