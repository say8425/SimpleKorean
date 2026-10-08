#!/usr/bin/env python3
"""Claude Code 훅의 글쓰기 점검. 알리기만 하고 막지 않는다.

PostToolUse(.md 파일의 Write|Edit): evals/ko_lint.py로 파일을 검사한다. 위반이 있으면 오류부터
MAX_HOOK_HITS개까지 줄 번호, 범주, 강도, 문구를 stderr로 보내고 2로 끝낸다. PostToolUse의 종료
코드 2는 알림이다. 도구는 이미 실행되었다. 한글 비율이 MIN_HANGUL_RATIO보다 낮은 파일, Claude
설정 디렉터리와 .claude 경로의 파일, SIMPLE_KOREAN_LINT_EXCLUDE 글롭에 맞는 파일은 건너뛴다.
프로젝트의 .simple-korean.json이 깨져 있으면 기본 설정으로 검사하고 그 사실을 한 줄 알린다.

Stop: last_assistant_message가 한국어이면 답변 규칙(헤더, 불릿, 굵은 글씨, em-dash, 슬롭 어휘,
인사말, 맺음말)을 점검하고, 어긴 것이 있을 때만 systemMessage를 낸다. 항상 0으로 끝내므로
세션이 되풀이되지 않는다.
"""
import fnmatch
import json
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT / "evals"))

MAX_HOOK_HITS = 12
MIN_HANGUL_RATIO = 0.3
CLAUDE_DIR = ".claude"
REPLY_COUNTS = (("em_dash", "em-dash"), ("bold_spans", "굵은 글씨"), ("headers", "헤더"), ("bullets", "목록 항목"))


def load_linter():
    try:
        import ko_lint  # noqa: WPS433
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


def _detail(lint, text, target):
    """검사 결과와 설정 알림(없으면 None)을 돌려준다. 깨진 설정은 기본 설정으로 대신한다."""
    try:
        return lint.lint_detail(text, "descriptive", path=str(target)), None
    except ValueError as err:
        note = f"설정 파일을 읽지 못해 기본 설정으로 점검했습니다: {err}"
        return lint.lint_detail(text, "descriptive", config={}), note


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
    detail, note = _detail(lint, text, target)
    if not detail and not note:
        return 0
    detail = sorted(detail, key=lambda h: (h["severity"] != "error", h["line"]))
    errors = sum(1 for h in detail if h["severity"] == "error")
    lines = [f"simple-korean: {target.name}에 오류 {errors}건, 경고 {len(detail) - errors}건이 있습니다."]
    lines += [f"  {note}"] if note else []
    for h in detail[:MAX_HOOK_HITS]:
        label = lint.LABELS.get(h["category"], h["category"])
        lines.append(f"  {h['line']}번 줄, {label}({lint.SEVERITY_LABELS[h['severity']]}): {h['text']}")
    if len(detail) > MAX_HOOK_HITS:
        lines.append(f"  그 밖에 {len(detail) - MAX_HOOK_HITS}건이 더 있습니다.")
    lines.append("방금 쓴 파일에서 이 항목을 고친 뒤 계속하세요.")
    sys.stderr.write("\n".join(lines) + "\n")
    return 2


def stop(event):
    reply = event.get("last_assistant_message") or ""
    lint = load_linter()
    if lint is None or lint.ko_text.hangul_ratio(reply) < MIN_HANGUL_RATIO:
        return 0
    counts = lint.reader_check(reply)["counts"]
    problems = [f"{label} {counts[key]}개" for key, label in REPLY_COUNTS if counts[key]]
    slop = len(lint.ko_rules.SLOP_RX.findall(lint.ko_text.mask(lint.ko_text.nfc(reply))))
    if slop:
        problems.append(f"슬롭 어휘 {slop}개")
    if counts["opener"]:
        problems.append("인사말")
    if counts["closer"]:
        problems.append("맺음말")
    if problems:
        message = "simple-korean 답변 점검: " + ", ".join(problems) + ". 서술형으로 답하세요."
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
