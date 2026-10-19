#!/usr/bin/env python3
"""이 폴더의 원자료로 docs/research/reply-tables.md의 실험 수치를 다시 계산해 출력한다.

    python3 docs/research/data/reply-tables/analyze.py

답 모양, 표의 칸과 폭, 자료값이 남은 비율, 판정 수, criteria.md의 채택 조건을 센다. 레포지토리의
evals/ko_lint.py(reader_check)를 쓰고, 판정 모델은 다시 부르지 않는다.
"""
import json
import re
import statistics as st
import sys
import unicodedata
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[3] / "evals"))
import ko_lint  # noqa: E402

CONDS = ("baseline", "prohibit", "permit", "conditional")
TABLE_CONDS = ("permit", "conditional")
PAIRS = (("prohibit", "permit"), ("prohibit", "conditional"), ("permit", "conditional"))
SAME = ("prohibit@1", "prohibit@2")
KEYS = ("understand", "find", "overall")
LABEL = {"understand": "이해", "find": "찾기", "overall": "전체 선호"}
JUDGES = (("judge-opus.jsonl", "Opus"), ("judge-jev.jsonl", "Jev"))
FENCE = re.compile(r"```.*?```", re.S)
CODE = re.compile(r"`([^`\n]*)`")
SEP = re.compile(r"^\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?\s*$")
LINKS = re.compile(r"그러므로|때문|그래서|따라서|하지만|그러나|그러면|므로|반면|대신")


def load(name):
    path = HERE / name
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def width(text):
    """터미널 표시 폭. 동아시아 폭이 W나 F인 글자는 2칸, 결합 문자는 0칸이다."""
    return sum(0 if unicodedata.combining(ch) else 2 if unicodedata.east_asian_width(ch) in "WF" else 1
               for ch in text)


def cells(line):
    """표 행을 셀로 나눈다. 인라인 코드 안의 |는 나누지 않고, 렌더링되면 사라지는 백틱은 뺀다."""
    masked = CODE.sub(lambda m: m.group(1).replace("|", "\0"), line.strip())
    parts = re.split(r"(?<!\\)\|", masked.strip().strip("|"))
    return [p.replace("\0", "|").replace("\\|", "|").strip() for p in parts]


def tables(text):
    """코드 블록 밖의 마크다운 표 목록. 표마다 첫 줄 번호와 머리글 행을 포함한 셀 목록을 준다."""
    lines = FENCE.sub(lambda m: "\n" * m.group(0).count("\n"), text).split("\n")
    found, i = [], 1
    while i < len(lines):
        if SEP.match(lines[i]) and "|" in lines[i - 1]:
            rows = [cells(lines[i - 1])]
            j = i + 1
            while j < len(lines) and "|" in lines[j] and lines[j].strip():
                rows.append(cells(lines[j]))
                j += 1
            found.append({"line": i - 1, "rows": rows})
            i = j
        else:
            i += 1
    return found


def table_width(rows):
    """상자 테두리로 그릴 때의 폭: 열마다 가장 넓은 칸의 폭 합 + 열 수 x 3 + 1."""
    ncols = max(len(r) for r in rows)
    widest = [max(width(r[c]) if c < len(r) else 0 for r in rows) for c in range(ncols)]
    return sum(widest) + 3 * ncols + 1


def first_line_table(text):
    first = next((ln for ln in text.split("\n") if ln.strip()), "")
    return first.lstrip().startswith("|")


def coverage(text, targets):
    flat = text.replace(",", "")
    hit = 0
    for t in targets:
        pat = re.escape(t.replace(",", ""))
        if t.replace(",", "").isdigit():
            pat = rf"(?<![\d.]){pat}(?![\d])"
        hit += bool(re.search(pat, flat))
    return hit / len(targets)


def shape(text):
    counts = ko_lint.reader_check(text)["counts"]
    tbs = tables(text)
    body = [c for t in tbs for r in t["rows"][1:] for c in r]
    return {"chars": len(text), "sentences": counts["sentences"], "headers": counts["headers"],
            "tables": len(tbs), "widths": [table_width(t["rows"]) for t in tbs],
            "rows": [len(t["rows"]) - 1 for t in tbs], "cols": [max(len(r) for r in t["rows"]) for t in tbs],
            "cell_chars": [len(CODE.sub(r"\1", c)) for c in body],
            "lead_table": first_line_table(text), "links": len(LINKS.findall(FENCE.sub(" ", text))),
            "em_dash": counts["em_dash"], "bold": counts["bold_spans"]}


def tally(records, pair, ids, key, length_ok=None):
    c = Counter()
    for r in records:
        if tuple(r["pair"]) == pair and r["id"] in ids and (length_ok is None or length_ok(r)):
            c[r["winner"][key]] += 1
    return c


def fmt(c, pair):
    return f"{pair[0]} {c[pair[0]]}, {pair[1]} {c[pair[1]]}, 무승부 {c['tie']}"


