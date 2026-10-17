#!/usr/bin/env python3
"""전후 예시를 원본 출력에서 만든다. 고를 과제와 질문은 측정 전에 정했다(PICKS). 글은 고치지 않는다.

    python3 evals/make_examples.py evals/results/<날짜>            # examples/before-after.md를 쓴다
    python3 evals/make_examples.py evals/results/<날짜> --readme   # README 다섯 개의 보기 블록도 바꾼다
"""
import json
import re
import unicodedata
import sys
from pathlib import Path

import readme_i18n as i18n

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
EXAMPLES = ROOT / "examples" / "before-after.md"
RUN = 1
DOC_PICKS = (
    ("readme-intro", "plain", "README 소개(설명문)"),
    ("troubleshooting", "plain", "문제 해결(절차문)"),
    ("error-message", "plain", "오류 메시지"),
    ("release-notes", "strict", "릴리스 노트(엄격 모드)"),
)
REPLY_PICKS = (("oom", "OOMKilled 질문"), ("cache", "캐시 무효화 질문"))
# README 보기 블록은 문서 예시 하나를 좌우 표로 보인다. 답변 예시는 코드 블록이 표 칸보다 넓어서
# 오른쪽 칸을 밀어내므로 examples/before-after.md에만 둔다.
README_PICK = ("troubleshooting", "plain")
# 표 칸 하나에 들어가는 코드 줄의 너비다. 고정폭 글꼴의 칸으로 세고, 넓은 글자(한글 등)는 두 칸이다.
# 이보다 넓은 코드 줄이 있으면 칸이 넓어져 옆 칸을 밀어낸다.
CELL_CODE_COLUMNS = 50
COND_LABELS = {"plain": "기본 모드", "strict": "엄격 모드"}
EXAMPLE_BLOCK = re.compile(r"<!-- example:start -->\n(.*?)\n<!-- example:end -->", re.S)
SOURCE_BLOCK = re.compile(
    r"<!-- source: (\S+) -->\n<!-- simple-korean: off -->\n(.*?)\n<!-- simple-korean: on -->", re.S)


def quote(text):
    """원문을 인용 블록으로 바꾼다. 빈 줄에는 '>'만 남긴다."""
    return "\n".join(f"> {line}" if line else ">" for line in text.rstrip("\n").split("\n"))


def unquote(block):
    return "\n".join(re.sub(r"^> ?", "", line) for line in block.split("\n"))


def raw_text(rel):
    """레포지토리 기준 경로의 원본 출력. 문서는 JSON의 text, 답변은 파일 내용이다."""
    path = ROOT / rel
    data = path.read_text(encoding="utf-8")
    return json.loads(data)["text"] if path.suffix == ".json" else data


def source_block(rel):
    return f"<!-- source: {rel} -->\n<!-- simple-korean: off -->\n{quote(raw_text(rel))}\n<!-- simple-korean: on -->"


def _pair(results_dir, sub, item, cond, ext):
    base = Path(results_dir, sub).resolve().relative_to(ROOT).as_posix()
    return f"{base}/baseline__{item}__r{RUN}.{ext}", f"{base}/{cond}__{item}__r{RUN}.{ext}"


def _section(title, before, after, after_label):
    return "\n\n".join([f"## {title}", f"전: 스킬 없음, `{before}`", source_block(before),
                        f"후: {after_label}, `{after}`", source_block(after)])


def examples_md(results_dir):
    """examples/before-after.md 전체."""
    parts = ["# 전후 예시",
             "'전'은 스킬 없이 만든 원본 출력입니다. '후'는 같은 과제를 스킬을 켜고 만든 원본 출력입니다. "
             "두 글 모두 고치지 않고 옮겼습니다. 과제와 질문은 측정 전에 정했습니다(`evals/make_examples.py`의 PICKS). "
             "`python3 evals/check_numbers.py`가 이 파일의 글을 원본 파일과 글자 하나까지 대조합니다."]
    for scenario, cond, title in DOC_PICKS:
        before, after = _pair(results_dir, "docs", scenario, cond, "json")
        parts.append(_section(title, before, after, COND_LABELS[cond]))
    for question, title in REPLY_PICKS:
        before, after = _pair(results_dir, "reply", question, "plain", "txt")
        parts.append(_section(f"답변: {title}", before, after, "SimpleKorean"))
    return "\n\n".join(parts) + "\n"


def _cell(rel):
    """표 칸 하나. GitHub는 HTML 칸 안의 마크다운을 앞뒤 빈 줄이 있어야 그린다."""
    return f'<td valign="top">\n\n{source_block(rel)}\n\n</td>'


