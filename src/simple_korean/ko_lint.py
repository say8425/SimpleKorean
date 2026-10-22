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

from . import ko_rules, ko_terms, ko_text

TEXT_TYPES = ("procedural", "descriptive")
REPLY = "reply"
SEVERITY_LABELS = {"error": "오류", "warning": "경고"}
LABELS = {
    "sentence_over_limit": "문장 길이", "trailing_condition": "뒤에 붙은 조건", "hedge": "짐작·권고",
    "will_calque": "미래형 직역", "double_passive": "이중 피동", "translationese": "번역투",
    "light_verb": "기능동사", "noun_ending": "명사형 종결", "register_mix": "문체 혼용",
    "colloquial": "구어 축약", "em_dash": "em-dash", "semicolon": "세미콜론", "latin_abbrev": "라틴 약어",
    "slop_word": "슬롭 어휘", "synonym_rotation": "한 단어 한 뜻", "spelling": "표기",
    "term_choice": "지정형 아님", "term_mix": "표기 혼용", "strict_ending": "엄격: 문장 끝",
    "strict_condition": "엄격: 조건 표현", "strict_connective": "엄격: 접속어",
    "opener": "인사말", "closer": "맺음말", "bold": "굵은 글씨", "table": "표", "lead_structure": "첫 줄의 헤더나 목록",
}
USAGE = ("사용법: ko_lint.py [--type procedural|descriptive|reply] [--strict] [--config 파일] "
         "[--gate|--gate=error|--gate=warning] (파일... | -) | --self-test\n"
         "값을 받는 옵션은 '--type=reply'처럼 써도 됩니다. '-'로 시작하는 파일 이름은 '--' 뒤에 쓰세요.")
VALUE_FLAGS = ("--type", "--config")
GATES = {"--gate": "error", "--gate=error": "error", "--gate=warning": "warning"}
BOLD = re.compile(r"\*\*[^*\n]+\*\*")
# 가운뎃점. 표준 글자 ·(U+00B7)와 흔히 대신 쓰는 ㆍ(U+318D), ・(U+30FB)를 센다.
MIDDLE_DOT = re.compile("[·ㆍ・]")
HEADER = re.compile(r"^#{1,6}\s", re.M)
# 줄 앞 공백은 [^\S\n]*로 센다. re.M에서 \s*는 빈 줄을 넘어가서, 빈 줄이 많으면 시간이 제곱으로 는다.
BULLET = re.compile(r"^[^\S\n]*([-*+]|\d+[.)])\s", re.M)
# 표의 구분 줄(|---|:-:|)을 센다. 보통 표 하나에 한 줄이다. 인용 블록 안의 표와 한 열짜리 "---|" 표는
# 세지 않는다. 모든 칸이 "-"인 데이터 행과 "--|--" 줄은 표로 센다.
TABLE_RULE = re.compile(r"^[^\S\n]*(?:\|[^\S\n]*:?-+:?[^\S\n]*(?:\|[^\S\n]*:?-+:?[^\S\n]*)*\|?"
                        r"|:?-+:?[^\S\n]*(?:\|[^\S\n]*:?-+:?[^\S\n]*)+\|?)[^\S\n]*$", re.M)
# 빈 줄을 건너뛴 첫 줄이 헤더나 목록 항목인지 본다. 네 칸 이상 들여 쓴 줄은 코드로 보고 세지 않는다.
# "요약\n---" 같은 밑줄 헤더는 놓치고, 첫 줄의 "* * *"는 목록으로 센다.
LEAD_STRUCTURE = re.compile(r"\A(?:[^\S\n]*\n)*[^\S\n]{0,3}(?:#{1,6}\s|[-*+]\s|\d+[.)]\s)")
OPENER = re.compile(  # 공백도 \W이므로 앞부분은 \W* 하나로 쓴다. \s*\W*는 같은 공백을 나눠 갖느라 느리다.
    r"^\W*(?:좋은\s?질문|훌륭한\s?질문|물론(?:입니다|이죠|이에요|요)"
    r"|네[,.!]?\s*(?:알겠습니다|좋습니다|맞습니다)"
    r"|[^.!?\n]{0,40}에\s?대해\s?(?:설명|알아보|살펴보)[^.!?\n]{0,12}겠습니다)")
# 아직 놓치는 맺음말: "주시면 … ㄹ 수 있습니다", "받으면/필요하면 … 쓰겠습니다", 문장 안 인라인 코드에 마침표가 있는 제안.
CLOSER = re.compile(
    r"도움이\s?(?:되셨|되었으면|되길|됐으면|되었기를)"
    r"|궁금한\s?(?:점|사항)이\s?(?:있으시면|있다면|있으면)|언제든(?:지)?\s?(?:물어|말씀|문의|질문)"
    r"|(?:원하시면|필요하시면|(?:[^\s.!?]{1,20}\s?)?주시면|알려\s?주세요[.!]?\s+[^.!?\n]{0,40})[^.!?\n]{0,60}"
    r"(?:겠습니다|드릴게요|할게요|드릴\s수\s있습니다)")


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


