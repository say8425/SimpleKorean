# README 다국어판과 릴리스 자동화 구현 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** release-please로 버전·CHANGELOG·태그·Release를 자동화하고(PR 2), README를 영어·일본어·중국어·스페인어로 옮겨 생성 블록과 구조를 CI가 대조하게 한다(PR 3).

**Architecture:** PR 2는 release-please(`simple` + extra-files) 설정과 워크플로를 더하고, `check_numbers.py`의 버전 대조와 CHANGELOG 검사를 릴리스 흐름에 맞춘다. PR 제목은 새 스크립트가 커밋 규칙대로 검사한다. PR 3은 언어 표 `evals/readme_i18n.py`를 두고, 두 생성기가 그 문장 틀로 다섯 README의 블록을 쓴다. `check_numbers.py`는 같은 틀로 블록을 대조하고, 번역판의 구조를 한국어판과 대조한다.

**Tech Stack:** Python 3.9 이상(표준 라이브러리만, 수치 검증만 `.venv`의 kiwipiepy 0.24.0), GitHub Actions, `googleapis/release-please-action@v5`, release-please CLI 17.11.2(로컬 dry-run), shields.io 동적 배지, actionlint.

**Spec:** `docs/superpowers/specs/2026-10-14-readme-languages-design.md`

## Global Constraints

- 모든 Python 코드는 Python 3.9에서 돈다. CI의 `python39` 작업이 `evals/tests/run.py`를 3.9로 돌린다. `match`, `X | Y` 타입 표기, f-string 중괄호 안의 백슬래시를 쓰지 않는다.
- `evals/`의 코드는 표준 라이브러리만 쓴다. kiwipiepy는 쉬운 단어 비율에만 쓰고, `check_numbers.py`는 `.venv/bin/python`으로 돌린다.
- 코드의 주석과 독스트링은 한국어 해라체로 쓴다. 사용자에게 보이는 메시지는 지금 코드처럼 합쇼체로 쓴다(예: "README.md에 벤치마크 블록이 없습니다").
- 커밋 제목은 `<유형>: <한국어 해라체 문장>`이다. 유형은 feat, fix, perf, refactor, docs, test, chore, ci다. 커밋 끝에 아래 두 줄을 붙인다.
  ```
  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
  Claude-Session: https://claude.ai/code/session_01SanRSLxxVtkLMJh1wLGeGZ
  ```
- 한국어 README의 생성 블록은 한 글자도 바뀌지 않는다. `.venv/bin/python evals/check_numbers.py`가 이것을 증명한다.
- `README.md`, `CHANGELOG.md`, `SKILL.md`는 CI의 문서 관문 `python3 evals/ko_lint.py --gate=warning ...`을 통과한다.
- 시험은 pytest 없이 `python3 evals/tests/run.py`가 `evals/tests/test_*.py`의 `test_*` 함수를 돌린다.
- 언어 순서는 `ko`, `en`, `ja`, `zh`, `es`이고, 파일은 `README.md`, `docs/README.<언어>.md`이다.
- es의 숫자: 네 자리까지 구분 기호가 없다(2271). 다섯 자리부터 세 자리마다 U+00A0을 둔다. 퍼센트 앞에 U+00A0을 둔다(100 %). 소수점은 점이다.
- 태그 형식은 `v<버전>`이다. 릴리스 워크플로 권한은 `contents`, `issues`, `pull-requests` 쓰기다.
- 커밋하는 문서에는 로컬 절대 경로를 쓰지 않는다. 한 작업 안에서만 쓰는 임시 파일은 `S=${S:-$(mktemp -d)}`로 만든 폴더에 둔다. 다음 작업이 읽을 결과(dry-run 출력, 확인 메모, 스크린샷)는 git이 무시하는 `.superpowers/readme-languages/`에 둔다.
- push, PR 생성, 검사, 리뷰는 바로 한다. PR 병합, GitHub Release 생성, 레포 설정 변경은 결과를 보고하고 사용자의 확인을 받은 뒤에 한다.

## Review Focus

1. PR 제목에 범위나 `!`, 전각 콜론, 두 칸 공백, 대문자 유형이 오거나 제목이 비어 있으면(`fix(hooks): …`, `feat!: …`, `fix：…`) 형식 오류 한 줄로 알려 준다. 조용히 통과하거나 추적 정보를 쏟으면 안 된다. 시험: Task 3 `test_format_errors_name_the_rule`.
2. README 링크에 앵커가 붙거나(`SKILL.md#규칙`), 코드 블록·인라인 코드·인용 안에 링크 모양 글이 있거나, 번역판 링크에 `../`가 빠질 수 있다. 앵커는 떼고 파일을 찾는다. 코드와 인용은 세지 않는다. 빠진 `../`는 그 링크를 밝혀 알린다. 시험: Task 9 `test_structure_ignores_code_quotes_external_links_and_anchors`, `test_structure_matches_headings_and_links`.
3. CHANGELOG에 새 형식(`## [1.0.1](...) (날짜)`)과 옛 형식이 섞여 있어도 첫 항목의 버전과 날짜만 읽는다. 측정 날짜가 릴리스 날짜와 같은 날이면 릴리스한 측정으로 보고 검사한다. 시험: Task 1 `test_check_versions_requires_one_value_everywhere`, Task 2 `test_latest_release_date_reads_the_first_entry_in_either_form`, `test_unreleased_means_strictly_after_the_latest_release`.
4. `--readme`를 돌릴 때 README 하나에 블록 표시가 없거나 파일이 없으면, 아무 파일도 바꾸지 않고 그 파일 이름을 밝히고 멈춘다. 시험: Task 8 `test_update_readmes_stops_before_writing_when_a_readme_is_broken`.
5. 언어 선택 줄의 공백 하나가 다르거나 블록 표시가 두 번 나오면, 검사가 그대로 써야 할 블록을 보여 준다. 시험: Task 9 `test_structure_needs_the_exact_language_line_and_single_markers`.

---

## 작업 환경

- 모든 명령은 레포 루트에서 돌린다: `cd "$(git rev-parse --show-toplevel)"`.
- `.venv`가 없으면 만든다.
  ```bash
  uv venv .venv --python 3.12 && uv pip install --python .venv/bin/python kiwipiepy==0.24.0 kiwipiepy-model==0.24.0
  ```
- CI와 같은 전체 확인(이 계획에서 "전체 확인"이라고 부른다):
  ```bash
  python3 evals/ko_lint.py --self-test
  python3 evals/tests/run.py
  node --test src/hooks/simple-korean-activate.test.js
  python3 src/hooks/test_lint_hook.py
  .venv/bin/python evals/check_numbers.py
  python3 evals/ko_lint.py --gate=warning skills/simple-korean/SKILL.md skills/simple-korean/references/*.md prompts/system-prompt.md output-styles/simple-korean.md README.md CHANGELOG.md tools/slop-lexicon/README.md src/hooks/README.md data/basic-vocabulary/README.md
  actionlint
  ```
  기대: 모든 명령이 0으로 끝나고, `check_numbers OK`가 나온다. `run.py`의 출력에 `FAIL`이 없다.

## 파일 구성

PR 2(브랜치 `ci/release-please`, 스펙 커밋이 이미 있다):

| 파일 | 책임 |
|---|---|
| `release-please-config.json` (새 파일) | 릴리스 유형, 태그 형식, 한국어 CHANGELOG 절, 버전을 올릴 파일 |
| `.release-please-manifest.json` (새 파일) | 마지막 릴리스 버전 |
| `.github/workflows/release.yml` (새 파일) | `main` push마다 release-please를 돌린다 |
| `.github/workflows/pr-title.yml` (새 파일) | PR 제목 검사를 돌린다 |
| `evals/check_pr_title.py` (새 파일) | PR 제목이 커밋 규칙을 지키는지 본다 |
| `evals/tests/test_check_pr_title.py` (새 파일) | 위 스크립트의 시험 |
| `evals/check_numbers.py` | 버전 대조 대상, 아직 릴리스하지 않은 측정의 CHANGELOG 검사 |
| `evals/tests/test_check_numbers.py` | 위 변경의 시험 |
| `evals/calibration/hits.py` | 독스트링 한 줄 |
| `skills/simple-korean/SKILL.md` | 버전 줄의 release-please 표시 |
| `README.md` | 동적 배지, 기여 절의 PR 제목 규칙 |
| `CHANGELOG.md` | 머리말 |

PR 3(브랜치 `docs/readme-languages`, PR 2를 병합한 `main`에서 만든다):

| 파일 | 책임 |
|---|---|
| `evals/readme_i18n.py` (새 파일) | 언어 표, 숫자 표기, 언어 선택 줄, 생성 블록의 문장 틀 |
| `evals/tests/test_readme_i18n.py` (새 파일) | 언어 표와 두 생성기의 언어별 출력 시험 |
| `evals/report.py` | 벤치마크 블록을 언어별로 쓰고, 다섯 README를 함께 고친다 |
| `evals/make_examples.py` | 보기 블록을 언어별로 쓰고, 다섯 README를 함께 고친다 |
| `evals/check_numbers.py` | 번역판의 블록·글자 수·구조 검사, `main`에 연결 |
| `evals/tests/test_check_numbers.py` | 위 검사의 시험 |
| `docs/README.en.md`, `docs/README.ja.md`, `docs/README.zh.md`, `docs/README.es.md` (새 파일) | 번역판 |
| `README.md` | 언어 선택 줄, 영어 문단 삭제 |

---

## Part A — PR 2: release-please

시작하기 전에: 사용자가 이 계획을 승인하면 계획 문서를 `ci/release-please` 브랜치에 커밋한다. 커밋 제목은 `docs: README 다국어판과 릴리스 자동화 구현 계획을 적는다`이다.

### Task 1: release-please 설정과 버전 대조

**Files:**
- Create: `release-please-config.json`, `.release-please-manifest.json`, `.github/workflows/release.yml`
- Modify: `skills/simple-korean/SKILL.md:12`, `evals/check_numbers.py:14,36-43`
- Test: `evals/tests/test_check_numbers.py:1-5,43-54`

**Interfaces:**
- Produces: `check_numbers.VERSION_PATTERNS`의 키는 `skills/simple-korean/SKILL.md`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `.codex-plugin/plugin.json`, `.release-please-manifest.json`, `CHANGELOG.md`다. `README.md`는 없다. `release-please-config.json`의 `packages["."]["extra-files"]`는 이 키 가운데 CHANGELOG와 매니페스트를 뺀 네 파일이다.

- [ ] **Step 1: 실패하는 시험을 쓴다**

`evals/tests/test_check_numbers.py` 맨 위의 import에 `import re`를 더한다(`import json` 다음 줄).

```python
import json
import re
import sys
import tempfile
from pathlib import Path
```

`test_check_versions_requires_one_value_everywhere`를 통째로 바꾸고, 그 아래에 도우미와 시험 하나를 더한다.

```python
def test_check_versions_requires_one_value_everywhere():
    texts = {
        "skills/simple-korean/SKILL.md": SKILL,
        ".claude-plugin/plugin.json": '{"version": "1.0.0"}',
        ".claude-plugin/marketplace.json": '{"plugins": [{"version": "1.0.0"}]}',
        ".codex-plugin/plugin.json": '{"version": "1.0.0"}',
        ".release-please-manifest.json": '{\n  ".": "1.0.0"\n}\n',
        "CHANGELOG.md": "# 변경 기록\n\n## 1.0.0, 2026-10-09\n",
    }
    assert "README.md" not in cn.VERSION_PATTERNS
    assert cn.check_versions(texts) == []
    assert cn.check_versions({**texts, "CHANGELOG.md": "## 1.0.1, 2026-10-10\n"}) != []
    assert cn.check_versions({**texts, ".release-please-manifest.json": '{".": "1.0.1"}'}) != []
    bumped = {name: text.replace("1.0.0", "1.0.1") for name, text in texts.items()}
    released = ("# 변경 기록\n\n## [1.0.1](https://github.com/say8425/SimpleKorean/compare/v1.0.0...v1.0.1) (2026-10-20)\n\n"
                "### 고친 것\n\n* 고친다\n\n## 1.0.0, 2026-10-09\n")
    assert cn.check_versions({**bumped, "CHANGELOG.md": released}) == []


def _jsonpath(data, path):
    """'$.plugins[0].version' 같은 단순한 JSONPath를 따라간다."""
    for key, index in re.findall(r"\.(\w+)|\[(\d+)\]", path[1:]):
        data = data[key] if key else data[int(index)]
    return data


def test_release_config_bumps_every_versioned_file():
    config = json.loads((cn.ROOT / "release-please-config.json").read_text(encoding="utf-8"))
    package = config["packages"]["."]
    assert package["release-type"] == "simple" and config["include-component-in-tag"] is False
    version = json.loads((cn.ROOT / ".release-please-manifest.json").read_text(encoding="utf-8"))["."]
    bumped = set()
    for item in package["extra-files"]:
        if isinstance(item, str):
            bumped.add(item)
            continue
        bumped.add(item["path"])
        data = json.loads((cn.ROOT / item["path"]).read_text(encoding="utf-8"))
        assert _jsonpath(data, item["jsonpath"]) == version, item
    assert bumped == set(cn.VERSION_PATTERNS) - {"CHANGELOG.md", ".release-please-manifest.json"}
    skill = (cn.ROOT / "skills/simple-korean/SKILL.md").read_text(encoding="utf-8")
    assert f'  version: "{version}" # x-release-please-version\n' in skill
```

- [ ] **Step 2: 시험이 실패하는지 본다**

Run: `python3 evals/tests/run.py evals/tests/test_check_numbers.py`
Expected: `FAIL test_check_numbers.test_check_versions_requires_one_value_everywhere`(README.md가 아직 대조 대상이다)와 `FAIL test_check_numbers.test_release_config_bumps_every_versioned_file`(`release-please-config.json`이 없다).

- [ ] **Step 3: 설정 파일 세 개를 만든다**

`.release-please-manifest.json`:

```json
{
  ".": "1.0.0"
}
```

`release-please-config.json`:

```json
{
  "$schema": "https://raw.githubusercontent.com/googleapis/release-please/main/schemas/config.json",
  "include-component-in-tag": false,
  "changelog-sections": [
    {"type": "feat", "section": "기능"},
    {"type": "fix", "section": "고친 것"},
    {"type": "perf", "section": "성능"},
    {"type": "refactor", "section": "리팩터링", "hidden": true},
    {"type": "docs", "section": "문서", "hidden": true},
    {"type": "test", "section": "시험", "hidden": true},
    {"type": "chore", "section": "기타", "hidden": true},
    {"type": "ci", "section": "CI", "hidden": true}
  ],
  "packages": {
    ".": {
      "release-type": "simple",
      "extra-files": [
        {"type": "json", "path": ".claude-plugin/plugin.json", "jsonpath": "$.version"},
        {"type": "json", "path": ".claude-plugin/marketplace.json", "jsonpath": "$.plugins[0].version"},
        {"type": "json", "path": ".codex-plugin/plugin.json", "jsonpath": "$.version"},
        "skills/simple-korean/SKILL.md"
      ]
    }
  }
}
```

`.github/workflows/release.yml`:

```yaml
name: release
on:
  push:
    branches: [main]
  workflow_dispatch:
permissions:
  contents: write
  issues: write
  pull-requests: write
jobs:
  release-please:
    runs-on: ubuntu-latest
    steps:
      - uses: googleapis/release-please-action@v5
        with:
          config-file: release-please-config.json
          manifest-file: .release-please-manifest.json
```

- [ ] **Step 4: SKILL.md 버전 줄에 표시를 붙인다**

`skills/simple-korean/SKILL.md` 12번째 줄을 바꾼다.

전:
```yaml
  version: "1.0.0"
```
후:
```yaml
  version: "1.0.0" # x-release-please-version
```

- [ ] **Step 5: 버전 대조 대상을 바꾼다**

`evals/check_numbers.py` 14번째 줄(독스트링)을 바꾼다.

```python
- 버전 문자열이 SKILL.md, 플러그인 매니페스트 세 개, .release-please-manifest.json, CHANGELOG 첫 항목에서 같은지 본다.
```

`VERSION_PATTERNS`를 통째로 바꾼다.

