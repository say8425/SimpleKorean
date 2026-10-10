#!/usr/bin/env python3
"""SimpleKorean 린터. 정규식으로 셀 수 있는 위반을 센다.

알려진 한계: 정규식 검사이고 형태소 분석을 하지 않는다. 거짓 일치와 놓침이 있다. 숫자는 같은
린터 버전끼리 비교하는 값이고 준수 판정이 아니다. 어떤 도구도 규칙 준수를 보장하지 못한다.

사용법:
  python3 evals/ko_lint.py --type procedural 파일.md
  cat 글.md | python3 evals/ko_lint.py -
  python3 evals/ko_lint.py --strict --gate 파일1.md 파일2.md
  python3 evals/ko_lint.py --type reply 답변.txt
  python3 evals/ko_lint.py --self-test
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ko_rules  # noqa: E402
import ko_terms  # noqa: E402
import ko_text  # noqa: E402

TEXT_TYPES = ("procedural", "descriptive")
SEVERITY_LABELS = {"error": "오류", "warning": "경고"}
LABELS = {
    "sentence_over_limit": "문장 길이", "trailing_condition": "뒤에 붙은 조건", "hedge": "짐작·권고",
    "will_calque": "미래형 직역", "double_passive": "이중 피동", "translationese": "번역투",
    "light_verb": "기능동사", "noun_ending": "명사형 종결", "register_mix": "문체 혼용",
    "colloquial": "구어 축약", "em_dash": "em-dash", "semicolon": "세미콜론", "latin_abbrev": "라틴 약어",
    "slop_word": "슬롭 어휘", "synonym_rotation": "한 단어 한 뜻", "spelling": "표기",
    "term_choice": "지정형 아님", "term_mix": "표기 혼용", "strict_ending": "엄격: 문장 끝",
    "strict_condition": "엄격: 조건 표현", "strict_connective": "엄격: 접속어",
}
USAGE = ("사용법: ko_lint.py [--type procedural|descriptive|reply] [--strict] [--config 파일] "
         "[--gate|--gate=error|--gate=warning] (파일... | -) | --self-test\n"
         "값을 받는 옵션은 '--type=reply'처럼 써도 됩니다. '-'로 시작하는 파일 이름은 '--' 뒤에 쓰세요.")
VALUE_FLAGS = ("--type", "--config")
GATES = {"--gate": "error", "--gate=error": "error", "--gate=warning": "warning"}
BOLD = re.compile(r"\*\*[^*\n]+\*\*")
HEADER = re.compile(r"^#{1,6}\s", re.M)
# 줄 앞 공백은 [^\S\n]*로 센다. re.M에서 \s*는 빈 줄을 넘어가서, 빈 줄이 많으면 시간이 제곱으로 는다.
BULLET = re.compile(r"^[^\S\n]*([-*+]|\d+[.)])\s", re.M)
OPENER = re.compile(  # 공백도 \W이므로 앞부분은 \W* 하나로 쓴다. \s*\W*는 같은 공백을 나눠 갖느라 느리다.
    r"^\W*(?:좋은\s?질문|훌륭한\s?질문|물론(?:입니다|이죠|이에요|요)"
    r"|네[,.!]?\s*(?:알겠습니다|좋습니다|맞습니다)"
    r"|[^.!?\n]{0,40}에\s?대해\s?(?:설명|알아보|살펴보)[^.!?\n]{0,12}겠습니다)")
CLOSER = re.compile(
    r"도움이\s?(?:되셨|되었으면|되길|됐으면|되었기를)"
    r"|궁금한\s?(?:점|사항)이\s?(?:있으시면|있다면|있으면)|언제든(?:지)?\s?(?:물어|말씀|문의|질문)"
    r"|(?:원하시면|필요하시면|알려\s?주시면|말씀해\s?주시면)[^.!?\n]{0,60}(?:드리겠습니다|드릴게요|드릴\s수\s있습니다)")


def _config(config, path):
    """설정 인자를 dict로 바꾼다. dict는 그대로, 경로는 읽고, 없으면 path에서 위로 찾는다."""
    if isinstance(config, dict):
        return config
    if config:
        return ko_terms.load_config(config)
    if path:
        return ko_terms.load_config(ko_terms.find_config(path))
    return {}


def _prepare(text):
    body = ko_text.strip_frontmatter(ko_text.nfc(text))
    return ko_text.mask(body), ko_text.units(body)


def _analyze(text, text_type, strict, config, path):
    """검사를 한 번 돌려 (위반 목록, 문장 단위, 설정 경고)를 돌려준다."""
    if text_type not in TEXT_TYPES:
        raise ValueError(f"text_type은 {TEXT_TYPES} 가운데 하나여야 합니다: {text_type!r}")
    masked, units = _prepare(text)
    cfg = _config(config, path)
    concepts, config_warnings = ko_terms.apply_config(ko_terms.load_terms(), cfg)
    hits = (ko_rules.lexical_hits(masked, strict=strict)
            + ko_rules.sentence_hits(units, text_type)
            + ko_rules.register_hits(units)
            + ko_terms.term_hits(masked, concepts, strict=strict, extra_skip=cfg.get("skip", ())))
    rows = [{"category": h.category, "severity": h.severity, "line": h.line, "text": h.text} for h in hits]
    return sorted(rows, key=lambda r: (r["line"], r["category"], r["text"])), units, config_warnings


def lint_detail(text, text_type="descriptive", strict=False, config=None, path=None):
    """lint()가 세는 위반을 하나씩 돌려준다. 항목: category, severity, line, text."""
    return _analyze(text, text_type, strict, config, path)[0]


def lint(text, text_type="descriptive", strict=False, config=None, path=None):
    """위반 수를 범주별로 센 보고서를 돌려준다."""
    return _summary(*_analyze(text, text_type, strict, config, path), text_type, strict)


def _summary(detail, units, config_warnings, text_type, strict):
    """위반 목록과 문장 단위로 lint() 보고서를 만든다."""
    lengths = [ko_text.eojeol_count(u.text) for u in units]
    eojeol = max(1, sum(lengths))
    errors = sum(1 for h in detail if h["severity"] == "error")
    return {
        "type": text_type,
        "strict": strict,
        "eojeol": eojeol,
        "sentences": len(units),
        "mean_sentence_eojeol": round(sum(lengths) / max(1, len(lengths)), 1),
        "longest_sentence_eojeol": max(lengths, default=0),
        "violations": dict(Counter(h["category"] for h in detail)),
        "errors_total": errors,
        "warnings_total": len(detail) - errors,
        "violations_total": len(detail),
        "violations_per_100_eojeol": round(100.0 * len(detail) / eojeol, 2),
        "config_warnings": config_warnings,
    }


def reply_fillers(text):
    """답변의 인사말과 맺음말 여부를 (opener, closer)로 돌려준다."""
    t = ko_text.nfc(text)
    return bool(OPENER.search(t)), bool(CLOSER.search(t))


def reader_check(text):
    """채팅 답변에서 독자가 보는 것을 센다.

    sentences는 목록 항목과 표 행도 문장으로 센다. 답변 규칙에는 문장 수 상한이 없으므로
    visible_total에는 넣지 않는다.
    """
    text = ko_text.nfc(text)
    prose = re.sub(r"```.*?```", " ", text, flags=re.S)
    prose = re.sub(r"`[^`\n]+`", "CODE", prose)
    no_md = re.sub(r"^[^\S\n]*(#{1,6}\s|[-*+]\s|\d+[.)]\s|\|)", "", prose, flags=re.M)
    no_md = re.sub(r"^[\s:|-]+$", "", no_md, flags=re.M)
    sents = [p for p in re.split(r"(?<=[.!?])[\"')\]”’]*\s+|\n+", no_md) if len(p.strip().split()) >= 2]
    opener, closer = reply_fillers(text)
    counts = {
        "sentences": len(sents),
        "em_dash": len(ko_rules.DASH.findall(prose)),
        "bold_spans": len(BOLD.findall(prose)),
        "headers": len(HEADER.findall(prose)),
        "bullets": len(BULLET.findall(prose)),
        "opener": int(opener),
        "closer": int(closer),
    }
    visible = counts["em_dash"] + counts["bold_spans"] + counts["headers"] + counts["bullets"]
    return {"type": "reply", "eojeol": max(1, len(no_md.split())), "counts": counts, "visible_total": visible}


SLOP_FIXTURE = """강력한 재시도 기능을 활용하여 실패한 업로드는 자동으로 다시 시도되어지며 이를 통해 데이터의 무결성이 원활하게 보장되고 있습니다 — 어떤 네트워크 장애가 발생하더라도 시스템이 안정적으로 동작하도록 설계된 이 구조에 대해 자세히 살펴보겠습니다.
자격 증명을 검증하는 것이 좋습니다; 설정을 확인할 수도 있습니다. 예를 들어 타임아웃 컨피그 등등.
배포를 진행합니다. 만약 문제가 계속되면 지원팀에 연락하세요. 이 옵션은 다음 버전에서 제거될 것입니다.
근데 메세지 형식은 바뀔 겁니다.
로그를 확인하세요(빌드가 실패한 경우).
설정 변경 필요.
이 값은 기본값이다.
오류가 나면 에러 로그를 보세요.
"""

CLEAN_FIXTURE = """sqlpipe는 실패한 업로드를 자동으로 다시 시도합니다. 이 과정은 데이터를 그대로 지킵니다.

