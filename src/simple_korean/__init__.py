"""SimpleKorean 규칙 판본을 Python에서 읽는다. 표준 라이브러리만 쓴다.

    from simple_korean import prompt_block, __version__
    prompt = prompt_block(variant="sentences", lang="en")

판본은 prompts/의 파일이다. 규칙 블록(prompts/system-prompt.md)의 답변 절을 둘로 나눴다. sentences는 문장 규칙을,
format은 서식 규칙을 담는다. 두 판본을 이어 붙이면 답변 규칙 전체가 된다. 문서 규칙은 담지 않는다. lang은 규칙을
적은 언어이고 답변의 언어를 정하지 않는다. 파일의 첫 줄은 판본, 언어, 버전을 적은 HTML 주석이다. 설치한
패키지에서는 패키지 안의 사본을 읽고, 레포지토리에서는 prompts/의 원본을 읽는다.
"""
from pathlib import Path
from types import MappingProxyType

__version__ = "1.1.1"  # x-release-please-version

VARIANTS = MappingProxyType({"sentences": "sentence-rules", "format": "format-rules"})
LANGS = ("ko", "en")
_HERE = Path(__file__).resolve().parent


def prompt_path(variant="sentences", lang="ko"):
    """판본 파일의 경로를 돌려준다. 모르는 판본이나 언어이면 ValueError를 낸다."""
    if variant not in VARIANTS:
        raise ValueError(f"variant는 {tuple(VARIANTS)} 가운데 하나여야 합니다: {variant!r}")
    if lang not in LANGS:
        raise ValueError(f"lang은 {LANGS} 가운데 하나여야 합니다: {lang!r}")
    name = f"{VARIANTS[variant]}.{lang}.md"
    bundled = _HERE / "prompts" / name
    return bundled if bundled.is_file() else _HERE.parent.parent / "prompts" / name


def prompt_block(variant="sentences", lang="ko"):
    """판본 글을 돌려준다. 첫 줄의 버전 주석도 그대로 담는다."""
    return prompt_path(variant, lang).read_text(encoding="utf-8")
