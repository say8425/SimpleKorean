#!/usr/bin/env python3
"""측정 결과를 모으고 표를 그린다. RESULTS.md, README, check_numbers.py가 같은 함수를 쓴다.

수치는 언제나 원본 출력에서 다시 계산한다. 저장된 점수 파일은 쓰지 않는다.

    python3 evals/report.py evals/results/<날짜>            # RESULTS.md를 쓰고 한국어 README 블록을 출력한다
    python3 evals/report.py evals/results/<날짜> --readme   # README 다섯 개의 벤치마크 블록도 바꾼다(readme_i18n.README)
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import ko_lint  # noqa: E402
import ko_terms  # noqa: E402
import ko_text  # noqa: E402
import metrics  # noqa: E402
import readme_i18n as i18n  # noqa: E402

REPLY_CONDS = ("baseline", "plain")
DOC_CONDS = ("baseline", "plain", "strict")
REPLY_SEP = "|---|---:|---:|---:|---:|---:|---:|---:|---:|"
DOC_SEP = "|---|---:|---:|---:|---:|---:|---:|---:|"
README_BLOCK = re.compile(r"<!-- benchmark:start (\S+) -->\n(.*?)\n<!-- benchmark:end -->", re.S)


def reply_stats(results_dir):
    """조건별 답변 합계: n, eojeol, sentences, em_dash, bold_spans, headers, bullets, fillers, visible."""
    stats = {c: Counter() for c in REPLY_CONDS}
    for path in sorted(Path(results_dir, "reply").glob("*__*__r*.txt")):
        cond = path.name.split("__")[0]
        rc = ko_lint.reader_check(path.read_text(encoding="utf-8"))
        acc = stats[cond]
        acc["n"] += 1
        acc["eojeol"] += rc["eojeol"]
        for key in ("sentences", "em_dash", "bold_spans", "headers", "bullets"):
            acc[key] += rc["counts"][key]
        acc["fillers"] += rc["counts"]["opener"] + rc["counts"]["closer"]
        acc["visible"] += rc["visible_total"]
    return {c: dict(v) for c, v in stats.items()}


def judge_stats(results_dir):
    """판정 결과: plain(SimpleKorean 승), tie, baseline(기준선 승), n."""
    tally = Counter(json.loads(p.read_text(encoding="utf-8"))["winner"]
                    for p in sorted(Path(results_dir, "judge").glob("*.json")))
    return {"plain": tally["plain"], "tie": tally["tie"], "baseline": tally["baseline"], "n": sum(tally.values())}


def doc_stats(results_dir, scenarios):
    """조건별 문서 합계. 모든 조건을 같은 기준(기본 모드 린터, 기본 단어 목록)으로 잰다."""
    types = {s["id"]: s["type"] for s in scenarios}
    concepts = ko_terms.load_terms()
    stats = {c: Counter() for c in DOC_CONDS}
    for path in sorted(Path(results_dir, "docs").glob("*.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        text, acc = record["text"], stats[record["condition"]]
        report = ko_lint.lint(text, types[record["scenario"]], config={})
        acc["n"] += 1
        acc["eojeol"] += report["eojeol"]
        acc["errors"] += report["errors_total"]
        acc["warnings"] += report["warnings_total"]
        acc["translationese"] += report["violations"].get("translationese", 0)
        acc["longest"] = max(acc["longest"], report["longest_sentence_eojeol"])
        occurrences = ko_terms.scan(ko_text.mask(ko_text.nfc(text)), concepts)
        acc["terms"] += len(occurrences)
        acc["designated"] += sum(1 for o in occurrences if o.role in ("write", "alias"))
        easy = metrics.easy_word_counts(text)
        if easy is not None:
            acc["easy"] += easy[0]
            acc["content"] += easy[1]
    return {c: dict(v) for c, v in stats.items()}


def spelling_distribution(results_dir):
    """{개념: {조건: Counter(형태)}}. 스킬이 만든 표기 변화를 따로 보기 위한 표의 재료다."""
    concepts = ko_terms.load_terms()
    dist = {}
    for path in sorted(Path(results_dir, "docs").glob("*.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        for o in ko_terms.scan(ko_text.mask(ko_text.nfc(record["text"])), concepts):
            dist.setdefault(o.concept, {}).setdefault(record["condition"], Counter())[o.form] += 1
    return dist


def _t(lang, key):
    return i18n.TEXT[lang][key]


def _pct(part, whole, lang="ko"):
    return i18n.percent(f"{100 * part / whole:.1f}", lang) if whole else _t(lang, "not_measured")


def render_reply_table(stats, lang="ko"):
    labels = _t(lang, "labels")
    lines = [_t(lang, "reply_header"), REPLY_SEP]
    for cond in REPLY_CONDS:
        s = Counter(stats[cond])
        n = max(1, s["n"])
        label = labels["reply_plain"] if cond == "plain" else labels[cond]
        lines.append(f"| {label} | {s['n']} | {s['eojeol'] / n:.0f} | {s['sentences'] / n:.1f} | "
                     f"{s['em_dash']} | {s['bold_spans']} | {s['headers']} | {s['bullets']} | {s['fillers']} |")
    return "\n".join(lines)


def render_doc_table(stats, lang="ko"):
    labels = _t(lang, "labels")
    lines = [_t(lang, "doc_header"), DOC_SEP]
    for cond in DOC_CONDS:
        s = Counter(stats[cond])
        w = max(1, s["eojeol"])
        lines.append(f"| {labels[cond]} | {s['n']} | {100 * s['errors'] / w:.2f} | {100 * s['warnings'] / w:.2f} | "
                     f"{100 * s['translationese'] / w:.2f} | {_pct(s['designated'], s['terms'], lang)} | "
                     f"{_pct(s['easy'], s['content'], lang)} | {_t(lang, 'longest').format(n=s['longest'])} |")
    return "\n".join(lines)


def render_headline(stats, judge, lang="ko"):
    base, plain = stats["baseline"].get("visible", 0), stats["plain"].get("visible", 0)
    cut = round(100 * (base - plain) / base) if base else 0
    return _t(lang, "headline").format(cut=i18n.percent(cut, lang), base=base, plain=plain, n=judge["n"],
                                       wins=judge["plain"], ties=judge["tie"], losses=judge["baseline"])


def render_spelling_table(dist):
    lines = ["| 개념 | 스킬 없음 | 기본 모드 | 엄격 모드 |", "|---|---|---|---|"]
    order = sorted(dist, key=lambda cid: (-sum(sum(c.values()) for c in dist[cid].values()), cid))
    for cid in order:
        cells = [", ".join(f"{form} {n}" for form, n in sorted(dist[cid].get(c, Counter()).items(), key=lambda x: (-x[1], x[0]))) or "0"
                 for c in DOC_CONDS]
        lines.append(f"| {cid} | " + " | ".join(cells) + " |")
    return "\n".join(lines)


def _shape(results_dir, sub, pattern):
    """원본 파일 이름에서 (과제 수, 회차 수)를 센다. 파일 이름은 <조건>__<id>__r<회차>.<확장자>다."""
    names = [p.name.rsplit(".", 1)[0].split("__") for p in Path(results_dir, sub).glob(pattern)]
    ids = {n[1] for n in names if len(n) == 3}
    runs = {n[2] for n in names if len(n) == 3}
    return len(ids), len(runs)


def benchmark_stats(results_dir, scenarios):
    """README 벤치마크 블록의 수치. 언어마다 다시 세지 않도록 한 번 센다."""
    replies = reply_stats(results_dir)
    return {
        "rel": Path(results_dir).resolve().relative_to(ROOT).as_posix(),
        "replies": replies,
        "judge": judge_stats(results_dir),
        "docs": doc_stats(results_dir, scenarios),
        "n_reply": replies["plain"].get("n", 0) + replies["baseline"].get("n", 0),
        "reply_shape": _shape(results_dir, "reply", "*.txt"),
        "doc_shape": _shape(results_dir, "docs", "*.json"),
    }


def render_readme_block(stats, lang="ko"):
    """벤치마크 블록 본문을 그 언어로 쓴다. check_numbers.py가 README와 글자 하나까지 대조한다."""
    (questions, reply_runs), (tasks, doc_runs), rel = stats["reply_shape"], stats["doc_shape"], stats["rel"]
    return "\n\n".join([
        _t(lang, "reply_intro").format(questions=questions, runs=reply_runs, total=stats["n_reply"])
        + render_headline(stats["replies"], stats["judge"], lang),
        render_reply_table(stats["replies"], lang),
        _t(lang, "doc_intro").format(tasks=tasks, runs=doc_runs),
        render_doc_table(stats["docs"], lang),
        _t(lang, "results_link").format(rel=rel, href=i18n.link(lang, f"{rel}/RESULTS.md")),
    ])


def readme_block(results_dir, scenarios, lang="ko"):
    """README 벤치마크 블록 본문. lang은 readme_i18n.LANGS 가운데 하나다."""
    return render_readme_block(benchmark_stats(results_dir, scenarios), lang)


def results_md(results_dir, scenarios):
    """RESULTS.md 전체. meta.json의 격리 확인 결과를 함께 싣는다."""
    meta = json.loads(Path(results_dir, "meta.json").read_text(encoding="utf-8"))
    iso = meta["isolation"]
    return "\n\n".join([
        f"# 측정 결과 ({meta['date']})",
        f"모델은 `{meta['model']}`, effort는 `{meta['effort']}`, 판정 모델은 `{meta['judge_model']}`입니다. "
        f"Claude Code {iso['claude_code_version']}에서 `--setting-sources \"\" --strict-mcp-config`로 실행했습니다.",
        f"격리 확인: MCP 서버 {len(iso['mcp_servers'])}개, 플러그인 {', '.join(iso['plugins']) or '없음'}, "
        f"출력 스타일 `{iso['output_style']}`, 문제 {len(meta['isolation_problems'])}건.",
        "## README 블록",
        readme_block(results_dir, scenarios),
        "## 표기 분포",
        "기본 단어 목록으로 센 개념별 표기 수입니다. 스킬이 만든 표기 변화를 사람의 관행과 따로 보려고 싣습니다.",
        "<!-- simple-korean: off -->\n" + render_spelling_table(spelling_distribution(results_dir)) + "\n<!-- simple-korean: on -->",
        "## 수치를 읽을 때 주의할 점",
        "- 린터는 정규식 검사입니다. 형태소 분석을 하지 않아 거짓 일치와 놓침이 있습니다. 모든 조건을 같은 린터로 쟀습니다.\n"
        "- 쉬운 단어 비율은 kiwipiepy 0.24.0으로 뽑은 내용어 가운데 국어 기초 어휘 1등급 표제어의 비율입니다.\n"
        "- 판정 모델도 Claude라서 같은 계열에 유리한 편향이 있을 수 있습니다.\n"
        "- 조건마다 두 번씩만 실행했습니다. 한 번 실행의 편차를 감안하세요.",
        "다시 계산하려면 `python3 evals/report.py " + Path(results_dir).resolve().relative_to(ROOT).as_posix() + "`를 실행하세요.",
    ]) + "\n"


def replace_readme_block(readme_text, results_dir, block, name="README.md"):
    """README의 벤치마크 블록을 새 결과 디렉터리와 본문으로 바꾼 새 문자열."""
    rel = Path(results_dir).resolve().relative_to(ROOT).as_posix()
    new = f"<!-- benchmark:start {rel} -->\n{block}\n<!-- benchmark:end -->"
    if not README_BLOCK.search(readme_text):
        raise SystemExit(f"{name}에 <!-- benchmark:start ... --> ... <!-- benchmark:end --> 블록이 없습니다")
    return README_BLOCK.sub(lambda m: new, readme_text, count=1)


def update_readmes(results_dir, scenarios, langs=i18n.LANGS, root=ROOT, stats=None):
    """README들의 벤치마크 블록을 바꾼다. 하나라도 읽지 못하거나 블록이 없으면 아무 파일도 바꾸지 않고 멈춘다."""
    stats = stats or benchmark_stats(results_dir, scenarios)
    texts = {}
    for lang in langs:
        name = i18n.README[lang]
        path = Path(root) / name
        try:
            current = path.read_text(encoding="utf-8")
        except OSError as err:
            raise SystemExit(f"{name}: 읽지 못했습니다({err})")
        texts[path] = replace_readme_block(current, results_dir, render_readme_block(stats, lang), name)
    for path, text in texts.items():
        path.write_text(text, encoding="utf-8")


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if not args:
        raise SystemExit("사용법: report.py <결과 디렉터리> [--readme]")
    results_dir = Path(args[0])
    scenarios = json.loads((HERE / "scenarios.json").read_text(encoding="utf-8"))
    Path(results_dir, "RESULTS.md").write_text(results_md(results_dir, scenarios), encoding="utf-8")
    stats = benchmark_stats(results_dir, scenarios)
    print(render_readme_block(stats))
    if "--readme" in args:
        update_readmes(results_dir, scenarios, stats=stats)
    return 0


if __name__ == "__main__":
    sys.exit(main())