def _analyze(text, text_type, strict, config, path, formatting=True):
    """검사를 한 번 돌려 (위반 목록, 문장 단위, 설정 경고)를 돌려준다."""
    if text_type not in TEXT_TYPES + (REPLY,):
        raise ValueError(f"text_type은 {TEXT_TYPES + (REPLY,)} 가운데 하나여야 합니다: {text_type!r}")
    if not formatting and text_type != REPLY:
        raise ValueError(f"formatting=False는 text_type이 {REPLY!r}일 때만 씁니다: {text_type!r}")
    if strict and text_type == REPLY:
        raise ValueError("strict는 문서에만 씁니다. 답변은 모든 모드에서 기본 모드 규칙을 따릅니다")
    masked, units = _prepare(text)
    if text_type == REPLY:
        return _rows(reply_hits(text, formatting)), units, []
    cfg = _config(config, path)
    concepts, config_warnings = ko_terms.apply_config(ko_terms.load_terms(), cfg)
    hits = (ko_rules.lexical_hits(masked, strict=strict)
            + ko_rules.sentence_hits(units, text_type)
            + ko_rules.register_hits(units)
            + ko_terms.term_hits(masked, concepts, strict=strict, extra_skip=cfg.get("skip", ())))
    return _rows(hits), units, config_warnings


def _rows(hits):
    rows = [{"category": h.category, "severity": h.severity, "line": h.line, "text": h.text} for h in hits]
    return sorted(rows, key=lambda r: (r["line"], r["category"], r["text"]))


def lint_detail(text, text_type="descriptive", strict=False, config=None, path=None, formatting=True):
    """lint()가 세는 위반을 하나씩 돌려준다. 항목: category, severity, line, text.

    text_type이 "reply"이면 채팅 답변으로 보고 SKILL.md의 답변 규칙만 검사한다(reply_hits()). 문서 규칙(문장 길이,
    짐작 표현, 번역투, 표기)은 보지 않는다. 답변을 문서 규칙으로도 검사하려면 "descriptive"로 한 번 더 부른다.
    답변에는 config, path, strict를 쓰지 않는다. strict를 켜면 ValueError를 낸다. formatting=False는 답변의
    서식 검사(굵은 글씨, 표, 첫 줄의 헤더나 목록)를 끈다. em-dash는 문장 규칙이라 끄지 않는다.
    """
    return _analyze(text, text_type, strict, config, path, formatting)[0]


def lint(text, text_type="descriptive", strict=False, config=None, path=None, formatting=True):
    """위반 수를 범주별로 센 보고서를 돌려준다. 인자는 lint_detail()과 같다."""
    return _summary(*_analyze(text, text_type, strict, config, path, formatting), text_type, strict)


def _hit(category, text, pos, snippet):
    return ko_rules.Hit(category, ko_rules.ERROR, ko_text.line_of(text, pos), snippet)


def reply_hits(text, formatting=True):
    """답변 규칙의 위반. Stop 훅이 보는 항목과 같다.

    em-dash, 슬롭 어휘, 문체 혼용, 인사말, 맺음말을 늘 보고, formatting이 참이면 굵은 글씨, 표, 첫 줄의 헤더나
    목록도 본다. 코드 블록과 인라인 코드 안은 세지 않는다. 표는 구분 줄 하나를 표 하나로 센다.
    """
    text = ko_text.nfc(text)
    masked = ko_text.mask(text)
    hits = [_hit("em_dash", masked, m.start(), m.group(0).strip()) for m in ko_rules.DASH.finditer(masked)]
    hits += [ko_rules.Hit("slop_word", ko_rules.WARNING, ko_text.line_of(masked, m.start()), m.group(0).strip())
             for m in ko_rules.SLOP_RX.finditer(masked)]
    hits += ko_rules.register_hits(ko_text.units(text))
    hits += [_hit(category, text, m.end() - 1, m.group(0).strip())
             for category, rx in (("opener", OPENER), ("closer", CLOSER)) for m in [rx.search(text)] if m]
    if not formatting:
        return hits
    shown = ko_text.mask(text, quotes=False)
    hits += [_hit("bold", shown, m.start(), m.group(0)) for m in BOLD.finditer(shown)]
    hits += [_hit("table", shown, m.start(), m.group(0).strip()) for m in TABLE_RULE.finditer(shown)]
    lead = LEAD_STRUCTURE.match(shown)
    if lead:
        line = ko_text.line_of(shown, lead.end() - 1)
        hits.append(ko_rules.Hit("lead_structure", ko_rules.ERROR, line, text.split("\n")[line - 1].strip()))
    return hits


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

    visible_total은 답변 규칙이 막는 서식의 합이다. em-dash, 굵은 글씨, 표, 첫 줄의 헤더나 목록(lead_structure)을
    더한다. lead_structure는 코드 블록을 뺀 첫 줄이 헤더나 목록 항목이면 1이다. 답변 규칙은 답을 쓴 첫 문장
    뒤에 헤더와 목록을 두게 한다. 그 밖의 헤더와 목록 항목은 답의 내용과 길이를 보고 쓸 수 있으므로 세기만 한다.
    가운뎃점(middle_dot)도 답변 규칙이 막지 않으므로 세기만 한다. 코드 안의 가운뎃점은 세지 않는다.
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
        "middle_dot": len(MIDDLE_DOT.findall(prose)),
        "bold_spans": len(BOLD.findall(prose)),
        "headers": len(HEADER.findall(prose)),
        "bullets": len(BULLET.findall(prose)),
        "tables": len(TABLE_RULE.findall(prose)),
        "lead_structure": int(bool(LEAD_STRUCTURE.match(prose))),
        "opener": int(opener),
        "closer": int(closer),
    }
    visible = counts["em_dash"] + counts["bold_spans"] + counts["tables"] + counts["lead_structure"]
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
    dots = reader_check("읽기·쓰기ㆍ삭제를 나눕니다. `a·b`\n```\n가·나\n```\n")
    assert (dots["counts"]["middle_dot"], dots["visible_total"]) == (2, 0), dots
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
