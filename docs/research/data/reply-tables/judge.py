#!/usr/bin/env python3
"""reply-tables 실험의 쌍 판정. 같은 질문, 같은 회차의 두 답을 순서를 바꿔 두 번 비교한다.

    python3 docs/research/data/reply-tables/judge.py --judge opus --out judge-opus.jsonl
    python3 docs/research/data/reply-tables/judge.py --judge jev --out judge-jev.jsonl

Opus는 evals/bench_common.py의 격리된 claude -p로 부른다. Jev는 TypeSafe API로 부르고, 환경 변수
TYPESAFE_API_KEY를 쓴다. 정책 쌍 세 개와 함께 prohibit의 1회차 대 2회차(같은 정책 두 답)도 판정한다.
이미 있는 판정은 건너뛴다.
"""
import argparse
import hashlib
import json
import os
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[3] / "evals"))
import bench_common as bc  # noqa: E402

PAIRS = (("prohibit", "permit"), ("prohibit", "conditional"), ("permit", "conditional"))
SAME = ("prohibit@1", "prohibit@2")
KEYS = ("understand", "find", "overall")
API = "https://api.typesafe.ai/v1/systemone"
SPEC = json.loads((HERE / "judge-prompts.json").read_text(encoding="utf-8"))


def load_answers(name):
    rows = [json.loads(line) for line in (HERE / name).read_text(encoding="utf-8").splitlines() if line.strip()]
    return {(r["cond"], r["id"], r["run"]): r["text"] for r in rows}


def tasks(answers, prompts):
    """(쌍, 질문, 회차, 앞 답, 뒤 답) 목록. 같은 정책 두 답은 회차를 0으로 적는다."""
    out = []
    for pair in PAIRS:
        for p in prompts:
            for run in (1, 2):
                out.append((pair, p, run, answers[(pair[0], p["id"], run)], answers[(pair[1], p["id"], run)]))
    for p in prompts:
        out.append((SAME, p, 0, answers[("prohibit", p["id"], 1)], answers[("prohibit", p["id"], 2)]))
    return out


def winner(pair, first, second):
    """첫 순서는 앞 조건이 A, 둘째 순서는 뒤 조건이 A다. 두 순서가 같은 조건을 고를 때만 승이다."""
    w1 = {"A": pair[0], "B": pair[1]}.get(first)
    w2 = {"A": pair[1], "B": pair[0]}.get(second)
    return w1 if w1 is not None and w1 == w2 else "tie"


def opus_once(question, a, b):
    prompt = SPEC["opus_prompt_template"].format(question=question, a=a, b=b)
    for _ in range(3):
        text = bc.call_claude(prompt, model=SPEC["opus_model"], effort=SPEC["opus_effort"])["text"]
        try:
            data = json.loads(text[text.index("{"):text.rindex("}") + 1])
        except ValueError:
            continue
        if all(data.get(k) in ("A", "B", "tie") for k in KEYS):
            return {k: data[k] for k in (*KEYS, "reason")}
    raise RuntimeError("Opus가 세 번 모두 형식에 맞는 JSON을 내지 않았습니다")


def jev_once(question, a, b, cache):
    body = json.dumps({"state": {"question": question, "answer_A": a, "answer_B": b},
                       "model": SPEC["jev_model"], "questions": SPEC["jev_questions"]},
                      ensure_ascii=False, sort_keys=True).encode()
    path = cache / (hashlib.sha256(body).hexdigest() + ".json")
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    req = urllib.request.Request(API, data=body, method="POST", headers={
        "Authorization": f"Bearer {os.environ['TYPESAFE_API_KEY']}", "Content-Type": "application/json"})
    for attempt in range(8):
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = json.loads(resp.read())
            path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            return data
        except urllib.error.HTTPError as err:
            if err.code != 429 and err.code < 500:
                raise RuntimeError(f"Jev {err.code}: {err.read()[:300]!r}") from err
            time.sleep(retry_delay(err.headers.get("retry-after"), attempt))
        except OSError:  # URLError, 연결 끊김, 읽기 시간 초과(3.9의 socket.timeout 포함)
            time.sleep(2 ** attempt)
    raise RuntimeError("Jev가 여덟 번 모두 응답하지 않았습니다")


def retry_delay(header, attempt):
    """retry-after가 초 단위 숫자면 그 값을, 날짜이거나 없으면 2의 거듭제곱 초를 쓴다."""
    try:
        return float(header)
    except (TypeError, ValueError):
        return 2 ** attempt


def judge_opus(pair, p, run, a, b, _cache):
    o1, o2 = opus_once(p["prompt"], a, b), opus_once(p["prompt"], b, a)
    return {"pair": list(pair), "id": p["id"], "run": run, "judge_model": SPEC["opus_model"],
            "order1": o1, "order2": o2, "winner": {k: winner(pair, o1[k], o2[k]) for k in KEYS}}


def judge_jev(pair, p, run, a, b, cache):
    r1, r2 = jev_once(p["prompt"], a, b, cache), jev_once(p["prompt"], b, a, cache)
    o1 = {k: {"choice": r1["answers"][k]["choice"], "probabilities": r1["answers"][k]["probabilities"]} for k in KEYS}
    o2 = {k: {"choice": r2["answers"][k]["choice"], "probabilities": r2["answers"][k]["probabilities"]} for k in KEYS}
    p_x = {k: round((o1[k]["probabilities"]["A"] + o2[k]["probabilities"]["B"]) / 2, 4) for k in KEYS}
    return {"pair": list(pair), "id": p["id"], "run": run, "model": r1["model"], "order1": o1, "order2": o2,
            "p_x": p_x, "winner": {k: winner(pair, o1[k]["choice"], o2[k]["choice"]) for k in KEYS}}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--judge", choices=("opus", "jev"), required=True)
    ap.add_argument("--answers", default="answers.jsonl")
    ap.add_argument("--out", required=True, help="이 폴더 안의 출력 파일 이름")
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--cache", default=str(Path(tempfile.gettempdir()) / "simple-korean-jev-cache"))
    a = ap.parse_args(argv)
    if a.judge == "jev" and not os.environ.get("TYPESAFE_API_KEY"):
        raise SystemExit("Jev로 판정하려면 환경 변수 TYPESAFE_API_KEY가 있어야 합니다")
    prompts = json.loads((HERE / "prompts.json").read_text(encoding="utf-8"))
    out = HERE / a.out
    done = set()
    if out.exists():
        for line in out.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                done.add((tuple(r["pair"]), r["id"], r["run"]))
    todo = [t for t in tasks(load_answers(a.answers), prompts) if (t[0], t[1]["id"], t[2]) not in done]
    print(f"남은 판정 {len(todo)}개 (이미 {len(done)}개)", flush=True)
    cache = Path(a.cache)
    cache.mkdir(parents=True, exist_ok=True)
    fn = judge_opus if a.judge == "opus" else judge_jev
    lock = threading.Lock()

    def one(t):
        rec = fn(*t, cache)
        with lock, out.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        return rec

    failed = 0
    with ThreadPoolExecutor(max_workers=a.workers) as pool:
        futures = [pool.submit(one, t) for t in todo]
        for i, fut in enumerate(as_completed(futures), 1):
            try:
                rec = fut.result()
                print(f"[{i}/{len(todo)}] {'/'.join(rec['pair'])} {rec['id']} {rec['run']} {rec['winner']}", flush=True)
            except Exception as err:  # noqa: BLE001  실패한 판정은 다시 실행하면 채운다
                failed += 1
                print(f"[{i}/{len(todo)}] 실패: {err}", flush=True)
    print(f"끝: 실패 {failed}개", flush=True)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
