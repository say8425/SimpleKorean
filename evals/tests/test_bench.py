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


def test_build_prompt_appends_the_draft():
    sc = {"id": "polish", "type": "procedural", "prompt": "초안을 다듬어 주세요.", "draft": "**초안** — 본문"}
    assert run_bench.build_prompt(sc, "baseline") == "초안을 다듬어 주세요.\n\n초안:\n\n**초안** — 본문\n\n(초안 끝)"
    # 초안 뒤의 지시(TAIL)를 초안으로 읽지 않도록 초안이 끝난 곳을 밝힌다
    assert "과제: 초안을 다듬어 주세요.\n\n초안:\n\n**초안** — 본문\n\n(초안 끝)" + run_bench.TAIL in run_bench.build_prompt(sc, "plain")
    assert "과제: 엄격 모드로 쓰세요. 초안을 다듬어 주세요.\n\n초안:" in run_bench.build_prompt(sc, "strict")


def test_benchmark_inputs_carry_the_marks_the_readme_describes():
    # README는 질문마다 em-dash와 가운뎃점을 하나씩 넣었고, 다듬기 초안에 세 표시가 모두 있다고 쓴다
    for sc in json.loads((bc.HERE / "reply_scenarios.json").read_text(encoding="utf-8")):
        assert (sc["prompt"].count("—"), sc["prompt"].count("·")) == (1, 1), sc["id"]
    drafts = [s for s in json.loads((bc.HERE / "scenarios.json").read_text(encoding="utf-8")) if s.get("draft")]
    assert [s["id"] for s in drafts] == ["polish"]
    assert all(report.marks(drafts[0]["draft"])[key] > 0 for key in report.MARKS)


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
        # 헤더와 목록 항목은 결함으로 세지 않는다. 기준선의 결함은 굵은 글씨 1개와 em-dash 1개다
        assert replies["baseline"]["visible"] == 2 and replies["plain"]["visible"] == 0
        assert report.judge_stats(root) == {"plain": 1, "tie": 0, "baseline": 0, "n": 1}
        headline = report.render_headline(replies, report.judge_stats(root))
        assert "100% 줄었습니다(2개에서 0개)" in headline and "1쌍 가운데 1쌍에서 이겼고" in headline
        docs = report.doc_stats(root, [{"id": "readme-intro", "type": "descriptive"}])
        assert docs["baseline"]["errors"] == 1 and docs["baseline"]["translationese"] == 1
        table = report.render_doc_table(docs)
        assert table.splitlines()[2].startswith("| 스킬 없음 | 1 |")
        dist = report.spelling_distribution(root)
        assert dict(dist["message"]["baseline"]) == {"메세지": 1}
        assert "| message | 메세지 1 | 메시지 1 | 메시지 1 |" in report.render_spelling_table(dist)


def test_polish_stats_count_marks_in_the_draft_and_the_polished_documents():
    with tempfile.TemporaryDirectory() as d:
        root = _fake_results(d)
        for cond, text in (("baseline", "**연결** — 방화벽·보안 그룹을 보세요."), ("plain", "방화벽과 보안 그룹을 확인하세요."),
                           ("strict", "방화벽을 확인해야 합니다.")):
            (root / "docs" / f"{cond}__polish__r1.json").write_text(
                json.dumps({"condition": cond, "scenario": "polish", "text": text}, ensure_ascii=False), encoding="utf-8")
        scenarios = [{"id": "readme-intro", "type": "descriptive"},
                     {"id": "polish", "type": "procedural", "draft": "**a** — b·c `d·e`"}]
        stats = report.polish_stats(root, scenarios)
        # 코드 안의 가운뎃점은 세지 않는다
        assert stats["draft"] == {"em_dash": 1, "bold_spans": 1, "middle_dot": 1}
        assert stats["baseline"] == {"n": 1, "em_dash": 1, "bold_spans": 1, "middle_dot": 1}
        assert stats["plain"] == {"n": 1, "em_dash": 0, "bold_spans": 0, "middle_dot": 0}
        intro, table = report.render_polish(stats, source="x/inputs/scenarios.json").split("\n\n")
        assert intro.startswith("문서 과제 가운데 하나는") and "em-dash 1개, 굵은 글씨 1개, 가운뎃점 1개" in intro
        assert "모두 남으면 em-dash 1개" in intro and "[`x/inputs/scenarios.json`](x/inputs/scenarios.json)" in intro
        assert table.splitlines()[2] == "| 스킬 없음 | 1 | 1 | 1 | 1 |"
        # 두 번 다듬었으면 표시가 모두 남았을 때의 합은 초안의 두 배다
        twice = {**stats, "baseline": {**stats["baseline"], "n": 2}}
        assert "모두 남으면 em-dash 2개, 굵은 글씨 2개, 가운뎃점 2개" in report.render_polish(twice)
        # 다듬기 과제가 없거나, 과제는 있어도 다듬은 문서가 없으면 문단과 표를 싣지 않는다
        assert report.render_polish(report.polish_stats(root, scenarios[:1])) == ""
        for path in (root / "docs").glob("*__polish__*.json"):
            path.unlink()
        assert report.render_polish(report.polish_stats(root, scenarios)) == ""


