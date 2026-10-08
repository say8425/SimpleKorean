#!/usr/bin/env python3
"""공개한 수치와 글을 원본 파일에서 다시 만들어 대조한다. CI가 푸시마다 돌린다.

쉬운 단어 비율을 다시 계산하려면 kiwipiepy가 있어야 한다. 로컬에서는 측정용 가상 환경으로 돌린다.

    .venv/bin/python evals/check_numbers.py

검사하는 것:
- README의 벤치마크 블록과 RESULTS.md를 원본 출력에서 다시 만든 글과 비교한다(report.py).
- README와 examples/before-after.md의 인용 블록을 원본 출력과 비교한다(make_examples.py).
- 보정 기록 RECORD.md를 hits.tsv와 보정 출력에서 다시 만들어 비교하고, CHANGELOG에 보정 줄이 있는지 본다.
- 규칙 블록 두 벌이 같은지, 핵심 문구가 SKILL.md와 규칙 블록에 모두 있는지 본다.
- 버전 문자열이 SKILL.md, 매니페스트 세 개, README 배지, CHANGELOG 첫 항목에서 같은지 본다.
"""
import difflib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CALIBRATION = HERE / "calibration"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(CALIBRATION))
import bench_common  # noqa: E402
import hits  # noqa: E402
import make_examples  # noqa: E402
import metrics  # noqa: E402
import report  # noqa: E402

KEY_PHRASES = ("서술형으로 답하세요", "em-dash를 쓰지 마세요", "첫 문장에 답", "바꾸지 마세요", "확인하다", "레포지토리")
VERSION_PATTERNS = {
    "skills/simple-korean/SKILL.md": r'version:\s*"([^"]+)"',
    ".claude-plugin/plugin.json": r'"version":\s*"([^"]+)"',
    ".claude-plugin/marketplace.json": r'"version":\s*"([^"]+)"',
    ".codex-plugin/plugin.json": r'"version":\s*"([^"]+)"',
    "README.md": r"badge/version-([0-9.]+)-",
    "CHANGELOG.md": r"(?m)^## ([0-9]+\.[0-9]+\.[0-9]+)",
}


def _diff(label, expected, found):
    lines = difflib.unified_diff(found.splitlines(), expected.splitlines(), "지금 글", "다시 만든 글", lineterm="", n=1)
    return f"{label}: 원본에서 다시 만든 글과 다릅니다\n" + "\n".join(list(lines)[:40])


def check_benchmark(readme, changelog, scenarios, require_easy=True):
    """README 벤치마크 블록, RESULTS.md, CHANGELOG의 결과 경로를 확인한다.

    require_easy가 참이면 kiwipiepy가 없을 때 멈춘다. 없으면 쉬운 단어 비율이 '측정 안 함'으로 바뀌어
    공개한 표와 달라지기 때문이다. 단위 시험만 이 값을 끈다.
    """
    m = report.README_BLOCK.search(readme)
    if not m:
        return ["README.md에 벤치마크 블록이 없습니다"]
    rel, results_dir = m.group(1), ROOT / m.group(1)
    if require_easy and metrics.easy_word_counts("확인합니다.") is None:
        return ["kiwipiepy가 없어 쉬운 단어 비율을 다시 계산하지 못했습니다. .venv/bin/python으로 돌리세요"]
    meta = json.loads((results_dir / "meta.json").read_text(encoding="utf-8"))
    problems = [f"README.md가 {label} `{meta[key]}`를 밝히지 않습니다"
                for key, label in (("model", "작성 모델"), ("judge_model", "판정 모델")) if f"`{meta[key]}`" not in readme]
    block = report.readme_block(results_dir, scenarios)
    if m.group(2) != block:
        problems.append(_diff("README 벤치마크 블록", block, m.group(2)))
    rebuilt = report.results_md(results_dir, scenarios)
    current = (results_dir / "RESULTS.md").read_text(encoding="utf-8")
    if current != rebuilt:
        problems.append(_diff(f"{rel}/RESULTS.md", rebuilt, current))
    if rel not in changelog:
        problems.append(f"CHANGELOG.md가 측정 결과 {rel}을 가리키지 않습니다")
    return problems


