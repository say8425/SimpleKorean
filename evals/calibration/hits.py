#!/usr/bin/env python3
"""보정 도구. 기준선 출력에서 린터가 잡은 것을 모두 나열하고, 사람이 붙인 판정으로 정밀도를 센다.

    python3 evals/calibration/hits.py list evals/calibration/baseline > evals/calibration/hits.tsv
    python3 evals/calibration/hits.py record evals/calibration/baseline evals/calibration/hits.tsv \\
        > evals/calibration/RECORD.md

hits.tsv의 label 칸에는 맞는 일치면 TP, 거짓 일치면 FP를 적는다. FP 행의 note 칸에는 원인을 적는다.
record는 지금 린터로 다시 잡은 결과를 판정과 맞대어, 보정 뒤 남은 거짓 일치와 놓친 맞는 일치를 센다.
"""
import csv
import io
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import ko_lint  # noqa: E402
import ko_rules  # noqa: E402
import ko_text  # noqa: E402

COLUMNS = ("file", "line", "mode", "category", "severity", "match", "context", "label", "note")
COMPLIANT = HERE / "compliant-ko.md"
KIND_LABELS = {"procedural": "절차문", "descriptive": "설명문"}
LABELS = {**ko_lint.LABELS, "opener": "인사말", "closer": "맺음말"}


def _context(text, line):
    lines = ko_text.nfc(text).split("\n")
    s = lines[line - 1].strip() if 0 < line <= len(lines) else ""
    return s if len(s) <= 160 else s[:160] + "…"


def _row(file, line, mode, category, severity, match, context):
    return {"file": file, "line": str(line), "mode": mode, "category": category, "severity": severity,
            "match": match, "context": context, "label": "", "note": ""}


