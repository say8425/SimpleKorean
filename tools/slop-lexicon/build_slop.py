#!/usr/bin/env python3
"""한국어 슬롭 어휘 목록(evals/slop.tsv)을 만든다.

원본 SimpleEnglish는 공개된 금지 목록 122개 가운데 8개 이상에 나온 말을 골랐다. 여기서는
라이선스를 확인한 한국어 AI 문체 스킬들(sources.json)을 고정 커밋으로 내려받고, 후보 말이
규칙 줄(표 행, 목록 항목, 화살표가 있는 줄, 따옴표 안의 말)에 나온 출처 수를 센다.
문턱 이상이고, 다른 린트 범주가 이미 잡지 않고, 제외 목록에 없는 말만 남긴다.

    python3 -I tools/slop-lexicon/build_slop.py fetch    # 출처를 cache/에 내려받는다
    python3 -I tools/slop-lexicon/build_slop.py report   # 후보별 출처 수와 새 후보를 출력한다
    python3 -I tools/slop-lexicon/build_slop.py build    # evals/slop.tsv를 쓴다
"""
import json
import re
import sys
import urllib.request
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT / "evals"))
CACHE = HERE / "cache"
SOURCES = HERE / "sources.json"
CANDIDATES = HERE / "candidates.tsv"
EXCLUSIONS = HERE / "exclusions.tsv"
OUT = ROOT / "evals" / "slop.tsv"
THRESHOLD = 2
RULE_LINE = re.compile(r"^\s*(?:\||[-*+]\s|\d+[.)]\s)|→|->|⇒")
QUOTED = re.compile(r"[\"'“”‘’`「」『』]([^\"'“”‘’`「」『』\n]{2,30})[\"'“”‘’`「」『』]")
HANGUL_TERM = re.compile(r"^[가-힣][가-힣 ]{1,11}$")
NEVER = re.compile(r"(?!x)x")
REPO_NAME = re.compile(r"[A-Za-z0-9-]+/[A-Za-z0-9_.-]+")
COMMIT_HASH = re.compile(r"[0-9a-f]{6,40}")
FILE_PATH = re.compile(r"[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*")


def nfc(text):
    return unicodedata.normalize("NFC", text)


def rule_text(text):
    """규칙으로 보이는 부분만 모은다: 표 행, 목록 항목, 화살표가 있는 줄, 따옴표와 백틱 안의 말."""
    lines = [line for line in text.splitlines() if RULE_LINE.search(line)]
    quoted = [m.group(1) for m in QUOTED.finditer(text)]
    return nfc("\n".join(lines + quoted))


def term_regex(term):
    return re.compile(r"(?<![가-힣])" + r"\s*".join(re.escape(p) for p in nfc(term).split()))


def count_sources(terms, texts):
    """말마다 그 말을 규칙 부분에 담은 출처 수. texts는 {출처: 원문}이다."""
    rules = {repo: rule_text(text) for repo, text in texts.items()}
    return {t: sum(1 for r in rules.values() if term_regex(t).search(r)) for t in terms}


def covered_elsewhere(term):
    """슬롭이 아닌 다른 린트 범주가 이미 잡는 말이면 참이다. 같은 말을 두 번 세지 않기 위해서다."""
    import ko_rules
    return any(h.category != "slop_word" for h in ko_rules.lexical_hits(term, slop_rx=NEVER))


