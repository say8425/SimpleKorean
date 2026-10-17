import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import run_pressure  # noqa: E402

SAMPLE = """# 압력 시험

## 시나리오 1: 첫째

> 한 줄 프롬프트입니다.

- [ ] 기준

## 시나리오 2: 둘째

<!-- simple-korean: off -->
> 첫 줄입니다.
>
> 둘째 문단입니다.
<!-- simple-korean: on -->

> 이 인용은 프롬프트가 아닙니다.
"""


def test_parse_scenarios_reads_first_quote_block():
    got = run_pressure.parse_scenarios(SAMPLE)
    assert [s["n"] for s in got] == [1, 2] and got[1]["title"] == "둘째"
    assert got[0]["prompt"] == "한 줄 프롬프트입니다."
    assert got[1]["prompt"] == "첫 줄입니다.\n\n둘째 문단입니다."


def test_parse_scenarios_rejects_missing_prompt():
    try:
        run_pressure.parse_scenarios("## 시나리오 3: 빈 시나리오\n\n- [ ] 기준\n")
    except SystemExit as err:
        assert "시나리오 3" in str(err)
    else:
        raise AssertionError("프롬프트 없는 시나리오를 받아들였습니다")


def test_real_file_has_ten_numbered_scenarios():
    got = run_pressure.parse_scenarios(run_pressure.TESTS_MD.read_text(encoding="utf-8"))
    assert [s["n"] for s in got] == list(range(1, 11))
    assert got[8]["prompt"].startswith("Write a git commit message")
    assert "디스크 사용량이 90%" in got[9]["prompt"]
    assert all(len(s["prompt"]) > 20 for s in got)
    assert "시도되어지며" in got[1]["prompt"] and "해요체로" in got[6]["prompt"]


def test_pressure_cmd_isolates_and_adds_plugin_only_when_asked():
    base = run_pressure.pressure_cmd("질문")
    assert base[:3] == ["claude", "-p", "질문"] and "--plugin-dir" not in base
    assert base[base.index("--setting-sources") + 1] == "" and "--strict-mcp-config" in base
    plugin = run_pressure.pressure_cmd("질문", "/repo")
    assert plugin[-2:] == ["--plugin-dir", "/repo"]
    assert plugin[plugin.index("--allowedTools") + 1] == "Read,Skill"


def test_baseline_cannot_read_files_and_plugin_cannot_search():
    # 2026-10-08: 파일 도구를 연 기준선이 디스크에서 이 레포지토리의 규칙 목록을 찾아 K 번호를 인용했다
    base = run_pressure.pressure_cmd("질문")
    assert "--allowedTools" not in base
    assert {"Read", "Glob", "Grep", "Skill", "Bash"} <= set(base[base.index("--disallowedTools") + 1].split(","))
    plugin = run_pressure.pressure_cmd("질문", "/repo")
    assert {"Glob", "Grep", "Bash"} <= set(plugin[plugin.index("--disallowedTools") + 1].split(","))


def test_machine_report_counts_lint_and_style_criteria():
    r1 = run_pressure.machine_report(1, "연결이 끊기면 설정을 확인하는 것이 좋습니다.\n")
    assert r1["hedge"] == 1 and r1["sentence_over_limit"] == 0
    r6 = run_pressure.machine_report(6, "sqlpipe는 테이블을 복사한다. 설정은 YAML 파일 하나입니다.\n")
    assert r6 == {"요청한 문체 문장": 1, "다른 문체 문장": 1}
    r7 = run_pressure.machine_report(7, "**메모리**가 모자라서 파드가 죽었어요.\n- 한도를 늘리세요\n")
    assert r7 == {"요청한 문체 문장": 2, "다른 문체 문장": 0, "visible_total": 1}
    mixed = run_pressure.machine_report(7, "메모리가 모자라서 파드가 죽었습니다. 한도를 늘리세요.\n")
    assert mixed["다른 문체 문장"] == 1
    r8 = run_pressure.machine_report(8, "백업은 반드시 하루에 한 번 실행해야 합니다.\n")
    assert r8["strict_ending"] == 1
    r10 = run_pressure.machine_report(10, "## 원인\n\n**로그**가 쌓였습니다.\n")
    assert r10 == {"visible_total": 2, "lead_structure": 1}, r10
    assert run_pressure.machine_report(4, "아무 글입니다.") == {}
    assert run_pressure.machine_report(9, "fix: handle an empty CSV header row") == {"한글 비율": 0.0}


def test_check_lines_reads_saved_outputs():
    with tempfile.TemporaryDirectory() as d:
        Path(d, "plugin__p3__r1.txt").write_text("백업이 있는지 확인하세요.\n", encoding="utf-8")
        Path(d, "baseline__p4__r1.txt").write_text("히어로 문구입니다.\n", encoding="utf-8")
        lines = run_pressure.check_lines(d)
    assert lines == ["baseline__p4__r1.txt: 읽고 판정", "plugin__p3__r1.txt: noun_ending=0"]


def test_generate_writes_round_files_and_skips_existing():
    seen = []

    def fake(prompt, cmd=None, **kwargs):
        seen.append(cmd)
        return {"text": "출력입니다."}

    scenarios = [{"n": 4, "title": "t", "prompt": "p"}]
    with tempfile.TemporaryDirectory() as d:
        run_pressure.generate(d, scenarios, 2, call=fake, sleep=0, plugin_dir="/repo")
        assert sorted(p.name for p in Path(d).iterdir()) == ["baseline__p4__r2.txt", "plugin__p4__r2.txt"]
        assert "--plugin-dir" not in seen[0] and seen[1][-2:] == ["--plugin-dir", "/repo"]
        run_pressure.generate(d, scenarios, 2, call=fake, sleep=0, plugin_dir="/repo")
        assert len(seen) == 2
