#!/usr/bin/env python3
"""전후 예시를 원본 출력에서 만든다. 고를 과제와 질문은 측정 전에 정했다(PICKS). 글은 고치지 않는다.

    python3 evals/make_examples.py evals/results/<날짜>            # examples/before-after.md를 쓴다
    python3 evals/make_examples.py evals/results/<날짜> --readme   # README 다섯 개의 보기 블록도 바꾼다
    python3 evals/make_examples.py evals/results/<날짜> --diffs before   # examples/diffs/에 '전' 글을 쓴다
    python3 evals/make_examples.py evals/results/<날짜> --diffs after    # examples/diffs/에 '후' 글을 쓴다

examples/diffs/에는 예시마다 원문만 담은 파일이 하나씩 있다. '전'으로 커밋한 뒤 '후'로 바꿔 커밋하면 GitHub가 그
커밋에서 두 글의 차이를 보인다. 초안이 있는 다듬기 과제의 '전'은 초안이고, 나머지는 스킬 없이 만든 출력이다.
main은 squash 병합만 받으므로 두 단계를 PR 두 개로 차례로 병합한다(#25, #26). 그래서 검사는 두 단계를 모두 받는다.
새 결과 디렉터리로 바꾸면 이렇게 diff 커밋을 새로 만들고 DIFF_URL과 DIFF_RESULTS를 고친다.
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
DIFFS = Path("examples", "diffs")
# examples/diffs/를 '전'에서 '후'로 바꾼 커밋(#26). 이 커밋의 diff가 예시마다 두 글의 차이를 보인다.
DIFF_URL = "https://github.com/say8425/SimpleKorean/commit/ca720c2beaed9572581ed132e99237ad2e3d794a"
# DIFF_URL의 커밋을 만든 결과 디렉터리. README가 다른 결과를 가리키면 check_numbers.py가 알린다.
DIFF_RESULTS = "evals/results/2026-10-21"
STAGES = ("before", "after")
RUN = 1
DOC_PICKS = (
    ("polish", "plain", "초안 다듬기(절차문)"),
    ("readme-intro", "plain", "README 소개(설명문)"),
    ("troubleshooting", "plain", "문제 해결(절차문)"),
    ("error-message", "plain", "오류 메시지"),
    ("release-notes", "strict", "릴리스 노트(엄격 모드)"),
)
REPLY_PICKS = (("oom", "OOMKilled 질문"), ("cache", "캐시 무효화 질문"))
# README 보기 블록은 문서 예시 하나를 좌우 표로 보인다. 답변 예시는 코드 블록이 표 칸보다 넓어서
# 오른쪽 칸을 밀어내므로 examples/before-after.md에만 둔다. 보기 예시는 초안 다듬기 과제다. 이 과제의 초안에는
# em-dash, 굵은 글씨, 가운뎃점이 들어 있어서 스킬이 이것을 지우는지 보인다.
README_PICK = ("polish", "plain")
# 표 칸 하나에 들어가는 코드 줄의 너비다. 고정폭 글꼴의 칸으로 세고, 넓은 글자(한글 등)는 두 칸이다.
# 이보다 넓은 코드 줄이 있으면 칸이 넓어져 옆 칸을 밀어낸다. 보기 표는 초안까지 세 칸이다.
CELL_CODE_COLUMNS = 34
COND_LABELS = {"plain": "기본 모드", "strict": "엄격 모드"}
EXAMPLE_BLOCK = re.compile(r"<!-- example:start -->\n(.*?)\n<!-- example:end -->", re.S)
SOURCE_BLOCK = re.compile(
    r"<!-- source: (\S+) -->\n<!-- simple-korean: off -->\n(.*?)\n<!-- simple-korean: on -->", re.S)
# 다듬기 과제의 초안 인용. 경로는 결과 디렉터리에 복사한 입력(inputs/scenarios.json)이고, # 뒤는 과제 id다.
DRAFT_BLOCK = re.compile(
    r"<!-- draft: (\S+)#(\S+) -->\n<!-- simple-korean: off -->\n(.*?)\n<!-- simple-korean: on -->", re.S)


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


def inputs_rel(results_dir):
    """결과 디렉터리에 복사한 문서 과제 입력의 레포지토리 기준 경로(bench_common.save_inputs)."""
    return Path(results_dir, "inputs", "scenarios.json").resolve().relative_to(ROOT).as_posix()


def draft_text(rel, scenario):
    """레포지토리 기준 경로의 입력 파일에서 그 과제의 초안. 파일이나 초안이 없으면 None이다."""
    path = ROOT / rel
    if not path.exists():
        return None
    return next((s.get("draft") for s in json.loads(path.read_text(encoding="utf-8")) if s["id"] == scenario), None)


def draft_block(rel, scenario):
    return (f"<!-- draft: {rel}#{scenario} -->\n<!-- simple-korean: off -->\n"
            f"{quote(draft_text(rel, scenario))}\n<!-- simple-korean: on -->")


def _pair(results_dir, sub, item, cond, ext):
    base = Path(results_dir, sub).resolve().relative_to(ROOT).as_posix()
    return f"{base}/baseline__{item}__r{RUN}.{ext}", f"{base}/{cond}__{item}__r{RUN}.{ext}"


def _section(title, before, after, after_label, draft=None):
    """예시 절 하나. draft가 (입력 경로, 과제 id)이면 두 조건이 다듬은 초안을 먼저 싣는다."""
    parts = [f"## {title}"]
    if draft:
        parts += [f"초안: `{draft[0]}`의 `{draft[1]}` 과제", draft_block(*draft)]
    return "\n\n".join(parts + [f"전: 스킬 없음, `{before}`", source_block(before),
                                 f"후: {after_label}, `{after}`", source_block(after)])


def examples_md(results_dir):
    """examples/before-after.md 전체."""
    parts = ["# 전후 예시",
             "'전'은 스킬 없이 만든 원본 출력입니다. '후'는 같은 과제를 스킬을 켜고 만든 원본 출력입니다. "
             "두 글 모두 고치지 않고 옮겼습니다. 다듬기 과제에는 두 조건에 준 초안도 싣습니다. "
             "과제와 질문은 측정 전에 정했습니다(`evals/make_examples.py`의 PICKS). "
             "`python3 evals/check_numbers.py`가 이 파일의 글을 원본 파일과 글자 하나까지 대조합니다.",
             "`examples/diffs/`에는 같은 예시의 '후' 글만 과제마다 파일 하나로 나눠 두었습니다. "
             f"예시마다 바뀐 곳은 [이 커밋의 diff]({DIFF_URL})에서 볼 수 있습니다. "
             "다듬기 과제의 diff는 초안과 '후' 글의 차이를 보입니다."]
    rel = inputs_rel(results_dir)
    for scenario, cond, title in DOC_PICKS:
        before, after = _pair(results_dir, "docs", scenario, cond, "json")
        draft = (rel, scenario) if draft_text(rel, scenario) else None
        parts.append(_section(title, before, after, COND_LABELS[cond], draft))
    for question, title in REPLY_PICKS:
        before, after = _pair(results_dir, "reply", question, "plain", "txt")
        parts.append(_section(f"답변: {title}", before, after, "SimpleKorean"))
    return "\n\n".join(parts) + "\n"


def diff_texts(results_dir, doc_picks=DOC_PICKS, reply_picks=REPLY_PICKS):
    """examples/diffs/의 (파일 이름, 전 글, 후 글) 목록."""
    rel, items = inputs_rel(results_dir), []
    for scenario, cond, _ in doc_picks:
        before, after = _pair(results_dir, "docs", scenario, cond, "json")
        items.append((f"{scenario}.md", draft_text(rel, scenario) or raw_text(before), raw_text(after)))
    for question, _ in reply_picks:
        before, after = _pair(results_dir, "reply", question, "plain", "txt")
        items.append((f"reply-{question}.md", raw_text(before), raw_text(after)))
    return items


def _diff_file(text):
    """examples/diffs/의 파일 하나에 쓰는 글. 원문 끝의 줄바꿈을 하나로 맞춘다."""
    return text.rstrip("\n") + "\n"


def write_diffs(results_dir, stage, root=ROOT, **picks):
    """examples/diffs/에 stage('before' 또는 'after')의 글을 쓴다."""
    if stage not in STAGES:
        raise SystemExit(f"--diffs에는 {' 또는 '.join(STAGES)}를 쓰세요")
    out = Path(root) / DIFFS
    out.mkdir(parents=True, exist_ok=True)
    for name, before, after in diff_texts(results_dir, **picks):
        (out / name).write_text(_diff_file(before if stage == "before" else after), encoding="utf-8")


def check_diffs(results_dir, root=ROOT, **picks):
    """examples/diffs/의 파일마다 원본의 전이나 후와 같은지 확인해 문제 목록을 돌려준다."""
    problems, names = [], set()
    for name, before, after in diff_texts(results_dir, **picks):
        names.add(name)
        rel = (DIFFS / name).as_posix()
        path = Path(root) / DIFFS / name
        if not path.is_file():
            problems.append(f"{rel}: 파일이 없습니다")
        elif path.read_text(encoding="utf-8") not in (_diff_file(before), _diff_file(after)):
            problems.append(f"{rel}: 원본의 전과 후 어느 쪽과도 다릅니다")
    extra = sorted(p.name for p in (Path(root) / DIFFS).glob("*.md") if p.name not in names)
    problems += [f"{(DIFFS / name).as_posix()}: 고른 예시에 없는 파일입니다" for name in extra]
    return problems


def diff_url_problems(results_rel):
    """README가 가리키는 결과 디렉터리와 DIFF_URL을 만든 결과 디렉터리가 다르면 문제 목록을 돌려준다."""
    if Path(results_rel).as_posix().rstrip("/") == DIFF_RESULTS:
        return []
    return [f"DIFF_URL은 {DIFF_RESULTS}로 만든 diff입니다. README는 {results_rel}을 가리킵니다. "
            "make_examples.py 머리의 순서대로 diff 커밋을 새로 만들고 DIFF_URL과 DIFF_RESULTS를 고치세요"]


def _cell(rel):
    """표 칸 하나. GitHub는 HTML 칸 안의 마크다운을 앞뒤 빈 줄이 있어야 그린다."""
    return f'<td valign="top">\n\n{source_block(rel)}\n\n</td>'


def readme_example(results_dir, lang="ko"):
    """README 보기 블록의 본문. 표의 칸은 차례로 초안, 스킬 없이 다듬은 문서, SimpleKorean을 켜고 다듬은 문서다.

    초안을 표 밖에 따로 인용하면 초안과 거의 같은 스킬 없는 문서가 두 번 실린 것처럼 보인다. 그래서 세 글을 한 표에
    나란히 둔다. 인용한 글은 어느 언어에서나 한국어 원문이다.
    """
    scenario, cond = README_PICK
    before, after = _pair(results_dir, "docs", scenario, cond, "json")
    text, rel = i18n.TEXT[lang], inputs_rel(results_dir)
    table = "\n".join([
        "<table>", "<tr>",
        f'<th width="34%">{text["example_draft_head"]}</th>',
        f'<th width="33%">{text["example_before"]}</th>',
        f'<th width="33%">{text["example_after"]}</th>',
        "</tr>", "<tr>",
        f'<td valign="top">\n\n{draft_block(rel, scenario)}\n\n</td>', _cell(before), _cell(after),
        "</tr>", "</table>",
    ])
    return "\n\n".join([table, text["example_files"].format(before=before, after=after),
                         text["example_draft"].format(src=rel, href=i18n.link(lang, rel), id=scenario),
                         text["example_docs"].format(href=i18n.link(lang, "examples/before-after.md"), diff=DIFF_URL)])


def wide_code_lines(text):
    """코드 블록 안에서 CELL_CODE_COLUMNS칸보다 넓은 줄의 목록."""
    wide, fence = [], None
    for line in text.splitlines():
        run = re.match(r"[^\S\n]{0,3}(`{3,}|~{3,})", line)
        if run and fence is None:
            fence = run.group(1)
            continue
        # 닫는 울타리는 여는 것과 같은 글자로, 같거나 더 길게 쓰고 뒤에 다른 글이 없어야 한다
        if run and run.group(1)[0] == fence[0] and len(run.group(1)) >= len(fence) and not line[run.end():].strip():
            fence = None
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
    rel = inputs_rel(results_dir)
    # README의 보기 설명(손으로 쓴 문단과 칸 이름)은 다듬기 과제를 가정한다
    if (ROOT / rel).exists() and not draft_text(rel, scenario):
        problems.append(f"{rel}: README_PICK 과제 {scenario}에 초안이 없습니다. README의 보기 설명은 다듬기 과제를 가정합니다")
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
    for m in DRAFT_BLOCK.finditer(markdown):
        rel, scenario = m.group(1), m.group(2)
        try:
            expected = draft_text(rel, scenario)
        except (OSError, ValueError, KeyError) as err:
            problems.append(f"{rel}#{scenario}: 초안을 읽지 못했습니다({err})")
            continue
        if expected is None:
            problems.append(f"{rel}#{scenario}: 초안이 없습니다")
        elif unquote(m.group(3)) != expected.rstrip("\n"):
            problems.append(f"{rel}#{scenario}: 인용한 초안이 원본과 다릅니다")
    return problems


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if not args:
        raise SystemExit("사용법: make_examples.py <결과 디렉터리> [--readme] [--diffs before|after]")
    stage = None
    if "--diffs" in args:
        i = args.index("--diffs")
        stage = args[i + 1] if i + 1 < len(args) else ""
        # 다른 파일을 쓰기 전에 멈춘다
        if stage not in STAGES:
            raise SystemExit(f"--diffs에는 {' 또는 '.join(STAGES)}를 쓰세요")
    try:
        text = examples_md(args[0])
    except (OSError, ValueError, KeyError) as err:
        raise SystemExit(f"{args[0]}: 보기에 쓸 원본을 읽지 못했습니다({err}). DOC_PICKS의 과제가 모두 있는 결과 디렉터리를 쓰세요")
    EXAMPLES.parent.mkdir(parents=True, exist_ok=True)
    EXAMPLES.write_text(text, encoding="utf-8")
    if "--readme" in args:
        update_readmes(args[0])
    if stage:
        write_diffs(args[0], stage)
    return 0


if __name__ == "__main__":
    sys.exit(main())