def readme_example(results_dir, lang="ko"):
    """README 보기 블록의 본문. 왼쪽 칸은 스킬 없이, 오른쪽 칸은 SimpleKorean을 켜고 쓴 문서다.

    인용한 출력은 어느 언어에서나 한국어 원문이다.
    """
    scenario, cond = README_PICK
    before, after = _pair(results_dir, "docs", scenario, cond, "json")
    text = i18n.TEXT[lang]
    table = "\n".join([
        "<table>", "<tr>",
        f'<th width="50%">{text["example_before"]}</th>',
        f'<th width="50%">{text["example_after"]}</th>',
        "</tr>", "<tr>", _cell(before), _cell(after), "</tr>", "</table>",
    ])
    return "\n\n".join([table, text["example_files"].format(before=before, after=after),
                        text["example_docs"].format(href=i18n.link(lang, "examples/before-after.md"))])


def wide_code_lines(text):
    """코드 블록 안에서 CELL_CODE_COLUMNS칸보다 넓은 줄의 목록."""
    wide, fence = [], None
    for line in text.splitlines():
        mark = line.lstrip()[:3]
        if mark in ("```", "~~~") and fence in (None, mark):
            fence = None if fence else mark
            continue
        if fence and sum(2 if unicodedata.east_asian_width(c) in ("W", "F") else 1 for c in line) > CELL_CODE_COLUMNS:
            wide.append(line)
    return wide


def pick_problems(results_dir):
    """README 보기 예시가 측정 전에 정한 문서 예시인지, 표 칸을 넘칠 만큼 넓은 코드 줄이 없는지 본다."""
    if README_PICK not in {pick[:2] for pick in DOC_PICKS}:
        return [f"README_PICK {README_PICK}가 DOC_PICKS에 없습니다"]
    scenario, cond = README_PICK
    problems = []
    for rel in _pair(results_dir, "docs", scenario, cond, "json"):
        try:
            if wide_code_lines(raw_text(rel)):
                problems.append(f"{rel}: 코드 블록에 {CELL_CODE_COLUMNS}칸보다 넓은 줄이 있어 README 보기 표의 칸을 넘칩니다")
        except (OSError, ValueError, KeyError) as err:
            problems.append(f"{rel}: 원본을 읽지 못했습니다({err})")
    return problems


def replace_example_block(readme_text, body, name="README.md"):
    """README의 보기 블록을 새 본문으로 바꾼 새 문자열."""
    if not EXAMPLE_BLOCK.search(readme_text):
        raise SystemExit(f"{name}에 <!-- example:start --> ... <!-- example:end --> 블록이 없습니다")
    return EXAMPLE_BLOCK.sub(lambda m: f"<!-- example:start -->\n{body}\n<!-- example:end -->", readme_text, count=1)


def update_readmes(results_dir, langs=i18n.LANGS, root=ROOT):
    """README들의 보기 블록을 바꾼다. 하나라도 읽지 못하거나 블록이 없으면 아무 파일도 바꾸지 않고 멈춘다."""
    texts = {}
    for lang in langs:
        name = i18n.README[lang]
        path = Path(root) / name
        try:
            current = path.read_text(encoding="utf-8")
        except OSError as err:
            raise SystemExit(f"{name}: 읽지 못했습니다({err})")
        texts[path] = replace_example_block(current, readme_example(results_dir, lang), name)
    for path, text in texts.items():
        path.write_text(text, encoding="utf-8")


def check_sources(markdown):
    """인용 블록마다 원본 파일과 같은지 확인해 문제 목록을 돌려준다."""
    problems = []
    for m in SOURCE_BLOCK.finditer(markdown):
        rel = m.group(1)
        try:
            expected = raw_text(rel).rstrip("\n")
        except (OSError, ValueError, KeyError) as err:
            problems.append(f"{rel}: 원본을 읽지 못했습니다({err})")
            continue
        if unquote(m.group(2)) != expected:
            problems.append(f"{rel}: 인용한 글이 원본과 다릅니다")
    return problems


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if not args:
        raise SystemExit("사용법: make_examples.py <결과 디렉터리> [--readme]")
    EXAMPLES.parent.mkdir(parents=True, exist_ok=True)
    EXAMPLES.write_text(examples_md(args[0]), encoding="utf-8")
    if "--readme" in args:
        update_readmes(args[0])
    return 0


if __name__ == "__main__":
    sys.exit(main())
