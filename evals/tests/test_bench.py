import json
import re
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import bench_common as bc  # noqa: E402
import report  # noqa: E402
import run_bench  # noqa: E402
import run_reply_bench  # noqa: E402


def test_claude_cmd_isolates_settings_mcp_and_tools():
    cmd = bc.claude_cmd("질문", system="규칙")
    assert cmd[:3] == ["claude", "-p", "질문"]
    i = cmd.index("--setting-sources")
    assert cmd[i + 1] == "" and "--strict-mcp-config" in cmd
    assert cmd[cmd.index("--disallowedTools") + 1].startswith("Bash,Read,Write,Edit")
    assert cmd[cmd.index("--append-system-prompt") + 1] == "규칙"
    assert "--verbose" in bc.claude_cmd("q", output="stream-json")


def test_parse_result_accepts_object_or_event_list():
    assert bc.parse_result('{"type": "result", "result": "A"}')["result"] == "A"
    events = [{"type": "system"}, {"type": "result", "result": "B"}]
    assert bc.parse_result(json.dumps(events))["result"] == "B"


def test_call_claude_raises_on_failure_and_returns_text():
    ok = SimpleNamespace(returncode=0, stdout='{"type":"result","result":"답","usage":{"input_tokens":5},"total_cost_usd":0.01}', stderr="")
    got = bc.call_claude("q", run=lambda *a, **k: ok)
    assert got["text"] == "답" and got["input_tokens"] == 5 and got["cost_usd"] == 0.01
    bad = SimpleNamespace(returncode=1, stdout="", stderr="boom")
    try:
        bc.call_claude("q", run=lambda *a, **k: bad)
    except RuntimeError as err:
        assert "boom" in str(err)
    else:
        raise AssertionError("RuntimeError가 나야 합니다")


def test_call_claude_runs_given_command():
    seen = []

    def run(cmd, **kwargs):
        seen.append(cmd)
        return SimpleNamespace(returncode=0, stdout='{"type":"result","result":"답"}', stderr="")

    assert bc.call_claude("q", run=run, cmd=["claude", "-p", "q", "--plugin-dir", "x"])["text"] == "답"
    assert seen[0][-2:] == ["--plugin-dir", "x"]


def test_meta_date_uses_dated_directory_or_today():
    assert bc.meta_date("evals/results/2026-10-09") == "2026-10-09"
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", bc.meta_date("evals/calibration/baseline"))


def test_isolation_problems_flags_leaks():
    clean = bc.init_summary(json.dumps({"type": "system", "subtype": "init", "mcp_servers": [],
                                        "plugins": [{"source": "cc-plugin-telemetry@builtin"}],
                                        "output_style": "default", "memory_paths": {"auto": "/x"}}))
    assert bc.isolation_problems(clean) == []
    leaky = bc.init_summary(json.dumps({"type": "system", "subtype": "init", "mcp_servers": [{"name": "slack"}],
                                        "plugins": [{"source": "x@market"}], "output_style": "simple-korean",
                                        "memory_paths": {"auto": "/x", "user": "/y"}}))
    assert len(bc.isolation_problems(leaky)) == 4
    assert bc.isolation_problems(bc.init_summary("")) == ["init 이벤트가 없습니다"]


def test_build_prompt_conditions():
    sc = {"id": "x", "type": "descriptive", "prompt": "과제 본문"}
    assert run_bench.build_prompt(sc, "baseline") == "과제 본문"
    plain = run_bench.build_prompt(sc, "plain")
    assert plain.startswith(run_bench.LEAD) and "## 답변" in plain and "과제: 과제 본문" in plain
    assert "name: simple-korean" not in plain
    strict = run_bench.build_prompt(sc, "strict")
    assert "엄격 모드: 문장 끝, 접속어, 단어" in strict and "과제: 엄격 모드로 쓰세요. 과제 본문" in strict


def test_generate_writes_and_resumes():
    calls = []

    def fake(prompt, **kwargs):
        calls.append(prompt)
        return {"text": "본문입니다.", "model": "m", "effort": "low"}

    with tempfile.TemporaryDirectory() as d:
        scenarios = [{"id": "a", "type": "descriptive", "prompt": "p"}]
        run_bench.generate(d, scenarios, 1, call=fake, sleep=0)
        assert len(calls) == 3 and len(list(Path(d, "docs").glob("*.json"))) == 3
        run_bench.generate(d, scenarios, 1, call=fake, sleep=0)
        assert len(calls) == 3


def test_generate_only_requested_conditions():
    calls = []

    def fake(prompt, **kwargs):
        calls.append(prompt)
        return {"text": "본문입니다.", "model": "m", "effort": "low"}

    with tempfile.TemporaryDirectory() as d:
        run_bench.generate(d, [{"id": "a", "type": "descriptive", "prompt": "p"}], 1,
                           call=fake, sleep=0, conditions=("baseline",))
        assert calls == ["p"]
        assert [p.name for p in Path(d, "docs").iterdir()] == ["baseline__a__r1.json"]
    with tempfile.TemporaryDirectory() as d:
        run_reply_bench.generate(d, [{"id": "q", "prompt": "질문"}], 1, call=fake, sleep=0, conditions=("baseline",))
        assert [p.name for p in Path(d, "reply").iterdir()] == ["baseline__q__r1.txt"]


