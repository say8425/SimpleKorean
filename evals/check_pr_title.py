#!/usr/bin/env python3
"""PR 제목이 커밋 규칙을 지키는지 본다. squash 병합에서는 PR 제목이 main의 커밋 제목과 CHANGELOG의 한 줄이 된다.

    PR_TITLE='fix: 설정 파일의 지정형을 20자로 제한한다' python3 evals/check_pr_title.py

규칙: '<유형>: <한국어 해라체 문장>'. 유형은 TYPES 가운데 하나이고, 범위와 '!'는 쓰지 않는다.
내용은 린터 관문(--gate=warning)을 통과해야 한다. 제목은 외부 입력이므로 환경 변수로만 받는다.
"""
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import ko_lint  # noqa: E402
import ko_text  # noqa: E402

TYPES = ("feat", "fix", "perf", "refactor", "docs", "test", "chore", "ci")
TITLE = re.compile(r"(" + "|".join(TYPES) + r"): (\S.*)")
EXAMPLE = "fix: 설정 파일의 지정형을 20자로 제한한다"


def problems(title):
    """제목의 문제 목록. 비어 있으면 통과다."""
    m = TITLE.fullmatch(title)
    if not m:
        return [f"제목은 '<유형>: <내용>' 형식이어야 합니다. 유형은 {', '.join(TYPES)} 가운데 하나입니다. 예: {EXAMPLE}"]
    content = m.group(2)
    found = []
    if ko_text.register(content) != "haera":
        found.append(f"내용을 해라체 문장으로 쓰세요(예: 고친다, 더한다, 바꾼다): {content}")
    for hit in ko_lint.lint_detail(content, config={}):
        found.append(f"린터 {ko_lint.LABELS.get(hit['category'], hit['category'])}: {hit['text']}")
    return found


def main():
    title = os.environ.get("PR_TITLE", "")
    found = problems(title)
    if found:
        print(f"PR 제목이 규칙에 맞지 않습니다: {title}")
        for problem in found:
            print(" -", problem)
        return 1
    print(f"PR 제목 OK: {title}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
