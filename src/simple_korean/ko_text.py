"""SimpleKorean 린터가 쓰는 한국어 텍스트 도구.

표준 라이브러리만 쓰고 Python 3.9 이상에서 돈다. 함수는 입력을 바꾸지 않고 새 값을 돌려준다.
"""
import re
import unicodedata
from bisect import bisect_left, bisect_right
from collections import namedtuple
from functools import lru_cache

HANGUL_FIRST = 0xAC00
HANGUL_LAST = 0xD7A3
JONG_RIEUL = 8  # 받침 28종 가운데 ㄹ의 번호. 0은 받침 없음이다.
JONG_BIEUP = 17  # 받침 ㅂ의 번호. 합쇼체 어미 "-ㅂ니다", "-ㅂ니까"는 '니' 앞 음절에 이 받침이 있다.

OFF_REGION = re.compile(
    r"<!--\s*simple-korean:\s*off\s*-->.*?(?:<!--\s*simple-korean:\s*on\s*-->|\Z)", re.S)
# 여는 줄의 백틱이나 물결은 끝까지 한 번에 잡는다((?!`)). 짧게 다시 잡아 보면 결과는 같고,
# 줄바꿈 없이 끝나는 긴 백틱 줄에서 시간만 제곱으로 는다.
FENCE = re.compile(r"^[ \t]*(`{3,}(?!`)|~{3,}(?!~))[^\n]*\n.*?(?:^[ \t]*\1[ \t]*$|\Z)", re.S | re.M)
INLINE_CODE = re.compile(r"`[^`\n]+`")
# URL 바로 뒤의 굵은 글씨 표시(**)와 대시는 URL이 아니다. 한글은 IRI의 일부일 수 있어 그대로 둔다.
URL = re.compile(r"https?://[^\s)>\]*—–]+")
ENTITY = re.compile(r"&(?:[A-Za-z][A-Za-z0-9]{1,31}|#[0-9]{1,7}|#[xX][0-9A-Fa-f]{1,6});")
QUOTES = (
    re.compile(r'"[^"\n]{1,200}"'),
    re.compile(r"“[^”\n]{1,200}”"),
    re.compile(r"‘[^’\n]{1,200}’"),
    re.compile(r"「[^」\n]{1,200}」"),
    re.compile(r"『[^』\n]{1,200}』"),
    re.compile(r"(?<![A-Za-z])'[^'\n]{1,80}'(?![A-Za-z])"),
)
FRONTMATTER = re.compile(r"\A---[ \t]*\n.*?\n---[ \t]*(?=\n|\Z)", re.S)


def nfc(text):
    """유니코드 NFC로 정규화하고, 맨 앞의 BOM을 떼고, CRLF와 CR을 LF로 바꾼다."""
    t = unicodedata.normalize("NFC", text)
    t = t[1:] if t.startswith("﻿") else t
    return t.replace("\r\n", "\n").replace("\r", "\n")


def is_hangul(ch):
    """한 글자가 한글 음절(가~힣)이면 참이다."""
    return len(ch) == 1 and HANGUL_FIRST <= ord(ch) <= HANGUL_LAST


def jongseong(ch):
    """한글 음절의 받침 번호. 받침이 없으면 0, ㄹ이면 8, 한글 음절이 아니면 -1이다."""
    if not is_hangul(ch):
        return -1
    return (ord(ch) - HANGUL_FIRST) % 28


def _blank(match):
    """찾은 부분을 같은 길이의 공백으로 바꾼다. 줄바꿈은 남겨 줄 번호를 지킨다."""
    return re.sub(r"[^\n]", " ", match.group(0))


def _blank_comments(text):
    """닫힌 HTML 주석을 같은 길이의 공백으로 지운다. 닫히지 않은 '<!--'는 그대로 둔다.

    정규식 '<!--.*?-->'와 결과가 같다. 정규식은 닫히지 않은 '<!--'마다 글 끝까지 다시 훑어서
    '<!--'가 많으면 시간이 제곱으로 늘어난다. 여기서는 '-->'가 더 없으면 바로 멈춘다.
    """
    parts, pos = [], 0
    while True:
        start = text.find("<!--", pos)
        end = text.find("-->", start + 4) if start >= 0 else -1
        if end < 0:
            break
        parts.append(text[pos:start])
        parts.append(re.sub(r"[^\n]", " ", text[start:end + 3]))
        pos = end + 3
    parts.append(text[pos:])
    return "".join(parts)


