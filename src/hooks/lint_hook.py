#!/usr/bin/env python3
"""Claude Code 훅의 글쓰기 점검. 알리기만 하고 막지 않는다.

PostToolUse(.md 파일의 Write|Edit): 린터(simple_korean.ko_lint)로 파일을 검사한다. 위반이 있으면 오류부터
MAX_HOOK_HITS개까지 줄 번호, 범주, 강도, 문구를 stderr로 보내고 2로 끝낸다. Edit이면 편집 전의 글도 검사하고,
편집이 더한 위반만 알린다(added_hits). 편집 전부터 있던 위반은 건수만 덧붙인다. 편집 전의 글은 tool_response의
originalFile에서 얻는다. originalFile이 없으면 new_string을 old_string으로 되돌린다. 되돌릴 자리가 하나로 정해지지 않으면(new_string이
비었거나, 파일에 없거나, 두 번 이상 나오거나, replace_all이면) 파일 전체의 위반을 알린다. PostToolUse의 종료
코드 2는 알림이다. 도구는 이미 실행되었다. 한글 비율이 MIN_HANGUL_RATIO보다 낮은 파일, Claude
설정 디렉터리와 .claude 경로의 파일, SIMPLE_KOREAN_LINT_EXCLUDE 글롭에 맞는 파일은 건너뛴다.
프로젝트의 .simple-korean.json이 깨져 있으면 기본 설정으로 검사하고 그 사실을 한 줄 알린다.

Stop: last_assistant_message가 한국어이면 ko_lint.reply_hits로 답변 규칙(굵은 글씨, em-dash, 표, 첫 줄의 헤더나
목록, 슬롭 어휘, 인사말, 맺음말)을 점검하고, 어긴 것이 있을 때만 systemMessage를 낸다. 코드 안은 세지 않는다.
em-dash, 슬롭 어휘, 인사말, 맺음말은 따옴표 인용 안도 세지 않고, 서식은 따옴표 안도 센다. 첫 줄이 아닌 헤더와
목록 항목은 답의 내용과 길이를 보고 쓸 수 있으므로 알리지 않는다. 항상 0으로 끝내므로 세션이 되풀이되지 않는다.
"""
import difflib
import fnmatch
import json
from collections import Counter, defaultdict
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT / "src"))

MAX_HOOK_HITS = 12
MAX_LINE_CHARS = 300
MIN_HANGUL_RATIO = 0.3
CLAUDE_DIR = ".claude"
REPLY_COUNTS = (("em_dash", "em-dash"), ("bold", "굵은 글씨"), ("table", "표"))
REPLY_FLAGS = (("lead_structure", "첫 줄의 헤더나 목록"),)
REPLY_FILLERS = (("opener", "인사말"), ("closer", "맺음말"))
# difflib으로 맞추는 가운데 줄 수의 상한. difflib은 반복이 많은 긴 글에서 시간이 세제곱으로 는다.
MAX_DIFF_LINES = 4000
# 줄 글의 비슷함을 재는 위반 쌍 수의 상한. 넘으면 남은 위반을 순서대로 짝짓는다.
PAIR_BUDGET = 1000
SIMILAR_CHARS = 300  # 줄 글의 비슷함은 줄 앞의 이만큼만 잰다.


def load_linter():
    try:
        from simple_korean import ko_lint  # noqa: WPS433
        return ko_lint
    except Exception:  # noqa: BLE001  린터를 못 읽으면 조용히 건너뛴다
        return None


def absolute(path, cwd=None):
    """경로를 절대 경로로 만든다. 하네스가 세션 디렉터리 기준 상대 경로를 보낼 수 있다."""
    return pathlib.Path(cwd or ".", pathlib.Path(path).expanduser()).absolute()


def variants(path):
    """적힌 그대로의 경로와 심볼릭 링크를 푼 경로. 제외 규칙은 둘 중 하나만 맞아도 적용한다."""
    return {pathlib.Path(os.path.normpath(path)), path.resolve()}


def excluded(target):
    """에이전트가 자기용으로 쓰는 마크다운과 사용자가 제외한 경로이면 참이다."""
    config_dirs = variants(absolute(os.environ.get("CLAUDE_CONFIG_DIR") or f"~/{CLAUDE_DIR}"))
    raw = os.environ.get("SIMPLE_KOREAN_LINT_EXCLUDE", "").split(os.pathsep)
    patterns = [os.path.expanduser(p) for p in raw if p]
    for form in variants(target):
        if CLAUDE_DIR in form.parts or any(form.is_relative_to(d) for d in config_dirs):
            return True
        if any(fnmatch.fnmatch(str(form), p) for p in patterns):
            return True
    return False


def one_line(text, limit=MAX_LINE_CHARS):
    """알림에 넣을 글을 한 줄로 만든다. 줄바꿈과 제어 문자는 이스케이프하고 limit자에서 자른다.

    파일 이름, 설정 경고, 문서 조각이 모델에 가는 알림의 줄 구조를 바꾸지 못하게 한다.
    """
    flat = "".join(ch if ch.isprintable() else repr(ch)[1:-1] for ch in str(text))
    return flat if len(flat) <= limit else flat[:limit] + "…"


