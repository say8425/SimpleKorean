"""SimpleKorean 린터가 쓰는 한국어 텍스트 도구.

표준 라이브러리만 쓰고 Python 3.9 이상에서 돈다. 함수는 입력을 바꾸지 않고 새 값을 돌려준다.
"""
import re
import unicodedata

HANGUL_FIRST = 0xAC00
HANGUL_LAST = 0xD7A3
JONG_RIEUL = 8  # 받침 28종 가운데 ㄹ의 번호. 0은 받침 없음이다.

OFF_REGION = re.compile(
    r"<!--\s*simple-korean:\s*off\s*-->.*?(?:<!--\s*simple-korean:\s*on\s*-->|\Z)", re.S)
FENCE = re.compile(r"^[ \t]*(`{3,}|~{3,})[^\n]*\n.*?(?:^[ \t]*\1[ \t]*$|\Z)", re.S | re.M)
COMMENT = re.compile(r"<!--.*?-->", re.S)
INLINE_CODE = re.compile(r"`[^`\n]+`")
URL = re.compile(r"https?://[^\s)>\]]+")
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
    """유니코드 NFC로 정규화하고 CRLF와 CR을 LF로 바꾼다."""
    return unicodedata.normalize("NFC", text).replace("\r\n", "\n").replace("\r", "\n")


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


def strip_frontmatter(text):
    """맨 앞의 YAML frontmatter를 공백으로 지운다. 줄 수는 그대로다."""
    return FRONTMATTER.sub(_blank, text, count=1)


def mask(text, quotes=True):
    """어휘 검사용 보기를 만든다.

    꺼짐 구역, 코드 블록, HTML 주석, 인라인 코드, URL을 지운다. quotes가 참이면 따옴표 인용도
    지운다. 지운 자리는 같은 길이의 공백이라 위치와 줄 번호가 원문과 같다.
    """
    t = OFF_REGION.sub(_blank, text)
    t = FENCE.sub(_blank, t)
    t = COMMENT.sub(_blank, t)
    t = INLINE_CODE.sub(_blank, t)
    t = URL.sub(_blank, t)
    if quotes:
        for rx in QUOTES:
            t = rx.sub(_blank, t)
    return t


def line_of(text, pos):
    """위치 pos가 있는 줄 번호(1부터)."""
    return text.count("\n", 0, pos) + 1


def hangul_ratio(text):
    """코드와 URL을 뺀 글자 가운데 한글 음절의 비율. 분모는 한글 음절 수와 라틴 문자 수의 합이다."""
    body = mask(nfc(text), quotes=False)
    hangul = sum(1 for c in body if is_hangul(c))
    latin = sum(1 for c in body if c.isascii() and c.isalpha())
    total = hangul + latin
    return hangul / total if total else 0.0