실패가 계속되면 자격 증명이 맞는지 확인하세요. 문제가 계속되면 지원팀에 연락하세요.
"""

TABLE_FIXTURE = """| 열 A | 열 B | 열 C |
|---|---|---|
| 아주 길고 단어가 많은 첫째 칸 내용입니다 | 둘째 칸도 꽤 깁니다 | 셋째 칸 |
| 이 칸에도 내용이 더 있습니다 | 여기도 마찬가지입니다 | 그리고 여기도 |
"""

LIST_FIXTURE = """다음 항목을 쓸 수 있습니다:

- 끝에 마침표가 없는 첫째 항목
- 끝에 마침표가 없는 둘째 항목
- 끝에 마침표가 없는 셋째 항목

이어지는 본문 문장입니다.
"""

# 앞의 세 줄에 있는 대시만 논리를 잇는 대시다.
DASH_FIXTURE = """배포가 실패했습니다 — 디스크가 가득 찼습니다.
업로드가 실패했습니다 -- 토큰이 만료되었습니다.
재시도가 실패했습니다 - 포트가 닫혀 있었습니다.
운영 환경에서 --force를 쓰지 마세요.
대기 시간은 5 - 10분입니다.
범위는 5–10분이고 2024–2025 시즌에 해당합니다.
칠판에 x - y = z를 쓰세요.
`--config sqlpipe.yaml` 플래그를 쓰세요.
패널을 떼어 내세요:
   -   볼트 네 개를 푸세요.
