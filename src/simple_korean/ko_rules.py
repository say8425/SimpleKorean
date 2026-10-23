"""SimpleKorean 린터의 규칙. 함수마다 Hit 목록을 돌려준다.

어휘 규칙은 ko_text.mask()로 지운 보기를 받고, 문장 규칙은 ko_text.units()의 결과를 받는다.
"""
import re
from collections import Counter, namedtuple
from pathlib import Path

from ._paths import resource
from .ko_text import JONG_RIEUL, eojeol_count, jongseong, line_of, nfc, register, sentence_kind, tail

ERROR, WARNING = "error", "warning"
Hit = namedtuple("Hit", "category severity line text")

# 받침이 ㄴ인 음절. 관형형 '-ㄴ/-은/-는'(지우는, 받은, 긴, 백업한)은 이 음절로 끝난다.
NIEUN = "".join(chr(c) for c in range(0xAC00, 0xD7A4) if (c - 0xAC00) % 28 == 4)
# '-는 것이/게 좋다'의 문장 끝. '좋은지', '좋을지', '좋다는' 같은 안긴 문장과 '좋은 방법'은 권고가 아니라 뺀다.
GOOD = r"(?:(?:더|가장|제일|훨씬)\s)?좋(?=습니다|아(?:요)?(?![가-힣])|겠|다(?![가-힣])|지\s?않)"
DASH = re.compile(r"—|(?<!\d)–(?!\d)|(?<= )--(?= )|(?<=[^\s\d]{2}) - (?=[^\s\d]{2})")

