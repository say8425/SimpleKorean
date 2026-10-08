#!/usr/bin/env python3
"""압력 시험 실행기. evals/pressure-tests.md의 시나리오를 스킬 없이 한 번, 플러그인을 켜고 한 번 돌린다.

플러그인 조건은 이 레포지토리를 --plugin-dir로 올려 세션 시작 훅과 스킬을 실제로 쓴다. 스킬 파일을
읽는 Read와 Skill만 허용하고, 디렉터리를 뒤질 수 있는 Glob과 Grep은 막는다. 기준선은 파일 도구를 모두
막는다. 도구를 열어 둔 기준선이 디스크에서 이 레포지토리의 규칙 목록을 찾아 읽은 적이 있다(2026-10-08).
이미 있는 출력은 건너뛴다.

    python3 evals/run_pressure.py --out evals/results/<날짜>/pressure [--round 1] [--only 2,6] [--conditions plugin]
    python3 evals/run_pressure.py --out evals/results/<날짜>/pressure --check   # 기계로 셀 기준만 센다
"""
import argparse
import re
import sys
import time
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bench_common as bc  # noqa: E402
import ko_lint  # noqa: E402
import ko_text  # noqa: E402

TESTS_MD = bc.HERE / "pressure-tests.md"
CONDITIONS = ("baseline", "plugin")
PLUGIN_ALLOWED = "Read,Skill"
PLUGIN_DENIED = "Bash,Glob,Grep,Write,Edit,WebFetch,WebSearch,NotebookEdit"
BASELINE_DENIED = "Bash,Read,Glob,Grep,Skill,Write,Edit,WebFetch,WebSearch,NotebookEdit"
HEADING = re.compile(r"^## 시나리오 (\d+): (.+)$")
LINT_CHECKS = {
    1: ("procedural", False, ("sentence_over_limit", "hedge", "synonym_rotation", "trailing_condition")),
    3: ("procedural", False, ("noun_ending",)),
    8: ("descriptive", True, ("strict_ending", "strict_condition", "strict_connective", "hedge", "will_calque")),
}
STYLE_CHECKS = {6: ("haera",), 7: ("haeyo", "haeyo_imp")}


def parse_scenarios(markdown):
    """'## 시나리오 N: 제목' 아래 첫 인용 블록을 프롬프트로 읽는다."""
    scenarios = []
    for block in re.split(r"(?m)^(?=## 시나리오 \d+: )", markdown):
        m = HEADING.match(block.split("\n", 1)[0])
        if not m:
            continue
        quote = re.search(r"(?m)^>.*(?:\n>.*)*", block)
        if not quote:
            raise SystemExit(f"시나리오 {m.group(1)}에 인용 블록 프롬프트가 없습니다")
        prompt = "\n".join(re.sub(r"^> ?", "", line) for line in quote.group(0).split("\n")).strip()
        scenarios.append({"n": int(m.group(1)), "title": m.group(2).strip(), "prompt": prompt})
    return scenarios


def pressure_cmd(prompt, plugin_dir=None):
    """압력 시험용 claude 명령. 설정과 MCP 서버는 읽지 않는다. 기준선은 파일 도구 없이 돈다."""
    cmd = ["claude", "-p", prompt, "--model", bc.MODEL, "--effort", bc.EFFORT,
           "--setting-sources", "", "--strict-mcp-config", "--output-format", "json"]
    if not plugin_dir:
        return cmd + ["--disallowedTools", BASELINE_DENIED]
    return cmd + ["--allowedTools", PLUGIN_ALLOWED, "--disallowedTools", PLUGIN_DENIED, "--plugin-dir", str(plugin_dir)]


def generate(out, scenarios, round_no=1, call=bc.call_claude, sleep=2.0, conditions=CONDITIONS, plugin_dir=bc.ROOT):
    """시나리오 × 조건의 출력을 out/<조건>__p<번호>__r<회차>.txt로 쓴다. 있는 파일은 건너뛴다."""
    Path(out).mkdir(parents=True, exist_ok=True)
    for sc in scenarios:
        for cond in conditions:
            path = Path(out) / f"{cond}__p{sc['n']}__r{round_no}.txt"
            if path.exists() and path.read_text(encoding="utf-8").strip():
                continue
            print(f"{cond} 시나리오 {sc['n']} r{round_no}", flush=True)
            try:
                res = call(sc["prompt"], cmd=pressure_cmd(sc["prompt"], plugin_dir if cond == "plugin" else None))
            except Exception as err:  # noqa: BLE001  하나가 실패해도 나머지는 돈다
                print(f"  실패: {err}", flush=True)
                continue
            path.write_text(res["text"], encoding="utf-8")
            time.sleep(sleep)


def machine_report(n, text):
    """시나리오 n에서 기계로 셀 수 있는 값. 셀 기준이 없는 시나리오는 빈 dict다."""
    report = {}
    if n in LINT_CHECKS:
        kind, strict, categories = LINT_CHECKS[n]
        found = Counter(h["category"] for h in ko_lint.lint_detail(text, kind, strict=strict, config={}))
        report.update({c: found[c] for c in categories})
    if n in STYLE_CHECKS:
        styles = Counter(r for r in (ko_text.register(u.text) for u in ko_text.units(text)) if r)
        wanted = sum(styles[s] for s in STYLE_CHECKS[n])
        report.update({"요청한 문체 문장": wanted, "다른 문체 문장": sum(styles.values()) - wanted})
    if n == 7:
        report["visible_total"] = ko_lint.reader_check(text)["visible_total"]
    if n == 9:
        report["한글 비율"] = round(ko_text.hangul_ratio(text), 2)
    return report


def check_lines(out):
    """출력 파일마다 기계 확인 값을 한 줄로 만든다."""
    lines = []
    for path in sorted(Path(out).glob("*__p*__r*.txt")):
        n = int(re.search(r"__p(\d+)__", path.name).group(1))
        values = machine_report(n, path.read_text(encoding="utf-8"))
        lines.append(f"{path.name}: " + (", ".join(f"{k}={v}" for k, v in values.items()) or "읽고 판정"))
    return lines


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--round", type=int, default=1)
    ap.add_argument("--only", default="", help="쉼표로 나눈 시나리오 번호")
    ap.add_argument("--conditions", default=",".join(CONDITIONS), help="쉼표로 나눈 조건 목록")
    ap.add_argument("--check", action="store_true", help="저장된 출력의 기계 확인 값만 출력한다")
    a = ap.parse_args(argv)
    if a.check:
        print("\n".join(check_lines(a.out)))
        return 0
    conditions = bc.parse_conditions(a.conditions, CONDITIONS)
    scenarios = parse_scenarios(TESTS_MD.read_text(encoding="utf-8"))
    if a.only:
        wanted = {int(x) for x in a.only.split(",") if x.strip()}
        scenarios = [s for s in scenarios if s["n"] in wanted]
    generate(a.out, scenarios, a.round, conditions=conditions)
    return 0


if __name__ == "__main__":
    sys.exit(main())
