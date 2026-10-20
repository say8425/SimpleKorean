#!/usr/bin/env python3
"""공개한 수치와 글을 원본 파일에서 다시 만들어 대조한다. CI가 푸시마다 돌린다.

쉬운 단어 비율을 다시 계산하려면 kiwipiepy가 있어야 한다. 로컬에서는 측정용 가상 환경으로 돌린다.

    .venv/bin/python evals/check_numbers.py

검사하는 것:
- README 다섯 개의 벤치마크 블록과 RESULTS.md를 원본 출력에서 다시 만든 글과 비교한다(report.py, readme_i18n.py).
- README 다섯 개의 보기 블록과 examples/before-after.md의 인용 블록을 원본 출력과 비교한다(make_examples.py).
- 번역판의 제목, 레포 링크, 언어 선택 줄, 블록 표시가 한국어판과 맞는지 본다.
- 보정 기록 RECORD.md를 hits.tsv와 보정 출력에서 다시 만들어 비교한다.
- 측정 결과 경로와 보정 줄이 CHANGELOG에 있는지 본다. 마지막 릴리스보다 늦은 측정과 보정은 건너뛴다.
- 규칙 블록 두 벌이 같은지, 핵심 문구가 SKILL.md와 규칙 블록에 모두 있는지 본다.
- SKILL.md description에 스펙 10절의 호출 문구가 모두 있는지 본다.
- 버전 문자열이 SKILL.md, 플러그인 매니페스트 세 개, .release-please-manifest.json, CHANGELOG 첫 항목에서 같은지 본다.
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
import readme_i18n as i18n  # noqa: E402
import report  # noqa: E402

KEY_PHRASES = ("헤더와 목록을 써도 됩니다", "em-dash를 쓰지 마세요", "첫 문장에 답", "바꾸지 마세요", "확인하다", "레포지토리", "굵은 글씨와 표", "첫 문장 뒤에 두세요",
               "엄격 모드, 통제 언어, KS A 0001, STE, ASD-STE100")
SKILL_TRIGGERS = ("쉬운 한국어", "번역투 빼 줘", "AI 티 안 나게", "문서 다듬어 줘", "통제 언어", "엄격 모드", "KS A 0001",
                  "plain Korean", "Simple Korean", "controlled language")
VERSION_PATTERNS = {
    "skills/simple-korean/SKILL.md": r'version:\s*"([^"]+)"',
    ".claude-plugin/plugin.json": r'"version":\s*"([^"]+)"',
    ".claude-plugin/marketplace.json": r'"version":\s*"([^"]+)"',
    ".codex-plugin/plugin.json": r'"version":\s*"([^"]+)"',
    ".release-please-manifest.json": r'"\."\s*:\s*"([^"]+)"',
    "CHANGELOG.md": r"(?m)^## \[?([0-9]+\.[0-9]+\.[0-9]+)",
}
CHANGELOG_ENTRY = re.compile(r"(?m)^## \[?[0-9]+\.[0-9]+\.[0-9]+\]?.*?([0-9]{4}-[0-9]{2}-[0-9]{2})")
RECORD_DATE = re.compile(r"\A# 보정 기록 \(([0-9]{4}-[0-9]{2}-[0-9]{2})\)")


def _diff(label, expected, found):
    lines = difflib.unified_diff(found.splitlines(), expected.splitlines(), "지금 글", "다시 만든 글", lineterm="", n=1)
    return f"{label}: 원본에서 다시 만든 글과 다릅니다\n" + "\n".join(list(lines)[:40])


def latest_release_date(changelog):
    """CHANGELOG 첫 항목의 날짜(YYYY-MM-DD). 옛 형식과 release-please 형식을 모두 읽고, 항목이 없으면 None이다."""
    m = CHANGELOG_ENTRY.search(changelog)
    return m.group(1) if m else None


def unreleased(date, changelog):
    """측정 날짜가 마지막 릴리스 날짜보다 늦으면 참이다. 같은 날이면 릴리스한 측정으로 본다."""
    latest = latest_release_date(changelog)
    return latest is not None and date > latest


KIWI_MISSING = "kiwipiepy가 없어 쉬운 단어 비율을 다시 계산하지 못했습니다. .venv/bin/python으로 돌리세요"
FENCES = ("```", "~~~")
HEADING = re.compile(r"(#{1,6}) ")
LINK = re.compile(r'\]\(([^)\s]+)\)|(?:href|src)="([^"]+)"')
EXTERNAL = ("http://", "https://", "mailto:", "#")
MARKERS = ("<!-- benchmark:start ", "<!-- benchmark:end -->", "<!-- example:start -->", "<!-- example:end -->")


def check_benchmark(readme, changelog, scenarios, require_easy=True, stats=None):
    """한국어 README 벤치마크 블록, RESULTS.md, CHANGELOG의 결과 경로를 확인한다.

    require_easy가 참이면 kiwipiepy가 없을 때 멈춘다. 없으면 쉬운 단어 비율이 '측정 안 함'으로 바뀌어
    공개한 표와 달라지기 때문이다. 단위 시험만 이 값을 끈다. stats는 report.benchmark_stats의 결과이고,
    없으면 여기서 센다.
    """
    m = report.README_BLOCK.search(readme)
    if not m:
        return ["README.md에 벤치마크 블록이 없습니다"]
    rel, results_dir = m.group(1), ROOT / m.group(1)
    if require_easy and metrics.easy_word_counts("확인합니다.") is None:
        return [KIWI_MISSING]
    meta = json.loads((results_dir / "meta.json").read_text(encoding="utf-8"))
    problems = check_benchmark_block(readme, "ko", meta, stats or report.benchmark_stats(results_dir, scenarios))
    rebuilt = report.results_md(results_dir, scenarios)
    current = (results_dir / "RESULTS.md").read_text(encoding="utf-8")
    if current != rebuilt:
        problems.append(_diff(f"{rel}/RESULTS.md", rebuilt, current))
    if rel not in changelog and not unreleased(meta["date"], changelog):
        problems.append(f"CHANGELOG.md가 측정 결과 {rel}을 가리키지 않습니다. 이 결과를 싣는 릴리스 항목에 경로를 적으세요")
    return problems


def check_benchmark_block(text, lang, meta, stats):
    """README 하나의 벤치마크 블록과 모델 이름을 본다. 블록은 그 언어로 다시 만든 글과 같아야 한다."""
    name = i18n.README[lang]
    problems = [f"{name}가 {label} `{meta[key]}`를 밝히지 않습니다"
                for key, label in (("model", "작성 모델"), ("judge_model", "판정 모델")) if f"`{meta[key]}`" not in text]
    block = report.render_readme_block(stats, lang)
    current = report.README_BLOCK.search(text).group(2)
    if current != block:
        problems.append(_diff(f"{name} 벤치마크 블록", block, current))
    return problems


def check_examples(readme, examples):
    """인용한 출력이 원본과 같은지 보고, 한국어 README의 보기 블록 전체를 다시 만들어 대조한다."""
    problems = make_examples.check_sources(readme) + make_examples.check_sources(examples)
    if not make_examples.SOURCE_BLOCK.search(readme):
        problems.append("README.md에 원본 인용 블록이 없습니다")
    bench = report.README_BLOCK.search(readme)
    if bench:
        problems += check_example_block(readme, "ko", ROOT / bench.group(1))
    return problems


def check_example_block(text, lang, results_dir):
    """보기 블록 전체(설명 문장과 인용)를 그 언어로 다시 만든 글과 대조한다."""
    name = i18n.README[lang]
    m = make_examples.EXAMPLE_BLOCK.search(text)
    if not m:
        return [f"{name}에 보기 블록이 없습니다"]
    problems = make_examples.pick_problems(results_dir) if lang == "ko" else []
    expected = make_examples.readme_example(results_dir, lang)
    return problems + ([] if m.group(1) == expected else [_diff(f"{name} 보기 블록", expected, m.group(1))])


def check_calibration(changelog, calibration=CALIBRATION):
    """RECORD.md를 다시 만들어 비교하고, 'CHANGELOG에 옮길 줄'이 CHANGELOG에 있는지 본다.

    마지막 릴리스보다 늦은 보정은 아직 실을 릴리스 항목이 없으므로 CHANGELOG를 보지 않는다.
    """
    try:
        rebuilt = hits.record_md(Path(calibration) / "baseline", hits.read_tsv(Path(calibration) / "hits.tsv"))
    except SystemExit as err:
        return [f"보정 기록을 다시 만들지 못했습니다: {err}"]
    current = (Path(calibration) / "RECORD.md").read_text(encoding="utf-8")
    problems = [] if current == rebuilt else [_diff("evals/calibration/RECORD.md", rebuilt, current)]
    date = RECORD_DATE.search(rebuilt)
    if date and unreleased(date.group(1), changelog):
        return problems
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


def check_triggers(skill_md):
    """SKILL.md frontmatter의 description에 스펙 10절의 호출 문구가 모두 있는지 본다. 줄바꿈은 공백으로 읽는다."""
    front = re.search(r"\A---\n(.*?)\n---\n", skill_md, re.S)
    desc = re.search(r"(?ms)^description:(.*?)(?=^\S|\Z)", front.group(1)) if front else None
    text = " ".join(desc.group(1).split()) if desc else ""
    return [f"SKILL.md description에 호출 문구가 없습니다: {t}" for t in SKILL_TRIGGERS if t not in text]


def check_block_size(readme, prompt_md, lang="ko"):
    """README가 밝힌 규칙 블록 글자 수가 훅이 넣는 블록의 실제 길이와 같은지 본다. 문구는 언어마다 다르다."""
    n = len(bench_common.rule_block(prompt_md))
    size = i18n.TEXT[lang]["block_size"].format(n=i18n.grouped(n, lang))
    return [] if size in readme else [f"{i18n.README[lang]}에 '{size}'가 없습니다. 훅이 세션마다 넣는 블록의 길이를 적으세요"]


def check_versions(texts):
    """{경로: 글}에서 버전 문자열을 꺼내 모두 같은지 본다."""
    found = {}
    for name, pattern in VERSION_PATTERNS.items():
        m = re.search(pattern, texts[name])
        found[name] = m.group(1) if m else None
    return [] if None not in found.values() and len(set(found.values())) == 1 else [f"버전 문자열이 다릅니다: {found}"]


def _prose(text):
    """코드 블록과 인용 블록 밖의 줄. 인라인 코드는 지운다."""
    lines, fenced = [], False
    for line in text.split("\n"):
        if line.startswith(FENCES):
            fenced = not fenced
            continue
        if not fenced and not line.startswith(">"):
            lines.append(re.sub(r"`[^`]*`", "", line))
    return lines


def readme_outline(text, lang):
    """(제목 수준 목록, 레포 링크 목록, 문제 목록). 링크는 레포 기준 경로이고, 언어 선택 줄은 뺀다."""
    prose = _prose(text.replace(i18n.language_line(lang), ""))
    levels, links, problems = [], [], []
    for line in prose:
        heading = HEADING.match(line)
        if heading:
            levels.append(len(heading.group(1)))
        for m in LINK.finditer(line):
            target = m.group(1) or m.group(2)
            if target.startswith(EXTERNAL):
                continue
            if lang != "ko":
                if not target.startswith("../"):
                    problems.append(f"{i18n.README[lang]}: 레포 링크에 ../가 없습니다: {target}")
                    continue
                target = target[3:]
            links.append(target)
    return levels, links, problems


def check_readme_structure(ko_readme, lang, text, root=None):
    """README 하나의 구조를 본다. 언어 선택 줄, 블록 표시, 링크한 파일, 번역판이면 한국어판과 같은 제목과 링크."""
    root = Path(root) if root else ROOT
    name = i18n.README[lang]
    line = i18n.language_line(lang)
    problems = [] if text.count(line) == 1 else [f"{name}: 언어 선택 줄이 한 번 있어야 합니다. 이 블록을 그대로 쓰세요:\n{line}"]
    problems += [f"{name}: '{marker.strip()}' 표시가 한 번 있어야 합니다" for marker in MARKERS if text.count(marker) != 1]
    levels, links, found = readme_outline(text, lang)
    problems += found
    if lang != "ko":
        ko_levels, ko_links, _ = readme_outline(ko_readme, "ko")
        if levels != ko_levels:
            problems.append(f"{name}: 제목 수준이 한국어판과 다릅니다. 한국어판 {ko_levels}, 이 파일 {levels}")
        if links != ko_links:
            diff = difflib.unified_diff(ko_links, links, "README.md", name, lineterm="", n=0)
            problems.append(f"{name}: 레포 링크가 한국어판과 다릅니다\n" + "\n".join(diff))
    problems += [f"{name}: 링크한 파일이 없습니다: {t}" for t in links if not (root / t.split("#", 1)[0]).exists()]
    return problems


def check_translation(lang, text, ko_readme, scenarios, prompt_md, stats=None, root=None):
    """번역판 하나를 검사한다. 결과 경로, 생성 블록 두 개, 인용, 모델 이름, 규칙 블록 글자 수, 구조를 본다."""
    name = i18n.README[lang]
    m = report.README_BLOCK.search(text)
    if not m:
        return [f"{name}에 벤치마크 블록이 없습니다"] + check_readme_structure(ko_readme, lang, text, root)
    if stats is None:
        ko = report.README_BLOCK.search(ko_readme)
        if not ko:
            return ["README.md에 벤치마크 블록이 없습니다"]
        stats = report.benchmark_stats(ROOT / ko.group(1), scenarios)
    results_dir = ROOT / stats["rel"]
    problems = [] if m.group(1) == stats["rel"] else [f"{name}의 결과 경로 {m.group(1)}가 한국어판({stats['rel']})과 다릅니다"]
    meta = json.loads((results_dir / "meta.json").read_text(encoding="utf-8"))
    return (problems + check_benchmark_block(text, lang, meta, stats) + make_examples.check_sources(text)
            + check_example_block(text, lang, results_dir) + check_block_size(text, prompt_md, lang)
            + check_readme_structure(ko_readme, lang, text, root))


REQUIRED = ("README.md", "CHANGELOG.md", "examples/before-after.md", "evals/scenarios.json",
            "evals/calibration/RECORD.md", "evals/calibration/hits.tsv", "prompts/system-prompt.md",
            "output-styles/simple-korean.md") + tuple(VERSION_PATTERNS) + tuple(i18n.README[lang] for lang in i18n.LANGS[1:])


def _read(rel):
    return (ROOT / rel).read_text(encoding="utf-8")


def translation_problems(lang):
    """레포에 있는 번역판 하나를 검사한다. 번역하는 동안 한 언어만 볼 때 쓴다(.venv/bin/python으로 돌린다)."""
    missing = [f"파일이 없습니다: {rel}" for rel in ("README.md", i18n.README[lang]) if not (ROOT / rel).is_file()]
    if missing:
        return missing
    if metrics.easy_word_counts("확인합니다.") is None:
        return [KIWI_MISSING]
    return check_translation(lang, _read(i18n.README[lang]), _read("README.md"),
                             json.loads(_read("evals/scenarios.json")), _read("prompts/system-prompt.md"))


def main():
    missing = sorted({rel for rel in REQUIRED if not (ROOT / rel).is_file()})
    if missing:
        print("MISMATCH")
        print("\n".join(f" - 파일이 없습니다: {rel}" for rel in missing))
        return 1
    readme, changelog = _read("README.md"), _read("CHANGELOG.md")
    scenarios, prompt = json.loads(_read("evals/scenarios.json")), _read("prompts/system-prompt.md")
    bench = report.README_BLOCK.search(readme)
    stats = None
    if bench and metrics.easy_word_counts("확인합니다.") is not None:
        stats = report.benchmark_stats(ROOT / bench.group(1), scenarios)
    problems = (check_benchmark(readme, changelog, scenarios, stats=stats)
                + check_examples(readme, _read("examples/before-after.md"))
                + check_calibration(changelog)
                + check_rule_block(prompt, _read("output-styles/simple-korean.md"), _read("skills/simple-korean/SKILL.md"))
                + check_triggers(_read("skills/simple-korean/SKILL.md"))
                + check_block_size(readme, prompt)
                + check_readme_structure(readme, "ko", readme)
                + check_versions({name: _read(name) for name in VERSION_PATTERNS}))
    if stats:
        for lang in i18n.LANGS[1:]:
            problems += check_translation(lang, _read(i18n.README[lang]), readme, scenarios, prompt, stats)
    if problems:
        print("MISMATCH")
        for problem in problems:
            print(" -", problem)
        return 1
    print("check_numbers OK: 공개한 수치와 글이 원본 파일과 같습니다")
    return 0


if __name__ == "__main__":
    sys.exit(main())