def _detail(lint, text, target):
    """검사 결과와 설정 알림(없으면 None)을 돌려준다. 깨진 설정은 기본 설정으로 대신한다."""
    terms = lint.ko_terms
    try:
        config = terms.load_config(terms.find_config(str(target)))
    except ValueError as err:
        note = f"설정 파일을 읽지 못해 기본 설정으로 점검했습니다: {err}"
        return lint.lint_detail(text, "descriptive", config={}), note
    _, warnings = terms.apply_config(terms.load_terms(), config)
    note = "설정 경고: " + "; ".join(warnings) if warnings else None
    return lint.lint_detail(text, "descriptive", config=config), note


def _before_edit(event, text, nfc):
    """Edit 전의 글(NFC). Edit이 아니거나 하나로 정하지 못하면 None이다.

    tool_response의 originalFile을 먼저 쓴다. 없으면 text에 한 번만 나오는 new_string을 old_string으로 되돌린다.
    new_string이 두 번 이상 나오면 어느 것이 편집한 자리인지 알 수 없다.
    """
    if event.get("tool_name") != "Edit":
        return None
    response = event.get("tool_response")
    original = response.get("originalFile") if isinstance(response, dict) else None
    if isinstance(original, str):
        return nfc(original)
    tool_input = event.get("tool_input") or {}
    old, new = tool_input.get("old_string"), tool_input.get("new_string")
    if not isinstance(old, str) or not isinstance(new, str) or tool_input.get("replace_all") is True:
        return None
    old, new = nfc(old), nfc(new)
    first = text.find(new) if new else -1
    if first < 0 or text.find(new, first + 1) >= 0:
        return None
    return text[:first] + old + text[first + len(new):]


def _line_map(before_lines, after_lines):
    """편집 뒤의 줄 번호(1부터)를 편집 전의 같은 줄 번호로 잇는 dict.

    앞뒤에서 같은 줄은 그대로 잇고, 다른 가운데만 difflib으로 맞춘다. 가운데가 MAX_DIFF_LINES줄보다 길면 가운데
    줄은 잇지 않는다. 그 줄의 위반은 added_hits의 둘째 단계가 짝짓는다.
    """
    n, m = len(before_lines), len(after_lines)
    head = 0
    while head < min(n, m) and before_lines[head] == after_lines[head]:
        head += 1
    tail = 0
    while tail < min(n, m) - head and before_lines[n - 1 - tail] == after_lines[m - 1 - tail]:
        tail += 1
    same = {k: k for k in range(1, head + 1)}
    same.update((m - k, n - k) for k in range(tail))
    middle_before, middle_after = before_lines[head:n - tail], after_lines[head:m - tail]
    if max(len(middle_before), len(middle_after)) <= MAX_DIFF_LINES:
        for a, b, size in difflib.SequenceMatcher(None, middle_before, middle_after).get_matching_blocks():
            same.update((head + b + k + 1, head + a + k + 1) for k in range(size))
    return same


def _line(lines, number):
    return lines[number - 1] if 0 < number <= len(lines) else ""


def _similarity(a, b):
    return difflib.SequenceMatcher(None, a[:SIMILAR_CHARS], b[:SIMILAR_CHARS]).ratio()


def _paired(new_lines, old_lines, budget):
    """새 위반의 줄 글(new_lines)과 남은 옛 위반의 줄 글(old_lines)을 짝짓는다. 짝지은 새 위반의 색인을 돌려준다.

    줄 글이 같은 쌍(옮긴 줄)을 먼저 잇고, 남은 쌍은 줄 글이 비슷한 쌍부터 잇는다. 그래서 번호만 고친 옛 줄의 위반을
    새 위반으로 알리지 않는다. 남은 쌍이 budget[0]보다 많으면 순서대로 잇는다.
    """
    free = Counter(old_lines)
    paired = set()
    for i, line in enumerate(new_lines):
        if free[line]:
            free[line] -= 1
            paired.add(i)
    rest_old = list(free.elements())
    rest_new = [i for i in range(len(new_lines)) if i not in paired]
    if not rest_old or not rest_new:
        return paired
    cost = len(rest_old) * len(rest_new)
    if cost > budget[0]:
        return paired | set(rest_new[:len(rest_old)])
    budget[0] -= cost
    scored = sorted(((_similarity(old, new_lines[i]), -i, -j) for i in rest_new for j, old in enumerate(rest_old)),
                    reverse=True)
    used = set()
    for _, neg_i, neg_j in scored:
        if -neg_i not in paired and -neg_j not in used:
            paired.add(-neg_i)
            used.add(-neg_j)
    return paired


