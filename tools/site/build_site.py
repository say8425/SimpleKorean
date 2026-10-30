#!/usr/bin/env python3
"""tools/site/template.html과 strings/<언어>.json으로 site/의 언어별 소개 페이지를 만든다.

한국어 페이지는 site/index.html, 나머지는 site/<언어>/index.html이다. 템플릿의 {{이름}} 자리에 문구를 넣는다.
문구 파일마다 이름이 한국어판과 같아야 하고, 템플릿에서 쓰지 않는 문구가 있으면 실패한다.

    python3 tools/site/build_site.py          # 페이지를 다시 쓴다
    python3 tools/site/build_site.py --check  # 다시 만든 글과 다르면 실패한다
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "tools" / "site"
TEMPLATE = HERE / "template.html"
STRINGS = HERE / "strings"
SITE_URL = "https://say8425.github.io/SimpleKorean/"
LANGS = ("ko", "en", "ja", "zh", "es")
NAMES = {"ko": "한국어", "en": "English", "ja": "日本語", "zh": "中文", "es": "Español"}
TAG = {"ko": "ko", "en": "en", "ja": "ja", "zh": "zh-Hans", "es": "es"}  # lang과 hreflang에 쓰는 언어 태그. 경로는 LANGS를 쓴다.
OG_LOCALE = {"ko": "ko_KR", "en": "en_US", "ja": "ja_JP", "zh": "zh_CN", "es": "es_ES"}
HOLE = re.compile(r"\{\{(\w+)\}\}")


def page_path(lang):
    """레포지토리 최상위에서 본 페이지 경로."""
    return Path("site") / ("index.html" if lang == "ko" else f"{lang}/index.html")


def page_url(lang):
    return SITE_URL + ("" if lang == "ko" else f"{lang}/")


def link(src, dst):
    """src 페이지에서 dst 페이지로 가는 상대 경로."""
    if src == dst:
        return "./"
    if src == "ko":
        return f"{dst}/"
    return "../" if dst == "ko" else f"../{dst}/"


def load_strings():
    strings = {lang: json.loads((STRINGS / f"{lang}.json").read_text(encoding="utf-8")) for lang in LANGS}
    for lang in LANGS:
        diff = set(strings[lang]) ^ set(strings["ko"])
        if diff:
            raise ValueError(f"strings/{lang}.json의 이름이 한국어판과 다릅니다: {sorted(diff)}")
    return strings


def render(template, strings, lang):
    """한 언어의 페이지 글. 빠진 문구나 쓰지 않은 문구가 있으면 ValueError를 낸다."""
    alternates = [f'<link rel="alternate" hreflang="{TAG[other]}" href="{page_url(other)}">' for other in LANGS]
    alternates.append(f'<link rel="alternate" hreflang="x-default" href="{page_url("ko")}">')
    og_alternates = [f'<meta property="og:locale:alternate" content="{OG_LOCALE[o]}">' for o in LANGS if o != lang]
    langnav = [
        f'<a href="{link(lang, o)}" aria-current="page" lang="{TAG[o]}">{NAMES[o]}</a>' if o == lang
        else f'<a href="{link(lang, o)}" hreflang="{TAG[o]}" lang="{TAG[o]}">{NAMES[o]}</a>'
        for o in LANGS
    ]
    values = {
        **strings[lang],
        "lang_tag": TAG[lang],
        "base": "" if lang == "ko" else "../",
        "url": page_url(lang),
        "og_locale": OG_LOCALE[lang],
        "alternates": "\n".join(alternates),
        "og_alternates": "\n".join(og_alternates),
        "langnav": "\n".join(langnav),
    }
    used = set()

    def fill(m):
        name = m.group(1)
        if name not in values:
            raise ValueError(f"strings/{lang}.json에 {name}이 없습니다")
        used.add(name)
        return values[name]

    text = HOLE.sub(fill, template)
    unused = set(strings[lang]) - used
    if unused:
        raise ValueError(f"템플릿에서 쓰지 않는 문구가 있습니다: {sorted(unused)}")
    return text


def build():
    """{페이지 경로: 글}."""
    template = TEMPLATE.read_text(encoding="utf-8")
    strings = load_strings()
    return {page_path(lang): render(template, strings, lang) for lang in LANGS}


def check(root=ROOT):
    """다시 만든 페이지와 커밋한 페이지가 다르면 문제 목록을 돌려준다."""
    problems = []
    pages = build()
    for path in sorted((Path(root) / "site").glob("*/index.html")):
        rel = path.relative_to(root)
        if rel not in pages:
            problems.append(f"{rel.as_posix()}: LANGS에 없는 언어의 페이지입니다. 지우거나 LANGS에 더하세요")
    for rel, text in pages.items():
        path = Path(root) / rel
        if not path.is_file() or path.read_text(encoding="utf-8") != text:
            problems.append(f"{rel.as_posix()}: tools/site/build_site.py로 다시 만든 글과 다릅니다")
    return problems


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if args not in ([], ["--check"]):
        print(__doc__, file=sys.stderr)
        return 2
    if args == ["--check"]:
        problems = check()
        for p in problems:
            print(p, file=sys.stderr)
        return 1 if problems else 0
    for rel, text in build().items():
        path = ROOT / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        print(rel.as_posix())
    return 0


if __name__ == "__main__":
    sys.exit(main())
