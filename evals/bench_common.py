#!/usr/bin/env python3
"""벤치마크 스크립트가 함께 쓰는 claude 호출 도구.

claude -p를 격리해서 부른다. 사용자·프로젝트 설정과 MCP 서버를 읽지 않고, 도구를 끄고, 빈 임시
디렉터리에서 돌린다. 내장 플러그인(*@builtin)은 끌 수 없지만 모든 조건에 똑같이 들어간다.

    python3 evals/bench_common.py --probe --out evals/results/<날짜>   # 격리를 확인하고 meta.json을 쓴다
"""
import argparse
import json
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
MODEL = "claude-sonnet-5-5"
JUDGE_MODEL = "claude-opus-5-5"
EFFORT = "low"
DISALLOWED = "Bash,Read,Write,Edit,Glob,Grep,WebFetch,WebSearch,NotebookEdit"
BUILTIN_SUFFIX = "@builtin"


def claude_cmd(prompt, model=MODEL, effort=EFFORT, system=None, output="json"):
    """격리된 claude -p 명령 목록."""
    cmd = ["claude", "-p", prompt, "--model", model, "--effort", effort,
           "--setting-sources", "", "--strict-mcp-config",
           "--disallowedTools", DISALLOWED, "--output-format", output]
    if output == "stream-json":
        cmd.append("--verbose")
    if system:
        cmd += ["--append-system-prompt", system]
    return cmd


def parse_result(stdout):
    """--output-format json 출력에서 result 이벤트를 꺼낸다. 객체 하나이거나 이벤트 목록이다."""
    data = json.loads(stdout)
    if isinstance(data, list):
        data = next(e for e in data if isinstance(e, dict) and e.get("type") == "result")
    return data


def call_claude(prompt, model=MODEL, effort=EFFORT, system=None, timeout=600, run=subprocess.run, cmd=None):
    """claude를 한 번 부르고 text, 사용량, 비용을 돌려준다. cmd를 주면 그 명령을 그대로 쓴다.

    실패하면 RuntimeError를 낸다.
    """
    started = time.time()
    with tempfile.TemporaryDirectory(prefix="simple-korean-bench-") as cwd:
        proc = run(cmd or claude_cmd(prompt, model, effort, system), capture_output=True, text=True,
                   timeout=timeout, cwd=cwd, stdin=subprocess.DEVNULL)
    if proc.returncode != 0:
        raise RuntimeError(f"{model}: {proc.stderr[:300]}")
    env = parse_result(proc.stdout)
    if env.get("is_error"):
        raise RuntimeError(f"{model}: {str(env.get('result'))[:300]}")
    usage = env.get("usage") or {}
    return {"text": env.get("result", ""), "model": model, "effort": effort,
            "input_tokens": usage.get("input_tokens"), "output_tokens": usage.get("output_tokens"),
            "cost_usd": env.get("total_cost_usd"),
            "duration_ms": env.get("duration_ms", int(1000 * (time.time() - started)))}


def init_summary(stream_stdout):
    """stream-json 출력의 init 이벤트를 요약한다."""
    init = {}
    for line in stream_stdout.splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if event.get("type") == "system" and event.get("subtype") == "init":
            init = event
    return {
        "found": bool(init),
        "claude_code_version": init.get("claude_code_version"),
        "model": init.get("model"),
        "mcp_servers": [m.get("name") for m in init.get("mcp_servers") or []],
        "plugins": [p.get("source", p.get("name", "")) for p in init.get("plugins") or []],
        "output_style": init.get("output_style"),
        "memory_paths": sorted((init.get("memory_paths") or {}).keys()),
    }


def isolation_problems(summary):
    """격리가 깨진 곳을 사람이 읽을 문장 목록으로 돌려준다. 비어 있으면 깨끗하다."""
    problems = []
    if not summary["found"]:
        problems.append("init 이벤트가 없습니다")
    if summary["mcp_servers"]:
        problems.append(f"MCP 서버가 섞였습니다: {summary['mcp_servers']}")
    outside = [p for p in summary["plugins"] if not p.endswith(BUILTIN_SUFFIX)]
    if outside:
        problems.append(f"내장이 아닌 플러그인이 섞였습니다: {outside}")
    if summary["output_style"] not in (None, "default"):
        problems.append(f"출력 스타일이 기본이 아닙니다: {summary['output_style']}")
    if set(summary["memory_paths"]) - {"auto"}:
        problems.append(f"메모리 파일이 섞였습니다: {summary['memory_paths']}")
    return problems


def probe(model=MODEL, run=subprocess.run):
    """격리 상태를 한 번 확인하고 (요약, 문제 목록)을 돌려준다."""
    with tempfile.TemporaryDirectory(prefix="simple-korean-probe-") as cwd:
        proc = run(claude_cmd("Reply with exactly: OK", model, EFFORT, output="stream-json"),
                   capture_output=True, text=True, timeout=300, cwd=cwd, stdin=subprocess.DEVNULL)
    summary = init_summary(proc.stdout)
    return summary, isolation_problems(summary)


def parse_conditions(value, allowed):
    """쉼표로 나눈 조건 목록을 검사해 튜플로 돌려준다. 모르는 조건이 있으면 멈춘다."""
    chosen = tuple(c.strip() for c in value.split(",") if c.strip())
    if not chosen or any(c not in allowed for c in chosen):
        raise SystemExit(f"조건은 {', '.join(allowed)} 가운데에서 고르세요: {value!r}")
    return chosen


def rule_block(text):
    """첫 번째와 두 번째 --- 줄 사이의 규칙 블록. 없으면 본문 전체."""
    parts = re.split(r"^---[ \t]*$", text, flags=re.M)
    return parts[1].strip() if len(parts) >= 3 else text.strip()


def skill_body(path):
    """마크다운 파일에서 frontmatter를 뗀 본문."""
    text = Path(path).read_text(encoding="utf-8")
    return re.sub(r"\A---\n.*?\n---\n", "", text, count=1, flags=re.S).strip()


def meta_date(out):
    """결과 디렉터리 이름이 날짜(YYYY-MM-DD)면 그 날짜, 아니면 오늘 날짜."""
    name = Path(out).name
    return name if re.fullmatch(r"\d{4}-\d{2}-\d{2}", name) else time.strftime("%Y-%m-%d")


def write_meta(out, summary, problems, date):
    meta = {"date": date, "model": MODEL, "judge_model": JUDGE_MODEL, "effort": EFFORT,
            "isolation": summary, "isolation_problems": problems}
    Path(out).mkdir(parents=True, exist_ok=True)
    Path(out, "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return meta


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    if not a.probe:
        ap.error("--probe만 지원합니다")
    summary, problems = probe()
    write_meta(a.out, summary, problems, meta_date(a.out))
    print(json.dumps({"isolation": summary, "problems": problems}, ensure_ascii=False, indent=2))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