def added_hits(before, after, before_hits, after_hits):
    """after에만 있는 위반. 편집 뒤의 위반 가운데 편집 전의 같은 위반과 짝지은 것을 뺀다.

    첫째, 편집하지 않은 줄(_line_map)의 위반은 편집 전의 같은 줄에 (범주, 문구)가 같은 위반이 있으면 뺀다.
    둘째, 남은 위반은 (범주, 문구)가 같은 편집 전의 남은 위반과 줄 글로 짝지어 뺀다(_paired). 그래서 같은 편집이
    위반 하나를 지우고 (범주, 문구)가 같은 위반을 새로 쓰면 알리지 않는다. 문체 혼용처럼 편집이 다른 줄에 만든
    위반은 새 위반으로 남는다.
    """
    before_lines, after_lines = before.split("\n"), after.split("\n")
    same = _line_map(before_lines, after_lines)
    left = Counter((h["line"], h["category"], h["text"]) for h in before_hits)
    rest = []
    for h in after_hits:
        key = (same.get(h["line"]), h["category"], h["text"])
        if left[key]:
            left[key] -= 1
        else:
            rest.append(h)
    olds = defaultdict(list)
    for (line, category, text), count in left.items():
        olds[(category, text)] += [_line(before_lines, line)] * count
    groups = defaultdict(list)
    for index, h in enumerate(rest):
        groups[(h["category"], h["text"])].append(index)
    budget, dropped = [PAIR_BUDGET], set()
    for key, indexes in groups.items():
        new_lines = [_line(after_lines, rest[i]["line"]) for i in indexes]
        dropped.update(indexes[k] for k in _paired(new_lines, olds.get(key, []), budget))
    return [h for i, h in enumerate(rest) if i not in dropped]


def post_tool_use(event):
    path = (event.get("tool_input") or {}).get("file_path") or ""
    if not path.endswith(".md"):
        return 0
    target = absolute(path, event.get("cwd"))
    lint = load_linter()
    if lint is None or excluded(target):
        return 0
    try:
        text = target.read_text(encoding="utf-8")
    except OSError:
        return 0
    if lint.ko_text.hangul_ratio(text) < MIN_HANGUL_RATIO:
        return 0
    text = lint.ko_text.nfc(text)
    detail, note = _detail(lint, text, target)
    total, before = len(detail), _before_edit(event, text, lint.ko_text.nfc)
    if before is not None and detail:
        detail = added_hits(before, text, _detail(lint, before, target)[0], detail)
    if not detail and not note:
        return 0
    sys.stderr.write(_message(lint, one_line(target.name), detail, note, before is not None, total - len(detail)))
    return 2


def _message(lint, name, detail, note, edited, kept):
    """PostToolUse 알림 글. edited는 Edit의 차이만 본 경우이고, kept는 편집 전부터 있던 위반 수다."""
    detail = sorted(detail, key=lambda h: (h["severity"] != "error", h["line"]))
    errors = sum(1 for h in detail if h["severity"] == "error")
    counts = f"오류 {errors}건, 경고 {len(detail) - errors}건"
    if edited:
        head = f"{name}에서 이번 편집이 더한 위반은 " + (f"{counts}입니다." if detail else "없습니다.")
    else:
        head = f"{name}에 {counts}이 있습니다." if detail else f"{name}에 위반이 없습니다."
    lines = [f"simple-korean: {head}"] + ([f"  {one_line(note)}"] if note else [])
    for h in detail[:MAX_HOOK_HITS]:
        label = lint.LABELS.get(h["category"], h["category"])
        lines.append(f"  {h['line']}번 줄, {label}({lint.SEVERITY_LABELS[h['severity']]}): {one_line(h['text'])}")
    if len(detail) > MAX_HOOK_HITS:
        lines.append(f"  그 밖에 {len(detail) - MAX_HOOK_HITS}건이 더 있습니다.")
    if detail and kept:
        lines.append(f"  편집 전부터 있던 위반 {kept}건은 알리지 않았습니다.")
    lines.append("방금 쓴 파일에서 이 항목을 고친 뒤 계속하세요." if detail else "설정 파일을 고친 뒤 계속하세요.")
    return "\n".join(lines) + "\n"


def stop(event):
    reply = event.get("last_assistant_message") or ""
    lint = load_linter()
    if lint is None or lint.ko_text.hangul_ratio(reply) < MIN_HANGUL_RATIO:
        return 0
    counts = Counter(h.category for h in lint.reply_hits(reply))
    problems = [f"{label} {counts[key]}개" for key, label in REPLY_COUNTS if counts[key]]
    problems += [label for key, label in REPLY_FLAGS if counts[key]]
    problems += [f"슬롭 어휘 {counts['slop_word']}개"] if counts["slop_word"] else []
    problems += [label for key, label in REPLY_FILLERS if counts[key]]
    if problems:
        message = "simple-korean 답변 점검: " + ", ".join(problems) + ". 다음 답변에서는 이 항목을 고치세요."
        print(json.dumps({"systemMessage": message}, ensure_ascii=False))
    return 0


def main():
    try:
        event = json.load(sys.stdin)
    except Exception:  # noqa: BLE001
        return 0
    try:
        name = event.get("hook_event_name", "")
        if name == "PostToolUse":
            return post_tool_use(event)
        if name == "Stop":
            return stop(event)
    except Exception:  # noqa: BLE001  알림용 훅이다. 오류가 나도 세션을 막거나 되풀이하지 않는다
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