"""

REPLY_FIXTURE = """**네** — 문제가 있습니다.

## 이유
- 랙이 늘어납니다.
- 사용자가 기다립니다.

지금 확인하세요. 그다음 늘리세요."""

TRICKY_REPLY = ('그가 "지금 멈춰."라고 했습니다. 그다음 (고장 났습니다.) 다 끝났습니다.\n\n'
                "```\n# 헤더 아님\n**굵게 아님**\n- 불릿 아님\n```\n")

EXPECTED_MIN = {
    "sentence_over_limit": 1, "trailing_condition": 1, "hedge": 2, "will_calque": 1,
    "double_passive": 1, "translationese": 4, "light_verb": 1, "noun_ending": 1, "register_mix": 1,
    "colloquial": 2, "em_dash": 1, "semicolon": 1, "latin_abbrev": 1, "slop_word": 3,
    "synonym_rotation": 1, "spelling": 1, "term_mix": 1,
}


def self_test():
    """고정 예문으로 범주마다 한 번 이상 걸리는지, 깨끗한 예문은 0인지 확인한다."""
    slop = lint(SLOP_FIXTURE, "procedural", config={})
    for category, n in EXPECTED_MIN.items():
        assert slop["violations"].get(category, 0) >= n, (category, slop["violations"])
    clean = lint(CLEAN_FIXTURE, "procedural", config={})
    assert clean["violations_total"] == 0, lint_detail(CLEAN_FIXTURE, "procedural", config={})
    assert lint(DASH_FIXTURE, "procedural", config={})["violations"].get("em_dash", 0) == 3
    assert lint(TABLE_FIXTURE, config={})["violations"].get("sentence_over_limit", 0) == 0
    assert lint(LIST_FIXTURE, config={})["violations"].get("sentence_over_limit", 0) == 0
    cell = lint("| 열 | 값 |\n|---|---|\n| 다시 시작할 수도 있습니다 | 괜찮습니다 |\n", config={})["violations"]
    assert cell.get("hedge") == 1 and cell.get("sentence_over_limit", 0) == 0, cell
    off = "<!-- simple-korean: off -->\n강력한 도구를 활용하세요 — 정말로.\n<!-- simple-korean: on -->\n로그를 읽으세요.\n"
    assert lint(off, config={})["violations_total"] == 0
    strict = "백업을 반드시 확인해야 합니다. 서버나 클라이언트를 다시 시작하세요. 실패할 경우 로그를 보세요.\n"
    assert lint(strict, config={})["violations_total"] == 0
    sv = lint(strict, strict=True, config={})["violations"]
    assert (sv.get("strict_ending"), sv.get("strict_connective"), sv.get("strict_condition")) == (1, 1, 1), sv
    r = reader_check(REPLY_FIXTURE)["counts"]
    assert (r["sentences"], r["em_dash"], r["bold_spans"], r["headers"], r["bullets"]) == (5, 1, 1, 1, 2), r
    t = reader_check(TRICKY_REPLY)["counts"]
    assert (t["sentences"], t["headers"], t["bold_spans"], t["bullets"]) == (3, 0, 0, 0), t
    detail = lint_detail(SLOP_FIXTURE, "procedural", config={})
    assert len(detail) == slop["violations_total"]
    assert Counter(h["category"] for h in detail) == Counter(slop["violations"])
    print("self-test OK:", slop["violations_total"], "violations in slop fixture, 0 in clean")


def _parse(args):
    """명령줄을 (옵션, 파일 목록)으로 나눈다. '--이름 값'과 '--이름=값'을 모두 받고 모르는 옵션은 거부한다."""
    opts = {"type": "descriptive", "config": None, "gate": None, "strict": False}
    files, rest = [], list(args)
    while rest:
        arg = rest.pop(0)
        name, eq, value = arg.partition("=")
        if arg == "--":
            files.extend(rest)
            break
        if arg in GATES:
            opts["gate"] = GATES[arg]
        elif arg == "--strict":
            opts["strict"] = True
        elif name in VALUE_FLAGS:
            if not eq and not rest:
                sys.exit(f"{name} 뒤에 값이 없습니다\n{USAGE}")
            opts[name[2:]] = value if eq else rest.pop(0)
        elif arg.startswith("-") and arg != "-":
            sys.exit(f"알 수 없는 옵션 {arg!r}\n{USAGE}")
        else:
            files.append(arg)
    return opts, files


def _read(src):
    """파일이나 표준 입력('-')을 UTF-8로 읽는다. 읽지 못하면 이름을 밝히고 끝낸다."""
    name = "표준 입력" if src == "-" else src
    try:
        if src == "-":
            return sys.stdin.buffer.read().decode("utf-8")
        return Path(src).read_text(encoding="utf-8")
    except OSError as err:
        sys.exit(str(err))
    except UnicodeDecodeError as err:
        sys.exit(f"{name}: UTF-8로 읽지 못했습니다({err.start + 1}번째 바이트). UTF-8로 저장한 뒤 다시 실행하세요.")


def _check_one(src, text_type, strict, config, gate):
    """파일 하나를 검사해 (보고서, 실패 여부)를 돌려준다."""
    text = _read(src)
    if text_type == "reply":
        report = reader_check(text)
        return {**report, "file": src}, report["visible_total"] > 0
    path = None if src == "-" else src
    detail, units, config_warnings = _analyze(text, text_type, strict, config, path)
    report = _summary(detail, units, config_warnings, text_type, strict)
    failed = report["errors_total"] > 0 or (gate == "warning" and report["warnings_total"] > 0)
    if gate:
        report = {**report, "hits": [h for h in detail if gate == "warning" or h["severity"] == "error"]}
    return {**report, "file": src}, failed


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    if "--self-test" in args:
        self_test()
        return 0
    opts, files = _parse(args)
    if opts["type"] not in TEXT_TYPES + ("reply",):
        sys.exit(f"알 수 없는 --type {opts['type']!r}\n{USAGE}")
    if not files:
        sys.exit(USAGE)
    reports, failed = [], False
    for src in files:
        try:
            report, bad = _check_one(src, opts["type"], opts["strict"], opts["config"], opts["gate"])
        except ValueError as err:
            sys.exit(f"설정 파일 오류: {err}")
        reports.append(report)
        failed = failed or bad
    print(json.dumps(reports[0] if len(reports) == 1 else reports, ensure_ascii=False, indent=2))
    return 1 if opts["gate"] and failed else 0


if __name__ == "__main__":
    sys.exit(main())
