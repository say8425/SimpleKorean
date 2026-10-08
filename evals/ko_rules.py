"""SimpleKorean 린터의 규칙. 함수마다 Hit 목록을 돌려준다.

어휘 규칙은 ko_text.mask()로 지운 보기를 받고, 문장 규칙은 ko_text.units()의 결과를 받는다.
"""
import re
from collections import Counter, namedtuple
from pathlib import Path

from ko_text import JONG_RIEUL, eojeol_count, jongseong, line_of, nfc, register, sentence_kind, tail

ERROR, WARNING = "error", "warning"
Hit = namedtuple("Hit", "category severity line text")

DASH = re.compile(r"—|(?<!\d)–(?!\d)|(?<= )--(?= )|(?<=[^\s\d]{2}) - (?=[^\s\d]{2})")

LEXICAL = (
    ("hedge", ERROR, re.compile(
        r"\s수도\s?있|것\s?같(?:습니다|다|아요|은데|아서)|[는은]\s?것이\s?좋|기(?:를)?\s?바랍니다"
        r"|것으로\s?(?:보입니다|보인다|판단됩니다|판단된다|예상됩니다|추정됩니다)"
        r"|(?<![가-힣])아마(?:도)?(?![가-힣])")),
    ("double_passive", ERROR, re.compile(
        r"(?:되어|보여|쓰여|읽혀|잊혀|불려|닫혀|열려|나뉘어|놓여|짜여|믿겨|갇혀|담겨|쌓여|찢겨)"
        r"(?:지|진|질|집|졌|져)")),
    ("translationese", WARNING, re.compile("|".join((
        r"에\s?대(?:해|한|하여|해서)",
        r"[을를]\s?통(?:해|한|하여|해서)",
        r"에\s?의(?:해|한|하여|해서)",
        r"에\s?있어(?:서)?(?![가-힣])",
        r"[을를]\s?가지고\s?있",
        r"(?:으로|로)\s?인(?:해|한|하여|해서)",
        r"하는\s?것이\s?가능|것이\s?가능합니다",
        r"[이가]\s?요구(?:됩|된|되)",
        r"할\s?필요가\s?있",
        r"에\s?위치(?:한|해|하)",
        r"(?<![가-힣])만(?:약|일)(?![가-힣])",
        r"고\s?있(?:습니다|다)(?![가-힣])",
        r"(?:으로|로)부터",
    )))),
    ("light_verb", WARNING, re.compile(r"(?:진행|수행|실시)(?:하|합|했|해|한|할|함|됩|된|되|될|됨)")),
    ("colloquial", WARNING, re.compile(
        r"(?<![가-힣])(?:근데|그치만|걍|겁니다|거예요|거에요|건데|거죠)(?![가-힣])")),
    ("latin_abbrev", WARNING, re.compile(
        r"\b(?:e\.g\.|i\.e\.|etc\.?)(?=[\s,)]|$)|(?<![가-힣])(?:기타\s?)?등등", re.I)),
    ("em_dash", ERROR, DASH),
    ("semicolon", ERROR, re.compile(r";")),
    ("slop_word", WARNING, re.compile(r"(?:단순히|단지)\s[^.!?\n]{0,40}?아니라")),
)
STRICT_LEXICAL = (
    ("strict_ending", WARNING, re.compile(r"(?<![가-힣])반드시(?![가-힣])")),
    ("strict_ending", WARNING, re.compile(r"[는은]\s?편이\s?(?:좋|낫)|(?:하여야|해야)\s?할\s?것")),
)
WILL = re.compile(r"(\S)\s것(?:입니다|이다|이며|이고|이니)")
COND = re.compile(r"(\S)\s경우(?=에|,|\s|$)")
NA_LIST = re.compile(r"(?<![가-힣A-Za-z0-9])([가-힣A-Za-z0-9]+?)(이나|나)\s(?=[가-힣A-Za-z0-9])")
NA_STOP = frozenset({"하나", "그러나", "아무나", "누구나", "언제나", "어디나", "무엇이나", "뭐나"})
CHECK_VERB = re.compile(r"(?<![가-힣])(확인|검증|점검|체크|검사)(?=하|합|했|해|한|할|됩|된|되|될)")
CONFIG_NOUN = re.compile(r"(?<![가-힣])(설정\s?파일|구성\s?파일|컨피그(?:\s?파일)?|컨피규레이션)")
SLOP_CORE = ("원활", "효율적", "강력한", "혁신적", "획기적", "손쉽게", "간편하게", "매끄럽게", "포괄적",
             "견고한", "극대화", "시너지", "패러다임", "결론적으로", "요약하자면", "정리하자면",
             "살펴보겠습니다", "알아보겠습니다")
