"""SimpleKorean 규칙 판본과 린터를 Python에서 쓴다. 표준 라이브러리만 쓴다.

    from simple_korean import prompt_block, __version__
    prompt = prompt_block(variant="sentences", lang="en")

판본은 prompts/의 파일이다. 규칙 블록(prompts/system-prompt.md)의 답변 절을 둘로 나눴다. sentences는 문장 규칙을,
format은 서식 규칙을 담는다. 설계 문서 5장에 따라 sentences는 슬롭 어휘와 번역투를 지우라는 문장도 담는다. 두 판본을 이어 붙이면 답변 규칙 전체가 된다. 그 밖의 문서 규칙은 담지 않는다. lang은 규칙을
적은 언어이고 답변의 언어를 정하지 않는다. 파일의 첫 줄은 판본, 언어, 버전을 적은 HTML 주석이다. 설치한
패키지에서는 패키지 안의 사본을 읽고, 레포지토리에서는 prompts/의 원본을 읽는다.

린터는 lint_detail(), lint(), reader_check()로 쓴다. 답변을 서식 규칙을 뺀 답변 규칙으로 검사하려면 다음처럼 부른다.

    from simple_korean import lint_detail
    errors = [h for h in lint_detail(reply, "reply", formatting=False) if h["severity"] == "error"]
"""
from types import MappingProxyType

from ._paths import resource
from .ko_lint import lint, lint_detail, reader_check

__version__ = "1.1.1"  # x-release-please-version
__all__ = ("__version__", "VARIANTS", "LANGS", "prompt_path", "prompt_block", "lint", "lint_detail", "reader_check")

VARIANTS = MappingProxyType({"sentences": "sentence-rules", "format": "format-rules"})
LANGS = ("ko", "en")


def prompt_path(variant="sentences", lang="ko"):
    """판본 파일의 경로를 돌려준다. 모르는 판본이나 언어이면 ValueError를 낸다."""
    if variant not in VARIANTS:
        raise ValueError(f"variant는 {tuple(VARIANTS)} 가운데 하나여야 합니다: {variant!r}")
    if lang not in LANGS:
        raise ValueError(f"lang은 {LANGS} 가운데 하나여야 합니다: {lang!r}")
    name = f"{VARIANTS[variant]}.{lang}.md"
    return resource(f"prompts/{name}", f"prompts/{name}")


def prompt_block(variant="sentences", lang="ko"):
    """판본 글을 돌려준다. 첫 줄의 버전 주석도 그대로 담는다."""
    return prompt_path(variant, lang).read_text(encoding="utf-8")