def strip_frontmatter(text):
    """맨 앞의 YAML frontmatter를 공백으로 지운다. 줄 수는 그대로다."""
    return FRONTMATTER.sub(_blank, text, count=1)


def mask(text, quotes=True):
    """어휘 검사용 보기를 만든다.

    꺼짐 구역, 코드 블록, HTML 주석, 인라인 코드, URL, HTML 엔티티(&nbsp; 같은 것)를 지운다.
    quotes가 참이면 따옴표 인용도 지운다. 지운 자리는 같은 길이의 공백이라 위치와 줄 번호가
    원문과 같다.
    """
    t = OFF_REGION.sub(_blank, text)
    t = FENCE.sub(_blank, t)
    t = _blank_comments(t)
    t = INLINE_CODE.sub(_blank, t)
    t = URL.sub(_blank, t)
    t = ENTITY.sub(_blank, t)
    if quotes:
        for rx in QUOTES:
            t = rx.sub(_blank, t)
    return t


@lru_cache(maxsize=8)
def _newlines(text):
    """줄바꿈 위치의 튜플. 같은 글에 여러 번 물어도 한 번만 센다."""
    return tuple(m.start() for m in re.finditer("\n", text))


def line_of(text, pos):
    """위치 pos가 있는 줄 번호(1부터)."""
    return bisect_left(_newlines(text), pos) + 1


def hangul_ratio(text):
    """코드와 URL을 뺀 글자 가운데 한글 음절의 비율. 분모는 한글 음절 수와 라틴 문자 수의 합이다."""
    body = mask(nfc(text), quotes=False)
    hangul = sum(1 for c in body if is_hangul(c))
    latin = sum(1 for c in body if c.isascii() and c.isalpha())
    total = hangul + latin
    return hangul / total if total else 0.0


Unit = namedtuple("Unit", "text line kind")  # kind: prose, list, table

HEADING = re.compile(r"^\s{0,3}#{1,6}\s")
LIST_ITEM = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+(.*)$")
TABLE_ROW = re.compile(r"^\s*\|(.*)\|\s*$")
TABLE_SEP = re.compile(r"^\s*\|[\s:|-]+\|\s*$")
BLOCKQUOTE = re.compile(r"^\s*(?:>\s?)+")
SPLIT = re.compile(r"(?<=[.!?])([\"'”’)\]]*)\s+")
PAREN = re.compile(r"\([^()\n]*\)")
# 숫자 덩어리([\d,.]의 연속)의 맨 앞에서만 맞추기 시작한다. 덩어리 가운데에서 다시 시작하면
# 결과는 같고 시간만 제곱으로 는다. 앞에 붙은 쉼표와 마침표(".5")는 첫째 묶음에 담아 그대로 둔다.
NUM_UNIT = re.compile(
    r"(?<![\d,.])([,.]*)(\d[\d,.]*)\s+(%|[A-Za-z]{1,5}|초|분|시간|일|주|개월|년|개|건|회|번|명|배|원|자|줄|행|쪽|장|단계)"
    r"(?=[\s.,!?)]|$|[가-힣])")
PROC_ENDINGS = ("세요", "십시오", "시오", "하라", "하자")
NOUN_YO = ("필요", "중요", "주요", "개요", "소요", "수요", "강요", "동요")
# '요' 앞 음절이 이 모음으로 끝나는 열린 음절이면 해요체 어미다(해요, 바꿔요, 할게요, 지요).
YO_VOWELS = frozenset({0, 1, 4, 5, 6, 7, 8, 9, 10, 14, 15, 20})  # ㅏㅐㅓㅔㅕㅖㅗㅘㅙㅝㅞㅣ
YO_CLOSED = ("든요", "군요", "걸요")
HAERA_RA = ("하라", "말라", "으라", "보라", "두라", "쓰라")
TRAIL_GROUP = re.compile(r"(?<=[^\s(])\s*\([^()]*\)$")


def tail(sentence):
    """문장 끝의 부호, 닫는 따옴표, 맨 끝의 괄호 하나를 뗀 문자열. 문장 전체가 괄호이면 괄호는 둔다."""
    t = TRAIL_GROUP.sub("", sentence.rstrip(" \t.!?:;\"'”’"))
    return t.rstrip(" \t.!?:;\"'”’)]")


def _haeyo(t):
    """'요'로 끝나는 말이 해요체 어미인지 가린다. '소요', '필요' 같은 명사는 아니다."""
    if not t.endswith("요") or t.endswith(NOUN_YO) or len(t) < 2:
        return False
    if t.endswith(YO_CLOSED):
        return True
    before = t[-2]
    return is_hangul(before) and jongseong(before) == 0 and (ord(before) - 0xAC00) // 28 % 21 in YO_VOWELS


