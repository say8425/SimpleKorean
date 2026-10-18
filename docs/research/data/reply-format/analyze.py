#!/usr/bin/env python3
"""이 폴더의 원자료로 docs/research/reply-formatting.md의 실험 수치를 다시 계산해 출력한다.

    python3 docs/research/data/reply-format/analyze.py

레포지토리의 evals/ko_lint.py(reader_check)를 쓴다. 판정 모델을 다시 부르지 않는다.
"""
import json
import re
import statistics as st
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[3] / "evals"))
import ko_lint  # noqa: E402

CONDS = ("baseline", "prohibit", "permit", "mandate", "permit_plus")
PAIRS = (("prohibit", "permit"), ("prohibit", "mandate"), ("permit", "mandate"), ("permit", "permit_plus"))
KEYS = ("understand", "find", "overall")
FENCE = re.compile(r"```.*?```", re.S)
ITEM = re.compile(r"^[^\S\n]*(?:[-*+]|\d+[.)])\s+(.*)$", re.M)
CODE = re.compile(r"`[^`\n]*`")
# 항목 끝의 "예:"나 쌍점은 뒤에 오던 코드의 머리말이므로 떼고 본다
LEAD_IN = re.compile(r"(?:\s*예)?\s*:\s*\.?\s*$")
TRAIL = re.compile(r"[\s.!?:;,)\]\"'”’…]+$")
# 문장 끝 뒤에 붙은 괄호 덧붙임("…확인하세요(예: X).")은 떼고 본다
PAREN = re.compile(r"\s*\([^()]*\)[\s.!?]*$")
NOUN_YO = ("필요", "개요", "주요", "중요", "요망", "수요")
NOUN_END = re.compile(r"(?:함|음|임|됨|필요|예정|가능|불가|완료|요망|바람|것)$")
# "그러므로"를 "므로"보다 먼저 두어 한 번만 센다
LINKS = re.compile(r"그러므로|때문|그래서|따라서|하지만|그러나|그러면|므로|반면|대신")


def load(name):
    return [json.loads(line) for line in (HERE / name).read_text(encoding="utf-8").splitlines() if line.strip()]


def is_sentence(text):
    """코드와 끝 부호를 뗀 항목이 문장 끝(다, 까, 죠, 요)으로 끝나면 참. 명사형 끝과 '필요' 같은 명사는 뺀다."""
    t = LEAD_IN.sub("", CODE.sub("", text))
    while PAREN.search(t):
        t = PAREN.sub("", t)
    t = TRAIL.sub("", t)
    if not t or NOUN_END.search(t) or t.endswith(NOUN_YO):
        return False
    return t.endswith(("다", "까", "죠", "요"))


def shape(text):
    counts = ko_lint.reader_check(text)["counts"]
    prose = FENCE.sub(" ", text)
    items = [m.group(1).strip() for m in ITEM.finditer(prose)]
    worded = [it for it in items if CODE.sub("", it).strip(" .:")]  # 코드만 있는 항목은 빼고 센다
    return {"chars": len(text), "sentences": counts["sentences"], "headers": counts["headers"],
            "items": len(items), "worded": len(worded), "fragments": sum(1 for it in worded if not is_sentence(it)),
            "links": len(LINKS.findall(prose)), "defects": ko_lint.reader_check(text)["visible_total"]}


def median(values):
    m = st.median(values)
    return f"{m:,.1f}" if m % 1 else f"{int(m):,}"