```python
VERSION_PATTERNS = {
    "skills/simple-korean/SKILL.md": r'version:\s*"([^"]+)"',
    ".claude-plugin/plugin.json": r'"version":\s*"([^"]+)"',
    ".claude-plugin/marketplace.json": r'"version":\s*"([^"]+)"',
    ".codex-plugin/plugin.json": r'"version":\s*"([^"]+)"',
    ".release-please-manifest.json": r'"\."\s*:\s*"([^"]+)"',
    "CHANGELOG.md": r"(?m)^## \[?([0-9]+\.[0-9]+\.[0-9]+)",
}
```

- [ ] **Step 6: 시험과 검증을 돌린다**

Run: `python3 evals/tests/run.py evals/tests/test_check_numbers.py`
Expected: `FAIL` 없음.

Run: `.venv/bin/python evals/check_numbers.py && actionlint .github/workflows/release.yml && claude plugin validate skills --strict && python3 evals/ko_lint.py --gate=warning skills/simple-korean/SKILL.md >/dev/null && echo OK`
Expected: `check_numbers OK: ...`, `✔ Validation passed`, `OK`.

- [ ] **Step 7: 커밋한다**

```bash
git add release-please-config.json .release-please-manifest.json .github/workflows/release.yml skills/simple-korean/SKILL.md evals/check_numbers.py evals/tests/test_check_numbers.py
git commit -F - <<'EOF'
ci: release-please 설정을 더하고 버전 대조 대상을 맞춘다

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01SanRSLxxVtkLMJh1wLGeGZ
EOF
```

### Task 2: 아직 릴리스하지 않은 측정은 CHANGELOG 검사를 건너뛴다

**Files:**
- Modify: `evals/check_numbers.py:8-15,51-75,85-97`, `evals/calibration/hits.py:172`
- Test: `evals/tests/test_check_numbers.py:84-121`

**Interfaces:**
- Consumes: Task 1의 `VERSION_PATTERNS`.
- Produces: `check_numbers.CHANGELOG_ENTRY`, `check_numbers.RECORD_DATE`(정규식), `check_numbers.latest_release_date(changelog: str) -> str 또는 None`(`YYYY-MM-DD`), `check_numbers.unreleased(date: str, changelog: str) -> bool`.

- [ ] **Step 1: 실패하는 시험을 쓴다**

`test_check_calibration_rebuilds_record_and_needs_changelog_lines`를 도우미 `_calibration`과 함께 바꾸고, 새 시험 넷을 더한다.

```python
def test_latest_release_date_reads_the_first_entry_in_either_form():
    old = "# 변경 기록\n\n항목마다 적습니다.\n\n## 1.0.0, 2026-10-10\n\n- 처음\n\n### 보정\n\n- 줄\n"
    assert cn.latest_release_date(old) == "2026-10-10"
    new = old.replace("## 1.0.0, 2026-10-10", "## [1.1.0](https://github.com/say8425/SimpleKorean/compare/v1.0.0...v1.1.0)"
                      " (2026-11-20)\n\n### 기능\n\n* 더한다 ([#4](https://github.com/say8425/SimpleKorean/issues/4))\n\n"
                      "## 1.0.0, 2026-10-10")
    assert cn.latest_release_date(new) == "2026-11-20"
    assert cn.latest_release_date("# 변경 기록\n") is None


def test_unreleased_means_strictly_after_the_latest_release():
    changelog = "# 변경 기록\n\n## 1.0.0, 2026-10-10\n"
    assert cn.unreleased("2026-10-11", changelog)
    assert not cn.unreleased("2026-10-10", changelog)
    assert not cn.unreleased("2026-10-08", changelog)
    assert not cn.unreleased("2026-10-11", "# 변경 기록\n")


def test_check_benchmark_skips_the_changelog_path_for_unreleased_results():
    scenarios = [{"id": "readme-intro", "type": "descriptive"}]
    with tempfile.TemporaryDirectory(dir=str(cn.ROOT / "evals")) as d:
        root = _results(d)
        readme = report.replace_readme_block("문서와 답변은 `m`이 쓰고 판정은 `j`가 했습니다.\n"
                                             "<!-- benchmark:start x -->\n\n<!-- benchmark:end -->\n", root,
                                             report.readme_block(root, scenarios))
        (root / "RESULTS.md").write_text(report.results_md(root, scenarios), encoding="utf-8")
        same_day = "# 변경 기록\n\n## 1.0.0, 2099-01-01\n"
        earlier = "# 변경 기록\n\n## 1.0.0, 2098-12-31\n"
        found = cn.check_benchmark(readme, same_day, scenarios, require_easy=False)
        assert any("CHANGELOG.md가 측정 결과" in p and "릴리스 항목" in p for p in found)
        assert cn.check_benchmark(readme, earlier, scenarios, require_easy=False) == []


def _calibration(d, date="2026-10-09"):
    """임시 보정 디렉터리에 기준선 문서 하나, hits.tsv, RECORD.md를 쓰고 (디렉터리, RECORD.md 본문)을 돌려준다."""
    cal, base = Path(d), Path(d) / "baseline"
    (base / "docs").mkdir(parents=True)
    (base / "reply").mkdir()
    record = {"text": "이 문서는 sqlpipe에 대해 설명합니다.\n", "condition": "baseline", "scenario": "x",
              "type": "descriptive", "run": 1}
    (base / "docs" / "baseline__x__r1.json").write_text(json.dumps(record, ensure_ascii=False), encoding="utf-8")
    (base / "meta.json").write_text(json.dumps({"date": date, "model": "m", "effort": "low"}), encoding="utf-8")
    rows = [{**r, "label": "TP"} for r in hits.doc_rows(base) + hits.reply_rows(base)]
    (cal / "hits.tsv").write_text(hits.to_tsv(rows), encoding="utf-8")
    text = hits.record_md(base, rows)
    (cal / "RECORD.md").write_text(text, encoding="utf-8")
    return cal, text


def test_check_calibration_rebuilds_record_and_needs_changelog_lines():
    with tempfile.TemporaryDirectory() as d:
        cal, text = _calibration(d)
        lines = text.split("## CHANGELOG에 옮길 줄", 1)[1].strip()
        assert cn.check_calibration(lines, cal) == []
        assert any("CHANGELOG.md에 보정 줄이 없습니다" in p for p in cn.check_calibration("", cal))
        (cal / "RECORD.md").write_text(text.replace("그대로입니다", "바뀌었습니다"), encoding="utf-8")
        assert any(p.startswith("evals/calibration/RECORD.md:") for p in cn.check_calibration(lines, cal))


def test_check_calibration_skips_changelog_lines_for_an_unreleased_record():
    with tempfile.TemporaryDirectory() as d:
        cal, _ = _calibration(d, date="2026-10-09")
        found = cn.check_calibration("# 변경 기록\n\n## 1.0.0, 2026-10-09\n", cal)
        assert any("CHANGELOG.md에 보정 줄이 없습니다" in p for p in found)
        assert cn.check_calibration("# 변경 기록\n\n## 1.0.0, 2026-10-08\n", cal) == []
```

- [ ] **Step 2: 시험이 실패하는지 본다**

Run: `python3 evals/tests/run.py evals/tests/test_check_numbers.py`
Expected: 새 시험 넷이 `AttributeError: module 'check_numbers' has no attribute 'latest_release_date'`와 메시지 불일치로 `FAIL`한다.

- [ ] **Step 3: 날짜 도우미를 더한다**

`evals/check_numbers.py`에서 `VERSION_PATTERNS` 바로 아래에 정규식 둘을 더한다.

```python
CHANGELOG_ENTRY = re.compile(r"(?m)^## \[?[0-9]+\.[0-9]+\.[0-9]+\]?.*?([0-9]{4}-[0-9]{2}-[0-9]{2})")
RECORD_DATE = re.compile(r"\A# 보정 기록 \(([0-9]{4}-[0-9]{2}-[0-9]{2})\)")
```

`_diff` 함수 아래에 두 함수를 더한다.

```python
def latest_release_date(changelog):
    """CHANGELOG 첫 항목의 날짜(YYYY-MM-DD). 옛 형식과 release-please 형식을 모두 읽고, 항목이 없으면 None이다."""
    m = CHANGELOG_ENTRY.search(changelog)
    return m.group(1) if m else None


def unreleased(date, changelog):
    """측정 날짜가 마지막 릴리스 날짜보다 늦으면 참이다. 같은 날이면 릴리스한 측정으로 본다."""
    latest = latest_release_date(changelog)
    return latest is not None and date > latest
```

- [ ] **Step 4: 두 검사에 규칙을 넣는다**

`check_benchmark`의 마지막 검사 두 줄을 바꾼다.

전:
```python
    if rel not in changelog:
        problems.append(f"CHANGELOG.md가 측정 결과 {rel}을 가리키지 않습니다")
```
후:
```python
    if rel not in changelog and not unreleased(meta["date"], changelog):
        problems.append(f"CHANGELOG.md가 측정 결과 {rel}을 가리키지 않습니다. 이 결과를 싣는 릴리스 항목에 경로를 적으세요")
```

`check_calibration`을 통째로 바꾼다.

```python
def check_calibration(changelog, calibration=CALIBRATION):
    """RECORD.md를 다시 만들어 비교하고, 'CHANGELOG에 옮길 줄'이 CHANGELOG에 있는지 본다.

    마지막 릴리스보다 늦은 보정은 아직 실을 릴리스 항목이 없으므로 CHANGELOG를 보지 않는다.
    """
    try:
        rebuilt = hits.record_md(Path(calibration) / "baseline", hits.read_tsv(Path(calibration) / "hits.tsv"))
    except SystemExit as err:
        return [f"보정 기록을 다시 만들지 못했습니다: {err}"]
    current = (Path(calibration) / "RECORD.md").read_text(encoding="utf-8")
    problems = [] if current == rebuilt else [_diff("evals/calibration/RECORD.md", rebuilt, current)]
    date = RECORD_DATE.search(rebuilt)
    if date and unreleased(date.group(1), changelog):
        return problems
    for line in rebuilt.split("## CHANGELOG에 옮길 줄", 1)[1].strip().splitlines():
        text = line.lstrip("- ").strip()
        if text and text not in changelog:
            problems.append(f"CHANGELOG.md에 보정 줄이 없습니다: {text}")
    return problems
```

모듈 독스트링의 검사 목록(8-15번째 줄)을 바꾼다.

```python
검사하는 것:
- README의 벤치마크 블록과 RESULTS.md를 원본 출력에서 다시 만든 글과 비교한다(report.py).
- README와 examples/before-after.md의 인용 블록을 원본 출력과 비교한다(make_examples.py).
- 보정 기록 RECORD.md를 hits.tsv와 보정 출력에서 다시 만들어 비교한다.
- 측정 결과 경로와 보정 줄이 CHANGELOG에 있는지 본다. 마지막 릴리스보다 늦은 측정과 보정은 건너뛴다.
- 규칙 블록 두 벌이 같은지, 핵심 문구가 SKILL.md와 규칙 블록에 모두 있는지 본다.
- SKILL.md description에 스펙 10절의 호출 문구가 모두 있는지 본다.
- 버전 문자열이 SKILL.md, 플러그인 매니페스트 세 개, .release-please-manifest.json, CHANGELOG 첫 항목에서 같은지 본다.
```

`evals/calibration/hits.py` 172번째 줄의 독스트링을 바꾼다.

```python
    """그 보정을 싣는 릴리스 항목의 보정 절에 그대로 옮길 줄."""
```

- [ ] **Step 5: 시험과 검증을 돌린다**

Run: `python3 evals/tests/run.py && .venv/bin/python evals/check_numbers.py`
Expected: `FAIL` 없음, `check_numbers OK`. 지금 결과와 보정은 2026-10-08이고 1.0.0은 2026-10-10이라 두 검사가 그대로 돈다.

- [ ] **Step 6: 커밋한다**

```bash
git add evals/check_numbers.py evals/calibration/hits.py evals/tests/test_check_numbers.py
git commit -F - <<'EOF'
ci: 아직 릴리스하지 않은 측정은 CHANGELOG 검사에서 뺀다

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01SanRSLxxVtkLMJh1wLGeGZ
EOF
```

### Task 3: PR 제목 검사

**Files:**
- Create: `evals/check_pr_title.py`, `.github/workflows/pr-title.yml`
- Test: `evals/tests/test_check_pr_title.py`

**Interfaces:**
- Consumes: `ko_lint.lint_detail(text, config={})`(항목: category, severity, line, text), `ko_lint.LABELS`, `ko_text.register(sentence) -> "haera" | "hapsyo" | ... | None`, Task 1의 `release-please-config.json`.
- Produces: `check_pr_title.TYPES`(튜플), `check_pr_title.problems(title: str) -> list[str]`, `check_pr_title.main() -> int`(환경 변수 `PR_TITLE`을 읽는다).

- [ ] **Step 1: 실패하는 시험을 쓴다**

`evals/tests/test_check_pr_title.py`:

```python
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import check_pr_title as pt  # noqa: E402


def test_good_titles_pass():
    for title in ("fix: 설정 파일의 지정형을 20자로 제한한다",
                  "ci: release-please로 릴리스 PR을 만든다",
                  "docs: README를 영어, 일본어, 중국어, 스페인어로 옮긴다",
                  "feat: `ko_lint`가 BOM 뒤의 frontmatter를 건너뛴다."):
        assert pt.problems(title) == [], title


def test_format_errors_name_the_rule():
    for title in ("", "설정 파일을 고친다", "fix(hooks): 훅을 고친다", "feat!: 규칙을 바꾼다",
                  "fix：전각 콜론을 쓴다", "fix:  공백이 둘이다", "Fix: 대문자 유형을 쓴다", "style: 서식을 고친다"):
        found = pt.problems(title)
        assert len(found) == 1 and "'<유형>: <내용>'" in found[0], title


def test_content_must_be_haera():
    assert any("해라체" in p for p in pt.problems("fix: 설정 파일의 지정형을 20자로 제한합니다"))
    assert any("해라체" in p for p in pt.problems("docs: README 번역 추가"))


def test_content_must_pass_the_linter():
    assert any(p.startswith("린터 ") and "메세지" in p for p in pt.problems("fix: 메세지 처리를 고친다"))


def test_changelog_sections_cover_the_title_types():
    config = json.loads((pt.ROOT / "release-please-config.json").read_text(encoding="utf-8"))
    sections = {s["type"]: s for s in config["changelog-sections"]}
    assert set(sections) == set(pt.TYPES)
    assert {t for t, s in sections.items() if not s.get("hidden")} == {"feat", "fix", "perf"}


def test_main_reads_the_title_from_the_environment():
    old = os.environ.get("PR_TITLE")
    try:
        os.environ["PR_TITLE"] = "fix: 설정 파일의 지정형을 20자로 제한한다"
        assert pt.main() == 0
        os.environ["PR_TITLE"] = "fix: 고쳤습니다"
        assert pt.main() == 1
        del os.environ["PR_TITLE"]
        assert pt.main() == 1
    finally:
        if old is None:
            os.environ.pop("PR_TITLE", None)
        else:
            os.environ["PR_TITLE"] = old
```

- [ ] **Step 2: 시험이 실패하는지 본다**

Run: `python3 evals/tests/run.py evals/tests/test_check_pr_title.py`
Expected: `ModuleNotFoundError: No module named 'check_pr_title'`.

- [ ] **Step 3: 스크립트를 쓴다**

`evals/check_pr_title.py`:

```python
#!/usr/bin/env python3
"""PR 제목이 커밋 규칙을 지키는지 본다. squash 병합에서는 PR 제목이 main의 커밋 제목과 CHANGELOG의 한 줄이 된다.

    PR_TITLE='fix: 설정 파일의 지정형을 20자로 제한한다' python3 evals/check_pr_title.py

규칙: '<유형>: <한국어 해라체 문장>'. 유형은 TYPES 가운데 하나이고, 범위와 '!'는 쓰지 않는다.
내용은 린터 관문(--gate=warning)을 통과해야 한다. 제목은 외부 입력이므로 환경 변수로만 받는다.
"""
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import ko_lint  # noqa: E402
import ko_text  # noqa: E402

TYPES = ("feat", "fix", "perf", "refactor", "docs", "test", "chore", "ci")
TITLE = re.compile(r"(" + "|".join(TYPES) + r"): (\S.*)")
EXAMPLE = "fix: 설정 파일의 지정형을 20자로 제한한다"


def problems(title):
    """제목의 문제 목록. 비어 있으면 통과다."""
    m = TITLE.fullmatch(title)
    if not m:
        return [f"제목은 '<유형>: <내용>' 형식이어야 합니다. 유형은 {', '.join(TYPES)} 가운데 하나입니다. 예: {EXAMPLE}"]
    content = m.group(2)
    found = []
    if ko_text.register(content) != "haera":
        found.append(f"내용을 해라체 문장으로 쓰세요(예: 고친다, 더한다, 바꾼다): {content}")
    for hit in ko_lint.lint_detail(content, config={}):
        found.append(f"린터 {ko_lint.LABELS.get(hit['category'], hit['category'])}: {hit['text']}")
    return found


def main():
    title = os.environ.get("PR_TITLE", "")
    found = problems(title)
    if found:
        print(f"PR 제목이 규칙에 맞지 않습니다: {title}")
        for problem in found:
            print(" -", problem)
        return 1
    print(f"PR 제목 OK: {title}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: 워크플로를 쓴다**

`.github/workflows/pr-title.yml`:

```yaml
name: pr-title
on:
  pull_request:
    types: [opened, edited, synchronize, reopened]
permissions:
  contents: read
jobs:
  title:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - uses: actions/setup-python@v7
        with: { python-version: "3.12" }
      - run: python3 evals/check_pr_title.py
        env:
          PR_TITLE: ${{ github.event.pull_request.title }}
```

- [ ] **Step 5: 시험과 검증을 돌린다**

Run: `python3 evals/tests/run.py && actionlint .github/workflows/pr-title.yml && PR_TITLE='ci: release-please로 릴리스 PR을 만든다' python3 evals/check_pr_title.py`
Expected: `FAIL` 없음, actionlint 출력 없음, `PR 제목 OK: ci: release-please로 릴리스 PR을 만든다`.

Run: `PR_TITLE='docs: README 번역 추가' python3 evals/check_pr_title.py; echo "exit=$?"`
Expected: 해라체 안내 한 줄과 `exit=1`.

- [ ] **Step 6: 커밋한다**

```bash
git add evals/check_pr_title.py evals/tests/test_check_pr_title.py .github/workflows/pr-title.yml
git commit -F - <<'EOF'
ci: PR 제목이 커밋 규칙을 지키는지 검사한다

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01SanRSLxxVtkLMJh1wLGeGZ
EOF
```

### Task 4: 한국어 README의 배지와 기여 절, CHANGELOG 머리말

**Files:**
- Modify: `README.md:7`, `README.md:266`, `CHANGELOG.md:3`

**Interfaces:**
- Consumes: Task 1의 버전 대조(README 배지를 보지 않는다), Task 3의 제목 규칙.
- Produces: 동적 배지 줄(PR 3의 번역판이 그대로 옮긴다), 기여 절의 PR 제목 문단(PR 3이 번역한다).

- [ ] **Step 1: 배지를 바꾼다**

`README.md` 7번째 줄.

전:
```html
  <a href="skills/simple-korean/SKILL.md"><img src="https://img.shields.io/badge/version-1.0.0-blue?style=flat" alt="version 1.0.0"></a>
```
후:
```html
  <a href="https://github.com/say8425/SimpleKorean/releases/latest"><img src="https://img.shields.io/github/v/release/say8425/SimpleKorean?label=version&style=flat" alt="version"></a>
```

- [ ] **Step 2: 기여 절에 PR 제목 규칙을 더한다**

`README.md` 기여 절의 마지막 문단("올리기 전에 ...를 돌리세요.") 뒤에 빈 줄과 이 문단을 더한다.

```markdown
PR 제목은 `fix: 설정 파일의 지정형을 20자로 제한한다`처럼 `<유형>: <해라체 문장>`으로 쓰세요. 유형은 feat, fix, perf, refactor, docs, test, chore, ci 가운데 하나입니다. 병합하면 PR 제목이 그대로 변경 기록의 한 줄이 됩니다. feat, fix, perf만 새 릴리스를 만듭니다.
```

- [ ] **Step 3: CHANGELOG 머리말을 바꾼다**

`CHANGELOG.md` 3번째 줄.

전:
```markdown
항목마다 버전, 날짜, 측정한 효과를 적습니다.
```
후:
```markdown
항목마다 버전, 날짜, 바뀐 것을 적습니다. 측정 결과가 바뀌면 그 릴리스에 결과 경로를 적습니다.
```

- [ ] **Step 4: 전체 확인을 돌린다**

Run: "작업 환경"의 전체 확인 명령, 그리고 `grep -c "badge/version-" README.md`
Expected: 모두 0으로 끝나고, grep은 `0`을 출력한다. 위 두 문단은 계획을 쓸 때 린터로 돌려 경고 0개를 확인했다.

- [ ] **Step 5: 커밋한다**

```bash
git add README.md CHANGELOG.md
git commit -F - <<'EOF'
docs: 버전 배지를 릴리스에서 읽고 PR 제목 규칙을 적는다

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01SanRSLxxVtkLMJh1wLGeGZ
EOF
```

### Task 5: 릴리스 PR 미리 보기와 스킬 로더 확인

이 작업은 코드를 바꾸지 않는다. 결과는 Task 6의 PR 본문에 적는다.

**Files:** 없음(임시 브랜치 `tmp/release-dry-run`과 임시 폴더만 쓴다)

**Interfaces:**
- Consumes: Task 1-4의 커밋이 있는 `ci/release-please` 브랜치.
- Produces: `.superpowers/readme-languages/dry-run.txt`, `.superpowers/readme-languages/release.patch`, 확인 결과 메모 `.superpowers/readme-languages/verify.md`.

- [ ] **Step 1: 임시 브랜치에 빈 fix 커밋을 얹어 올린다**

숨긴 유형(ci, docs)만 있으면 release-please는 릴리스 PR을 만들지 않는다. 그래서 빈 `fix:` 커밋을 하나 얹는다.

```bash
S=$(mktemp -d) && N=.superpowers/readme-languages && mkdir -p "$N"
git switch -c tmp/release-dry-run
git commit --allow-empty -q -m "fix: 릴리스 PR 모양을 미리 본다"
git push -q -u origin tmp/release-dry-run
```

- [ ] **Step 2: release-please CLI를 임시 폴더에 설치한다**

```bash
(cd "$S" && echo '{"name":"rp","private":true}' > package.json && pnpm add release-please@17.11.2)
```
Expected: `+ release-please 17.11.2`.

- [ ] **Step 3: dry-run으로 릴리스 PR과 파일 diff를 본다**

`--trace`가 있으면 CLI가 파일마다 실제 diff를 출력한다.

```bash
node "$S/node_modules/release-please/build/src/bin/release-please.js" release-pr \
  --token="$(gh auth token)" --repo-url=say8425/SimpleKorean --target-branch=tmp/release-dry-run \
  --config-file=release-please-config.json --manifest-file=.release-please-manifest.json \
  --dry-run --trace > "$N/dry-run.txt" 2> "$S/dry-run.log"
grep -E "^Would open|^title:|^updates:|^  \S+: " "$N/dry-run.txt"
```

Expected:
- `Would open 1 pull requests`
- `title:` 줄이 `release 1.0.1`로 끝난다.
- 업데이트 목록에 `CHANGELOG.md`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `.codex-plugin/plugin.json`, `skills/simple-korean/SKILL.md`, `.release-please-manifest.json`이 있다.
- `body:`에 `## [1.0.1](https://github.com/say8425/SimpleKorean/compare/v1.0.0...v1.0.1)`, `### 고친 것`, `* 릴리스 PR 모양을 미리 본다`가 있다.

body에 2026-10-10 이전 커밋(영어 제목의 feat·fix)이 보이면, release-please가 태그만으로는 `v1.0.0`을 찾지 못한 것이다. 이것을 `$N/verify.md`에 적는다. Task 6의 `v1.0.0` Release를 만든 뒤 이 단계를 다시 돌려서, 그때는 빈 fix 커밋 하나만 보이는지 확인한다.

- [ ] **Step 4: diff를 레포 사본에 적용한다**

```bash
python3 - "$N/dry-run.txt" > "$N/release.patch" <<'EOF'
import re
import sys
out = open(sys.argv[1], encoding="utf-8").read()
print("".join(m.group(0) for m in re.finditer(r"(?ms)^Index: \S+\n.*?(?=^Index: |^  \S+: |\Z)", out)), end="")
EOF
mkdir "$S/orig" "$S/copy"
git archive tmp/release-dry-run | tar -x -C "$S/orig"
git archive tmp/release-dry-run | tar -x -C "$S/copy"
patch -p0 -d "$S/copy" < "$N/release.patch"
diff -ru "$S/orig" "$S/copy"
grep -c "^Index: version.txt" "$N/release.patch"
```

Expected:
- `patch`가 오류 없이 끝난다.
- `diff` 출력에서 JSON 세 파일과 SKILL.md는 버전 줄 하나씩만 바뀐다. 한국어 설명은 그대로다.
- `.release-please-manifest.json`이 `1.0.1`이 된다.
- CHANGELOG의 새 항목이 머리말 뒤, `## 1.0.0, 2026-10-10` 앞에 들어간다.
- 마지막 grep은 `0`을 출력한다(`version.txt`를 만들지 않는다).

- [ ] **Step 5: 바뀐 사본이 검사를 통과하는지 본다**

```bash
REPO="$PWD"
(cd "$S/copy" && "$REPO/.venv/bin/python" evals/check_numbers.py && python3 evals/ko_lint.py --gate=warning CHANGELOG.md > /dev/null && echo "gate OK")
```
Expected: `check_numbers OK`와 `gate OK`.

- [ ] **Step 6: 세 스킬 로더가 SKILL.md를 읽는지 본다**

```bash
claude plugin validate skills --strict
CODEX_HOME="$S/codex-home" && mkdir -p "$CODEX_HOME" && export CODEX_HOME
codex plugin marketplace add "$PWD" && codex plugin add simple-korean@simple-korean
codex debug prompt-input | grep -c "simple-korean:simple-korean: 기술 문서와"
unset CODEX_HOME
(cd "$S" && pnpm dlx skills add "$OLDPWD" --list) | grep -c "simple-korean"
```
Expected: Claude Code는 `✔ Validation passed`를 출력한다. Codex의 grep은 1 이상이다(격리한 `CODEX_HOME`에 설치했으므로 사용자 설정은 그대로다). skills CLI의 grep은 1 이상이다.

- [ ] **Step 7: 결과를 적고 임시 브랜치를 지운다**

`$N/verify.md`에 Step 3-6의 결과(Expected와 다른 점이 있으면 그 내용)를 적는다. 그다음 임시 브랜치를 지운다.

```bash
git switch ci/release-please
git push -q origin --delete tmp/release-dry-run
git branch -D tmp/release-dry-run
```

### Task 6: PR 2를 열고, 레포 작업과 병합을 확인받는다

**Files:** 없음(GitHub 작업)

**Interfaces:**
- Consumes: Task 1-5의 결과, `.superpowers/readme-languages/verify.md`.
- Produces: 병합한 PR 2, `v1.0.0` GitHub Release, Actions PR 권한, squash 병합 설정.

- [ ] **Step 1: 커밋할 문서에 로컬 경로가 없는지 본다**

```bash
grep -nE "/Use[r]s/|/priva[t]e/|/hom[e]/" docs/superpowers/specs/2026-10-14-readme-languages-design.md docs/superpowers/plans/2026-10-16-readme-languages.md || echo "로컬 경로 없음"
```
Expected: `로컬 경로 없음`.

- [ ] **Step 2: 전체 확인을 돌리고 브랜치를 올린다**

Run: 전체 확인. Expected: 모두 통과.

```bash
git push -u origin ci/release-please
```

- [ ] **Step 3: PR을 연다**

`S=${S:-$(mktemp -d)}`로 임시 폴더를 정하고, 본문 파일 `$S/pr2-body.md`를 이 틀로 쓴다. `<...>` 자리는 `.superpowers/readme-languages/verify.md`의 실제 결과로 채운다.

~~~markdown
## 바뀌는 것

- release-please로 릴리스를 자동화합니다. `main`에 `feat`, `fix`, `perf` 커밋이 들어가면 릴리스 PR이 열리고, 병합하면 버전 문자열, CHANGELOG, 태그, GitHub Release가 함께 바뀝니다.
- README의 버전 배지를 GitHub Release를 읽는 동적 배지로 바꿉니다.
- 새 워크플로 `pr-title`이 PR 제목을 `<유형>: <해라체 문장>` 규칙과 문서 관문으로 검사합니다.
- 다시 잰 결과와 보정 기록은 마지막 릴리스보다 늦으면 CHANGELOG 검사를 건너뜁니다.
- 설계와 구현 계획: `docs/superpowers/specs/2026-10-14-readme-languages-design.md`, `docs/superpowers/plans/2026-10-16-readme-languages.md`

## 확인한 것

- release-please 17.11.2 dry-run(임시 브랜치에 빈 `fix:` 커밋): <제목, 새 항목 제목, 절 이름>
- diff를 사본에 적용: JSON 세 파일과 SKILL.md는 버전 줄만 바뀌고, 새 항목은 1.0.0 항목 앞에 들어가고, `version.txt`는 생기지 않습니다. 사본에서 `check_numbers`와 문서 관문이 통과합니다.
- 스킬 로더: `claude plugin validate skills --strict` 통과, Codex `debug prompt-input`에 스킬 설명이 뜸, skills CLI `--list`에 스킬이 뜸.

## 병합 전에 할 일(확인 뒤)

1. `v1.0.0` GitHub Release를 만듭니다.
2. Actions가 PR을 만들 수 있게 합니다.
3. 병합 방식을 squash만으로 정하고, 커밋 제목은 PR 제목으로 합니다.

## 시험 계획

- [ ] `check`, `python39`, `pr-title`이 통과합니다.
- [ ] 병합 뒤 `release` 워크플로가 성공하고, 사용자에게 보이는 커밋이 없어 릴리스 PR을 만들지 않습니다.
- [ ] 배지가 v1.0.0을 보입니다.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01SanRSLxxVtkLMJh1wLGeGZ
~~~

```bash
gh pr create --base main --head ci/release-please --title "ci: release-please로 릴리스 PR을 만든다" --body-file "$S/pr2-body.md"
```

- [ ] **Step 4: CI를 기다리고 코드 리뷰를 받는다**

```bash
gh pr checks --watch --interval 20
```
Expected: `check`, `python39`, `pr-title`이 모두 `pass`. 그다음 `superpowers:requesting-code-review` 스킬로 PR을 리뷰한다. Critical과 Important 지적은 고치고 다시 올린다.

- [ ] **Step 5: 사용자에게 보고하고 확인을 받는다**

PR 링크, CI 결과, 리뷰 결과, Task 5의 결과를 보고한다. 아래 세 가지 레포 작업과 병합을 해도 되는지 묻고, 답을 기다린다.

- [ ] **Step 6: 확인을 받은 뒤 `v1.0.0` Release를 만든다**

```bash
S=${S:-$(mktemp -d)}
python3 - > "$S/v1.0.0-notes.md" <<'EOF'
import re
from pathlib import Path
text = Path("CHANGELOG.md").read_text(encoding="utf-8")
entry = text.split("## 1.0.0, 2026-10-10\n", 1)[1].strip()
base = "https://github.com/say8425/SimpleKorean/blob/v1.0.0/"
print(re.sub(r"\]\((?!https?://)([^)]+)\)", lambda m: f"]({base}{m.group(1)})", entry))
EOF
gh release create v1.0.0 --verify-tag --title v1.0.0 --notes-file "$S/v1.0.0-notes.md" --latest
gh release view v1.0.0 --json tagName,name,isLatest
```
Expected: `{"isLatest":true,"name":"v1.0.0","tagName":"v1.0.0"}`. Task 5 Step 3에서 태그를 못 찾았다고 적었다면, 지금 Task 5 Step 1-3을 다시 돌려 빈 fix 커밋 하나만 보이는지 확인하고 임시 브랜치를 지운다.

- [ ] **Step 7: Actions 권한과 병합 방식을 바꾼다**