def check_examples(readme, examples):
    problems = make_examples.check_sources(readme) + make_examples.check_sources(examples)
    if not make_examples.SOURCE_BLOCK.search(readme):
        problems.append("README.md에 원본 인용 블록이 없습니다")
    return problems


def check_calibration(changelog, calibration=CALIBRATION):
    """RECORD.md를 다시 만들어 비교하고, 'CHANGELOG에 옮길 줄'이 CHANGELOG에 있는지 본다."""
    try:
        rebuilt = hits.record_md(Path(calibration) / "baseline", hits.read_tsv(Path(calibration) / "hits.tsv"))
    except SystemExit as err:
        return [f"보정 기록을 다시 만들지 못했습니다: {err}"]
    current = (Path(calibration) / "RECORD.md").read_text(encoding="utf-8")
    problems = [] if current == rebuilt else [_diff("evals/calibration/RECORD.md", rebuilt, current)]
    for line in rebuilt.split("## CHANGELOG에 옮길 줄", 1)[1].strip().splitlines():
        text = line.lstrip("- ").strip()
        if text and text not in changelog:
            problems.append(f"CHANGELOG.md에 보정 줄이 없습니다: {text}")
    return problems


def check_rule_block(prompt_md, style_md, skill_md):
    """규칙 블록 두 벌이 같고, 핵심 문구가 SKILL.md와 규칙 블록에 모두 있는지 본다."""
    prompt = bench_common.rule_block(prompt_md)
    style = re.sub(r"\A---\n.*?\n---\n", "", style_md, count=1, flags=re.S).strip()
    problems = [] if prompt == style else ["prompts/system-prompt.md와 output-styles/simple-korean.md의 규칙 블록이 다릅니다"]
    for phrase in KEY_PHRASES:
        problems += [f"{name}에 핵심 문구가 없습니다: {phrase}"
                     for name, text in (("SKILL.md", skill_md), ("규칙 블록", prompt)) if phrase not in text]
    return problems


def check_block_size(readme, prompt_md):
    """README가 밝힌 규칙 블록 글자 수가 훅이 넣는 블록의 실제 길이와 같은지 본다."""
    size = f"규칙 블록 {len(bench_common.rule_block(prompt_md)):,}자"
    return [] if size in readme else [f"README.md에 '{size}'가 없습니다. 훅이 세션마다 넣는 블록의 길이를 적으세요"]


def check_versions(texts):
    """{경로: 글}에서 버전 문자열을 꺼내 모두 같은지 본다."""
    found = {}
    for name, pattern in VERSION_PATTERNS.items():
        m = re.search(pattern, texts[name])
        found[name] = m.group(1) if m else None
    return [] if None not in found.values() and len(set(found.values())) == 1 else [f"버전 문자열이 다릅니다: {found}"]


REQUIRED = ("README.md", "CHANGELOG.md", "examples/before-after.md", "evals/scenarios.json",
            "evals/calibration/RECORD.md", "evals/calibration/hits.tsv", "prompts/system-prompt.md",
            "output-styles/simple-korean.md") + tuple(VERSION_PATTERNS)


def _read(rel):
    return (ROOT / rel).read_text(encoding="utf-8")


def main():
    missing = sorted({rel for rel in REQUIRED if not (ROOT / rel).is_file()})
    if missing:
        print("MISMATCH")
        print("\n".join(f" - 파일이 없습니다: {rel}" for rel in missing))
        return 1
    readme, changelog = _read("README.md"), _read("CHANGELOG.md")
    problems = (check_benchmark(readme, changelog, json.loads(_read("evals/scenarios.json")))
                + check_examples(readme, _read("examples/before-after.md"))
                + check_calibration(changelog)
                + check_rule_block(_read("prompts/system-prompt.md"), _read("output-styles/simple-korean.md"),
                                   _read("skills/simple-korean/SKILL.md"))
                + check_block_size(readme, _read("prompts/system-prompt.md"))
                + check_versions({name: _read(name) for name in VERSION_PATTERNS}))
    if problems:
        print("MISMATCH")
        for problem in problems:
            print(" -", problem)
        return 1
    print("check_numbers OK: 공개한 수치와 글이 원본 파일과 같습니다")
    return 0


if __name__ == "__main__":
    sys.exit(main())
