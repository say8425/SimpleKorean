"""표기 단어 목록(data/terms.json)과 프로젝트 설정(.simple-korean.json)을 다룬다."""
import copy
import json
import re
import unicodedata
from bisect import bisect_left
from collections import namedtuple
from pathlib import Path

from ko_rules import ERROR, WARNING, Hit
from ko_text import line_of, nfc

ROOT = Path(__file__).resolve().parent.parent
TERMS_JSON = ROOT / "data" / "terms.json"
CONFIG_NAME = ".simple-korean.json"
CONFIG_KEYS = frozenset({"terms", "skip", "spacing"})
GLOBAL_SKIP = ("캐시백", "캐쉬백", "레포트", "쉘프", "디플로이먼트", "디렉토리 유틸리티", "컬럼비아")
SPACING_SWITCHABLE = frozenset({"parameter_spacing", "return_value_spacing", "open_source_spacing"})
RANK = {None: 0, "mix": 0, WARNING: 1, ERROR: 2}
# 설정 값은 세션 시작 훅을 거쳐 모델의 문맥에 들어간다(src/hooks/simple-korean-activate.js와 같은 기준).
MAX_FORM_CHARS = 20
MAX_SKIP_ENTRIES = 100
FORM_CHARS = re.compile(r"[가-힣A-Za-z0-9 ]+")
SHOWN_KEY = re.compile(r"[A-Za-z0-9_.-]{1,40}")

Occurrence = namedtuple("Occurrence", "concept form role start")


def load_terms(path=TERMS_JSON):
    """단어 목록의 개념 목록을 읽는다."""
    return json.loads(Path(path).read_text(encoding="utf-8"))["concepts"]


def find_config(start):
    """start 파일이나 디렉터리에서 위로 올라가며 .simple-korean.json을 찾는다. 없으면 None."""
    here = Path(start).expanduser().resolve()
    here = here if here.is_dir() else here.parent
    for directory in (here, *here.parents):
        candidate = directory / CONFIG_NAME
        if candidate.is_file():
            return candidate
    return None


def _shown(key):
    """설정에서 온 키를 메시지에 넣을 형태로 바꾼다. 평범한 id는 그대로, 아니면 40자까지 repr로 보인다."""
    return key if SHOWN_KEY.fullmatch(key) else repr(key[:40])


def form_ok(form):
    """지정형으로 받을 문자열인지 본다. NFC로 맞춘 뒤 한글, 영문, 숫자, 공백만 쓰고, 앞뒤 공백을 뺀 길이가
    1~MAX_FORM_CHARS자다. 단어 목록의 형태는 모두 한글과 공백이다."""
    f = unicodedata.normalize("NFC", form)
    return bool(FORM_CHARS.fullmatch(f)) and 0 < len(f.strip(" ")) <= MAX_FORM_CHARS


def skip_ok(skip):
    """건너뛸 문자열 목록인지 본다. MAX_SKIP_ENTRIES개 이하이고, 항목마다 출력할 수 있는 글자로 된 빈칸 아닌 한 줄이다."""
    return (isinstance(skip, list) and len(skip) <= MAX_SKIP_ENTRIES
            and all(isinstance(s, str) and s.isprintable() and s.strip(" ") for s in skip))


def load_config(path):
    """설정 파일을 읽는다. path가 없으면 빈 설정이다. 형식이 틀리면 경로를 담은 ValueError를 낸다."""
    if not path:
        return {}
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as err:
        raise ValueError(f"{path}: 설정을 읽지 못했습니다: {err}") from err
    if not isinstance(data, dict):
        raise ValueError(f"{path}: 설정은 JSON 객체여야 합니다")
    unknown = sorted(set(data) - CONFIG_KEYS)
    if unknown:
        raise ValueError(f"{path}: 알 수 없는 키 [{', '.join(_shown(k) for k in unknown)}]")
    if data.get("spacing", "attached") not in ("attached", "spaced"):
        raise ValueError(f"{path}: spacing은 attached 또는 spaced여야 합니다")
    _check_types(path, data)
    return data


def _check_types(path, data):
    """terms와 skip 값의 타입을 검사한다. 틀리면 경로를 담은 ValueError를 낸다."""
    terms = data.get("terms", {})
    if not isinstance(terms, dict):
        raise ValueError(f"{path}: terms는 개념 id를 키로 쓰는 객체여야 합니다")
    for cid, value in terms.items():
        entry = {"write": value} if isinstance(value, str) else value
        ok = (isinstance(entry, dict) and set(entry) <= {"write", "reason"}
              and isinstance(entry.get("write"), str) and form_ok(entry["write"])
              and isinstance(entry.get("reason", ""), str))
        if not ok:
            raise ValueError(f'{path}: terms.{_shown(cid)}는 "형태" 문자열이나 {{"write": "형태", "reason": "이유"}} '
                             f"객체여야 합니다. 형태는 한글, 영문, 숫자, 공백으로 {MAX_FORM_CHARS}자 이하입니다")
    if not skip_ok(data.get("skip", [])):
        raise ValueError(f"{path}: skip은 한 줄짜리 문자열 {MAX_SKIP_ENTRIES}개 이하의 목록이어야 합니다")