def main():
    prompts = json.loads((HERE / "prompts.json").read_text(encoding="utf-8"))
    fit = {p["id"] for p in prompts if p["table_fit"]}
    unfit = {p["id"] for p in prompts} - fit
    targets = {p["id"]: p["targets"] for p in prompts if "targets" in p}
    answers = load("answers.jsonl")
    text = {(a["cond"], a["id"], a["run"]): a["text"] for a in answers}
    shapes = {k: shape(v) for k, v in text.items()}

    print("== 답 모양(Sonnet, 조건마다 답 40개)")
    for cond in CONDS:
        rows = [(k, s) for k, s in shapes.items() if k[0] == cond]
        if not rows:
            continue
        t_ans = [s for k, s in rows if k[1] in fit]
        n_ans = [s for k, s in rows if k[1] in unfit]
        ws = [w for _, s in rows for w in s["widths"]]
        cell = [c for _, s in rows for c in s["cell_chars"]]
        sent = sum(s["sentences"] for _, s in rows)
        print(f"{cond}: 표 있는 답 T {sum(1 for s in t_ans if s['tables'])}/{len(t_ans)}, "
              f"N {sum(1 for s in n_ans if s['tables'])}/{len(n_ans)}, 표 {len(ws)}개, "
              f"글자 수 중앙값 {st.median(s['chars'] for _, s in rows)}, 헤더 있는 답 {sum(1 for _, s in rows if s['headers'])}, "
              f"10문장당 연결어 {10 * sum(s['links'] for _, s in rows) / max(sent, 1):.2f}, "
              f"첫 줄 표 {sum(1 for _, s in rows if s['lead_table'])}, em-dash {sum(s['em_dash'] for _, s in rows)}, "
              f"굵은 글씨 {sum(s['bold'] for _, s in rows)}")
        if ws:
            print(f"  표 폭: 중앙값 {st.median(ws)}칸, 최댓값 {max(ws)}칸, 80칸 이하 {sum(w <= 80 for w in ws)}/{len(ws)}, "
                  f"100칸 이하 {sum(w <= 100 for w in ws)}/{len(ws)}, 120칸 이하 {sum(w <= 120 for w in ws)}/{len(ws)}")
            rws = [r for _, s in rows for r in s["rows"]]
            cls = [c for _, s in rows for c in s["cols"]]
            print(f"  행 수 중앙값 {st.median(rws)}, 열 수 중앙값 {st.median(cls)}, 셀 글자 수 중앙값 {st.median(cell)}, "
                  f"20자 넘는 셀 {sum(c > 20 for c in cell)}/{len(cell)}")
        cov = [coverage(text[k], targets[k[1]]) for k, _ in rows if k[1] in targets]
        if cov:
            print(f"  자료값이 남은 비율(질문 {len(targets)}개 x 2회): 평균 {st.mean(cov):.2f}")
    per_q = Counter((k[0], k[1]) for k, s in shapes.items() if s["tables"])
    print("== 질문별 표 있는 답 수(두 회차 합)")
    for p in prompts:
        print(f"{p['id']}({'T' if p['table_fit'] else 'N'}): " +
              ", ".join(f"{c} {per_q[(c, p['id'])]}" for c in CONDS))
    opus = load("answers-opus.jsonl")
    if opus:
        print(f"== claude-opus-5-5 답 모양(조건마다 질문 20개 x 1회, 판정하지 않음)")
        for cond in CONDS:
            rows = [shape(a["text"]) | {"id": a["id"]} for a in opus if a["cond"] == cond]
            if not rows:
                continue
            ws = [w for s in rows for w in s["widths"]]
            cell = [c for s in rows for c in s["cell_chars"]]
            line = (f"{cond}: 표 있는 답 T {sum(1 for s in rows if s['id'] in fit and s['tables'])}/10, "
                    f"N {sum(1 for s in rows if s['id'] in unfit and s['tables'])}/10, 표 {len(ws)}개, "
                    f"글자 수 중앙값 {st.median(s['chars'] for s in rows)}")
            if ws:
                line += (f", 표 폭 중앙값 {st.median(ws)}칸, 100칸 이하 {sum(w <= 100 for w in ws)}/{len(ws)}, "
                         f"셀 글자 수 중앙값 {st.median(cell)}")
            print(line)

    def diff_ok(r):
        a = text[(r["pair"][0], r["id"], r["run"])]
        b = text[(r["pair"][1], r["id"], r["run"])]
        return abs(len(a) - len(b)) < 0.2 * max(len(a), len(b))

    results = {}
    for name, judge in JUDGES:
        recs = load(name)
        if not recs:
            continue
        print(f"== {judge} 판정")
        for pair in PAIRS:
            for subset, ids in (("T", fit), ("N", unfit)):
                for key in KEYS:
                    c = tally(recs, pair, ids, key)
                    results[(judge, pair, subset, key)] = c
                    print(f"{'/'.join(pair)} {subset} {LABEL[key]}: {fmt(c, pair)}")
            for key in KEYS:
                c = tally(recs, pair, fit | unfit, key)
                results[(judge, pair, "all", key)] = c
            c = tally(recs, pair, fit, "overall", diff_ok)
            results[(judge, pair, "T-len", "overall")] = c
            print(f"{'/'.join(pair)} T 길이 차 20% 미만 {sum(c.values())}쌍의 전체 선호: {fmt(c, pair)}")
            c = tally(recs, pair, fit | unfit, "understand", diff_ok)
            print(f"{'/'.join(pair)} 전체 길이 차 20% 미만 {sum(c.values())}쌍의 이해: {fmt(c, pair)}")
        for key in KEYS:
            c = tally(recs, SAME, fit | unfit, key)
            print(f"같은 정책 두 답(prohibit 1회차/2회차) {LABEL[key]}: 1회차 {c[SAME[0]]}, 2회차 {c[SAME[1]]}, 무승부 {c['tie']}")
        for x in TABLE_CONDS:
            pair = ("prohibit", x)
            gain = {key: Counter() for key in ("find", "overall")}
            for r in recs:
                if tuple(r["pair"]) == pair and r["id"] in fit:
                    for key in gain:
                        gain[key][r["id"]] += {x: 1, "prohibit": -1}.get(r["winner"][key], 0)
            print(f"T 질문별 {x}의 앞섬(찾기/전체 선호, 두 회차 합): " +
                  ", ".join(f"{q} {gain['find'][q]:+d}/{gain['overall'][q]:+d}" for q in sorted(fit)))
        decided = [r for r in recs if tuple(r["pair"]) in PAIRS and r["winner"]["overall"] != "tie"]
        longer = sum(1 for r in decided
                     if len(text[(r["winner"]["overall"], r["id"], r["run"])]) >=
                     len(text[(r["pair"][1] if r["winner"]["overall"] == r["pair"][0] else r["pair"][0], r["id"], r["run"])]))
        print(f"전체 선호에서 승패가 난 {len(decided)}쌍 가운데 긴 답이 이긴 쌍 {longer}")
    if len(results) == 0:
        return
    both = [load(name) for name, _ in JUDGES]
    if all(both):
        key_of = {(tuple(r["pair"]), r["id"], r["run"]): r["winner"] for r in both[1]}
        common = [(r["winner"], key_of[(tuple(r["pair"]), r["id"], r["run"])]) for r in both[0]
                  if tuple(r["pair"]) in PAIRS and (tuple(r["pair"]), r["id"], r["run"]) in key_of]
        print("== 두 판정 모델의 일치(정책 쌍 120쌍): " +
              ", ".join(f"{LABEL[k]} {sum(1 for a, b in common if a[k] == b[k])}" for k in KEYS))

    print("== 채택 조건(criteria.md)")
    passed = {}
    for x in TABLE_CONDS:
        pair = ("prohibit", x)

        def lead(judge, subset, key):
            c = results[(judge, pair, subset, key)]
            return c[x] - c["prohibit"]

        js = [j for _, j in JUDGES if (j, pair, "T", "find") in results]
        n_tables = sum(1 for k, s in shapes.items() if k[0] == x and k[1] in unfit and s["tables"])
        ws = [w for k, s in shapes.items() if k[0] == x for w in s["widths"]]
        checks = [
            ("1 T 찾기 5쌍 이상", all(lead(j, "T", "find") >= 5 for j in js), [lead(j, "T", "find") for j in js]),
            ("2 T 전체 선호 3쌍 이상", all(lead(j, "T", "overall") >= 3 for j in js), [lead(j, "T", "overall") for j in js]),
            ("3 N 찾기와 전체 선호 -3 이상", all(lead(j, "N", k) >= -3 for j in js for k in ("find", "overall")),
             [lead(j, "N", k) for j in js for k in ("find", "overall")]),
            ("4 이해에서 두 모델 모두 -4 이하가 아님", not all(lead(j, "all", "understand") <= -4 for j in js),
             [lead(j, "all", "understand") for j in js]),
            ("5 T 길이 통제 전체 선호 0 이상", all(lead(j, "T-len", "overall") >= 0 for j in js),
             [lead(j, "T-len", "overall") for j in js]),
            ("6 N 표 있는 답 4개 이하", n_tables <= 4, [n_tables]),
            ("7 표의 75% 이상이 100칸 이하", bool(ws) and sum(w <= 100 for w in ws) / len(ws) >= 0.75,
             [f"{sum(w <= 100 for w in ws)}/{len(ws)}"]),
        ]
        passed[x] = all(ok for _, ok, _ in checks)
        print(f"{x} (판정 모델 순서 {', '.join(js)}):")
        for label, ok, vals in checks:
            print(f"  {'통과' if ok else '실패'} {label}: {vals}")
        print(f"  => {'채택 조건을 모두 만족' if passed[x] else '채택 조건 미달'}")
    if all(passed.values()):
        pair = ("permit", "conditional")
        leads = [results[(j, pair, "all", "overall")]["permit"] - results[(j, pair, "all", "overall")]["conditional"]
                 for _, j in JUDGES if (j, pair, "all", "overall") in results]
        print(f"두 정책 모두 통과. permit 대 conditional 전체 선호에서 permit이 앞선 쌍: {leads}")


if __name__ == "__main__":
    main()