```bash
gh api -X PUT repos/say8425/SimpleKorean/actions/permissions/workflow -f default_workflow_permissions=read -F can_approve_pull_request_reviews=true
gh api repos/say8425/SimpleKorean/actions/permissions/workflow
gh api -X PATCH repos/say8425/SimpleKorean -F allow_squash_merge=true -F allow_merge_commit=false -F allow_rebase_merge=false \
  -f squash_merge_commit_title=PR_TITLE -f squash_merge_commit_message=COMMIT_MESSAGES \
  --jq '{allow_squash_merge, allow_merge_commit, allow_rebase_merge, squash_merge_commit_title, squash_merge_commit_message}'
```
Expected: `{"default_workflow_permissions":"read","can_approve_pull_request_reviews":true}`와 `{"allow_merge_commit":false,"allow_rebase_merge":false,"allow_squash_merge":true,"squash_merge_commit_message":"COMMIT_MESSAGES","squash_merge_commit_title":"PR_TITLE"}`.

- [ ] **Step 8: 병합하고 결과를 본다**

```bash
gh pr merge ci/release-please --squash --delete-branch
sleep 20
RID=$(gh run list --workflow release.yml --branch main --limit 1 --json databaseId -q '.[0].databaseId')
gh run watch "$RID" --exit-status
gh run view "$RID" --log | grep -iE "no user facing commits|would open|release" | head -5
curl -s "https://img.shields.io/github/v/release/say8425/SimpleKorean?label=version" | grep -o "v1\.0\.0" | head -1
```
Expected: 워크플로가 성공한다. 로그에 사용자에게 보이는 커밋이 없어 건너뛰었다는 줄(`No user facing commits found`)이 있다. 배지 grep이 `v1.0.0`을 출력한다. `main`의 `check`와 `python39`도 통과한다.

---

## Part B — PR 3: README 다국어판

시작하기 전에 PR 2를 병합한 `main`에서 브랜치를 만든다.

```bash
git fetch -q origin && git switch -c docs/readme-languages origin/main
```

### Task 7: 언어 표 `evals/readme_i18n.py`

**Files:**
- Create: `evals/readme_i18n.py`
- Test: `evals/tests/test_readme_i18n.py`

**Interfaces:**
- Produces:
  - `LANGS = ("ko", "en", "ja", "zh", "es")`, `README: dict[str, str]`(레포 기준 경로), `NAMES: dict[str, str]`, `NBSP = " "`
  - `TEXT[lang]`의 키: `reply_intro`(`questions`, `runs`, `total`), `headline`(`cut`, `base`, `plain`, `n`, `wins`, `ties`, `losses`), `reply_header`, `doc_intro`(`tasks`, `runs`), `doc_header`, `longest`(`n`), `not_measured`, `results_link`(`rel`, `href`), `labels`(키 `baseline`, `reply_plain`, `plain`, `strict`), `example_before`(`path`), `example_after`(`path`), `example_docs`(`href`), `block_size`(`n`)
  - `prefix(lang) -> str`, `link(lang, rel) -> str`, `readme_link(src, dst) -> str`, `language_line(lang) -> str`, `grouped(n: int, lang) -> str`, `percent(number, lang) -> str`

- [ ] **Step 1: 실패하는 시험을 쓴다**

`evals/tests/test_readme_i18n.py`:

```python
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE.parent))
import make_examples as mx  # noqa: E402
import readme_i18n as i18n  # noqa: E402
import report  # noqa: E402


def test_every_language_has_every_template():
    keys = set(i18n.TEXT["ko"])
    for lang in i18n.LANGS:
        assert set(i18n.TEXT[lang]) == keys, lang
        assert set(i18n.TEXT[lang]["labels"]) == {"baseline", "reply_plain", "plain", "strict"}, lang
    assert set(i18n.README) == set(i18n.NAMES) == set(i18n.LANGS)


def test_korean_templates_keep_the_current_sentences():
    ko = i18n.TEXT["ko"]
    assert ko["block_size"].format(n=i18n.grouped(2271, "ko")) == "규칙 블록 2,271자"
    assert ko["longest"].format(n=18) == "18어절"
    assert ko["example_docs"].format(href="examples/before-after.md") == \
        "문서 예시는 [`examples/before-after.md`](examples/before-after.md)에 있습니다."


def test_numbers_follow_each_language():
    assert [i18n.grouped(2271, lang) for lang in i18n.LANGS] == ["2,271", "2,271", "2,271", "2,271", "2271"]
    assert i18n.grouped(12345, "es") == "12 345" and i18n.grouped(12345, "en") == "12,345"
    assert i18n.grouped(999, "es") == "999"
    assert i18n.percent("95.0", "ko") == "95.0%" and i18n.percent("95.0", "es") == "95.0 %"
    assert i18n.percent(100, "zh") == "100%"


def test_language_line_links_every_other_language():
    assert i18n.language_line("ko") == (
        '<p align="center">\n  한국어 | <a href="docs/README.en.md">English</a> | '
        '<a href="docs/README.ja.md">日本語</a> | <a href="docs/README.zh.md">中文</a> | '
        '<a href="docs/README.es.md">Español</a>\n</p>')
    en = i18n.language_line("en")
    assert '<a href="../README.md">한국어</a> | English | <a href="README.ja.md">日本語</a>' in en
    assert ">English</a>" not in en


def test_links_get_the_language_prefix():
    assert i18n.link("ko", "examples/before-after.md") == "examples/before-after.md"
    assert i18n.link("ja", "examples/before-after.md") == "../examples/before-after.md"
```

- [ ] **Step 2: 시험이 실패하는지 본다**

Run: `python3 evals/tests/run.py evals/tests/test_readme_i18n.py`
Expected: `ModuleNotFoundError: No module named 'readme_i18n'`.

- [ ] **Step 3: 모듈을 쓴다**

`evals/readme_i18n.py`:

```python
"""README 다섯 언어판의 언어 표와 생성 블록의 문장 틀.

report.py와 make_examples.py는 이 틀로 언어마다 블록을 만들고, check_numbers.py는 같은 틀로 대조한다.
한국어 틀은 두 생성기가 쓰던 문장 그대로라서 한국어 README의 블록은 바뀌지 않는다. 틀을 고치면
`report.py <결과 디렉터리> --readme`와 `make_examples.py <결과 디렉터리> --readme`로 README를 다시 쓴다.
"""

LANGS = ("ko", "en", "ja", "zh", "es")
README = {"ko": "README.md", "en": "docs/README.en.md", "ja": "docs/README.ja.md",
          "zh": "docs/README.zh.md", "es": "docs/README.es.md"}
NAMES = {"ko": "한국어", "en": "English", "ja": "日本語", "zh": "中文", "es": "Español"}
NBSP = " "

TEXT = {
    "ko": {
        "reply_intro": "답변: 전문용어가 하나씩 든 질문 {questions}개를 조건마다 {runs}번씩 물었습니다. 답변은 모두 {total}개입니다. ",
        "headline": ("스킬을 켜면 독자가 보는 결함(em-dash, 굵은 글씨, 헤더, 불릿)이 {cut} 줄었습니다({base}개에서 {plain}개). "
                     "블라인드 판정에서 SimpleKorean 답변은 {n}쌍 가운데 {wins}쌍에서 이겼고, "
                     "{ties}쌍에서 비겼고, {losses}쌍에서 졌습니다."),
        "reply_header": "| 조건 | 답변 수 | 평균 어절 | 평균 문장 | em-dash | 굵은 글씨 | 헤더 | 불릿 | 인사말과 맺음말 |",
        "doc_intro": ("문서: sqlpipe 문서 과제 {tasks}개를 조건마다 {runs}번씩 썼습니다. 비율은 린터가 센 수를 어절 수로 나눈 값입니다. "
                      "린터는 정규식 검사이므로 순위로 읽지 말고 방향으로 읽으세요."),
        "doc_header": "| 조건 | 문서 수 | 100어절당 오류 | 100어절당 경고 | 100어절당 번역투 | 지정 표기 비율 | 쉬운 단어 비율 | 가장 긴 문장 |",
        "longest": "{n}어절",
        "not_measured": "측정 안 함",
        "results_link": "원본 출력, 표기 분포, 측정 조건은 [`{rel}/RESULTS.md`]({href})에 있습니다.",
        "labels": {"baseline": "스킬 없음", "reply_plain": "SimpleKorean", "plain": "기본 모드", "strict": "엄격 모드"},
        "example_before": "스킬 없이 쓴 답변(`{path}`):",
        "example_after": "같은 모델이 SimpleKorean을 켜고 쓴 답변(`{path}`):",
        "example_docs": "문서 예시는 [`examples/before-after.md`]({href})에 있습니다.",
        "block_size": "규칙 블록 {n}자",
    },
    "en": {
        "reply_intro": ("Replies: we asked {questions} questions {runs} times in each condition. "
                        "Each question contains one technical term. There are {total} replies in total. "),
        "headline": ("With the skill on, reader-visible defects (em-dashes, bold text, headers, bullets) fell by {cut} "
                     "(from {base} to {plain}). In a blind judgment of {n} pairs, the SimpleKorean reply won {wins}, "
                     "tied {ties}, and lost {losses}."),
        "reply_header": ("| Condition | Replies | Mean eojeol | Mean sentences | em-dash | Bold | Headers | Bullets | "
                         "Greetings and sign-offs |"),
        "doc_intro": ("Documents: the model wrote each of {tasks} sqlpipe documentation tasks {runs} times in each condition. "
                      "Each rate is the linter's count divided by the eojeol count. The linter is a regex check, "
                      "so read the numbers as a direction, not as a ranking."),
        "doc_header": ("| Condition | Documents | Errors per 100 eojeol | Warnings per 100 eojeol | "
                       "Translationese per 100 eojeol | Designated spelling rate | Easy word rate | Longest sentence |"),
        "longest": "{n} eojeol",
        "not_measured": "not measured",
        "results_link": ("The raw outputs, the spelling distribution, and the test conditions are in "
                         "[`{rel}/RESULTS.md`]({href})."),
        "labels": {"baseline": "No skill", "reply_plain": "SimpleKorean", "plain": "Default mode", "strict": "Strict mode"},
        "example_before": "Reply written without the skill (`{path}`):",
        "example_after": "Reply from the same model with SimpleKorean on (`{path}`):",
        "example_docs": "Document examples are in [`examples/before-after.md`]({href}).",
        "block_size": "rule block of {n} characters",
    },
    "ja": {
        "reply_intro": "回答：専門用語を1つずつ含む質問{questions}個を、条件ごとに{runs}回ずつ尋ねました。回答は全部で{total}個です。",
        "headline": ("スキルを有効にすると、読者に見える欠陥（em-dash、太字、見出し、箇条書き）が{cut}減りました"
                     "（{base}個から{plain}個）。ブラインド判定では、SimpleKorean の回答が{n}組のうち{wins}組で勝ち、"
                     "{ties}組で引き分け、{losses}組で負けました。"),
        "reply_header": "| 条件 | 回答数 | 平均語節数 | 平均文数 | em-dash | 太字 | 見出し | 箇条書き | 挨拶と結び |",
        "doc_intro": ("文書：sqlpipe の文書課題{tasks}個を、条件ごとに{runs}回ずつ書きました。"
                      "比率は、リンターが数えた件数を語節数で割った値です。"
                      "リンターは正規表現による検査なので、順位ではなく傾向として読んでください。"),
        "doc_header": ("| 条件 | 文書数 | 100語節あたりのエラー | 100語節あたりの警告 | 100語節あたりの翻訳調 | "
                       "指定表記の比率 | やさしい語の比率 | 最長の文 |"),
        "longest": "{n}語節",
        "not_measured": "未測定",
        "results_link": "生の出力、表記の分布、測定条件は [`{rel}/RESULTS.md`]({href}) にあります。",
        "labels": {"baseline": "スキルなし", "reply_plain": "SimpleKorean", "plain": "基本モード", "strict": "厳格モード"},
        "example_before": "スキルなしで書いた回答（`{path}`）：",
        "example_after": "同じモデルが SimpleKorean を有効にして書いた回答（`{path}`）：",
        "example_docs": "文書の例は [`examples/before-after.md`]({href}) にあります。",
        "block_size": "{n}文字のルールブロック",
    },
    "zh": {
        "reply_intro": "回答：我们把 {questions} 个问题在每个条件下各问了 {runs} 次，每个问题含一个专业术语，共得到 {total} 个回答。",
        "headline": ("启用技能后，读者能看到的缺陷（em-dash、粗体、标题、列表符号）减少了 {cut}（从 {base} 个降到 {plain} 个）。"
                     "在 {n} 组盲评中，SimpleKorean 的回答赢了 {wins} 组，平了 {ties} 组，输了 {losses} 组。"),
        "reply_header": "| 条件 | 回答数 | 平均语节数 | 平均句数 | em-dash | 粗体 | 标题 | 列表符号 | 问候语和结束语 |",
        "doc_intro": ("文档：sqlpipe 的 {tasks} 个文档任务在每个条件下各写了 {runs} 次。比率是检查器的计数除以语节数得到的值。"
                      "检查器使用正则表达式，所以请把数字当作方向，而不是排名。"),
        "doc_header": ("| 条件 | 文档数 | 每 100 语节错误 | 每 100 语节警告 | 每 100 语节翻译腔 | 规定写法比例 | "
                       "简单词比例 | 最长句子 |"),
        "longest": "{n} 个语节",
        "not_measured": "未测量",
        "results_link": "原始输出、写法分布和测量条件见 [`{rel}/RESULTS.md`]({href})。",
        "labels": {"baseline": "无技能", "reply_plain": "SimpleKorean", "plain": "基本模式", "strict": "严格模式"},
        "example_before": "未启用技能时写的回答（`{path}`）：",
        "example_after": "同一模型启用 SimpleKorean 后写的回答（`{path}`）：",
        "example_docs": "文档示例见 [`examples/before-after.md`]({href})。",
        "block_size": "{n} 个字符的规则块",
    },
    "es": {
        "reply_intro": ("Respuestas: hicimos {questions} preguntas {runs} veces en cada condición. "
                        "Cada pregunta contiene un término técnico. En total hay {total} respuestas. "),
        "headline": ("Con la skill activada, los defectos visibles para el lector (em-dash, negritas, encabezados, viñetas) "
                     "bajaron un {cut} (de {base} a {plain}). En una evaluación a ciegas de {n} pares, la respuesta de "
                     "SimpleKorean ganó {wins}, empató {ties} y perdió {losses}."),
        "reply_header": ("| Condición | Respuestas | Media de eojeol | Media de oraciones | em-dash | Negritas | "
                         "Encabezados | Viñetas | Saludos y despedidas |"),
        "doc_intro": ("Documentos: el modelo escribió cada una de las {tasks} tareas de documentación de sqlpipe {runs} veces "
                      "en cada condición. Cada tasa es el recuento del linter dividido entre el número de eojeol. "
                      "El linter es una comprobación con expresiones regulares, así que lea las cifras como una dirección, "
                      "no como una clasificación."),
        "doc_header": ("| Condición | Documentos | Errores por 100 eojeol | Avisos por 100 eojeol | Calcos por 100 eojeol | "
                       "Tasa de grafía designada | Tasa de palabras fáciles | Oración más larga |"),
        "longest": "{n} eojeol",
        "not_measured": "no medido",
        "results_link": ("Las salidas originales, la distribución de grafías y las condiciones de medición están en "
                         "[`{rel}/RESULTS.md`]({href})."),
        "labels": {"baseline": "Sin skill", "reply_plain": "SimpleKorean", "plain": "Modo básico", "strict": "Modo estricto"},
        "example_before": "Respuesta escrita sin la skill (`{path}`):",
        "example_after": "Respuesta del mismo modelo con SimpleKorean activado (`{path}`):",
        "example_docs": "Los ejemplos de documentos están en [`examples/before-after.md`]({href}).",
        "block_size": "bloque de reglas de {n} caracteres",
    },
}


def prefix(lang):
    """README에서 레포 루트까지의 상대 경로. 번역판은 docs/에 있다."""
    return "" if lang == "ko" else "../"


def link(lang, rel):
    """레포 기준 경로를 그 언어의 README에서 쓸 링크 대상으로 바꾼다."""
    return prefix(lang) + rel


def readme_link(src, dst):
    """src 언어의 README에서 dst 언어의 README로 가는 상대 링크. 번역판끼리는 같은 폴더에 있다."""
    if src == "ko":
        return README[dst]
    return "../" + README[dst] if dst == "ko" else README[dst].split("/")[-1]


def language_line(lang):
    """언어 선택 줄. 순서는 LANGS를 따르고, 현재 언어는 링크 없이 쓴다."""
    items = [NAMES[other] if other == lang else f'<a href="{readme_link(lang, other)}">{NAMES[other]}</a>'
             for other in LANGS]
    return '<p align="center">\n  ' + " | ".join(items) + "\n</p>"


def grouped(n, lang):
    """큰 정수를 그 언어의 관례대로 쓴다. es는 네 자리까지 묶지 않고, 다섯 자리부터 줄바꿈 없는 공백으로 묶는다(RAE)."""
    if lang != "es":
        return f"{n:,}"
    return str(n) if abs(n) < 10000 else f"{n:,}".replace(",", NBSP)


def percent(number, lang):
    """숫자에 퍼센트 기호를 붙인다. es는 기호 앞에 줄바꿈 없는 공백을 둔다(RAE)."""
    return f"{number}{NBSP}%" if lang == "es" else f"{number}%"
```