def _override(concept, new, reason):
    """지정형을 new로 바꾼 새 개념과 경고 목록을 돌려준다."""
    c = copy.deepcopy(concept)
    warnings = []
    if c["group"] == 1 and not reason:
        warnings.append(f"{c['id']}: ① 무리의 지정형을 바꾸려면 reason을 적어야 합니다")
    c["accept"] = [f for f in c.get("accept", []) if f != new] + [c["write"]]
    c["replaced"] = c.get("replaced", []) + [c["write"]]
    c["flag"]["forms"] = [f for f in c["flag"]["forms"] if f != new]
    c["alias"] = [f for f in c.get("alias", []) if f != new]
    c["write"] = new
    return c, warnings


def apply_config(concepts, config):
    """설정을 반영한 새 개념 목록과 설정 경고 목록을 돌려준다. 입력은 바꾸지 않는다."""
    overrides = config.get("terms", {})
    spaced = config.get("spacing") == "spaced"
    known = {c["id"] for c in concepts}
    warnings = [f"{_shown(cid)}: 단어 목록에 없는 개념입니다" for cid in overrides if cid not in known]
    result = []
    for concept in concepts:
        override = overrides.get(concept["id"])
        if override is None and spaced and concept["id"] in SPACING_SWITCHABLE:
            override = {"write": concept["flag"]["forms"][0], "reason": "spacing=spaced"}
        new = nfc(override if isinstance(override, str) else (override or {}).get("write", ""))
        if new and new != concept["write"]:
            reason = None if isinstance(override, str) else override.get("reason")
            changed, notes = _override(concept, new, reason)
            result.append(changed)
            warnings.extend(notes)
        else:
            result.append(copy.deepcopy(concept))
    return result, warnings


def _form_regex(form):
    return r"\s+".join(re.escape(part) for part in nfc(form).split())


def _spans(strings, masked):
    return [(m.start(), m.end()) for s in strings for m in re.finditer(_form_regex(s), masked)]


def _merge(spans):
    """겹치거나 맞닿은 구간을 하나로 합친 목록. 시작 위치 순이다."""
    merged = []
    for a, b in sorted(spans):
        if merged and a <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], b))
        else:
            merged.append((a, b))
    return merged


def _covered(merged, starts, start, end):
    """[start, end)가 합친 구간 가운데 하나와 겹치면 참이다. starts는 merged의 시작 위치 목록이다."""
    i = bisect_left(starts, end) - 1
    return i >= 0 and merged[i][1] > start


def _roles(concept):
    pairs = ([(concept["write"], "write")] + [(f, "alias") for f in concept.get("alias", [])]
             + [(f, "flag") for f in concept["flag"]["forms"]]
             + [(f, "accept") for f in concept.get("accept", [])])
    return sorted(pairs, key=lambda pair: len(pair[0]), reverse=True)


def scan(masked, concepts, extra_skip=()):
    """개념마다 형태가 나온 자리를 찾는다. 긴 형태부터 맞추고, 건너뛸 문자열과 겹치는 자리는 뺀다."""
    shared = _spans(tuple(dict.fromkeys(nfc(s) for s in (*GLOBAL_SKIP, *extra_skip))), masked)
    shared_merged = _merge(shared)
    found = []
    for c in concepts:
        roles = _roles(c)
        role_of = {}
        for form, role in roles:
            role_of.setdefault(" ".join(nfc(form).split()), role)
        rx = re.compile(r"(?<![가-힣])(?:" + "|".join(_form_regex(f) for f, _ in roles) + ")")
        own = _spans(c.get("skip", []), masked)
        skip = _merge(shared + own) if own else shared_merged
        starts = [a for a, _ in skip]
        for m in rx.finditer(masked):
            if _covered(skip, starts, m.start(), m.end()):
                continue
            form = " ".join(m.group(0).split())
            found.append(Occurrence(c["id"], form, role_of[form], m.start()))
    return found


def _canon(occ):
    return "write" if occ.role in ("write", "alias") else occ.form


def _base_severity(concept, occ, strict):
    if occ.role == "flag":
        level = concept["flag"]["strict" if strict else "default"]
        if level in (ERROR, WARNING):
            return level, "spelling"
        return (WARNING, "spelling") if strict else (None, None)
    if occ.role == "accept" and (strict or occ.form in concept.get("replaced", ())):
        return WARNING, "term_choice"
    return None, None


def _concept_hits(masked, concept, occs, strict):
    kinds = list(dict.fromkeys(_canon(o) for o in occs))
    mixed = len(kinds) >= 2 and concept.get("mix", True)
    base = "write" if (strict or "write" in kinds) else kinds[0]
    hits = []
    for o in occs:
        kind = _canon(o)
        if kind == "write":
            continue
        severity, category = _base_severity(concept, o, strict)
        if mixed and kind != base:
            mix = ERROR if strict else WARNING
            if RANK[mix] > RANK[severity]:
                severity, category = mix, category or "term_mix"
        if severity in (ERROR, WARNING):
            hits.append(Hit(category, severity, line_of(masked, o.start), f"{o.form} → {concept['write']}"))
    return hits


def term_hits(masked, concepts, strict=False, extra_skip=()):
    """표기 검사. 잡을 형태, 지정형이 아닌 형태, 문서 안 혼용을 강도와 함께 돌려준다."""
    by_concept = {}
    for occ in scan(masked, concepts, extra_skip):
        by_concept.setdefault(occ.concept, []).append(occ)
    cmap = {c["id"]: c for c in concepts}
    hits = []
    for cid, occs in by_concept.items():
        hits.extend(_concept_hits(masked, cmap[cid], sorted(occs, key=lambda o: o.start), strict))
    return hits