LEXICAL = (
    ("hedge", ERROR, re.compile(
        r"\s수도\s?있|것\s?같(?:습니다|다|아요|은데|아서)|[" + NIEUN + r"]\s?(?:것이|게)\s?" + GOOD
        + r"|(?:기(?:를)?|길)\s?바랍니다"
        r"|것으로\s?(?:보입니다|보인다|판단됩니다|판단된다|예상됩니다|추정됩니다)"
        r"|(?<![가-힣])아마(?:도)?(?![가-힣])")),
    ("double_passive", ERROR, re.compile(
        r"(?:되어|보여|쓰여|읽혀|잊혀|불려|닫혀|열려|나뉘어|놓여|짜여|믿겨|갇혀|담겨|쌓여|찢겨)"
        r"(?:지|진|질|집|졌|져)")),
    ("translationese", WARNING, re.compile("|".join((
        r"에\s?대(?:해|한|하여|해서)",
        r"[을를]\s?통(?:해|한|하여|해서)",
        r"에\s?의(?:해|한|하여|해서)",
        r"에\s?있어(?:서(?:는|도)?|선)?(?![가-힣])(?!\s*안\s?[되돼됐됩된])",
        r"[을를]\s?가지고\s?있",
        r"(?:으로|로)\s?인(?:해|한|하여|해서)",
        r"하는\s?것이\s?가능|것이\s?가능합니다",
        r"[이가]\s?요구(?:됩|된|되)",
        r"할\s?필요가\s?있",
        r"에\s?위치(?:한|해|하)",
        r"(?<![가-힣])만(?:약|일)(?:에)?(?![가-힣])(?!\s*대비)",
        r"고\s?있(?:습니다|다)(?![가-힣])",
        r"(?:으로|로)부터",
    )))),
    ("light_verb", WARNING, re.compile(r"(?:진행|수행|실시)(?:하|합|했|해|한|할|함|됩|된|되|될|됨)")),
    ("colloquial", WARNING, re.compile(
        r"(?<![가-힣])(?:근데|그치만|걍|거예요|거에요|건데|거죠)(?![가-힣])")),
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
# 나열의 '(이)나' 뒤에는 명사가 온다. 보조 용언이 바로 오면 '어긋나 있다' 같은 '-나다' 동사다.
NA_AUX = ("있", "버리", "버렸", "버린", "버려", "버립")
CHECK_VERB = re.compile(r"(?<![가-힣])(확인|검증|점검|체크|검사)(?=하|합|했|해|한|할|됩|된|되|될)")
CONFIG_NOUN = re.compile(r"(?<![가-힣])(설정\s?파일|구성\s?파일|컨피그(?:\s?파일)?|컨피규레이션)")
SLOP_CORE = ("원활", "효율적", "강력한", "혁신적", "획기적", "손쉽게", "간편하게", "매끄럽게", "포괄적",
             "견고한", "극대화", "시너지", "패러다임", "결론적으로", "요약하자면", "정리하자면",
             "살펴보겠습니다", "알아보겠습니다")
SLOP_TSV = resource("data/slop.tsv", "evals/slop.tsv")


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


# '겁니다'는 '것입니다'의 준말이다('멈춘 겁니다', '할 겁니다', '있을 겁니다', '어제 겁니다', 'API 겁니다').
# 앞 어절이 '걸다'의 목적어나 부사어이면 '걸다'의 활용이라 뺀다('제약을 겁니다', '제한도 겁니다', '벽에 겁니다').
# 조사 '을/를/은/는'은 관형형 어미 '-을/-를/-은/-는'과 모양이 같다. 그래서 이 조사 앞이 '걸다'와 함께 쓰는 명사일
# 때만 뺀다. 아직 잘못 잡는 꼴: 목록에 없는 명사 뒤의 '걸다'('가드를 겁니다'), 부사 뒤의 '걸다'('다시 겁니다').
GEOP = re.compile(r"(?<![가-힣])겁니다(?![가-힣])")
EOJEOL_BEFORE = re.compile(r"(\S{1,40})\s+$")
HANGUL_TAIL = re.compile(r"[가-힣]+$")
GEOLDA_OBJECTS = ("제약", "락", "잠금", "조건", "필터", "제한", "트리거", "인덱스", "훅", "링크", "타임아웃", "키",
                  "브레이크포인트", "중단점", "알람", "전화", "말", "기대", "희망", "목숨", "시동", "돈", "내기",
                  "브레이크", "제동", "태클", "시비", "최면", "주문", "마법", "빗장", "자물쇠", "그림", "액자",
                  "간판", "현수막", "커튼", "깃발", "옷", "모자")
GEOLDA_PARTICLES = ("도", "만", "에", "에서", "에는", "에서는", "로", "로는", "까지", "부터", "마저", "조차")
CASE_PARTICLES = ("을", "를", "은", "는")
CONTRACTED_OBJECTS = frozenset({"이걸", "그걸", "저걸", "요걸", "뭘"})


def _geolda(word):
    """'겁니다' 앞 어절(한글 부분)이 '걸다'의 목적어나 부사어이면 참이다."""
    if word in CONTRACTED_OBJECTS or word in CASE_PARTICLES or word.endswith(GEOLDA_PARTICLES):
        return True
    return word.endswith(CASE_PARTICLES) and word[:-1].endswith(GEOLDA_OBJECTS)


def geop_hits(masked):
    """구어 축약 '겁니다'(것입니다). '걸다'의 활용인 '겁니다'는 뺀다. 앞 어절은 40자까지만 본다."""
    hits = []
    for m in GEOP.finditer(masked):
        before = EOJEOL_BEFORE.search(masked, max(0, m.start() - 64), m.start())
        word = HANGUL_TAIL.search(before.group(1)) if before else None
        if not (word and _geolda(word.group(0))):
            hits.append(Hit("colloquial", WARNING, line_of(masked, m.start()), "겁니다"))
    return hits


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
        if word in NA_STOP or word.endswith("거나") or masked.startswith(NA_AUX, m.end()):
            continue
        hits.append(Hit("strict_connective", WARNING, line_of(masked, m.start()), word))
    return hits


def lexical_hits(masked, strict=False, slop_rx=None):
    """어휘 규칙을 모두 돌린다. masked는 ko_text.mask()의 결과다."""
    hits = []
    for category, severity, rx in LEXICAL:
        hits += _hits_from(rx, masked, category, severity)
    hits += will_calque_hits(masked)
    hits += geop_hits(masked)
    hits += _hits_from(slop_rx or SLOP_RX, masked, "slop_word", WARNING)
    hits += rotation_hits(masked)
    if strict:
        for category, severity, rx in STRICT_LEXICAL:
            hits += _hits_from(rx, masked, category, severity)
        hits += condition_hits(masked) + connective_hits(masked)
    return hits


LIMITS = {"procedural": 15, "descriptive": 20}
TRAIL_PROVISO = re.compile(r"^(?:단|다만),\s")
TRAIL_PAREN = re.compile(r"(?:세요|십시오|시오)\s*\([^()]*(?:경우|때|면|시)\)\s*[.!]?$")
NOUN_END = re.compile(r"(?:함|음|임|됨|필요|예정|가능|불가|완료|요망|바람|것)$")
STYLES = (
    frozenset({"hapsyo", "haeyo_imp"}),
    frozenset({"hapsyo", "hapsyo_imp"}),
    frozenset({"haera"}),
    frozenset({"haeyo", "haeyo_imp"}),
)


def _snippet(text, limit=80):
    return text if len(text) <= limit else text[:limit] + "…"


def sentence_hits(units, text_type="descriptive", limits=None):
    """문장 단위 규칙: 길이, 뒤에 붙은 조건, 명사형 종결."""
    limits = limits or LIMITS
    hits = []
    for u in units:
        kind = sentence_kind(u.text) or text_type
        n = eojeol_count(u.text)
        if n > limits[kind]:
            hits.append(Hit("sentence_over_limit", WARNING, u.line, f"{n}어절: {_snippet(u.text)}"))
        if TRAIL_PROVISO.match(u.text) or TRAIL_PAREN.search(u.text):
            hits.append(Hit("trailing_condition", WARNING, u.line, _snippet(u.text)))
        if u.kind == "prose" and NOUN_END.search(tail(u.text)):
            hits.append(Hit("noun_ending", WARNING, u.line, _snippet(u.text)))
    return hits


def register_hits(units):
    """문체 혼용. 허용 조합 가운데 가장 많은 문장을 덮는 조합을 고르고, 거기서 벗어난 문장을 잡는다."""
    found = [(u, register(u.text)) for u in units]
    found = [(u, r) for u, r in found if r]
    if not found:
        return []
    counts = Counter(r for _, r in found)
    best = max(STYLES, key=lambda style: sum(counts[r] for r in style))
    return [Hit("register_mix", WARNING, u.line, _snippet(u.text)) for u, r in found if r not in best]