- [ ] **Step 4: 시험을 돌린다**

Run: `python3 evals/tests/run.py evals/tests/test_readme_i18n.py`
Expected: `FAIL` 없음.

- [ ] **Step 5: 커밋한다**

```bash
git add evals/readme_i18n.py evals/tests/test_readme_i18n.py
git commit -F - <<'EOF'
docs: README 다섯 언어판의 문장 틀을 둔다

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01SanRSLxxVtkLMJh1wLGeGZ
EOF
```

### Task 8: 두 생성기가 언어별 블록을 쓴다

**Files:**
- Modify: `evals/report.py:1-8,17-27,89-133,142-158,184-209`, `evals/make_examples.py:1-12,75-115`
- Test: `evals/tests/test_readme_i18n.py`(이어 쓴다)

**Interfaces:**
- Consumes: Task 7의 `i18n.TEXT`, `i18n.link`, `i18n.percent`, `i18n.README`, `i18n.LANGS`.
- Produces:
  - `report.benchmark_stats(results_dir, scenarios) -> dict`(키 `rel`, `replies`, `judge`, `docs`, `n_reply`, `reply_shape`, `doc_shape`)
  - `report.render_readme_block(stats, lang="ko") -> str`
  - `report.readme_block(results_dir, scenarios, lang="ko") -> str`
  - `report.render_headline(stats, judge, lang="ko")`, `report.render_reply_table(stats, lang="ko")`, `report.render_doc_table(stats, lang="ko")`
  - `report.replace_readme_block(readme_text, results_dir, block, name="README.md") -> str`
  - `report.update_readmes(results_dir, scenarios, langs=i18n.LANGS, root=ROOT, stats=None) -> None`
  - `make_examples.readme_example(results_dir, lang="ko") -> str`
  - `make_examples.replace_example_block(readme_text, body, name="README.md") -> str`
  - `make_examples.update_readmes(results_dir, langs=i18n.LANGS, root=ROOT) -> None`

- [ ] **Step 1: 실패하는 시험을 쓴다**

`evals/tests/test_readme_i18n.py` 끝에 더한다.

```python
SCENARIOS = [{"id": "readme-intro", "type": "descriptive"}]
EMPTY = "<!-- example:start -->\n\n<!-- example:end -->\n\n<!-- benchmark:start x -->\n\n<!-- benchmark:end -->\n"


def _results(d):
    """ROOT 아래 임시 결과 디렉터리에 답변 두 개, 판정 하나, 문서 세 개를 쓴다."""
    root = Path(d)
    (root / "reply").mkdir()
    (root / "reply" / "baseline__oom__r1.txt").write_text("**네** — 메모리가 부족합니다.\n\n- 한도\n", encoding="utf-8")
    (root / "reply" / "plain__oom__r1.txt").write_text("메모리 한도를 넘어서 파드가 끝났습니다.", encoding="utf-8")
    (root / "judge").mkdir()
    (root / "judge" / "oom__r1.json").write_text(json.dumps({"winner": "plain"}), encoding="utf-8")
    (root / "docs").mkdir()
    for cond, text in (("baseline", "메세지를 보냅니다."), ("plain", "메시지를 보냅니다."), ("strict", "메시지를 보냅니다.")):
        record = {"condition": cond, "scenario": "readme-intro", "text": text}
        (root / "docs" / f"{cond}__readme-intro__r1.json").write_text(json.dumps(record, ensure_ascii=False),
                                                                        encoding="utf-8")
    return root


def _site(d):
    """README 다섯 개가 빈 블록 표시만 가진 임시 레포 뼈대."""
    site = Path(d) / "site"
    for lang in i18n.LANGS:
        path = site / i18n.README[lang]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(EMPTY, encoding="utf-8")
    return site


def _exit_message(call):
    """call이 SystemExit로 끝나면 그 메시지를 돌려주고, 아니면 시험을 실패시킨다."""
    try:
        call()
    except SystemExit as err:
        return str(err)
    raise AssertionError("SystemExit가 나야 합니다")


def test_benchmark_blocks_link_from_each_readme_folder():
    with tempfile.TemporaryDirectory(dir=str(ROOT / "evals")) as d:
        root = _results(d)
        rel = root.resolve().relative_to(ROOT).as_posix()
        stats = report.benchmark_stats(root, SCENARIOS)
        ko = report.render_readme_block(stats, "ko")
        assert ko == report.readme_block(root, SCENARIOS)
        assert f"[`{rel}/RESULTS.md`]({rel}/RESULTS.md)" in ko and "| 엄격 모드 |" in ko
        for lang in i18n.LANGS[1:]:
            block = report.render_readme_block(stats, lang)
            assert f"[`{rel}/RESULTS.md`](../{rel}/RESULTS.md)" in block, lang
            assert f"| {i18n.TEXT[lang]['labels']['strict']} |" in block, lang
        assert "100 %" in report.render_readme_block(stats, "es")


def test_example_blocks_keep_the_korean_outputs():
    with tempfile.TemporaryDirectory(dir=str(ROOT / "evals")) as d:
        root = _results(d)
        ko = mx.readme_example(root, "ko")
        assert ko == mx.readme_example(root)
        for lang in i18n.LANGS[1:]:
            body = mx.readme_example(root, lang)
            assert mx.SOURCE_BLOCK.findall(body) == mx.SOURCE_BLOCK.findall(ko), lang
            assert "](../examples/before-after.md)" in body, lang


def test_update_readmes_fills_every_language():
    with tempfile.TemporaryDirectory(dir=str(ROOT / "evals")) as d:
        root, site = _results(d), _site(d)
        rel = root.resolve().relative_to(ROOT).as_posix()
        mx.update_readmes(root, root=site)
        report.update_readmes(root, SCENARIOS, root=site)
        for lang in i18n.LANGS:
            text = (site / i18n.README[lang]).read_text(encoding="utf-8")
            assert f"<!-- benchmark:start {rel} -->" in text, lang
            assert mx.EXAMPLE_BLOCK.search(text).group(1) == mx.readme_example(root, lang), lang
            assert report.README_BLOCK.search(text).group(2) == report.readme_block(root, SCENARIOS, lang), lang


def test_update_readmes_stops_before_writing_when_a_readme_is_broken():
    with tempfile.TemporaryDirectory(dir=str(ROOT / "evals")) as d:
        root, site = _results(d), _site(d)
        (site / "docs/README.ja.md").write_text("블록 없음\n", encoding="utf-8")
        assert "docs/README.ja.md" in _exit_message(lambda: mx.update_readmes(root, root=site))
        assert "docs/README.ja.md" in _exit_message(lambda: report.update_readmes(root, SCENARIOS, root=site))
        assert (site / "README.md").read_text(encoding="utf-8") == EMPTY
        (site / "docs/README.ja.md").unlink()
        assert "docs/README.ja.md" in _exit_message(lambda: mx.update_readmes(root, root=site))
        assert "docs/README.ja.md" in _exit_message(lambda: report.update_readmes(root, SCENARIOS, root=site))
```

- [ ] **Step 2: 시험이 실패하는지 본다**

Run: `python3 evals/tests/run.py evals/tests/test_readme_i18n.py`
Expected: 새 시험 넷이 `AttributeError`(`benchmark_stats`, `update_readmes` 없음)나 `TypeError`(`readme_example`에 언어 인자 없음)로 `FAIL`.

- [ ] **Step 3: `report.py`를 고친다**

모듈 독스트링의 사용법 두 줄을 바꾼다.

```python
    python3 evals/report.py evals/results/<날짜>            # RESULTS.md를 쓰고 한국어 README 블록을 출력한다
    python3 evals/report.py evals/results/<날짜> --readme   # README 다섯 개의 벤치마크 블록도 바꾼다(readme_i18n.README)
```

import에 `import readme_i18n as i18n  # noqa: E402`를 더한다(`import metrics` 다음 줄). `REPLY_LABELS`와 `DOC_LABELS` 두 줄은 지우고, 그 자리에 표 구분선 두 줄을 둔다.

```python
REPLY_SEP = "|---|---:|---:|---:|---:|---:|---:|---:|---:|"
DOC_SEP = "|---|---:|---:|---:|---:|---:|---:|---:|"
```

`_pct`부터 `render_headline`까지(89-121번째 줄)를 통째로 바꾼다.

```python
def _t(lang, key):
    return i18n.TEXT[lang][key]


def _pct(part, whole, lang="ko"):
    return i18n.percent(f"{100 * part / whole:.1f}", lang) if whole else _t(lang, "not_measured")


def render_reply_table(stats, lang="ko"):
    labels = _t(lang, "labels")
    lines = [_t(lang, "reply_header"), REPLY_SEP]
    for cond in REPLY_CONDS:
        s = Counter(stats[cond])
        n = max(1, s["n"])
        label = labels["reply_plain"] if cond == "plain" else labels[cond]
        lines.append(f"| {label} | {s['n']} | {s['eojeol'] / n:.0f} | {s['sentences'] / n:.1f} | "
                     f"{s['em_dash']} | {s['bold_spans']} | {s['headers']} | {s['bullets']} | {s['fillers']} |")
    return "\n".join(lines)


def render_doc_table(stats, lang="ko"):
    labels = _t(lang, "labels")
    lines = [_t(lang, "doc_header"), DOC_SEP]
    for cond in DOC_CONDS:
        s = Counter(stats[cond])
        w = max(1, s["eojeol"])
        lines.append(f"| {labels[cond]} | {s['n']} | {100 * s['errors'] / w:.2f} | {100 * s['warnings'] / w:.2f} | "
                     f"{100 * s['translationese'] / w:.2f} | {_pct(s['designated'], s['terms'], lang)} | "
                     f"{_pct(s['easy'], s['content'], lang)} | {_t(lang, 'longest').format(n=s['longest'])} |")
    return "\n".join(lines)


def render_headline(stats, judge, lang="ko"):
    base, plain = stats["baseline"].get("visible", 0), stats["plain"].get("visible", 0)
    cut = round(100 * (base - plain) / base) if base else 0
    return _t(lang, "headline").format(cut=i18n.percent(cut, lang), base=base, plain=plain, n=judge["n"],
                                       wins=judge["plain"], ties=judge["tie"], losses=judge["baseline"])
```

`readme_block`(142-158번째 줄)을 세 함수로 바꾼다.

```python
def benchmark_stats(results_dir, scenarios):
    """README 벤치마크 블록의 수치. 언어마다 다시 세지 않도록 한 번 센다."""
    replies = reply_stats(results_dir)
    return {
        "rel": Path(results_dir).resolve().relative_to(ROOT).as_posix(),
        "replies": replies,
        "judge": judge_stats(results_dir),
        "docs": doc_stats(results_dir, scenarios),
        "n_reply": replies["plain"].get("n", 0) + replies["baseline"].get("n", 0),
        "reply_shape": _shape(results_dir, "reply", "*.txt"),
        "doc_shape": _shape(results_dir, "docs", "*.json"),
    }


def render_readme_block(stats, lang="ko"):
    """벤치마크 블록 본문을 그 언어로 쓴다. check_numbers.py가 README와 글자 하나까지 대조한다."""
    (questions, reply_runs), (tasks, doc_runs), rel = stats["reply_shape"], stats["doc_shape"], stats["rel"]
    return "\n\n".join([
        _t(lang, "reply_intro").format(questions=questions, runs=reply_runs, total=stats["n_reply"])
        + render_headline(stats["replies"], stats["judge"], lang),
        render_reply_table(stats["replies"], lang),
        _t(lang, "doc_intro").format(tasks=tasks, runs=doc_runs),
        render_doc_table(stats["docs"], lang),
        _t(lang, "results_link").format(rel=rel, href=i18n.link(lang, f"{rel}/RESULTS.md")),
    ])


def readme_block(results_dir, scenarios, lang="ko"):
    """README 벤치마크 블록 본문. lang은 readme_i18n.LANGS 가운데 하나다."""
    return render_readme_block(benchmark_stats(results_dir, scenarios), lang)
```

`replace_readme_block`과 `main`(184-209번째 줄)을 바꾼다. `update_readmes`를 그 사이에 둔다.

```python
def replace_readme_block(readme_text, results_dir, block, name="README.md"):
    """README의 벤치마크 블록을 새 결과 디렉터리와 본문으로 바꾼 새 문자열."""
    rel = Path(results_dir).resolve().relative_to(ROOT).as_posix()
    new = f"<!-- benchmark:start {rel} -->\n{block}\n<!-- benchmark:end -->"
    if not README_BLOCK.search(readme_text):
        raise SystemExit(f"{name}에 <!-- benchmark:start ... --> 블록이 없습니다")
    return README_BLOCK.sub(lambda m: new, readme_text, count=1)


def update_readmes(results_dir, scenarios, langs=i18n.LANGS, root=ROOT, stats=None):
    """README들의 벤치마크 블록을 바꾼다. 하나라도 읽지 못하거나 블록이 없으면 아무 파일도 바꾸지 않고 멈춘다."""
    stats = stats or benchmark_stats(results_dir, scenarios)
    texts = {}
    for lang in langs:
        name = i18n.README[lang]
        path = Path(root) / name
        try:
            current = path.read_text(encoding="utf-8")
        except OSError as err:
            raise SystemExit(f"{name}: 읽지 못했습니다({err})")
        texts[path] = replace_readme_block(current, results_dir, render_readme_block(stats, lang), name)
    for path, text in texts.items():
        path.write_text(text, encoding="utf-8")


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if not args:
        raise SystemExit("사용법: report.py <결과 디렉터리> [--readme]")
    results_dir = Path(args[0])
    scenarios = json.loads((HERE / "scenarios.json").read_text(encoding="utf-8"))
    Path(results_dir, "RESULTS.md").write_text(results_md(results_dir, scenarios), encoding="utf-8")
    stats = benchmark_stats(results_dir, scenarios)
    print(render_readme_block(stats))
    if "--readme" in args:
        update_readmes(results_dir, scenarios, stats=stats)
    return 0
```

- [ ] **Step 4: `make_examples.py`를 고친다**

모듈 독스트링의 두 번째 사용법 줄을 바꾼다.

```python
    python3 evals/make_examples.py evals/results/<날짜> --readme   # README 다섯 개의 보기 블록도 바꾼다
```

import에 `import readme_i18n as i18n`을 더한다(`from pathlib import Path` 다음 줄). 스크립트로 돌 때도 `evals/`가 `sys.path`의 첫 칸이라 그대로 읽힌다.

`readme_example`부터 `main`까지(75-115번째 줄)를 바꾼다. `check_sources`는 그대로 둔다.

```python
def readme_example(results_dir, lang="ko"):
    """README 보기 블록의 본문. 인용한 출력은 어느 언어에서나 한국어 원문이다."""
    before, after = _pair(results_dir, "reply", README_PICK, "plain", "txt")
    text = i18n.TEXT[lang]
    return "\n\n".join([text["example_before"].format(path=before), source_block(before),
                        text["example_after"].format(path=after), source_block(after),
                        text["example_docs"].format(href=i18n.link(lang, "examples/before-after.md"))])


def replace_example_block(readme_text, body, name="README.md"):
    """README의 보기 블록을 새 본문으로 바꾼 새 문자열."""
    if not EXAMPLE_BLOCK.search(readme_text):
        raise SystemExit(f"{name}에 <!-- example:start --> 블록이 없습니다")
    return EXAMPLE_BLOCK.sub(lambda m: f"<!-- example:start -->\n{body}\n<!-- example:end -->", readme_text, count=1)


def update_readmes(results_dir, langs=i18n.LANGS, root=ROOT):
    """README들의 보기 블록을 바꾼다. 하나라도 읽지 못하거나 블록이 없으면 아무 파일도 바꾸지 않고 멈춘다."""
    texts = {}
    for lang in langs:
        name = i18n.README[lang]
        path = Path(root) / name
        try:
            current = path.read_text(encoding="utf-8")
        except OSError as err:
            raise SystemExit(f"{name}: 읽지 못했습니다({err})")
        texts[path] = replace_example_block(current, readme_example(results_dir, lang), name)
    for path, text in texts.items():
        path.write_text(text, encoding="utf-8")
```