SLOP_TSV = Path(__file__).resolve().parent / "slop.tsv"


def load_slop_terms(path=SLOP_TSV):
    """slop.tsv의 첫 열과 핵심 목록을 합친다. 긴 말부터 정렬한다. '#'으로 시작하는 줄은 주석이다."""
    terms = set(SLOP_CORE)
    p = Path(path)
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            term = nfc(line.split("\t")[0].strip())
            if term and not term.startswith("#"):
                terms.add(term)
    return sorted(terms, key=lambda t: (-len(t), t))


def slop_pattern(terms):
    """어절 앞에서 맞추는 슬롭 정규식. 뒤에 붙는 조사와 어미는 허용한다."""
    alts = (r"\s+".join(re.escape(part) for part in t.split()) for t in terms)
    return re.compile(r"(?<![가-힣])(?:" + "|".join(alts) + ")")


SLOP_RX = slop_pattern(load_slop_terms())


def _hits_from(rx, masked, category, severity):
    return [Hit(category, severity, line_of(masked, m.start()), m.group(0).strip())
            for m in rx.finditer(masked)]


def will_calque_hits(masked):
    """'-ㄹ 것입니다' 꼴. ' 것' 앞 음절의 받침이 ㄹ일 때만 잡는다."""
    return [Hit("will_calque", ERROR, line_of(masked, m.start()), m.group(0).strip())
            for m in WILL.finditer(masked) if jongseong(m.group(1)) == JONG_RIEUL]


def rotation_hits(masked):
    """한 단어 한 뜻. 지정한 말(확인, 설정)이 있으면 그 말을, 없으면 처음 나온 말을 기준으로 다른 말을 잡는다."""
    hits = []
    for base_name, rx in (("확인", CHECK_VERB), ("설정", CONFIG_NOUN)):
        first_by_stem = {}
        for m in rx.finditer(masked):
            first_by_stem.setdefault(re.sub(r"\s|파일", "", m.group(1)), m)
        if not first_by_stem:
            continue
        base = base_name if base_name in first_by_stem else next(iter(first_by_stem))
        hits.extend(Hit("synonym_rotation", WARNING, line_of(masked, m.start()), f"{m.group(1)} ({base_name})")
                    for stem, m in first_by_stem.items() if stem != base)
    return hits


def condition_hits(masked):
    """엄격 모드: '-ㄹ 경우', '-는 경우' 같은 조건 표현."""
    return [Hit("strict_condition", WARNING, line_of(masked, m.start()), m.group(0).strip())
            for m in COND.finditer(masked)
            if m.group(1) in "는은한인된" or jongseong(m.group(1)) == JONG_RIEUL]


def connective_hits(masked):
    """엄격 모드: '(이)나'로 잇는 나열."""
    hits = []
    for m in NA_LIST.finditer(masked):
        word = m.group(1) + m.group(2)
        if word in NA_STOP or word.endswith("거나"):
            continue
        hits.append(Hit("strict_connective", WARNING, line_of(masked, m.start()), word))
    return hits


def lexical_hits(masked, strict=False, slop_rx=None):
    """어휘 규칙을 모두 돌린다. masked는 ko_text.mask()의 결과다."""
    hits = []
    for category, severity, rx in LEXICAL:
        hits += _hits_from(rx, masked, category, severity)
    hits += will_calque_hits(masked)
    hits += _hits_from(slop_rx or SLOP_RX, masked, "slop_word", WARNING)
    hits += rotation_hits(masked)
    if strict:
        for category, severity, rx in STRICT_LEXICAL:
            hits += _hits_from(rx, masked, category, severity)
        hits += condition_hits(masked) + connective_hits(masked)
    return hits