def split_sentences(text):
    """문장 끝 부호 뒤의 공백에서 나눈다. (문장, 시작 위치) 목록을 돌려준다."""
    out, pos = [], 0
    for m in SPLIT.finditer(text):
        end = m.start() + len(m.group(1))
        piece = text[pos:end].strip()
        if piece:
            out.append((piece, pos))
        pos = m.end()
    rest = text[pos:].strip()
    if rest:
        out.append((rest, pos))
    return out


def _counting_line(line):
    """세는 보기 한 줄. 인라인 코드, URL, 인용은 앞 어절에 붙는 한 덩어리로 바꾼다."""
    line = INLINE_CODE.sub("CODE", line)
    line = URL.sub("URL", line)
    for rx in QUOTES:
        line = rx.sub("QUOTE", line)
    return line


def _paragraph_units(para):
    """모은 본문 줄 (줄 번호, 내용)을 이어 문장 단위로 나눈다."""
    if not para:
        return []
    joined, starts = "", []
    for _, line in para:
        if joined:
            joined += " "
        starts.append(len(joined))
        joined += line.strip()
    numbers = [number for number, _ in para]
    return [Unit(sent, numbers[bisect_right(starts, offset) - 1], "prose")
            for sent, offset in split_sentences(joined)]


def units(text):
    """문장 단위 목록을 만든다.

    코드 블록, HTML 주석, 꺼짐 구역, 제목, 표 구분 줄은 건너뛴다. 표 칸과 목록 항목은 각각
    나누고, 본문은 문단으로 이은 뒤 문장으로 나눈다. 어절이 둘 미만인 조각은 뺀다.
    지역 목록만 고치고 입력은 바꾸지 않는다.
    """
    base = _blank_comments(FENCE.sub(_blank, OFF_REGION.sub(_blank, nfc(text))))
    found, para = [], []
    for number, raw in enumerate(base.split("\n"), 1):
        line = _counting_line(BLOCKQUOTE.sub("", raw))
        if not line.strip() or HEADING.match(line) or TABLE_SEP.match(line):
            found.extend(_paragraph_units(para))
            para = []
            continue
        row, item = TABLE_ROW.match(line), LIST_ITEM.match(line)
        if row or item:
            found.extend(_paragraph_units(para))
            para = []
            pieces = row.group(1).split("|") if row else [item.group(1)]
            kind = "table" if row else "list"
            found.extend(Unit(sent, number, kind)
                         for piece in pieces for sent, _ in split_sentences(piece.strip()))
            continue
        para.append((number, line))
    found.extend(_paragraph_units(para))
    return [u for u in found if len(u.text.split()) >= 2]


def eojeol_count(sentence):
    """어절 수를 센다. 괄호 안의 글은 앞 어절에 붙이고, 숫자와 단위는 한 어절로 친다."""
    s = PAREN.sub("", PAREN.sub("", sentence))
    s = NUM_UNIT.sub(r"\1\2\3", s)
    return len(s.split())


def sentence_kind(sentence):
    """명령형 어미로 끝나면 procedural, 평서·의문 어미로 끝나면 descriptive, 나머지는 None."""
    t = tail(sentence)
    if t.endswith(PROC_ENDINGS):
        return "procedural"
    if t.endswith(("니다", "니까", "다", "죠")) or _haeyo(t):
        return "descriptive"
    return None


def register(sentence):
    """문장 끝 어미로 문체를 가린다. 가릴 수 없으면 None."""
    t = tail(sentence)
    if t.endswith(("십시오", "시오")):
        return "hapsyo_imp"
    # t[-3]은 '니다', '니까' 바로 앞 음절이다. '아니다'처럼 받침 ㅂ이 없으면 합쇼체가 아니다.
    if t.endswith(("니다", "니까")) and len(t) >= 3 and jongseong(t[-3]) == JONG_BIEUP:
        return "hapsyo"
    if t.endswith("니까"):
        return None  # '죽었으니까'의 '-니까'는 연결 어미라 문체를 알려 주지 않는다.
    if t.endswith("세요"):
        return "haeyo_imp"
    if t.endswith("죠") or _haeyo(t):
        return "haeyo"
    if t.endswith(("다", "하자", "까", "냐") + HAERA_RA):
        return "haera"
    return None