`check_sources`는 지금 자리(`replace_example_block` 다음)에 그대로 둔다. `main`은 `--readme` 부분만 바꾼다.

```python
def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if not args:
        raise SystemExit("사용법: make_examples.py <결과 디렉터리> [--readme]")
    EXAMPLES.parent.mkdir(parents=True, exist_ok=True)
    EXAMPLES.write_text(examples_md(args[0]), encoding="utf-8")
    if "--readme" in args:
        update_readmes(args[0])
    return 0
```

- [ ] **Step 5: 시험과 수치 검증을 돌린다**

Run: `python3 evals/tests/run.py && .venv/bin/python evals/check_numbers.py`
Expected: `FAIL` 없음, `check_numbers OK`. 한국어 README의 블록이 한 글자도 바뀌지 않았다는 증거다.

- [ ] **Step 6: 커밋한다**

```bash
git add evals/report.py evals/make_examples.py evals/tests/test_readme_i18n.py
git commit -F - <<'EOF'
docs: 두 생성기가 README 블록을 언어마다 쓴다

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01SanRSLxxVtkLMJh1wLGeGZ
EOF
```

### Task 9: 번역판 검사 함수와 구조 검사

`main()`은 이 작업에서 바꾸지 않는다. 번역판이 생긴 뒤 Task 14에서 연결한다.

**Files:**
- Modify: `evals/check_numbers.py`(import, `check_benchmark`, `check_examples`, `check_block_size`, 새 함수들)
- Test: `evals/tests/test_check_numbers.py`

**Interfaces:**
- Consumes: Task 7의 `i18n`, Task 8의 `report.benchmark_stats`, `report.render_readme_block`, `make_examples.readme_example(results_dir, lang)`, `make_examples.EXAMPLE_BLOCK`.
- Produces:
  - `check_benchmark(readme, changelog, scenarios, require_easy=True, stats=None)`
  - `check_benchmark_block(text, lang, meta, stats) -> list[str]`
  - `check_example_block(text, lang, results_dir) -> list[str]`
  - `check_block_size(readme, prompt_md, lang="ko") -> list[str]`
  - `readme_outline(text, lang) -> (제목 수준 목록, 레포 링크 목록, 문제 목록)`
  - `check_readme_structure(ko_readme, lang, text, root=None) -> list[str]`
  - `check_translation(lang, text, ko_readme, scenarios, prompt_md, stats=None, root=None) -> list[str]`
  - `translation_problems(lang) -> list[str]`(레포 파일을 읽는다. 번역 작업에서 쓴다)

- [ ] **Step 1: 실패하는 시험을 쓴다**

`evals/tests/test_check_numbers.py`의 import에 `import readme_i18n as i18n  # noqa: E402`를 더한다(`import report` 다음 줄).

`test_check_benchmark_catches_stale_numbers_and_missing_changelog_path`의 한 줄을 바꾼다.

전:
```python
        assert any("README 벤치마크 블록" in p for p in cn.check_benchmark(stale, changelog, scenarios, require_easy=False))
```
후:
```python
        assert any("README.md 벤치마크 블록" in p for p in cn.check_benchmark(stale, changelog, scenarios, require_easy=False))
```

파일 끝에 시험을 더한다.

```python
def _readme(lang, body):
    """언어 선택 줄, 본문, 빈 블록 표시로 된 작은 README."""
    return (f"{i18n.language_line(lang)}\n\n{body}\n\n"
            "<!-- example:start -->\n\n<!-- example:end -->\n\n"
            "<!-- benchmark:start x -->\n\n<!-- benchmark:end -->\n")


def test_structure_matches_headings_and_links():
    ko = _readme("ko", '## 설치\n\n[`SKILL.md`](skills/simple-korean/SKILL.md)와 <a href="LICENSE">MIT</a>\n\n## 기여\n')
    en = _readme("en", '## Install\n\n[`SKILL.md`](../skills/simple-korean/SKILL.md) and <a href="../LICENSE">MIT</a>\n\n'
                       '## Contributing\n')
    assert cn.check_readme_structure(ko, "ko", ko) == []
    assert cn.check_readme_structure(ko, "en", en) == []
    assert any("제목 수준" in p for p in cn.check_readme_structure(ko, "en", en.replace("## Contributing\n", "")))
    no_prefix = en.replace("](../skills", "](skills")
    assert any("../가 없습니다" in p and "skills/simple-korean/SKILL.md" in p
               for p in cn.check_readme_structure(ko, "en", no_prefix))
    found = cn.check_readme_structure(ko, "en", en.replace("simple-korean/SKILL.md", "simple-korean/NOPE.md"))
    assert any("레포 링크가 한국어판과 다릅니다" in p for p in found)
    assert any("링크한 파일이 없습니다" in p for p in found)


def test_structure_ignores_code_quotes_external_links_and_anchors():
    body = ("## 설치\n\n```bash\n# 주석은 제목이 아니다\n[가짜](nope.md)\n```\n\n> ## 인용 안의 제목\n> [인용](nope.md)\n\n"
            "`[코드](nope.md)`와 [웹](https://example.com)과 [앵커](#설치)\n\n[규칙](skills/simple-korean/SKILL.md#규칙)\n")
    ko = _readme("ko", body)
    assert cn.readme_outline(ko, "ko")[:2] == ([2], ["skills/simple-korean/SKILL.md#규칙"])
    assert cn.check_readme_structure(ko, "ko", ko) == []


def test_structure_needs_the_exact_language_line_and_single_markers():
    ko = _readme("ko", "## 설치\n")
    spaced = ko.replace(" | ", "|", 1)
    assert any("언어 선택 줄" in p and i18n.language_line("ko") in p for p in cn.check_readme_structure(ko, "ko", spaced))
    doubled = ko + "<!-- example:start -->\n"
    assert any("example:start" in p for p in cn.check_readme_structure(ko, "ko", doubled))


def test_check_block_size_uses_each_language_phrase():
    big = "\n".join([BLOCK] * 40)
    prompt = f"# 시스템 프롬프트\n\n---\n{big}\n---\n"
    n = len(big)
    assert n >= 1000
    assert cn.check_block_size(f"It adds a rule block of {n:,} characters.", prompt, "en") == []
    assert cn.check_block_size(f"Añade un bloque de reglas de {n} caracteres.", prompt, "es") == []
    assert cn.check_block_size(f"Añade un bloque de reglas de {n:,} caracteres.", prompt, "es") != []


def test_check_example_block_compares_the_sentences_too():
    with tempfile.TemporaryDirectory(dir=str(cn.ROOT / "evals")) as d:
        root = _results(d)
        empty = "<!-- example:start -->\n\n<!-- example:end -->\n"
        for lang in i18n.LANGS:
            assert cn.check_example_block(mx.replace_example_block(empty, mx.readme_example(root, lang)), lang, root) == []
        ko = mx.replace_example_block(empty, mx.readme_example(root, "ko"))
        edited = ko.replace("스킬 없이 쓴 답변", "스킬 없이 만든 답변")
        assert any("README.md 보기 블록" in p for p in cn.check_example_block(edited, "ko", root))
        assert cn.check_example_block("블록 없음", "en", root) == ["docs/README.en.md에 보기 블록이 없습니다"]


def test_check_translation_passes_a_generated_translation():
    scenarios = [{"id": "readme-intro", "type": "descriptive"}]
    prompt = f"---\n{BLOCK}\n---\n"
    with tempfile.TemporaryDirectory(dir=str(cn.ROOT / "evals")) as d:
        root = _results(d)
        (root / "RESULTS.md").write_text("결과\n", encoding="utf-8")
        rel = root.resolve().relative_to(cn.ROOT).as_posix()
        stats = report.benchmark_stats(root, scenarios)

        def page(lang):
            size = i18n.TEXT[lang]["block_size"].format(n=i18n.grouped(len(BLOCK), lang))
            text = (f"{i18n.language_line(lang)}\n\n`m`, `j`, {size}\n\n## A\n\n"
                    "<!-- example:start -->\n\n<!-- example:end -->\n\n"
                    f"<!-- benchmark:start {rel} -->\n\n<!-- benchmark:end -->\n")
            text = mx.replace_example_block(text, mx.readme_example(root, lang))
            return report.replace_readme_block(text, root, report.render_readme_block(stats, lang))

        ko, en = page("ko"), page("en")
        assert cn.check_translation("en", en, ko, scenarios, prompt, stats) == []
        stale = en.replace(f"benchmark:start {rel}", "benchmark:start evals/results/2026-10-08")
        assert any("결과 경로" in p for p in cn.check_translation("en", stale, ko, scenarios, prompt, stats))


def test_translation_problems_names_missing_files():
    old = cn.ROOT
    with tempfile.TemporaryDirectory() as d:
        cn.ROOT = Path(d)
        try:
            assert cn.translation_problems("en") == ["파일이 없습니다: README.md", "파일이 없습니다: docs/README.en.md"]
        finally:
            cn.ROOT = old
```

- [ ] **Step 2: 시험이 실패하는지 본다**

Run: `python3 evals/tests/run.py evals/tests/test_check_numbers.py`
Expected: 새 시험들이 `AttributeError`(`check_readme_structure` 등 없음)로, 바꾼 줄이 메시지 불일치로 `FAIL`.

- [ ] **Step 3: import와 상수를 더한다**

`evals/check_numbers.py`의 import에 `import readme_i18n as i18n  # noqa: E402`를 더한다(`import metrics` 다음 줄). `check_benchmark` 앞에 상수를 둔다.

```python
KIWI_MISSING = "kiwipiepy가 없어 쉬운 단어 비율을 다시 계산하지 못했습니다. .venv/bin/python으로 돌리세요"
FENCES = ("```", "~~~")
HEADING = re.compile(r"(#{1,6}) ")
LINK = re.compile(r'\]\(([^)\s]+)\)|(?:href|src)="([^"]+)"')
EXTERNAL = ("http://", "https://", "mailto:", "#")
MARKERS = ("<!-- benchmark:start ", "<!-- benchmark:end -->", "<!-- example:start -->", "<!-- example:end -->")
```

- [ ] **Step 4: 벤치마크와 보기 검사를 언어별로 나눈다**

`check_benchmark`와 `check_examples`를 통째로 바꾸고, 두 함수를 더한다.

```python
def check_benchmark(readme, changelog, scenarios, require_easy=True, stats=None):
    """한국어 README 벤치마크 블록, RESULTS.md, CHANGELOG의 결과 경로를 확인한다.

    require_easy가 참이면 kiwipiepy가 없을 때 멈춘다. 없으면 쉬운 단어 비율이 '측정 안 함'으로 바뀌어
    공개한 표와 달라지기 때문이다. 단위 시험만 이 값을 끈다. stats는 report.benchmark_stats의 결과이고,
    없으면 여기서 센다.
    """
    m = report.README_BLOCK.search(readme)
    if not m:
        return ["README.md에 벤치마크 블록이 없습니다"]
    rel, results_dir = m.group(1), ROOT / m.group(1)
    if require_easy and metrics.easy_word_counts("확인합니다.") is None:
        return [KIWI_MISSING]
    meta = json.loads((results_dir / "meta.json").read_text(encoding="utf-8"))
    problems = check_benchmark_block(readme, "ko", meta, stats or report.benchmark_stats(results_dir, scenarios))
    rebuilt = report.results_md(results_dir, scenarios)
    current = (results_dir / "RESULTS.md").read_text(encoding="utf-8")
    if current != rebuilt:
        problems.append(_diff(f"{rel}/RESULTS.md", rebuilt, current))
    if rel not in changelog and not unreleased(meta["date"], changelog):
        problems.append(f"CHANGELOG.md가 측정 결과 {rel}을 가리키지 않습니다. 이 결과를 싣는 릴리스 항목에 경로를 적으세요")
    return problems


def check_benchmark_block(text, lang, meta, stats):
    """README 하나의 벤치마크 블록과 모델 이름을 본다. 블록은 그 언어로 다시 만든 글과 같아야 한다."""
    name = i18n.README[lang]
    problems = [f"{name}가 {label} `{meta[key]}`를 밝히지 않습니다"
                for key, label in (("model", "작성 모델"), ("judge_model", "판정 모델")) if f"`{meta[key]}`" not in text]
    block = report.render_readme_block(stats, lang)
    current = report.README_BLOCK.search(text).group(2)
    if current != block:
        problems.append(_diff(f"{name} 벤치마크 블록", block, current))
    return problems


def check_examples(readme, examples):
    """인용한 출력이 원본과 같은지 보고, 한국어 README의 보기 블록 전체를 다시 만들어 대조한다."""
    problems = make_examples.check_sources(readme) + make_examples.check_sources(examples)
    if not make_examples.SOURCE_BLOCK.search(readme):
        problems.append("README.md에 원본 인용 블록이 없습니다")
    bench = report.README_BLOCK.search(readme)
    if bench:
        problems += check_example_block(readme, "ko", ROOT / bench.group(1))
    return problems


def check_example_block(text, lang, results_dir):
    """보기 블록 전체(설명 문장과 인용)를 그 언어로 다시 만든 글과 대조한다."""
    name = i18n.README[lang]
    m = make_examples.EXAMPLE_BLOCK.search(text)
    if not m:
        return [f"{name}에 보기 블록이 없습니다"]
    expected = make_examples.readme_example(results_dir, lang)
    return [] if m.group(1) == expected else [_diff(f"{name} 보기 블록", expected, m.group(1))]
```

`check_block_size`를 바꾼다.

```python
def check_block_size(readme, prompt_md, lang="ko"):
    """README가 밝힌 규칙 블록 글자 수가 훅이 넣는 블록의 실제 길이와 같은지 본다. 문구는 언어마다 다르다."""
    n = len(bench_common.rule_block(prompt_md))
    size = i18n.TEXT[lang]["block_size"].format(n=i18n.grouped(n, lang))
    return [] if size in readme else [f"{i18n.README[lang]}에 '{size}'가 없습니다. 훅이 세션마다 넣는 블록의 길이를 적으세요"]
```

- [ ] **Step 5: 구조 검사와 번역판 검사를 더한다**

`check_versions` 아래에 더한다.

```python
def _prose(text):
    """코드 블록과 인용 블록 밖의 줄. 인라인 코드는 지운다."""
    lines, fenced = [], False
    for line in text.split("\n"):
        if line.startswith(FENCES):
            fenced = not fenced
            continue
        if not fenced and not line.startswith(">"):
            lines.append(re.sub(r"`[^`]*`", "", line))
    return lines


def readme_outline(text, lang):
    """(제목 수준 목록, 레포 링크 목록, 문제 목록). 링크는 레포 기준 경로이고, 언어 선택 줄은 뺀다."""
    prose = _prose(text.replace(i18n.language_line(lang), ""))
    levels, links, problems = [], [], []
    for line in prose:
        heading = HEADING.match(line)
        if heading:
            levels.append(len(heading.group(1)))
        for m in LINK.finditer(line):
            target = m.group(1) or m.group(2)
            if target.startswith(EXTERNAL):
                continue
            if lang != "ko":
                if not target.startswith("../"):
                    problems.append(f"{i18n.README[lang]}: 레포 링크에 ../가 없습니다: {target}")
                    continue
                target = target[3:]
            links.append(target)
    return levels, links, problems