def test_marks_count_a_polished_document_wrapped_in_one_fence():
    assert report.marks("```markdown\n**a** — b·c\n```\n") == {"em_dash": 1, "bold_spans": 1, "middle_dot": 1}
    # 안에 코드 블록이 또 있으면 울타리를 벗기지 않는다
    nested = "```\n**a** — b\n```\n중간\n```\nc·d\n```"
    assert report.marks(nested) == report.marks(nested.replace("**a** — b", "").replace("c·d", ""))


def test_save_inputs_copies_once_and_refuses_other_inputs():
    with tempfile.TemporaryDirectory() as d:
        first = bc.save_inputs(d, "reply_scenarios.json")
        assert first == json.loads((bc.HERE / "reply_scenarios.json").read_text(encoding="utf-8"))
        assert bc.save_inputs(d, "reply_scenarios.json") == first
        Path(d, "inputs", "reply_scenarios.json").write_text("[]\n", encoding="utf-8")
        try:
            bc.save_inputs(d, "reply_scenarios.json")
        except SystemExit as err:
            assert "새 결과 디렉터리" in str(err)
        else:
            raise AssertionError("다른 입력이면 멈춰야 합니다")


def test_git_state_reports_commit_and_dirty_or_none():
    calls = []

    def fake(cmd, **kwargs):
        calls.append(cmd)
        return SimpleNamespace(stdout="abc123\n" if cmd[1] == "rev-parse" else " M README.md\n")
    assert bc.git_state(run=fake) == ("abc123", True)

    def broken(cmd, **kwargs):
        raise OSError("git 없음")
    assert bc.git_state(run=broken) == (None, None)


def test_benchmark_stats_use_the_inputs_saved_with_the_results():
    with tempfile.TemporaryDirectory(dir=str(report.ROOT / "evals")) as d:
        root = _fake_results(d)
        (root / "docs" / "baseline__polish__r1.json").write_text(
            json.dumps({"condition": "baseline", "scenario": "polish", "text": "**a** — b"}, ensure_ascii=False), encoding="utf-8")
        current = [{"id": "readme-intro", "type": "descriptive"}, {"id": "polish", "type": "procedural"}]
        old = report.benchmark_stats(root, current)
        # 입력을 복사해 두지 않은 옛 결과는 질문 문장을 원래대로 쓰고, 지금의 scenarios를 쓴다
        assert old["reply_marked"] is False and old["polish_source"] == "evals/scenarios.json"
        assert not report.polished(old["polish"])
        (root / "inputs").mkdir()
        saved = current[:1] + [{**current[1], "draft": "**a** — b·c"}]
        (root / "inputs" / "scenarios.json").write_text(json.dumps(saved, ensure_ascii=False), encoding="utf-8")
        (root / "inputs" / "reply_scenarios.json").write_text(
            json.dumps([{"id": "q", "prompt": "느립니다 — 목록·검색이요."}], ensure_ascii=False), encoding="utf-8")
        (root / "reply" / "baseline__q__r1.txt").write_text("**네** 그렇습니다.\n- 하나\n", encoding="utf-8")
        new = report.benchmark_stats(root, current)
        assert new["reply_marked"] is True and new["polish_source"].endswith("/inputs/scenarios.json")
        assert new["polish"]["draft"] == {"em_dash": 1, "bold_spans": 1, "middle_dot": 1}
        block = report.render_readme_block(new)
        assert "질문마다 em-dash와 가운뎃점(·)을 하나씩 넣었습니다." in block
        # 기준선 답변에 em-dash가 없으면 다듬기 과제를 보라고 적는다
        assert "em-dash를 지우는지는 아래 문서의 다듬기 과제로 봅니다." in block
        assert "질문마다" not in report.render_readme_block(old) and "다듬기 과제로 봅니다" not in report.render_readme_block(old)


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
