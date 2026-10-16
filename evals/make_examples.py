#!/usr/bin/env python3
"""전후 예시를 원본 출력에서 만든다. 고를 과제와 질문은 측정 전에 정했다(PICKS). 글은 고치지 않는다.

    python3 evals/make_examples.py evals/results/<날짜>            # examples/before-after.md를 쓴다
    python3 evals/make_examples.py evals/results/<날짜> --readme   # README 다섯 개의 보기 블록도 바꾼다
"""
import json
import re
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
README_PICK = "oom"
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
             "'전'은 스킬 없이 만든 원본 출력이고, '후'는 같은 과제를 스킬을 켜고 만든 원본 출력입니다. "
             "두 글 모두 고치지 않고 옮겼습니다. 과제와 질문은 측정 전에 정했습니다(`evals/make_examples.py`의 PICKS). "
             "`python3 evals/check_numbers.py`가 이 파일의 글을 원본 파일과 글자 하나까지 대조합니다."]
    for scenario, cond, title in DOC_PICKS:
        before, after = _pair(results_dir, "docs", scenario, cond, "json")
        parts.append(_section(title, before, after, COND_LABELS[cond]))
    for question, title in REPLY_PICKS:
        before, after = _pair(results_dir, "reply", question, "plain", "txt")
        parts.append(_section(f"답변: {title}", before, after, "SimpleKorean"))
    return "\n\n".join(parts) + "\n"


def readme_example(results_dir, lang="ko"):
    """README 보기 블록의 본문. 인용한 출력은 어느 언어에서나 한국어 원문이다."""
    before, after = _pair(results_dir, "reply", README_PICK, "plain", "txt")
    text = i18n.TEXT[lang]
    return "\n\n".join([text["example_before"].format(path=before), source_block(before),
                        text["example_after"].format(path=after), source_block(after),
                        text["example_docs"].format(href=i18n.link(lang, "examples/before-after.md"))])


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
