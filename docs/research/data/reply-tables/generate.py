#!/usr/bin/env python3
"""reply-tables 실험의 답을 만든다. 조건마다 규칙 블록의 답변 문단 두 개만 policies.json의 문장으로 바꾼다.

    python3 docs/research/data/reply-tables/generate.py --out answers.jsonl --runs 2
    python3 docs/research/data/reply-tables/generate.py --model claude-opus-5-5 --runs 1 --out answers-opus.jsonl

evals/bench_common.py의 격리된 claude -p를 쓴다. 이미 있는 (조건, 질문, 회차)는 건너뛰므로 멈춘 뒤 다시
실행하면 남은 답만 만든다.
"""
import argparse
import json
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[3] / "evals"))
import bench_common as bc  # noqa: E402

CONDS = ("baseline", "prohibit", "permit", "conditional")


def rule_blocks():
    """조건마다 시스템 프롬프트에 붙일 규칙 블록. baseline은 None이다."""
    base = (HERE / "base-rule-block.md").read_text(encoding="utf-8").strip()
    policies = json.loads((HERE / "policies.json").read_text(encoding="utf-8"))
    blocks = {"baseline": None}
    for cond, texts in policies.items():
        block = base
        for key in ("format", "lead"):
            old = policies["prohibit"][key]
            if base.count(old) != 1:
                raise SystemExit(f"base-rule-block.md에서 prohibit의 {key} 문단을 한 번 찾지 못했습니다")
            block = block.replace(old, texts[key])
        blocks[cond] = block
    return blocks


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="answers.jsonl", help="이 폴더 안의 출력 파일 이름")
    ap.add_argument("--model", default=bc.MODEL)
    ap.add_argument("--effort", default=bc.EFFORT)
    ap.add_argument("--runs", type=int, default=2)
    ap.add_argument("--conds", default=",".join(CONDS))
    ap.add_argument("--workers", type=int, default=6)
    a = ap.parse_args(argv)
    conds = bc.parse_conditions(a.conds, CONDS)
    prompts = json.loads((HERE / "prompts.json").read_text(encoding="utf-8"))
    blocks = rule_blocks()
    out = HERE / a.out
    done = set()
    if out.exists():
        for line in out.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                done.add((r["cond"], r["id"], r["run"]))
    jobs = [(c, p, r) for r in range(1, a.runs + 1) for p in prompts for c in conds if (c, p["id"], r) not in done]
    print(f"남은 답 {len(jobs)}개 (이미 {len(done)}개)", flush=True)
    lock = threading.Lock()

    def one(cond, p, run):
        res = bc.call_claude(p["prompt"], model=a.model, effort=a.effort, system=blocks[cond])
        rec = {"cond": cond, "id": p["id"], "run": run, "model": a.model, "effort": a.effort, "text": res["text"],
               "cost_usd": res.get("cost_usd"), "duration_ms": res.get("duration_ms")}
        with lock, out.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        return cond, p["id"], run

    failed = 0
    with ThreadPoolExecutor(max_workers=a.workers) as pool:
        futures = [pool.submit(one, *job) for job in jobs]
        for i, fut in enumerate(as_completed(futures), 1):
            try:
                cond, pid, run = fut.result()
                print(f"[{i}/{len(jobs)}] {cond} {pid} {run}", flush=True)
            except Exception as err:  # noqa: BLE001  실패한 답은 다시 실행하면 채운다
                failed += 1
                print(f"[{i}/{len(jobs)}] 실패: {err}", flush=True)
    print(f"끝: 실패 {failed}개", flush=True)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