def check_readme_structure(ko_readme, lang, text, root=None):
    """README 하나의 구조를 본다. 언어 선택 줄, 블록 표시, 링크한 파일, 번역판이면 한국어판과 같은 제목과 링크."""
    root = Path(root) if root else ROOT
    name = i18n.README[lang]
    line = i18n.language_line(lang)
    problems = [] if text.count(line) == 1 else [f"{name}: 언어 선택 줄이 한 번 있어야 합니다. 이 블록을 그대로 쓰세요:\n{line}"]
    problems += [f"{name}: '{marker.strip()}' 표시가 한 번 있어야 합니다" for marker in MARKERS if text.count(marker) != 1]
    levels, links, found = readme_outline(text, lang)
    problems += found
    if lang != "ko":
        ko_levels, ko_links, _ = readme_outline(ko_readme, "ko")
        if levels != ko_levels:
            problems.append(f"{name}: 제목 수준이 한국어판과 다릅니다. 한국어판 {ko_levels}, 이 파일 {levels}")
        if links != ko_links:
            diff = difflib.unified_diff(ko_links, links, "README.md", name, lineterm="", n=0)
            problems.append(f"{name}: 레포 링크가 한국어판과 다릅니다\n" + "\n".join(diff))
    problems += [f"{name}: 링크한 파일이 없습니다: {t}" for t in links if not (root / t.split("#", 1)[0]).exists()]
    return problems


def check_translation(lang, text, ko_readme, scenarios, prompt_md, stats=None, root=None):
    """번역판 하나를 검사한다. 결과 경로, 생성 블록 두 개, 인용, 모델 이름, 규칙 블록 글자 수, 구조를 본다."""
    name = i18n.README[lang]
    m = report.README_BLOCK.search(text)
    if not m:
        return [f"{name}에 벤치마크 블록이 없습니다"] + check_readme_structure(ko_readme, lang, text, root)
    if stats is None:
        ko = report.README_BLOCK.search(ko_readme)
        stats = report.benchmark_stats(ROOT / ko.group(1), scenarios)
    results_dir = ROOT / stats["rel"]
    problems = [] if m.group(1) == stats["rel"] else [f"{name}의 결과 경로 {m.group(1)}가 한국어판({stats['rel']})과 다릅니다"]
    meta = json.loads((results_dir / "meta.json").read_text(encoding="utf-8"))
    return (problems + check_benchmark_block(text, lang, meta, stats) + make_examples.check_sources(text)
            + check_example_block(text, lang, results_dir) + check_block_size(text, prompt_md, lang)
            + check_readme_structure(ko_readme, lang, text, root))


def translation_problems(lang):
    """레포에 있는 번역판 하나를 검사한다. 번역하는 동안 한 언어만 볼 때 쓴다(.venv/bin/python으로 돌린다)."""
    missing = [f"파일이 없습니다: {rel}" for rel in ("README.md", i18n.README[lang]) if not (ROOT / rel).is_file()]
    if missing:
        return missing
    if metrics.easy_word_counts("확인합니다.") is None:
        return [KIWI_MISSING]
    return check_translation(lang, _read(i18n.README[lang]), _read("README.md"),
                             json.loads(_read("evals/scenarios.json")), _read("prompts/system-prompt.md"))
```

`_read`는 `REQUIRED` 아래에 있으므로 `translation_problems`는 `_read` 정의보다 뒤(파일에서 `_read` 다음, `main` 앞)에 둔다.

- [ ] **Step 6: 시험과 수치 검증을 돌린다**

Run: `python3 evals/tests/run.py && .venv/bin/python evals/check_numbers.py`
Expected: `FAIL` 없음, `check_numbers OK`(보기 블록 전체 대조가 지금 한국어 README에서 통과한다).

- [ ] **Step 7: 커밋한다**

```bash
git add evals/check_numbers.py evals/tests/test_check_numbers.py
git commit -F - <<'EOF'
docs: 번역판의 생성 블록과 구조를 검사하는 함수를 더한다

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01SanRSLxxVtkLMJh1wLGeGZ
EOF
```

### 번역 규칙 (Task 10-13이 따른다)

원문은 한국어 `README.md`다(PR 2의 배지와 기여 절이 들어간 상태). 아래를 지킨다.

1. 파일 첫머리는 이 순서다: 첫머리 문구(가운데 정렬 `<p><strong>…</strong></p>`), 빈 줄, `language_line(lang)` 블록, 빈 줄, 배지 블록. 한국어판의 영어 문단("SimpleKorean is an agent skill …")은 옮기지 않는다.
2. 언어 선택 줄은 손으로 쓰지 않고 출력해서 붙인다: `python3 -c "import sys; sys.path.insert(0,'evals'); import readme_i18n as i; print(i.language_line('<lang>'))"`.
3. 배지 블록은 한국어판과 같고, `LICENSE` 링크만 `../LICENSE`다.
4. 제목 10개를 한국어판과 같은 순서와 수준(`##`)으로 둔다. 제목 글은 아래 표를 쓴다.
5. 레포 링크는 한국어판과 같은 순서로 두고, 모두 `../`를 붙인다. 순서는 `python3 -c "import sys; sys.path.insert(0,'evals'); import check_numbers as c; print(c.readme_outline(open('README.md', encoding='utf-8').read(), 'ko')[1])"`로 본다.
6. 두 생성 블록은 빈 표시만 쓰고(`<!-- example:start -->`, 빈 줄, `<!-- example:end -->`, `<!-- benchmark:start evals/results/2026-10-08 -->`, 빈 줄, `<!-- benchmark:end -->`), 내용은 생성기로 채운다. 표시의 위치는 한국어판과 같다.
7. 벤치마크 절 소개 문단에는 백틱으로 감싼 `claude-sonnet-5-5`와 `claude-opus-5-5`를 그대로 두고, 아래 표의 "어절 풀이" 문장을 넣는다.
8. 설치 절에는 아래 표의 "규칙 블록 문장"을 쓴다. 숫자는 `python3 -c "import sys; sys.path.insert(0,'evals'); import bench_common as b, readme_i18n as i; n=len(b.rule_block(open('prompts/system-prompt.md', encoding='utf-8').read())); print(i.TEXT['<lang>']['block_size'].format(n=i.grouped(n, '<lang>')))"`의 출력과 같아야 한다.
9. 보기 절의 소개는 아래 표의 문장을 쓴다(답변이 한국어라는 점을 밝힌다).
10. 규칙 표의 한국어 예시("-면", "단, ~경우", "되어지다", "~에 의해", "-고 있습니다", "-ㄹ 수도 있습니다", "확인", "백업 확인 필요", "강력한", "디렉토리" 등)와 표기 정책 표의 한국어 형태는 그대로 두고, 그 언어로 짧은 풀이를 괄호에 붙인다. FAQ의 "리포지터리", "보디", "릴리즈", "컬럼"도 같다.
11. 명령어, 코드 블록, JSON 예시, 파일 경로, 제품 이름은 그대로 둔다.
12. 기여 절의 PR 제목 문단은 아래 표의 문장을 쓴다. 나머지 기여 절과 라이선스 절은 그대로 옮긴다.
13. 파일 끝(라이선스 절 마지막 문단 뒤)에 빈 줄과 아래 표의 "끝 줄"을 둔다.
14. 용어는 아래 용어집을 따른다. 생성 블록의 조건 이름과 같은 말을 본문에서도 쓴다.
15. 문장은 짧게, 능동태로, 과장 없이 쓴다. 영어판은 SimpleEnglish 규칙을 따른다. 일본어는 です·ます체, 중국어는 간체와 中英 사이 띄어쓰기, 스페인어는 지역색 없는 표준어와 usted 존대를 쓴다.

제목:

| 한국어 | en | ja | zh | es |
|---|---|---|---|---|
| 설치 | Install | インストール | 安装 | Instalación |
| 보기 | Example | 例 | 示例 | Ejemplo |
| 벤치마크 | Benchmark | ベンチマーク | 基准测试 | Benchmark |
| 규칙 | Rules | ルール | 规则 | Reglas |
| 모드 | Modes | モード | 模式 | Modos |
| 표기 정책 | Spelling policy | 表記方針 | 写法规范 | Política de grafía |
| 자주 묻는 질문 | FAQ | よくある質問 | 常见问题 | Preguntas frecuentes |
| 원본과의 관계 | Relation to the original | 元のプロジェクトとの関係 | 与原项目的关系 | Relación con el proyecto original |
| 기여 | Contributing | 貢献 | 贡献 | Contribuir |
| 라이선스 | License | ライセンス | 许可证 | Licencia |

정해 둔 문장:

| 항목 | en | ja | zh | es |
|---|---|---|---|---|
| 첫머리 문구 | Makes Korean technical documents written by AI read like a maintenance manual. | AIが書いた韓国語の技術文書を、整備マニュアルのように読めるようにします。 | 让 AI 写的韩语技术文档读起来像维修手册。 | Hace que los documentos técnicos en coreano escritos por IA se lean como un manual de mantenimiento. |
| 규칙 블록 문장 | The session-start hook adds a rule block of 2,271 characters to each session. | セッション開始フックは、セッションごとに2,271文字のルールブロックを追加します。 | 会话启动钩子会在每个会话中加入 2,271 个字符的规则块。 | El hook de inicio de sesión añade un bloque de reglas de 2271 caracteres en cada sesión. |
| 보기 소개 | Below are raw outputs from the same model for the same question. We copied both replies without changes. The replies are in Korean, because this skill makes the model write Korean. | 同じ質問に同じモデルが答えた生の出力です。どちらの回答も手を加えずに載せました。このスキルはモデルに韓国語を書かせるものなので、回答は韓国語のままです。 | 以下是同一模型对同一问题的原始输出。两个回答都未作修改。本技能让模型写韩语，所以回答保持韩语原文。 | Estas son salidas originales del mismo modelo para la misma pregunta. Copiamos las dos respuestas sin cambios. Las respuestas están en coreano, porque esta skill hace que el modelo escriba en coreano. |
| 어절 풀이 | An eojeol is a Korean word unit separated by spaces. | 語節（어절）は、韓国語で空白によって区切られる単位です。 | 语节（어절）是韩语中以空格分隔的单位。 | Un eojeol es una unidad del coreano separada por espacios. |
| PR 제목 문단 | Write the PR title as `<type>: <Korean sentence>`, for example `fix: 설정 파일의 지정형을 20자로 제한한다`. The sentence ends in the plain declarative form (`-ㄴ다`). The type is one of feat, fix, perf, refactor, docs, test, chore, and ci. When we merge a PR, its title becomes one line of the changelog. Only feat, fix, and perf make a new release. If you cannot write the title in Korean, write it in English. The maintainer will change it before the merge, and the title check fails until then. | PR のタイトルは `fix: 설정 파일의 지정형을 20자로 제한한다` のように `<種類>: <韓国語の文>` の形で書いてください。文は韓国語の平叙形（`-ㄴ다`）で終えます。種類は feat、fix、perf、refactor、docs、test、chore、ci のいずれかです。PR をマージすると、タイトルがそのまま変更履歴の 1 行になります。新しいリリースを作るのは feat、fix、perf だけです。韓国語でタイトルを書けない場合は英語で書いてください。マージの前にメンテナーが書き直します。それまではタイトルの検査が失敗します。 | PR 标题请写成 `<类型>: <韩语句子>`，例如 `fix: 설정 파일의 지정형을 20자로 제한한다`。句子用韩语的平述形（`-ㄴ다`）结尾。类型是 feat、fix、perf、refactor、docs、test、chore、ci 之一。合并 PR 后，标题会原样成为变更记录中的一行。只有 feat、fix、perf 会产生新版本。如果不会用韩语写标题，可以用英语写，维护者会在合并前改写，在此之前标题检查会失败。 | Escriba el título del PR como `<tipo>: <oración en coreano>`, por ejemplo `fix: 설정 파일의 지정형을 20자로 제한한다`. La oración termina en la forma declarativa llana del coreano (`-ㄴ다`). El tipo es uno de feat, fix, perf, refactor, docs, test, chore y ci. Al fusionar un PR, su título pasa a ser una línea del registro de cambios. Solo feat, fix y perf crean una nueva versión. Si no puede escribir el título en coreano, escríbalo en inglés. El mantenedor lo cambiará antes de fusionar y, hasta entonces, la comprobación del título fallará. |
| 끝 줄 | This translation was not reviewed by a native speaker. Please report errors in an [issue](https://github.com/say8425/SimpleKorean/issues). | この翻訳はネイティブスピーカーの確認を受けていません。誤りは [Issue](https://github.com/say8425/SimpleKorean/issues) でお知らせください。 | 本译文未经母语者审校。如发现错误，请通过 [Issue](https://github.com/say8425/SimpleKorean/issues) 告诉我们。 | Esta traducción no la ha revisado un hablante nativo. Informe de los errores en un [issue](https://github.com/say8425/SimpleKorean/issues). |

규칙 블록 문장의 숫자(2,271)는 계획을 쓸 때의 값이다. 8번의 명령이 다른 숫자를 내면 그 숫자를 쓴다.

용어집:

| 한국어 | en | ja | zh | es |
|---|---|---|---|---|
| 스킬 | skill | スキル | 技能 | skill |
| 에이전트 스킬 | agent skill | エージェントスキル | 智能体技能 | skill de agente |
| 기본 모드 | default mode | 基本モード | 基本模式 | modo básico |
| 엄격 모드 | strict mode | 厳格モード | 严格模式 | modo estricto |
| 점검 모드 | review mode | 点検モード | 检查模式 | modo de revisión |
| 규칙 블록 | rule block | ルールブロック | 规则块 | bloque de reglas |
| 세션 시작 훅 | session-start hook | セッション開始フック | 会话启动钩子 | hook de inicio de sesión |
| 글쓰기 점검 훅 | writing-check hook | 執筆チェックフック | 写作检查钩子 | hook de revisión de escritura |
| 출력 스타일 | output style | 出力スタイル | 输出样式 | estilo de salida |
| 린터 | linter | リンター | 检查器 | linter |
| 어절 | eojeol | 語節 | 语节 | eojeol |
| 번역투 | translationese | 翻訳調 | 翻译腔 | calco |
| 지정형, 지정 표기 | designated spelling | 指定表記 | 规定写法 | grafía designada |
| 표기 | spelling | 表記 | 写法 | grafía |
| 통제 언어 | controlled language | 統制言語 | 受控语言 | lenguaje controlado |
| 블라인드 판정 | blind judgment | ブラインド判定 | 盲评 | evaluación a ciegas |
| 원본 출력 | raw output | 生の出力 | 原始输出 | salida original |
| 변경 기록 | changelog | 変更履歴 | 变更记录 | registro de cambios |

### Task 10: 영어판 `docs/README.en.md`

**Files:**
- Create: `docs/README.en.md`

**Interfaces:**
- Consumes: Task 7의 `language_line("en")`, `TEXT["en"]`, Task 8의 `report.update_readmes`, `make_examples.update_readmes`, Task 9의 `translation_problems`, `readme_outline`.
- Produces: 구조 검사를 통과하는 영어판.

- [ ] **Step 1: 한국어판의 구조를 출력한다**

Run: `python3 -c "import sys; sys.path.insert(0,'evals'); import check_numbers as c; t=open('README.md', encoding='utf-8').read(); print(c.readme_outline(t, 'ko')[:2])"`
Expected: `##` 10개의 수준 목록과 레포 링크 목록. 이 두 목록이 영어판의 확인표다.

- [ ] **Step 2: 번역 규칙대로 `docs/README.en.md`를 쓴다**

"번역 규칙" 절의 1-15번, 제목 표의 en 칸, 정해 둔 문장의 en 칸, 용어집의 en 칸을 따른다. 생성 블록은 빈 표시만 둔다.

- [ ] **Step 3: 생성 블록을 채운다**

```bash
.venv/bin/python - <<'EOF'
import json
import sys
sys.path.insert(0, "evals")
import make_examples
import report
d = "evals/results/2026-10-08"
report.update_readmes(d, json.load(open("evals/scenarios.json", encoding="utf-8")), langs=("en",))
make_examples.update_readmes(d, langs=("en",))
EOF
```

- [ ] **Step 4: 영어판을 검사한다**

Run: `.venv/bin/python -c "import sys; sys.path.insert(0,'evals'); import check_numbers as c; print('\n'.join(c.translation_problems('en')) or 'OK')"`
Expected: `OK`. 문제가 나오면 메시지대로 고치고 다시 돌린다.

- [ ] **Step 5: 커밋한다**

```bash
git add docs/README.en.md
git commit -F - <<'EOF'
docs: README 영어판을 더한다

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01SanRSLxxVtkLMJh1wLGeGZ
EOF
```

### Task 11: 일본어판 `docs/README.ja.md`

**Files:**
- Create: `docs/README.ja.md`

**Interfaces:**
- Consumes: Task 7의 `language_line("ja")`, `TEXT["ja"]`, Task 8의 `report.update_readmes`, `make_examples.update_readmes`, Task 9의 `translation_problems`, `readme_outline`.
- Produces: 구조 검사를 통과하는 일본어판.

- [ ] **Step 1: 한국어판의 구조를 출력한다**

Run: `python3 -c "import sys; sys.path.insert(0,'evals'); import check_numbers as c; t=open('README.md', encoding='utf-8').read(); print(c.readme_outline(t, 'ko')[:2])"`
Expected: `##` 10개의 수준 목록과 레포 링크 목록.

- [ ] **Step 2: 번역 규칙대로 `docs/README.ja.md`를 쓴다**

"번역 규칙" 절의 1-15번, 제목 표의 ja 칸, 정해 둔 문장의 ja 칸, 용어집의 ja 칸을 따른다. 생성 블록은 빈 표시만 둔다.

- [ ] **Step 3: 생성 블록을 채운다**

```bash
.venv/bin/python - <<'EOF'
import json
import sys
sys.path.insert(0, "evals")
import make_examples
import report
d = "evals/results/2026-10-08"
report.update_readmes(d, json.load(open("evals/scenarios.json", encoding="utf-8")), langs=("ja",))
make_examples.update_readmes(d, langs=("ja",))
EOF
```

- [ ] **Step 4: 일본어판을 검사한다**

Run: `.venv/bin/python -c "import sys; sys.path.insert(0,'evals'); import check_numbers as c; print('\n'.join(c.translation_problems('ja')) or 'OK')"`
Expected: `OK`.

- [ ] **Step 5: 커밋한다**

```bash
git add docs/README.ja.md
git commit -F - <<'EOF'
docs: README 일본어판을 더한다

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01SanRSLxxVtkLMJh1wLGeGZ
EOF
```

### Task 12: 중국어판 `docs/README.zh.md`

**Files:**
- Create: `docs/README.zh.md`

**Interfaces:**
- Consumes: Task 7의 `language_line("zh")`, `TEXT["zh"]`, Task 8의 `report.update_readmes`, `make_examples.update_readmes`, Task 9의 `translation_problems`, `readme_outline`.
- Produces: 구조 검사를 통과하는 중국어(간체)판.

- [ ] **Step 1: 한국어판의 구조를 출력한다**

Run: `python3 -c "import sys; sys.path.insert(0,'evals'); import check_numbers as c; t=open('README.md', encoding='utf-8').read(); print(c.readme_outline(t, 'ko')[:2])"`
Expected: `##` 10개의 수준 목록과 레포 링크 목록.

- [ ] **Step 2: 번역 규칙대로 `docs/README.zh.md`를 쓴다**

"번역 규칙" 절의 1-15번, 제목 표의 zh 칸, 정해 둔 문장의 zh 칸, 용어집의 zh 칸을 따른다. 간체만 쓴다. 생성 블록은 빈 표시만 둔다.

- [ ] **Step 3: 생성 블록을 채운다**

```bash
.venv/bin/python - <<'EOF'
import json
import sys
sys.path.insert(0, "evals")
import make_examples
import report
d = "evals/results/2026-10-08"
report.update_readmes(d, json.load(open("evals/scenarios.json", encoding="utf-8")), langs=("zh",))
make_examples.update_readmes(d, langs=("zh",))
EOF
```

- [ ] **Step 4: 중국어판을 검사한다**

Run: `.venv/bin/python -c "import sys; sys.path.insert(0,'evals'); import check_numbers as c; print('\n'.join(c.translation_problems('zh')) or 'OK')"`
Expected: `OK`.

- [ ] **Step 5: 커밋한다**

```bash
git add docs/README.zh.md
git commit -F - <<'EOF'
docs: README 중국어판을 더한다

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01SanRSLxxVtkLMJh1wLGeGZ
EOF
```

### Task 13: 스페인어판 `docs/README.es.md`

**Files:**
- Create: `docs/README.es.md`

**Interfaces:**
- Consumes: Task 7의 `language_line("es")`, `TEXT["es"]`, `grouped`, `percent`, Task 8의 `report.update_readmes`, `make_examples.update_readmes`, Task 9의 `translation_problems`, `readme_outline`.
- Produces: 구조 검사를 통과하는 스페인어판.

- [ ] **Step 1: 한국어판의 구조를 출력한다**

Run: `python3 -c "import sys; sys.path.insert(0,'evals'); import check_numbers as c; t=open('README.md', encoding='utf-8').read(); print(c.readme_outline(t, 'ko')[:2])"`
Expected: `##` 10개의 수준 목록과 레포 링크 목록.

- [ ] **Step 2: 번역 규칙대로 `docs/README.es.md`를 쓴다**

"번역 규칙" 절의 1-15번, 제목 표의 es 칸, 정해 둔 문장의 es 칸, 용어집의 es 칸을 따른다. 본문에 손으로 쓰는 숫자도 es 표기를 따른다(네 자리 수는 구분 기호 없이, 예: FAQ의 "1104"). 생성 블록은 빈 표시만 둔다.

- [ ] **Step 3: 생성 블록을 채운다**

```bash
.venv/bin/python - <<'EOF'
import json
import sys
sys.path.insert(0, "evals")
import make_examples
import report
d = "evals/results/2026-10-08"
report.update_readmes(d, json.load(open("evals/scenarios.json", encoding="utf-8")), langs=("es",))
make_examples.update_readmes(d, langs=("es",))
EOF
```

- [ ] **Step 4: 스페인어판을 검사한다**

Run: `.venv/bin/python -c "import sys; sys.path.insert(0,'evals'); import check_numbers as c; print('\n'.join(c.translation_problems('es')) or 'OK')"`
Expected: `OK`.

- [ ] **Step 5: 커밋한다**

```bash
git add docs/README.es.md
git commit -F - <<'EOF'
docs: README 스페인어판을 더한다

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01SanRSLxxVtkLMJh1wLGeGZ
EOF
```

### Task 14: 한국어 README를 잇고 `main`에 번역판 검사를 연결한다

**Files:**
- Modify: `README.md:1-11`, `evals/check_numbers.py`(독스트링, `REQUIRED`, `main`)
- Test: `evals/tests/test_check_numbers.py`

**Interfaces:**
- Consumes: Task 9의 `check_readme_structure`, `check_translation`, `check_benchmark(..., stats=)`, Task 10-13의 번역판.
- Produces: `REQUIRED`에 번역판 네 개가 들어간다. `main()`이 다섯 README를 모두 검사한다.

- [ ] **Step 1: 실패하는 시험을 쓴다**

`evals/tests/test_check_numbers.py` 끝에 더한다.

```python
def test_main_requires_every_readme():
    assert {i18n.README[lang] for lang in i18n.LANGS} <= set(cn.REQUIRED)
```

Run: `python3 evals/tests/run.py evals/tests/test_check_numbers.py`
Expected: `FAIL test_check_numbers.test_main_requires_every_readme`.

- [ ] **Step 2: 한국어 README 첫머리를 바꾼다**

첫머리 문구 블록과 배지 블록 사이에 언어 선택 줄을 넣는다. 블록은 `python3 -c "import sys; sys.path.insert(0,'evals'); import readme_i18n as i; print(i.language_line('ko'))"`의 출력을 그대로 쓴다.

```html
<p align="center">
  <strong>AI가 쓴 한국어 기술 문서를 정비 매뉴얼처럼 읽히게 합니다.</strong>
</p>

<p align="center">
  한국어 | <a href="docs/README.en.md">English</a> | <a href="docs/README.ja.md">日本語</a> | <a href="docs/README.zh.md">中文</a> | <a href="docs/README.es.md">Español</a>
</p>

<p align="center">
```

"SimpleKorean is an agent skill that makes LLMs write plain Korean …"로 시작하는 영어 문단과 그 뒤의 빈 줄을 지운다. 계획을 쓸 때 이 두 변경을 넣은 README를 문서 관문으로 돌려 오류와 경고가 0개임을 확인했다.

- [ ] **Step 3: `main`에 번역판 검사를 연결한다**

`evals/check_numbers.py`의 `REQUIRED`를 바꾼다.

```python
REQUIRED = ("README.md", "CHANGELOG.md", "examples/before-after.md", "evals/scenarios.json",
            "evals/calibration/RECORD.md", "evals/calibration/hits.tsv", "prompts/system-prompt.md",
            "output-styles/simple-korean.md") + tuple(VERSION_PATTERNS) + tuple(i18n.README[lang] for lang in i18n.LANGS[1:])
```

`main`을 바꾼다.

```python
def main():
    missing = sorted({rel for rel in REQUIRED if not (ROOT / rel).is_file()})
    if missing:
        print("MISMATCH")
        print("\n".join(f" - 파일이 없습니다: {rel}" for rel in missing))
        return 1
    readme, changelog = _read("README.md"), _read("CHANGELOG.md")
    scenarios, prompt = json.loads(_read("evals/scenarios.json")), _read("prompts/system-prompt.md")
    bench = report.README_BLOCK.search(readme)
    stats = None
    if bench and metrics.easy_word_counts("확인합니다.") is not None:
        stats = report.benchmark_stats(ROOT / bench.group(1), scenarios)
    problems = (check_benchmark(readme, changelog, scenarios, stats=stats)
                + check_examples(readme, _read("examples/before-after.md"))
                + check_calibration(changelog)
                + check_rule_block(prompt, _read("output-styles/simple-korean.md"), _read("skills/simple-korean/SKILL.md"))
                + check_triggers(_read("skills/simple-korean/SKILL.md"))
                + check_block_size(readme, prompt)
                + check_readme_structure(readme, "ko", readme)
                + check_versions({name: _read(name) for name in VERSION_PATTERNS}))
    if stats:
        for lang in i18n.LANGS[1:]:
            problems += check_translation(lang, _read(i18n.README[lang]), readme, scenarios, prompt, stats)
    if problems:
        print("MISMATCH")
        for problem in problems:
            print(" -", problem)
        return 1
    print("check_numbers OK: 공개한 수치와 글이 원본 파일과 같습니다")
    return 0
```

모듈 독스트링의 검사 목록 첫 두 줄을 바꾼다.

```python
- README 다섯 개의 벤치마크 블록과 RESULTS.md를 원본 출력에서 다시 만든 글과 비교한다(report.py, readme_i18n.py).
- README 다섯 개의 보기 블록과 examples/before-after.md의 인용 블록을 원본 출력과 비교한다(make_examples.py).
- 번역판의 제목, 레포 링크, 언어 선택 줄, 블록 표시가 한국어판과 맞는지 본다.
```

- [ ] **Step 4: 전체 확인을 돌린다**

Run: 전체 확인.
Expected: 모두 통과. `check_numbers OK`는 이제 다섯 README를 모두 대조한 결과다.

- [ ] **Step 5: 고의로 깨서 검사가 잡는지 본다**

```bash
S=${S:-$(mktemp -d)} && cp docs/README.ja.md "$S/ja.bak"
python3 - <<'EOF'
from pathlib import Path
p = Path("docs/README.ja.md")
text = p.read_text(encoding="utf-8")
p.write_text(text.replace("\n## ", "\n### ", 1), encoding="utf-8")
EOF
.venv/bin/python evals/check_numbers.py | grep "제목 수준"
cp "$S/ja.bak" docs/README.ja.md && .venv/bin/python evals/check_numbers.py
```
Expected: 첫 실행은 `docs/README.ja.md: 제목 수준이 한국어판과 다릅니다` 줄을 출력한다. 되돌린 뒤에는 `check_numbers OK`.

- [ ] **Step 6: 커밋한다**

```bash
git add README.md evals/check_numbers.py evals/tests/test_check_numbers.py
git commit -F - <<'EOF'
docs: 한국어 README에 언어 선택 줄을 두고 번역판 검사를 잇는다

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01SanRSLxxVtkLMJh1wLGeGZ
EOF
```

### Task 15: PR 3을 열고, 화면을 확인하고, 병합을 확인받는다

**Files:** 없음(GitHub 작업)

**Interfaces:**
- Consumes: Task 7-14의 커밋.
- Produces: 병합한 PR 3.

- [ ] **Step 1: 전체 확인을 돌리고 브랜치를 올린다**

Run: 전체 확인. Expected: 모두 통과.

```bash
git push -u origin docs/readme-languages
```

- [ ] **Step 2: GitHub 화면에서 다섯 README를 본다**

브라우저로 `https://github.com/say8425/SimpleKorean/blob/docs/readme-languages/README.md`와 `docs/README.{en,ja,zh,es}.md`를 연다. 확인할 것: 언어 선택 줄이 가운데에 있고 링크가 맞는 파일로 간다, 배지가 `version v1.0.0`으로 뜬다, 두 표가 깨지지 않는다, 상대 링크(LICENSE, SKILL.md, RESULTS.md, examples)가 열린다.

- [ ] **Step 3: 화면을 찍는다**

같은 화면에서 첫머리(첫머리 문구, 언어 선택 줄, 배지, 첫 문단)를 찍는다. 한국어판은 `main`의 README(바뀌기 전)와 이 브랜치의 README(바뀐 뒤)를 찍고, 번역판 네 개는 이 브랜치에서 찍는다. 파일은 `.superpowers/readme-languages/shots/`에 둔다.

- [ ] **Step 4: PR을 연다**

`github-image-upload` 스킬로 `.superpowers/readme-languages/shots/`의 이미지를 올려 링크를 받는다. `S=${S:-$(mktemp -d)}`로 임시 폴더를 정하고, 본문 파일 `$S/pr3-body.md`를 이 틀로 쓰고, `## Screenshots`에 받은 이미지 링크를 넣는다.

~~~markdown
## 바뀌는 것

- README를 영어, 일본어, 중국어(간체), 스페인어로 옮겼습니다(`docs/README.<언어>.md`). 다섯 파일 모두 첫머리에 언어 선택 줄이 있습니다.
- 벤치마크 블록과 보기 블록은 `evals/readme_i18n.py`의 언어별 문장 틀로 생성기가 씁니다. 인용한 모델 출력은 모든 언어에서 한국어 원문입니다.
- `check_numbers.py`가 다섯 README의 생성 블록을 글자 하나까지 대조하고, 번역판의 제목·레포 링크·언어 선택 줄·블록 표시를 한국어판과 대조합니다.
- 한국어 README 첫머리의 영어 문단을 지웠습니다. 영어판이 그 역할을 맡습니다.
- 번역은 원어민 검토를 받지 않았고, 번역판마다 끝에 오류 제보를 부탁하는 줄을 두었습니다.

## Screenshots

<이미지 링크: 한국어판 전, 한국어판 후, en, ja, zh, es>

## 시험 계획

- [ ] `check`, `python39`, `pr-title`이 통과합니다.
- [ ] GitHub 화면에서 다섯 README의 언어 링크, 배지, 표, 상대 링크가 맞습니다.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01SanRSLxxVtkLMJh1wLGeGZ
~~~

```bash
gh pr create --base main --head docs/readme-languages --title "docs: README를 영어, 일본어, 중국어, 스페인어로 옮긴다" --body-file "$S/pr3-body.md"
```

- [ ] **Step 5: CI를 기다리고 코드 리뷰를 받는다**

```bash
gh pr checks --watch --interval 20
```
Expected: `check`, `python39`, `pr-title`이 모두 `pass`. 그다음 `superpowers:requesting-code-review` 스킬로 리뷰한다. 번역판은 언어마다 용어집과 정해 둔 문장을 지켰는지도 보게 한다.

- [ ] **Step 6: 사용자에게 보고하고 병합 확인을 받는다**

PR 링크, CI 결과, 리뷰 결과, 스크린샷을 보고하고 병합해도 되는지 묻는다. 확인을 받으면 병합한다.

```bash
gh pr merge docs/readme-languages --squash --delete-branch
```

- [ ] **Step 7: 병합 뒤 확인**

`main`의 `check`, `python39`, `release`가 통과하는지 본다. `release` 로그에는 사용자에게 보이는 커밋이 없다는 줄이 있어야 한다(docs 유형). 레포 첫 화면의 언어 선택 줄에서 네 번역판이 열리는지 본다.
