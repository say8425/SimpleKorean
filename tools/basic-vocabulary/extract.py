#!/usr/bin/env python3
"""국립국어원 「국어 기초 어휘 선정 및 어휘 등급화 목록」(2023) xlsx에서 등급, 어휘, 품사, 어종만 뽑는다.

xlsx는 공공누리 제1유형이다(출처 표시). '의미' 열은 사전 뜻풀이라 싣지 않는다. 표준 라이브러리만 쓴다.

    python3 -I tools/basic-vocabulary/extract.py <xlsx 경로> data/basic-vocabulary/grades.tsv
"""
import csv
import re
import sys
import xml.etree.ElementTree as ET
import zipfile

SHEET = "전체(1~5등급), 40,000개"
M = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
KEEP = ("등급", "어휘", "품사", "어종")
EXPECTED = {"1등급": 5000, "2등급": 2500, "3등급": 5500, "4등급": 10000, "5등급": 17000}


def _shared_strings(z):
    if "xl/sharedStrings.xml" not in z.namelist():
        return []
    root = ET.fromstring(z.read("xl/sharedStrings.xml"))
    return ["".join(t.text or "" for t in si.iter(M + "t")) for si in root.iter(M + "si")]


def _sheet_path(z, name):
    workbook = ET.fromstring(z.read("xl/workbook.xml"))
    rels = {r.get("Id"): r.get("Target") for r in ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))}
    for sheet in workbook.iter(M + "sheet"):
        if sheet.get("name") == name:
            target = rels[sheet.get(R + "id")]
            return target.lstrip("/") if target.startswith("/") else "xl/" + target
    names = [s.get("name") for s in workbook.iter(M + "sheet")]
    raise SystemExit(f"시트 {name!r}가 없습니다. 있는 시트: {names}")


def _cell_value(cell, shared):
    v = cell.find(M + "v")
    if cell.get("t") == "s" and v is not None:
        return shared[int(v.text)]
    if cell.get("t") == "inlineStr":
        return "".join(t.text or "" for t in cell.iter(M + "t"))
    return v.text if v is not None and v.text else ""


def read_rows(xlsx, sheet=SHEET):
    """시트의 행을 {열 글자: 값} 목록으로 읽는다."""
    with zipfile.ZipFile(xlsx) as z:
        shared = _shared_strings(z)
        root = ET.fromstring(z.read(_sheet_path(z, sheet)))
    return [{re.match(r"[A-Z]+", c.get("r")).group(0): _cell_value(c, shared) for c in row.iter(M + "c")}
            for row in root.iter(M + "row")]


def extract(rows):
    """머리글 행으로 열을 찾아 (등급, 어휘, 품사, 어종) 행을 돌려준다. 머리글이 다르면 멈춘다."""
    header = rows[0]
    columns = {}
    for name in KEEP:
        found = [k for k, v in header.items() if v == name]
        if not found:
            raise SystemExit(f"머리글에 {name!r} 열이 없습니다: {header}")
        columns[name] = found[0]
    return [tuple(r.get(columns[n], "") for n in KEEP) for r in rows[1:] if r.get(columns["어휘"])]


def check_counts(records, expected=EXPECTED):
    """등급별 개수가 보고서의 값과 같은지 확인한다. 다르면 멈춘다."""
    counts = {}
    for grade, *_ in records:
        counts[grade] = counts.get(grade, 0) + 1
    if counts != expected:
        raise SystemExit(f"등급별 개수가 다릅니다: {counts} (기대값 {expected})")


def write_tsv(records, out):
    with open(out, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="\t", lineterminator="\n")
        writer.writerow(KEEP)
        writer.writerows(records)


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 2:
        raise SystemExit("사용법: extract.py <xlsx 경로> <출력 TSV 경로>")
    records = extract(read_rows(args[0]))
    check_counts(records)
    write_tsv(records, args[1])
    print(f"{len(records)} rows -> {args[1]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