def test_parse_conditions_rejects_unknown():
    assert bc.parse_conditions("baseline", ("baseline", "plain")) == ("baseline",)
    assert bc.parse_conditions(" plain , baseline ", ("baseline", "plain")) == ("plain", "baseline")
    for bad in ("", "skill", "baseline,skill"):
        try:
            bc.parse_conditions(bad, ("baseline", "plain"))
        except SystemExit as err:
            assert "baseline, plain" in str(err)
        else:
            raise AssertionError(bad)


def test_reply_generate_uses_rule_block_only_for_plain():
    seen = []

    def fake(prompt, system=None, **kwargs):
        seen.append(system)
        return {"text": "답입니다."}

    with tempfile.TemporaryDirectory() as d:
        run_reply_bench.generate(d, [{"id": "q", "prompt": "질문"}], 1, call=fake, sleep=0)
        assert seen[0] is None and "레포지토리" in seen[1]
        assert sorted(p.name for p in Path(d, "reply").iterdir()) == ["baseline__q__r1.txt", "plain__q__r1.txt"]


def test_judge_parsing_and_combination():
    assert run_reply_bench.parse_winner('{"winner": "B"}') == "B"
    assert run_reply_bench.parse_winner("모르겠습니다") is None
    assert run_reply_bench.combine("B", "A") == "plain"
    assert run_reply_bench.combine("A", "B") == "baseline"
    assert run_reply_bench.combine("B", "B") == "tie"
    assert run_reply_bench.combine(None, "A") == "tie"
    assert run_reply_bench.combine("tie", "tie") == "tie"


def _fake_results(d):
    root = Path(d)
    (root / "reply").mkdir()
    (root / "reply" / "baseline__q__r1.txt").write_text("**네** — 그렇습니다.\n- 하나\n- 둘\n", encoding="utf-8")
    (root / "reply" / "plain__q__r1.txt").write_text("빌드가 실패한 이유는 디스크입니다.", encoding="utf-8")
    (root / "judge").mkdir()
    (root / "judge" / "q__r1.json").write_text(json.dumps({"winner": "plain"}), encoding="utf-8")
    (root / "docs").mkdir()
    for cond, text in (("baseline", "메세지를 보냅니다. 서버에 대해 설명합니다."), ("plain", "메시지를 보냅니다."), ("strict", "메시지를 보냅니다.")):
        (root / "docs" / f"{cond}__readme-intro__r1.json").write_text(
            json.dumps({"condition": cond, "scenario": "readme-intro", "text": text}, ensure_ascii=False), encoding="utf-8")
    return root


def test_report_tables_from_fake_results():
    with tempfile.TemporaryDirectory() as d:
        root = _fake_results(d)
        replies = report.reply_stats(root)
        assert replies["baseline"]["visible"] == 4 and replies["plain"]["visible"] == 0
        assert report.judge_stats(root) == {"plain": 1, "tie": 0, "baseline": 0, "n": 1}
        headline = report.render_headline(replies, report.judge_stats(root))
        assert "100% 줄었습니다(4개에서 0개)" in headline and "1쌍 가운데 1쌍에서 이겼고" in headline
        docs = report.doc_stats(root, [{"id": "readme-intro", "type": "descriptive"}])
        assert docs["baseline"]["errors"] == 1 and docs["baseline"]["translationese"] == 1
        table = report.render_doc_table(docs)
        assert table.splitlines()[2].startswith("| 스킬 없음 | 1 |")
        dist = report.spelling_distribution(root)
        assert dict(dist["message"]["baseline"]) == {"메세지": 1}
        assert "| message | 메세지 1 | 메시지 1 | 메시지 1 |" in report.render_spelling_table(dist)


def test_readme_block_fills_an_empty_template_block():
    readme = "앞\n<!-- benchmark:start evals/results/YYYY-MM-DD -->\n\n<!-- benchmark:end -->\n"
    with tempfile.TemporaryDirectory(dir=str(report.ROOT / "evals")) as d:
        new = report.replace_readme_block(readme, d, "표")
    assert "-->\n표\n<!-- benchmark:end -->" in new and "YYYY" not in new


def test_readme_block_round_trip():
    readme = "앞\n<!-- benchmark:start evals/results/old -->\n옛 내용\n<!-- benchmark:end -->\n뒤\n"
    with tempfile.TemporaryDirectory(dir=str(report.ROOT / "evals")) as d:
        new = report.replace_readme_block(readme, d, "새 내용")
        rel = Path(d).resolve().relative_to(report.ROOT).as_posix()
        assert f"<!-- benchmark:start {rel} -->\n새 내용\n<!-- benchmark:end -->" in new
        assert new.startswith("앞\n") and new.endswith("뒤\n")
