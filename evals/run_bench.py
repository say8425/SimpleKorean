#!/usr/bin/env python3
"""문서 벤치마크. 과제 9개를 기준선, 기본 모드, 엄격 모드로 쓰게 하고 원본 출력을 저장한다.

이미 있는 원본 파일은 건너뛰므로 중간에 멈춰도 다시 이어서 돌릴 수 있다.

    python3 evals/run_bench.py --out evals/results/<날짜> [--runs 2] [--conditions baseline,plain,strict] [--smoke]
"""
import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bench_common as bc  # noqa: E402

CONDITIONS = ("baseline", "plain", "strict")
SKILL = bc.ROOT / "skills" / "simple-korean" / "SKILL.md"
STRICT = bc.ROOT / "skills" / "simple-korean" / "references" / "strict-mode.md"
LEAD = "다음 글쓰기 지침을 자가 점검 단계까지 정확히 따르세요.\n\n"
TAIL = "\n\n규칙 설명 없이 최종 글만 쓰세요."


def task_text(scenario):
    """과제 글. 다듬기 과제는 지시 뒤에 초안(draft)을 붙인다."""
    draft = scenario.get("draft")
    return scenario["prompt"] + (f"\n\n초안:\n\n{draft}" if draft else "")


def build_prompt(scenario, condition):
    """조건에 맞는 프롬프트. 기준선은 과제만, 기본 모드는 SKILL.md 본문을, 엄격 모드는 strict-mode.md까지 붙인다."""
    if condition == "baseline":
        return task_text(scenario)
    rules = bc.skill_body(SKILL)
    task = task_text(scenario)
    if condition == "strict":
        rules = rules + "\n\n" + bc.skill_body(STRICT)
        task = "엄격 모드로 쓰세요. " + task
    return LEAD + rules + "\n\n---\n\n과제: " + task + TAIL


def generate(out, scenarios, runs, call=bc.call_claude, sleep=2.0, conditions=CONDITIONS):
    """조건 × 과제 × 회차의 원본 출력을 out/docs/에 JSON으로 쓴다. 있는 파일은 건너뛴다."""
    docs = Path(out) / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    todo = [(c, s, r) for r in range(1, runs + 1) for c in conditions for s in scenarios]
    for i, (cond, sc, run) in enumerate(todo, 1):
        path = docs / f"{cond}__{sc['id']}__r{run}.json"
        if path.exists():
            continue
        print(f"[{i}/{len(todo)}] {cond} {sc['id']} r{run}", flush=True)
        try:
            res = call(build_prompt(sc, cond))
        except Exception as err:  # noqa: BLE001  하나가 실패해도 나머지는 돈다
            print(f"  실패: {err}", flush=True)
            continue
        record = {**res, "condition": cond, "scenario": sc["id"], "type": sc["type"], "run": run}
        path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        time.sleep(sleep)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--runs", type=int, default=2)
    ap.add_argument("--conditions", default=",".join(CONDITIONS), help="쉼표로 나눈 조건 목록")
    ap.add_argument("--smoke", action="store_true", help="과제 2개를 1회만 돈다")
    a = ap.parse_args(argv)
    conditions = bc.parse_conditions(a.conditions, CONDITIONS)
    scenarios = json.loads((bc.HERE / "scenarios.json").read_text(encoding="utf-8"))
    runs = 1 if a.smoke else a.runs
    generate(a.out, scenarios[:2] if a.smoke else scenarios, runs, conditions=conditions)
    return 0


if __name__ == "__main__":
    sys.exit(main())
