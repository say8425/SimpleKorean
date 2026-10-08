#!/usr/bin/env python3
"""답변 벤치마크와 블라인드 판정.

기준선과 SimpleKorean(규칙 블록을 시스템 프롬프트에 붙임)으로 질문 8개에 답하게 하고, 판정 모델이
두 답변을 순서를 바꿔 두 번 비교한다. 이미 있는 파일은 건너뛴다.

    python3 evals/run_reply_bench.py --out evals/results/<날짜> [--runs 2] [--conditions baseline,plain]
    python3 evals/run_reply_bench.py --out evals/results/<날짜> [--runs 2] --judge
"""
import argparse
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bench_common as bc  # noqa: E402

CONDITIONS = ("baseline", "plain")
SYSTEM_PROMPT = bc.ROOT / "prompts" / "system-prompt.md"
JUDGE_PROMPT = (
    "아래는 같은 질문에 대한 두 답변 A와 B입니다. 이 분야를 모르는 독자가 한 번 읽고 정확히 이해할 수 있는 "
    "답변을 고르세요. 서식이 아니라 이해하기 쉬운지와 내용이 정확한지를 보세요. 다른 말 없이 JSON 한 줄로만 "
    '답하세요. {{"winner": "A"}}, {{"winner": "B"}}, {{"winner": "tie"}} 가운데 하나입니다.\n\n'
    "질문:\n{question}\n\n답변 A:\n{a}\n\n답변 B:\n{b}")


def generate(out, scenarios, runs, call=bc.call_claude, sleep=2.0, conditions=CONDITIONS):
    """조건 × 질문 × 회차의 답변을 out/reply/<조건>__<id>__r<회차>.txt로 쓴다."""
    system = bc.rule_block(SYSTEM_PROMPT.read_text(encoding="utf-8"))
    reply = Path(out) / "reply"
    reply.mkdir(parents=True, exist_ok=True)
    for run in range(1, runs + 1):
        for cond in conditions:
            for sc in scenarios:
                path = reply / f"{cond}__{sc['id']}__r{run}.txt"
                if path.exists() and path.read_text(encoding="utf-8").strip():
                    continue
                print(f"{cond} {sc['id']} r{run}", flush=True)
                try:
                    res = call(sc["prompt"], system=system if cond == "plain" else None)
                except Exception as err:  # noqa: BLE001
                    print(f"  실패: {err}", flush=True)
                    continue
                path.write_text(res["text"], encoding="utf-8")
                time.sleep(sleep)


def parse_winner(text):
    """판정 출력에서 A, B, tie 가운데 하나를 꺼낸다. 못 읽으면 None."""
    m = re.search(r'"winner"\s*:\s*"(A|B|tie)"', text or "")
    return m.group(1) if m else None


def combine(first, second):
    """두 순서의 판정을 합친다. 첫째는 A=기준선, 둘째는 A=SimpleKorean이다. 두 번 모두 같은 쪽이면 그쪽, 아니면 tie."""
    pick1 = {"A": "baseline", "B": "plain"}.get(first, "tie")
    pick2 = {"A": "plain", "B": "baseline"}.get(second, "tie")
    return pick1 if pick1 == pick2 else "tie"


def judge(out, scenarios, runs, call=bc.call_claude):
    """답변 쌍마다 판정을 out/judge/<id>__r<회차>.json으로 쓴다."""
    jdir, reply = Path(out) / "judge", Path(out) / "reply"
    jdir.mkdir(parents=True, exist_ok=True)
    for run in range(1, runs + 1):
        for sc in scenarios:
            path = jdir / f"{sc['id']}__r{run}.json"
            base_p, plain_p = reply / f"baseline__{sc['id']}__r{run}.txt", reply / f"plain__{sc['id']}__r{run}.txt"
            if path.exists() or not (base_p.exists() and plain_p.exists()):
                continue
            base, plain = base_p.read_text(encoding="utf-8"), plain_p.read_text(encoding="utf-8")
            ask = lambda a, b: parse_winner(call(JUDGE_PROMPT.format(question=sc["prompt"], a=a, b=b), model=bc.JUDGE_MODEL)["text"])  # noqa: E731
            first, second = ask(base, plain), ask(plain, base)
            record = {"scenario": sc["id"], "run": run, "judge_model": bc.JUDGE_MODEL,
                      "order1_baseline_first": first, "order2_plain_first": second, "winner": combine(first, second)}
            path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(f"판정 {sc['id']} r{run}: {record['winner']}", flush=True)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--runs", type=int, default=2)
    ap.add_argument("--conditions", default=",".join(CONDITIONS), help="쉼표로 나눈 조건 목록")
    ap.add_argument("--judge", action="store_true")
    a = ap.parse_args(argv)
    conditions = bc.parse_conditions(a.conditions, CONDITIONS)
    scenarios = json.loads((bc.HERE / "reply_scenarios.json").read_text(encoding="utf-8"))
    if a.judge:
        judge(a.out, scenarios, a.runs)
    else:
        generate(a.out, scenarios, a.runs, conditions=conditions)
    return 0


if __name__ == "__main__":
    sys.exit(main())