def read_tsv(path):
    """'#' 주석과 빈 줄을 뺀 TSV 행 목록. 파일이 없으면 빈 목록이다."""
    p = Path(path)
    if not p.exists():
        return []
    return [line.split("\t") for line in p.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#")]


def build_rows(candidates, exclusions, texts, threshold=THRESHOLD):
    """(말, 출처 수, 바꿀 말) 행. 출처 수가 많은 순, 같으면 가나다순이다."""
    excluded = {nfc(r[0]) for r in exclusions}
    terms = [nfc(c[0]) for c in candidates]
    counts = count_sources(terms, texts)
    rows = []
    for c, term in zip(candidates, terms):
        swap = c[1] if len(c) > 1 and c[1] else "(지우세요)"
        if term in excluded or counts[term] < threshold or covered_elsewhere(term):
            continue
        rows.append((term, counts[term], swap))
    return sorted(rows, key=lambda r: (-r[1], r[0]))


def discover(texts, known, threshold=THRESHOLD):
    """후보에 없는 따옴표 속 한국어 말 가운데 여러 출처에 나온 것. 사람이 후보에 더할지 고른다."""
    pool = {}
    for repo, text in texts.items():
        for m in QUOTED.finditer(nfc(text)):
            s = m.group(1).strip()
            if HANGUL_TERM.match(s) and s not in known:
                pool.setdefault(s, set()).add(repo)
    return sorted(((s, len(r)) for s, r in pool.items() if len(r) >= threshold), key=lambda x: (-x[1], x[0]))


def write_tsv(rows, n_sources, out=OUT):
    header = ["# SimpleKorean 슬롭 어휘. tools/slop-lexicon/build_slop.py가 만든다. 직접 고치지 마세요.",
              f"# 열: 말, 이 말을 규칙에 담은 출처 수(전체 {n_sources}곳), 바꿀 말"]
    Path(out).write_text("\n".join(header + [f"{t}\t{n}\t{s}" for t, n, s in rows]) + "\n", encoding="utf-8")


def check_source(source):
    """출처 항목의 repo, commit, files가 허용한 형태인지 본다. 아니면 ValueError를 낸다.

    files에 '..', '#', '?', 절대 경로가 들어가면 받는 주소와 저장하는 경로가 달라져 캐시 밖에 쓸 수 있다.
    """
    repo, commit, files = source.get("repo"), source.get("commit"), source.get("files")
    if not (isinstance(repo, str) and REPO_NAME.fullmatch(repo) and repo.split("/")[1] not in (".", "..")):
        raise ValueError(f"repo는 '소유자/저장소' 형태여야 합니다: {repo!r}")
    if not (isinstance(commit, str) and COMMIT_HASH.fullmatch(commit)):
        raise ValueError(f"{repo}: commit은 16진수 해시여야 합니다: {commit!r}")
    if not isinstance(files, list) or not files:
        raise ValueError(f"{repo}: files는 비어 있지 않은 목록이어야 합니다")
    for rel in files:
        if not (isinstance(rel, str) and FILE_PATH.fullmatch(rel) and not {".", ".."} & set(rel.split("/"))):
            raise ValueError(f"{repo}: 파일 경로는 저장소 안의 상대 경로여야 합니다: {rel!r}")
    return source


def load_sources(path=SOURCES):
    """sources.json을 읽고 항목마다 check_source로 검사한다."""
    return [check_source(s) for s in json.loads(Path(path).read_text(encoding="utf-8"))]


def _cache_file(source, rel, cache=CACHE):
    """출처 파일을 둘 캐시 안의 경로. 캐시 밖을 가리키면 ValueError를 낸다."""
    root = Path(cache).resolve()
    path = (root / source["repo"].replace("/", "__") / rel).resolve()
    if not path.is_relative_to(root):
        raise ValueError(f"캐시 밖을 가리킵니다: {path}")
    return path


def fetch(sources, cache=CACHE, opener=urllib.request.urlopen):
    """출처 파일을 고정 커밋으로 내려받는다. 출처마다 디렉터리를 따로 쓴다. 먼저 모든 항목을 검사한다."""
    for s in sources:
        check_source(s)
    for s in sources:
        for rel in s["files"]:
            dest = _cache_file(s, rel, cache)
            url = f"https://raw.githubusercontent.com/{s['repo']}/{s['commit']}/{rel}"
            dest.parent.mkdir(parents=True, exist_ok=True)
            with opener(url, timeout=30) as resp:
                dest.write_bytes(resp.read())
            print("fetched", url)


def source_texts(sources, cache=CACHE):
    """{출처: 파일들을 이은 원문}. 파일이 없으면 fetch를 먼저 하라고 알리고 멈춘다."""
    texts = {}
    for s in sources:
        parts = []
        for rel in check_source(s)["files"]:
            p = _cache_file(s, rel, cache)
            if not p.exists():
                raise SystemExit(f"{p}가 없습니다. 먼저 fetch를 실행하세요.")
            parts.append(p.read_text(encoding="utf-8", errors="replace"))
        texts[s["repo"]] = "\n".join(parts)
    return texts


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    command = args[0] if args else "build"
    try:
        sources = load_sources()
    except ValueError as err:
        raise SystemExit(f"{SOURCES.name}: {err}") from err
    if command == "fetch":
        fetch(sources)
        return 0
    texts = source_texts(sources)
    candidates = read_tsv(CANDIDATES)
    if command == "report":
        counts = count_sources([nfc(c[0]) for c in candidates], texts)
        for term, n in sorted(counts.items(), key=lambda x: (-x[1], x[0])):
            print(f"{n}\t{term}\t{'다른 범주가 잡음' if covered_elsewhere(term) else ''}")
        print("--- 후보에 없는 따옴표 속 말(출처 수)")
        for s, n in discover(texts, {nfc(c[0]) for c in candidates})[:80]:
            print(f"{n}\t{s}")
        return 0
    rows = build_rows(candidates, read_tsv(EXCLUSIONS), texts)
    write_tsv(rows, len(sources))
    print(f"{len(rows)} terms -> {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