def main():
    answers = load("answers.jsonl")
    by = {(a["cond"], a["id"], a["run"]): a["text"] for a in answers}
    shapes = defaultdict(list)
    for a in answers:
        shapes[a["cond"]].append((a, shape(a["text"])))
    print("== 답 모양(조건마다 32개)")
    for c in CONDS:
        ss = [s for _, s in shapes[c]]
        sent = sum(s["sentences"] for s in ss)
        print(f"{c:12} 헤더 쓴 답 {sum(1 for s in ss if s['headers']):2}  목록 쓴 답 {sum(1 for s in ss if s['items']):2}  "
              f"글자 중앙값 {median([s['chars'] for s in ss]):>7}  조각 항목 {sum(s['fragments'] for s in ss)}/{sum(s['worded'] for s in ss)}  "
              f"연결어 10문장당 {10 * sum(s['links'] for s in ss) / sent:.2f}, 답당 {sum(s['links'] for s in ss) / len(ss):.2f}  "
              f"항목 답당 {sum(s['items'] for s in ss) / len(ss):.2f}  결함 {sum(s['defects'] for s in ss)}")
    short = [(a, s) for a, s in shapes["permit"] if s["chars"] < 700]
    print(f"허용의 700자 미만 답 {len(short)}개({min(s['chars'] for _, s in short)}~{max(s['chars'] for _, s in short)}자): "
          f"헤더 쓴 답 {sum(1 for _, s in short if s['headers'])}, 목록 쓴 답 {sum(1 for _, s in short if s['items'])}")
    types = {p["id"]: p["type"] for p in json.loads((HERE / "prompts.json").read_text(encoding="utf-8"))}
    bare = [(a, s) for a, s in shapes["mandate"] if not s["headers"] and types[a["id"]] in ("조언", "개념과 영향", "비교와 판단")]
    print(f"조건부 의무에서 조언, 개념과 영향, 비교와 판단 질문의 답 {len(bare)}개: 헤더 쓴 답 0, "
          f"{min(s['chars'] for _, s in bare)}~{max(s['chars'] for _, s in bare)}자")

    length = {k: len(v) for k, v in by.items()}
    for name in ("judge-opus.jsonl", "judge-jev.jsonl"):
        recs = load(name)
        print(f"\n== {name}: 쌍과 기준마다 앞 조건, 뒤 조건, 무승부")
        for x, y in PAIRS:
            rs = [r for r in recs if tuple(r["pair"]) == (x, y)]
            line = []
            for k in KEYS:
                c = Counter(r["winner"][k] for r in rs)
                line.append(f"{k} {c[x]}-{c[y]}-{c['tie']}")
            print(f"{x} 대 {y} (n={len(rs)}): " + ", ".join(line))
        main_recs = [r for r in recs if tuple(r["pair"]) in PAIRS[:3]]
        for x, y in PAIRS[:3]:
            c = Counter(r["winner"]["overall"] for r in main_recs if tuple(r["pair"]) == (x, y) and types[r["id"]] == "문제 해결")
            print(f"문제 해결 질문 8쌍의 overall, {x} 대 {y}: {c[x]}-{c[y]}-{c['tie']}")
        wins = [f"{r['pair'][1] if r['pair'][0] == 'prohibit' else r['pair'][0]} 상대 {r['id']} r{r['run']}" for r in main_recs
                if r["winner"]["overall"] == "prohibit"]
        print(f"금지가 overall에서 이긴 쌍 {len(wins)}개: " + ", ".join(wins))
        for k in KEYS:
            decided = [r for r in main_recs if r["winner"][k] != "tie"]
            longer = sum(1 for r in decided if r["winner"][k] == max(r["pair"], key=lambda c: length[(c, r["id"], r["run"])]))
            print(f"{k}: 승패가 난 {len(decided)}쌍 가운데 긴 답이 이긴 쌍 {longer}")
        print("길이 차가 긴 쪽의 20% 미만인 쌍:")
        for x, y in PAIRS[:3]:
            close = [r for r in main_recs if tuple(r["pair"]) == (x, y)
                     and abs(length[(x, r["id"], r["run"])] - length[(y, r["id"], r["run"])])
                     < 0.2 * max(length[(x, r["id"], r["run"])], length[(y, r["id"], r["run"])])]
            parts = []
            for k in ("overall", "understand"):
                c = Counter(r["winner"][k] for r in close)
                parts.append(f"{k} {c[x]}-{c[y]}-{c['tie']}")
            print(f"  {x} 대 {y} {len(close)}쌍: " + ", ".join(parts))
    opus = {(tuple(r["pair"]), r["id"], r["run"]): r for r in load("judge-opus.jsonl")}
    jev = {(tuple(r["pair"]), r["id"], r["run"]): r for r in load("judge-jev.jsonl")}
    keys = [k for k in opus if k[0] in PAIRS[:3]]
    print(f"\n전체 선호에서 두 판정 모델이 같은 쌍: {sum(1 for k in keys if opus[k]['winner']['overall'] == jev[k]['winner']['overall'])}/{len(keys)}")
    und = [opus[k] for k in keys if "prohibit" in k[0] and opus[k]["winner"]["understand"] == "prohibit"]
    print(f"Opus가 이해에서 금지를 고른 {len(und)}쌍 가운데 찾기는 상대가 이긴 쌍 "
          f"{sum(1 for r in und if r['winner']['find'] not in ('prohibit', 'tie'))}, 질문 {len({r['id'] for r in und})}개")


if __name__ == "__main__":
    main()