def doc_rows(results_dir):
    """문서 원본마다 기본 모드 위반과, 엄격 모드에서만 나오는 위반을 행으로 만든다."""
    rows = []
    for path in sorted(Path(results_dir, "docs").glob("*.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        text, kind, rel = record["text"], record["type"], f"docs/{path.name}"
        plain = ko_lint.lint_detail(text, kind, config={})
        seen = {(h["line"], h["category"], h["text"]) for h in plain}
        strict = [h for h in ko_lint.lint_detail(text, kind, strict=True, config={})
                  if (h["line"], h["category"], h["text"]) not in seen]
        for mode, hits in (("기본", plain), ("엄격", strict)):
            rows += [_row(rel, h["line"], mode, h["category"], h["severity"], h["text"], _context(text, h["line"]))
                     for h in hits]
    return rows


def reply_rows(results_dir):
    """답변 원본마다 답변 점검 훅이 세는 말(인사말, 맺음말, 슬롭 어휘)의 일치를 행으로 만든다."""
    rows = []
    for path in sorted(Path(results_dir, "reply").glob("*.txt")):
        text = ko_text.nfc(path.read_text(encoding="utf-8"))
        opener = ko_lint.OPENER.search(text)
        found = ([("opener", opener)] if opener else []) + [("closer", m) for m in ko_lint.CLOSER.finditer(text)]
        found += [("slop_word", m) for m in ko_rules.SLOP_RX.finditer(ko_text.mask(text))]
        for category, m in found:
            line = text.count("\n", 0, m.start()) + 1
            rows.append(_row(f"reply/{path.name}", line, "답변", category, "warning", m.group(0).strip(),
                             _context(text, line)))
    return rows


def to_tsv(rows):
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=COLUMNS, delimiter="\t", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue()


def read_tsv(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def key(row):
    return (row["file"], str(row["line"]), row["mode"], row["category"], row["match"])


def check_labels(labeled, current):
    """판정이 빠진 행과, 지금 린터가 잡지만 hits.tsv에 없는 행을 문장 목록으로 돌려준다."""
    problems = [f"판정이 없습니다: {r['file']}:{r['line']} {r['category']} {r['match']}"
                for r in labeled if r["label"] not in ("TP", "FP")]
    known = {key(r) for r in labeled}
    problems += [f"hits.tsv에 없는 일치입니다: {r['file']}:{r['line']} {r['category']} {r['match']}"
                 for r in current if key(r) not in known]
    return problems


def precision_table(labeled, current):
    """범주별 판정 수(hits, TP, FP)와 보정 뒤 남은 거짓 일치(fp_left), 놓친 맞는 일치(tp_lost)."""
    now = {key(r) for r in current}
    table = {}
    for r in labeled:
        t = table.setdefault(r["category"], Counter())
        t["hits"] += 1
        t[r["label"]] += 1
        t["fp_left"] += int(r["label"] == "FP" and key(r) in now)
        t["tp_lost"] += int(r["label"] == "TP" and key(r) not in now)
    return table


def length_stats(texts):
    """[(본문, 문서 유형)]에서 문장 유형별 문장 수, 가장 긴 문장, 상한을 넘은 문장 수를 센다."""
    stats = {kind: Counter() for kind in ko_rules.LIMITS}
    for text, doc_type in texts:
        for u in ko_text.units(ko_text.strip_frontmatter(ko_text.nfc(text))):
            kind = ko_text.sentence_kind(u.text) or doc_type
            n = ko_text.eojeol_count(u.text)
            stats[kind]["sentences"] += 1
            stats[kind]["max"] = max(stats[kind]["max"], n)
            stats[kind]["over"] += int(n > ko_rules.LIMITS[kind])
    return stats


def decide_limits(limits, compliant, baseline):
    """상한을 정한다. 규칙을 지킨 예문이 상한을 넘을 때만 그 길이로 올리고, 근거 없이 줄이지 않는다."""
    decided, reasons = {}, {}
    for kind, limit in limits.items():
        top, over = compliant[kind]["max"], baseline[kind]["over"]
        decided[kind] = max(limit, top)
        if top > limit:
            reasons[kind] = f"규칙을 지킨 예문의 가장 긴 문장이 {top}어절이라 {limit}어절에서 올렸습니다."
        elif over == 0:
            reasons[kind] = "기준선 문장 가운데 상한을 넘은 문장이 없습니다. 줄일 근거가 없어 그대로 둡니다."
        else:
            reasons[kind] = f"규칙을 지킨 예문은 모두 상한 안입니다(최대 {top}어절). 기준선 문장 {over}개가 상한을 넘었습니다."
    return decided, reasons


def _precision_section(table):
    lines = ["| 범주 | 판정한 일치 | 맞음 | 거짓 | 정밀도 | 보정 뒤 남은 거짓 | 보정 뒤 놓친 맞음 |",
             "|---|---:|---:|---:|---:|---:|---:|"]
    for cat in sorted(table, key=lambda c: (-table[c]["hits"], c)):
        t = table[cat]
        lines.append(f"| {LABELS.get(cat, cat)} | {t['hits']} | {t['TP']} | {t['FP']} | "
                     f"{t['TP'] / t['hits']:.2f} | {t['fp_left']} | {t['tp_lost']} |")
    return "\n".join(lines)


def _length_section(compliant, baseline, decided, reasons):
    lines = ["| 문장 유형 | 상한 | 규칙을 지킨 예문의 최댓값 | 기준선 문장 수 | 기준선 최댓값 | 상한을 넘은 기준선 문장 |",
             "|---|---:|---:|---:|---:|---:|"]
    for kind, limit in ko_rules.LIMITS.items():
        c, b = compliant[kind], baseline[kind]
        lines.append(f"| {KIND_LABELS[kind]} | {limit}어절 | {c['max']}어절 | {b['sentences']} | {b['max']}어절 | {b['over']} |")
    lines.append("")
    lines += [f"- {KIND_LABELS[k]}: {decided[k]}어절. {reasons[k]}" for k in ko_rules.LIMITS]
    return "\n".join(lines)


def _fp_section(labeled):
    fps = [r for r in labeled if r["label"] == "FP"]
    if not fps:
        return "거짓 일치가 없었습니다."
    rows = ["<!-- simple-korean: off -->", "| 파일 | 줄 | 범주 | 잡힌 말 | 원인 |", "|---|---:|---|---|---|"]
    rows += [f"| {r['file']} | {r['line']} | {LABELS.get(r['category'], r['category'])} | {r['match']} | {r['note']} |"
             for r in fps]
    return "\n".join(rows + ["<!-- simple-korean: on -->"])


def changelog_lines(table, labeled, decided, limits=None):
    """그 보정을 싣는 릴리스 항목의 보정 절에 그대로 옮길 줄."""
    limits = limits or ko_rules.LIMITS
    changed = [f"{KIND_LABELS[k]} {limits[k]}어절에서 {decided[k]}어절로" for k in limits if decided[k] != limits[k]]
    kept = ", ".join(f"{KIND_LABELS[k]} {limits[k]}어절" for k in limits)
    lines = [f"- 문장 길이 상한을 바꿨습니다: {', '.join(changed)}." if changed else
             f"- 문장 길이 상한은 {kept} 그대로입니다. 규칙을 지킨 예문은 모두 상한 안이었습니다."]
    for cat in sorted(table):
        t = table[cat]
        if t["FP"]:
            notes = ", ".join(sorted({r["note"] for r in labeled if r["category"] == cat and r["label"] == "FP"}))
            lines.append(f"- '{LABELS.get(cat, cat)}' 범주에서 판정한 {t['hits']}건 가운데 거짓 일치(린터가 잘못 잡은 곳) {t['FP']}건을 찾아 "
                         f"{t['FP'] - t['fp_left']}건을 고쳤습니다. 원인은 {notes}입니다.")
    if len(lines) == 1:
        lines.append("- 기준선 출력에서 거짓 일치를 찾지 못했습니다.")
    return lines


def record_md(results_dir, labeled):
    """RECORD.md 본문. 판정이 빠졌거나 hits.tsv에 없는 일치가 있으면 SystemExit로 멈춘다."""
    current = doc_rows(results_dir) + reply_rows(results_dir)
    problems = check_labels(labeled, current)
    if problems:
        raise SystemExit("\n".join(problems[:20] + [f"모두 {len(problems)}건입니다."]))
    docs = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(Path(results_dir, "docs").glob("*.json"))]
    n_replies = len(list(Path(results_dir, "reply").glob("*.txt")))
    meta = json.loads(Path(results_dir, "meta.json").read_text(encoding="utf-8"))
    table = precision_table(labeled, current)
    compliant = length_stats([(COMPLIANT.read_text(encoding="utf-8"), "procedural")])
    baseline = length_stats([(d["text"], d["type"]) for d in docs])
    decided, reasons = decide_limits(ko_rules.LIMITS, compliant, baseline)
    return "\n\n".join([
        f"# 보정 기록 ({meta['date']})",
        f"스킬 없이 기준선 문서 {len(docs)}개와 답변 {n_replies}개를 `{meta['model']}`(effort `{meta['effort']}`)로 만들었습니다. "
        "린터가 잡은 일치를 하나씩 맞음과 거짓으로 판정했습니다. 판정과 거짓 일치의 원인은 `hits.tsv`에 있습니다.",
        "## 범주별 정밀도", _precision_section(table),
        "## 문장 길이", _length_section(compliant, baseline, decided, reasons),
        "## 거짓 일치 목록", _fp_section(labeled),
        "## CHANGELOG에 옮길 줄", "\n".join(changelog_lines(table, labeled, decided)),
    ]) + "\n"


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if len(args) == 2 and args[0] == "list":
        sys.stdout.write(to_tsv(doc_rows(args[1]) + reply_rows(args[1])))
        return 0
    if len(args) == 3 and args[0] == "record":
        sys.stdout.write(record_md(args[1], read_tsv(args[2])))
        return 0
    raise SystemExit("사용법: hits.py list <보정 디렉터리> | hits.py record <보정 디렉터리> <hits.tsv>")


if __name__ == "__main__":
    sys.exit(main())
