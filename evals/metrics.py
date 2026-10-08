"""측정 전용 지표. 형태소 분석기 kiwipiepy가 없으면 None을 돌려준다. 린터와 훅은 이 모듈을 쓰지 않는다."""
import csv
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GRADES = ROOT / "data" / "basic-vocabulary" / "grades.tsv"
POS_TAGS = {"명사": "NNG", "동사": "VV", "형용사": "VA", "부사": "MAG"}
CONTENT_TAGS = frozenset(POS_TAGS.values())


@lru_cache(maxsize=4)
def grade1_lemmas(path=str(GRADES)):
    """1등급 표제어 집합. 원소는 (표제어, Kiwi 품사 태그)다. '동사/보조동사'처럼 품사가 여럿이면 각각 넣는다."""
    with open(path, encoding="utf-8", newline="") as f:
        return frozenset((row["어휘"], POS_TAGS[pos])
                         for row in csv.DictReader(f, delimiter="\t") if row["등급"] == "1등급"
                         for pos in row["품사"].split("/") if pos in POS_TAGS)


@lru_cache(maxsize=1)
def _kiwi():
    try:
        from kiwipiepy import Kiwi
    except ImportError:
        return None
    return Kiwi()


def _tag(token):
    """VV-R, VA-I 같은 규칙·불규칙 표시를 뗀 품사 태그."""
    return token.tag.split("-")[0]


def _lemma(token):
    """Kiwi 토큰의 표제어. 동사와 형용사는 어간에 '다'를 붙인다."""
    return token.form + "다" if _tag(token) in ("VV", "VA") else token.form


def easy_word_counts(text, path=str(GRADES)):
    """(1등급 내용어 수, 전체 내용어 수). 내용어는 일반 명사, 동사, 형용사, 일반 부사다. 분석기가 없으면 None."""
    kiwi = _kiwi()
    if kiwi is None:
        return None
    easy = grade1_lemmas(path)
    tokens = [t for t in kiwi.tokenize(text) if _tag(t) in CONTENT_TAGS]
    return sum(1 for t in tokens if (_lemma(t), _tag(t)) in easy), len(tokens)
