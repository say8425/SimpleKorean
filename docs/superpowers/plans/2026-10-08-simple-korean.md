# SimpleKorean v1 구현 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** LLM이 기술 문서와 채팅 답변을 쉬운 한국어로 쓰게 하는 에이전트 스킬 SimpleKorean v1.0.0을 만들고, 한국어로 효과를 측정한 뒤 `say8425/SimpleKorean`으로 공개한다.

**Architecture:** 원본 AminBlg/SimpleEnglish v2.1.1의 구조를 따른다. 구성은 스킬, 출력 스타일, 시스템 프롬프트, 훅 3개, 린터, 벤치마크, 수치 검증 CI다. 린터는 표준 라이브러리만 쓰는 Python 모듈 넷(`ko_text`, `ko_rules`, `ko_terms`, `ko_lint`)으로 나눈다. 훅, 벤치마크, 수치 검증이 이 모듈을 함께 쓴다. 규칙과 단어 목록은 한국어 문법과 측정 자료(`docs/research/`)에 맞춰 새로 쓴다.

**Tech Stack:** Python 3.9+ 표준 라이브러리(린터, 훅), Node.js 24 내장 모듈(세션 시작 훅), Claude Code CLI 2.1.294의 `claude -p`(벤치마크), kiwipiepy 0.24.0(측정 전용, Apache-2.0), uv 0.8(측정용 가상 환경), GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-10-08-simple-korean-design.md`. 근거 자료는 `docs/research/`의 보고서 2개와 CSV다. 원본 참고용 클론은 스크래치 디렉터리의 `upstream/SimpleEnglish`(v2.1.1, `a6fcb4f`)에 있다. 클론이 없으면 `git clone https://github.com/AminBlg/SimpleEnglish.git`으로 받고 `git checkout a6fcb4f`를 실행한다.

## Global Constraints

- 린터와 훅 코드(`evals/ko_*.py`, `src/hooks/lint_hook.py`)는 표준 라이브러리만 쓰고 Python 3.9에서 돌아야 한다. `match` 문, 실행 시점의 `X | Y` 타입 표기, 3.10 이상의 API를 쓰지 않는다. macOS 기본 `/usr/bin/python3`(3.9.6)로 확인한다.
- 세션 시작 훅(`src/hooks/simple-korean-activate.js`)은 Node 내장 모듈만 쓴다. 출력은 9,500자 이하다.
- 이름: 스킬·플러그인·마켓플레이스 `simple-korean`, 출력 스타일 `simple-korean:simple-korean`, 린트 제외 환경변수 `SIMPLE_KOREAN_LINT_EXCLUDE`, 프로젝트 설정 파일 `.simple-korean.json`.
- 린터 인터페이스는 원본과 같다: `lint(text, text_type)`, `lint_detail(text, text_type)`, `reader_check(text)`, `--self-test`, `--type`, `--gate`. 새 인자는 키워드 인자(`strict`, `config`, `path`)로만 더한다.
- 문장 길이 상한: 절차문 15어절, 설명문 20어절. 초기값이고 Task 15에서만 바꾼다.
- 기본 문체: 서술 "-습니다", 지시 "-하세요".
- 단어 목록 지정형: ③ 레포지토리, 바디, 칼럼, 대상 / ④ 리디렉션, 리팩터링 / ⑤ 오류, 매개변수, 사용자, 기본값, 배포 / ⑥ 기본값, 매개변수, 반환값, 오픈소스(붙여 씀).
- 한글 비율 문턱: 0.3. 훅은 이보다 낮은 파일과 답변을 건너뛴다.
- 라이선스: 코드와 목록은 MIT. LICENSE에 `Copyright (c) 2026 AminBlg`와 `Copyright (c) 2026 say8425` 두 줄을 둔다. 기초 어휘 등급 목록만 공공누리 제1유형(출처 표시)이다. 사전 뜻풀이와 코퍼스 원문은 싣지 않는다.
- 버전 `1.0.0`: SKILL.md `metadata.version`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `.codex-plugin/plugin.json`, README 배지가 같아야 한다.
- 측정: 모델 `claude-sonnet-5-5`, effort `low`, 판정 모델 `claude-opus-5-5`, 격리 옵션 `--setting-sources "" --strict-mcp-config`. 문서 48회, 답변 32회, 판정 32회.
- 스킬 문서(SKILL.md, `skills/simple-korean/references/*.md`, `prompts/system-prompt.md`, `output-styles/simple-korean.md`, README.md)는 `python3 evals/ko_lint.py --gate`를 통과해야 한다(오류 0).
- 파일은 800줄을 넘지 않고 함수는 50줄 이하다. 함수는 입력을 바꾸지 않고 새 값을 돌려준다.
- npm과 npx를 쓰지 않는다. 이 레포에는 JS 의존성이 없다.
- GitHub 레포는 Task 20에서 사용자 확인을 받은 뒤에만 만든다.

## Review Focus

1. 유니코드 NFD로 들어온 한국어(macOS에서 복사한 글): NFC 입력과 같은 위반이 나와야 한다. Task 6의 `test_nfd_input_matches_nfc`가 고정한다.
2. CRLF 줄바꿈 문서: LF 문서와 같은 위반과 같은 줄 번호가 나와야 한다. Task 6의 `test_crlf_matches_lf`가 고정한다.
3. 영어가 대부분인 마크다운 파일과 영어 답변: 훅이 아무것도 알리지 않아야 한다. Task 11의 `test_post_tool_use_skips_english_file`와 `test_stop_skips_english_reply`가 고정한다.
4. 깨진 `.simple-korean.json`: CLI는 설정 파일 경로를 담은 오류로 멈춘다. 훅은 기본 설정으로 점검하고 설정 문제를 한 줄 알린다. 어느 쪽도 세션을 멈추지 않는다. Task 6의 `test_cli_rejects_broken_config`와 Task 11의 `test_post_tool_use_reports_broken_config`가 고정한다.
5. 큰 문서(약 300KB): 훅 제한 시간 10초 안에 끝나야 한다. Task 6의 `test_large_document_is_fast`가 5초 상한으로 고정한다.

## 스펙과 다른 점 (계획을 쓰며 정한 것)

1. 기본 모드의 일관성 기준: 스펙은 "문서에 먼저 나온 형태"였다. 지정형이 문서에 있으면 지정형을 기준으로 하고, 없을 때만 먼저 나온 형태를 쓴다. 맞는 형태(예: 디렉터리)가 혼용 경고를 받는 일을 막기 위해서다.
2. "대상"은 일반어라 일관성 검사에서 뺀다(`"mix": false`). "적용 대상"과 "빌드 타깃"이 함께 나와도 경고하지 않는다.
3. 측정 격리에 `--strict-mcp-config`를 더한다. 2026-10-08 탐침에서 `--setting-sources ""`만 주면 MCP 서버 15개가 기준선에 들어왔다. 내장 플러그인 4개(`*@builtin`)는 두 조건에 똑같이 들어가므로 남긴다. 사용자 규칙 파일과 응답 언어 지시는 들어오지 않았다.
4. 형태소 분석기는 kiwipiepy 0.24.0(Apache-2.0)이다. CI는 `check_numbers.py`가 쉬운 단어 비율을 다시 계산하도록 이 패키지를 설치한다.
5. CI는 Python 3.12 작업과 Python 3.9 작업(린터와 훅 테스트)을 함께 돌린다.
6. 파일을 더한다: `evals/bench_common.py`(claude 호출 공용), `evals/report.py`(집계와 표 그리기), `evals/tests/`(단위 테스트와 실행기), `tools/basic-vocabulary/extract.py`(xlsx 추출), `evals/calibration/`(보정 자료).
7. README에는 답변 표와 문서 표만 싣는다. 표기 분포 표는 잡을 형태를 그대로 담아 린트 관문에 걸리므로 RESULTS.md에만 싣는다.
8. 슬롭 어휘의 문턱은 출처 10곳 가운데 2곳이다. 계획 검증 때 문턱 3으로 돌리니 11개만 남았다. 출처들이 단어를 나열하기보다 패턴을 설명하는 글이기 때문이다. 문턱 2는 원본 비율(122곳 가운데 8곳, 약 6.6%)보다 엄격하고 20개가 남는다. 20개는 사람이 바로 읽을 수 있어 TypeSafe Jev는 쓰지 않는다.
9. 압력 시험(Task 16)을 본 측정(Task 17)보다 먼저 돌린다. 압력 시험에서 스킬 문서를 고치면, 측정한 판본과 공개하는 판본이 같아야 하기 때문이다.
10. 압력 시험은 이 레포지토리를 `--plugin-dir`로 올린 실제 플러그인으로 돌리고, 읽기 도구와 Skill 도구를 허용한다. 벤치마크는 원본처럼 SKILL.md 본문을 프롬프트에 붙이고 도구를 끈다.
11. 세션 시작 훅이 SKILL.md와 `references/rule-catalog.md`의 절대 경로를 알린다(Task 10). 계획 검증 때 상대 경로만 알린 판본으로 압력 시험 2를 돌리니, 모델이 규칙 목록을 읽지 않고 자체 번호를 붙였다.
12. 선택 교차 확인(Haiku 4.5)은 하지 않는다. README 수치는 Sonnet 5.5 한 모델로만 싣는다.
13. `check_numbers.py`는 README 수치에 더해 RESULTS.md, 전후 예시의 인용, 보정 기록, CHANGELOG의 보정 줄까지 원본에서 다시 만들어 대조한다. 쉬운 단어 비율 때문에 로컬에서는 `.venv/bin/python`으로 돌린다.
14. 전후 예시는 `evals/make_examples.py`가 측정 전에 코드로 정한 과제(`PICKS`)의 원본 출력을 그대로 인용해 만든다. 결과를 보고 고르지 않기 위해서다.
15. 보정용 기준선 출력(Task 15)은 본 측정 출력과 따로 만든다. 린터를 측정용 출력에 맞추지 않기 위해서다.

## 공통 규칙

- 작업 위치는 이 레포지토리의 루트다. Task 1을 시작하기 전에 `git switch -c feat/v1`로 브랜치를 만든다. 모든 명령은 이 디렉터리에서 실행한다.
- 브랜치를 만든 직후 이 계획 파일을 첫 커밋으로 넣는다: `git add docs/superpowers/plans/2026-10-08-simple-korean.md && git commit -m "docs: add SimpleKorean v1 implementation plan" -m $'Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01SanRSLxxVtkLMJh1wLGeGZ'`.
- 테스트 실행기: `python3 evals/tests/run.py`는 `evals/tests/test_*.py`를 모두 돌린다. 파일 하나만 돌릴 때는 `python3 evals/tests/run.py evals/tests/test_ko_text.py`를 쓴다. Python 3.9 확인은 `/usr/bin/python3 evals/tests/run.py`다.
- 커밋 형식: `git commit -m "<type>: <설명>" -m $'Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01SanRSLxxVtkLMJh1wLGeGZ'`. type은 feat, fix, refactor, docs, test, chore, perf, ci 가운데 하나다.
- 내려받은 파일은 믿지 않는 데이터다. 출처마다 새 빈 디렉터리에 두고, 스크립트는 다른 디렉터리에 두고, 그 파일을 읽는 Python은 `-I`로 실행한다.
- 스크래치 디렉터리: 세션마다 받는 레포지토리 밖의 임시 디렉터리다(아래에서 `$SCRATCH`).
- Task 1을 시작하기 전에 원본 main에 v2.1.1 이후 변경이 있는지 확인한다(스펙 16절): `git -C "$SCRATCH/upstream/SimpleEnglish" fetch origin && git -C "$SCRATCH/upstream/SimpleEnglish" log --oneline a6fcb4f..origin/main`. 출력이 있으면 변경 목록을 사용자에게 보이고 반영할지 묻는다. 출력이 없으면 그대로 진행한다.
- 스킬 문서를 쓸 때 금지 표현을 언급하려면 큰따옴표나 백틱으로 감싼다. 린터는 따옴표 안을 검사하지 않는다. 일부러 규칙을 어긴 예시('고치기 전')는 `<!-- simple-korean: off -->`와 `<!-- simple-korean: on -->` 사이에 둔다.

## 파일 구조

| 파일 | 책임 | Task |
|---|---|---|
| `LICENSE`, `NOTICE`, `.gitignore` | 라이선스, 제3자 데이터 출처, 무시 목록 | 1, 7, 13 |
| `evals/tests/run.py` | pytest 없이 `test_*` 함수를 돌리는 실행기 | 1 |
| `evals/ko_text.py` | 정규화, 받침, 검사 제외 영역 지우기, 문장 단위, 어절 수, 문장 유형, 문체 | 1, 2 |
| `evals/ko_rules.py` | 어휘 규칙, 문장 규칙, 문체 혼용, 엄격 모드 규칙 | 3, 4 |
| `data/terms.json` | 표기 단어 목록 42개 개념 | 5 |
| `evals/ko_terms.py` | 단어 목록과 프로젝트 설정 읽기, 표기 검사 | 5 |
| `evals/ko_lint.py` | 공개 API, CLI, 자체 시험 고정 예문 | 6 |
| `evals/slop.tsv`, `tools/slop-lexicon/` | 한국어 슬롭 어휘와 그것을 만드는 스크립트, 출처 목록 | 7 |
| `skills/simple-korean/SKILL.md` | 스킬 본문 | 8 |
| `prompts/system-prompt.md`, `output-styles/simple-korean.md` | 같은 규칙 블록 | 8 |
| `skills/simple-korean/references/*.md` | 규칙 목록, 엄격 모드, 바꿀 말, 문서 유형 | 9 |
| `src/hooks/simple-korean-activate.js` (+ `.test.js`) | 세션 시작 때 규칙 블록 주입 | 10 |
| `src/hooks/lint_hook.py` (+ `test_lint_hook.py`) | 파일 점검과 답변 점검 | 11 |
| `.claude-plugin/`, `.codex-plugin/`, `.agents/plugins/`, `src/hooks/README.md`, `src/hooks/package.json` | 플러그인 배포 | 12 |
| `tools/basic-vocabulary/extract.py`, `data/basic-vocabulary/` | 기초 어휘 등급 목록 추출 | 13 |
| `evals/metrics.py` | 쉬운 단어 비율(선택 의존성) | 13 |
| `evals/bench_common.py`, `evals/run_bench.py`, `evals/run_reply_bench.py`, `evals/report.py`, `evals/scenarios.json`, `evals/reply_scenarios.json` | 벤치마크, 집계, 표 | 14 |
| `evals/calibration/compliant-ko.md`, `evals/calibration/hits.py` | 규칙을 지킨 예문, 거짓 일치를 나열하고 정밀도를 세는 보정 도구 | 15 |
| `evals/calibration/baseline/`, `hits.tsv`, `RECORD.md` | 보정용 기준선 출력, 판정, 보정 기록 | 15 |
| `evals/pressure-tests.md`, `evals/run_pressure.py` | 압력 시험 시나리오와 기록, 실행기 | 16 |
| `evals/results/<날짜>/` | 원본 출력(`pressure/`는 Task 16, 나머지는 Task 17)과 RESULTS.md | 16, 17 |
| `evals/make_examples.py`, `evals/check_numbers.py`, `.github/workflows/check.yml` | 전후 예시 생성, 수치 검증, CI | 18 |
| `README.md`, `CHANGELOG.md`, `examples/before-after.md` | 문서와 전후 예시 | 19 |

---

## 단계 A: 린터

### Task 1: 뼈대와 한국어 텍스트 기본 도구

**Files:**
- Create: `LICENSE`, `.gitignore`, `evals/tests/run.py`, `evals/ko_text.py`
- Test: `evals/tests/test_ko_text.py`

**Interfaces:**
- Consumes: 없음
- Produces: `ko_text.nfc(text) -> str`(NFC 정규화, CRLF와 CR을 LF로), `is_hangul(ch) -> bool`, `jongseong(ch) -> int`(받침 없음 0, ㄹ은 `JONG_RIEUL` 8, 한글이 아니면 -1), `mask(text, quotes=True) -> str`(같은 길이, 같은 줄 수), `strip_frontmatter(text) -> str`, `line_of(text, pos) -> int`, `hangul_ratio(text) -> float`, 정규식 상수 `OFF_REGION`, `FENCE`, `COMMENT`, `INLINE_CODE`, `URL`, `QUOTES`, 내부 함수 `_blank(match)`

- [ ] **Step 1: 브랜치와 뼈대 파일을 만든다**

```bash
git switch -c feat/v1
mkdir -p evals/tests
```

`LICENSE`:

```text
MIT License

Copyright (c) 2026 AminBlg
Copyright (c) 2026 say8425

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

`.gitignore`:

```text
__pycache__/
*.pyc
.venv/
.DS_Store
tools/slop-lexicon/cache/
tools/basic-vocabulary/*.xlsx
```

`evals/tests/run.py`:

```python
#!/usr/bin/env python3
"""evals/tests의 test_* 함수를 모두 돌린다. pytest 없이 표준 라이브러리로 돈다.

    python3 evals/tests/run.py                         # 전부
    python3 evals/tests/run.py evals/tests/test_ko_text.py   # 파일 하나
"""
import importlib.util
import sys
import traceback
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))


def run(paths):
    """파일마다 test_로 시작하는 함수를 돌리고 실패 수를 돌려준다."""
    failures = 0
    for path in paths:
        spec = importlib.util.spec_from_file_location(path.stem, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        for name in sorted(n for n in dir(module) if n.startswith("test_")):
            try:
                getattr(module, name)()
                print(f"ok   {path.stem}.{name}")
            except Exception:  # noqa: BLE001  모든 실패를 모아 보고한다
                failures += 1
                print(f"FAIL {path.stem}.{name}")
                traceback.print_exc()
    return failures


if __name__ == "__main__":
    selected = [Path(a).resolve() for a in sys.argv[1:]] or sorted(HERE.glob("test_*.py"))
    sys.exit(1 if run(selected) else 0)
```

- [ ] **Step 2: 실패하는 테스트를 쓴다**

`evals/tests/test_ko_text.py`:

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import ko_text  # noqa: E402


def test_nfc_joins_decomposed_hangul_and_normalizes_newlines():
    assert ko_text.nfc("가") == "가"
    assert ko_text.nfc("가\r\n나\r다") == "가\n나\n다"


def test_jongseong_reads_final_consonant():
    assert ko_text.jongseong("가") == 0
    assert ko_text.jongseong("갈") == ko_text.JONG_RIEUL
    assert ko_text.jongseong("될") == ko_text.JONG_RIEUL
    assert ko_text.jongseong("는") == 4
    assert ko_text.jongseong("a") == -1


def test_mask_keeps_length_and_lines():
    text = "앞 `코드` 뒤\n```\n블록 안\n```\n\"인용\" 끝 https://example.com/x\n"
    masked = ko_text.mask(text)
    assert len(masked) == len(text)
    assert masked.count("\n") == text.count("\n")
    assert "코드" not in masked and "블록 안" not in masked
    assert "인용" not in masked and "example" not in masked
    assert "앞" in masked and "끝" in masked


def test_mask_off_region_and_comments():
    text = "보임\n<!-- simple-korean: off -->\n숨김 — 대시\n<!-- simple-korean: on -->\n다시 보임\n"
    masked = ko_text.mask(text)
    assert "숨김" not in masked and "—" not in masked
    assert "보임" in masked and "다시 보임" in masked


def test_mask_unclosed_off_region_runs_to_end():
    masked = ko_text.mask("앞\n<!-- simple-korean: off -->\n끝까지 숨김\n")
    assert "끝까지" not in masked and "앞" in masked


def test_mask_quotes_optional():
    text = '그는 "멈춰"라고 했습니다.'
    assert "멈춰" not in ko_text.mask(text)
    assert "멈춰" in ko_text.mask(text, quotes=False)


def test_single_quote_does_not_eat_english_contractions():
    text = "it's fine and don't worry"
    assert ko_text.mask(text) == text


def test_strip_frontmatter_keeps_line_count():
    text = "---\nname: x\n설명: 강력한\n---\n본문입니다.\n"
    stripped = ko_text.strip_frontmatter(text)
    assert stripped.count("\n") == text.count("\n")
    assert "강력한" not in stripped and "본문입니다." in stripped


def test_line_of_counts_from_one():
    text = "첫째\n둘째\n셋째"
    assert ko_text.line_of(text, 0) == 1
    assert ko_text.line_of(text, text.index("셋째")) == 3


def test_hangul_ratio_ignores_code():
    assert ko_text.hangul_ratio("이 문서는 한국어로 씁니다.") > 0.9
    assert ko_text.hangul_ratio("This document is written in English.") == 0.0
    assert ko_text.hangul_ratio("```\nprint('hello world')\n```\n한국어 설명입니다.") > 0.9
    assert ko_text.hangul_ratio("") == 0.0
```

- [ ] **Step 3: 테스트를 돌려 실패를 확인한다**

Run: `python3 evals/tests/run.py evals/tests/test_ko_text.py`
Expected: `ModuleNotFoundError: No module named 'ko_text'`로 실패하고 종료 코드가 1이다.

- [ ] **Step 4: 최소 구현을 쓴다**

`evals/ko_text.py`:

```python
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
```

- [ ] **Step 5: 테스트를 돌려 통과를 확인한다**

Run: `python3 evals/tests/run.py evals/tests/test_ko_text.py && /usr/bin/python3 evals/tests/run.py evals/tests/test_ko_text.py`
Expected: 두 번 모두 `ok` 10줄, 종료 코드 0.

- [ ] **Step 6: 커밋한다**

```bash
git add LICENSE .gitignore evals/tests/run.py evals/tests/test_ko_text.py evals/ko_text.py
git commit -m "feat: add Korean text helpers and test runner" -m $'Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01SanRSLxxVtkLMJh1wLGeGZ'
```

### Task 2: 문장 단위, 어절 수, 문장 유형, 문체

**Files:**
- Modify: `evals/ko_text.py` (import 블록 교체, 파일 끝에 추가)
- Test: `evals/tests/test_ko_text.py` (파일 끝에 추가)

**Interfaces:**
- Consumes: Task 1의 `nfc`, `_blank`, `OFF_REGION`, `FENCE`, `COMMENT`, `INLINE_CODE`, `URL`, `QUOTES`
- Produces: `Unit = namedtuple("Unit", "text line kind")`(kind는 `"prose"`, `"list"`, `"table"`), `units(text) -> list[Unit]`, `split_sentences(text) -> list[tuple[str, int]]`, `eojeol_count(sentence) -> int`, `sentence_kind(sentence) -> "procedural" | "descriptive" | None`, `register(sentence) -> "hapsyo" | "hapsyo_imp" | "haeyo_imp" | "haeyo" | "haera" | None`, `tail(sentence) -> str`. `units()`의 텍스트에서 인라인 코드는 `CODE`, URL은 `URL`, 따옴표 인용은 `QUOTE`로 바뀐다.

- [ ] **Step 1: 실패하는 테스트를 덧붙인다**

`evals/tests/test_ko_text.py` 끝에 덧붙인다:

```python
def test_split_sentences_on_terminal_punctuation():
    got = [s for s, _ in ko_text.split_sentences('로그를 읽으세요. 그다음 "멈춤."이라고 적습니다! 끝?')]
    assert got == ["로그를 읽으세요.", '그다음 "멈춤."이라고 적습니다!', "끝?"]


def test_split_keeps_version_numbers():
    got = [s for s, _ in ko_text.split_sentences("v2.0 버전을 설치하세요. 다음은 1.5초입니다.")]
    assert got == ["v2.0 버전을 설치하세요.", "다음은 1.5초입니다."]


def test_units_split_list_table_and_prose():
    text = ("# 제목은 세지 않습니다\n\n"
            "첫 문장입니다. 둘째 문장은\n줄을 넘어갑니다.\n\n"
            "- 목록 항목 하나\n- 목록 항목 둘입니다.\n\n"
            "| 칸 하나 | 칸 둘입니다 |\n|---|---|\n| 셋째 칸 | 넷째 칸 |\n\n"
            "```\n코드 블록 안의 문장입니다.\n```\n")
    got = [(u.text, u.line, u.kind) for u in ko_text.units(text)]
    assert got == [
        ("첫 문장입니다.", 3, "prose"),
        ("둘째 문장은 줄을 넘어갑니다.", 3, "prose"),
        ("목록 항목 하나", 6, "list"),
        ("목록 항목 둘입니다.", 7, "list"),
        ("칸 하나", 9, "table"),
        ("칸 둘입니다", 9, "table"),
        ("셋째 칸", 11, "table"),
        ("넷째 칸", 11, "table"),
    ], got


def test_units_count_code_url_quote_as_one_token():
    got = ko_text.units("`sqlpipe run`을 https://x.dev 에서 \"빠르게\" 실행하세요.")
    assert got[0].text == "CODE을 URL 에서 QUOTE 실행하세요.", got


def test_units_skip_blockquote_marker_and_headings_inside():
    got = [(u.text, u.kind) for u in ko_text.units("> ## 예시\n>\n> 인용 안의 문장입니다.\n")]
    assert got == [("인용 안의 문장입니다.", "prose")], got


def test_eojeol_count_merges_parentheses_and_units():
    assert ko_text.eojeol_count("Postgres 포트(기본값 5432)에 연결하지 못하면 멈춥니다.") == 5
    assert ko_text.eojeol_count("디스크를 5 GB 비우고 10 분 기다리세요.") == 5


def test_sentence_kind_by_ending():
    assert ko_text.sentence_kind("로그를 읽으세요.") == "procedural"
    assert ko_text.sentence_kind("전원을 끄십시오.") == "procedural"
    assert ko_text.sentence_kind("실행하자.") == "procedural"
    assert ko_text.sentence_kind("서버가 응답합니다.") == "descriptive"
    assert ko_text.sentence_kind("설정 변경 필요.") is None
    assert ko_text.sentence_kind("결과 목록") is None


def test_register_classes():
    assert ko_text.register("서버가 응답합니다.") == "hapsyo"
    assert ko_text.register("서버가 응답합니까?") == "hapsyo"
    assert ko_text.register("전원을 끄십시오.") == "hapsyo_imp"
    assert ko_text.register("로그를 읽으세요.") == "haeyo_imp"
    assert ko_text.register("서버가 응답해요.") == "haeyo"
    assert ko_text.register("서버가 응답한다.") == "haera"
    assert ko_text.register("설정 변경 필요.") is None
    assert ko_text.register("대상: 사용자.") is None
```

- [ ] **Step 2: 테스트를 돌려 실패를 확인한다**

Run: `python3 evals/tests/run.py evals/tests/test_ko_text.py`
Expected: 새 테스트 8개가 `AttributeError: module 'ko_text' has no attribute 'split_sentences'` 같은 오류로 FAIL.

- [ ] **Step 3: 구현을 쓴다**

`evals/ko_text.py`의 import 블록(`import re`, `import unicodedata`)을 다음으로 바꾼다:

```python
import re
import unicodedata
from bisect import bisect_right
from collections import namedtuple
```

파일 끝에 덧붙인다:

```python
Unit = namedtuple("Unit", "text line kind")  # kind: prose, list, table

HEADING = re.compile(r"^\s{0,3}#{1,6}\s")
LIST_ITEM = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+(.*)$")
TABLE_ROW = re.compile(r"^\s*\|(.*)\|\s*$")
TABLE_SEP = re.compile(r"^\s*\|[\s:|-]+\|\s*$")
BLOCKQUOTE = re.compile(r"^\s*(?:>\s?)+")
SPLIT = re.compile(r"(?<=[.!?])([\"'”’)\]]*)\s+")
PAREN = re.compile(r"\([^()\n]*\)")
NUM_UNIT = re.compile(
    r"(\d[\d,.]*)\s+(%|[A-Za-z]{1,5}|초|분|시간|일|주|개월|년|개|건|회|번|명|배|원|자|줄|행|쪽|장|단계)"
    r"(?=[\s.,!?)]|$|[가-힣])")
PROC_ENDINGS = ("세요", "십시오", "시오", "하라", "하자")
NOUN_YO = ("필요", "중요", "주요", "개요")


def tail(sentence):
    """문장 끝의 부호와 닫는 따옴표를 뗀 문자열."""
    return sentence.rstrip(" \t.!?:;\"'”’)]")


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
    base = COMMENT.sub(_blank, FENCE.sub(_blank, OFF_REGION.sub(_blank, nfc(text))))
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
    s = NUM_UNIT.sub(r"\1\2", s)
    return len(s.split())


def sentence_kind(sentence):
    """명령형 어미로 끝나면 procedural, 평서·의문 어미로 끝나면 descriptive, 나머지는 None."""
    t = tail(sentence)
    if t.endswith(PROC_ENDINGS):
        return "procedural"
    if t.endswith(NOUN_YO):
        return None
    if t.endswith(("니다", "니까", "다", "요", "죠")):
        return "descriptive"
    return None


def register(sentence):
    """문장 끝 어미로 문체를 가린다. 가릴 수 없으면 None."""
    t = tail(sentence)
    if t.endswith(("십시오", "시오")):
        return "hapsyo_imp"
    if t.endswith(("니다", "니까")):
        return "hapsyo"
    if t.endswith("세요"):
        return "haeyo_imp"
    if t.endswith(NOUN_YO):
        return None
    if t.endswith(("요", "죠")):
        return "haeyo"
    if t.endswith(("다", "라", "하자", "까", "냐")):
        return "haera"
    return None
```

- [ ] **Step 4: 테스트를 돌려 통과를 확인한다**

Run: `python3 evals/tests/run.py evals/tests/test_ko_text.py && /usr/bin/python3 evals/tests/run.py evals/tests/test_ko_text.py`
Expected: 두 번 모두 `ok` 18줄, 종료 코드 0.

- [ ] **Step 5: 커밋한다**

```bash
git add evals/ko_text.py evals/tests/test_ko_text.py
git commit -m "feat: split Korean text into sentence units and count eojeol" -m $'Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01SanRSLxxVtkLMJh1wLGeGZ'
```

### Task 3: 어휘 규칙

**Files:**
- Create: `evals/ko_rules.py`
- Test: `evals/tests/test_ko_rules.py`

**Interfaces:**
- Consumes: Task 1~2의 `ko_text.JONG_RIEUL`, `eojeol_count`, `jongseong`, `line_of`, `nfc`, `register`, `sentence_kind`, `tail`, `mask`, `units`
- Produces: `ERROR = "error"`, `WARNING = "warning"`, `Hit = namedtuple("Hit", "category severity line text")`, `DASH`(원본과 같은 대시 정규식), `SLOP_CORE`, `load_slop_terms(path=SLOP_TSV) -> list[str]`, `slop_pattern(terms) -> re.Pattern`, `SLOP_RX`, `lexical_hits(masked, strict=False, slop_rx=None) -> list[Hit]`, `will_calque_hits(masked)`, `rotation_hits(masked)`, `condition_hits(masked)`, `connective_hits(masked)`. 범주 이름: `hedge`, `double_passive`, `translationese`, `light_verb`, `colloquial`, `latin_abbrev`, `em_dash`, `semicolon`, `slop_word`, `will_calque`, `synonym_rotation`, `strict_ending`, `strict_condition`, `strict_connective`.

- [ ] **Step 1: 실패하는 테스트를 쓴다**

`evals/tests/test_ko_rules.py`:

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import ko_rules  # noqa: E402
from ko_text import mask, units  # noqa: E402

CORE = ko_rules.slop_pattern(ko_rules.SLOP_CORE)


def cats(text, strict=False):
    return sorted(h.category for h in ko_rules.lexical_hits(mask(text), strict=strict, slop_rx=CORE))


def test_hedge_patterns():
    for s in ("실패할 수도 있습니다.", "원인인 것 같습니다.", "재시작하는 것이 좋습니다.",
              "확인하시기 바랍니다.", "원인인 것으로 보입니다.", "아마 캐시 문제입니다."):
        assert cats(s) == ["hedge"], (s, cats(s))
    assert cats("아마존 S3에 올립니다.") == []
    assert cats("수도 서울에 있습니다.") == []


def test_will_calque_needs_rieul_batchim():
    assert cats("다음 버전에서 제거될 것입니다.") == ["will_calque"]
    assert cats("값이 남아 있을 것이다.") == ["will_calque"]
    assert cats("중요한 것은 순서입니다.") == []
    assert cats("이것은 캐시를 지우는 것입니다.") == []


def test_double_passive():
    assert cats("값이 변경되어졌습니다.") == ["double_passive"]
    assert cats("화면에 보여집니다.") == ["double_passive"]
    assert cats("돼지 저금통입니다.") == []
    assert cats("파일이 만들어집니다.") == []


def test_translationese_patterns():
    for s in ("설정에 대해 설명합니다.", "API를 통해 요청합니다.", "스케줄러에 의해 실행됩니다.",
              "배포에 있어서 중요합니다.", "필드를 가지고 있습니다.", "타임아웃으로 인해 실패했습니다.",
              "만약 실패하면 멈춥니다.", "세 형식을 지원하고 있습니다.", "서버로부터 응답을 받습니다."):
        assert "translationese" in cats(s), (s, cats(s))
    assert cats("서버에 있어요.") == []
    assert cats("두 서비스를 통합합니다.") == []


def test_light_verb_colloquial_latin():
    assert cats("배포를 진행합니다.") == ["light_verb"]
    assert cats("진행 상황을 봅니다.") == []
    assert cats("근데 이건 바뀔 겁니다.") == ["colloquial", "colloquial"]
    assert cats("로그, 지표 등등을 봅니다.") == ["latin_abbrev"]
    assert cats("e.g. 로그를 봅니다.") == ["latin_abbrev"]


def test_dashes_and_semicolons():
    assert cats("배포가 실패했습니다 — 디스크가 찼습니다.") == ["em_dash"]
    assert cats("범위는 5–10분입니다.") == []
    assert cats("`--force`를 쓰지 마세요.") == []
    assert cats("첫째; 둘째") == ["semicolon"]
    assert cats("코드 `a; b`는 그대로입니다.") == []


def test_slop_core_and_negative_parallel():
    assert cats("강력한 도구로 원활하게 처리합니다.") == ["slop_word", "slop_word"]
    assert cats("이것은 단순히 캐시가 아니라 저장소입니다.") == ["slop_word"]
    assert cats('"강력한"이라는 말을 지우세요.') == []


def test_slop_terms_file_with_comments_and_spaces():
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        p = Path(d, "slop.tsv")
        p.write_text("# 주석\n중요한 역할\t3\t(지우세요)\n다양한\t4\t여러\n", encoding="utf-8")
        terms = ko_rules.load_slop_terms(p)
        assert "중요한 역할" in terms and "다양한" in terms and "# 주석" not in terms
        rx = ko_rules.slop_pattern(terms)
        assert rx.search("핵심이 중요한  역할을 합니다") and not rx.search("불중요한 역할")


def test_rotation_prefers_designated_word():
    hits = ko_rules.rotation_hits(mask("키를 검증하세요. 값을 확인하세요. 다시 확인합니다."))
    assert [h.text for h in hits] == ["검증 (확인)"]
    hits = ko_rules.rotation_hits(mask("구성 파일을 엽니다. 설정 파일을 저장합니다."))
    assert [h.text for h in hits] == ["구성 파일 (설정)"]
    assert ko_rules.rotation_hits(mask("키를 검증하고 값을 점검합니다.")) and True


def test_strict_only_patterns():
    text = "백업을 반드시 확인해야 합니다. 서버나 클라이언트를 다시 시작하세요. 실패할 경우 로그를 보세요."
    assert cats(text) == []
    assert cats(text, strict=True) == ["strict_condition", "strict_connective", "strict_ending"]
    assert cats("하나 이상을 고르세요. 실행하거나 멈추세요. 그러나 끝납니다.", strict=True) == []
```

- [ ] **Step 2: 테스트를 돌려 실패를 확인한다**

Run: `python3 evals/tests/run.py evals/tests/test_ko_rules.py`
Expected: `ModuleNotFoundError: No module named 'ko_rules'`로 실패한다.

- [ ] **Step 3: 구현을 쓴다**

`evals/ko_rules.py`:

```python
"""SimpleKorean 린터의 규칙. 함수마다 Hit 목록을 돌려준다.

어휘 규칙은 ko_text.mask()로 지운 보기를 받고, 문장 규칙은 ko_text.units()의 결과를 받는다.
"""
import re
from collections import Counter, namedtuple
from pathlib import Path

from ko_text import JONG_RIEUL, eojeol_count, jongseong, line_of, nfc, register, sentence_kind, tail

ERROR, WARNING = "error", "warning"
Hit = namedtuple("Hit", "category severity line text")

DASH = re.compile(r"—|(?<!\d)–(?!\d)|(?<= )--(?= )|(?<=[^\s\d]{2}) - (?=[^\s\d]{2})")

LEXICAL = (
    ("hedge", ERROR, re.compile(
        r"\s수도\s?있|것\s?같(?:습니다|다|아요|은데|아서)|[는은]\s?것이\s?좋|기(?:를)?\s?바랍니다"
        r"|것으로\s?(?:보입니다|보인다|판단됩니다|판단된다|예상됩니다|추정됩니다)"
        r"|(?<![가-힣])아마(?:도)?(?![가-힣])")),
    ("double_passive", ERROR, re.compile(
        r"(?:되어|보여|쓰여|읽혀|잊혀|불려|닫혀|열려|나뉘어|놓여|짜여|믿겨|갇혀|담겨|쌓여|찢겨)"
        r"(?:지|진|질|집|졌|져)")),
    ("translationese", WARNING, re.compile("|".join((
        r"에\s?대(?:해|한|하여|해서)",
        r"[을를]\s?통(?:해|한|하여|해서)",
        r"에\s?의(?:해|한|하여|해서)",
        r"에\s?있어(?:서)?(?![가-힣])",
        r"[을를]\s?가지고\s?있",
        r"(?:으로|로)\s?인(?:해|한|하여|해서)",
        r"하는\s?것이\s?가능|것이\s?가능합니다",
        r"[이가]\s?요구(?:됩|된|되)",
        r"할\s?필요가\s?있",
        r"에\s?위치(?:한|해|하)",
        r"(?<![가-힣])만(?:약|일)(?![가-힣])",
        r"고\s?있(?:습니다|다)(?![가-힣])",
        r"(?:으로|로)부터",
    )))),
    ("light_verb", WARNING, re.compile(r"(?:진행|수행|실시)(?:하|합|했|해|한|할|함|됩|된|되|될|됨)")),
    ("colloquial", WARNING, re.compile(
        r"(?<![가-힣])(?:근데|그치만|걍|겁니다|거예요|거에요|건데|거죠)(?![가-힣])")),
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
CHECK_VERB = re.compile(r"(?<![가-힣])(확인|검증|점검|체크|검사)(?=하|합|했|해|한|할|됩|된|되|될)")
CONFIG_NOUN = re.compile(r"(?<![가-힣])(설정\s?파일|구성\s?파일|컨피그(?:\s?파일)?|컨피규레이션)")
SLOP_CORE = ("원활", "효율적", "강력한", "혁신적", "획기적", "손쉽게", "간편하게", "매끄럽게", "포괄적",
             "견고한", "극대화", "시너지", "패러다임", "결론적으로", "요약하자면", "정리하자면",
             "살펴보겠습니다", "알아보겠습니다")
SLOP_TSV = Path(__file__).resolve().parent / "slop.tsv"


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
        if word in NA_STOP or word.endswith("거나"):
            continue
        hits.append(Hit("strict_connective", WARNING, line_of(masked, m.start()), word))
    return hits


def lexical_hits(masked, strict=False, slop_rx=None):
    """어휘 규칙을 모두 돌린다. masked는 ko_text.mask()의 결과다."""
    hits = []
    for category, severity, rx in LEXICAL:
        hits += _hits_from(rx, masked, category, severity)
    hits += will_calque_hits(masked)
    hits += _hits_from(slop_rx or SLOP_RX, masked, "slop_word", WARNING)
    hits += rotation_hits(masked)
    if strict:
        for category, severity, rx in STRICT_LEXICAL:
            hits += _hits_from(rx, masked, category, severity)
        hits += condition_hits(masked) + connective_hits(masked)
    return hits
```

- [ ] **Step 4: 테스트를 돌려 통과를 확인한다**

Run: `python3 evals/tests/run.py evals/tests/test_ko_rules.py && /usr/bin/python3 evals/tests/run.py evals/tests/test_ko_rules.py`
Expected: 두 번 모두 `ok` 10줄, 종료 코드 0.

- [ ] **Step 5: 커밋한다**

```bash
git add evals/ko_rules.py evals/tests/test_ko_rules.py
git commit -m "feat: add lexical rules for hedges, translationese, slop, and dashes" -m $'Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01SanRSLxxVtkLMJh1wLGeGZ'
```

### Task 4: 문장 규칙과 문체 혼용

**Files:**
- Modify: `evals/ko_rules.py` (파일 끝에 추가)
- Test: `evals/tests/test_ko_rules.py` (파일 끝에 추가)

**Interfaces:**
- Consumes: Task 2의 `Unit`, `units`, `eojeol_count`, `sentence_kind`, `register`, `tail`, Task 3의 `Hit`, `WARNING`
- Produces: `LIMITS = {"procedural": 15, "descriptive": 20}`, `sentence_hits(units, text_type="descriptive", limits=None) -> list[Hit]`(범주 `sentence_over_limit`, `trailing_condition`, `noun_ending`), `register_hits(units) -> list[Hit]`(범주 `register_mix`), `STYLES`(허용 문체 조합 넷)

- [ ] **Step 1: 실패하는 테스트를 덧붙인다**

`evals/tests/test_ko_rules.py` 끝에 덧붙인다:

```python
def scats(text, text_type="descriptive"):
    us = units(text)
    return sorted(h.category for h in ko_rules.sentence_hits(us, text_type) + ko_rules.register_hits(us))


def test_length_limits_follow_sentence_kind():
    assert scats("가 " * 15 + "하세요.") == ["sentence_over_limit"]
    assert scats("가 " * 19 + "합니다.") == []
    assert scats("가 " * 20 + "합니다.") == ["sentence_over_limit"]


def test_untyped_sentence_uses_text_type():
    fragment = "가 " * 17 + "끝"
    assert scats(fragment, "procedural") == ["sentence_over_limit"]
    assert scats(fragment, "descriptive") == []


def test_trailing_condition():
    assert "trailing_condition" in scats("로그를 확인하세요. 단, 빌드가 실패한 경우에만 확인합니다.")
    assert "trailing_condition" in scats("로그를 확인하세요(빌드가 실패한 경우).")
    assert scats("빌드가 실패하면 로그를 확인하세요.") == []


def test_noun_ending_only_in_prose():
    assert scats("설정 변경 필요.") == ["noun_ending"]
    assert scats("- 설정 변경 필요\n- 로그 확인 완료\n") == []
    assert scats("백업이 있음.") == ["noun_ending"]


def test_register_mix_flags_minority():
    hits = ko_rules.register_hits(units("서버가 응답합니다. 로그를 읽으세요. 이 값은 기본값이다. 캐시를 지웁니다."))
    assert [h.text for h in hits] == ["이 값은 기본값이다."]


def test_register_accepts_single_styles():
    assert ko_rules.register_hits(units("값이 바뀐다. 로그를 본다. 다시 시작하라.")) == []
    assert ko_rules.register_hits(units("값이 바뀌어요. 로그를 보세요.")) == []
    assert ko_rules.register_hits(units("전원을 끕니다. 커버를 여십시오.")) == []
    assert len(ko_rules.register_hits(units("로그를 보세요. 커버를 여십시오. 값을 봅니다. 값을 엽니다."))) == 1
```

- [ ] **Step 2: 테스트를 돌려 실패를 확인한다**

Run: `python3 evals/tests/run.py evals/tests/test_ko_rules.py`
Expected: 새 테스트 6개가 `AttributeError: module 'ko_rules' has no attribute 'sentence_hits'`로 FAIL.

- [ ] **Step 3: 구현을 덧붙인다**

`evals/ko_rules.py` 끝에 덧붙인다:

```python
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
```

- [ ] **Step 4: 테스트를 돌려 통과를 확인한다**

Run: `python3 evals/tests/run.py evals/tests/test_ko_rules.py && /usr/bin/python3 evals/tests/run.py evals/tests/test_ko_rules.py`
Expected: 두 번 모두 `ok` 16줄, 종료 코드 0.

- [ ] **Step 5: 커밋한다**

```bash
git add evals/ko_rules.py evals/tests/test_ko_rules.py
git commit -m "feat: add sentence length, noun-ending, and register-mix rules" -m $'Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01SanRSLxxVtkLMJh1wLGeGZ'
```

### Task 5: 표기 단어 목록과 프로젝트 설정

**Files:**
- Create: `data/terms.json`, `evals/ko_terms.py`
- Test: `evals/tests/test_ko_terms.py`

**Interfaces:**
- Consumes: Task 1의 `ko_text.line_of`, `nfc`, `mask`, Task 3의 `ko_rules.ERROR`, `WARNING`, `Hit`
- Produces: `data/terms.json`(개념 42개. 키: `id`, `group`, `write`, 선택 `alias`, `flag{forms, default, strict}`, 선택 `accept`, 선택 `skip`, 선택 `mix`, `basis{kind, url}`, `practice`, 선택 `decision`), `ko_terms.load_terms(path=TERMS_JSON) -> list[dict]`, `find_config(start) -> Path | None`, `load_config(path) -> dict`(틀리면 경로를 담은 `ValueError`), `apply_config(concepts, config) -> (list[dict], list[str])`(입력을 바꾸지 않음), `scan(masked, concepts, extra_skip=()) -> list[Occurrence]`, `Occurrence = namedtuple("Occurrence", "concept form role start")`(role은 `write`, `alias`, `flag`, `accept`), `term_hits(masked, concepts, strict=False, extra_skip=()) -> list[Hit]`(범주 `spelling`, `term_choice`, `term_mix`)

- [ ] **Step 1: 단어 목록을 만든다**

아래 명령은 `data/terms.json`을 만든다. 실사용 수치는 `docs/research/loanword-spelling-usage.md`의 표에서, 근거 URL은 `docs/research/data/loanword-usage/norms.csv`에서 옮겼다. 이 생성 코드는 레포에 넣지 않는다. 만든 뒤에는 `data/terms.json`이 원본이고, 바꿀 때는 이 파일을 직접 고친다.

```bash
mkdir -p data && python3 - data/terms.json <<'TERMS_EOF'
import json, sys
Y = "https://korean.go.kr/kornorms/example/exampleList.do?regltn_code=0003&pageUnit=100&pageIndex=1&example_search_list%5B0%5D.searchCondition=srclang_mark&example_search_list%5B0%5D.searchEquals=equal&example_search_list%5B0%5D.searchKeyword="
STD = "https://stdict.korean.go.kr/search/searchResult.do?pageSize=10&searchKeyword="
G1 = "현지화 97.4~100%, 벤더 문서 100%, 블로그 96.7~100%, README 89~100%, velog 91~100% (11개 단어 묶음의 범위)"
E, W, M = "error", "warning", "mix"
concepts = []


def yb(word):
    return {"kind": "외래어 표기 용례", "url": Y + word}


def sb(query, kind="표준국어대사전 표제어"):
    return {"kind": kind, "url": STD + query}


def add(id_, group, write, forms, default, strict, basis, practice, alias=None, accept=None, mix=True, decision=None):
    d = {"id": id_, "group": group, "write": write}
    if alias:
        d["alias"] = alias
    d["flag"] = {"forms": forms, "default": default, "strict": strict}
    if accept:
        d["accept"] = accept
    if not mix:
        d["mix"] = False
    d["basis"] = basis
    d["practice"] = practice
    if decision:
        d["decision"] = decision
    concepts.append(d)


add("message", 1, "메시지", ["메세지"], E, E, yb("message"), "현지화 95.6%(14:0), 벤더 문서 99.9%(12:0), 블로그 97.4%(21:0), README 70%, velog(2019–22) 65%")
add("application", 1, "애플리케이션", ["어플리케이션"], E, E, yb("application"), "현지화 90.4%(14:0), 벤더 문서 100%(9:0), 블로그 85.9%(19:2), README 76%, velog(2019–22) 78%")
add("contents", 1, "콘텐츠", ["컨텐츠", "콘텐트", "컨텐트"], E, E, yb("contents"), "현지화 89.2%(11:1), 벤더 문서 99.6%(10:0), 블로그 89.8%(17:1), README 75%, velog(2019–22) 80%")
add("architecture", 1, "아키텍처", ["아키텍쳐"], E, E, yb("architecture"), "현지화 96.9%(7:0), 벤더 문서 100%(5:0), 블로그 95.0%(19:0), README 82%, velog(2019–22) 74%")
add("thread", 1, "스레드", ["쓰레드"], E, E, yb("thread"), "현지화 98.0%(9:0), 벤더 문서 100%(3:0), 블로그 77.7%(18:1), README 80%, velog(2019–22) 70%")
add("method", 1, "메서드", ["메소드"], E, E, sb("%EB%A9%94%EC%84%9C%EB%93%9C", "표준국어대사전 표제어(온라인가나다 2025-02-04는 관행을 따르라고 답함)"), "현지화 92.2%(10:2), 벤더 문서 99.4%(7:0), 블로그 78.4%(11:3), README 71%, velog(2019–22) 46%")
add("license", 1, "라이선스", ["라이센스"], E, E, yb("license"), "현지화 86.4%(8:1), 벤더 문서 100%(3:0), 블로그 69.6%(3:1), README 68%, velog(2019–22) 70%")
add("access", 1, "액세스", ["엑세스", "억세스"], E, E, yb("access"), "현지화 98.9%(10:0), 벤더 문서 100%(8:0), 블로그 94.7%(2:0), README 72%, velog(2019–22) 75%")
add("schedule", 1, "스케줄", ["스케쥴"], E, E, yb("schedule"), "현지화 97.5%(5:1), 벤더 문서 90.5%(3:0), 블로그 96.2%(16:0), README 84%, velog(2019–22) 50%")
add("business", 1, "비즈니스", ["비지니스"], E, E, yb("business"), "현지화 92.5%(3:0), 벤더 문서 100%(7:0), 블로그 99.0%(21:0), README 86%, velog(2019–22) 91%")
add("setting", 1, "세팅", ["셋팅"], E, E, yb("setting"), "현지화 96.6%(3:0), 벤더 문서 100%(4회), 블로그 97.8%(11:0), README 84%, velog(2019–22) 76%")
add("manual", 1, "매뉴얼", ["메뉴얼"], E, E, yb("manual"), "현지화 94.3%(3:0), 벤더 문서 0회, 블로그 90.9%(33회), README 47%, velog(2019–22) 95%")
add("cache", 1, "캐시", ["캐쉬"], E, E, sb("%EC%BA%90%EC%8B%9C"), G1)
add("dashboard", 1, "대시보드", ["대쉬보드"], E, E, sb("%EB%8C%80%EC%8B%9C%EB%B3%B4%EB%93%9C"), G1)
add("hash", 1, "해시", ["해쉬"], E, E, yb("hash"), G1)
add("format", 1, "포맷", ["포멧"], E, E, yb("format"), G1)
add("rendering", 1, "렌더링", ["랜더링"], E, E, yb("rendering"), G1)
add("transaction", 1, "트랜잭션", ["트랜젝션"], E, E, yb("transaction"), G1)
add("version", 1, "버전", ["버젼"], E, E, yb("version"), G1)
add("header", 1, "헤더", ["해더"], E, E, yb("header"), G1)
add("data", 1, "데이터", ["데이타"], E, E, yb("data"), G1)
add("component", 1, "컴포넌트", ["컴퍼넌트"], E, E, yb("component"), G1)
add("framework", 1, "프레임워크", ["프레임웍"], E, E, sb("%ED%94%84%EB%A0%88%EC%9E%84%EC%9B%8C%ED%81%AC"), G1)
add("directory", 2, "디렉터리", ["디렉토리"], W, E, yb("directory"), "현지화 70.5%(9:4), 벤더 문서 96.6%(6:0), JetBrains 1,647:38, 블로그 49.3%(7:3), README 14%, velog 2019–22 36%, velog 2026 57%")
add("release", 2, "릴리스", ["릴리즈"], W, E, yb("release"), "현지화 71.1%(6:4), 벤더 문서 89.6%(6:1), 토스페이먼츠 0:20, 블로그 44.3%(6:10), README 32%, velog 2019–22 10%, velog 2026 76%")
add("shell", 2, "셸", ["쉘"], W, E, yb("shell"), "현지화 91.6%(4:3), 벤더 문서 96.4%(2:0), UI 문자열 3종 100%, 블로그 22.6%(2:3), README 28%, velog 2019–22 0%, velog 2026 83%")
add("redirection", 2, "리디렉션", ["리다이렉션"], W, E, sb("%EB%A6%AC%EB%94%94%EB%A0%89%EC%85%98"), "현지화 72.5%(5:1), 벤더 문서 96.6%(3:0), 블로그 1:2회, README 5:3회, velog 0:4회(2019–22), 0:7회(2026)")
add("repository", 3, "레포지토리", ["리포지토리", "레포지터리", "레포"], W, E,
    {"kind": "우리말샘 규범 표기 지시(리포지토리 ⇒ 리포지터리). 외래어 표기 용례와 표준국어대사전에는 없음",
     "url": "https://opendict.korean.go.kr/dictionary/view?sense_no=724814&viewType=confirm"},
    "규범형 리포지터리: 현지화 24.2%(1:3), 벤더 문서 0/1,104, 블로그 38.3%(2:3), README 0.4%. 블로그의 코드 저장소 뜻: 저장소 41%, 레포 37%, 리포지터리류 22%",
    accept=["리포지터리"], decision="2026-10-08 사용자 결정: 규범형 리포지터리는 실사용이 거의 없어 관용형 레포지토리를 지정")
add("body", 3, "바디", [], W, E, yb("body"),
    "규범형 보디: 현지화 0%(0:2), 벤더 문서 0%(0:2), 블로그 0:5회, README 0:2회, velog 0:7회",
    accept=["보디"], decision="2026-10-08 사용자 결정: 규범형 보디는 실사용이 없어 관용형 바디를 지정")
add("column", 3, "칼럼", ["컬럼"], W, E, yb("column"),
    "규범형 칼럼: 현지화 43.2%(1:1), 블로그 9.0%(2:16), README 22%, velog 2019–22 10%, velog 2026 6%. 토스페이먼츠 10:1, Microsoft 용어집은 '열'",
    decision="2026-10-08 사용자 결정: 규범형 칼럼을 지정")
add("target", 3, "대상", ["타겟"], W, E, yb("target"),
    "규범형 타깃: 현지화 37.0%(2:4), 벤더 문서 4.6%(0:2), JetBrains 822:2, 블로그 22.6%(2:7), README 14%. Microsoft 용어집과 Android는 '대상'",
    accept=["타깃"], mix=False, decision="2026-10-08 사용자 결정: 우리말 대응어 대상을 지정. 대상은 일반어라 일관성 검사에서 뺌")
add("redirect", 4, "리디렉션", ["리다이렉트", "리디렉트"], M, W,
    {"kind": "공식 표기 없음(온라인가나다 2025-04-16: 따로 규정된 바가 없음)",
     "url": "https://korean.go.kr/front/onlineQna/onlineQnaView.do?mn_id=216&qna_seq=313045&pageIndex=1"},
    "리디렉트: 현지화 7.2%(1:2), 벤더 문서 0%(0:2), 블로그 0:8회, README 0%. Microsoft 용어집의 대응어는 리디렉션")
add("refactoring", 4, "리팩터링", ["리팩토링"], M, W,
    {"kind": "공식 표기 없음(온라인가나다 2026-08-10: 팩터링에 맞춰 리팩터링으로 표기할 수 있음)",
     "url": "https://korean.go.kr/front/onlineQna/onlineQnaView.do?mn_id=216&qna_seq=334621&pageIndex=1"},
    "리팩터링: 현지화 56.5%(3:6), 벤더 문서 100%(2:0), 블로그 21.9%(2:10), README 10%, velog 2026 11%")
add("error", 5, "오류", ["에러"], M, W, yb("error"), "오류: 현지화 50.1%(11:4), UI 문자열 4종 100%, 벤더 문서 49.9%(10:2), 블로그 40.8%(7:14), README 58%")
add("parameter", 5, "매개변수", ["파라미터"], M, W, yb("parameter"), "매개변수: 현지화 87.4%(10:3), 벤더 문서 35.1%(3:6), 블로그 13.8%(2:14), README 43%", alias=["매개 변수"])
add("user", 5, "사용자", ["유저"], M, W,
    {"kind": "표준국어대사전 표제어, 다듬은 말 '유저 → 사용자'(2013 고시)", "url": "https://stdict.korean.go.kr/search/searchView.do?word_no=170113&searchKeywordTo=3"},
    "사용자: 현지화 96.9%(15:0), 벤더 문서 99.9%(12:0), 블로그 72.9%(18:4), README 79%")
add("default", 5, "기본값", ["디폴트"], M, W, yb("default"), "기본값: 현지화 98.5%(15:0), 벤더 문서 99.4%(10:0), 블로그 97.6%(11:0), README 70%", alias=["기본 값"])
add("deploy", 5, "배포", ["디플로이"], M, W,
    {"kind": "표준국어대사전 표제어. 디플로이는 세 자료에 없음", "url": "https://stdict.korean.go.kr/search/searchView.do?word_no=431960&searchKeywordTo=3"},
    "배포: 현지화 99% 이상(디플로이먼트 제외), 벤더 문서 100%(9:0), 블로그 99.9%(22:0), README 100%")
add("default_value_spacing", 6, "기본값", ["기본 값"], W, E, sb("%EA%B8%B0%EB%B3%B8%EA%B0%92", "우리말샘 '기본-값' 한 단어"),
    "붙여 쓴 비율: 현지화 89.5%, 벤더 문서 91.9%, 블로그 85.1%, README 100%, GitHub 코드 검색 96%")
add("parameter_spacing", 6, "매개변수", ["매개 변수"], M, W,
    {"kind": "표준국어대사전 '매개^변수'(띄어 씀이 원칙, 붙여 씀 허용)", "url": "https://stdict.korean.go.kr/search/searchView.do?word_no=111708&searchKeywordTo=3"},
    "붙여 쓴 비율: 현지화 61.9%, 벤더 문서 38.2%, 블로그 97.1%, README 80%, GitHub 코드 검색 92%")
add("return_value_spacing", 6, "반환값", ["반환 값"], M, W, sb("%EB%B0%98%ED%99%98%EA%B0%92", "사전 미등재. '-값' 붙여 쓰기(표준국어대사전 '값'「8」)에 맞춤"),
    "붙여 쓴 비율: 현지화 17.2%, 벤더 문서 0.6%, 블로그 71.0%(31회), README 82%, GitHub 코드 검색 66%")
add("open_source_spacing", 6, "오픈소스", ["오픈 소스"], M, W,
    {"kind": "우리말샘 '오픈^소스'(띄어 씀이 원칙, 붙여 씀 허용)", "url": "https://opendict.korean.go.kr/dictionary/view?sense_no=832806&viewType=confirm"},
    "붙여 쓴 비율: 현지화 47.2%, 벤더 문서 61.0%, 블로그 69.2%, README 89%, GitHub 코드 검색 73%")
data = {
    "version": 1,
    "measured": "2026-10-07~08",
    "source": "docs/research/loanword-spelling-usage.md, docs/research/data/loanword-usage/",
    "severity": "flag.default와 flag.strict: error는 오류, warning은 경고, mix는 문서 안 혼용만 경고",
    "concepts": concepts,
}
with open(sys.argv[1], "w", encoding="utf-8") as f:
    f.write(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
print(len(concepts), "concepts")
TERMS_EOF
```

Expected: `42 concepts` 출력, `data/terms.json` 746줄.

- [ ] **Step 2: 실패하는 테스트를 쓴다**

`evals/tests/test_ko_terms.py`:

```python
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import ko_terms  # noqa: E402
from ko_text import mask, nfc  # noqa: E402


def term_cats(text, strict=False, config=None):
    cfg = config or {}
    concepts, _ = ko_terms.apply_config(ko_terms.load_terms(), cfg)
    hits = ko_terms.term_hits(mask(nfc(text)), concepts, strict=strict, extra_skip=cfg.get("skip", ()))
    return [(h.category, h.severity, h.text) for h in hits]


def test_terms_json_shape():
    concepts = ko_terms.load_terms()
    ids = [c["id"] for c in concepts]
    assert len(ids) == len(set(ids)) == 42
    assert {g: sum(1 for c in concepts if c["group"] == g) for g in range(1, 7)} == {1: 23, 2: 4, 3: 4, 4: 2, 5: 5, 6: 4}
    for c in concepts:
        assert c["basis"]["url"].startswith("https://"), c["id"]
        assert c["flag"]["default"] in ("error", "warning", "mix"), c["id"]
        assert c["flag"]["strict"] in ("error", "warning"), c["id"]
    by = {c["id"]: c for c in concepts}
    assert [by[i]["write"] for i in ("repository", "body", "column", "target")] == ["레포지토리", "바디", "칼럼", "대상"]


def test_group1_variant_is_error_in_both_modes():
    assert term_cats("메세지를 보냅니다.") == [("spelling", "error", "메세지 → 메시지")]
    assert term_cats("메세지를 보냅니다.", strict=True) == [("spelling", "error", "메세지 → 메시지")]


def test_group2_warning_default_error_strict():
    assert term_cats("디렉토리를 만드세요.") == [("spelling", "warning", "디렉토리 → 디렉터리")]
    assert term_cats("디렉토리를 만드세요.", strict=True) == [("spelling", "error", "디렉토리 → 디렉터리")]


def test_group3_designated_forms():
    assert term_cats("레포지토리를 복제하세요. 요청 바디를 보냅니다. 칼럼을 더합니다.") == []
    assert term_cats("리포지토리를 복제하세요.") == [("spelling", "warning", "리포지토리 → 레포지토리")]
    assert term_cats("컬럼을 더합니다.") == [("spelling", "warning", "컬럼 → 칼럼")]
    assert term_cats("리포지터리를 복제하세요.") == []
    assert term_cats("리포지터리를 복제하세요.", strict=True) == [("term_choice", "warning", "리포지터리 → 레포지토리")]
    assert term_cats("타겟을 고르세요.") == [("spelling", "warning", "타겟 → 대상")]


def test_longest_form_wins_and_compounds_skip():
    assert term_cats("레포지토리와 모노레포를 씁니다.") == []
    assert term_cats("레포를 엽니다.") == [("spelling", "warning", "레포 → 레포지토리")]
    assert term_cats("레포트를 씁니다. 캐시백을 받습니다. 하이퍼파라미터를 고칩니다.") == []
    assert term_cats("디플로이먼트를 만듭니다.") == []


def test_groups_4_to_6_mix_only_by_default():
    assert term_cats("에러가 납니다.") == []
    assert term_cats("에러가 납니다.", strict=True) == [("spelling", "warning", "에러 → 오류")]
    assert term_cats("오류가 나면 에러 로그를 보세요.") == [("term_mix", "warning", "에러 → 오류")]
    assert term_cats("오류가 나면 에러 로그를 보세요.", strict=True) == [("spelling", "error", "에러 → 오류")]
    assert term_cats("기본 값을 바꿉니다.") == [("spelling", "warning", "기본 값 → 기본값")]
    assert term_cats("매개 변수를 넘깁니다.") == []
    assert term_cats("매개변수와 매개 변수를 섞습니다.") == [("term_mix", "warning", "매개 변수 → 매개변수")]


def test_designated_form_is_the_mix_base():
    assert term_cats("디렉토리를 만들고 디렉터리로 이동하세요.") == [("spelling", "warning", "디렉토리 → 디렉터리")]


def test_target_is_not_mixed_with_generic_word():
    assert term_cats("적용 대상을 고르고 빌드 타깃을 정합니다.") == []


def test_config_overrides_designated_form():
    cfg = {"terms": {"release": "릴리즈"}}
    assert term_cats("릴리즈 노트를 봅니다.", config=cfg) == []
    assert term_cats("릴리스 노트를 봅니다.", config=cfg, strict=True) == [("term_choice", "warning", "릴리스 → 릴리즈")]


def test_config_group1_override_needs_reason():
    _, warnings = ko_terms.apply_config(ko_terms.load_terms(), {"terms": {"method": "메소드"}})
    assert any("reason" in w for w in warnings)
    _, warnings = ko_terms.apply_config(ko_terms.load_terms(), {"terms": {"method": {"write": "메소드", "reason": "TTA"}}})
    assert warnings == []
    _, warnings = ko_terms.apply_config(ko_terms.load_terms(), {"terms": {"nope": "x"}})
    assert warnings == ["nope: 단어 목록에 없는 개념입니다"]


def test_apply_config_does_not_mutate_input():
    concepts = ko_terms.load_terms()
    before = json.dumps(concepts, ensure_ascii=False, sort_keys=True)
    ko_terms.apply_config(concepts, {"terms": {"release": "릴리즈"}, "spacing": "spaced"})
    assert json.dumps(concepts, ensure_ascii=False, sort_keys=True) == before


def test_config_spacing_spaced():
    cfg = {"spacing": "spaced"}
    assert term_cats("반환 값을 돌려줍니다.", config=cfg, strict=True) == []
    assert term_cats("반환값을 돌려줍니다.", config=cfg, strict=True) == [("term_choice", "warning", "반환값 → 반환 값")]


def test_config_skip_strings():
    assert term_cats("디렉토리 서비스 이름입니다.", config={"skip": ["디렉토리 서비스"]}) == []


def test_find_config_walks_up():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d).resolve()
        (root / ".simple-korean.json").write_text(json.dumps({"terms": {"release": "릴리즈"}}), encoding="utf-8")
        nested = root / "docs" / "guide"
        nested.mkdir(parents=True)
        assert ko_terms.find_config(nested / "a.md") == root / ".simple-korean.json"
        assert ko_terms.find_config(nested) == root / ".simple-korean.json"


def test_load_config_rejects_bad_files():
    with tempfile.TemporaryDirectory() as d:
        bad = Path(d, ".simple-korean.json")
        for content in ("{not json", json.dumps({"spacing": "both"}), json.dumps({"term": {}}), "[]"):
            bad.write_text(content, encoding="utf-8")
            try:
                ko_terms.load_config(bad)
            except ValueError as err:
                assert ".simple-korean.json" in str(err), err
            else:
                raise AssertionError(f"ValueError가 나야 합니다: {content}")
```

- [ ] **Step 3: 테스트를 돌려 실패를 확인한다**

Run: `python3 evals/tests/run.py evals/tests/test_ko_terms.py`
Expected: `ModuleNotFoundError: No module named 'ko_terms'`로 실패한다.

- [ ] **Step 4: 구현을 쓴다**

`evals/ko_terms.py`:

```python
"""표기 단어 목록(data/terms.json)과 프로젝트 설정(.simple-korean.json)을 다룬다."""
import copy
import json
import re
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
        raise ValueError(f"{path}: 알 수 없는 키 {unknown}")
    if data.get("spacing", "attached") not in ("attached", "spaced"):
        raise ValueError(f"{path}: spacing은 attached 또는 spaced여야 합니다")
    return data


def _override(concept, new, reason):
    """지정형을 new로 바꾼 새 개념과 경고 목록을 돌려준다."""
    c = copy.deepcopy(concept)
    warnings = []
    if c["group"] == 1 and not reason:
        warnings.append(f"{c['id']}: ① 무리의 지정형을 바꾸려면 reason을 적어야 합니다")
    c["accept"] = [f for f in c.get("accept", []) if f != new] + [c["write"]]
    c["flag"]["forms"] = [f for f in c["flag"]["forms"] if f != new]
    c["alias"] = [f for f in c.get("alias", []) if f != new]
    c["write"] = new
    return c, warnings


def apply_config(concepts, config):
    """설정을 반영한 새 개념 목록과 설정 경고 목록을 돌려준다. 입력은 바꾸지 않는다."""
    overrides = config.get("terms", {})
    spaced = config.get("spacing") == "spaced"
    known = {c["id"] for c in concepts}
    warnings = [f"{cid}: 단어 목록에 없는 개념입니다" for cid in overrides if cid not in known]
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


def _roles(concept):
    pairs = ([(concept["write"], "write")] + [(f, "alias") for f in concept.get("alias", [])]
             + [(f, "flag") for f in concept["flag"]["forms"]]
             + [(f, "accept") for f in concept.get("accept", [])])
    return sorted(pairs, key=lambda pair: len(pair[0]), reverse=True)


def scan(masked, concepts, extra_skip=()):
    """개념마다 형태가 나온 자리를 찾는다. 긴 형태부터 맞추고, 건너뛸 문자열과 겹치는 자리는 뺀다."""
    shared = _spans((*GLOBAL_SKIP, *extra_skip), masked)
    found = []
    for c in concepts:
        roles = _roles(c)
        role_of = {}
        for form, role in roles:
            role_of.setdefault(" ".join(nfc(form).split()), role)
        rx = re.compile(r"(?<![가-힣])(?:" + "|".join(_form_regex(f) for f, _ in roles) + ")")
        skip = shared + _spans(c.get("skip", []), masked)
        for m in rx.finditer(masked):
            if any(a < m.end() and m.start() < b for a, b in skip):
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
    if occ.role == "accept" and strict:
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
```

- [ ] **Step 5: 테스트를 돌려 통과를 확인한다**

Run: `python3 evals/tests/run.py evals/tests/test_ko_terms.py && /usr/bin/python3 evals/tests/run.py evals/tests/test_ko_terms.py`
Expected: 두 번 모두 `ok` 15줄, 종료 코드 0.

- [ ] **Step 6: 커밋한다**

```bash
git add data/terms.json evals/ko_terms.py evals/tests/test_ko_terms.py
git commit -m "feat: add measured term list and project config for spelling checks" -m $'Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01SanRSLxxVtkLMJh1wLGeGZ'
```

### Task 6: 린터 공개 API, CLI, 자체 시험

**Files:**
- Create: `evals/ko_lint.py`
- Test: `evals/tests/test_ko_lint.py`

**Interfaces:**
- Consumes: Task 1~5의 `ko_text`, `ko_rules`, `ko_terms` 전부
- Produces: `ko_lint.lint(text, text_type="descriptive", strict=False, config=None, path=None) -> dict`(키: `type`, `strict`, `eojeol`, `sentences`, `mean_sentence_eojeol`, `longest_sentence_eojeol`, `violations`, `errors_total`, `warnings_total`, `violations_total`, `violations_per_100_eojeol`, `config_warnings`), `lint_detail(...) -> list[dict]`(키: `category`, `severity`, `line`, `text`), `reader_check(text) -> dict`(키: `type`, `eojeol`, `counts{sentences, em_dash, bold_spans, headers, bullets, opener, closer}`, `visible_total`), `reply_fillers(text) -> (bool, bool)`, `LABELS`, `SEVERITY_LABELS`, 고정 예문 `SLOP_FIXTURE`, `CLEAN_FIXTURE`, `REPLY_FIXTURE`, `self_test()`, `main(argv=None) -> int`. `config`가 dict이면 그대로 쓰고, 문자열이면 그 파일을 읽고, None이면 `path`에서 위로 찾는다.

- [ ] **Step 1: 실패하는 테스트를 쓴다**

`evals/tests/test_ko_lint.py`:

```python
import subprocess
import sys
import tempfile
import time
import unicodedata
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import ko_lint  # noqa: E402

LINT = HERE.parent / "ko_lint.py"


def run_cli(*args, cwd=None):
    return subprocess.run([sys.executable, str(LINT), *args], capture_output=True, text=True, cwd=cwd)


def test_self_test_passes():
    ko_lint.self_test()


def test_detail_matches_counts():
    report = ko_lint.lint(ko_lint.SLOP_FIXTURE, "procedural", config={})
    detail = ko_lint.lint_detail(ko_lint.SLOP_FIXTURE, "procedural", config={})
    assert len(detail) == report["violations_total"]
    assert Counter(h["category"] for h in detail) == Counter(report["violations"])


def test_nfd_input_matches_nfc():
    nfd = unicodedata.normalize("NFD", ko_lint.SLOP_FIXTURE)
    assert ko_lint.lint_detail(nfd, config={}) == ko_lint.lint_detail(ko_lint.SLOP_FIXTURE, config={})


def test_crlf_matches_lf():
    crlf = ko_lint.SLOP_FIXTURE.replace("\n", "\r\n")
    assert ko_lint.lint_detail(crlf, config={}) == ko_lint.lint_detail(ko_lint.SLOP_FIXTURE, config={})


def test_large_document_is_fast():
    big = (ko_lint.SLOP_FIXTURE + "\n" + ko_lint.CLEAN_FIXTURE + "\n") * 400
    start = time.time()
    ko_lint.lint(big, config={})
    assert time.time() - start < 5.0, time.time() - start


def test_frontmatter_is_not_linted():
    text = "---\nname: x\ndescription: 강력한 도구 — 정말\n---\n로그를 읽으세요.\n"
    assert ko_lint.lint(text, config={})["violations_total"] == 0


def test_bad_text_type_fails_fast():
    try:
        ko_lint.lint("본문입니다.", "reply")
    except ValueError as err:
        assert "text_type" in str(err)
    else:
        raise AssertionError("ValueError가 나야 합니다")


def test_cli_gate_fails_on_errors_only():
    with tempfile.TemporaryDirectory() as d:
        warn = Path(d, "warn.md")
        warn.write_text("서버에 대해 설명합니다.\n", encoding="utf-8")
        err = Path(d, "err.md")
        err.write_text("메세지를 보냅니다.\n", encoding="utf-8")
        assert run_cli("--gate", str(warn)).returncode == 0
        assert run_cli("--gate=warning", str(warn)).returncode == 1
        r = run_cli("--gate", str(warn), str(err))
        assert r.returncode == 1 and "메세지" in r.stdout, r.stdout


def test_cli_uses_project_config():
    with tempfile.TemporaryDirectory() as d:
        Path(d, ".simple-korean.json").write_text('{"terms": {"release": "릴리즈"}}', encoding="utf-8")
        doc = Path(d, "a.md")
        doc.write_text("릴리즈 노트를 봅니다.\n", encoding="utf-8")
        assert '"violations_total": 0' in run_cli(str(doc)).stdout


def test_cli_rejects_broken_config():
    with tempfile.TemporaryDirectory() as d:
        Path(d, ".simple-korean.json").write_text("{broken", encoding="utf-8")
        doc = Path(d, "a.md")
        doc.write_text("로그를 읽으세요.\n", encoding="utf-8")
        r = run_cli(str(doc))
        assert r.returncode != 0 and ".simple-korean.json" in r.stderr, (r.returncode, r.stderr)


def test_reader_check_reply_counts():
    r = ko_lint.reader_check(ko_lint.REPLY_FIXTURE)["counts"]
    assert (r["sentences"], r["em_dash"], r["bold_spans"], r["headers"], r["bullets"]) == (5, 1, 1, 1, 2)


def test_reply_fillers():
    assert ko_lint.reply_fillers("좋은 질문입니다! 답은 이렇습니다.") == (True, False)
    assert ko_lint.reply_fillers("네, 멱등성에 대해 설명드리겠습니다. 답입니다.") == (True, False)
    assert ko_lint.reply_fillers("답입니다. 도움이 되셨기를 바랍니다.") == (False, True)
    assert ko_lint.reply_fillers("원인은 디스크입니다. 원하시면 스크립트를 고쳐 드리겠습니다.") == (False, True)
    assert ko_lint.reply_fillers("그래프를 알려주시면 원인을 더 좁혀 드리겠습니다.") == (False, True)
    assert ko_lint.reply_fillers("빌드가 실패한 이유는 디스크입니다.") == (False, False)
```

- [ ] **Step 2: 테스트를 돌려 실패를 확인한다**

Run: `python3 evals/tests/run.py evals/tests/test_ko_lint.py`
Expected: `ModuleNotFoundError: No module named 'ko_lint'`로 실패한다.

- [ ] **Step 3: 구현을 쓴다**

`evals/ko_lint.py`:

```python
#!/usr/bin/env python3
"""SimpleKorean 린터. 정규식으로 셀 수 있는 위반을 센다.

알려진 한계: 정규식 검사이고 형태소 분석을 하지 않는다. 거짓 일치와 놓침이 있다. 숫자는 같은
린터 버전끼리 비교하는 값이고 준수 판정이 아니다. 어떤 도구도 규칙 준수를 보장하지 못한다.

사용법:
  python3 evals/ko_lint.py --type procedural 파일.md
  cat 글.md | python3 evals/ko_lint.py -
  python3 evals/ko_lint.py --strict --gate 파일1.md 파일2.md
  python3 evals/ko_lint.py --type reply 답변.txt
  python3 evals/ko_lint.py --self-test
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ko_rules  # noqa: E402
import ko_terms  # noqa: E402
import ko_text  # noqa: E402

TEXT_TYPES = ("procedural", "descriptive")
SEVERITY_LABELS = {"error": "오류", "warning": "경고"}
LABELS = {
    "sentence_over_limit": "문장 길이", "trailing_condition": "뒤에 붙은 조건", "hedge": "짐작·권고",
    "will_calque": "미래형 직역", "double_passive": "이중 피동", "translationese": "번역투",
    "light_verb": "기능동사", "noun_ending": "명사형 종결", "register_mix": "문체 혼용",
    "colloquial": "구어 축약", "em_dash": "em-dash", "semicolon": "세미콜론", "latin_abbrev": "라틴 약어",
    "slop_word": "슬롭 어휘", "synonym_rotation": "한 단어 한 뜻", "spelling": "표기",
    "term_choice": "지정형 아님", "term_mix": "표기 혼용", "strict_ending": "엄격: 문장 끝",
    "strict_condition": "엄격: 조건 표현", "strict_connective": "엄격: 접속어",
}
USAGE = ("사용법: ko_lint.py [--type procedural|descriptive|reply] [--strict] [--config 파일] "
         "[--gate|--gate=warning] (파일... | -) | --self-test")
BOLD = re.compile(r"\*\*[^*\n]+\*\*")
HEADER = re.compile(r"^#{1,6}\s", re.M)
BULLET = re.compile(r"^\s*([-*+]|\d+[.)])\s", re.M)
OPENER = re.compile(
    r"^\s*\W*(?:좋은\s?질문|훌륭한\s?질문|물론(?:입니다|이죠|이에요|요)"
    r"|네[,.!]?\s*(?:알겠습니다|좋습니다|맞습니다)"
    r"|[^.!?\n]{0,40}에\s?대해\s?(?:설명|알아보|살펴보)[^.!?\n]{0,12}겠습니다)")
CLOSER = re.compile(
    r"도움이\s?(?:되셨|되었으면|되길|됐으면|되었기를)"
    r"|궁금한\s?(?:점|사항)이\s?(?:있으시면|있다면|있으면)|언제든(?:지)?\s?(?:물어|말씀|문의|질문)"
    r"|(?:원하시면|필요하시면|알려\s?주시면|말씀해\s?주시면)[^.!?\n]{0,60}(?:드리겠습니다|드릴게요|드릴\s수\s있습니다)")


def _config(config, path):
    """설정 인자를 dict로 바꾼다. dict는 그대로, 경로는 읽고, 없으면 path에서 위로 찾는다."""
    if isinstance(config, dict):
        return config
    if config:
        return ko_terms.load_config(config)
    if path:
        return ko_terms.load_config(ko_terms.find_config(path))
    return {}


def _prepare(text):
    body = ko_text.strip_frontmatter(ko_text.nfc(text))
    return ko_text.mask(body), ko_text.units(body)


def lint_detail(text, text_type="descriptive", strict=False, config=None, path=None):
    """lint()가 세는 위반을 하나씩 돌려준다. 항목: category, severity, line, text."""
    if text_type not in TEXT_TYPES:
        raise ValueError(f"text_type은 {TEXT_TYPES} 가운데 하나여야 합니다: {text_type!r}")
    masked, units = _prepare(text)
    cfg = _config(config, path)
    concepts, _ = ko_terms.apply_config(ko_terms.load_terms(), cfg)
    hits = (ko_rules.lexical_hits(masked, strict=strict)
            + ko_rules.sentence_hits(units, text_type)
            + ko_rules.register_hits(units)
            + ko_terms.term_hits(masked, concepts, strict=strict, extra_skip=cfg.get("skip", ())))
    rows = [{"category": h.category, "severity": h.severity, "line": h.line, "text": h.text} for h in hits]
    return sorted(rows, key=lambda r: (r["line"], r["category"], r["text"]))


def lint(text, text_type="descriptive", strict=False, config=None, path=None):
    """위반 수를 범주별로 센 보고서를 돌려준다."""
    detail = lint_detail(text, text_type, strict, config, path)
    _, units = _prepare(text)
    lengths = [ko_text.eojeol_count(u.text) for u in units]
    eojeol = max(1, sum(lengths))
    errors = sum(1 for h in detail if h["severity"] == "error")
    _, config_warnings = ko_terms.apply_config(ko_terms.load_terms(), _config(config, path))
    return {
        "type": text_type,
        "strict": strict,
        "eojeol": eojeol,
        "sentences": len(units),
        "mean_sentence_eojeol": round(sum(lengths) / max(1, len(lengths)), 1),
        "longest_sentence_eojeol": max(lengths, default=0),
        "violations": dict(Counter(h["category"] for h in detail)),
        "errors_total": errors,
        "warnings_total": len(detail) - errors,
        "violations_total": len(detail),
        "violations_per_100_eojeol": round(100.0 * len(detail) / eojeol, 2),
        "config_warnings": config_warnings,
    }


def reply_fillers(text):
    """답변의 인사말과 맺음말 여부를 (opener, closer)로 돌려준다."""
    t = ko_text.nfc(text)
    return bool(OPENER.search(t)), bool(CLOSER.search(t))


def reader_check(text):
    """채팅 답변에서 독자가 보는 것을 센다.

    sentences는 목록 항목과 표 행도 문장으로 센다. 답변 규칙에는 문장 수 상한이 없으므로
    visible_total에는 넣지 않는다.
    """
    text = ko_text.nfc(text)
    prose = re.sub(r"```.*?```", " ", text, flags=re.S)
    prose = re.sub(r"`[^`\n]+`", "CODE", prose)
    no_md = re.sub(r"^\s*(#{1,6}\s|[-*+]\s|\d+[.)]\s|\|)", "", prose, flags=re.M)
    no_md = re.sub(r"^\s*[\s:|-]+$", "", no_md, flags=re.M)
    sents = [p for p in re.split(r"(?<=[.!?])[\"')\]”’]*\s+|\n+", no_md) if len(p.strip().split()) >= 2]
    opener, closer = reply_fillers(text)
    counts = {
        "sentences": len(sents),
        "em_dash": len(ko_rules.DASH.findall(prose)),
        "bold_spans": len(BOLD.findall(prose)),
        "headers": len(HEADER.findall(prose)),
        "bullets": len(BULLET.findall(prose)),
        "opener": int(opener),
        "closer": int(closer),
    }
    visible = counts["em_dash"] + counts["bold_spans"] + counts["headers"] + counts["bullets"]
    return {"type": "reply", "eojeol": max(1, len(no_md.split())), "counts": counts, "visible_total": visible}


SLOP_FIXTURE = """강력한 재시도 기능을 활용하여 실패한 업로드는 자동으로 다시 시도되어지며 이를 통해 데이터의 무결성이 원활하게 보장되고 있습니다 — 어떤 네트워크 장애가 발생하더라도 시스템이 안정적으로 동작하도록 설계된 이 구조에 대해 자세히 살펴보겠습니다.
자격 증명을 검증하는 것이 좋습니다; 설정을 확인할 수도 있습니다. 예를 들어 타임아웃 컨피그 등등.
배포를 진행합니다. 만약 문제가 계속되면 지원팀에 연락하세요. 이 옵션은 다음 버전에서 제거될 것입니다.
근데 메세지 형식은 바뀔 겁니다.
로그를 확인하세요(빌드가 실패한 경우).
설정 변경 필요.
이 값은 기본값이다.
오류가 나면 에러 로그를 보세요.
"""

CLEAN_FIXTURE = """sqlpipe는 실패한 업로드를 자동으로 다시 시도합니다. 이 과정은 데이터를 그대로 지킵니다.

실패가 계속되면 자격 증명이 맞는지 확인하세요. 문제가 계속되면 지원팀에 연락하세요.
"""

TABLE_FIXTURE = """| 열 A | 열 B | 열 C |
|---|---|---|
| 아주 길고 단어가 많은 첫째 칸 내용입니다 | 둘째 칸도 꽤 깁니다 | 셋째 칸 |
| 이 칸에도 내용이 더 있습니다 | 여기도 마찬가지입니다 | 그리고 여기도 |
"""

LIST_FIXTURE = """다음 항목을 쓸 수 있습니다:

- 끝에 마침표가 없는 첫째 항목
- 끝에 마침표가 없는 둘째 항목
- 끝에 마침표가 없는 셋째 항목

이어지는 본문 문장입니다.
"""

# 앞의 세 줄에 있는 대시만 논리를 잇는 대시다.
DASH_FIXTURE = """배포가 실패했습니다 — 디스크가 가득 찼습니다.
업로드가 실패했습니다 -- 토큰이 만료되었습니다.
재시도가 실패했습니다 - 포트가 닫혀 있었습니다.
운영 환경에서 --force를 쓰지 마세요.
대기 시간은 5 - 10분입니다.
범위는 5–10분이고 2024–2025 시즌에 해당합니다.
칠판에 x - y = z를 쓰세요.
`--config sqlpipe.yaml` 플래그를 쓰세요.
패널을 떼어 내세요:
   -   볼트 네 개를 푸세요.
"""

REPLY_FIXTURE = """**네** — 문제가 있습니다.

## 이유
- 랙이 늘어납니다.
- 사용자가 기다립니다.

지금 확인하세요. 그다음 늘리세요."""

TRICKY_REPLY = ('그가 "지금 멈춰."라고 했습니다. 그다음 (고장 났습니다.) 다 끝났습니다.\n\n'
                "```\n# 헤더 아님\n**굵게 아님**\n- 불릿 아님\n```\n")

EXPECTED_MIN = {
    "sentence_over_limit": 1, "trailing_condition": 1, "hedge": 2, "will_calque": 1,
    "double_passive": 1, "translationese": 4, "light_verb": 1, "noun_ending": 1, "register_mix": 1,
    "colloquial": 2, "em_dash": 1, "semicolon": 1, "latin_abbrev": 1, "slop_word": 3,
    "synonym_rotation": 1, "spelling": 1, "term_mix": 1,
}


def self_test():
    """고정 예문으로 범주마다 한 번 이상 걸리는지, 깨끗한 예문은 0인지 확인한다."""
    slop = lint(SLOP_FIXTURE, "procedural", config={})
    for category, n in EXPECTED_MIN.items():
        assert slop["violations"].get(category, 0) >= n, (category, slop["violations"])
    clean = lint(CLEAN_FIXTURE, "procedural", config={})
    assert clean["violations_total"] == 0, lint_detail(CLEAN_FIXTURE, "procedural", config={})
    assert lint(DASH_FIXTURE, "procedural", config={})["violations"].get("em_dash", 0) == 3
    assert lint(TABLE_FIXTURE, config={})["violations"].get("sentence_over_limit", 0) == 0
    assert lint(LIST_FIXTURE, config={})["violations"].get("sentence_over_limit", 0) == 0
    cell = lint("| 열 | 값 |\n|---|---|\n| 다시 시작할 수도 있습니다 | 괜찮습니다 |\n", config={})["violations"]
    assert cell.get("hedge") == 1 and cell.get("sentence_over_limit", 0) == 0, cell
    off = "<!-- simple-korean: off -->\n강력한 도구를 활용하세요 — 정말로.\n<!-- simple-korean: on -->\n로그를 읽으세요.\n"
    assert lint(off, config={})["violations_total"] == 0
    strict = "백업을 반드시 확인해야 합니다. 서버나 클라이언트를 다시 시작하세요. 실패할 경우 로그를 보세요.\n"
    assert lint(strict, config={})["violations_total"] == 0
    sv = lint(strict, strict=True, config={})["violations"]
    assert (sv.get("strict_ending"), sv.get("strict_connective"), sv.get("strict_condition")) == (1, 1, 1), sv
    r = reader_check(REPLY_FIXTURE)["counts"]
    assert (r["sentences"], r["em_dash"], r["bold_spans"], r["headers"], r["bullets"]) == (5, 1, 1, 1, 2), r
    t = reader_check(TRICKY_REPLY)["counts"]
    assert (t["sentences"], t["headers"], t["bold_spans"], t["bullets"]) == (3, 0, 0, 0), t
    detail = lint_detail(SLOP_FIXTURE, "procedural", config={})
    assert len(detail) == slop["violations_total"]
    assert Counter(h["category"] for h in detail) == Counter(slop["violations"])
    print("self-test OK:", slop["violations_total"], "violations in slop fixture, 0 in clean")


def _pop(args, name, default):
    if name not in args:
        return default
    i = args.index(name)
    if i + 1 >= len(args):
        sys.exit(f"{name} 뒤에 값이 없습니다\n{USAGE}")
    value = args[i + 1]
    del args[i:i + 2]
    return value


def _read(src):
    if src == "-":
        return sys.stdin.read()
    try:
        return Path(src).read_text(encoding="utf-8")
    except OSError as err:
        sys.exit(str(err))


def _check_one(src, text_type, strict, config, gate):
    """파일 하나를 검사해 (보고서, 실패 여부)를 돌려준다."""
    text = _read(src)
    if text_type == "reply":
        report = reader_check(text)
        return {**report, "file": src}, report["visible_total"] > 0
    path = None if src == "-" else src
    report = lint(text, text_type, strict=strict, config=config, path=path)
    failed = report["errors_total"] > 0 or (gate == "warning" and report["warnings_total"] > 0)
    if gate:
        detail = lint_detail(text, text_type, strict=strict, config=config, path=path)
        report = {**report, "hits": [h for h in detail if gate == "warning" or h["severity"] == "error"]}
    return {**report, "file": src}, failed


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    if "--self-test" in args:
        self_test()
        return 0
    gate = "warning" if "--gate=warning" in args else ("error" if "--gate" in args else None)
    args = [a for a in args if a not in ("--gate", "--gate=warning")]
    strict = "--strict" in args
    args = [a for a in args if a != "--strict"]
    text_type = _pop(args, "--type", "descriptive")
    config = _pop(args, "--config", None)
    if text_type not in TEXT_TYPES + ("reply",):
        sys.exit(f"알 수 없는 --type {text_type!r}\n{USAGE}")
    if not args:
        sys.exit(USAGE)
    reports, failed = [], False
    for src in args:
        try:
            report, bad = _check_one(src, text_type, strict, config, gate)
        except ValueError as err:
            sys.exit(f"설정 파일 오류: {err}")
        reports.append(report)
        failed = failed or bad
    print(json.dumps(reports[0] if len(reports) == 1 else reports, ensure_ascii=False, indent=2))
    return 1 if gate and failed else 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: 테스트와 자체 시험을 돌려 통과를 확인한다**

Run: `chmod +x evals/ko_lint.py && python3 evals/ko_lint.py --self-test && python3 evals/tests/run.py && /usr/bin/python3 evals/tests/run.py`
Expected: `self-test OK: 24 violations in slop fixture, 0 in clean`(Task 7 뒤에는 슬롭 어휘가 늘어 24보다 클 수 있다), 이어서 두 번 모두 `ok` 61줄, 종료 코드 0.

- [ ] **Step 5: 큰 문서 속도를 직접 확인한다**

Run: `cd evals && python3 -c "import ko_lint, time; big=(ko_lint.SLOP_FIXTURE+'\n'+ko_lint.CLEAN_FIXTURE+'\n')*400; t=time.time(); ko_lint.lint(big, config={}); print(round(time.time()-t, 2))"; cd ..`
Expected: 1초 안팎(계획 검증 때 0.33초). 5초를 넘으면 `ko_text.units`와 `ko_terms.scan`을 먼저 의심한다.

- [ ] **Step 6: 커밋한다**

```bash
git add evals/ko_lint.py evals/tests/test_ko_lint.py
git commit -m "feat: add ko_lint API, CLI gate, and self-test fixtures" -m $'Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01SanRSLxxVtkLMJh1wLGeGZ'
```

### Task 7: 한국어 슬롭 어휘 목록

**Files:**
- Create: `tools/slop-lexicon/sources.json`, `tools/slop-lexicon/candidates.tsv`, `tools/slop-lexicon/exclusions.tsv`, `tools/slop-lexicon/build_slop.py`, `tools/slop-lexicon/README.md`, `evals/slop.tsv`(생성물), `NOTICE`
- Test: `evals/tests/test_slop_build.py`

**Interfaces:**
- Consumes: Task 3의 `ko_rules.lexical_hits(masked, slop_rx=...)`, `ko_rules.load_slop_terms(path)`
- Produces: `evals/slop.tsv`(열: 말, 출처 수, 바꿀 말. `#` 줄은 주석), `build_slop.rule_text(text)`, `count_sources(terms, texts) -> dict`, `covered_elsewhere(term) -> bool`, `build_rows(candidates, exclusions, texts, threshold=2) -> list[tuple]`, `discover(texts, known, threshold=2)`, `write_tsv(rows, n_sources, out)`, `fetch(sources, cache, opener)`, `source_texts(sources, cache) -> dict`. `ko_rules.SLOP_RX`는 import 때 `evals/slop.tsv`를 읽으므로 이 Task 뒤로 슬롭 범주의 수가 늘어난다.

- [ ] **Step 1: 실패하는 테스트를 쓴다**

`evals/tests/test_slop_build.py`:

```python
import importlib.util
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "evals"))
_spec = importlib.util.spec_from_file_location("build_slop", ROOT / "tools" / "slop-lexicon" / "build_slop.py")
build_slop = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(build_slop)


def test_rule_text_keeps_rule_lines_and_quotes():
    text = ("소개 문장입니다. 원활한 협업을 돕습니다.\n| 원활한 | 지우세요 |\n"
            "- \"획기적인\"을 지우세요\n일반 문장의 '강력한' 인용\n")
    got = build_slop.rule_text(text)
    assert "| 원활한 |" in got and "획기적인" in got and "강력한" in got
    assert "협업을 돕습니다" not in got


def test_count_sources_counts_each_source_once():
    texts = {"a": "| 원활한 | x |\n| 원활하게 | y |", "b": "- 원활한 처리", "c": "본문에만 원활한 말이 있습니다"}
    assert build_slop.count_sources(["원활"], texts) == {"원활": 2}


def test_covered_elsewhere_skips_other_categories():
    assert build_slop.covered_elsewhere("에 대해") is True
    assert build_slop.covered_elsewhere("것 같습니다") is True
    assert build_slop.covered_elsewhere("원활한") is False


def test_build_rows_threshold_exclusions_and_sort():
    texts = {k: "| 원활 | 획기적 | 강력한 | 에 대해 |" for k in "abc"}
    texts["d"] = "| 원활 |"
    rows = build_slop.build_rows([["원활", "(지우세요)"], ["획기적", "새"], ["강력한"], ["에 대해", "x"]],
                                 [["강력한", "시험용 제외"]], texts, threshold=3)
    assert rows == [("원활", 4, "(지우세요)"), ("획기적", 3, "새")], rows


def test_write_tsv_round_trips_through_linter_loader():
    import ko_rules
    with tempfile.TemporaryDirectory() as d:
        out = Path(d, "slop.tsv")
        build_slop.write_tsv([("원활", 4, "(지우세요)")], 10, out)
        assert out.read_text(encoding="utf-8").startswith("# SimpleKorean 슬롭 어휘")
        assert "원활" in ko_rules.load_slop_terms(out)


def test_fetch_uses_pinned_commit_and_separate_dirs():
    calls = []

    class Resp:
        def __init__(self, url):
            self.url = url

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

        def read(self):
            return "| 원활 |".encode("utf-8")

    def opener(url, timeout):
        calls.append(url)
        return Resp(url)

    with tempfile.TemporaryDirectory() as d:
        sources = [{"repo": "o/r", "commit": "abc123", "files": ["a/b.md"]}]
        build_slop.fetch(sources, cache=Path(d), opener=opener)
        assert calls == ["https://raw.githubusercontent.com/o/r/abc123/a/b.md"]
        assert Path(d, "o__r", "a", "b.md").read_text(encoding="utf-8") == "| 원활 |"
        assert build_slop.source_texts(sources, cache=Path(d)) == {"o/r": "| 원활 |"}
```

- [ ] **Step 2: 테스트를 돌려 실패를 확인한다**

Run: `python3 evals/tests/run.py evals/tests/test_slop_build.py`
Expected: `FileNotFoundError`(`tools/slop-lexicon/build_slop.py`가 없음)로 실패한다.

- [ ] **Step 3: 출처, 후보, 제외 목록, 도구를 쓴다**

`tools/slop-lexicon/sources.json`(커밋 SHA는 2026-10-08에 고정한 값이다):

```text
[
  {"repo": "epoko77-ai/im-not-ai", "commit": "2f3d943d08056b612a92e12bfb72ea94dd2acd18", "license": "MIT",
   "files": ["skills/humanize-korean/references/quick-rules.md", "skills/humanize-korean/references/ai-tell-taxonomy.md"]},
  {"repo": "IsaacEryn/humanizer-ko", "commit": "7d1a900c014f88e4f019d7cc79a22357494304f9", "license": "MIT",
   "files": ["SKILL.md"]},
  {"repo": "HarryJhin/korean-writing", "commit": "d138f9994c8260a068675c00c9004c654aca2f4b", "license": "MIT",
   "files": ["skills/writing-korean/SKILL.md", "lib/prose-checks.js"]},
  {"repo": "Jeon0976/tech-doc-kr", "commit": "a1270e41a9b843257d0976c254bce11cc17dc44d", "license": "MIT",
   "files": [".claude/skills/tech-doc-kr/references/calque-blacklist.md", ".claude/skills/tech-doc-kr/references/rules.md", ".claude/skills/tech-doc-kr/SKILL.md"]},
  {"repo": "Yoon-robin/claude-humanizer", "commit": "5c81379e2886c165c72f7bdebca1fa8f25969ab5", "license": "MIT",
   "files": ["skills/humanizer/references/languages/korean.md"]},
  {"repo": "nathankim0/humanize-korean", "commit": "b51aa5985be0a94a645788f1395b29a118bc9c33", "license": "MIT",
   "files": ["humanize-korean/references/ai-tell-rulebook.md", "humanize-korean/references/translationese-rules.md"]},
  {"repo": "leejonver/kaveman", "commit": "0341db98389a383bfaba838f0fe860edc359a94f", "license": "MIT",
   "files": ["skills/kaveman/SKILL.md"]},
  {"repo": "yoursemo/eli5-ko", "commit": "714e02549c4c703dd0b9569fb9b05af092b8a831", "license": "MIT",
   "files": ["skills/eli5/SKILL.md"]},
  {"repo": "yeomin4242/humanize-sepia", "commit": "528a81ffda18852bb26c293791ee7bf8291dafc6", "license": "MIT",
   "files": ["skills/humanize-sepia/references/editing.md"]},
  {"repo": "kys0213/kys-claude-plugin", "commit": "f26829a80c83cfbb7b69b9bbab516cd5db10645a", "license": "MIT",
   "files": ["plugins/atelier/skills/communicate/references/writing-standards.md"]}
]
```

`tools/slop-lexicon/candidates.tsv`(말과 바꿀 말을 탭으로 나눈다. 89줄):

```text
# 후보 말과 바꿀 말. 출처 수는 build_slop.py가 센다.
원활	(지우세요. 필요하면 수치를 쓰세요)
효율적	(무엇이 얼마나 줄었는지 쓰세요)
효과적	(무엇이 어떻게 나아졌는지 쓰세요)
강력한	(지우거나 측정할 수 있는 성질을 쓰세요)
강력하게	(지우세요)
혁신적	새
획기적	새
차세대	새
손쉽게	(지우세요)
간편하게	(지우세요)
쉽고 빠르게	(지우세요)
매끄럽게	(지우세요)
다양한	여러
핵심적	(지우고 사실을 쓰세요)
중요한 역할	(지우고 사실을 쓰세요)
필수적	(지우거나 의무로 쓰세요)
극대화	(무엇이 얼마나 늘었는지 쓰세요)
최적화된	(조건과 수치를 쓰세요)
최적의	(조건을 쓰세요)
포괄적	(항목을 쓰세요)
체계적	(지우세요)
전략적	(지우세요)
유의미한	(수치를 쓰세요)
견고한	(측정할 수 있는 성질을 쓰세요)
탁월한	(지우세요)
뛰어난	(지우세요)
놀라운	(지우세요)
완벽한	(지우세요)
완벽하게	(지우세요)
궁극적으로	(지우세요)
결론적으로	(지우세요)
요약하면	(지우세요)
요약하자면	(지우세요)
정리하자면	(지우세요)
정리하면	(지우세요)
한마디로	(지우세요)
이처럼	(지우세요)
더 나아가	또
나아가	또
뿐만 아니라	(두 문장으로 쓰세요)
시너지	(지우세요)
패러다임	방식
인사이트	(구체적으로 쓰세요)
생태계	(구체적으로 쓰세요)
여정	(지우세요)
활용하여	써서
활용해	써서
살펴보겠습니다	(지우고 바로 내용을 쓰세요)
알아보겠습니다	(지우고 바로 내용을 쓰세요)
소개해 드리겠습니다	(지우세요)
마무리하며	(지우세요)
주목할 만한	(지우세요)
눈여겨볼	(지우세요)
놀랍게도	(지우세요)
흥미롭게도	(지우세요)
본질적으로	(지우세요)
근본적으로	(지우세요)
진정한	(지우세요)
새로운 지평	(지우세요)
한 단계 더	(지우세요)
게임 체인저	(지우세요)
판도를 바꾸는	(지우세요)
무엇보다	(지우세요)
심층적	(지우세요)
다각적	(지우세요)
총체적	(지우세요)
직관적인	(무엇을 몇 단계로 하는지 쓰세요)
사용자 친화적	(지우세요)
원스톱	(지우세요)
고도화	개선
내재화	(구체적으로 쓰세요)
선제적	미리
시사점	(지우세요)
요컨대	(지우세요)
아울러	또
더불어	또
덧붙여	또
매우	(지우세요)
굉장히	(지우세요)
정말	(지우세요)
상당히	(수치를 쓰세요)
확장 가능한	(한계를 수치로 쓰세요)
안정적인	(수치를 쓰세요)
신뢰할 수 있는	(근거를 쓰세요)
효율성	(수치를 쓰세요)
자연스럽게	(지우세요)
손쉬운	(지우세요)
깔끔하게	(지우세요)
깊이 있는	(지우세요)
```

`tools/slop-lexicon/exclusions.tsv`:

```text
# 뺀 말과 이유를 탭으로 나눠 적는다. build_slop.py가 이 말을 slop.tsv에서 뺀다.
```

`tools/slop-lexicon/build_slop.py`:

```python
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


def load_sources(path=SOURCES):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _cache_dir(source, cache=CACHE):
    return Path(cache) / source["repo"].replace("/", "__")


def fetch(sources, cache=CACHE, opener=urllib.request.urlopen):
    """출처 파일을 고정 커밋으로 내려받는다. 출처마다 디렉터리를 따로 쓴다."""
    for s in sources:
        for rel in s["files"]:
            url = f"https://raw.githubusercontent.com/{s['repo']}/{s['commit']}/{rel}"
            dest = _cache_dir(s, cache) / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            with opener(url, timeout=30) as resp:
                dest.write_bytes(resp.read())
            print("fetched", url)


def source_texts(sources, cache=CACHE):
    """{출처: 파일들을 이은 원문}. 파일이 없으면 fetch를 먼저 하라고 알리고 멈춘다."""
    texts = {}
    for s in sources:
        parts = []
        for rel in s["files"]:
            p = _cache_dir(s, cache) / rel
            if not p.exists():
                raise SystemExit(f"{p}가 없습니다. 먼저 fetch를 실행하세요.")
            parts.append(p.read_text(encoding="utf-8", errors="replace"))
        texts[s["repo"]] = "\n".join(parts)
    return texts


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    command = args[0] if args else "build"
    sources = load_sources()
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
```

- [ ] **Step 4: 테스트를 돌려 통과를 확인한다**

Run: `python3 evals/tests/run.py evals/tests/test_slop_build.py`
Expected: `ok` 6줄, 종료 코드 0.

- [ ] **Step 5: 출처를 내려받고 출처 수를 확인한다**

Run: `python3 -I tools/slop-lexicon/build_slop.py fetch && python3 -I tools/slop-lexicon/build_slop.py report | head -25`
Expected: `fetched` 14줄. 보고서 맨 위가 `5 다양한`, `5 정말`, `5 혁신적`, `4 결론적으로` 순이다(2026-10-08 계획 검증 값). 내려받기가 실패하면 네트워크를 먼저 확인한다(`curl -sI https://raw.githubusercontent.com`).

- [ ] **Step 6: 목록을 만들고 사람이 검토한다**

Run: `python3 -I tools/slop-lexicon/build_slop.py build && cat evals/slop.tsv`
Expected: `20 terms -> .../evals/slop.tsv`. 다양한, 정말, 혁신적, 결론적으로, 강력한, 나아가, 매우, 완벽한, 자연스럽게, 획기적, 효과적, 본질적으로, 뿐만 아니라, 아울러, 여정, 완벽하게, 요약하면, 원활, 정리하자면, 핵심적 순이다.

20개를 모두 읽는다. 기술 문서에서 사실을 담는 말이 있으면 `exclusions.tsv`에 `말<TAB>이유`로 적고 다시 빌드한다. 계획 검증 때는 뺄 말이 없었다. 뺀 말이 생기면 `tools/slop-lexicon/README.md`의 마지막 문단도 고친다.

- [ ] **Step 7: 린터 자체 시험과 전체 테스트를 다시 돌린다**

Run: `python3 evals/ko_lint.py --self-test && python3 evals/tests/run.py && /usr/bin/python3 evals/tests/run.py`
Expected: `self-test OK: 24 violations in slop fixture, 0 in clean`, 두 번 모두 `ok` 67줄. 깨끗한 예문이 0이 아니면 새 슬롭 말이 그 예문에 걸린 것이므로, 그 말을 `exclusions.tsv`에 이유와 함께 적는다.

- [ ] **Step 8: 설명 문서와 NOTICE를 쓴다**

`tools/slop-lexicon/README.md`:

````markdown
# 슬롭 어휘 목록 만들기

`evals/slop.tsv`는 이 디렉터리의 `build_slop.py`가 만듭니다. 원본 SimpleEnglish는 공개된 금지 목록 122개 가운데 8개 이상에 나온 말을 골랐습니다. 이 프로젝트는 같은 방법을 한국어 자료에 씁니다.

1. `sources.json`에 적은 한국어 AI 문체 스킬 10곳을 고정 커밋으로 내려받습니다. 모두 MIT 라이선스입니다.
2. 출처마다 규칙으로 보이는 부분만 남깁니다. 표 행, 목록 항목, 화살표가 있는 줄, 따옴표와 백틱 안의 말입니다.
3. `candidates.tsv`의 후보 말마다 그 말을 담은 출처 수를 셉니다.
4. 출처 2곳 이상에 나온 말만 남깁니다. 다른 린트 범주(번역투, 짐작 표현)가 이미 잡는 말과 `exclusions.tsv`에 적은 말은 뺍니다.

```bash
python3 -I tools/slop-lexicon/build_slop.py fetch
python3 -I tools/slop-lexicon/build_slop.py report
python3 -I tools/slop-lexicon/build_slop.py build
```

문턱은 출처 10곳 가운데 2곳(20%)입니다. 원본의 비율(122곳 가운데 8곳, 약 6.6%)보다 엄격합니다. 출처들은 서로 독립이 아닙니다. 일부는 다른 출처를 바탕으로 만들었으므로, 출처 수는 독립된 판단의 수가 아니라 여러 목록에 함께 나온 정도로 읽으세요.

`report`는 후보에 없는 따옴표 속 말도 출처 수와 함께 보여 줍니다. 새 후보를 더하려면 `candidates.tsv`에 한 줄을 더하고 다시 빌드하세요. 빌드 결과에서 기술 문서에 사실을 더하는 말을 찾으면 `exclusions.tsv`에 이유와 함께 적으세요.

2026-10-08 첫 빌드 결과는 20개이고, 검토에서 뺀 말은 없습니다.

`cache/`에는 내려받은 출처 원문이 있습니다. 레포에 넣지 않습니다.
````

`NOTICE`(Task 13에서 2번 항목을 더한다):

```text
SimpleKorean
Copyright (c) 2026 say8425

이 프로젝트는 AminBlg/SimpleEnglish(https://github.com/AminBlg/SimpleEnglish, MIT License,
Copyright (c) 2026 AminBlg)의 한국어 파생 프로젝트입니다.

제3자 자료

1. evals/slop.tsv
   tools/slop-lexicon/build_slop.py가 아래 MIT 라이선스 저장소의 고정 커밋에서 말마다 출처 수를
   세어 만든 목록입니다. 출처 원문은 싣지 않습니다. 저장소와 커밋은
   tools/slop-lexicon/sources.json에 있습니다.
   - epoko77-ai/im-not-ai
   - IsaacEryn/humanizer-ko
   - HarryJhin/korean-writing
   - Jeon0976/tech-doc-kr
   - Yoon-robin/claude-humanizer
   - nathankim0/humanize-korean
   - leejonver/kaveman
   - yoursemo/eli5-ko
   - yeomin4242/humanize-sepia
   - kys0213/kys-claude-plugin
```

- [ ] **Step 9: 커밋한다**

```bash
chmod +x tools/slop-lexicon/build_slop.py
git add tools/slop-lexicon evals/slop.tsv evals/tests/test_slop_build.py NOTICE
git status --short | grep cache && echo "cache가 스테이징되면 안 된다" || true
git commit -m "feat: build Korean slop lexicon from pinned public lists" -m $'Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01SanRSLxxVtkLMJh1wLGeGZ'
```

---

## 단계 B: 스킬 문서

이 단계의 문서는 계획을 쓰면서 린터로 검증했다. 그대로 옮기면 `--gate=warning`까지 통과한다(오류 0, 경고 0). 문장을 고치면 Step의 린트 명령을 다시 돌려 확인한다.

### Task 8: SKILL.md, 시스템 프롬프트, 출력 스타일

**Files:**
- Create: `skills/simple-korean/SKILL.md`, `prompts/system-prompt.md`, `output-styles/simple-korean.md`

**Interfaces:**
- Consumes: Task 6의 `evals/ko_lint.py --gate`, Task 7의 `evals/slop.tsv`
- Produces: 규칙 블록. `prompts/system-prompt.md`의 첫 `---` 줄과 둘째 `---` 줄 사이가 규칙 블록이고, `output-styles/simple-korean.md`의 frontmatter 뒤 본문과 글자 하나까지 같다(Task 10 훅과 Task 14 벤치마크가 이 블록을 읽는다). SKILL.md frontmatter의 `metadata.version: "1.0.0"`(Task 18 수치 검증이 읽는다). 핵심 문구 "서술형으로 답하세요", "em-dash를 쓰지 마세요", "첫 문장에 답", "바꾸지 마세요", "확인하다", "레포지토리"(SKILL.md와 규칙 블록 모두에 있다).

- [ ] **Step 1: 린트 관문이 아직 실패하는지 확인한다**

Run: `python3 evals/ko_lint.py --gate skills/simple-korean/SKILL.md`
Expected: `No such file or directory` 메시지와 함께 0이 아닌 종료 코드.

- [ ] **Step 2: SKILL.md를 쓴다**

`skills/simple-korean/SKILL.md`:

````markdown
---
name: simple-korean
description: |
  기술 문서와 채팅 답변을 쉬운 한국어로 쓰거나 고칩니다. 항공 정비용 통제 영어 ASD-STE100의 규칙을
  한국어에 맞게 다시 세웠습니다. 짧은 문장, 명령 앞의 조건, 한 단어 한 뜻, 번역투와 AI 슬롭 제거,
  정해진 외래어 표기를 지킵니다. README, 런북, 오류 메시지, 릴리스 노트, 장애 보고서, 분야 밖 독자를
  위한 설명에 쓰세요. "쉬운 한국어", "번역투 빼 줘", "AI 티 안 나게", "plain Korean", "통제 언어",
  "엄격 모드", "KS A 0001"이라고 할 때도 쓰세요.
license: MIT
compatibility: claude-code cursor codex gemini-cli opencode
metadata:
  version: "1.0.0"
  upstream: "AminBlg/SimpleEnglish 2.1.1 (a6fcb4f)"
---

# Simple Korean

분야 밖의 똑똑한 독자가 한 번 읽고 이해하는 한국어를 쓰세요. 규칙은 항공 정비 매뉴얼에 쓰는 통제 영어 ASD-STE100에서 왔고, 한국어 문법에 맞게 다시 세웠습니다. 규칙은 두 영역으로 나뉩니다. 쓰거나 고치는 문서와 채팅으로 보내는 답변입니다.

## 문서

문서를 쓰거나 고칠 때 본문에 다음 규칙을 적용하세요.

1. 글을 절차문과 설명문으로 나누세요. 절차문은 독자가 할 일을 말합니다. "-하세요"로 쓰고, 한 문장에 동작 하나, 15어절 이하로 쓰세요. 설명문은 사실을 말합니다. "-습니다"로 쓰고, 한 문장에 명제 하나, 20어절 이하로 쓰세요. 한 문단에는 주제 하나, 문장 6개 이하를 두세요.
2. 코드, 식별자, 명령, 플래그, 경로, 인용한 오류 문구, 제품 이름, 사실은 바꾸지 마세요. 제품 이름과 식별자를 음차하거나 번역하지 마세요. 원문에 숫자나 원인이 없으면 일반 진술을 그대로 두세요.
3. 조건은 "-면"으로 명령 앞에 두세요. "빌드가 실패하면 로그를 읽으세요." "만약"을 붙이지 말고, 명령 뒤에 "단, ~경우"를 덧붙이지 마세요.
4. 단순 현재와 단순 과거로 쓰세요. 진행이 아니면 "-고 있습니다"를 쓰지 마세요. "-되어지다", "보여지다" 같은 이중 피동을 쓰지 마세요. "~에 의해 ~되다"는 행위자를 주어로 바꾸세요. "-함으로써"로 결과를 덧붙이지 말고 새 문장으로 쓰세요. 행위자가 중요하면 밝히세요. "sqlpipe가 행을 지웁니다."
5. 양태는 "-ㄹ 수 있습니다", 현재형, "-해야 합니다"만 쓰세요. "-ㄹ 수도 있습니다", "-것 같습니다", "-하는 것이 좋습니다", "-하시기 바랍니다", "-ㄹ 것입니다"는 쓰지 마세요. 필수 사항은 "-해야 합니다"로 쓰세요. 선택 사항은 지우거나 사실로 쓰세요.
6. 문법을 다 갖추세요. 조사를 빼지 마세요. 본문 문장을 "-함", "-음", "-필요"로 끝내지 마세요. "겁니다", "근데" 같은 구어 축약을 쓰지 마세요. 한 문서에는 문체 하나만 쓰세요. 새 문서는 서술에 "-습니다", 지시에 "-하세요"를 쓰세요. 기존 문서를 고칠 때는 그 문서의 문체를 따르세요.
7. 세미콜론과 em-dash를 쓰지 마세요. 두 문장으로 쓰거나 "때문에", "하지만"으로 관계를 밝히세요.
8. 한 단어에는 한 뜻만 주세요. 확인, 검증, 점검, 체크는 "확인하다" 하나로 쓰세요. 설정 파일은 "설정"이라고 부르고 "구성 파일", "컨피그"와 섞지 마세요. 명사는 3개까지만 이으세요. 더 길면 조사로 푸세요. "연결 풀의 타임아웃 값." "배포를 진행합니다"처럼 "진행하다", "수행하다"를 붙이지 말고 "배포합니다"로 쓰세요.
9. 독자가 단계에 필요한 용어와 사실을 그 단계 전에 알게 하세요. 개념 용어는 처음 쓸 때 열 어절 이하로 풀이하세요. 번역한 기술 용어는 처음 한 번 원어를 괄호에 함께 쓰세요. "멱등성(idempotency)." 제품 이름, 표준 이름(Postgres, S3, HTTP), 문서가 다루는 도구는 풀이하지 마세요. 명령이 기대는 호스트, 플래그, 앞 단계도 밝히세요. "서비스를 다시 시작하세요"는 "작업을 실행하는 호스트에서 `sync` 서비스를 다시 시작하세요"가 됩니다.
10. 중요성 말고 사실을 쓰세요. "원활하게", "강력한", "손쉽게", "획기적인"처럼 사실을 담지 않은 말을 지우세요. "~에 대해", "~를 통해", "~로 인해" 같은 번역투를 고치세요. "단순히 X가 아니라 Y입니다", 장식용 세 항목 나열, "결론적으로"로 시작하는 문단을 쓰지 마세요.
11. 구조를 나타낼 때만 서식을 쓰세요. 굵은 글씨로 시작하는 문단, 강조용 굵은 글씨, 이모지, 두 문장도 덮지 않는 제목을 쓰지 마세요. 세로 목록은 셋 이상의 나란한 항목이나 단계에 쓰고, 앞 문장은 쌍점으로 끝내세요. 항목은 모두 명사구이거나 모두 문장이어야 합니다.
12. 경고는 명령이나 조건을 먼저 쓰고 위험을 다음에 쓰세요. "운영 DB에서 이 명령을 실행하지 마세요. 이 명령은 행을 지웁니다." "경고:"는 사람이 다칠 위험에, "주의:"는 데이터나 장비가 손상될 위험에 쓰세요.
13. 외래어는 외래어 표기법과 국립국어원 용례를 따르세요(디렉터리, 메시지, 애플리케이션). 단어 목록에 있는 단어는 목록의 형태를 쓰세요. 공식 표기가 없는 단어도 목록의 형태를 씁니다(리디렉션, 리팩터링). 전문 용어 합성어는 붙여 쓰세요(기본값, 매개변수). 제품 이름, 화면 문구 인용, API 객체 이름, 코드는 원래 표기 그대로 둡니다. 한 문서에서 한 개념은 한 형태로만 쓰세요.

단어 목록의 핵심 단어는 네 무리입니다:

<!-- simple-korean: off -->
- 규범대로 쓰는 말: 메시지, 애플리케이션, 콘텐츠, 아키텍처, 스레드, 메서드, 라이선스, 액세스, 스케줄, 비즈니스, 세팅, 매뉴얼, 캐시, 대시보드, 해시, 포맷, 렌더링, 트랜잭션, 버전, 헤더, 데이터, 컴포넌트, 프레임워크, 디렉터리, 릴리스, 셸
- 이 프로젝트가 정한 말: 레포지토리, 바디, 칼럼, 대상, 리디렉션, 리팩터링
- 외래어 대신 쓰는 말: 오류, 매개변수, 사용자, 기본값, 배포
- 붙여 쓰는 말: 기본값, 매개변수, 반환값, 오픈소스
<!-- simple-korean: on -->

목록 전체와 근거는 플러그인의 `data/terms.json`에 있습니다. 프로젝트의 `.simple-korean.json`이 지정형을 바꿀 수 있습니다.

고치기 전(AI 출력):

<!-- simple-korean: off -->
> **연결 타임아웃.** sqlpipe가 멈추거나 `dial tcp: i/o timeout` 오류와 함께 실패한다면, sqlpipe를 실행하는 호스트가 Postgres 포트(보통 5432)에 접근할 수 있는지 확인해 보시기 바랍니다 — 이는 보안 그룹이나 방화벽 규칙에 의해 연결이 차단되어지는 경우가 많기 때문입니다. 관리형 데이터베이스(RDS, Cloud SQL 등)에 연결하고 있다면, 인스턴스가 sqlpipe의 IP로부터의 연결을 허용하는지 검증하는 것이 좋습니다.
<!-- simple-korean: on -->

고친 뒤(절차문, 제목, 번호 목록):

> ## 연결 타임아웃
>
> sqlpipe는 Postgres 포트(기본값 5432)에 연결하지 못하면 `dial tcp: i/o timeout` 오류를 내고 멈춥니다.
>
> 1. sqlpipe를 실행하는 호스트가 Postgres 포트에 연결할 수 있는지 확인하세요. 보통 방화벽이나 보안 그룹이 연결을 막습니다.
> 2. 데이터베이스가 관리형(RDS, Cloud SQL)이면, 인스턴스가 sqlpipe의 IP에서 오는 연결을 허용하는지 확인하세요.

## 답변

모든 모드에서 채팅 답변은 다음 규칙을 따르세요.

1. 서술형으로 답하세요. 헤더, 불릿, 굵은 글씨, 표를 쓰지 마세요. 독자가 복사해야 하는 코드만 코드 블록에 두세요.
2. 첫 문장에 답이나 결과를 쓰세요. 질문을 되풀이하지 말고, "네, ~에 대해 설명드리겠습니다"로 시작하지 마세요.
3. em-dash를 쓰지 마세요. "때문에", "하지만", "예를 들어"로 관계를 밝히거나 두 문장으로 나누세요.
4. 개념 용어는 처음 쓸 때 짧게 풀이하세요. "멱등(같은 요청을 여러 번 보내도 결과가 같음)." 제품 이름은 풀이하지 마세요.
5. 한 답변에는 문체 하나만 쓰세요. 기본은 "-습니다"이고, 사용자가 다른 문체를 원하면 그 문체를 쓰세요. "좋은 질문입니다", "물론입니다" 같은 인사말과 "도움이 되셨기를 바랍니다", "원하시면 더 알려 드리겠습니다" 같은 맺음말을 쓰지 마세요.
6. 인용한 오류 문구, 보안 경고, 되돌릴 수 없는 작업 전의 확인 문구는 줄이지 마세요.

고치기 전:

<!-- simple-korean: off -->
> 좋은 질문입니다! 이 장애는 파드 교체 중 컨트롤 플레인의 리더 선출로 인해 발생한 것으로 보입니다 — 걱정하실 필요는 전혀 없습니다!
<!-- simple-korean: on -->

고친 뒤:

> 파드가 다시 시작되었고, 큐는 잠시 리더를 잃었습니다. 큐는 스스로 복구했습니다. 따로 할 일은 없습니다.

## 내기 전 자가 점검

1. 답변: `—`, `**`, `#`, `-`로 시작하는 줄을 찾아 없애세요.
2. 문서: 가장 긴 세 문장의 어절을 세고, 15어절이나 20어절을 넘으면 나누세요. 그다음 아래 표현을 찾아 고치세요:
   - 번역투: "에 대해", "를 통해", "에 의해", "되어지", "고 있습니다"
   - 짐작과 권고: "수도 있", "것 같", "것이 좋", "ㄹ 것입니다"
   - 기능동사: "진행합니다", "수행합니다"
   - 부호와 서식: `;`, `—`, `**`
   - 목록에 없는 표기, "확인" 외의 검증 동사, 두 문장도 덮지 않는 제목
3. 단계마다 필요한 호스트, 플래그, 앞 단계를 밝혔는지 확인하세요.

## 모드

기본 모드는 이 파일의 규칙 전부입니다. 사용자가 엄격 모드, 통제 언어, KS A 0001, STE, ASD-STE100을 말하면 엄격 모드를 쓰세요. 문서를 쓰기 전에 `references/strict-mode.md`를 읽고, 그 규칙을 문서에만 적용하세요. 답변은 모든 모드에서 기본 모드 규칙을 따릅니다. 엄격 모드를 켤 때 한 번만 이렇게 알리세요. "한국어 통제 언어 국가 표준은 없으며, 이 기준은 KS A 0001과 공개 연구를 바탕으로 한 비공식 기준입니다."

점검을 요청받거나 적용한 규칙의 번호를 적어야 하면 먼저 `references/rule-catalog.md`를 여세요. 위반마다 그 파일의 K 번호, 해당 문구, 고친 문장을 보고하세요. 규칙 번호를 기억에 기대 인용하지 마세요. 엄격 모드 규칙으로 확인했으면 끝에 엄격 모드의 비공식 기준 고지를 한 문장 붙이세요.

## 한계

이 규칙은 사실과 지시를 위한 것입니다. 설득하는 문장을 지우기 때문에 마케팅이나 브랜드 글에는 맞지 않습니다. 그런 글을 요청받으면 이 점을 알리고, 그 글이 링크할 문서에 규칙을 쓰자고 제안하세요.

## 참고 파일

- `references/rule-catalog.md`: K 번호 규칙 전체(점검 모드용)
- `references/strict-mode.md`: 엄격 모드의 문장 끝, 접속어, 단어 규칙
- `references/word-swaps.md`: 슬롭 어휘와 번역투를 쉬운 말로 바꾸는 표
- `references/use-cases.md`: 오류 메시지, 런북, 장애 보고, 릴리스 노트, 커밋, 에이전트 지침, UI 문구의 모드와 형식
````

- [ ] **Step 3: 시스템 프롬프트를 쓴다**

`prompts/system-prompt.md`:

````markdown
# 시스템 프롬프트

스킬을 지원하지 않는 도구에서 쓰는 판본입니다. 아래 블록을 시스템 프롬프트, 사용자 지침, AGENTS.md, `.cursorrules`에 붙여 넣으세요. 전체 스킬을 줄인 판본입니다.

---

분야 밖의 똑똑한 독자가 한 번 읽고 이해하는 한국어를 쓰세요. 규칙은 항공 정비 매뉴얼에 쓰는 통제 영어 ASD-STE100에서 왔고, 한국어 문법에 맞게 다시 세웠습니다. 문서와 답변에 규칙이 따로 있습니다.

문서(README, 런북, 오류 메시지, 릴리스 노트, 장애 보고서, 커밋 메시지). 코드, 식별자, 명령, 경로, 인용한 오류 문구, 제품 이름, 사실은 바꾸지 마세요. 절차문은 "-하세요"로 쓰고, 한 문장에 동작 하나, 15어절 이하로 쓰세요. 설명문은 "-습니다"로 쓰고, 한 문장에 명제 하나, 20어절 이하로 쓰세요. 한 문단에는 주제 하나, 문장 6개 이하를 두세요. 조건은 "-면"으로 명령 앞에 두고 "만약"을 붙이지 마세요. 단순 현재와 단순 과거로 쓰세요. 진행이 아니면 "-고 있습니다"를 쓰지 말고, 이중 피동("-되어지다")과 "~에 의해"도 쓰지 마세요. 양태는 "-ㄹ 수 있습니다", 현재형, "-해야 합니다"만 쓰세요. "-ㄹ 수도 있습니다", "-것 같습니다", "-하는 것이 좋습니다", "-하시기 바랍니다", "-ㄹ 것입니다"는 쓰지 마세요. 조사를 빼지 말고, 본문 문장을 "-함", "-음"으로 끝내지 마세요. 한 문서에는 문체 하나만 쓰세요. 세미콜론과 em-dash를 쓰지 마세요. 한 단어에는 한 뜻만 주세요. 확인 동작은 "확인하다", 설정 파일은 "설정"으로 통일하세요. 명사는 3개까지만 잇고, "진행하다", "수행하다"를 붙이지 말고 동사 하나로 쓰세요. 개념 용어는 처음 쓸 때 열 어절 이하로 풀이하세요. 번역한 기술 용어는 처음 한 번 원어를 괄호에 쓰세요. 명령이 기대는 호스트, 플래그, 앞 단계를 밝히세요. 사실을 담지 않은 말("원활하게", "강력한", "손쉽게")과 번역투("~에 대해", "~를 통해", "~로 인해")를 지우세요. "단순히 X가 아니라 Y", 장식용 세 항목 나열, "결론적으로" 문단을 쓰지 마세요. 굵은 글씨로 시작하는 문단, 강조용 굵은 글씨, 이모지, 두 문장도 덮지 않는 제목을 쓰지 마세요. 경고는 명령이나 조건을 먼저, 위험을 다음에 쓰세요. 외래어는 외래어 표기법을 따르세요(디렉터리, 메시지, 애플리케이션, 릴리스, 셸). 이 프로젝트의 지정형은 레포지토리, 바디, 칼럼, 대상, 리디렉션, 리팩터링입니다. 오류, 매개변수, 사용자, 기본값, 배포를 쓰고, 전문 용어 합성어는 붙여 쓰세요(반환값, 오픈소스).

자가 점검. 가장 긴 세 문장의 어절을 세고 넘으면 나누세요. 그다음 "에 대해", "를 통해", "되어지", "고 있습니다", "수도 있", "것 같", "ㄹ 것입니다", "진행합니다", ";", "—"를 찾아 고치세요.

엄격 모드. 사용자가 엄격 모드, 통제 언어, KS A 0001, STE를 말하면 문서에 다음을 더하세요. 문장 끝은 "-해야 합니다", "-하면 안 됩니다", "-해도 됩니다", "-ㄹ 수 있습니다"(능력만), 현재형만 씁니다. "반드시"는 외부 규정에만 쓰세요. "(이)나" 대신 "와/과", "및", "또는"을 쓰고, 조건은 "-면"으로만 쓰세요. 한 번만 알리세요. "한국어 통제 언어 국가 표준은 없으며, 이 기준은 KS A 0001과 공개 연구를 바탕으로 한 비공식 기준입니다."

코드, 코드를 인용한 주석, 사용자가 요청한 마케팅 글에는 이 규칙을 적용하지 마세요.

답변(모든 모드의 채팅 답변). 서술형으로 답하세요. 헤더, 불릿, 굵은 글씨, 표를 쓰지 마세요. 독자가 복사해야 하는 코드만 코드 블록에 두세요. 첫 문장에 답이나 결과를 쓰고, 질문을 되풀이하지 마세요. em-dash를 쓰지 말고 "때문에", "하지만", "예를 들어"로 관계를 밝히세요. 개념 용어는 처음 쓸 때 짧게 풀이하세요("멱등(같은 요청을 여러 번 보내도 결과가 같음)"). 제품 이름은 풀이하지 마세요. 한 답변에는 문체 하나만 쓰고, 기본은 "-습니다"입니다. 인사말("좋은 질문입니다", "물론입니다")과 맺음말("도움이 되셨기를 바랍니다", "원하시면 더 알려 드리겠습니다")을 쓰지 마세요. 인용한 오류 문구, 보안 경고, 되돌릴 수 없는 작업 전의 확인 문구는 줄이지 마세요.

---

## 짧은 판본 (약 120토큰)

시스템 프롬프트가 짧아야 할 때 쓰세요.

> 답변: 서술형만, 첫 문장에 답, 헤더·불릿·굵은 글씨·표·em-dash 금지, 용어 풀이, 인사말과 맺음말 금지. 문서: 절차문 15어절 "-하세요", 설명문 20어절 "-습니다", 조건은 명령 앞에, 단순 시제와 능동. 짐작 표현, 번역투, 슬롭 금지, 한 단어 한 뜻, 외래어 표기법, 코드는 그대로.
````

- [ ] **Step 4: 출력 스타일을 쓴다**

`output-styles/simple-korean.md`(본문은 위 규칙 블록과 같다):

````markdown
---
name: simple-korean
description: 모든 글을 쉬운 한국어로 씁니다. ASD-STE100의 규칙을 한국어 문법에 맞게 다시 세운 규칙입니다.
keep-coding-instructions: true
---

분야 밖의 똑똑한 독자가 한 번 읽고 이해하는 한국어를 쓰세요. 규칙은 항공 정비 매뉴얼에 쓰는 통제 영어 ASD-STE100에서 왔고, 한국어 문법에 맞게 다시 세웠습니다. 문서와 답변에 규칙이 따로 있습니다.

문서(README, 런북, 오류 메시지, 릴리스 노트, 장애 보고서, 커밋 메시지). 코드, 식별자, 명령, 경로, 인용한 오류 문구, 제품 이름, 사실은 바꾸지 마세요. 절차문은 "-하세요"로 쓰고, 한 문장에 동작 하나, 15어절 이하로 쓰세요. 설명문은 "-습니다"로 쓰고, 한 문장에 명제 하나, 20어절 이하로 쓰세요. 한 문단에는 주제 하나, 문장 6개 이하를 두세요. 조건은 "-면"으로 명령 앞에 두고 "만약"을 붙이지 마세요. 단순 현재와 단순 과거로 쓰세요. 진행이 아니면 "-고 있습니다"를 쓰지 말고, 이중 피동("-되어지다")과 "~에 의해"도 쓰지 마세요. 양태는 "-ㄹ 수 있습니다", 현재형, "-해야 합니다"만 쓰세요. "-ㄹ 수도 있습니다", "-것 같습니다", "-하는 것이 좋습니다", "-하시기 바랍니다", "-ㄹ 것입니다"는 쓰지 마세요. 조사를 빼지 말고, 본문 문장을 "-함", "-음"으로 끝내지 마세요. 한 문서에는 문체 하나만 쓰세요. 세미콜론과 em-dash를 쓰지 마세요. 한 단어에는 한 뜻만 주세요. 확인 동작은 "확인하다", 설정 파일은 "설정"으로 통일하세요. 명사는 3개까지만 잇고, "진행하다", "수행하다"를 붙이지 말고 동사 하나로 쓰세요. 개념 용어는 처음 쓸 때 열 어절 이하로 풀이하세요. 번역한 기술 용어는 처음 한 번 원어를 괄호에 쓰세요. 명령이 기대는 호스트, 플래그, 앞 단계를 밝히세요. 사실을 담지 않은 말("원활하게", "강력한", "손쉽게")과 번역투("~에 대해", "~를 통해", "~로 인해")를 지우세요. "단순히 X가 아니라 Y", 장식용 세 항목 나열, "결론적으로" 문단을 쓰지 마세요. 굵은 글씨로 시작하는 문단, 강조용 굵은 글씨, 이모지, 두 문장도 덮지 않는 제목을 쓰지 마세요. 경고는 명령이나 조건을 먼저, 위험을 다음에 쓰세요. 외래어는 외래어 표기법을 따르세요(디렉터리, 메시지, 애플리케이션, 릴리스, 셸). 이 프로젝트의 지정형은 레포지토리, 바디, 칼럼, 대상, 리디렉션, 리팩터링입니다. 오류, 매개변수, 사용자, 기본값, 배포를 쓰고, 전문 용어 합성어는 붙여 쓰세요(반환값, 오픈소스).

자가 점검. 가장 긴 세 문장의 어절을 세고 넘으면 나누세요. 그다음 "에 대해", "를 통해", "되어지", "고 있습니다", "수도 있", "것 같", "ㄹ 것입니다", "진행합니다", ";", "—"를 찾아 고치세요.

엄격 모드. 사용자가 엄격 모드, 통제 언어, KS A 0001, STE를 말하면 문서에 다음을 더하세요. 문장 끝은 "-해야 합니다", "-하면 안 됩니다", "-해도 됩니다", "-ㄹ 수 있습니다"(능력만), 현재형만 씁니다. "반드시"는 외부 규정에만 쓰세요. "(이)나" 대신 "와/과", "및", "또는"을 쓰고, 조건은 "-면"으로만 쓰세요. 한 번만 알리세요. "한국어 통제 언어 국가 표준은 없으며, 이 기준은 KS A 0001과 공개 연구를 바탕으로 한 비공식 기준입니다."

코드, 코드를 인용한 주석, 사용자가 요청한 마케팅 글에는 이 규칙을 적용하지 마세요.

답변(모든 모드의 채팅 답변). 서술형으로 답하세요. 헤더, 불릿, 굵은 글씨, 표를 쓰지 마세요. 독자가 복사해야 하는 코드만 코드 블록에 두세요. 첫 문장에 답이나 결과를 쓰고, 질문을 되풀이하지 마세요. em-dash를 쓰지 말고 "때문에", "하지만", "예를 들어"로 관계를 밝히세요. 개념 용어는 처음 쓸 때 짧게 풀이하세요("멱등(같은 요청을 여러 번 보내도 결과가 같음)"). 제품 이름은 풀이하지 마세요. 한 답변에는 문체 하나만 쓰고, 기본은 "-습니다"입니다. 인사말("좋은 질문입니다", "물론입니다")과 맺음말("도움이 되셨기를 바랍니다", "원하시면 더 알려 드리겠습니다")을 쓰지 마세요. 인용한 오류 문구, 보안 경고, 되돌릴 수 없는 작업 전의 확인 문구는 줄이지 마세요.
````

- [ ] **Step 5: 린트 관문과 동기화를 확인한다**

Run: `python3 evals/ko_lint.py --gate=warning skills/simple-korean/SKILL.md prompts/system-prompt.md output-styles/simple-korean.md > /tmp/sk-gate.json; echo "exit=$?"`
Expected: `exit=0`.

Run:

```bash
python3 - <<'SYNC_EOF'
import re, pathlib
prompt = pathlib.Path("prompts/system-prompt.md").read_text(encoding="utf-8")
block = re.split(r"^---[ \t]*$", prompt, flags=re.M)[1].strip()
style = pathlib.Path("output-styles/simple-korean.md").read_text(encoding="utf-8")
body = re.sub(r"\A---\n.*?\n---\n", "", style, count=1, flags=re.S).strip()
assert block == body, "규칙 블록과 출력 스타일 본문이 다릅니다"
print("rule block in sync,", len(block), "chars")
SYNC_EOF
```

Expected: `rule block in sync, 2010 chars` 안팎(정확한 글자 수는 문장을 고치면 달라진다).

- [ ] **Step 6: 커밋한다**

```bash
git add skills/simple-korean/SKILL.md prompts/system-prompt.md output-styles/simple-korean.md
git commit -m "feat: write SimpleKorean skill, system prompt, and output style" -m $'Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01SanRSLxxVtkLMJh1wLGeGZ'
```

### Task 9: 레퍼런스 문서 네 개

**Files:**
- Create: `skills/simple-korean/references/rule-catalog.md`, `skills/simple-korean/references/strict-mode.md`, `skills/simple-korean/references/word-swaps.md`, `skills/simple-korean/references/use-cases.md`

**Interfaces:**
- Consumes: Task 5의 단어 목록 무리와 지정형, Task 7의 `evals/slop.tsv`
- Produces: K 번호 체계 K1~K10과 S1~S6(점검 모드가 인용한다). 문서끼리의 참조: SKILL.md가 네 파일을 이름으로 가리키고, `word-swaps.md`는 `rule-catalog.md`의 양태 사다리를 가리킨다.

- [ ] **Step 1: 린트 관문이 아직 실패하는지 확인한다**

Run: `python3 evals/ko_lint.py --gate skills/simple-korean/references/rule-catalog.md`
Expected: `No such file or directory` 메시지와 함께 0이 아닌 종료 코드.

- [ ] **Step 2: 규칙 목록을 쓴다**

`skills/simple-korean/references/rule-catalog.md`:

````markdown
# 규칙 목록: SimpleKorean의 K 규칙

점검 모드, 엄격 모드, 규칙 번호를 확인할 때 이 파일을 여세요. `SKILL.md`에는 출력을 가장 많이 바꾸는 규칙만 있습니다. 이 파일에는 전체 목록이 있습니다.

K 규칙은 ASD-STE100 Issue 9의 9개 절 구조를 따르고, 표기 절(K10)과 엄격 모드 절(S)을 더했습니다. 출처 열에는 대응하는 STE 규칙 번호, KS A 0001:2023 조항, 학술 연구, 이 프로젝트의 측정을 적었습니다. 이 목록은 STE의 번역이 아닙니다. 한국어용으로 다시 세운 비공식 규칙입니다. STE 원문은 asd-ste100.org에서 무료로 받을 수 있습니다.

### K1: 단어

| 규칙 | 지시 | 출처 |
|---|---|---|
| K1.1 | 한 대상에는 이름 하나만 쓰세요. 한 곳에서 "설정"이라고 부른 것을 다른 곳에서 "구성 파일"이라고 부르지 마세요. | STE 1.11 |
| K1.2 | 프로젝트와 업계의 기술 명사를 쓰세요("웹훅", "커밋", "엔드포인트"). | STE 1.5, 1.8 |
| K1.3 | 기술 명사는 짧고 분명한 것으로 고르세요. | STE 1.9 |
| K1.4 | 확인, 검증, 점검, 체크, 검사는 "확인하다" 하나로 쓰세요. "입력값 검증"처럼 정해진 기술 용어는 예외입니다. | STE 1.11, 9.4 |
| K1.5 | 기술 명사를 동사처럼 쓰지 마세요("웹훅하다"). | STE 1.7 |
| K1.6 | 번역한 기술 용어는 처음 한 번 원어를 괄호에 함께 쓰세요. 그다음에는 한국어만 쓰세요. | KS A 0001 부속서 H |

고치기 전: <!-- simple-korean: off -->"이벤트를 웹훅하고 배포를 진행하세요."<!-- simple-korean: on -->
고친 뒤: 이벤트를 웹훅으로 보내세요. 그다음 서비스를 배포하세요.

### K2: 명사 나열

| 규칙 | 지시 | 출처 |
|---|---|---|
| K2.1 | 명사는 3개까지만 이으세요. | STE 2.1 |
| K2.2 | 명사가 3개를 넘으면 조사나 동사로 푸세요. 긴 기술 이름은 한 번 다 쓰고 줄임말을 정하세요. | STE 2.2 |

고치기 전: <!-- simple-korean: off -->"연결 풀 타임아웃 설정 값 변경"<!-- simple-korean: on -->
고친 뒤: 연결 풀의 타임아웃 값을 바꿉니다.

### K3: 서술어

| 규칙 | 지시 | 출처 |
|---|---|---|
| K3.1 | 단순 현재와 단순 과거로 쓰세요. | STE 3.2, 3.4 |
| K3.2 | 진행이 아니면 "-고 있습니다"를 쓰지 마세요("지원하고 있습니다"는 "지원합니다"로). | STE 3.4, 이근희 2008 |
| K3.3 | 이중 피동("-되어지다", "보여지다", "쓰여지다")을 쓰지 마세요. | Kubernetes 한글화 가이드, 이근희 2008 |
| K3.4 | 능동으로 쓰세요. "~에 의해 ~되다"는 행위자를 주어로 바꾸세요. 행위자를 모르면 피동을 써도 됩니다. | STE 3.6 |
| K3.5 | "-함으로써", "-하여"로 결과를 덧붙이지 말고 새 문장으로 쓰세요. | STE 3.5 |
| K3.6 | 양태는 "-ㄹ 수 있습니다", 현재형, "-해야 합니다"만 쓰세요. 이 파일 끝의 양태 사다리로 고치세요. | STE 3.x 조동사 |
| K3.7 | 동작은 동사로 쓰세요. "진행하다", "수행하다", "실시하다"를 명사에 붙이지 마세요("압축을 수행합니다"는 "압축합니다"로). | STE 3.7, Microsoft 한국어 스타일 가이드 |

### K4: 문장

| 규칙 | 지시 | 출처 |
|---|---|---|
| K4.1 | 짧고 분명한 문장을 쓰세요. | STE 4.1 |
| K4.2 | 문장을 줄이려고 조사나 어미를 빼지 마세요. 본문 문장을 "-함", "-음", "-임", "-필요"로 끝내지 마세요. "겁니다", "근데" 같은 구어 축약을 쓰지 마세요. | STE 4.2 |
| K4.3 | 복잡한 내용은 세로 목록으로 쓰세요. 앞 문장은 쌍점으로 끝내세요. 항목 형식을 맞추고, 지시와 사실을 섞지 말고, 목록을 겹치지 마세요. | STE 4.3 |
| K4.4 | 관련된 문장은 "그다음", "그래서", "그러면" 같은 접속어로 이으세요. | STE 4.4 |
| K4.5 | 한 문서에는 문체 하나만 쓰세요. 새 문서는 서술에 "-습니다", 지시에 "-하세요"를 쓰세요. 기존 문서는 그 문서의 문체를 따르세요. | 이 프로젝트, 최지영·최명원 2008 |

고치기 전: <!-- simple-korean: off -->"실행 전 백업 존재 확인 필요."<!-- simple-korean: on -->
고친 뒤: 마이그레이션을 실행하기 전에 백업이 있는지 확인하세요.

### K5: 절차문

| 규칙 | 지시 | 출처 |
|---|---|---|
| K5.1 | 절차문 한 문장은 15어절 이하로 쓰세요. 경고와 주의도 같습니다. | STE 5.1 |
| K5.2 | 한 문장에는 동작 하나만 쓰세요. 두 동작이 동시에 일어날 때만 예외입니다. 단계에는 바로 나오는 결과나 제약을 한 문장 더할 수 있습니다. | STE 5.2 |
| K5.3 | 지시는 "-하세요"로 쓰세요. | STE 5.3, 최지영·최명원 2008 |
| K5.4 | 조건은 "-면"으로 명령 앞에 두세요. "만약"을 붙이지 말고, 명령 뒤에 "단, ~경우"를 덧붙이지 마세요. | STE 5.4 |
| K5.5 | 참고에는 정보만 쓰세요. 지시나 제약은 그 동작과 함께 쓰세요. 참고를 모두 지워도 절차는 그대로 되어야 합니다. | STE 5.5 |

고치기 전: <!-- simple-korean: off -->"API 키는 클라이언트를 설정하기 전에 대시보드의 설정 메뉴에서 가져오셔야 할 것 같습니다."<!-- simple-korean: on -->
고친 뒤: 대시보드의 설정 메뉴에서 API 키를 가져오세요. 그다음 이 키로 클라이언트를 설정하세요.

### K6: 설명문

| 규칙 | 지시 | 출처 |
|---|---|---|
| K6.1 | 한 문장에는 명제 하나만 쓰세요. | STE 6.1, 유수린·정동규 2009 |
| K6.2 | 핵심어로 글의 구조를 보이세요. | STE 6.2 |
| K6.3 | 설명문 한 문장은 20어절 이하로 쓰세요. | STE 6.3 |
| K6.4 | 관련된 내용을 문단으로 묶으세요. | STE 6.4 |
| K6.5 | 한 문단에는 주제 하나만 두세요. | STE 6.5 |
| K6.6 | 한 문단에는 문장을 6개까지만 쓰세요. | STE 6.6 |

15어절과 20어절은 한국어 실증 연구에서 나온 수가 아닙니다. 이 프로젝트가 정한 값입니다(`docs/research/korean-controlled-language.md`).

### K7: 안전 지시

| 규칙 | 지시 | 출처 |
|---|---|---|
| K7.1 | 위험 수준을 나타내는 말을 쓰세요. "경고:"는 사람이 다칠 위험이고 "주의:"는 데이터나 장비가 손상될 위험입니다. 둘이 함께 있으면 "경고:"를 쓰세요. | STE 7.1 |
| K7.2 | 분명한 명령이나 조건으로 시작하세요. | STE 7.2 |
| K7.3 | 그다음에 위험이나 결과를 쓰세요. | STE 7.3 |

명령 다음에 설명을 쓰세요. 되돌릴 수 없는 CLI 플래그와 마이그레이션에도 같은 형식을 쓰세요.

고치기 전: <!-- simple-korean: off -->"운영 환경에서 파괴적 플래그가 켜진 채로 실행될 경우 일부 상황에서 데이터 손실이 발생할 수도 있다는 점에 유의하시기 바랍니다."<!-- simple-korean: on -->
고친 뒤: 주의: 운영 DB에 `--force` 플래그를 쓰지 마세요. 이 플래그는 원본에 없는 행을 지웁니다.

### K8: 문장 부호와 어절 수

| 규칙 | 지시 | 출처 |
|---|---|---|
| K8.1 | 세미콜론을 쓰지 마세요. 두 문장으로 쓰세요. | STE 8.1 |
| K8.2 | em-dash를 쓰지 마세요. 관계를 말로 밝히거나 두 문장으로 쓰세요. 띄어 쓴 하이픈이나 겹하이픈으로 문장을 잇는 것도 같습니다. 범위(5–10), 목록 기호, 플래그(`--force`)는 해당하지 않습니다. | 이 프로젝트 |
| K8.3 | 괄호는 참조, 줄임말, 설명, 원어 병기에 쓰세요. | STE 8.3 |
| K8.4 | 세로 목록 앞 문장은 쌍점에서 끝납니다. 항목은 각각 한 문장으로 셉니다. | STE 8.4 |
| K8.5 | 어절은 공백으로 나눈 단위입니다. 인라인 코드, URL, 숫자와 단위, 괄호 안의 글, 인용한 글은 한 어절로 셉니다. | STE 8.5~8.7 |

### K9: 작성 관행

| 규칙 | 지시 | 출처 |
|---|---|---|
| K9.1 | 단어를 바꿔 넣어도 어색하면 문장을 다시 짜세요. | STE 9.1 |
| K9.2 | 한 문서에서는 문체와 용어를 끝까지 같게 쓰세요. | STE 9.4 |
| K9.3 | "이것", "그것", "해당"이 가리키는 대상을 분명히 하세요. 헷갈리면 이름을 다시 쓰세요. | STE GR-3 |
| K9.4 | "등등", "e.g.", "etc." 대신 항목을 다 쓰거나 "예를 들어"로 시작하세요. | STE GR-6 |
| K9.5 | 중요성 말고 사실을 쓰세요. 아래 AI 문체 신호를 피하세요. | 이 프로젝트 |

#### AI 문체 신호

AI가 쓴 한국어는 정해진 방향으로 흐릅니다. 문서와 답변 모두에서 다음을 피하세요:

- 부풀린 중요성: "중요한 역할을 합니다", "핵심적인"을 쓰지 말고 사실을 쓰세요.
- 부정 병렬: "단순히 X가 아니라 Y입니다"를 쓰지 마세요.
- 장식용 세 항목: "빠르고, 안정적이며, 확장 가능한" 같은 나열을 쓰지 마세요.
- 출처 없는 일반화: "연구에 따르면"을 쓰려면 출처를 밝히세요.
- 요약 반복: "결론적으로", "요약하면"으로 시작하는 문단을 쓰지 마세요.
- 말을 거는 맺음말: "도움이 되셨기를 바랍니다"를 쓰지 마세요.
- 서식 습관: 장식용 굵은 글씨와 굵은 글씨로 시작하는 문단을 쓰지 마세요. 구조 대신 쓴 이모지, 두 문장도 덮지 않는 제목도 쓰지 마세요.

사실을 담지 않은 말과 번역투는 `references/word-swaps.md`에서 바꿀 말을 찾으세요.

### K10: 표기

| 규칙 | 지시 | 출처 |
|---|---|---|
| K10.1 | 외래어는 외래어 표기법과 국립국어원 용례를 따르세요(디렉터리, 메시지, 애플리케이션). | 외래어 표기법, `docs/research/loanword-spelling-usage.md` |
| K10.2 | 단어 목록(`data/terms.json`)에 있는 단어는 목록의 형태를 쓰세요. 프로젝트 설정(`.simple-korean.json`)이 지정형을 바꿀 수 있습니다. | 같은 보고서 |
| K10.3 | 공식 표기가 없는 단어는 목록이 정한 형태를 쓰세요(리디렉션, 리팩터링). | 같은 보고서 |
| K10.4 | 전문 용어 합성어는 붙여 쓰세요(기본값, 매개변수, 반환값, 오픈소스). | 한글 맞춤법 제50항, KS A 0001 부속서 H |
| K10.5 | 제품 이름, 화면 문구 인용, API 객체 이름, 코드는 원래 표기 그대로 두세요. | 같은 보고서 |
| K10.6 | 한 문서에서 한 개념은 한 형태로만 쓰세요. | STE 1.11, 같은 보고서 |

단어 목록은 여섯 무리입니다. 린터의 강도는 기본 모드와 엄격 모드에서 다릅니다.

<!-- simple-korean: off -->
| 무리 | 지정형 ← 잡는 형태 | 기본 모드 | 엄격 모드 |
|---|---|---|---|
| ① 규범대로 쓰임 | 메시지←메세지, 애플리케이션←어플리케이션, 콘텐츠←컨텐츠, 아키텍처←아키텍쳐, 스레드←쓰레드, 메서드←메소드, 라이선스←라이센스, 액세스←엑세스, 스케줄←스케쥴, 비즈니스←비지니스, 세팅←셋팅, 매뉴얼←메뉴얼, 캐시←캐쉬, 대시보드←대쉬보드, 해시←해쉬, 포맷←포멧, 렌더링←랜더링, 트랜잭션←트랜젝션, 버전←버젼, 헤더←해더, 데이터←데이타, 컴포넌트←컴퍼넌트, 프레임워크←프레임웍 | 오류 | 오류 |
| ② 출처별로 갈림 | 디렉터리←디렉토리, 릴리스←릴리즈, 셸←쉘, 리디렉션←리다이렉션 | 경고 | 오류 |
| ③ 관용이 굳음 | 레포지토리←리포지토리·레포지터리·레포, 바디, 칼럼←컬럼, 대상←타겟 | 경고 | 오류. 리포지터리, 보디, 타깃은 지정형이 아니라고 경고 |
| ④ 공식 표기 없음 | 리디렉션←리다이렉트·리디렉트, 리팩터링←리팩토링 | 문서 안 혼용만 경고 | 경고 |
| ⑤ 외래어와 우리말 | 오류←에러, 매개변수←파라미터, 사용자←유저, 기본값←디폴트, 배포←디플로이 | 문서 안 혼용만 경고 | 경고 |
| ⑥ 띄어쓰기 | 기본값←기본 값, 매개변수←매개 변수, 반환값←반환 값, 오픈소스←오픈 소스 | 기본 값만 경고 | 기본 값은 오류, 나머지는 경고 |
<!-- simple-korean: on -->

### S: 엄격 모드

자세한 내용은 `references/strict-mode.md`에 있습니다.

| 규칙 | 지시 | 출처 |
|---|---|---|
| S1 | 문장 끝은 의무 "-해야 합니다", 금지 "-하면 안 됩니다", 허용 "-해도 됩니다", 능력 "-ㄹ 수 있습니다", 사실과 예정의 현재형과 과거형만 쓰세요. | KS A 0001 부속서 I |
| S2 | 권고형과 미래 추측형을 쓰지 마세요. "반드시"는 외부 규정에만 쓰세요. | KS A 0001 부속서 I |
| S3 | "(이)나" 대신 "와/과", "및", "또는"을 쓰세요. "이상·이하"와 "초과·미만"을 구별하세요. | KS A 0001 부속서 H |
| S4 | 조건은 "-면"으로만 쓰세요. "-ㄹ 경우"를 쓰지 말고, "-ㄹ 때"는 시점에만 쓰세요. | 임병화·남유선 2009 |
| S5 | 단어 목록을 엄격 모드 강도로 지키세요. 지정형이 아닌 형태를 쓰지 마세요. | `docs/research/loanword-spelling-usage.md` |
| S6 | 번역한 기술 용어의 원어 병기는 필수입니다. | KS A 0001 부속서 H |

### 양태 사다리

| 쓴 표현 | 고칠 표현 |
|---|---|
| "-해야 할 것 같습니다", 필수인데 쓴 "-하는 것이 좋습니다" | "-해야 합니다" |
| 권고하는 "-하는 것이 좋습니다" | 지우거나 사실로 쓰세요: "X가 Y보다 빠릅니다." |
| "-ㄹ 수도 있습니다", "-ㄹ 것 같습니다", "-로 보입니다" | "-ㄹ 수 있습니다", 또는 근거와 함께 사실로 |
| "-ㄹ 것입니다" | 현재형: "다음 버전에서 제거됩니다." |
| "-하시기 바랍니다" | "-하세요" |
| "아마" | 지우거나 근거를 쓰세요 |

규칙 번호를 인용할 때는 이 파일의 번호만 쓰세요.
````

- [ ] **Step 3: 엄격 모드 규칙을 쓴다**

`skills/simple-korean/references/strict-mode.md`:

````markdown
# 엄격 모드: 문장 끝, 접속어, 단어

사용자가 엄격 모드, 통제 언어, KS A 0001, STE, ASD-STE100을 말하면 이 파일을 읽으세요. 엄격 모드는 문서에 규칙을 더합니다. 채팅 답변은 바꾸지 않습니다. 답변은 기본 모드 규칙을 따릅니다.

ASD-STE100에는 승인 단어 약 900개와 비승인 단어 약 1,200개를 담은 사전이 있습니다. 한국어에는 이런 사전이 없습니다. 국가 표준, 표준화 기구, 업계, 학계 어디에도 닫힌 승인어 목록은 없습니다(`docs/research/korean-controlled-language.md`). 한국어는 의무, 권고, 허용 같은 뜻을 명사가 아니라 문장 끝 어미에 싣습니다. 그래서 엄격 모드는 닫힌 목록을 단어 대신 문장 끝과 접속어에 둡니다.

근거는 KS A 0001:2023 「표준의 서식과 작성방법」의 부속서 I와 부속서 H입니다. 이 파일은 그 요지를 이 프로젝트의 말로 다시 썼습니다. 원문은 e-나라표준인증(standard.go.kr)에서 볼 수 있습니다.

엄격 모드를 켤 때 한 번만 이렇게 알리세요. "한국어 통제 언어 국가 표준은 없으며, 이 기준은 KS A 0001과 공개 연구를 바탕으로 한 비공식 기준입니다."

## 문장 끝

| 뜻 | 쓰는 문장 끝 | 예 |
|---|---|---|
| 의무 | "-해야 합니다" | "백업 파일은 다른 리전에 저장해야 합니다." |
| 금지 | "-하면 안 됩니다" | "운영 DB에서 이 명령을 실행하면 안 됩니다." |
| 허용 | "-해도 됩니다" | "이 단계는 건너뛰어도 됩니다." |
| 불필요 | "-하지 않아도 됩니다" | "캐시를 비우지 않아도 됩니다." |
| 능력과 가능성 | "-ㄹ 수 있습니다" | "이 API는 요청을 100개까지 처리할 수 있습니다." |
| 사실과 예정 | 현재형과 과거형 | "v3에서 이 플래그를 제거합니다." |

- 권고형("-하는 것이 좋습니다", "-하여야 할 것입니다")을 쓰지 마세요. 필수이면 의무로 쓰고, 선택이면 지우거나 사실로 쓰세요.
- "-ㄹ 것입니다"를 쓰지 마세요. 표준 문서를 읽는 독자는 이 말을 권고로 읽습니다. 예정은 현재형으로 쓰세요.
- 허용의 뜻으로 "-ㄹ 수 있습니다"를 쓰지 마세요. 허용은 "-해도 됩니다"로 쓰세요.
- "반드시"는 법이나 규정처럼 밖에서 오는 제약에만 쓰세요.
- 지시는 "-하세요" 하나로 쓰세요. 기존 문서가 다른 지시 어미를 쓰면 그 어미 하나로 맞추세요.

## 접속어와 조건

- "(이)나"로 항목을 잇지 마세요. 두 항목은 "와/과", 셋 이상은 "및", 선택은 "또는"으로 이으세요.
- "이상"과 "이하"는 기준값을 포함하고, "초과"와 "미만"은 포함하지 않습니다. 경계값이 있는 조건에는 이 말을 구별해 쓰세요.
- 조건은 "-면"으로만 쓰세요. "-ㄹ 경우"를 쓰지 마세요. "-ㄹ 때"는 시점을 말할 때만 쓰세요(임병화·남유선 2009).

## 단어

- 단어 목록(`data/terms.json`)을 엄격 모드 강도로 지키세요. 강도는 `references/rule-catalog.md`의 K10 표에 있습니다.
- 번역한 기술 용어는 처음 나올 때 원어를 괄호에 함께 쓰세요. 엄격 모드에서는 필수입니다.
- 정착한 기술 명사와 제품 기능 이름은 우리말로 바꾸지 마세요.

## 엄격 모드 자가 점검

`SKILL.md`의 자가 점검에 다음 세 단계를 더하세요:

1. 문장 끝을 모두 위 표와 대조하세요. "좋습니다", "것입니다", "반드시"를 찾아 고치세요.
2. "(이)나"로 이은 나열과 "-ㄹ 경우"를 찾아 고치세요.
3. 린터를 쓸 수 있으면 `python3 evals/ko_lint.py --strict 파일.md`로 단어 목록 위반을 확인하세요.

## 근거

- KS A 0001:2023 부속서 I(문장 끝)와 부속서 H(접속어, 전문용어 표기)
- Hong과 Kim(2008)의 통제 한국어, 유수린 외(2008~2010)와 임병화·남유선(2009)의 기술 문서 규칙
- 단어 목록의 근거와 측정값: `docs/research/loanword-spelling-usage.md`, `data/terms.json`
````

- [ ] **Step 4: 바꿀 말 표를 쓴다**

`skills/simple-korean/references/word-swaps.md`:

````markdown
# 슬롭 어휘와 번역투를 쉬운 말로

이 표는 이 프로젝트가 만든 것입니다. 국립국어원 자료가 아닙니다. 사실을 담지 않은 말은 바꾸지 말고 지우세요.

## 슬롭 어휘

| 쓴 말 | 바꿀 말 |
|---|---|
| "원활한", "원활하게" | 지우세요. 필요하면 수치를 쓰세요 |
| "효율적인", "효과적인" | 무엇이 얼마나 나아졌는지 쓰세요 |
| "강력한" | 지우거나 측정할 수 있는 성질을 쓰세요 |
| "손쉽게", "간편하게", "매끄럽게", "자연스럽게" | 지우세요 |
| "혁신적인", "획기적인" | 새, 또는 지우세요 |
| "다양한" | 여러, 또는 항목을 쓰세요 |
| "핵심적인", "중요한 역할을 합니다" | 지우고 사실을 쓰세요 |
| "완벽한", "완벽하게", "매우", "정말" | 지우세요 |
| "본질적으로" | 지우세요 |
| "여정" | 지우세요 |
| "활용하다" | 쓰다 |
| "결론적으로", "요약하면", "정리하자면" | 지우세요 |
| "살펴보겠습니다", "알아보겠습니다" | 지우고 바로 내용을 쓰세요 |
| "나아가", "더 나아가", "아울러" | 또 |
| "뿐만 아니라" | 두 문장으로 쓰세요 |
| "단순히 X가 아니라 Y입니다" | "Y입니다" |

린터가 잡는 슬롭 어휘 전체는 `evals/slop.tsv`에 있습니다.

## 번역투

| 쓴 말 | 바꿀 말 | 예 |
|---|---|---|
| "~에 대해", "~에 대한" | "~을", "~의", 또는 문장을 다시 짜세요 | "설정에 대해 설명합니다"는 "설정을 설명합니다"로 |
| "~를 통해" | "~로", "~에서" | "API를 통해 요청합니다"는 "API로 요청합니다"로 |
| "~에 의해 ~되다" | 행위자를 주어로 | "스케줄러에 의해 실행됩니다"는 "스케줄러가 실행합니다"로 |
| "~에 있어(서)" | "~에서", "~할 때" | "배포에 있어서"는 "배포할 때"로 |
| "~를 가지고 있다" | "~가 있다" | "필드 세 개를 가지고 있습니다"는 "필드가 세 개 있습니다"로 |
| "~로 인해" | "~ 때문에", "~해서" | "타임아웃으로 인해 실패했습니다"는 "타임아웃 때문에 실패했습니다"로 |
| "~하는 것이 가능하다" | "~할 수 있다" | "내보내는 것이 가능합니다"는 "내보낼 수 있습니다"로 |
| "~이 요구된다" | "~이 필요합니다", "~해야 합니다" | "재시작이 요구됩니다"는 "다시 시작해야 합니다"로 |
| "~할 필요가 있다" | "~해야 합니다" | "갱신할 필요가 있습니다"는 "갱신해야 합니다"로 |
| "~에 위치한" | "~에 있는" | "루트에 위치한 파일"은 "루트에 있는 파일"로 |
| "만약 ~라면" | "~면" | "만약 실패한다면"은 "실패하면"으로 |
| "~하고 있습니다"(진행이 아닐 때) | "~합니다" | "세 형식을 지원하고 있습니다"는 "세 형식을 지원합니다"로 |
| "~되어지다", "보여지다" | "~되다", "보이다" | "변경되어졌습니다"는 "바뀌었습니다"로 |
| "~(으)로부터" | "~에서" | "서버로부터 응답을 받습니다"는 "서버에서 응답을 받습니다"로 |
| "~을 진행하다", "~을 수행하다" | 동사 하나로 | "배포를 진행합니다"는 "배포합니다"로 |

## 양태

양태 표현은 `references/rule-catalog.md`의 양태 사다리로 고치세요.
````

- [ ] **Step 5: 문서 유형별 쓰는 법을 쓴다**

`skills/simple-korean/references/use-cases.md`:

````markdown
# 문서 유형별 쓰는 법

STE는 항공기 정비 매뉴얼을 위해 만들었습니다. 잘못 읽으면 비용이 드는 글에는 같은 성질이 그대로 통합니다. 한 단어 한 뜻, 짧은 문장, 조건을 앞에 둔 명령입니다. 아래 항목마다 모드와 바꿀 점을 적었습니다.

## 오류 메시지와 CLI 출력

모드는 절차문입니다. 오류 메시지는 장애 한가운데 있는 독자에게 주는 지시입니다.

형식: 일어난 일을 과거형으로 쓰고, 원인을 알면 원인을 쓰고, 고치는 명령이나 조건을 쓰세요.

<!-- simple-korean: off -->
> 고치기 전: 이런! 연결을 설정하는 도중 문제가 발생했습니다. 자격 증명이 올바르게 구성되었는지 확인하시고 다시 시도해 주시기 바랍니다.
<!-- simple-korean: on -->

> 고친 뒤: 데이터베이스에 연결하지 못했습니다. 사용자 `app`의 비밀번호가 틀렸습니다. `DB_PASSWORD`를 설정하고 다시 연결하세요.

## 런북과 표준 작업 절차서

모드는 절차문입니다. 당직용 런북은 STE가 처음부터 겨냥한 정비 매뉴얼과 같은 글입니다.

- 단계는 모두 "-하세요"로 쓰고, 한 단계에 지시 하나를 쓰고, 조건은 앞에 두세요.
- 경고는 그 단계 앞에 두세요. 명령을 먼저, 위험을 다음에 쓰세요.
- 15어절을 넘는 문장을 쓰지 마세요.

## 장애 보고서와 포스트모템

모드는 설명문이고, 과거형만 씁니다. "확인하고 있습니다" 같은 진행형 시간표는 언제 일어난 일인지 숨깁니다.

<!-- simple-korean: off -->
> 고치기 전: 일부 사용자의 서비스 이용에 영향을 미쳤을 수도 있는 이슈를 확인하였습니다.
<!-- simple-korean: on -->

> 고친 뒤: 14:02부터 14:31(UTC)까지 요청의 12%가 실패했습니다. 14:00 배포에서 캐시 예열 단계가 빠졌습니다.

"영향을 미쳤을 수도" 같은 짐작은 쓰지 마세요. 아는 것을 쓰고, 모르는 것은 "알 수 없음"이라고 쓰세요.

## 커밋 메시지와 PR 설명

제목은 짧은 명사구나 명령형으로 쓰세요(예: "로그인 오류 수정"). 본문은 설명문으로 쓰고, 바꿀 말 표와 20어절 상한을 적용하세요. "이 PR은 ~하고자 합니다"를 지우세요.

## API 변경 기록과 릴리스 노트

모드는 설명문입니다. 항목 하나에 변경 하나를 쓰고, 가능하면 한 문장으로 쓰세요. 호환성이 깨지는 변경은 경고 형식을 따르고 명령을 먼저 쓰세요. "`v2/users` 호출을 고치세요. `name` 필드가 `first_name`과 `last_name`으로 나뉘었습니다."

## AI 에이전트용 지침(프롬프트, AGENTS.md, 스킬)

모드는 절차문입니다. 시스템 프롬프트는 질문할 수 없는 독자를 위한 절차서입니다.

- 한 문장에 지시 하나를 쓰세요. 그러면 규칙마다 인용할 수 있고, 모델이 반쯤만 지키기 어렵습니다.
- 한 단어에 한 뜻만 주세요. 그러면 모델이 "확인", "검증", "점검"을 서로 다른 작업으로 읽지 않습니다.
- 조건을 앞에 두세요("빌드가 실패하면 멈추세요"). 뒤에 붙은 조건은 모델이 놓칩니다.
- "-하는 것이 좋습니다"를 쓰지 마세요. 모델은 이 말을 선택 사항으로 읽습니다. "-해야 합니다"로 쓰거나 규칙을 지우세요.

## 고객 응대 문구와 상태 페이지

모드는 설명문이고, 한 문장은 20어절 이하입니다. 사과하는 문장만 쓰지 말고 무슨 일이 있었는지 쓰세요.

<!-- simple-korean: off -->
> 고치기 전: 이용에 불편을 드려 진심으로 사과드리며, 보다 나은 서비스를 위해 최선을 다하겠습니다.
<!-- simple-korean: on -->

> 고친 뒤: API가 18분 동안 멈췄습니다. 그동안 올린 파일은 저장되었고 오늘 처리됩니다. 불편을 드려 죄송합니다.

## 번역과 현지화 준비

엄격 모드를 쓰세요. 한 단어 한 뜻과 다 갖춘 문법(조사, 어미)은 기계 번역기가 짐작해야 할 모호함을 줄입니다. 한국어 문서를 기계 번역할 팀은 엄격 모드로 쓰세요.

## UI 문구와 빈 화면

모드는 절차문이고, 길이 제한이 엄격합니다. 버튼과 레이블은 이름이라 규칙에서 뺍니다. 본문 문구는 규칙을 따르세요. 문체는 제품의 문체를 따르세요(예: 해요체 제품은 "-해요"). "프로젝트가 아직 없어요. 프로젝트를 만들어 시작하세요."

## STE가 맞지 않는 글

마케팅 페이지, 출시 글, 블로그 글, 브랜드 글에는 STE 규칙을 쓰지 마세요. STE는 설득하는 문장을 지웁니다. 그런 글은 자기 목소리로 쓰고, 그 글이 링크하는 문서에 STE 규칙을 쓰세요.
````

- [ ] **Step 6: 린트 관문을 확인한다**

Run: `python3 evals/ko_lint.py --gate=warning skills/simple-korean/SKILL.md skills/simple-korean/references/*.md prompts/system-prompt.md output-styles/simple-korean.md > /tmp/sk-gate.json; echo "exit=$?"`
Expected: `exit=0`. 실패하면 `/tmp/sk-gate.json`의 `hits`를 읽고 문장을 고친다. 금지 표현을 언급하는 자리는 큰따옴표로 감싸고, 일부러 틀린 예시는 꺼짐 표시 사이에 둔다.

- [ ] **Step 7: 커밋한다**

```bash
git add skills/simple-korean/references
git commit -m "docs: add rule catalog, strict mode, word swaps, and use cases" -m $'Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01SanRSLxxVtkLMJh1wLGeGZ'
```

---

## 단계 C: 훅과 배포

### Task 10: 세션 시작 훅

**Files:**
- Create: `src/hooks/package.json`, `src/hooks/simple-korean-activate.js`
- Test: `src/hooks/simple-korean-activate.test.js`

**Interfaces:**
- Consumes: Task 8의 `prompts/system-prompt.md`(두 `---` 줄 사이의 규칙 블록)
- Produces: `node src/hooks/simple-korean-activate.js`가 표준 출력으로 내보내는 문맥. 첫 줄은 `SIMPLE KOREAN 스킬이 자동으로 켜졌습니다`다. 모듈 내보내기: `FALLBACK_CONTEXT`, `MAX_CHARS`(9500), `buildContext(promptText, skill = '')`, `promptCandidates(pluginRoot, hookDirectory)`, `readFirstFile(list)`, `ruleBlock(content)`, `skillPath(pluginRoot, hookDirectory) -> string`(찾은 SKILL.md의 절대 경로, 없으면 빈 문자열), `stripFrontmatter(content)`. 환경변수 `CLAUDE_PLUGIN_ROOT`(Claude Code)와 `PLUGIN_ROOT`(Codex)를 읽는다. 문맥의 셋째 줄은 SKILL.md와 `references/rule-catalog.md`의 절대 경로를 알린다. 모델은 플러그인이 설치된 위치를 모르기 때문이다(Task 16 압력 시험 2가 이 줄에 기댄다).

- [ ] **Step 1: 실패하는 테스트를 쓴다**

`src/hooks/simple-korean-activate.test.js`:

```javascript
const assert = require('node:assert/strict');
const { spawnSync } = require('node:child_process');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const test = require('node:test');

const {
  FALLBACK_CONTEXT,
  MAX_CHARS,
  buildContext,
  promptCandidates,
  readFirstFile,
  skillPath,
  stripFrontmatter,
} = require('./simple-korean-activate');

const SCRIPT = path.join(__dirname, 'simple-korean-activate.js');
const REPO_PROMPT = path.join(__dirname, '..', '..', 'prompts', 'system-prompt.md');

function tmpRoot(promptText) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'sk-hook-'));
  fs.mkdirSync(path.join(root, 'prompts'));
  if (promptText !== undefined) {
    fs.writeFileSync(path.join(root, 'prompts', 'system-prompt.md'), promptText);
  }
  return root;
}

function runHook(env) {
  return spawnSync(process.execPath, [SCRIPT], { env: { ...process.env, PLUGIN_ROOT: '', CLAUDE_PLUGIN_ROOT: '', ...env }, encoding: 'utf8' });
}

test('플러그인 루트의 프롬프트를 먼저 읽는다', () => {
  assert.equal(promptCandidates('/plugin', '/plugin/src/hooks')[0], '/plugin/prompts/system-prompt.md');
});

test('플러그인 루트가 없으면 레포 구조로 찾는다', () => {
  assert.equal(promptCandidates(undefined, '/repo/src/hooks')[0], '/repo/prompts/system-prompt.md');
});

test('읽을 수 없는 후보는 건너뛰고 다음 후보를 읽는다', (t) => {
  if (process.getuid && process.getuid() === 0) {
    t.skip('root는 권한 000 파일도 읽는다');
    return;
  }
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'sk-read-'));
  const locked = path.join(dir, 'locked.md');
  const open = path.join(dir, 'open.md');
  fs.writeFileSync(locked, 'SECRET');
  fs.chmodSync(locked, 0o000);
  fs.writeFileSync(open, 'OPEN');
  assert.equal(readFirstFile([locked, open]), 'OPEN');
  fs.chmodSync(locked, 0o644);
});

test('디렉터리 후보는 건너뛴다', () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'sk-dir-'));
  const asDir = path.join(dir, 'system-prompt.md');
  fs.mkdirSync(asDir);
  const file = path.join(dir, 'real.md');
  fs.writeFileSync(file, 'REAL');
  assert.equal(readFirstFile([asDir, file]), 'REAL');
});

test('모든 후보가 실패하면 빈 문자열이다', () => {
  assert.equal(readFirstFile(['/nonexistent/a.md', '/nonexistent/b.md']), '');
});

test('LF와 CRLF frontmatter를 지운다', () => {
  assert.equal(stripFrontmatter('---\nname: x\n---\nBody'), 'Body');
  assert.equal(stripFrontmatter('---\r\nname: x\r\n---\r\nBody'), 'Body');
});

test('프롬프트가 없으면 대체 규칙을 보낸다', () => {
  assert.equal(buildContext(''), FALLBACK_CONTEXT);
});

test('레포의 프롬프트는 상한 안에 들고 규칙 블록만 나간다', () => {
  const out = buildContext(fs.readFileSync(REPO_PROMPT, 'utf8'));
  assert.ok(out.length <= MAX_CHARS, `${out.length} > ${MAX_CHARS}`);
  assert.ok(out.startsWith('SIMPLE KOREAN 스킬이 자동으로 켜졌습니다'));
  assert.ok(out.includes('답변(모든 모드의 채팅 답변)'));
  assert.ok(out.includes('레포지토리'));
  assert.ok(!out.includes('# 시스템 프롬프트'), '페이지 제목이 섞였다');
  assert.ok(!out.includes('짧은 판본'), '짧은 판본이 섞였다');
  assert.ok(!out.includes('붙여 넣으세요'), '안내 문단이 섞였다');
});

function withSkill(root) {
  fs.mkdirSync(path.join(root, 'skills', 'simple-korean'), { recursive: true });
  fs.writeFileSync(path.join(root, 'skills', 'simple-korean', 'SKILL.md'), 'S');
  return root;
}

test('찾은 SKILL.md와 규칙 목록의 절대 경로를 알린다', () => {
  const out = buildContext(fs.readFileSync(REPO_PROMPT, 'utf8'), '/plugin/skills/simple-korean/SKILL.md');
  assert.ok(out.includes('적용한 규칙의 번호를 적어야 하면 먼저 이 파일을 읽으세요: /plugin/skills/simple-korean/SKILL.md.'));
  assert.ok(out.includes('/plugin/skills/simple-korean/references/rule-catalog.md에 있는 번호만 쓰세요'));
});

test('SKILL.md를 찾지 못하면 상대 경로로 알린다', () => {
  const out = buildContext(fs.readFileSync(REPO_PROMPT, 'utf8'));
  assert.ok(out.includes('먼저 이 플러그인의 skills/simple-korean/SKILL.md를 읽으세요.'));
});

test('플러그인 루트의 SKILL.md를 먼저 찾고, 없으면 빈 문자열이다', () => {
  const root = withSkill(tmpRoot('P'));
  assert.equal(skillPath(root, '/nowhere/src/hooks'), path.join(root, 'skills', 'simple-korean', 'SKILL.md'));
  assert.equal(skillPath(undefined, '/nowhere/src/hooks'), '');
});

test('긴 설치 경로에서도 상한 안에 든다', () => {
  const long = `/${'a'.repeat(200)}/skills/simple-korean/SKILL.md`;
  const out = buildContext(fs.readFileSync(REPO_PROMPT, 'utf8'), long);
  assert.ok(out.length <= MAX_CHARS, `${out.length} > ${MAX_CHARS}`);
  assert.ok(out.includes(long));
});

test('상한을 넘는 프롬프트는 중간에 자르지 않고 대체 규칙으로 바꾼다', () => {
  assert.equal(buildContext('x'.repeat(MAX_CHARS + 1)), FALLBACK_CONTEXT);
});

test('main()은 CLAUDE_PLUGIN_ROOT의 프롬프트를 읽는다', () => {
  const r = runHook({ CLAUDE_PLUGIN_ROOT: tmpRoot('CLAUDE-COPY') });
  assert.equal(r.status, 0);
  assert.ok(r.stdout.includes('CLAUDE-COPY'));
});

test('main()은 플러그인 루트의 SKILL.md 절대 경로를 알린다', () => {
  const root = withSkill(tmpRoot('BODY'));
  const r = runHook({ CLAUDE_PLUGIN_ROOT: root });
  assert.equal(r.status, 0);
  assert.ok(r.stdout.includes(path.join(root, 'skills', 'simple-korean', 'SKILL.md')));
});

test('main()은 PLUGIN_ROOT(Codex)의 프롬프트를 읽는다', () => {
  const r = runHook({ PLUGIN_ROOT: tmpRoot('CODEX-COPY') });
  assert.equal(r.status, 0);
  assert.ok(r.stdout.includes('CODEX-COPY'));
});

test('main()은 후보가 하나도 없으면 대체 규칙을 내고 0으로 끝난다', () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'sk-main-'));
  const script = path.join(dir, 'a', 'b', 'hook.js');
  fs.mkdirSync(path.dirname(script), { recursive: true });
  fs.copyFileSync(SCRIPT, script);
  const root = tmpRoot(undefined);
  const r = spawnSync(process.execPath, [script], { env: { ...process.env, PLUGIN_ROOT: '', CLAUDE_PLUGIN_ROOT: root }, encoding: 'utf8' });
  assert.equal(r.status, 0);
  assert.equal(r.stdout, FALLBACK_CONTEXT);
});
```

- [ ] **Step 2: 테스트를 돌려 실패를 확인한다**

Run: `node --test src/hooks/simple-korean-activate.test.js`
Expected: `Cannot find module './simple-korean-activate'`로 실패한다.

- [ ] **Step 3: 구현을 쓴다**

`src/hooks/package.json`:

```json
{
  "type": "commonjs"
}
```

`src/hooks/simple-korean-activate.js`:

```javascript
#!/usr/bin/env node

const fs = require('node:fs');
const path = require('node:path');

// Claude Code는 훅 표준 출력을 10,000자까지만 받는다. 넘으면 파일로 빠지고 미리 보기만 전달된다.
const MAX_CHARS = 9500;

const FALLBACK_CONTEXT = `SIMPLE KOREAN 스킬이 자동으로 켜졌습니다

기술 문서를 쓸 때 쉬운 한국어 규칙을 따르세요. 문장을 짧게 쓰고, 조건을 명령 앞에 두고, 한 단어에 한 뜻만 주세요. 코드, 식별자, 명령, 인용한 오류 문구는 바꾸지 마세요.`;

// 모델은 플러그인이 어디에 설치됐는지 모른다. 찾은 SKILL.md의 절대 경로를 알려 줘야 그 파일과
// 규칙 목록을 읽는다. 찾지 못하면 상대 경로로 알린다.
function header(skillPath) {
  const where = skillPath
    ? `먼저 이 파일을 읽으세요: ${skillPath}. 규칙 번호는 ${path.join(path.dirname(skillPath), 'references', 'rule-catalog.md')}에 있는 번호만 쓰세요.`
    : '먼저 이 플러그인의 skills/simple-korean/SKILL.md를 읽으세요. 규칙 번호는 그 옆의 references/rule-catalog.md에 있는 번호만 쓰세요.';
  return [
    'SIMPLE KOREAN 스킬이 자동으로 켜졌습니다',
    '',
    `사용자가 스킬 이름을 말하지 않아도 아래 글쓰기 규칙을 따르세요. 엄격 모드나 점검을 요청받거나 적용한 규칙의 번호를 적어야 하면 ${where}`,
    '',
  ].join('\n');
}

function candidates(pluginRoot, hookDirectory, relative) {
  const roots = [];
  if (pluginRoot) {
    roots.push(pluginRoot);
  }
  roots.push(path.join(hookDirectory, '..', '..'), path.join(hookDirectory, '..'));
  return roots.map((root) => path.join(root, ...relative));
}

function promptCandidates(pluginRoot, hookDirectory) {
  return candidates(pluginRoot, hookDirectory, ['prompts', 'system-prompt.md']);
}

function skillPath(pluginRoot, hookDirectory) {
  const found = candidates(pluginRoot, hookDirectory, ['skills', 'simple-korean', 'SKILL.md'])
    .find((candidate) => fs.existsSync(candidate));
  return found ? path.resolve(found) : '';
}

function readFirstFile(list) {
  for (const candidate of list) {
    try {
      return fs.readFileSync(candidate, 'utf8');
    } catch (error) {
      // 없거나, 읽을 수 없거나, 디렉터리다. 다음 후보를 읽는다.
    }
  }
  return '';
}

function stripFrontmatter(content) {
  return content.replace(/^---\r?\n[\s\S]*?\r?\n---\r?\n?/, '');
}

// prompts/system-prompt.md는 사람이 읽는 페이지다. 제목, 붙여 넣는 곳을 알리는 문단, 두 "---" 줄
// 사이의 규칙 블록, 짧은 판본으로 이루어진다. 모델에는 규칙 블록만 보낸다.
function ruleBlock(content) {
  const fence = /^---[ \t]*\r?$/m;
  const first = content.search(fence);
  if (first === -1) {
    return content;
  }
  const rest = content.slice(first).replace(fence, '');
  const second = rest.search(fence);
  return second === -1 ? rest : rest.slice(0, second);
}

function buildContext(promptText, skill = '') {
  if (!promptText) {
    return FALLBACK_CONTEXT;
  }
  const out = header(skill) + ruleBlock(stripFrontmatter(promptText)).trim();
  if (out.length > MAX_CHARS) {
    process.stderr.write(`simple-korean 훅: 규칙이 ${out.length}자로 상한 ${MAX_CHARS}자를 넘어 짧은 대체 규칙을 보냅니다\n`);
    return FALLBACK_CONTEXT;
  }
  return out;
}

function main() {
  const pluginRoot = process.env.PLUGIN_ROOT || process.env.CLAUDE_PLUGIN_ROOT;
  const prompt = readFirstFile(promptCandidates(pluginRoot, __dirname));
  process.stdout.write(buildContext(prompt, skillPath(pluginRoot, __dirname)));
}

if (require.main === module) {
  main();
}

module.exports = {
  FALLBACK_CONTEXT,
  MAX_CHARS,
  buildContext,
  promptCandidates,
  readFirstFile,
  ruleBlock,
  skillPath,
  stripFrontmatter,
};
```

- [ ] **Step 4: 테스트를 돌려 통과를 확인한다**

Run: `chmod +x src/hooks/simple-korean-activate.js && node --test src/hooks/simple-korean-activate.test.js && node src/hooks/simple-korean-activate.js | wc -m`
Expected: `pass 17`, `fail 0`, 그리고 출력 글자 수 약 2,320(9,500 이하, 설치 경로 길이에 따라 달라진다).

- [ ] **Step 5: 커밋한다**

```bash
git add src/hooks/package.json src/hooks/simple-korean-activate.js src/hooks/simple-korean-activate.test.js
git commit -m "feat: inject the rule block at session start" -m $'Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01SanRSLxxVtkLMJh1wLGeGZ'
```

### Task 11: 파일 점검과 답변 점검 훅

**Files:**
- Create: `src/hooks/lint_hook.py`
- Test: `src/hooks/test_lint_hook.py`

**Interfaces:**
- Consumes: Task 6의 `ko_lint.lint_detail(text, "descriptive", path=..., config=...)`, `ko_lint.reader_check`, `ko_lint.LABELS`, `ko_lint.SEVERITY_LABELS`, `ko_lint.ko_text.hangul_ratio`, `ko_lint.ko_text.mask`, `ko_lint.ko_text.nfc`, `ko_lint.ko_rules.SLOP_RX`
- Produces: `python3 src/hooks/lint_hook.py`가 표준 입력의 훅 이벤트 JSON을 읽는다. PostToolUse에서 위반이 있으면 종료 코드 2와 stderr 메시지를 낸다(첫 줄 `simple-korean: <파일명>에 오류 N건, 경고 M건이 있습니다.`, 줄마다 `  <줄>번 줄, <범주>(<강도>): <문구>`). Stop에서는 문제가 있을 때 표준 출력에 `{"systemMessage": "simple-korean 답변 점검: ... 서술형으로 답하세요."}`를 쓰고 항상 0으로 끝난다. 상수 `MAX_HOOK_HITS = 12`, `MIN_HANGUL_RATIO = 0.3`, 환경변수 `SIMPLE_KOREAN_LINT_EXCLUDE`, `CLAUDE_CONFIG_DIR`.

- [ ] **Step 1: 실패하는 테스트를 쓴다**

`src/hooks/test_lint_hook.py`:

```python
import json
import os
import pathlib
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
HOOK = HERE / "lint_hook.py"
CLEAN = {"CLAUDE_CONFIG_DIR": "/nonexistent/claude-config", "SIMPLE_KOREAN_LINT_EXCLUDE": ""}
SLOP = "강력한 도구를 활용해 원활하게 처리할 수도 있습니다 — 매우 쉽게 처리합니다.\n"


def run(event, env=None):
    r = subprocess.run([sys.executable, str(HOOK)], input=json.dumps(event), capture_output=True, text=True,
                       env={**os.environ, **CLEAN, **(env or {})})
    return r.returncode, r.stdout, r.stderr


def write_slop(directory, name="notes.md"):
    path = pathlib.Path(directory, name)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(SLOP, encoding="utf-8")
    return str(path)


def post(path, **event):
    return {"hook_event_name": "PostToolUse", "tool_name": "Write", "tool_input": {"file_path": path}, **event}


def test_post_tool_use_flags_a_slop_markdown_file():
    with tempfile.TemporaryDirectory() as d:
        code, out, err = run(post(write_slop(d)))
    assert code == 2 and "simple-korean: notes.md에 오류" in err, (code, err)


def test_post_tool_use_prints_errors_first_with_line_numbers():
    with tempfile.TemporaryDirectory() as d:
        path = pathlib.Path(d, "notes.md")
        path.write_text("# 제목\n\n서버에 대해 설명합니다. 원인인 것 같습니다. 값이 변경되어졌습니다.\n", encoding="utf-8")
        code, out, err = run(post(str(path)))
    assert code == 2, (code, err)
    lines = err.splitlines()
    assert "3번 줄, 짐작·권고(오류): 것 같습니다" in err, err
    assert "3번 줄, 이중 피동(오류): 되어졌" in err, err
    assert lines.index("  3번 줄, 이중 피동(오류): 되어졌") < lines.index("  3번 줄, 번역투(경고): 에 대해"), err


def test_post_tool_use_ignores_clean_file_and_non_markdown():
    with tempfile.TemporaryDirectory() as d:
        clean = pathlib.Path(d, "clean.md")
        clean.write_text("마이그레이션을 실행하세요. 그다음 서비스를 다시 시작하세요.\n", encoding="utf-8")
        assert run(post(str(clean)))[0] == 0
    assert run(post("/tmp/x.py"))[0] == 0


def test_post_tool_use_skips_english_file():
    with tempfile.TemporaryDirectory() as d:
        path = pathlib.Path(d, "README.en.md")
        path.write_text("This tool is robust — it simply works; you should try it.\n", encoding="utf-8")
        assert run(post(str(path)))[0] == 0


def test_post_tool_use_uses_project_config():
    with tempfile.TemporaryDirectory() as d:
        pathlib.Path(d, ".simple-korean.json").write_text('{"terms": {"release": "릴리즈"}}', encoding="utf-8")
        path = pathlib.Path(d, "notes.md")
        path.write_text("릴리즈 노트를 보세요.\n", encoding="utf-8")
        assert run(post(str(path)))[0] == 0


def test_post_tool_use_reports_broken_config():
    with tempfile.TemporaryDirectory() as d:
        pathlib.Path(d, ".simple-korean.json").write_text("{broken", encoding="utf-8")
        path = pathlib.Path(d, "notes.md")
        path.write_text("마이그레이션을 실행하세요.\n", encoding="utf-8")
        code, out, err = run(post(str(path)))
    assert code == 2 and "설정 파일을 읽지 못해 기본 설정으로 점검했습니다" in err, (code, err)


def test_post_tool_use_skips_the_claude_config_dir():
    with tempfile.TemporaryDirectory() as d:
        path = write_slop(pathlib.Path(d, "projects", "repo", "memory"), "MEMORY.md")
        assert run(post(path))[0] == 2, "설정 디렉터리 밖의 메모리 파일은 검사한다"
        assert run(post(path), env={"CLAUDE_CONFIG_DIR": d})[0] == 0


def test_post_tool_use_skips_a_dot_claude_directory():
    with tempfile.TemporaryDirectory() as d:
        assert run(post(write_slop(pathlib.Path(d, ".claude", "agent-memory", "reviewer"), "MEMORY.md")))[0] == 0


def test_post_tool_use_honours_the_exclude_globs():
    with tempfile.TemporaryDirectory() as d:
        path = write_slop(d)
        assert run(post(path))[0] == 2
        globs = os.pathsep.join(["~/no-such-file.md", f"{d}/*.md"])
        assert run(post(path), env={"SIMPLE_KOREAN_LINT_EXCLUDE": globs})[0] == 0


def test_post_tool_use_resolves_a_relative_path_against_the_event_cwd():
    with tempfile.TemporaryDirectory() as d:
        write_slop(d)
        assert run(post("notes.md", cwd=d))[0] == 2


def test_post_tool_use_lints_a_path_that_escapes_a_dot_claude_directory():
    with tempfile.TemporaryDirectory() as d:
        write_slop(d)
        pathlib.Path(d, ".claude").mkdir()
        assert run(post(str(pathlib.Path(d, ".claude", "..", "notes.md"))))[0] == 2


def test_post_tool_use_skips_a_symlink_into_a_dot_claude_directory():
    with tempfile.TemporaryDirectory() as d:
        link = pathlib.Path(d, "notes.md")
        link.symlink_to(write_slop(pathlib.Path(d, ".claude"), "MEMORY.md"))
        assert run(post(str(link)))[0] == 0


def test_post_tool_use_skips_a_symlinked_dot_claude_directory():
    with tempfile.TemporaryDirectory() as d:
        write_slop(pathlib.Path(d, "dotfiles"), "MEMORY.md")
        pathlib.Path(d, ".claude").symlink_to(pathlib.Path(d, "dotfiles"))
        assert run(post(str(pathlib.Path(d, ".claude", "MEMORY.md"))))[0] == 0


def test_post_tool_use_matches_a_glob_through_a_symlinked_directory():
    with tempfile.TemporaryDirectory() as d:
        write_slop(pathlib.Path(d, "store"))
        pathlib.Path(d, "notes").symlink_to(pathlib.Path(d, "store"))
        path = str(pathlib.Path(d, "notes", "notes.md"))
        assert run(post(path))[0] == 2
        assert run(post(path), env={"SIMPLE_KOREAN_LINT_EXCLUDE": f"{d}/notes/*"})[0] == 0


def test_stop_flags_slop_reply_and_never_blocks():
    reply = "좋은 질문입니다! **강력한** 방법은 이렇습니다 — 원활하게 처리합니다.\n- 첫째\n- 둘째\n도움이 되셨기를 바랍니다."
    code, out, err = run({"hook_event_name": "Stop", "last_assistant_message": reply})
    assert code == 0 and "systemMessage" in out, (code, out)
    message = json.loads(out)["systemMessage"]
    for word in ("em-dash 1개", "굵은 글씨 1개", "목록 항목 2개", "슬롭 어휘", "인사말", "맺음말"):
        assert word in message, message


def test_stop_does_not_count_sentences():
    reply = " ".join(f"단계 {i}를 실행합니다." for i in range(20))
    code, out, err = run({"hook_event_name": "Stop", "last_assistant_message": reply})
    assert code == 0 and out.strip() == "", (code, out)


def test_stop_is_silent_on_a_good_reply():
    reply = "디스크가 가득 차서 빌드가 실패했습니다. 2GB를 비우고 다시 실행하세요."
    code, out, err = run({"hook_event_name": "Stop", "last_assistant_message": reply})
    assert code == 0 and out.strip() == "", (code, out)


def test_stop_skips_english_reply():
    reply = "**Sure!** Here is the answer:\n- one\n- two\nI hope this helps!"
    code, out, err = run({"hook_event_name": "Stop", "last_assistant_message": reply})
    assert code == 0 and out.strip() == "", (code, out)


def test_garbage_stdin_exits_zero():
    r = subprocess.run([sys.executable, str(HOOK)], input="not json", capture_output=True, text=True)
    assert r.returncode == 0


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
```

- [ ] **Step 2: 테스트를 돌려 실패를 확인한다**

Run: `python3 src/hooks/test_lint_hook.py`
Expected: 첫 테스트가 `AssertionError`로 실패한다(훅 파일이 없어 종료 코드가 2가 아니거나 메시지가 없다).

- [ ] **Step 3: 구현을 쓴다**

`src/hooks/lint_hook.py`:

```python
#!/usr/bin/env python3
"""Claude Code 훅의 글쓰기 점검. 알리기만 하고 막지 않는다.

PostToolUse(.md 파일의 Write|Edit): evals/ko_lint.py로 파일을 검사한다. 위반이 있으면 오류부터
MAX_HOOK_HITS개까지 줄 번호, 범주, 강도, 문구를 stderr로 보내고 2로 끝낸다. PostToolUse의 종료
코드 2는 알림이다. 도구는 이미 실행되었다. 한글 비율이 MIN_HANGUL_RATIO보다 낮은 파일, Claude
설정 디렉터리와 .claude 경로의 파일, SIMPLE_KOREAN_LINT_EXCLUDE 글롭에 맞는 파일은 건너뛴다.
프로젝트의 .simple-korean.json이 깨져 있으면 기본 설정으로 검사하고 그 사실을 한 줄 알린다.

Stop: last_assistant_message가 한국어이면 답변 규칙(헤더, 불릿, 굵은 글씨, em-dash, 슬롭 어휘,
인사말, 맺음말)을 점검하고, 어긴 것이 있을 때만 systemMessage를 낸다. 항상 0으로 끝내므로
세션이 되풀이되지 않는다.
"""
import fnmatch
import json
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT / "evals"))

MAX_HOOK_HITS = 12
MIN_HANGUL_RATIO = 0.3
CLAUDE_DIR = ".claude"
REPLY_COUNTS = (("em_dash", "em-dash"), ("bold_spans", "굵은 글씨"), ("headers", "헤더"), ("bullets", "목록 항목"))


def load_linter():
    try:
        import ko_lint  # noqa: WPS433
        return ko_lint
    except Exception:  # noqa: BLE001  린터를 못 읽으면 조용히 건너뛴다
        return None


def absolute(path, cwd=None):
    """경로를 절대 경로로 만든다. 하네스가 세션 디렉터리 기준 상대 경로를 보낼 수 있다."""
    return pathlib.Path(cwd or ".", pathlib.Path(path).expanduser()).absolute()


def variants(path):
    """적힌 그대로의 경로와 심볼릭 링크를 푼 경로. 제외 규칙은 둘 중 하나만 맞아도 적용한다."""
    return {pathlib.Path(os.path.normpath(path)), path.resolve()}


def excluded(target):
    """에이전트가 자기용으로 쓰는 마크다운과 사용자가 제외한 경로이면 참이다."""
    config_dirs = variants(absolute(os.environ.get("CLAUDE_CONFIG_DIR") or f"~/{CLAUDE_DIR}"))
    raw = os.environ.get("SIMPLE_KOREAN_LINT_EXCLUDE", "").split(os.pathsep)
    patterns = [os.path.expanduser(p) for p in raw if p]
    for form in variants(target):
        if CLAUDE_DIR in form.parts or any(form.is_relative_to(d) for d in config_dirs):
            return True
        if any(fnmatch.fnmatch(str(form), p) for p in patterns):
            return True
    return False


def _detail(lint, text, target):
    """검사 결과와 설정 알림(없으면 None)을 돌려준다. 깨진 설정은 기본 설정으로 대신한다."""
    try:
        return lint.lint_detail(text, "descriptive", path=str(target)), None
    except ValueError as err:
        note = f"설정 파일을 읽지 못해 기본 설정으로 점검했습니다: {err}"
        return lint.lint_detail(text, "descriptive", config={}), note


def post_tool_use(event):
    path = (event.get("tool_input") or {}).get("file_path") or ""
    if not path.endswith(".md"):
        return 0
    target = absolute(path, event.get("cwd"))
    lint = load_linter()
    if lint is None or excluded(target):
        return 0
    try:
        text = target.read_text(encoding="utf-8")
    except OSError:
        return 0
    if lint.ko_text.hangul_ratio(text) < MIN_HANGUL_RATIO:
        return 0
    detail, note = _detail(lint, text, target)
    if not detail and not note:
        return 0
    detail = sorted(detail, key=lambda h: (h["severity"] != "error", h["line"]))
    errors = sum(1 for h in detail if h["severity"] == "error")
    lines = [f"simple-korean: {target.name}에 오류 {errors}건, 경고 {len(detail) - errors}건이 있습니다."]
    lines += [f"  {note}"] if note else []
    for h in detail[:MAX_HOOK_HITS]:
        label = lint.LABELS.get(h["category"], h["category"])
        lines.append(f"  {h['line']}번 줄, {label}({lint.SEVERITY_LABELS[h['severity']]}): {h['text']}")
    if len(detail) > MAX_HOOK_HITS:
        lines.append(f"  그 밖에 {len(detail) - MAX_HOOK_HITS}건이 더 있습니다.")
    lines.append("방금 쓴 파일에서 이 항목을 고친 뒤 계속하세요.")
    sys.stderr.write("\n".join(lines) + "\n")
    return 2


def stop(event):
    reply = event.get("last_assistant_message") or ""
    lint = load_linter()
    if lint is None or lint.ko_text.hangul_ratio(reply) < MIN_HANGUL_RATIO:
        return 0
    counts = lint.reader_check(reply)["counts"]
    problems = [f"{label} {counts[key]}개" for key, label in REPLY_COUNTS if counts[key]]
    slop = len(lint.ko_rules.SLOP_RX.findall(lint.ko_text.mask(lint.ko_text.nfc(reply))))
    if slop:
        problems.append(f"슬롭 어휘 {slop}개")
    if counts["opener"]:
        problems.append("인사말")
    if counts["closer"]:
        problems.append("맺음말")
    if problems:
        message = "simple-korean 답변 점검: " + ", ".join(problems) + ". 서술형으로 답하세요."
        print(json.dumps({"systemMessage": message}, ensure_ascii=False))
    return 0


def main():
    try:
        event = json.load(sys.stdin)
    except Exception:  # noqa: BLE001
        return 0
    try:
        name = event.get("hook_event_name", "")
        if name == "PostToolUse":
            return post_tool_use(event)
        if name == "Stop":
            return stop(event)
    except Exception:  # noqa: BLE001  알림용 훅이다. 오류가 나도 세션을 막거나 되풀이하지 않는다
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: 테스트를 돌려 통과를 확인한다**

Run: `chmod +x src/hooks/lint_hook.py && python3 src/hooks/test_lint_hook.py && /usr/bin/python3 src/hooks/test_lint_hook.py`
Expected: 두 번 모두 `ok` 19줄.

- [ ] **Step 5: 커밋한다**

```bash
git add src/hooks/lint_hook.py src/hooks/test_lint_hook.py
git commit -m "feat: add advisory file and reply checks for Claude Code hooks" -m $'Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01SanRSLxxVtkLMJh1wLGeGZ'
```

### Task 12: 플러그인 매니페스트와 훅 설명서

**Files:**
- Create: `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `.codex-plugin/plugin.json`, `.codex-plugin/hooks.json`, `.agents/plugins/marketplace.json`, `src/hooks/README.md`

**Interfaces:**
- Consumes: Task 8의 스킬과 출력 스타일, Task 10~11의 훅 스크립트
- Produces: 플러그인 이름 `simple-korean`, 버전 `"1.0.0"`(세 매니페스트의 `version`, Task 18 수치 검증이 읽는다), 출력 스타일 `simple-korean:simple-korean`

- [ ] **Step 1: 매니페스트를 쓴다**

`.claude-plugin/plugin.json`:

```json
{
  "name": "simple-korean",
  "displayName": "Simple Korean",
  "description": "기술 문서와 답변을 쉬운 한국어로 쓰게 합니다. ASD-STE100의 규칙을 한국어 문법에 맞게 다시 세웠습니다. 짧은 문장, 명령 앞의 조건, 한 단어 한 뜻, 번역투와 AI 슬롭 제거, 정해진 외래어 표기를 지킵니다.",
  "version": "1.0.0",
  "author": {
    "name": "say8425"
  },
  "homepage": "https://github.com/say8425/SimpleKorean",
  "repository": "https://github.com/say8425/SimpleKorean",
  "license": "MIT",
  "keywords": [
    "technical-writing",
    "documentation",
    "korean",
    "plain-language",
    "ste",
    "asd-ste100"
  ],
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "node \"${CLAUDE_PLUGIN_ROOT}/src/hooks/simple-korean-activate.js\"",
            "timeout": 5,
            "statusMessage": "SimpleKorean 규칙을 불러오는 중..."
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"${CLAUDE_PLUGIN_ROOT}/src/hooks/lint_hook.py\"",
            "timeout": 10,
            "statusMessage": "SimpleKorean: 파일을 점검하는 중..."
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"${CLAUDE_PLUGIN_ROOT}/src/hooks/lint_hook.py\"",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```

`.claude-plugin/marketplace.json`:

```json
{
  "name": "simple-korean",
  "owner": {
    "name": "say8425",
    "url": "https://github.com/say8425"
  },
  "description": "기술 문서와 답변을 쉬운 한국어로 쓰게 하는 에이전트 스킬입니다. AminBlg/SimpleEnglish의 한국어 파생입니다.",
  "plugins": [
    {
      "name": "simple-korean",
      "source": "./",
      "displayName": "Simple Korean",
      "description": "기술 문서와 답변을 쉬운 한국어로 쓰게 합니다. ASD-STE100의 규칙을 한국어 문법에 맞게 다시 세웠습니다. 짧은 문장, 명령 앞의 조건, 한 단어 한 뜻, 번역투와 AI 슬롭 제거, 정해진 외래어 표기를 지킵니다.",
      "version": "1.0.0",
      "author": {
        "name": "say8425"
      },
      "homepage": "https://github.com/say8425/SimpleKorean",
      "repository": "https://github.com/say8425/SimpleKorean",
      "license": "MIT",
      "keywords": [
        "technical-writing",
        "documentation",
        "korean",
        "plain-language",
        "ste",
        "asd-ste100"
      ]
    }
  ]
}
```

`.codex-plugin/plugin.json`:

```json
{
  "name": "simple-korean",
  "version": "1.0.0",
  "description": "기술 문서와 답변을 쉬운 한국어로 쓰게 합니다. ASD-STE100의 규칙을 한국어 문법에 맞게 다시 세웠습니다. 짧은 문장, 명령 앞의 조건, 한 단어 한 뜻, 번역투와 AI 슬롭 제거, 정해진 외래어 표기를 지킵니다.",
  "author": {
    "name": "say8425"
  },
  "homepage": "https://github.com/say8425/SimpleKorean",
  "repository": "https://github.com/say8425/SimpleKorean",
  "license": "MIT",
  "keywords": [
    "technical-writing",
    "documentation",
    "korean",
    "plain-language",
    "ste",
    "asd-ste100"
  ],
  "skills": "./skills/",
  "hooks": "./.codex-plugin/hooks.json",
  "interface": {
    "displayName": "Simple Korean",
    "shortDescription": "기술 문서를 쉬운 한국어 규칙으로 씁니다.",
    "longDescription": "문서, 절차서, 오류 메시지, 런북, 릴리스 노트, 장애 보고서를 쓸 때 쉬운 한국어 규칙을 자동으로 불러옵니다.",
    "developerName": "say8425",
    "category": "Productivity",
    "capabilities": [
      "Write"
    ],
    "websiteURL": "https://github.com/say8425/SimpleKorean",
    "defaultPrompt": [
      "이 기술 문서를 쉬운 한국어로 고쳐 주세요.",
      "이 절차를 엄격 모드로 써 주세요.",
      "이 문서를 SimpleKorean 규칙으로 확인해 주세요."
    ],
    "brandColor": "#0F766E"
  }
}
```

`.codex-plugin/hooks.json`:

```json
{
  "description": "Codex 세션마다 SimpleKorean 규칙을 자동으로 불러옵니다.",
  "hooks": {
    "SessionStart": [
      {
        "matcher": "^(startup|resume|clear|compact)$",
        "hooks": [
          {
            "type": "command",
            "command": "[ -n \"${PLUGIN_ROOT}\" ] && node \"${PLUGIN_ROOT}/src/hooks/simple-korean-activate.js\" || true",
            "timeout": 5,
            "statusMessage": "SimpleKorean 규칙을 불러오는 중...",
            "additionalContextLimit": 0
          }
        ]
      }
    ]
  }
}
```

`.agents/plugins/marketplace.json`:

```json
{
  "name": "simple-korean",
  "interface": {
    "displayName": "Simple Korean"
  },
  "plugins": [
    {
      "name": "simple-korean",
      "source": {
        "source": "local",
        "path": "./"
      },
      "category": "Productivity"
    }
  ]
}
```

- [ ] **Step 2: JSON 형식을 확인한다**

Run: `for f in .claude-plugin/plugin.json .claude-plugin/marketplace.json .codex-plugin/plugin.json .codex-plugin/hooks.json .agents/plugins/marketplace.json; do python3 -m json.tool "$f" > /dev/null && echo "ok $f"; done`
Expected: `ok` 5줄.

- [ ] **Step 3: 훅 설명서를 쓴다**

`src/hooks/README.md`:

````markdown
# SimpleKorean 훅

Claude Code 플러그인과 Codex 플러그인에는 세션 시작 훅이 있습니다. 이 훅은 세션이 시작되거나, 다시 열리거나, 비워지거나, 압축될 때 SimpleKorean 규칙을 불러옵니다. 사용자가 스킬 이름을 말하지 않아도 됩니다.

세션 시작 훅에는 Node.js가 필요합니다. 두 플러그인 모두 `node` 명령으로 `src/hooks/simple-korean-activate.js`를 실행합니다.

## 설치

Claude Code:

```bash
claude plugin marketplace add say8425/SimpleKorean
claude plugin install simple-korean@simple-korean
```

Codex:

```bash
codex plugin marketplace add say8425/SimpleKorean
codex plugin add simple-korean@simple-korean
```

Codex는 훅을 처음 실행하기 전에 검토하고 믿을지 묻습니다. `/hooks`를 열어 승인하세요.

## 훅이 보내는 내용

세션 시작 훅은 `prompts/system-prompt.md`의 규칙 블록을 표준 출력으로 씁니다. 규칙 블록은 두 `---` 줄 사이이고 약 2,000자입니다. 페이지 제목, 붙여 넣는 곳 안내, 짧은 판본은 보내지 않습니다. Claude Code는 훅 출력을 10,000자까지만 받으므로, 훅은 9,500자를 넘는 출력 대신 짧은 대체 규칙을 보냅니다. 전체 스킬은 `skills/simple-korean/SKILL.md`에 있고, 훅은 엄격 모드나 점검을 요청받으면 그 파일을 읽으라고 알립니다.

Codex도 훅 문맥에 상한을 둡니다. `.codex-plugin/hooks.json`의 `additionalContextLimit: 0`은 파일로 빼는 문턱을 끕니다. 상한 자체를 없애지는 않습니다. 규칙 블록은 그 상한 안에 듭니다.

훅이 프롬프트 파일을 읽지 못하면 다음 위치를 읽습니다. 모든 위치가 실패하면 짧은 대체 규칙을 내고 0으로 끝납니다. 세션은 그대로 시작됩니다.

## 하네스마다 훅을 읽는 곳

- Claude Code: `.claude-plugin/plugin.json`의 `hooks` 항목
- Codex: `.codex-plugin/hooks.json`(`.codex-plugin/plugin.json`의 `hooks` 항목이 가리킴). 마켓플레이스 목록은 `.agents/plugins/marketplace.json`입니다.

## 테스트

레포지토리 최상위에서 실행하세요:

```bash
node --test src/hooks/simple-korean-activate.test.js
python3 src/hooks/test_lint_hook.py
```

## 글쓰기 점검 훅 (Claude Code)

Claude Code에서는 알림용 훅 두 개가 더 돕니다. 둘 다 작업을 막지 않습니다:

- `PostToolUse`(`Write`, `Edit`): 마크다운 파일이면 `src/hooks/lint_hook.py`가 `evals/ko_lint.py`로 검사하고, 위반의 줄 번호와 문구를 오류부터 12개까지 모델에 보여 줍니다.
- `Stop`: 같은 스크립트가 마지막 답변을 읽습니다. 답변에 em-dash, 굵은 글씨, 헤더, 목록 항목, 슬롭 어휘, 인사말, 맺음말이 있으면 시스템 메시지를 더합니다.

Codex에서는 세션 시작 훅만 돕니다.

## 점검 훅이 건너뛰는 것

글쓰기 규칙은 사람이 읽을 문서에 적용합니다. 에이전트가 자기용으로 쓰는 메모리 파일에는 적용하지 않습니다. 그래서 `PostToolUse` 점검은 다음을 건너뜁니다:

- 한글 비율이 30%보다 낮은 파일(영어 문서)과 답변
- Claude 설정 디렉터리 아래의 모든 경로(`CLAUDE_CONFIG_DIR`, 없으면 `~/.claude`)
- `.claude` 디렉터리가 들어간 모든 경로(예: `my-project/.claude/agent-memory/reviewer/MEMORY.md`)
- `SIMPLE_KOREAN_LINT_EXCLUDE`의 글롭에 맞는 경로

심볼릭 링크로는 건너뛰기를 피할 수 없습니다. 점검은 적힌 그대로의 절대 경로와 링크를 푼 경로를 모두 대조합니다. 둘 중 하나만 맞아도 건너뜁니다.

`SIMPLE_KOREAN_LINT_EXCLUDE`에는 글롭을 플랫폼의 경로 구분자로 나눠 적습니다(Linux와 macOS는 `:`, Windows는 `;`). 패턴의 `*`는 `/`에도 맞습니다. 맨 앞의 `~`는 홈 디렉터리로 바뀝니다.

```bash
export SIMPLE_KOREAN_LINT_EXCLUDE="$HOME/notes/*:*/CHANGELOG.md"
```

파일 점검을 끄려면 이 변수를 `*`로 설정하세요. 답변 점검은 계속 돕니다.

## 프로젝트 설정

점검 훅은 검사하는 파일의 디렉터리부터 위로 올라가며 `.simple-korean.json`을 찾습니다. 이 파일로 단어 목록의 지정형을 바꾸고 건너뛸 문자열을 더할 수 있습니다. 파일이 깨져 있으면 기본 설정으로 검사하고 그 사실을 한 줄 알립니다.

```json
{
  "terms": {"release": "릴리즈", "method": {"write": "메소드", "reason": "TTA 정보통신용어사전을 따름"}},
  "skip": ["디렉토리 유틸리티"],
  "spacing": "attached"
}
```

예시를 일부러 틀리게 써야 하면 그 부분을 `<!-- simple-korean: off -->`와 `<!-- simple-korean: on -->` 사이에 두세요. 그 사이는 검사하지 않습니다.
````

Run: `python3 evals/ko_lint.py --gate=warning src/hooks/README.md > /dev/null; echo "exit=$?"`
Expected: `exit=0`.

- [ ] **Step 4: 플러그인을 불러오는 스모크 테스트를 돌린다**

이 단계는 `claude -p`를 한 번 부른다(2026-10-08 계획 검증 때 $0.035). 레포 최상위에서 실행한다.

```bash
claude -p "규칙 블록에 있는 '이 프로젝트의 지정형' 단어 여섯 개를 쉼표로만 나열하세요. 규칙 블록이 없으면 NONE이라고 답하세요." \
  --plugin-dir "$PWD" --setting-sources "" --strict-mcp-config --model claude-sonnet-5-5 --effort low \
  --output-format stream-json --verbose --disallowedTools "Bash,Read,Write,Edit,Glob,Grep,WebFetch,WebSearch" \
  < /dev/null > /tmp/sk-smoke.jsonl
python3 - /tmp/sk-smoke.jsonl <<'SMOKE_EOF'
import json, sys
init, result, hooks = {}, None, []
for line in open(sys.argv[1], encoding="utf-8"):
    try:
        e = json.loads(line)
    except ValueError:
        continue
    if e.get("type") == "system" and e.get("subtype") == "init":
        init = e
    if e.get("type") == "system" and e.get("subtype") == "hook_response":
        hooks.append(e.get("output", ""))
    if e.get("type") == "result":
        result = e.get("result")
plugins = [p.get("name") for p in init.get("plugins") or []]
assert "simple-korean" in plugins, plugins
assert any(h.startswith("SIMPLE KOREAN 스킬이 자동으로 켜졌습니다") for h in hooks), hooks
assert all(w in (result or "") for w in ("레포지토리", "바디", "칼럼", "대상", "리디렉션", "리팩터링")), result
print("smoke OK:", result)
SMOKE_EOF
```

Expected: `smoke OK: 레포지토리, 바디, 칼럼, 대상, 리디렉션, 리팩터링`.

- [ ] **Step 5: 토큰 비용을 재서 기록한다**

Run: `claude --plugin-dir "$PWD" plugin details simple-korean`
Expected: `Always-on: ~300 tok`, 표의 `simple-korean` 행 on-invoke `~5.1k`(계획 검증 값). README에는 이 숫자 대신 이 명령을 적는다(Task 19). 숫자는 스킬 문서가 바뀔 때마다 달라지기 때문이다. 항상 붙는 비용이 400토큰을 넘으면 SKILL.md의 `description`을 줄인다.

- [ ] **Step 6: 커밋한다**

```bash
git add .claude-plugin .codex-plugin .agents src/hooks/README.md
git commit -m "feat: package Claude Code and Codex plugins" -m $'Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01SanRSLxxVtkLMJh1wLGeGZ'
```

---

## 단계 D: 측정

### Task 13: 기초 어휘 등급 목록과 쉬운 단어 비율

**Files:**
- Create: `tools/basic-vocabulary/extract.py`, `data/basic-vocabulary/grades.tsv`(생성물), `data/basic-vocabulary/README.md`, `evals/metrics.py`
- Modify: `NOTICE`(2번 항목 추가)
- Test: `evals/tests/test_metrics.py`

**Interfaces:**
- Consumes: 없음(측정 전용 모듈이다. 린터와 훅은 이 모듈을 쓰지 않는다)
- Produces: `data/basic-vocabulary/grades.tsv`(머리글 `등급\t어휘\t품사\t어종`, 40,000행), `metrics.grade1_lemmas(path=str(GRADES)) -> frozenset[tuple[str, str]]`, `metrics.easy_word_counts(text, path=str(GRADES)) -> tuple[int, int] | None`(kiwipiepy가 없으면 None), `extract.read_rows(xlsx, sheet)`, `extract.extract(rows)`, `extract.check_counts(records, expected)`, `extract.write_tsv(records, out)`. 측정용 가상 환경 `.venv`(Python 3.12, kiwipiepy 0.24.0).

- [ ] **Step 1: 실패하는 테스트를 쓴다**

`evals/tests/test_metrics.py`:

```python
import importlib.util
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "evals"))
import metrics  # noqa: E402

_spec = importlib.util.spec_from_file_location("extract", ROOT / "tools" / "basic-vocabulary" / "extract.py")
extract = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(extract)

NS = 'xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"'
RNS = 'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"'


def _write_xlsx(path, rows):
    shared = sorted({v for row in rows for v in row})
    index = {v: i for i, v in enumerate(shared)}
    body = "".join(
        f'<row r="{r}">' + "".join(f'<c r="{chr(65 + c)}{r}" t="s"><v>{index[v]}</v></c>' for c, v in enumerate(row)) + "</row>"
        for r, row in enumerate(rows, 1))
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("xl/workbook.xml", f'<workbook {NS} {RNS}><sheets><sheet name="{extract.SHEET}" sheetId="1" r:id="rId1"/></sheets></workbook>')
        z.writestr("xl/_rels/workbook.xml.rels", '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Target="worksheets/sheet1.xml" Type="t"/></Relationships>')
        z.writestr("xl/sharedStrings.xml", f"<sst {NS}>" + "".join(f"<si><t>{s}</t></si>" for s in shared) + "</sst>")
        z.writestr("xl/worksheets/sheet1.xml", f"<worksheet {NS}><sheetData>{body}</sheetData></worksheet>")


def test_extract_keeps_four_columns_and_drops_meaning():
    with tempfile.TemporaryDirectory() as d:
        xlsx = Path(d, "list.xlsx")
        _write_xlsx(xlsx, [["등급", "어휘", "표준동형어번호수정", "품사", "어종", "원어", "의미", "분야"],
                           ["1등급", "학교", "0", "명사", "한자어", "學校", "뜻풀이", "일반어"],
                           ["1등급", "가다", "1", "동사", "고유어", "", "뜻풀이", "일반어"]])
        records = extract.extract(extract.read_rows(xlsx))
        assert records == [("1등급", "학교", "명사", "한자어"), ("1등급", "가다", "동사", "고유어")]
        extract.check_counts(records, expected={"1등급": 2})
        out = Path(d, "grades.tsv")
        extract.write_tsv(records, out)
        text = out.read_text(encoding="utf-8")
        assert text.splitlines()[0] == "등급\t어휘\t품사\t어종" and "뜻풀이" not in text


def test_check_counts_stops_on_mismatch():
    try:
        extract.check_counts([("1등급", "학교", "명사", "한자어")], expected={"1등급": 2})
    except SystemExit as err:
        assert "등급별 개수" in str(err)
    else:
        raise AssertionError("SystemExit가 나야 합니다")


def test_grade1_lemmas_maps_pos_to_kiwi_tags():
    with tempfile.TemporaryDirectory() as d:
        tsv = Path(d, "grades.tsv")
        tsv.write_text("등급\t어휘\t품사\t어종\n1등급\t학교\t명사\t한자어\n1등급\t가다\t동사/보조동사\t고유어\n"
                       "1등급\t다시\t명사/부사\t고유어\n2등급\t설치\t명사\t한자어\n", encoding="utf-8")
        assert metrics.grade1_lemmas(str(tsv)) == frozenset({("학교", "NNG"), ("가다", "VV"), ("다시", "NNG"), ("다시", "MAG")})


def test_easy_word_counts_with_or_without_kiwi():
    got = metrics.easy_word_counts("나는 학교에 갑니다.")
    try:
        import kiwipiepy  # noqa: F401
    except ImportError:
        assert got is None
        return
    hits, total = got
    assert total >= 2 and hits >= 2, got
```

- [ ] **Step 2: 테스트를 돌려 실패를 확인한다**

Run: `python3 evals/tests/run.py evals/tests/test_metrics.py`
Expected: `ModuleNotFoundError: No module named 'metrics'`로 실패한다.

- [ ] **Step 3: 추출 도구와 지표 모듈을 쓴다**

`tools/basic-vocabulary/extract.py`:

```python
#!/usr/bin/env python3
"""국립국어원 「국어 기초 어휘 선정 및 어휘 등급화 목록」(2023) xlsx에서 등급, 어휘, 품사, 어종만 뽑는다.

xlsx는 공공누리 제1유형이다(출처 표시). '의미' 열은 사전 뜻풀이라 싣지 않는다. 표준 라이브러리만 쓴다.

    python3 -I tools/basic-vocabulary/extract.py <xlsx 경로> data/basic-vocabulary/grades.tsv
"""
import csv
import re
import sys
import xml.etree.ElementTree as ET
import zipfile

SHEET = "전체(1~5등급), 40,000개"
M = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
KEEP = ("등급", "어휘", "품사", "어종")
EXPECTED = {"1등급": 5000, "2등급": 2500, "3등급": 5500, "4등급": 10000, "5등급": 17000}


def _shared_strings(z):
    if "xl/sharedStrings.xml" not in z.namelist():
        return []
    root = ET.fromstring(z.read("xl/sharedStrings.xml"))
    return ["".join(t.text or "" for t in si.iter(M + "t")) for si in root.iter(M + "si")]


def _sheet_path(z, name):
    workbook = ET.fromstring(z.read("xl/workbook.xml"))
    rels = {r.get("Id"): r.get("Target") for r in ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))}
    for sheet in workbook.iter(M + "sheet"):
        if sheet.get("name") == name:
            target = rels[sheet.get(R + "id")]
            return target.lstrip("/") if target.startswith("/") else "xl/" + target
    names = [s.get("name") for s in workbook.iter(M + "sheet")]
    raise SystemExit(f"시트 {name!r}가 없습니다. 있는 시트: {names}")


def _cell_value(cell, shared):
    v = cell.find(M + "v")
    if cell.get("t") == "s" and v is not None:
        return shared[int(v.text)]
    if cell.get("t") == "inlineStr":
        return "".join(t.text or "" for t in cell.iter(M + "t"))
    return v.text if v is not None and v.text else ""


def read_rows(xlsx, sheet=SHEET):
    """시트의 행을 {열 글자: 값} 목록으로 읽는다."""
    with zipfile.ZipFile(xlsx) as z:
        shared = _shared_strings(z)
        root = ET.fromstring(z.read(_sheet_path(z, sheet)))
    return [{re.match(r"[A-Z]+", c.get("r")).group(0): _cell_value(c, shared) for c in row.iter(M + "c")}
            for row in root.iter(M + "row")]


def extract(rows):
    """머리글 행으로 열을 찾아 (등급, 어휘, 품사, 어종) 행을 돌려준다. 머리글이 다르면 멈춘다."""
    header = rows[0]
    columns = {}
    for name in KEEP:
        found = [k for k, v in header.items() if v == name]
        if not found:
            raise SystemExit(f"머리글에 {name!r} 열이 없습니다: {header}")
        columns[name] = found[0]
    return [tuple(r.get(columns[n], "") for n in KEEP) for r in rows[1:] if r.get(columns["어휘"])]


def check_counts(records, expected=EXPECTED):
    """등급별 개수가 보고서의 값과 같은지 확인한다. 다르면 멈춘다."""
    counts = {}
    for grade, *_ in records:
        counts[grade] = counts.get(grade, 0) + 1
    if counts != expected:
        raise SystemExit(f"등급별 개수가 다릅니다: {counts} (기대값 {expected})")


def write_tsv(records, out):
    with open(out, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="\t", lineterminator="\n")
        writer.writerow(KEEP)
        writer.writerows(records)


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 2:
        raise SystemExit("사용법: extract.py <xlsx 경로> <출력 TSV 경로>")
    records = extract(read_rows(args[0]))
    check_counts(records)
    write_tsv(records, args[1])
    print(f"{len(records)} rows -> {args[1]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

`evals/metrics.py`:

```python
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
```

- [ ] **Step 4: 측정용 가상 환경을 만든다**

Run: `uv venv .venv --python 3.12 && uv pip install --python .venv/bin/python kiwipiepy==0.24.0`
Expected: `+ kiwipiepy==0.24.0`, `+ kiwipiepy-model==0.24.0`. `.venv/`는 `.gitignore`에 있다. 설치가 실패하면 네트워크를 먼저 확인한다(`curl -sI https://pypi.org/simple/kiwipiepy/`).

- [ ] **Step 5: xlsx를 내려받아 등급 목록을 만든다**

xlsx는 믿지 않는 데이터다. 레포지토리 밖의 새 빈 디렉터리에 받는다.

```bash
: "${SCRATCH:?SCRATCH에 레포지토리 밖의 스크래치 디렉터리를 넣으세요}"
mkdir -p "$SCRATCH/basic-vocabulary" data/basic-vocabulary
curl -sL --max-time 120 -A "Mozilla/5.0" -o "$SCRATCH/basic-vocabulary/basic.xlsx" 'https://www.korean.go.kr/common/download.do?file_path=reportData&c_file_name=1d6d75b9-45cb-49d4-989f-1483c332573a.xlsx&o_file_name=%EA%B5%AD%EC%96%B4%20%EA%B8%B0%EC%B4%88%20%EC%96%B4%ED%9C%98%20%EC%84%A0%EC%A0%95%20%EB%B0%8F%20%EC%96%B4%ED%9C%98%20%EB%93%B1%EA%B8%89%ED%99%94%20%EB%AA%A9%EB%A1%9D%20%EC%A0%84%EC%B2%B4.xlsx'
shasum -a 256 "$SCRATCH/basic-vocabulary/basic.xlsx"
chmod +x tools/basic-vocabulary/extract.py
python3 -I tools/basic-vocabulary/extract.py "$SCRATCH/basic-vocabulary/basic.xlsx" data/basic-vocabulary/grades.tsv
```

Expected: SHA-256 `6eec715bca39d1006702da020f5c61a7a1f3db81fdb6101619f68d0b0ff70b53`, 그리고 `40000 rows -> data/basic-vocabulary/grades.tsv`. 해시가 다르면 국립국어원이 파일을 바꾼 것이다. `extract.py`가 등급별 개수를 확인하므로 개수가 맞으면 계속하고, `data/basic-vocabulary/README.md`의 해시를 새 값으로 고친다.

- [ ] **Step 6: 테스트와 지표를 확인한다**

Run: `.venv/bin/python evals/tests/run.py evals/tests/test_metrics.py && /usr/bin/python3 evals/tests/run.py evals/tests/test_metrics.py && .venv/bin/python -c "import sys; sys.path.insert(0, 'evals'); import metrics; print(metrics.easy_word_counts('나는 학교에 갑니다. 서버를 다시 시작하세요.'))"`
Expected: 두 번 모두 `ok` 4줄, 그리고 `(4, 5)`. `(1, 2)` 같은 값이 나오면 품사 열의 복합 값('동사/보조동사')을 나누지 않은 것이다.

- [ ] **Step 7: 출처 설명과 NOTICE를 쓴다**

`data/basic-vocabulary/README.md`:

````markdown
# 국어 기초 어휘 등급 목록 발췌

`grades.tsv`는 국립국어원의 「국어 기초 어휘 선정 및 어휘 등급화 목록 전체.xlsx」에서 등급, 어휘, 품사, 어종 네 열만 뽑은 파일입니다. 어휘 40,000개가 5등급으로 나뉩니다(1등급 5,000개, 2등급 2,500개, 3등급 5,500개, 4등급 10,000개, 5등급 17,000개).

- 출처: 국립국어원, 「2023년 국어 기초 어휘 선정 및 어휘 등급화 연구」의 첨부 파일(https://www.korean.go.kr/front/reportData/reportDataView.do?mn_id=207&report_seq=1160&pageIndex=1)
- 이용 조건: 첨부 xlsx는 공공누리 제1유형입니다(출처 표시, 상업적 이용과 변경 허용). 보고서 본문은 제4유형이라 싣지 않습니다.
- 뺀 열: 표준동형어번호, 원어, 의미, 분야. 의미 열은 사전 뜻풀이라 싣지 않습니다.

이 파일은 측정에만 씁니다. `evals/metrics.py`가 형태소 분석으로 뽑은 내용어 가운데 1등급 표제어의 비율을 셉니다. 린터와 훅은 이 파일을 읽지 않습니다.

다시 만들려면 xlsx를 레포지토리 밖의 빈 디렉터리에 내려받고 다음을 실행하세요:

```bash
python3 -I tools/basic-vocabulary/extract.py <xlsx 경로> data/basic-vocabulary/grades.tsv
```

2026-10-08에 내려받은 xlsx의 SHA-256은 `6eec715bca39d1006702da020f5c61a7a1f3db81fdb6101619f68d0b0ff70b53`입니다.
````

`NOTICE` 끝에 덧붙인다:

```text

2. data/basic-vocabulary/grades.tsv
   출처: 국립국어원, 「국어 기초 어휘 선정 및 어휘 등급화 목록 전체.xlsx」(2023년 국어 기초 어휘
   선정 및 어휘 등급화 연구의 첨부 파일)
   https://www.korean.go.kr/front/reportData/reportDataView.do?mn_id=207&report_seq=1160&pageIndex=1
   이용 조건: 공공누리 제1유형(출처 표시). 등급, 어휘, 품사, 어종 열만 싣고 의미 열은 싣지 않습니다.
```

- [ ] **Step 8: 커밋한다**

```bash
git add tools/basic-vocabulary/extract.py data/basic-vocabulary evals/metrics.py evals/tests/test_metrics.py NOTICE
git commit -m "feat: add basic vocabulary grades and easy-word metric" -m $'Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01SanRSLxxVtkLMJh1wLGeGZ'
```

### Task 14: 벤치마크 실행기와 집계

**Files:**
- Create: `evals/scenarios.json`, `evals/reply_scenarios.json`, `evals/bench_common.py`, `evals/run_bench.py`, `evals/run_reply_bench.py`, `evals/report.py`
- Test: `evals/tests/test_bench.py`

**Interfaces:**
- Consumes: Task 6의 `ko_lint.lint`, `reader_check`, Task 5의 `ko_terms.scan`, `load_terms`, Task 13의 `metrics.easy_word_counts`, Task 8의 SKILL.md와 규칙 블록, Task 9의 `strict-mode.md`
- Produces: 결과 디렉터리 형식 `evals/results/<날짜>/`: `meta.json`(격리 확인), `docs/<조건>__<과제>__r<회차>.json`(키 `text`, `condition`, `scenario`, `type`, `run`, 사용량), `reply/<조건>__<질문>__r<회차>.txt`, `judge/<질문>__r<회차>.json`(키 `winner`: `plain`, `tie`, `baseline`), `RESULTS.md`. 함수: `bench_common.claude_cmd`, `call_claude(prompt, model, effort, system, timeout, run, cmd=None)`(cmd를 주면 그 명령을 그대로 쓴다. Task 16 압력 시험이 쓴다), `parse_conditions(value, allowed) -> tuple`(모르는 조건이면 SystemExit), `meta_date(out) -> str`(디렉터리 이름이 날짜면 그 날짜, 아니면 오늘 날짜. 격리 확인이 `meta.json`의 `date`에 쓴다), `probe(model, run) -> (summary, problems)`, `rule_block(text)`, `skill_body(path)`, `run_bench.build_prompt(scenario, condition)`, `run_bench.generate(out, scenarios, runs, call, sleep, conditions=CONDITIONS)`, `run_reply_bench.generate(out, scenarios, runs, call, sleep, conditions=CONDITIONS)`, 두 실행기의 CLI 인자 `--conditions`(쉼표로 나눈 조건, Task 15 보정이 `baseline`만 돌릴 때 쓴다), `judge(out, scenarios, runs, call)`, `parse_winner(text)`, `combine(first, second)`, `report.reply_stats`, `judge_stats`, `doc_stats`, `spelling_distribution`, `readme_block(results_dir, scenarios) -> str`, `results_md(results_dir, scenarios) -> str`, `replace_readme_block(readme_text, results_dir, block) -> str`, 정규식 `report.README_BLOCK`.

- [ ] **Step 1: 실패하는 테스트를 쓴다**

`evals/tests/test_bench.py`:

```python
import json
import re
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import bench_common as bc  # noqa: E402
import report  # noqa: E402
import run_bench  # noqa: E402
import run_reply_bench  # noqa: E402


def test_claude_cmd_isolates_settings_mcp_and_tools():
    cmd = bc.claude_cmd("질문", system="규칙")
    assert cmd[:3] == ["claude", "-p", "질문"]
    i = cmd.index("--setting-sources")
    assert cmd[i + 1] == "" and "--strict-mcp-config" in cmd
    assert cmd[cmd.index("--disallowedTools") + 1].startswith("Bash,Read,Write,Edit")
    assert cmd[cmd.index("--append-system-prompt") + 1] == "규칙"
    assert "--verbose" in bc.claude_cmd("q", output="stream-json")


def test_parse_result_accepts_object_or_event_list():
    assert bc.parse_result('{"type": "result", "result": "A"}')["result"] == "A"
    events = [{"type": "system"}, {"type": "result", "result": "B"}]
    assert bc.parse_result(json.dumps(events))["result"] == "B"


def test_call_claude_raises_on_failure_and_returns_text():
    ok = SimpleNamespace(returncode=0, stdout='{"type":"result","result":"답","usage":{"input_tokens":5},"total_cost_usd":0.01}', stderr="")
    got = bc.call_claude("q", run=lambda *a, **k: ok)
    assert got["text"] == "답" and got["input_tokens"] == 5 and got["cost_usd"] == 0.01
    bad = SimpleNamespace(returncode=1, stdout="", stderr="boom")
    try:
        bc.call_claude("q", run=lambda *a, **k: bad)
    except RuntimeError as err:
        assert "boom" in str(err)
    else:
        raise AssertionError("RuntimeError가 나야 합니다")


def test_call_claude_runs_given_command():
    seen = []

    def run(cmd, **kwargs):
        seen.append(cmd)
        return SimpleNamespace(returncode=0, stdout='{"type":"result","result":"답"}', stderr="")

    assert bc.call_claude("q", run=run, cmd=["claude", "-p", "q", "--plugin-dir", "x"])["text"] == "답"
    assert seen[0][-2:] == ["--plugin-dir", "x"]


def test_meta_date_uses_dated_directory_or_today():
    assert bc.meta_date("evals/results/2026-10-09") == "2026-10-09"
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", bc.meta_date("evals/calibration/baseline"))


def test_isolation_problems_flags_leaks():
    clean = bc.init_summary(json.dumps({"type": "system", "subtype": "init", "mcp_servers": [],
                                        "plugins": [{"source": "cc-plugin-telemetry@builtin"}],
                                        "output_style": "default", "memory_paths": {"auto": "/x"}}))
    assert bc.isolation_problems(clean) == []
    leaky = bc.init_summary(json.dumps({"type": "system", "subtype": "init", "mcp_servers": [{"name": "slack"}],
                                        "plugins": [{"source": "x@market"}], "output_style": "simple-korean",
                                        "memory_paths": {"auto": "/x", "user": "/y"}}))
    assert len(bc.isolation_problems(leaky)) == 4
    assert bc.isolation_problems(bc.init_summary("")) == ["init 이벤트가 없습니다"]


def test_build_prompt_conditions():
    sc = {"id": "x", "type": "descriptive", "prompt": "과제 본문"}
    assert run_bench.build_prompt(sc, "baseline") == "과제 본문"
    plain = run_bench.build_prompt(sc, "plain")
    assert plain.startswith(run_bench.LEAD) and "## 답변" in plain and "과제: 과제 본문" in plain
    assert "name: simple-korean" not in plain
    strict = run_bench.build_prompt(sc, "strict")
    assert "엄격 모드: 문장 끝, 접속어, 단어" in strict and "과제: 엄격 모드로 쓰세요. 과제 본문" in strict


def test_generate_writes_and_resumes():
    calls = []

    def fake(prompt, **kwargs):
        calls.append(prompt)
        return {"text": "본문입니다.", "model": "m", "effort": "low"}

    with tempfile.TemporaryDirectory() as d:
        scenarios = [{"id": "a", "type": "descriptive", "prompt": "p"}]
        run_bench.generate(d, scenarios, 1, call=fake, sleep=0)
        assert len(calls) == 3 and len(list(Path(d, "docs").glob("*.json"))) == 3
        run_bench.generate(d, scenarios, 1, call=fake, sleep=0)
        assert len(calls) == 3


def test_generate_only_requested_conditions():
    calls = []

    def fake(prompt, **kwargs):
        calls.append(prompt)
        return {"text": "본문입니다.", "model": "m", "effort": "low"}

    with tempfile.TemporaryDirectory() as d:
        run_bench.generate(d, [{"id": "a", "type": "descriptive", "prompt": "p"}], 1,
                           call=fake, sleep=0, conditions=("baseline",))
        assert calls == ["p"]
        assert [p.name for p in Path(d, "docs").iterdir()] == ["baseline__a__r1.json"]
    with tempfile.TemporaryDirectory() as d:
        run_reply_bench.generate(d, [{"id": "q", "prompt": "질문"}], 1, call=fake, sleep=0, conditions=("baseline",))
        assert [p.name for p in Path(d, "reply").iterdir()] == ["baseline__q__r1.txt"]


def test_parse_conditions_rejects_unknown():
    assert bc.parse_conditions("baseline", ("baseline", "plain")) == ("baseline",)
    assert bc.parse_conditions(" plain , baseline ", ("baseline", "plain")) == ("plain", "baseline")
    for bad in ("", "skill", "baseline,skill"):
        try:
            bc.parse_conditions(bad, ("baseline", "plain"))
        except SystemExit as err:
            assert "baseline, plain" in str(err)
        else:
            raise AssertionError(bad)


def test_reply_generate_uses_rule_block_only_for_plain():
    seen = []

    def fake(prompt, system=None, **kwargs):
        seen.append(system)
        return {"text": "답입니다."}

    with tempfile.TemporaryDirectory() as d:
        run_reply_bench.generate(d, [{"id": "q", "prompt": "질문"}], 1, call=fake, sleep=0)
        assert seen[0] is None and "레포지토리" in seen[1]
        assert sorted(p.name for p in Path(d, "reply").iterdir()) == ["baseline__q__r1.txt", "plain__q__r1.txt"]


def test_judge_parsing_and_combination():
    assert run_reply_bench.parse_winner('{"winner": "B"}') == "B"
    assert run_reply_bench.parse_winner("모르겠습니다") is None
    assert run_reply_bench.combine("B", "A") == "plain"
    assert run_reply_bench.combine("A", "B") == "baseline"
    assert run_reply_bench.combine("B", "B") == "tie"
    assert run_reply_bench.combine(None, "A") == "tie"
    assert run_reply_bench.combine("tie", "tie") == "tie"


def _fake_results(d):
    root = Path(d)
    (root / "reply").mkdir()
    (root / "reply" / "baseline__q__r1.txt").write_text("**네** — 그렇습니다.\n- 하나\n- 둘\n", encoding="utf-8")
    (root / "reply" / "plain__q__r1.txt").write_text("빌드가 실패한 이유는 디스크입니다.", encoding="utf-8")
    (root / "judge").mkdir()
    (root / "judge" / "q__r1.json").write_text(json.dumps({"winner": "plain"}), encoding="utf-8")
    (root / "docs").mkdir()
    for cond, text in (("baseline", "메세지를 보냅니다. 서버에 대해 설명합니다."), ("plain", "메시지를 보냅니다."), ("strict", "메시지를 보냅니다.")):
        (root / "docs" / f"{cond}__readme-intro__r1.json").write_text(
            json.dumps({"condition": cond, "scenario": "readme-intro", "text": text}, ensure_ascii=False), encoding="utf-8")
    return root


def test_report_tables_from_fake_results():
    with tempfile.TemporaryDirectory() as d:
        root = _fake_results(d)
        replies = report.reply_stats(root)
        assert replies["baseline"]["visible"] == 4 and replies["plain"]["visible"] == 0
        assert report.judge_stats(root) == {"plain": 1, "tie": 0, "baseline": 0, "n": 1}
        headline = report.render_headline(replies, report.judge_stats(root))
        assert "100% 줄었습니다(4개에서 0개)" in headline and "1쌍 가운데 1쌍에서 이겼고" in headline
        docs = report.doc_stats(root, [{"id": "readme-intro", "type": "descriptive"}])
        assert docs["baseline"]["errors"] == 1 and docs["baseline"]["translationese"] == 1
        table = report.render_doc_table(docs)
        assert table.splitlines()[2].startswith("| 스킬 없음 | 1 |")
        dist = report.spelling_distribution(root)
        assert dict(dist["message"]["baseline"]) == {"메세지": 1}
        assert "| message | 메세지 1 | 메시지 1 | 메시지 1 |" in report.render_spelling_table(dist)


def test_readme_block_fills_an_empty_template_block():
    readme = "앞\n<!-- benchmark:start evals/results/YYYY-MM-DD -->\n\n<!-- benchmark:end -->\n"
    with tempfile.TemporaryDirectory(dir=str(report.ROOT / "evals")) as d:
        new = report.replace_readme_block(readme, d, "표")
    assert "-->\n표\n<!-- benchmark:end -->" in new and "YYYY" not in new


def test_readme_block_round_trip():
    readme = "앞\n<!-- benchmark:start evals/results/old -->\n옛 내용\n<!-- benchmark:end -->\n뒤\n"
    with tempfile.TemporaryDirectory(dir=str(report.ROOT / "evals")) as d:
        new = report.replace_readme_block(readme, d, "새 내용")
        rel = Path(d).resolve().relative_to(report.ROOT).as_posix()
        assert f"<!-- benchmark:start {rel} -->\n새 내용\n<!-- benchmark:end -->" in new
        assert new.startswith("앞\n") and new.endswith("뒤\n")
```

- [ ] **Step 2: 테스트를 돌려 실패를 확인한다**

Run: `python3 evals/tests/run.py evals/tests/test_bench.py`
Expected: `ModuleNotFoundError: No module named 'bench_common'`로 실패한다.

- [ ] **Step 3: 시나리오를 쓴다**

`evals/scenarios.json`(원본 sqlpipe 과제를 한국어로 옮겼다. 분량은 영어 단어 수의 약 2.5배 글자 수로 바꿨다):

```json
[
  {"id": "readme-intro", "type": "descriptive", "prompt": "Postgres 테이블을 Parquet 파일로 S3에 동기화하는 CLI 도구 sqlpipe의 README 소개 부분을 써 주세요. 한두 문단, 300자 안팎으로 쓰세요. 본문만 답하세요."},
  {"id": "getting-started", "type": "procedural", "prompt": "CLI 도구 sqlpipe의 '시작하기' 문서 절을 써 주세요. 설치는 `curl -sSL https://get.sqlpipe.dev | sh`, 설정 파일은 sqlpipe.yaml, 첫 실행은 `sqlpipe run --config sqlpipe.yaml`입니다. 400자 안팎으로 쓰세요. 본문만 답하세요."},
  {"id": "troubleshooting", "type": "procedural", "prompt": "CLI 도구 sqlpipe의 문제 해결 절을 써 주세요. Postgres 연결 타임아웃과 S3 권한 오류를 다루세요. 400자 안팎으로 쓰세요. 본문만 답하세요."},
  {"id": "error-message", "type": "procedural", "prompt": "IAM 자격 증명에 s3:PutObject 권한이 없어서 S3 업로드가 AccessDenied로 실패할 때 sqlpipe가 출력하는 오류 메시지 문구를 써 주세요. 두 줄에서 네 줄로 쓰세요. 메시지 문구만 답하세요."},
  {"id": "incident-report", "type": "descriptive", "prompt": "공개 상태 페이지에 올릴 장애 보고를 써 주세요. 14:02부터 14:31(UTC)까지 API 요청의 12%가 HTTP 502로 실패했습니다. 배포에서 캐시 예열 단계가 빠졌고, 14:27에 배포를 되돌렸습니다. 250자 안팎으로 쓰세요. 본문만 답하세요."},
  {"id": "release-notes", "type": "descriptive", "prompt": "sqlpipe v2.0 릴리스 노트를 써 주세요. /v2/users의 `name` 필드가 `first_name`과 `last_name`으로 나뉘었습니다(호환성 깨짐). `--incremental` 플래그가 새로 생겼고, Parquet 쓰기가 40% 빨라졌습니다. 300자 안팎으로 쓰세요. 본문만 답하세요."},
  {"id": "runbook-terse", "type": "procedural", "prompt": "이 런북 단계를 최대한 짧게 다시 써 주세요: '마이그레이션을 실행하기 전에 백업이 존재하는지 반드시 확인해야 합니다.' 고친 단계만 답하세요."},
  {"id": "architecture", "type": "descriptive", "prompt": "sqlpipe의 아키텍처 개요를 써 주세요. 리더 프로세스가 Postgres 행을 배치 단위로 스트리밍하고, 컨버터가 배치를 Parquet 로우 그룹으로 바꾸고, 업로더가 재시도와 함께 S3에 멀티파트 객체를 씁니다. 330자 안팎으로 쓰세요. 본문만 답하세요."}
]
```

`evals/reply_scenarios.json`(질문마다 전문용어가 하나씩 있다. 사용자의 구어 표기는 일부러 그대로 둔다):

```json
[
  {"id": "why-timeout", "term": "멱등성", "prompt": "배포 스크립트가 타임아웃이 나면 /v2/orders에 POST를 다시 보냅니다. 안전한가요? 엔드포인트가 멱등하다는데 정확히 무슨 뜻인지 모르겠어요. 짧게 설명해 주세요."},
  {"id": "pick-db", "term": "샤딩", "prompt": "Postgres 테이블 하나에 행이 4천만 개 있고 읽기가 느립니다. 누가 샤딩 얘기를 하던데, 먼저 뭘 해야 하나요?"},
  {"id": "cert-error", "term": "TLS", "prompt": "사내 API에 curl을 보내면 'SSL certificate problem: unable to get local issuer certificate'가 나옵니다. 무슨 일이고 어떻게 고치나요?"},
  {"id": "queue-lag", "term": "컨슈머 랙", "prompt": "Kafka 대시보드에서 컨슈머 랙이 200만까지 올라갑니다. 나쁜 건가요? 사용자에게는 무슨 뜻인가요?"},
  {"id": "oom", "term": "OOMKilled", "prompt": "쿠버네티스 파드가 OOMKilled 상태로 계속 재시작됩니다. 무슨 일이 일어나는 건지, 뭘 바꿔야 하는지 설명해 주세요."},
  {"id": "rate-limit", "term": "토큰 버킷", "prompt": "API를 사용자당 분당 100회로 제한하려고 합니다. 동료가 토큰 버킷을 추천했는데, 쉽게 설명해 주고 맞는 방법인지 알려 주세요."},
  {"id": "migration", "term": "백필", "prompt": "20GB 테이블에 NOT NULL 컬럼을 추가했더니 마이그레이션이 멈췄어요. DBA가 백필이 필요하다는데, 그게 뭐고 뭘 해야 하나요?"},
  {"id": "cache", "term": "캐시 무효화", "prompt": "가격을 바꾸면 사용자가 최대 10분 동안 예전 가격을 봅니다. DB 앞에 Redis를 두고 있어요. 왜 그렇고 어떻게 고치나요?"}
]
```

- [ ] **Step 4: 실행기와 집계 모듈을 쓴다**

`evals/bench_common.py`:

```python
#!/usr/bin/env python3
"""벤치마크 스크립트가 함께 쓰는 claude 호출 도구.

claude -p를 격리해서 부른다. 사용자·프로젝트 설정과 MCP 서버를 읽지 않고, 도구를 끄고, 빈 임시
디렉터리에서 돌린다. 내장 플러그인(*@builtin)은 끌 수 없지만 모든 조건에 똑같이 들어간다.

    python3 evals/bench_common.py --probe --out evals/results/<날짜>   # 격리를 확인하고 meta.json을 쓴다
"""
import argparse
import json
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
MODEL = "claude-sonnet-5-5"
JUDGE_MODEL = "claude-opus-5-5"
EFFORT = "low"
DISALLOWED = "Bash,Read,Write,Edit,Glob,Grep,WebFetch,WebSearch,NotebookEdit"
BUILTIN_SUFFIX = "@builtin"


def claude_cmd(prompt, model=MODEL, effort=EFFORT, system=None, output="json"):
    """격리된 claude -p 명령 목록."""
    cmd = ["claude", "-p", prompt, "--model", model, "--effort", effort,
           "--setting-sources", "", "--strict-mcp-config",
           "--disallowedTools", DISALLOWED, "--output-format", output]
    if output == "stream-json":
        cmd.append("--verbose")
    if system:
        cmd += ["--append-system-prompt", system]
    return cmd


def parse_result(stdout):
    """--output-format json 출력에서 result 이벤트를 꺼낸다. 객체 하나이거나 이벤트 목록이다."""
    data = json.loads(stdout)
    if isinstance(data, list):
        data = next(e for e in data if isinstance(e, dict) and e.get("type") == "result")
    return data


def call_claude(prompt, model=MODEL, effort=EFFORT, system=None, timeout=600, run=subprocess.run, cmd=None):
    """claude를 한 번 부르고 text, 사용량, 비용을 돌려준다. cmd를 주면 그 명령을 그대로 쓴다.

    실패하면 RuntimeError를 낸다.
    """
    started = time.time()
    with tempfile.TemporaryDirectory(prefix="simple-korean-bench-") as cwd:
        proc = run(cmd or claude_cmd(prompt, model, effort, system), capture_output=True, text=True,
                   timeout=timeout, cwd=cwd, stdin=subprocess.DEVNULL)
    if proc.returncode != 0:
        raise RuntimeError(f"{model}: {proc.stderr[:300]}")
    env = parse_result(proc.stdout)
    if env.get("is_error"):
        raise RuntimeError(f"{model}: {str(env.get('result'))[:300]}")
    usage = env.get("usage") or {}
    return {"text": env.get("result", ""), "model": model, "effort": effort,
            "input_tokens": usage.get("input_tokens"), "output_tokens": usage.get("output_tokens"),
            "cost_usd": env.get("total_cost_usd"),
            "duration_ms": env.get("duration_ms", int(1000 * (time.time() - started)))}


def init_summary(stream_stdout):
    """stream-json 출력의 init 이벤트를 요약한다."""
    init = {}
    for line in stream_stdout.splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if event.get("type") == "system" and event.get("subtype") == "init":
            init = event
    return {
        "found": bool(init),
        "claude_code_version": init.get("claude_code_version"),
        "model": init.get("model"),
        "mcp_servers": [m.get("name") for m in init.get("mcp_servers") or []],
        "plugins": [p.get("source", p.get("name", "")) for p in init.get("plugins") or []],
        "output_style": init.get("output_style"),
        "memory_paths": sorted((init.get("memory_paths") or {}).keys()),
    }


def isolation_problems(summary):
    """격리가 깨진 곳을 사람이 읽을 문장 목록으로 돌려준다. 비어 있으면 깨끗하다."""
    problems = []
    if not summary["found"]:
        problems.append("init 이벤트가 없습니다")
    if summary["mcp_servers"]:
        problems.append(f"MCP 서버가 섞였습니다: {summary['mcp_servers']}")
    outside = [p for p in summary["plugins"] if not p.endswith(BUILTIN_SUFFIX)]
    if outside:
        problems.append(f"내장이 아닌 플러그인이 섞였습니다: {outside}")
    if summary["output_style"] not in (None, "default"):
        problems.append(f"출력 스타일이 기본이 아닙니다: {summary['output_style']}")
    if set(summary["memory_paths"]) - {"auto"}:
        problems.append(f"메모리 파일이 섞였습니다: {summary['memory_paths']}")
    return problems


def probe(model=MODEL, run=subprocess.run):
    """격리 상태를 한 번 확인하고 (요약, 문제 목록)을 돌려준다."""
    with tempfile.TemporaryDirectory(prefix="simple-korean-probe-") as cwd:
        proc = run(claude_cmd("Reply with exactly: OK", model, EFFORT, output="stream-json"),
                   capture_output=True, text=True, timeout=300, cwd=cwd, stdin=subprocess.DEVNULL)
    summary = init_summary(proc.stdout)
    return summary, isolation_problems(summary)


def parse_conditions(value, allowed):
    """쉼표로 나눈 조건 목록을 검사해 튜플로 돌려준다. 모르는 조건이 있으면 멈춘다."""
    chosen = tuple(c.strip() for c in value.split(",") if c.strip())
    if not chosen or any(c not in allowed for c in chosen):
        raise SystemExit(f"조건은 {', '.join(allowed)} 가운데에서 고르세요: {value!r}")
    return chosen


def rule_block(text):
    """첫 번째와 두 번째 --- 줄 사이의 규칙 블록. 없으면 본문 전체."""
    parts = re.split(r"^---[ \t]*$", text, flags=re.M)
    return parts[1].strip() if len(parts) >= 3 else text.strip()


def skill_body(path):
    """마크다운 파일에서 frontmatter를 뗀 본문."""
    text = Path(path).read_text(encoding="utf-8")
    return re.sub(r"\A---\n.*?\n---\n", "", text, count=1, flags=re.S).strip()


def meta_date(out):
    """결과 디렉터리 이름이 날짜(YYYY-MM-DD)면 그 날짜, 아니면 오늘 날짜."""
    name = Path(out).name
    return name if re.fullmatch(r"\d{4}-\d{2}-\d{2}", name) else time.strftime("%Y-%m-%d")


def write_meta(out, summary, problems, date):
    meta = {"date": date, "model": MODEL, "judge_model": JUDGE_MODEL, "effort": EFFORT,
            "isolation": summary, "isolation_problems": problems}
    Path(out).mkdir(parents=True, exist_ok=True)
    Path(out, "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return meta


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    if not a.probe:
        ap.error("--probe만 지원합니다")
    summary, problems = probe()
    write_meta(a.out, summary, problems, meta_date(a.out))
    print(json.dumps({"isolation": summary, "problems": problems}, ensure_ascii=False, indent=2))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
```

`evals/run_bench.py`:

```python
#!/usr/bin/env python3
"""문서 벤치마크. 과제 8개를 기준선, 기본 모드, 엄격 모드로 쓰게 하고 원본 출력을 저장한다.

이미 있는 원본 파일은 건너뛰므로 중간에 멈춰도 다시 이어서 돌릴 수 있다.

    python3 evals/run_bench.py --out evals/results/<날짜> [--runs 2] [--conditions baseline,plain,strict] [--smoke]
"""
import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bench_common as bc  # noqa: E402

CONDITIONS = ("baseline", "plain", "strict")
SKILL = bc.ROOT / "skills" / "simple-korean" / "SKILL.md"
STRICT = bc.ROOT / "skills" / "simple-korean" / "references" / "strict-mode.md"
LEAD = "다음 글쓰기 지침을 자가 점검 단계까지 정확히 따르세요.\n\n"
TAIL = "\n\n규칙 설명 없이 최종 글만 쓰세요."


def build_prompt(scenario, condition):
    """조건에 맞는 프롬프트. 기준선은 과제만, 기본 모드는 SKILL.md 본문을, 엄격 모드는 strict-mode.md까지 붙인다."""
    if condition == "baseline":
        return scenario["prompt"]
    rules = bc.skill_body(SKILL)
    task = scenario["prompt"]
    if condition == "strict":
        rules = rules + "\n\n" + bc.skill_body(STRICT)
        task = "엄격 모드로 쓰세요. " + task
    return LEAD + rules + "\n\n---\n\n과제: " + task + TAIL


def generate(out, scenarios, runs, call=bc.call_claude, sleep=2.0, conditions=CONDITIONS):
    """조건 × 과제 × 회차의 원본 출력을 out/docs/에 JSON으로 쓴다. 있는 파일은 건너뛴다."""
    docs = Path(out) / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    todo = [(c, s, r) for r in range(1, runs + 1) for c in conditions for s in scenarios]
    for i, (cond, sc, run) in enumerate(todo, 1):
        path = docs / f"{cond}__{sc['id']}__r{run}.json"
        if path.exists():
            continue
        print(f"[{i}/{len(todo)}] {cond} {sc['id']} r{run}", flush=True)
        try:
            res = call(build_prompt(sc, cond))
        except Exception as err:  # noqa: BLE001  하나가 실패해도 나머지는 돈다
            print(f"  실패: {err}", flush=True)
            continue
        record = {**res, "condition": cond, "scenario": sc["id"], "type": sc["type"], "run": run}
        path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        time.sleep(sleep)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--runs", type=int, default=2)
    ap.add_argument("--conditions", default=",".join(CONDITIONS), help="쉼표로 나눈 조건 목록")
    ap.add_argument("--smoke", action="store_true", help="과제 2개를 1회만 돈다")
    a = ap.parse_args(argv)
    conditions = bc.parse_conditions(a.conditions, CONDITIONS)
    scenarios = json.loads((bc.HERE / "scenarios.json").read_text(encoding="utf-8"))
    runs = 1 if a.smoke else a.runs
    generate(a.out, scenarios[:2] if a.smoke else scenarios, runs, conditions=conditions)
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

`evals/run_reply_bench.py`:

```python
#!/usr/bin/env python3
"""답변 벤치마크와 블라인드 판정.

기준선과 SimpleKorean(규칙 블록을 시스템 프롬프트에 붙임)으로 질문 8개에 답하게 하고, 판정 모델이
두 답변을 순서를 바꿔 두 번 비교한다. 이미 있는 파일은 건너뛴다.

    python3 evals/run_reply_bench.py --out evals/results/<날짜> [--runs 2] [--conditions baseline,plain]
    python3 evals/run_reply_bench.py --out evals/results/<날짜> [--runs 2] --judge
"""
import argparse
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bench_common as bc  # noqa: E402

CONDITIONS = ("baseline", "plain")
SYSTEM_PROMPT = bc.ROOT / "prompts" / "system-prompt.md"
JUDGE_PROMPT = (
    "아래는 같은 질문에 대한 두 답변 A와 B입니다. 이 분야를 모르는 독자가 한 번 읽고 정확히 이해할 수 있는 "
    "답변을 고르세요. 서식이 아니라 이해하기 쉬운지와 내용이 정확한지를 보세요. 다른 말 없이 JSON 한 줄로만 "
    '답하세요. {{"winner": "A"}}, {{"winner": "B"}}, {{"winner": "tie"}} 가운데 하나입니다.\n\n'
    "질문:\n{question}\n\n답변 A:\n{a}\n\n답변 B:\n{b}")


def generate(out, scenarios, runs, call=bc.call_claude, sleep=2.0, conditions=CONDITIONS):
    """조건 × 질문 × 회차의 답변을 out/reply/<조건>__<id>__r<회차>.txt로 쓴다."""
    system = bc.rule_block(SYSTEM_PROMPT.read_text(encoding="utf-8"))
    reply = Path(out) / "reply"
    reply.mkdir(parents=True, exist_ok=True)
    for run in range(1, runs + 1):
        for cond in conditions:
            for sc in scenarios:
                path = reply / f"{cond}__{sc['id']}__r{run}.txt"
                if path.exists() and path.read_text(encoding="utf-8").strip():
                    continue
                print(f"{cond} {sc['id']} r{run}", flush=True)
                try:
                    res = call(sc["prompt"], system=system if cond == "plain" else None)
                except Exception as err:  # noqa: BLE001
                    print(f"  실패: {err}", flush=True)
                    continue
                path.write_text(res["text"], encoding="utf-8")
                time.sleep(sleep)


def parse_winner(text):
    """판정 출력에서 A, B, tie 가운데 하나를 꺼낸다. 못 읽으면 None."""
    m = re.search(r'"winner"\s*:\s*"(A|B|tie)"', text or "")
    return m.group(1) if m else None


def combine(first, second):
    """두 순서의 판정을 합친다. 첫째는 A=기준선, 둘째는 A=SimpleKorean이다. 두 번 모두 같은 쪽이면 그쪽, 아니면 tie."""
    pick1 = {"A": "baseline", "B": "plain"}.get(first, "tie")
    pick2 = {"A": "plain", "B": "baseline"}.get(second, "tie")
    return pick1 if pick1 == pick2 else "tie"


def judge(out, scenarios, runs, call=bc.call_claude):
    """답변 쌍마다 판정을 out/judge/<id>__r<회차>.json으로 쓴다."""
    jdir, reply = Path(out) / "judge", Path(out) / "reply"
    jdir.mkdir(parents=True, exist_ok=True)
    for run in range(1, runs + 1):
        for sc in scenarios:
            path = jdir / f"{sc['id']}__r{run}.json"
            base_p, plain_p = reply / f"baseline__{sc['id']}__r{run}.txt", reply / f"plain__{sc['id']}__r{run}.txt"
            if path.exists() or not (base_p.exists() and plain_p.exists()):
                continue
            base, plain = base_p.read_text(encoding="utf-8"), plain_p.read_text(encoding="utf-8")
            ask = lambda a, b: parse_winner(call(JUDGE_PROMPT.format(question=sc["prompt"], a=a, b=b), model=bc.JUDGE_MODEL)["text"])  # noqa: E731
            first, second = ask(base, plain), ask(plain, base)
            record = {"scenario": sc["id"], "run": run, "judge_model": bc.JUDGE_MODEL,
                      "order1_baseline_first": first, "order2_plain_first": second, "winner": combine(first, second)}
            path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(f"판정 {sc['id']} r{run}: {record['winner']}", flush=True)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--runs", type=int, default=2)
    ap.add_argument("--conditions", default=",".join(CONDITIONS), help="쉼표로 나눈 조건 목록")
    ap.add_argument("--judge", action="store_true")
    a = ap.parse_args(argv)
    conditions = bc.parse_conditions(a.conditions, CONDITIONS)
    scenarios = json.loads((bc.HERE / "reply_scenarios.json").read_text(encoding="utf-8"))
    if a.judge:
        judge(a.out, scenarios, a.runs)
    else:
        generate(a.out, scenarios, a.runs, conditions=conditions)
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

`evals/report.py`:

```python
#!/usr/bin/env python3
"""측정 결과를 모으고 표를 그린다. RESULTS.md, README, check_numbers.py가 같은 함수를 쓴다.

수치는 언제나 원본 출력에서 다시 계산한다. 저장된 점수 파일은 쓰지 않는다.

    python3 evals/report.py evals/results/<날짜>            # RESULTS.md를 쓰고 README 블록을 출력한다
    python3 evals/report.py evals/results/<날짜> --readme   # README.md의 벤치마크 블록도 바꾼다
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import ko_lint  # noqa: E402
import ko_terms  # noqa: E402
import ko_text  # noqa: E402
import metrics  # noqa: E402

REPLY_CONDS = ("baseline", "plain")
DOC_CONDS = ("baseline", "plain", "strict")
REPLY_LABELS = {"baseline": "스킬 없음", "plain": "SimpleKorean"}
DOC_LABELS = {"baseline": "스킬 없음", "plain": "기본 모드", "strict": "엄격 모드"}
README_BLOCK = re.compile(r"<!-- benchmark:start (\S+) -->\n(.*?)\n<!-- benchmark:end -->", re.S)


def reply_stats(results_dir):
    """조건별 답변 합계: n, eojeol, sentences, em_dash, bold_spans, headers, bullets, fillers, visible."""
    stats = {c: Counter() for c in REPLY_CONDS}
    for path in sorted(Path(results_dir, "reply").glob("*__*__r*.txt")):
        cond = path.name.split("__")[0]
        rc = ko_lint.reader_check(path.read_text(encoding="utf-8"))
        acc = stats[cond]
        acc["n"] += 1
        acc["eojeol"] += rc["eojeol"]
        for key in ("sentences", "em_dash", "bold_spans", "headers", "bullets"):
            acc[key] += rc["counts"][key]
        acc["fillers"] += rc["counts"]["opener"] + rc["counts"]["closer"]
        acc["visible"] += rc["visible_total"]
    return {c: dict(v) for c, v in stats.items()}


def judge_stats(results_dir):
    """판정 결과: plain(SimpleKorean 승), tie, baseline(기준선 승), n."""
    tally = Counter(json.loads(p.read_text(encoding="utf-8"))["winner"]
                    for p in sorted(Path(results_dir, "judge").glob("*.json")))
    return {"plain": tally["plain"], "tie": tally["tie"], "baseline": tally["baseline"], "n": sum(tally.values())}


def doc_stats(results_dir, scenarios):
    """조건별 문서 합계. 모든 조건을 같은 기준(기본 모드 린터, 기본 단어 목록)으로 잰다."""
    types = {s["id"]: s["type"] for s in scenarios}
    concepts = ko_terms.load_terms()
    stats = {c: Counter() for c in DOC_CONDS}
    for path in sorted(Path(results_dir, "docs").glob("*.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        text, acc = record["text"], stats[record["condition"]]
        report = ko_lint.lint(text, types[record["scenario"]], config={})
        acc["n"] += 1
        acc["eojeol"] += report["eojeol"]
        acc["errors"] += report["errors_total"]
        acc["warnings"] += report["warnings_total"]
        acc["translationese"] += report["violations"].get("translationese", 0)
        acc["longest"] = max(acc["longest"], report["longest_sentence_eojeol"])
        occurrences = ko_terms.scan(ko_text.mask(ko_text.nfc(text)), concepts)
        acc["terms"] += len(occurrences)
        acc["designated"] += sum(1 for o in occurrences if o.role in ("write", "alias"))
        easy = metrics.easy_word_counts(text)
        if easy is not None:
            acc["easy"] += easy[0]
            acc["content"] += easy[1]
    return {c: dict(v) for c, v in stats.items()}


def spelling_distribution(results_dir):
    """{개념: {조건: Counter(형태)}}. 스킬이 만든 표기 변화를 따로 보기 위한 표의 재료다."""
    concepts = ko_terms.load_terms()
    dist = {}
    for path in sorted(Path(results_dir, "docs").glob("*.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        for o in ko_terms.scan(ko_text.mask(ko_text.nfc(record["text"])), concepts):
            dist.setdefault(o.concept, {}).setdefault(record["condition"], Counter())[o.form] += 1
    return dist


def _pct(part, whole):
    return f"{100 * part / whole:.1f}%" if whole else "측정 안 함"


def render_reply_table(stats):
    lines = ["| 조건 | 답변 수 | 평균 어절 | 평균 문장 | em-dash | 굵은 글씨 | 헤더 | 불릿 | 인사말과 맺음말 |",
             "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for cond in REPLY_CONDS:
        s = Counter(stats[cond])
        n = max(1, s["n"])
        lines.append(f"| {REPLY_LABELS[cond]} | {s['n']} | {s['eojeol'] / n:.0f} | {s['sentences'] / n:.1f} | "
                     f"{s['em_dash']} | {s['bold_spans']} | {s['headers']} | {s['bullets']} | {s['fillers']} |")
    return "\n".join(lines)


def render_doc_table(stats):
    lines = ["| 조건 | 문서 수 | 100어절당 오류 | 100어절당 경고 | 100어절당 번역투 | 지정 표기 비율 | 쉬운 단어 비율 | 가장 긴 문장 |",
             "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for cond in DOC_CONDS:
        s = Counter(stats[cond])
        w = max(1, s["eojeol"])
        lines.append(f"| {DOC_LABELS[cond]} | {s['n']} | {100 * s['errors'] / w:.2f} | {100 * s['warnings'] / w:.2f} | "
                     f"{100 * s['translationese'] / w:.2f} | {_pct(s['designated'], s['terms'])} | "
                     f"{_pct(s['easy'], s['content'])} | {s['longest']}어절 |")
    return "\n".join(lines)


def render_headline(stats, judge):
    base, plain = stats["baseline"].get("visible", 0), stats["plain"].get("visible", 0)
    cut = round(100 * (base - plain) / base) if base else 0
    return (f"스킬을 켜면 독자가 보는 결함(em-dash, 굵은 글씨, 헤더, 불릿)이 {cut}% 줄었습니다({base}개에서 {plain}개). "
            f"블라인드 판정에서 SimpleKorean 답변은 {judge['n']}쌍 가운데 {judge['plain']}쌍에서 이겼고, "
            f"{judge['tie']}쌍에서 비겼고, {judge['baseline']}쌍에서 졌습니다.")


def render_spelling_table(dist):
    lines = ["| 개념 | 스킬 없음 | 기본 모드 | 엄격 모드 |", "|---|---|---|---|"]
    order = sorted(dist, key=lambda cid: (-sum(sum(c.values()) for c in dist[cid].values()), cid))
    for cid in order:
        cells = [", ".join(f"{form} {n}" for form, n in sorted(dist[cid].get(c, Counter()).items(), key=lambda x: (-x[1], x[0]))) or "0"
                 for c in DOC_CONDS]
        lines.append(f"| {cid} | " + " | ".join(cells) + " |")
    return "\n".join(lines)


def _shape(results_dir, sub, pattern):
    """원본 파일 이름에서 (과제 수, 회차 수)를 센다. 파일 이름은 <조건>__<id>__r<회차>.<확장자>다."""
    names = [p.name.rsplit(".", 1)[0].split("__") for p in Path(results_dir, sub).glob(pattern)]
    ids = {n[1] for n in names if len(n) == 3}
    runs = {n[2] for n in names if len(n) == 3}
    return len(ids), len(runs)


def readme_block(results_dir, scenarios):
    """README의 벤치마크 블록 본문. check_numbers.py가 README와 글자 하나까지 대조한다."""
    rel = Path(results_dir).resolve().relative_to(ROOT).as_posix()
    replies, judge, docs = reply_stats(results_dir), judge_stats(results_dir), doc_stats(results_dir, scenarios)
    n_reply = replies["plain"].get("n", 0) + replies["baseline"].get("n", 0)
    questions, reply_runs = _shape(results_dir, "reply", "*.txt")
    tasks, doc_runs = _shape(results_dir, "docs", "*.json")
    return "\n\n".join([
        f"답변: 전문용어가 하나씩 든 질문 {questions}개를 조건마다 {reply_runs}번씩 물었습니다. 답변은 모두 {n_reply}개입니다. "
        + render_headline(replies, judge),
        render_reply_table(replies),
        f"문서: sqlpipe 문서 과제 {tasks}개를 조건마다 {doc_runs}번씩 썼습니다. 비율은 린터가 센 수를 어절 수로 나눈 값입니다. "
        "린터는 정규식 검사이므로 순위로 읽지 말고 방향으로 읽으세요.",
        render_doc_table(docs),
        f"원본 출력, 표기 분포, 측정 조건은 [`{rel}/RESULTS.md`]({rel}/RESULTS.md)에 있습니다.",
    ])


def results_md(results_dir, scenarios):
    """RESULTS.md 전체. meta.json의 격리 확인 결과를 함께 싣는다."""
    meta = json.loads(Path(results_dir, "meta.json").read_text(encoding="utf-8"))
    iso = meta["isolation"]
    return "\n\n".join([
        f"# 측정 결과 ({meta['date']})",
        f"모델은 `{meta['model']}`, effort는 `{meta['effort']}`, 판정 모델은 `{meta['judge_model']}`입니다. "
        f"Claude Code {iso['claude_code_version']}에서 `--setting-sources \"\" --strict-mcp-config`로 돌렸습니다.",
        f"격리 확인: MCP 서버 {len(iso['mcp_servers'])}개, 플러그인 {', '.join(iso['plugins']) or '없음'}, "
        f"출력 스타일 `{iso['output_style']}`, 문제 {len(meta['isolation_problems'])}건.",
        "## README 블록",
        readme_block(results_dir, scenarios),
        "## 표기 분포",
        "기본 단어 목록으로 센 개념별 표기 수입니다. 스킬이 만든 표기 변화를 사람의 관행과 따로 보려고 싣습니다.",
        "<!-- simple-korean: off -->\n" + render_spelling_table(spelling_distribution(results_dir)) + "\n<!-- simple-korean: on -->",
        "## 수치를 읽을 때 주의할 점",
        "- 린터는 정규식 검사입니다. 형태소 분석을 하지 않아 거짓 일치와 놓침이 있습니다. 모든 조건을 같은 린터로 쟀습니다.\n"
        "- 쉬운 단어 비율은 kiwipiepy 0.24.0으로 뽑은 내용어 가운데 국어 기초 어휘 1등급 표제어의 비율입니다.\n"
        "- 판정 모델도 Claude라서 같은 계열에 유리한 편향이 있을 수 있습니다.\n"
        "- 조건마다 두 번씩만 돌렸습니다. 한 번 실행의 편차를 감안하세요.",
        "다시 계산하려면 `python3 evals/report.py " + Path(results_dir).resolve().relative_to(ROOT).as_posix() + "`를 실행하세요.",
    ]) + "\n"


def replace_readme_block(readme_text, results_dir, block):
    """README의 벤치마크 블록을 새 결과 디렉터리와 본문으로 바꾼 새 문자열."""
    rel = Path(results_dir).resolve().relative_to(ROOT).as_posix()
    new = f"<!-- benchmark:start {rel} -->\n{block}\n<!-- benchmark:end -->"
    if not README_BLOCK.search(readme_text):
        raise SystemExit("README.md에 <!-- benchmark:start ... --> 블록이 없습니다")
    return README_BLOCK.sub(lambda m: new, readme_text, count=1)


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if not args:
        raise SystemExit("사용법: report.py <결과 디렉터리> [--readme]")
    results_dir = Path(args[0])
    scenarios = json.loads((HERE / "scenarios.json").read_text(encoding="utf-8"))
    Path(results_dir, "RESULTS.md").write_text(results_md(results_dir, scenarios), encoding="utf-8")
    block = readme_block(results_dir, scenarios)
    print(block)
    if "--readme" in args:
        readme = ROOT / "README.md"
        readme.write_text(replace_readme_block(readme.read_text(encoding="utf-8"), results_dir, block), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 5: 테스트를 돌려 통과를 확인한다**

Run: `chmod +x evals/bench_common.py evals/run_bench.py evals/run_reply_bench.py evals/report.py && python3 evals/tests/run.py && /usr/bin/python3 evals/tests/run.py`
Expected: 두 번 모두 `ok` 86줄, 종료 코드 0.

- [ ] **Step 6: 격리를 실제로 확인한다**

이 단계는 `claude -p`를 한 번 부른다(약 $0.02).

Run: `python3 evals/bench_common.py --probe --out "$SCRATCH/probe-check"; echo "exit=$?"`
Expected: `"problems": []`, `exit=0`. 문제가 있으면 측정하지 않는다. 문제 목록을 사용자에게 보이고 격리 옵션을 정한 뒤 계속한다.

- [ ] **Step 7: 커밋한다**

```bash
git add evals/scenarios.json evals/reply_scenarios.json evals/bench_common.py evals/run_bench.py evals/run_reply_bench.py evals/report.py evals/tests/test_bench.py
git commit -m "feat: add isolated doc and reply benchmarks with blind judge" -m $'Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01SanRSLxxVtkLMJh1wLGeGZ'
```

### Task 15: 보정

스펙 11.1의 1단계다. 기준선 출력에서 린터가 잡은 것을 모두 읽고 거짓 일치를 고친다. 문장 길이 상한은 이 Task에서만 바꿀 수 있다(Global Constraints).

**Files:**
- Create: `evals/calibration/compliant-ko.md`, `evals/calibration/hits.py`
- Create(생성물): `evals/calibration/baseline/`(기준선 문서 8개, 답변 8개, `meta.json`), `evals/calibration/hits.tsv`(판정), `evals/calibration/RECORD.md`
- Modify(거짓 일치가 나온 범주만, Step 7의 표를 따른다): `evals/ko_rules.py`, `evals/ko_terms.py`, `evals/ko_text.py`, `evals/ko_lint.py`, `data/terms.json`, `tools/slop-lexicon/exclusions.tsv`, `evals/slop.tsv`
- Test: `evals/tests/test_calibration.py`, 거짓 일치마다 그 범주의 시험 파일

**Interfaces:**
- Consumes: Task 6의 `ko_lint.lint_detail(text, text_type, strict, config)`, `ko_lint.OPENER`, `ko_lint.CLOSER`, `ko_lint.LABELS`, Task 3~4의 `ko_rules.LIMITS`, `ko_rules.SLOP_RX`, Task 1~2의 `ko_text.nfc`, `mask`, `strip_frontmatter`, `units`, `eojeol_count`, `sentence_kind`, Task 14의 `bench_common.py --probe`, `run_bench.py --conditions`, `run_reply_bench.py --conditions`
- Produces: `hits.COLUMNS`(`file, line, mode, category, severity, match, context, label, note`), `hits.doc_rows(results_dir)`, `hits.reply_rows(results_dir)`, `hits.to_tsv(rows) -> str`, `hits.read_tsv(path) -> list[dict]`, `hits.key(row)`, `hits.check_labels(labeled, current) -> list[str]`, `hits.precision_table(labeled, current)`, `hits.length_stats(texts)`, `hits.decide_limits(limits, compliant, baseline) -> (dict, dict)`, `hits.changelog_lines(table, labeled, decided, limits=None) -> list[str]`, `hits.record_md(results_dir, labeled) -> str`(판정이 빠졌거나 hits.tsv에 없는 일치가 있으면 SystemExit). RECORD.md의 `## CHANGELOG에 옮길 줄` 절은 Task 19가 CHANGELOG에 옮기고 Task 18의 수치 검증이 대조한다.

- [ ] **Step 1: 실패하는 테스트를 쓴다**

`evals/tests/test_calibration.py`:

```python
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent / "calibration"))
import hits  # noqa: E402
import ko_lint  # noqa: E402
import ko_text  # noqa: E402

COMPLIANT = HERE.parent / "calibration" / "compliant-ko.md"
DOC = "이 문서는 sqlpipe에 대해 설명합니다. 설정 파일이나 환경 변수로 값을 바꿀 수 있습니다.\n"
REPLY = ("좋은 질문입니다. 멱등성은 같은 요청을 여러 번 보내도 결과가 같은 성질이라 재시도를 효율적으로 할 수 있습니다.\n"
         "도움이 되셨기를 바랍니다.\n")


def test_compliant_translations_have_no_errors_or_long_sentences():
    text = COMPLIANT.read_text(encoding="utf-8")
    found = ko_lint.lint_detail(text, "procedural", config={})
    bad = [h for h in found if h["severity"] == "error" or h["category"] == "sentence_over_limit"]
    assert bad == [], bad


def test_compliant_translations_stay_well_under_the_limits():
    text = COMPLIANT.read_text(encoding="utf-8")
    longest = max(ko_text.eojeol_count(u.text) for u in ko_text.units(text))
    assert longest <= 12, longest


def _calibration_dir(d):
    Path(d, "docs").mkdir()
    Path(d, "reply").mkdir()
    record = {"text": DOC, "condition": "baseline", "scenario": "x", "type": "descriptive", "run": 1}
    Path(d, "docs", "baseline__x__r1.json").write_text(json.dumps(record, ensure_ascii=False), encoding="utf-8")
    Path(d, "reply", "baseline__q__r1.txt").write_text(REPLY, encoding="utf-8")
    Path(d, "meta.json").write_text(json.dumps({"date": "2026-10-09", "model": "m", "effort": "low"}), encoding="utf-8")
    return d


def _labeled(rows, fp_category):
    return [{**r, "label": "FP" if r["category"] == fp_category else "TP",
             "note": "원인" if r["category"] == fp_category else ""} for r in rows]


def test_rows_cover_default_strict_and_reply_checks():
    with tempfile.TemporaryDirectory() as d:
        rows = hits.doc_rows(_calibration_dir(d)) + hits.reply_rows(d)
    got = {(r["mode"], r["category"]) for r in rows}
    assert ("기본", "translationese") in got and ("엄격", "strict_connective") in got
    assert {("답변", "opener"), ("답변", "closer"), ("답변", "slop_word")} <= got
    assert all(r["context"] and r["label"] == "" for r in rows)


def test_tsv_round_trip_keeps_tabs_and_quotes():
    row = hits._row("docs/a.json", 3, "기본", "translationese", "warning", '에 "대해"\t', "문맥")
    with tempfile.TemporaryDirectory() as d:
        path = Path(d, "h.tsv")
        path.write_text(hits.to_tsv([row]), encoding="utf-8")
        assert hits.read_tsv(path) == [row]


def test_precision_counts_fp_left_and_tp_lost():
    a = hits._row("f", 1, "기본", "translationese", "warning", "에 대해", "c")
    b = hits._row("f", 2, "기본", "translationese", "warning", "을 통해", "c")
    c = hits._row("f", 3, "기본", "hedge", "error", "것 같", "c")
    labeled = [{**a, "label": "FP"}, {**b, "label": "TP"}, {**c, "label": "TP"}]
    table = hits.precision_table(labeled, [a, c])
    assert table["translationese"]["hits"] == 2 and table["translationese"]["FP"] == 1
    assert table["translationese"]["fp_left"] == 1 and table["translationese"]["tp_lost"] == 1
    assert table["hedge"]["TP"] == 1 and table["hedge"]["tp_lost"] == 0


def test_check_labels_flags_missing_and_unseen_rows():
    a = hits._row("f", 1, "기본", "translationese", "warning", "에 대해", "c")
    b = hits._row("f", 2, "기본", "hedge", "error", "것 같", "c")
    problems = hits.check_labels([a], [a, b])
    assert len(problems) == 2 and "판정이 없습니다" in problems[0] and "hits.tsv에 없는" in problems[1]


def test_decide_limits_only_raises_on_compliant_overflow():
    limits = {"procedural": 15, "descriptive": 20}
    compliant = {"procedural": {"max": 17}, "descriptive": {"max": 11}}
    baseline = {"procedural": {"over": 3}, "descriptive": {"over": 0}}
    decided, reasons = hits.decide_limits(limits, compliant, baseline)
    assert decided == {"procedural": 17, "descriptive": 20}
    assert "올렸습니다" in reasons["procedural"] and "그대로" in reasons["descriptive"]


def test_changelog_lines_follow_the_limits_in_use():
    kept = hits.changelog_lines({}, [], {"procedural": 12, "descriptive": 18}, {"procedural": 12, "descriptive": 18})
    assert kept == ["- 문장 길이 상한은 절차문 12어절, 설명문 18어절 그대로입니다. 규칙을 지킨 예문은 모두 상한 안이었습니다.",
                    "- 기준선 출력에서 거짓 일치를 찾지 못했습니다."]
    raised = hits.changelog_lines({}, [], {"procedural": 17, "descriptive": 20}, {"procedural": 15, "descriptive": 20})
    assert raised[0] == "- 문장 길이 상한을 바꿨습니다: 절차문 15어절에서 17어절로."


def test_record_stops_on_unlabeled_rows_and_renders_when_complete():
    with tempfile.TemporaryDirectory() as d:
        rows = hits.doc_rows(_calibration_dir(d)) + hits.reply_rows(d)
        try:
            hits.record_md(d, rows)
        except SystemExit as err:
            assert "판정이 없습니다" in str(err)
        else:
            raise AssertionError("판정 없는 행을 받아들였습니다")
        text = hits.record_md(d, _labeled(rows, "slop_word"))
    assert "## 범주별 정밀도" in text and "## CHANGELOG에 옮길 줄" in text
    assert "슬롭 어휘: 판정한 1건 가운데 거짓 일치 1건을 찾아 0건을 고쳤습니다. 원인: 원인." in text
    assert "문장 길이 상한은 절차문 15어절, 설명문 20어절 그대로입니다." in text
```

- [ ] **Step 2: 테스트를 돌려 실패를 확인한다**

Run: `python3 evals/tests/run.py evals/tests/test_calibration.py`
Expected: `ModuleNotFoundError: No module named 'hits'`로 실패한다.

- [ ] **Step 3: 규칙을 지킨 예문과 보정 도구를 쓴다**

`compliant-ko.md`는 원본 SimpleEnglish의 README, SKILL.md, `examples/before-after.md`, `references/use-cases.md`에서 규칙을 지킨 '고친 뒤' 문장을 한국어로 옮긴 것이다. 이 문장들에 오류나 상한 초과가 나오면 린터나 상한이 지나치게 엄격하다는 뜻이다.

`evals/calibration/compliant-ko.md`:

````markdown
# 규칙을 지킨 원본 예문의 한국어판

원본 SimpleEnglish v2.1.1의 `examples/before-after.md`, `SKILL.md`, `references/use-cases.md`에서 '고친 뒤' 문장을 한국어로 옮겼습니다. 이 문장들은 린터에서 오류와 문장 길이 경고가 하나도 없어야 합니다. 걸리면 린터나 상한이 지나치게 엄격하다는 뜻입니다.

## README 소개 (설명문)

sqlpipe는 PostgreSQL 테이블을 Parquet 파일로 Amazon S3에 복사하는 명령줄 도구입니다. 전체 ETL 플랫폼 없이 데이터를 데이터 레이크로 옮깁니다.

sqlpipe는 데이터베이스에 연결해 테이블을 배치 단위로 읽습니다. 배치를 Parquet로 바꿔 S3 버킷에 씁니다. 테이블 전체를 복사하거나, 워터마크 칼럼 이후의 새 행만 복사할 수 있습니다. 백필할 때 한 번 실행하거나 일정에 따라 실행하세요.

설정은 YAML 파일 하나입니다. 이 파일을 인프라 코드와 함께 버전 관리에 넣을 수 있습니다.

## 연결 타임아웃 (절차문)

sqlpipe는 Postgres 포트(기본값 5432)에 연결하지 못하면 `dial tcp: i/o timeout` 오류를 내고 멈춥니다.

1. sqlpipe를 실행하는 호스트가 Postgres 포트에 연결할 수 있는지 확인하세요. 보통 방화벽이나 보안 그룹이 연결을 막습니다.
2. 데이터베이스가 관리형(RDS, Cloud SQL)이면, 인스턴스가 sqlpipe의 IP에서 오는 연결을 허용하는지 확인하세요.
3. 네트워크가 느리면 설정에서 `source.connect_timeout_seconds` 값을 늘리세요.

## 오류 메시지 (절차문)

데이터베이스에 연결하지 못했습니다. 사용자 `app`의 비밀번호가 틀렸습니다.
`DB_PASSWORD`를 올바른 값으로 설정하고 다시 연결하세요.
오류가 계속되면 데이터베이스 관리자에게 접근 권한을 요청하세요.

## 장애 보고 (설명문, 과거형)

14:02부터 14:31(UTC)까지 API 요청의 12%가 HTTP 502로 실패했습니다. 14:00 배포에서 캐시 예열 단계가 빠져서 캐시 노드에 과부하가 걸렸습니다. 14:27에 배포를 되돌렸습니다. 14:31부터 모든 요청이 성공했습니다. 이번 주에 배포 파이프라인에 예열 확인 단계를 추가합니다.

## 호환성이 깨지는 변경 (릴리스 노트)

`/v2/users` 호출을 고치세요. `name` 필드가 `first_name`과 `last_name`으로 나뉘었습니다. 2026-09-01부터 `name` 필드는 null을 돌려줍니다.

## 경고

주의: 운영 DB에 `--force` 플래그를 쓰지 마세요. 이 플래그는 원본에 없는 행을 지웁니다.

## 답변

파드가 다시 시작되었고, 큐는 잠시 리더를 잃었습니다. 큐는 스스로 복구했습니다. 따로 할 일은 없습니다.

## 고객 응대

API가 18분 동안 멈췄습니다. 그동안 올린 파일은 저장되었고 오늘 처리됩니다.
````

`evals/calibration/hits.py`:

```python
#!/usr/bin/env python3
"""보정 도구. 기준선 출력에서 린터가 잡은 것을 모두 나열하고, 사람이 붙인 판정으로 정밀도를 센다.

    python3 evals/calibration/hits.py list evals/calibration/baseline > evals/calibration/hits.tsv
    python3 evals/calibration/hits.py record evals/calibration/baseline evals/calibration/hits.tsv \\
        > evals/calibration/RECORD.md

hits.tsv의 label 칸에는 맞는 일치면 TP, 거짓 일치면 FP를 적는다. FP 행의 note 칸에는 원인을 적는다.
record는 지금 린터로 다시 잡은 결과를 판정과 맞대어, 보정 뒤 남은 거짓 일치와 놓친 맞는 일치를 센다.
"""
import csv
import io
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import ko_lint  # noqa: E402
import ko_rules  # noqa: E402
import ko_text  # noqa: E402

COLUMNS = ("file", "line", "mode", "category", "severity", "match", "context", "label", "note")
COMPLIANT = HERE / "compliant-ko.md"
KIND_LABELS = {"procedural": "절차문", "descriptive": "설명문"}
LABELS = {**ko_lint.LABELS, "opener": "인사말", "closer": "맺음말"}


def _context(text, line):
    lines = ko_text.nfc(text).split("\n")
    s = lines[line - 1].strip() if 0 < line <= len(lines) else ""
    return s if len(s) <= 160 else s[:160] + "…"


def _row(file, line, mode, category, severity, match, context):
    return {"file": file, "line": str(line), "mode": mode, "category": category, "severity": severity,
            "match": match, "context": context, "label": "", "note": ""}


def doc_rows(results_dir):
    """문서 원본마다 기본 모드 위반과, 엄격 모드에서만 나오는 위반을 행으로 만든다."""
    rows = []
    for path in sorted(Path(results_dir, "docs").glob("*.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        text, kind, rel = record["text"], record["type"], f"docs/{path.name}"
        plain = ko_lint.lint_detail(text, kind, config={})
        seen = {(h["line"], h["category"], h["text"]) for h in plain}
        strict = [h for h in ko_lint.lint_detail(text, kind, strict=True, config={})
                  if (h["line"], h["category"], h["text"]) not in seen]
        for mode, hits in (("기본", plain), ("엄격", strict)):
            rows += [_row(rel, h["line"], mode, h["category"], h["severity"], h["text"], _context(text, h["line"]))
                     for h in hits]
    return rows


def reply_rows(results_dir):
    """답변 원본마다 답변 점검 훅이 세는 말(인사말, 맺음말, 슬롭 어휘)의 일치를 행으로 만든다."""
    rows = []
    for path in sorted(Path(results_dir, "reply").glob("*.txt")):
        text = ko_text.nfc(path.read_text(encoding="utf-8"))
        opener = ko_lint.OPENER.search(text)
        found = ([("opener", opener)] if opener else []) + [("closer", m) for m in ko_lint.CLOSER.finditer(text)]
        found += [("slop_word", m) for m in ko_rules.SLOP_RX.finditer(ko_text.mask(text))]
        for category, m in found:
            line = text.count("\n", 0, m.start()) + 1
            rows.append(_row(f"reply/{path.name}", line, "답변", category, "warning", m.group(0).strip(),
                             _context(text, line)))
    return rows


def to_tsv(rows):
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=COLUMNS, delimiter="\t", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue()


def read_tsv(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def key(row):
    return (row["file"], str(row["line"]), row["mode"], row["category"], row["match"])


def check_labels(labeled, current):
    """판정이 빠진 행과, 지금 린터가 잡지만 hits.tsv에 없는 행을 문장 목록으로 돌려준다."""
    problems = [f"판정이 없습니다: {r['file']}:{r['line']} {r['category']} {r['match']}"
                for r in labeled if r["label"] not in ("TP", "FP")]
    known = {key(r) for r in labeled}
    problems += [f"hits.tsv에 없는 일치입니다: {r['file']}:{r['line']} {r['category']} {r['match']}"
                 for r in current if key(r) not in known]
    return problems


def precision_table(labeled, current):
    """범주별 판정 수(hits, TP, FP)와 보정 뒤 남은 거짓 일치(fp_left), 놓친 맞는 일치(tp_lost)."""
    now = {key(r) for r in current}
    table = {}
    for r in labeled:
        t = table.setdefault(r["category"], Counter())
        t["hits"] += 1
        t[r["label"]] += 1
        t["fp_left"] += int(r["label"] == "FP" and key(r) in now)
        t["tp_lost"] += int(r["label"] == "TP" and key(r) not in now)
    return table


def length_stats(texts):
    """[(본문, 문서 유형)]에서 문장 유형별 문장 수, 가장 긴 문장, 상한을 넘은 문장 수를 센다."""
    stats = {kind: Counter() for kind in ko_rules.LIMITS}
    for text, doc_type in texts:
        for u in ko_text.units(ko_text.strip_frontmatter(ko_text.nfc(text))):
            kind = ko_text.sentence_kind(u.text) or doc_type
            n = ko_text.eojeol_count(u.text)
            stats[kind]["sentences"] += 1
            stats[kind]["max"] = max(stats[kind]["max"], n)
            stats[kind]["over"] += int(n > ko_rules.LIMITS[kind])
    return stats


def decide_limits(limits, compliant, baseline):
    """상한을 정한다. 규칙을 지킨 예문이 상한을 넘을 때만 그 길이로 올리고, 근거 없이 줄이지 않는다."""
    decided, reasons = {}, {}
    for kind, limit in limits.items():
        top, over = compliant[kind]["max"], baseline[kind]["over"]
        decided[kind] = max(limit, top)
        if top > limit:
            reasons[kind] = f"규칙을 지킨 예문의 가장 긴 문장이 {top}어절이라 {limit}어절에서 올렸습니다."
        elif over == 0:
            reasons[kind] = "기준선 문장 가운데 상한을 넘은 문장이 없습니다. 줄일 근거가 없어 그대로 둡니다."
        else:
            reasons[kind] = f"규칙을 지킨 예문은 모두 상한 안이고(최대 {top}어절), 기준선 문장 {over}개가 상한을 넘었습니다."
    return decided, reasons


def _precision_section(table):
    lines = ["| 범주 | 판정한 일치 | 맞음 | 거짓 | 정밀도 | 보정 뒤 남은 거짓 | 보정 뒤 놓친 맞음 |",
             "|---|---:|---:|---:|---:|---:|---:|"]
    for cat in sorted(table, key=lambda c: (-table[c]["hits"], c)):
        t = table[cat]
        lines.append(f"| {LABELS.get(cat, cat)} | {t['hits']} | {t['TP']} | {t['FP']} | "
                     f"{t['TP'] / t['hits']:.2f} | {t['fp_left']} | {t['tp_lost']} |")
    return "\n".join(lines)


def _length_section(compliant, baseline, decided, reasons):
    lines = ["| 문장 유형 | 상한 | 규칙을 지킨 예문의 최댓값 | 기준선 문장 수 | 기준선 최댓값 | 상한을 넘은 기준선 문장 |",
             "|---|---:|---:|---:|---:|---:|"]
    for kind, limit in ko_rules.LIMITS.items():
        c, b = compliant[kind], baseline[kind]
        lines.append(f"| {KIND_LABELS[kind]} | {limit}어절 | {c['max']}어절 | {b['sentences']} | {b['max']}어절 | {b['over']} |")
    lines.append("")
    lines += [f"- {KIND_LABELS[k]}: {decided[k]}어절. {reasons[k]}" for k in ko_rules.LIMITS]
    return "\n".join(lines)


def _fp_section(labeled):
    fps = [r for r in labeled if r["label"] == "FP"]
    if not fps:
        return "거짓 일치가 없었습니다."
    rows = ["<!-- simple-korean: off -->", "| 파일 | 줄 | 범주 | 잡힌 말 | 원인 |", "|---|---:|---|---|---|"]
    rows += [f"| {r['file']} | {r['line']} | {LABELS.get(r['category'], r['category'])} | {r['match']} | {r['note']} |"
             for r in fps]
    return "\n".join(rows + ["<!-- simple-korean: on -->"])


def changelog_lines(table, labeled, decided, limits=None):
    """CHANGELOG 1.0.0 항목의 보정 절에 그대로 옮길 줄."""
    limits = limits or ko_rules.LIMITS
    changed = [f"{KIND_LABELS[k]} {limits[k]}어절에서 {decided[k]}어절로" for k in limits if decided[k] != limits[k]]
    kept = ", ".join(f"{KIND_LABELS[k]} {limits[k]}어절" for k in limits)
    lines = [f"- 문장 길이 상한을 바꿨습니다: {', '.join(changed)}." if changed else
             f"- 문장 길이 상한은 {kept} 그대로입니다. 규칙을 지킨 예문은 모두 상한 안이었습니다."]
    for cat in sorted(table):
        t = table[cat]
        if t["FP"]:
            notes = "; ".join(sorted({r["note"] for r in labeled if r["category"] == cat and r["label"] == "FP"}))
            lines.append(f"- {LABELS.get(cat, cat)}: 판정한 {t['hits']}건 가운데 거짓 일치 {t['FP']}건을 찾아 "
                         f"{t['FP'] - t['fp_left']}건을 고쳤습니다. 원인: {notes}.")
    if len(lines) == 1:
        lines.append("- 기준선 출력에서 거짓 일치를 찾지 못했습니다.")
    return lines


def record_md(results_dir, labeled):
    """RECORD.md 본문. 판정이 빠졌거나 hits.tsv에 없는 일치가 있으면 SystemExit로 멈춘다."""
    current = doc_rows(results_dir) + reply_rows(results_dir)
    problems = check_labels(labeled, current)
    if problems:
        raise SystemExit("\n".join(problems[:20] + [f"모두 {len(problems)}건입니다."]))
    docs = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(Path(results_dir, "docs").glob("*.json"))]
    n_replies = len(list(Path(results_dir, "reply").glob("*.txt")))
    meta = json.loads(Path(results_dir, "meta.json").read_text(encoding="utf-8"))
    table = precision_table(labeled, current)
    compliant = length_stats([(COMPLIANT.read_text(encoding="utf-8"), "procedural")])
    baseline = length_stats([(d["text"], d["type"]) for d in docs])
    decided, reasons = decide_limits(ko_rules.LIMITS, compliant, baseline)
    return "\n\n".join([
        f"# 보정 기록 ({meta['date']})",
        f"기준선 문서 {len(docs)}개와 답변 {n_replies}개를 `{meta['model']}`(effort `{meta['effort']}`)로 만들었습니다. "
        "린터가 잡은 일치를 하나씩 맞음과 거짓으로 판정했습니다. 판정과 거짓 일치의 원인은 `hits.tsv`에 있습니다.",
        "## 범주별 정밀도", _precision_section(table),
        "## 문장 길이", _length_section(compliant, baseline, decided, reasons),
        "## 거짓 일치 목록", _fp_section(labeled),
        "## CHANGELOG에 옮길 줄", "\n".join(changelog_lines(table, labeled, decided)),
    ]) + "\n"


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if len(args) == 2 and args[0] == "list":
        sys.stdout.write(to_tsv(doc_rows(args[1]) + reply_rows(args[1])))
        return 0
    if len(args) == 3 and args[0] == "record":
        sys.stdout.write(record_md(args[1], read_tsv(args[2])))
        return 0
    raise SystemExit("사용법: hits.py list <보정 디렉터리> | hits.py record <보정 디렉터리> <hits.tsv>")


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: 테스트를 돌려 통과를 확인한다**

Run: `chmod +x evals/calibration/hits.py && python3 evals/tests/run.py evals/tests/test_calibration.py && /usr/bin/python3 evals/tests/run.py evals/tests/test_calibration.py && python3 evals/tests/run.py | grep -c '^ok'`
Expected: 앞의 두 번은 `ok` 9줄, 마지막(전체)은 `95`. 종료 코드는 모두 0.

- [ ] **Step 5: 기준선 출력을 만든다**

이 단계는 `claude -p`를 17번 부른다(격리 확인 1번, 문서 8번, 답변 8번). 스킬 없이 만든 출력이라 Task 16에서 스킬 문서가 바뀌어도 다시 만들지 않는다. 본 측정(Task 17)과 다른 출력을 쓰므로, 린터를 측정용 출력에 맞추는 일도 생기지 않는다.

Run:

```bash
python3 evals/bench_common.py --probe --out evals/calibration/baseline
python3 evals/run_bench.py --out evals/calibration/baseline --runs 1 --conditions baseline
python3 evals/run_reply_bench.py --out evals/calibration/baseline --runs 1 --conditions baseline
ls evals/calibration/baseline/docs | wc -l; ls evals/calibration/baseline/reply | wc -l
```

Expected: 격리 확인이 `"problems": []`를 출력하고 0으로 끝난다. 이어서 `8`과 `8`이 나온다. 파일이 모자라면 같은 명령을 다시 돌린다. 이미 있는 파일은 건너뛴다. 격리 문제가 나오면 멈추고 문제 목록을 사용자에게 보인다.

- [ ] **Step 6: 일치를 나열하고 판정한다**

Run: `python3 evals/calibration/hits.py list evals/calibration/baseline > evals/calibration/hits.tsv && wc -l evals/calibration/hits.tsv`
Expected: 머리글 1줄과 일치 행들이 나온다. 계획 검증 때 짧은 가짜 기준선 8개와 답변 8개로 돌리니 56행이었다. 실제 출력은 더 길어서 행이 더 많다.

행마다 `context` 칸의 문장을 읽고 `label` 칸을 채운다.
- `TP`: 범주가 막으려는 문제가 그 문장에 실제로 있다. 예: "설정에 대해 알아보겠습니다"의 "에 대해"는 번역투다.
- `FP`: 패턴이 다른 것에 걸렸다. 예: "강력한 일관성"의 "강력한"은 데이터베이스 용어(strong consistency)라서 슬롭이 아니다.
- `FP` 행의 `note` 칸에는 원인을 짧게 쓴다(예: "DB 용어 strong consistency"). 같은 원인은 같은 문구로 쓴다. RECORD.md와 CHANGELOG가 이 문구를 그대로 모은다.

판정은 문맥을 읽고 한다. 행이 100개를 넘으면 사용자 전역 규칙에 따라 TypeSafe Jev로 먼저 분류해도 된다. 그때도 Jev가 FP로 본 행, 확률이 0.25에서 0.75 사이인 행, TP로 본 행 가운데 무작위 20행은 직접 읽고 확정한다. `note`는 직접 쓴다. 칸에 탭과 큰따옴표가 들 수 있으므로 TSV는 `hits.read_tsv`와 `hits.to_tsv`(csv 모듈)로 읽고 쓴다.

- [ ] **Step 7: 거짓 일치를 고친다**

같은 원인의 FP를 하나로 묶고, 원인마다 이 순서를 지킨다.
1. 그 FP 문장을 '잡지 않아야 하는 예'로 담은 시험을 아래 표의 시험 파일에 더한다. 시험을 돌려 실패를 확인한다.
2. 표의 패턴을 좁힌다. 맞는 일치(TP)를 이유로 패턴을 바꾸지 않는다.
3. 그 시험 파일, `python3 evals/ko_lint.py --self-test`, `python3 evals/tests/run.py`를 돌려 통과를 확인한다.
4. Step 8의 RECORD.md에서 '보정 뒤 놓친 맞음'이 0인지 확인한다. 0이 아니면 좁힌 패턴이 맞는 일치까지 놓친 것이므로 다시 고친다.

시험의 형식은 다음과 같다. 원인이 실제로 나왔을 때만 더한다.

```python
def test_calibration_fp_strong_consistency_is_not_slop():
    # hits.tsv의 FP 행, note "DB 용어 strong consistency"
    masked = ko_text.mask("이 저장소는 강력한 일관성을 보장합니다.")
    assert [h for h in ko_rules.lexical_hits(masked) if h.category == "slop_word"] == []
```

좁힐 수 없는 FP는 RECORD.md 표의 범주 정밀도로 정한다.
- 정밀도가 0.8 이상이면 그대로 둔다. RECORD.md에 '보정 뒤 남은 거짓'으로 남는다.
- 정밀도가 0.8 미만이면 오류 범주는 경고로 낮추고, 경고 범주는 엄격 모드로만 옮긴다. 이 결정을 그 범주 FP 행의 `note`에 덧붙인다(예: "DB 용어 strong consistency, 경고로 낮춤").

| 범주 | 패턴이 있는 곳 | 시험 파일 |
|---|---|---|
| hedge, double_passive, translationese, light_verb, colloquial, latin_abbrev, em_dash, semicolon, slop_word의 "단순히…아니라" | `evals/ko_rules.py`의 `LEXICAL` | `evals/tests/test_ko_rules.py` |
| will_calque, synonym_rotation, strict_ending, strict_condition, strict_connective | `ko_rules.WILL`, `CHECK_VERB`, `CONFIG_NOUN`, `STRICT_LEXICAL`, `COND`, `NA_LIST`, `NA_STOP` | `evals/tests/test_ko_rules.py` |
| sentence_over_limit, trailing_condition, noun_ending | `ko_rules.TRAIL_PROVISO`, `TRAIL_PAREN`, `NOUN_END`. 문장을 잘못 나눴으면 `ko_text.split_sentences`, 어절을 잘못 셌으면 `ko_text.eojeol_count` | `evals/tests/test_ko_rules.py`, `evals/tests/test_ko_text.py` |
| register_mix | `ko_text.register`, `ko_rules.STYLES` | `evals/tests/test_ko_text.py`, `evals/tests/test_ko_rules.py` |
| spelling, term_choice, term_mix | 합성어에 걸렸으면 `ko_terms.GLOBAL_SKIP`, 잡을 형태가 틀렸으면 `data/terms.json`의 `flag.forms` | `evals/tests/test_ko_terms.py` |
| slop_word(어휘) | `ko_rules.SLOP_CORE`의 말이면 그 튜플이나 `slop_pattern`에 연어 예외를 더한다. `evals/slop.tsv`의 말이면 `tools/slop-lexicon/exclusions.tsv`에 말과 이유를 더하고 `python3 -I tools/slop-lexicon/build_slop.py build`를 돌린다 | `evals/tests/test_ko_rules.py`, `evals/tests/test_slop_build.py` |
| opener, closer | `ko_lint.OPENER`, `ko_lint.CLOSER` | `evals/tests/test_ko_lint.py` |

- [ ] **Step 8: 보정 기록을 만든다**

Run: `python3 evals/calibration/hits.py record evals/calibration/baseline evals/calibration/hits.tsv > evals/calibration/RECORD.md; echo "exit=$?"`
Expected: `exit=0`. RECORD.md에 '범주별 정밀도', '문장 길이', '거짓 일치 목록', 'CHANGELOG에 옮길 줄' 네 절이 있다. '보정 뒤 놓친 맞음' 칸은 모두 0이다.

`hits.tsv에 없는 일치입니다`로 멈추면 Step 7에서 패턴을 고치다 새 일치가 생긴 것이다. 새 행을 hits.tsv 끝에 붙이고, 판정을 채운 뒤, 다시 돌린다.

```bash
python3 - <<'PY'
import sys
sys.path.insert(0, "evals/calibration")
import hits
labeled = hits.read_tsv("evals/calibration/hits.tsv")
known = {hits.key(r) for r in labeled}
current = hits.doc_rows("evals/calibration/baseline") + hits.reply_rows("evals/calibration/baseline")
new = [r for r in current if hits.key(r) not in known]
with open("evals/calibration/hits.tsv", "a", encoding="utf-8", newline="") as f:
    f.write(hits.to_tsv(new).split("\n", 1)[1])
print(len(new), "행을 더했습니다. label과 note를 채우세요.")
PY
```

- [ ] **Step 9: 상한 결정을 반영한다**

RECORD.md '문장 길이' 절의 결정이 15어절과 20어절이면 할 일이 없다. 계획 검증 때 규칙을 지킨 예문의 가장 긴 문장은 11어절이었으므로 그대로일 가능성이 높다.

결정이 바뀌었으면 숫자가 나오는 곳을 모두 같은 값으로 바꾼다. `grep -rn "15어절\|20어절" skills prompts output-styles evals/ko_rules.py`로 찾는다. `prompts/system-prompt.md`와 `output-styles/simple-korean.md`의 규칙 블록은 글자 하나까지 같아야 한다. Global Constraints의 상한 줄과 Task 19의 README 규칙 표도 새 값으로 쓴다. 그다음 Step 8을 다시 돌린다.

- [ ] **Step 10: 전체 시험과 관문을 돌린다**

Run:

```bash
python3 evals/ko_lint.py --self-test && python3 evals/tests/run.py > /dev/null && /usr/bin/python3 evals/tests/run.py > /dev/null \
  && node --test src/hooks/simple-korean-activate.test.js > /dev/null && python3 src/hooks/test_lint_hook.py > /dev/null \
  && python3 evals/ko_lint.py --gate skills/simple-korean/SKILL.md skills/simple-korean/references/*.md prompts/system-prompt.md output-styles/simple-korean.md > /dev/null; echo "exit=$?"
```

Expected: `self-test OK: ...` 한 줄과 `exit=0`.

- [ ] **Step 11: 커밋한다**

```bash
git add evals/calibration evals/tests evals/ko_rules.py evals/ko_terms.py evals/ko_text.py evals/ko_lint.py evals/slop.tsv tools/slop-lexicon/exclusions.tsv data/terms.json
git commit -m "feat: calibrate the linter on baseline outputs" -m $'Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01SanRSLxxVtkLMJh1wLGeGZ'
```

### Task 16: 압력 시험

스펙 11.5다. 이 레포지토리를 실제 플러그인으로 올려 스킬의 행동을 시나리오 8개로 확인한다. 실패하면 스킬 문서를 고치므로 본 측정(Task 17)보다 먼저 한다. 그래야 측정한 판본과 공개하는 판본이 같다.

계획 검증 때 시나리오 2를 미리 돌렸다. 훅이 "이 플러그인의 skills/simple-korean/SKILL.md"라는 상대 경로만 알린 판본에서 모델은 도구를 한 번도 부르지 않았다. 그리고 K 번호 대신 자체 목록 번호(1~10)를 붙였다. Task 10의 훅이 절대 경로를 알리고 Task 8의 SKILL.md가 "규칙 번호를 적어야 하면" 규칙 목록을 열게 한 판본에서는, 규칙 목록을 읽고 실제 K 번호 13개를 인용했다. 13개 모두 `rule-catalog.md`에 있었다.

**Files:**
- Create: `evals/pressure-tests.md`, `evals/run_pressure.py`
- Create(생성물): `evals/results/<날짜>/pressure/`(시나리오 8개 × 조건 2개)
- Modify(실패가 나온 경우만): `skills/simple-korean/SKILL.md`, `skills/simple-korean/references/*.md`, `prompts/system-prompt.md`, `output-styles/simple-korean.md`, `src/hooks/simple-korean-activate.js`
- Test: `evals/tests/test_pressure.py`

**Interfaces:**
- Consumes: Task 14의 `bench_common.call_claude(prompt, ..., cmd=...)`, `parse_conditions`, `MODEL`, `EFFORT`, `ROOT`, `HERE`, Task 6의 `ko_lint.lint_detail`, `reader_check`, Task 2의 `ko_text.register`, `units`, Task 10의 세션 시작 훅(SKILL.md 절대 경로), Task 12의 플러그인 매니페스트
- Produces: `run_pressure.parse_scenarios(markdown) -> list[dict]`(키 `n`, `title`, `prompt`), `pressure_cmd(prompt, plugin_dir=None) -> list[str]`, `generate(out, scenarios, round_no=1, call, sleep, conditions, plugin_dir)`, `machine_report(n, text) -> dict`, `check_lines(out) -> list[str]`. 출력 파일 이름 `<baseline|plugin>__p<번호>__r<회차>.txt`. `evals/pressure-tests.md`의 '기록' 절(Task 20이 사용자에게 보인다).

- [ ] **Step 1: 실패하는 테스트를 쓴다**

`evals/tests/test_pressure.py`:

```python
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import run_pressure  # noqa: E402

SAMPLE = """# 압력 시험

## 시나리오 1: 첫째

> 한 줄 프롬프트입니다.

- [ ] 기준

## 시나리오 2: 둘째

<!-- simple-korean: off -->
> 첫 줄입니다.
>
> 둘째 문단입니다.
<!-- simple-korean: on -->

> 이 인용은 프롬프트가 아닙니다.
"""


def test_parse_scenarios_reads_first_quote_block():
    got = run_pressure.parse_scenarios(SAMPLE)
    assert [s["n"] for s in got] == [1, 2] and got[1]["title"] == "둘째"
    assert got[0]["prompt"] == "한 줄 프롬프트입니다."
    assert got[1]["prompt"] == "첫 줄입니다.\n\n둘째 문단입니다."


def test_parse_scenarios_rejects_missing_prompt():
    try:
        run_pressure.parse_scenarios("## 시나리오 3: 빈 시나리오\n\n- [ ] 기준\n")
    except SystemExit as err:
        assert "시나리오 3" in str(err)
    else:
        raise AssertionError("프롬프트 없는 시나리오를 받아들였습니다")


def test_real_file_has_eight_numbered_scenarios():
    got = run_pressure.parse_scenarios(run_pressure.TESTS_MD.read_text(encoding="utf-8"))
    assert [s["n"] for s in got] == list(range(1, 9))
    assert all(len(s["prompt"]) > 20 for s in got)
    assert "시도되어지며" in got[1]["prompt"] and "해요체로" in got[6]["prompt"]


def test_pressure_cmd_isolates_and_adds_plugin_only_when_asked():
    base = run_pressure.pressure_cmd("질문")
    assert base[:3] == ["claude", "-p", "질문"] and "--plugin-dir" not in base
    assert base[base.index("--setting-sources") + 1] == "" and "--strict-mcp-config" in base
    assert base[base.index("--allowedTools") + 1] == "Read,Glob,Grep,Skill"
    assert run_pressure.pressure_cmd("질문", "/repo")[-2:] == ["--plugin-dir", "/repo"]


def test_machine_report_counts_lint_and_style_criteria():
    r1 = run_pressure.machine_report(1, "연결이 끊기면 설정을 확인하는 것이 좋습니다.\n")
    assert r1["hedge"] == 1 and r1["sentence_over_limit"] == 0
    r6 = run_pressure.machine_report(6, "sqlpipe는 테이블을 복사한다. 설정은 YAML 파일 하나입니다.\n")
    assert r6 == {"요청한 문체 문장": 1, "다른 문체 문장": 1}
    r7 = run_pressure.machine_report(7, "메모리가 모자라서 파드가 죽었어요.\n- 한도를 늘리세요\n")
    assert r7 == {"요청한 문체 문장": 2, "다른 문체 문장": 0, "visible_total": 1}
    mixed = run_pressure.machine_report(7, "메모리가 모자라서 파드가 죽었습니다. 한도를 늘리세요.\n")
    assert mixed["다른 문체 문장"] == 1
    r8 = run_pressure.machine_report(8, "백업은 반드시 하루에 한 번 실행해야 합니다.\n")
    assert r8["strict_ending"] == 1
    assert run_pressure.machine_report(4, "아무 글입니다.") == {}


def test_check_lines_reads_saved_outputs():
    with tempfile.TemporaryDirectory() as d:
        Path(d, "plugin__p3__r1.txt").write_text("백업이 있는지 확인하세요.\n", encoding="utf-8")
        Path(d, "baseline__p4__r1.txt").write_text("히어로 문구입니다.\n", encoding="utf-8")
        lines = run_pressure.check_lines(d)
    assert lines == ["baseline__p4__r1.txt: 읽고 판정", "plugin__p3__r1.txt: noun_ending=0"]


def test_generate_writes_round_files_and_skips_existing():
    seen = []

    def fake(prompt, cmd=None, **kwargs):
        seen.append(cmd)
        return {"text": "출력입니다."}

    scenarios = [{"n": 4, "title": "t", "prompt": "p"}]
    with tempfile.TemporaryDirectory() as d:
        run_pressure.generate(d, scenarios, 2, call=fake, sleep=0, plugin_dir="/repo")
        assert sorted(p.name for p in Path(d).iterdir()) == ["baseline__p4__r2.txt", "plugin__p4__r2.txt"]
        assert "--plugin-dir" not in seen[0] and seen[1][-2:] == ["--plugin-dir", "/repo"]
        run_pressure.generate(d, scenarios, 2, call=fake, sleep=0, plugin_dir="/repo")
        assert len(seen) == 2
```

- [ ] **Step 2: 테스트를 돌려 실패를 확인한다**

Run: `python3 evals/tests/run.py evals/tests/test_pressure.py`
Expected: `ModuleNotFoundError: No module named 'run_pressure'`로 실패한다.

- [ ] **Step 3: 시나리오 문서와 실행기를 쓴다**

시나리오 2, 3, 6, 7의 프롬프트는 일부러 규칙을 어긴 글을 담으므로 꺼짐 표시로 감싼다. 실행기는 꺼짐 표시와 관계없이 제목 아래 첫 인용 블록을 프롬프트로 읽는다.

`evals/pressure-tests.md`:

````markdown
# 압력 시험

스킬의 행동을 확인하는 시나리오와 통과 기준입니다. 시나리오마다 스킬 없이 한 번, 플러그인을 켜고 한 번 돌려서 기준과 비교합니다. 기준선에서도 통과하는 기준은 아무것도 증명하지 못합니다. 쓸모 있는 기준은 기준선이 실패하는 기준입니다.

돌리려면 `python3 evals/run_pressure.py --out evals/results/<날짜>/pressure`를 실행하세요. 출력 파일 이름은 `<조건>__p<번호>__r<회차>.txt`입니다. 조건은 `baseline`(스킬 없음)과 `plugin`(이 레포지토리를 `--plugin-dir`로 올림) 두 가지입니다. 두 조건 모두 설정과 MCP 서버를 읽지 않고, 읽기 도구와 Skill 도구만 씁니다. 기계로 셀 수 있는 기준은 시나리오마다 적은 린터 명령으로 확인하세요. 나머지 기준은 출력을 읽고 판정하세요.

## 시나리오 1: 자연스러운 문서 과제

> Postgres 테이블을 Parquet 파일로 S3에 동기화하는 CLI 도구 sqlpipe의 문서를 써 주세요. 소개, '시작하기' 절, 연결 타임아웃과 권한 오류를 다루는 '문제 해결' 절을 넣고 1,200자 안팎으로 써 주세요.

통과 기준:

- [ ] 절차문에 15어절을 넘는 문장이 없습니다.
- [ ] 설명문에 20어절을 넘는 문장이 없습니다.
- [ ] 짐작과 권고 표현이 없습니다.
- [ ] 확인하는 동작을 "확인하다" 하나로 씁니다.
- [ ] 조건이 모두 명령 앞에 옵니다.
- [ ] 코드, 플래그, 오류 문구를 바꾸지 않습니다.

기계 확인: `python3 evals/ko_lint.py --type procedural <파일>`에서 `sentence_over_limit`, `hedge`, `synonym_rotation`, `trailing_condition`이 0이어야 합니다.

## 시나리오 2: 규칙 번호를 인용하는 재작성

<!-- simple-korean: off -->
> 이 문단을 SimpleKorean 규칙으로 다시 쓰고, 적용한 규칙을 번호와 함께 적어 주세요.
>
> 강력한 재시도 기능을 활용하여 실패한 업로드는 자동으로 다시 시도되어지며, 이를 통해 데이터의 무결성이 원활하게 보장되고 있습니다. 만약 네트워크 장애가 계속되면 설정을 확인하는 것이 좋습니다(타임아웃이 짧은 경우).
<!-- simple-korean: on -->

통과 기준:

- [ ] 인용한 규칙 번호가 모두 `skills/simple-korean/references/rule-catalog.md`에 있고, 번호와 내용이 맞습니다. 번호를 지어내지 않습니다.
- [ ] 다시 쓰기 전에 절차문인지 설명문인지 가립니다.
- [ ] 이중 피동 "시도되어지며"와 번역투 "을 통해", "만약"을 고칩니다.
- [ ] 괄호로 뒤에 붙은 조건을 명령 앞으로 옮깁니다.

## 시나리오 3: "최대한 짧게" 압력

<!-- simple-korean: off -->
> 이 런북 단계를 최대한 짧게 다시 써 주세요: "마이그레이션을 실행하기 전에 백업이 존재하는지 반드시 확인해야 합니다."
<!-- simple-korean: on -->

함정: 짧게 쓰라는 압력을 받으면 조사를 빼거나 "백업 확인 필요"처럼 명사형으로 끝내기 쉽습니다. 짧은 글과 전보문은 다릅니다.

통과 기준:

- [ ] 조사를 빼지 않고 문장을 끝까지 씁니다. 예: "백업이 있는지 확인하세요. 그다음 마이그레이션을 실행하세요."
- [ ] 명사형 종결과 개조식이 없습니다.

기계 확인: `python3 evals/ko_lint.py --type procedural <파일>`에서 `noun_ending`이 0이어야 합니다.

## 시나리오 4: 범위 밖 요청

> simple-korean 스킬로 sqlpipe 랜딩 페이지의 히어로 문구를 써 주세요.

통과 기준:

- [ ] 이 규칙이 마케팅 글에 맞지 않는다고 알립니다. 그리고 문서에 쓰자고 제안하거나 어떻게 할지 묻습니다.

## 시나리오 5: 오류 메시지

> S3 업로드가 AccessDenied로 실패할 때 sqlpipe가 출력할 오류 메시지를 써 주세요.

통과 기준:

- [ ] 일어난 일을 과거형으로 씁니다.
- [ ] 고치는 방법을 "-하세요"로 씁니다.
- [ ] 감탄("앗"), 사과("죄송합니다"), 권고("확인 바랍니다")가 없습니다.

## 시나리오 6: 해라체 문서 고치기

<!-- simple-korean: off -->
> 아래 문서를 SimpleKorean 규칙으로 고쳐 주세요.
>
> sqlpipe는 강력한 동기화 기능을 제공한다. 설정 파일은 YAML로 작성되어지며, 이를 통해 손쉽게 관리가 가능하다. 만약 연결이 실패하면 재시도를 진행하는 것이 좋다.
<!-- simple-korean: on -->

통과 기준:

- [ ] 해라체를 그대로 씁니다. "-습니다"로 바꾸지 않습니다.
- [ ] 슬롭 어휘("강력한", "손쉽게"), 이중 피동, 번역투, 기능동사("진행하는"), 권고형을 고칩니다.

기계 확인: `python3 evals/ko_lint.py <파일>`에서 `register_mix`가 0이어야 합니다.

## 시나리오 7: 해요체 답변 요청

<!-- simple-korean: off -->
> 해요체로 답해 주세요. 쿠버네티스에서 파드가 OOMKilled로 재시작되는 건 무슨 뜻이에요?
<!-- simple-korean: on -->

통과 기준:

- [ ] 답변 전체를 해요체 하나로 씁니다. "-습니다"를 섞지 않습니다.
- [ ] 서술형으로 답합니다. 헤더, 불릿, 굵은 글씨가 없습니다.
- [ ] 첫 문장이 답입니다.
- [ ] OOMKilled를 처음 쓸 때 짧게 풀이합니다.

기계 확인: `python3 evals/ko_lint.py --type reply <파일>`에서 `visible_total`이 0이어야 합니다.

## 시나리오 8: KS A 0001 엄격 모드 요구사항 문서

> 엄격 모드로 sqlpipe 백업 기능의 요구사항 문서를 써 주세요. 의무, 금지, 허용 조건을 하나씩 넣어 주세요.

통과 기준:

- [ ] 문장 끝은 정해진 다섯 가지만 씁니다. 의무 "-해야 합니다", 금지 "-하면 안 됩니다", 허용 "-해도 됩니다", 능력 "-ㄹ 수 있습니다", 사실은 현재형입니다.
- [ ] 권고형과 "-ㄹ 것입니다"가 없습니다.
- [ ] 접속어 "(이)나"가 없습니다.
- [ ] 비공식 기준이라는 고지를 한 번 넣습니다.

기계 확인: `python3 evals/ko_lint.py --strict <파일>`에서 이름이 `strict_`로 시작하는 범주와 `hedge`, `will_calque`가 모두 0이어야 합니다.
````

`evals/run_pressure.py`:

```python
#!/usr/bin/env python3
"""압력 시험 실행기. evals/pressure-tests.md의 시나리오를 스킬 없이 한 번, 플러그인을 켜고 한 번 돌린다.

플러그인 조건은 이 레포지토리를 --plugin-dir로 올려 세션 시작 훅과 스킬을 실제로 쓴다. 스킬이
레퍼런스를 읽을 수 있게 두 조건 모두 Read, Glob, Grep, Skill을 허용하고 나머지 도구는 막는다.
이미 있는 출력은 건너뛴다.

    python3 evals/run_pressure.py --out evals/results/<날짜>/pressure [--round 1] [--only 2,6] [--conditions plugin]
    python3 evals/run_pressure.py --out evals/results/<날짜>/pressure --check   # 기계로 셀 기준만 센다
"""
import argparse
import re
import sys
import time
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bench_common as bc  # noqa: E402
import ko_lint  # noqa: E402
import ko_text  # noqa: E402

TESTS_MD = bc.HERE / "pressure-tests.md"
CONDITIONS = ("baseline", "plugin")
ALLOWED = "Read,Glob,Grep,Skill"
DENIED = "Bash,Write,Edit,WebFetch,WebSearch,NotebookEdit"
HEADING = re.compile(r"^## 시나리오 (\d+): (.+)$")
LINT_CHECKS = {
    1: ("procedural", False, ("sentence_over_limit", "hedge", "synonym_rotation", "trailing_condition")),
    3: ("procedural", False, ("noun_ending",)),
    8: ("descriptive", True, ("strict_ending", "strict_condition", "strict_connective", "hedge", "will_calque")),
}
STYLE_CHECKS = {6: ("haera",), 7: ("haeyo", "haeyo_imp")}


def parse_scenarios(markdown):
    """'## 시나리오 N: 제목' 아래 첫 인용 블록을 프롬프트로 읽는다."""
    scenarios = []
    for block in re.split(r"(?m)^(?=## 시나리오 \d+: )", markdown):
        m = HEADING.match(block.split("\n", 1)[0])
        if not m:
            continue
        quote = re.search(r"(?m)^>.*(?:\n>.*)*", block)
        if not quote:
            raise SystemExit(f"시나리오 {m.group(1)}에 인용 블록 프롬프트가 없습니다")
        prompt = "\n".join(re.sub(r"^> ?", "", line) for line in quote.group(0).split("\n")).strip()
        scenarios.append({"n": int(m.group(1)), "title": m.group(2).strip(), "prompt": prompt})
    return scenarios


def pressure_cmd(prompt, plugin_dir=None):
    """압력 시험용 claude 명령. 설정과 MCP 서버는 읽지 않고, 읽기 도구와 Skill만 허용한다."""
    cmd = ["claude", "-p", prompt, "--model", bc.MODEL, "--effort", bc.EFFORT,
           "--setting-sources", "", "--strict-mcp-config",
           "--allowedTools", ALLOWED, "--disallowedTools", DENIED, "--output-format", "json"]
    return cmd + ["--plugin-dir", str(plugin_dir)] if plugin_dir else cmd


def generate(out, scenarios, round_no=1, call=bc.call_claude, sleep=2.0, conditions=CONDITIONS, plugin_dir=bc.ROOT):
    """시나리오 × 조건의 출력을 out/<조건>__p<번호>__r<회차>.txt로 쓴다. 있는 파일은 건너뛴다."""
    Path(out).mkdir(parents=True, exist_ok=True)
    for sc in scenarios:
        for cond in conditions:
            path = Path(out) / f"{cond}__p{sc['n']}__r{round_no}.txt"
            if path.exists() and path.read_text(encoding="utf-8").strip():
                continue
            print(f"{cond} 시나리오 {sc['n']} r{round_no}", flush=True)
            try:
                res = call(sc["prompt"], cmd=pressure_cmd(sc["prompt"], plugin_dir if cond == "plugin" else None))
            except Exception as err:  # noqa: BLE001  하나가 실패해도 나머지는 돈다
                print(f"  실패: {err}", flush=True)
                continue
            path.write_text(res["text"], encoding="utf-8")
            time.sleep(sleep)


def machine_report(n, text):
    """시나리오 n에서 기계로 셀 수 있는 값. 셀 기준이 없는 시나리오는 빈 dict다."""
    report = {}
    if n in LINT_CHECKS:
        kind, strict, categories = LINT_CHECKS[n]
        found = Counter(h["category"] for h in ko_lint.lint_detail(text, kind, strict=strict, config={}))
        report.update({c: found[c] for c in categories})
    if n in STYLE_CHECKS:
        styles = Counter(r for r in (ko_text.register(u.text) for u in ko_text.units(text)) if r)
        wanted = sum(styles[s] for s in STYLE_CHECKS[n])
        report.update({"요청한 문체 문장": wanted, "다른 문체 문장": sum(styles.values()) - wanted})
    if n == 7:
        report["visible_total"] = ko_lint.reader_check(text)["visible_total"]
    return report


def check_lines(out):
    """출력 파일마다 기계 확인 값을 한 줄로 만든다."""
    lines = []
    for path in sorted(Path(out).glob("*__p*__r*.txt")):
        n = int(re.search(r"__p(\d+)__", path.name).group(1))
        values = machine_report(n, path.read_text(encoding="utf-8"))
        lines.append(f"{path.name}: " + (", ".join(f"{k}={v}" for k, v in values.items()) or "읽고 판정"))
    return lines


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--round", type=int, default=1)
    ap.add_argument("--only", default="", help="쉼표로 나눈 시나리오 번호")
    ap.add_argument("--conditions", default=",".join(CONDITIONS), help="쉼표로 나눈 조건 목록")
    ap.add_argument("--check", action="store_true", help="저장된 출력의 기계 확인 값만 출력한다")
    a = ap.parse_args(argv)
    if a.check:
        print("\n".join(check_lines(a.out)))
        return 0
    conditions = bc.parse_conditions(a.conditions, CONDITIONS)
    scenarios = parse_scenarios(TESTS_MD.read_text(encoding="utf-8"))
    if a.only:
        wanted = {int(x) for x in a.only.split(",") if x.strip()}
        scenarios = [s for s in scenarios if s["n"] in wanted]
    generate(a.out, scenarios, a.round, conditions=conditions)
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: 테스트를 돌려 통과를 확인한다**

Run: `chmod +x evals/run_pressure.py && python3 evals/tests/run.py evals/tests/test_pressure.py && /usr/bin/python3 evals/tests/run.py evals/tests/test_pressure.py && python3 evals/tests/run.py | grep -c '^ok' && python3 evals/ko_lint.py --gate=warning evals/pressure-tests.md > /dev/null; echo "exit=$?"`
Expected: 앞의 두 번은 `ok` 7줄, 이어서 `102`(Task 15 Step 7에서 회귀 시험을 더했으면 그 수만큼 많다), 마지막에 `exit=0`(시나리오 문서도 오류와 경고가 없다).

- [ ] **Step 5: 시나리오를 돌린다**

이 단계는 `claude -p`를 16번 부른다. 계획 검증 때 플러그인 조건 한 번에 약 $0.04가 들었다.

Run:

```bash
DATE=$(date +%F)
python3 evals/run_pressure.py --out "evals/results/$DATE/pressure"
ls "evals/results/$DATE/pressure" | wc -l
python3 evals/run_pressure.py --out "evals/results/$DATE/pressure" --check
```

Expected: `16`. 이어서 파일마다 한 줄씩 기계 확인 값이 나온다. 예: `plugin__p3__r1.txt: noun_ending=0`, `plugin__p4__r1.txt: 읽고 판정`. 파일이 모자라면 같은 명령을 다시 돌린다.

- [ ] **Step 6: 채점하고 기록한다**

출력 16개를 모두 읽는다. 시나리오의 통과 기준마다 판정한다. 기계 확인 값이 있는 기준은 그 값을 쓴다(0이면 통과). `evals/pressure-tests.md` 끝에 이 절을 붙이고 칸을 채운다. `<날짜>`는 Step 5의 `$DATE`다. 통과는 O, 실패는 X다.

```markdown
## 기록

### <날짜>, `claude-sonnet-5-5`, effort low, 회차 1

출력은 `evals/results/<날짜>/pressure/`에 있습니다. 통과는 O, 실패는 X입니다.

| 시나리오 | 기준 | 스킬 없음 | SimpleKorean |
|---|---|---|---|
| 1 | 절차문 15어절 이하 |  |  |
| 1 | 설명문 20어절 이하 |  |  |
| 1 | 짐작과 권고 없음 |  |  |
| 1 | "확인하다" 하나 |  |  |
| 1 | 조건이 명령 앞 |  |  |
| 1 | 코드, 플래그, 오류 문구 그대로 |  |  |
| 2 | 실제 K 번호만 인용 |  |  |
| 2 | 유형을 먼저 가림 |  |  |
| 2 | 이중 피동과 번역투를 고침 |  |  |
| 2 | 괄호 조건을 명령 앞으로 |  |  |
| 3 | 조사를 지킴 |  |  |
| 3 | 명사형 종결과 개조식 없음 |  |  |
| 4 | 범위 밖이라고 알림 |  |  |
| 5 | 과거형으로 알림 |  |  |
| 5 | "-하세요"로 고치는 법 |  |  |
| 5 | 감탄, 사과, 권고 없음 |  |  |
| 6 | 해라체 유지 |  |  |
| 6 | 위반을 고침 |  |  |
| 7 | 해요체 하나 |  |  |
| 7 | 서술형 |  |  |
| 7 | 첫 문장이 답 |  |  |
| 7 | 용어 풀이 |  |  |
| 8 | 닫힌 문장 끝만 |  |  |
| 8 | 권고형과 미래형 없음 |  |  |
| 8 | "(이)나" 없음 |  |  |
| 8 | 비공식 기준 고지 |  |  |

실패한 기준은 다음과 같습니다.
```

표 아래에는 X마다 `- 시나리오 <번호>, <조건>: <이유 한 문장>` 줄을 쓴다. X가 하나도 없으면 "실패한 기준은 다음과 같습니다." 대신 "실패한 기준이 없습니다."를 쓴다.

- [ ] **Step 7: SimpleKorean의 실패를 고친다**

SimpleKorean 칸에 X가 없으면 Step 8로 간다.

X가 있으면 실패한 기준에 해당하는 SKILL.md 규칙이나 '내기 전 자가 점검' 줄을 고친다. 답변 규칙이면 `prompts/system-prompt.md`와 `output-styles/simple-korean.md`의 규칙 블록도 같은 글로 고친다. 그다음 그 시나리오만 플러그인 조건으로 다시 돌린다.

```bash
python3 evals/run_pressure.py --out "evals/results/$DATE/pressure" --round 2 --only <실패한 시나리오 번호들> --conditions plugin
python3 evals/run_pressure.py --out "evals/results/$DATE/pressure" --check
```

결과를 `### <날짜>, ..., 회차 2 (고친 뒤)` 표로 기록 절에 더한다. 다시 돌린 시나리오의 행만 넣고, 스킬 없음 칸은 "-"로 쓴다. 표 위에 무엇을 고쳤는지 한 문장으로 쓴다. 회차 2에서도 X이면 한 번 더 고치고 회차 3으로 돌린다. 회차 3에서도 X이면 더 고치지 않고 기록한다. 이 실패는 Task 20에서 사용자에게 알린다.

- [ ] **Step 8: 전체 시험과 관문을 돌린다**

Run:

```bash
python3 evals/ko_lint.py --self-test && python3 evals/tests/run.py > /dev/null && /usr/bin/python3 evals/tests/run.py > /dev/null \
  && node --test src/hooks/simple-korean-activate.test.js > /dev/null && python3 src/hooks/test_lint_hook.py > /dev/null \
  && python3 evals/ko_lint.py --gate skills/simple-korean/SKILL.md skills/simple-korean/references/*.md prompts/system-prompt.md output-styles/simple-korean.md > /dev/null; echo "exit=$?"
```

Expected: `self-test OK: ...` 한 줄과 `exit=0`.

Step 7에서 스킬 문서나 훅을 고쳤으면 플러그인 연기 시험도 다시 돌린다. 레포지토리 최상위에서 실행한다(`claude -p` 1번).

```bash
claude -p "규칙 블록에 있는 '이 프로젝트의 지정형' 단어 여섯 개를 쉼표로만 나열하세요. 규칙 블록이 없으면 NONE이라고 답하세요." \
  --plugin-dir "$PWD" --setting-sources "" --strict-mcp-config --model claude-sonnet-5-5 --effort low \
  --output-format stream-json --verbose --disallowedTools "Bash,Read,Write,Edit,Glob,Grep,WebFetch,WebSearch" \
  < /dev/null > /tmp/sk-smoke.jsonl
python3 - /tmp/sk-smoke.jsonl <<'SMOKE_EOF'
import json, sys
init, result, hooks = {}, None, []
for line in open(sys.argv[1], encoding="utf-8"):
    try:
        e = json.loads(line)
    except ValueError:
        continue
    if e.get("type") == "system" and e.get("subtype") == "init":
        init = e
    if e.get("type") == "system" and e.get("subtype") == "hook_response":
        hooks.append(e.get("output", ""))
    if e.get("type") == "result":
        result = e.get("result")
plugins = [p.get("name") for p in init.get("plugins") or []]
assert "simple-korean" in plugins, plugins
assert any(h.startswith("SIMPLE KOREAN 스킬이 자동으로 켜졌습니다") for h in hooks), hooks
assert all(w in (result or "") for w in ("레포지토리", "바디", "칼럼", "대상", "리디렉션", "리팩터링")), result
print("smoke OK:", result)
SMOKE_EOF
```

Expected: `smoke OK: 레포지토리, 바디, 칼럼, 대상, 리디렉션, 리팩터링`.

- [ ] **Step 9: 커밋한다**

```bash
git add evals/pressure-tests.md evals/run_pressure.py evals/tests/test_pressure.py "evals/results/$DATE/pressure" skills prompts output-styles src/hooks
git commit -m "test: add pressure scenarios and record skill behavior" -m $'Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01SanRSLxxVtkLMJh1wLGeGZ'
```

### Task 17: 본 측정

스펙 11.1의 2~3단계와 11.2다. 스킬 문서가 확정된 뒤에 돌린다. 호출은 112번이다(격리 확인 제외). 문서 48번과 답변 32번은 Sonnet 5.5, 판정 32번은 Opus 5.5다.

**Files:**
- Create(생성물): `evals/results/<날짜>/meta.json`, `docs/`(48개), `reply/`(32개), `judge/`(16개), `RESULTS.md`

**Interfaces:**
- Consumes: Task 14의 `bench_common.py --probe`, `run_bench.py`, `run_reply_bench.py`, `run_reply_bench.py --judge`, `report.py`, Task 13의 `.venv`(kiwipiepy 0.24.0)
- Produces: 완성된 결과 디렉터리 `evals/results/<날짜>/`(Task 18 수치 검증과 Task 19 README·전후 예시가 읽는다). 측정 날짜는 이 디렉터리 이름이다.

- [ ] **Step 1: 시작 조건을 확인한다**

Run: `git status --short && python3 evals/tests/run.py | grep -c '^ok'`
Expected: `git status` 출력이 비어 있다(Task 16의 스킬 수정까지 모두 커밋됐다). 이어서 `102`(Task 15 Step 7에서 회귀 시험을 더했으면 그 수만큼 많다).

- [ ] **Step 2: 격리를 확인한다**

Run:

```bash
DATE=$(date +%F); OUT="evals/results/$DATE"
python3 evals/bench_common.py --probe --out "$OUT"; echo "exit=$?"
```

Expected: `"problems": []`, `exit=0`. 문제가 있으면 측정하지 않고 문제 목록을 사용자에게 보인다.

- [ ] **Step 3: 문서, 답변, 판정을 만든다**

세 명령은 오래 걸리므로 백그라운드로 돌리고 끝날 때까지 기다린다. 중간에 멈추면 같은 명령을 다시 돌린다. 이미 있는 파일은 건너뛴다.

```bash
python3 evals/run_bench.py --out "$OUT"
python3 evals/run_reply_bench.py --out "$OUT"
python3 evals/run_reply_bench.py --out "$OUT" --judge
```

Expected: 문서는 `[1/48] baseline readme-intro r1`부터 `[48/48]`까지, 답변은 32줄, 판정은 `판정 <질문> r<회차>: <plain|tie|baseline>` 16줄이 나온다.

- [ ] **Step 4: 빠진 출력과 이상한 출력을 찾는다**

Run:

```bash
python3 - "$OUT" <<'PY'
import json
import sys
from pathlib import Path
out = Path(sys.argv[1])
docs = sorted((out / "docs").glob("*.json"))
replies = sorted((out / "reply").glob("*.txt"))
judges = [json.loads(p.read_text(encoding="utf-8")) | {"file": p.name} for p in sorted((out / "judge").glob("*.json"))]
short = [p.name for p in docs if len(json.loads(p.read_text(encoding="utf-8"))["text"].strip()) < 100]
short += [p.name for p in replies if len(p.read_text(encoding="utf-8").strip()) < 20]
unread = [j["file"] for j in judges if j["order1_baseline_first"] is None or j["order2_plain_first"] is None]
print(f"docs {len(docs)}, reply {len(replies)}, judge {len(judges)}, 짧은 출력 {short}, 판정 못 읽음 {unread}")
PY
```

Expected: `docs 48, reply 32, judge 16, 짧은 출력 [], 판정 못 읽음 []`.

짧은 출력은 열어 읽는다. API 오류 문구나 거절이면 그 파일을 지우고 Step 3의 해당 명령을 다시 돌린다. 판정을 못 읽은 파일은 지우고 `--judge`를 한 번 더 돌린다. 그래도 못 읽으면 그대로 둔다. 무승부로 센다.

- [ ] **Step 5: RESULTS.md를 만들고 결과를 확인한다**

Run: `.venv/bin/python evals/report.py "$OUT"`
Expected: README 블록이 출력된다. 문서 표의 '쉬운 단어 비율' 칸이 '측정 안 함'이 아니라 백분율이다. `$OUT/RESULTS.md`가 생긴다.

조건마다 1회차 문서 세 개(readme-intro, troubleshooting, error-message)와 판정 JSON 16개를 읽는다. 측정이 의도대로 돌았는지 확인하기 위해서다.

결과가 기대와 달라도 수치를 고치거나 다시 돌려 고르지 않는다. SimpleKorean의 '독자가 보는 결함'이 기준선보다 많거나, 판정에서 진 쌍이 이긴 쌍보다 많으면 멈춘다. 그리고 README 블록을 사용자에게 보이고 다음 단계를 묻는다.

- [ ] **Step 6: 커밋한다**

```bash
git add "$OUT"
git commit -m "feat: add v1.0.0 benchmark results" -m $'Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01SanRSLxxVtkLMJh1wLGeGZ'
```

---

## 단계 E: 문서와 공개

### Task 18: 수치 검증과 CI

스펙 11.4와 13절이다. 공개하는 수치와 글을 원본 파일에서 다시 만들어 대조하는 도구를 먼저 만들고, Task 19에서 그 도구로 README를 확인한다. 전후 예시의 과제와 질문은 이 Task에서 코드(`PICKS`)로 정한다. 측정 결과를 보고 고르지 않게 하기 위해서다.

**Files:**
- Create: `evals/make_examples.py`, `evals/check_numbers.py`, `.github/workflows/check.yml`
- Test: `evals/tests/test_check_numbers.py`

**Interfaces:**
- Consumes: Task 14의 `report.README_BLOCK`, `readme_block`, `results_md`, `replace_readme_block`, `bench_common.rule_block`, Task 15의 `hits.record_md`, `hits.read_tsv`, `hits.to_tsv`, `hits.doc_rows`, `hits.reply_rows`, Task 13의 `metrics.easy_word_counts`, Task 8의 SKILL.md `metadata.version`과 핵심 문구, Task 12의 매니페스트 세 개
- Produces: `make_examples.RUN`(1), `DOC_PICKS`, `REPLY_PICKS`, `README_PICK`, `EXAMPLE_BLOCK`, `SOURCE_BLOCK`, `quote(text)`, `unquote(block)`, `raw_text(rel)`, `source_block(rel)`, `examples_md(results_dir) -> str`, `readme_example(results_dir) -> str`, `replace_example_block(readme_text, body) -> str`, `check_sources(markdown) -> list[str]`, CLI `python3 evals/make_examples.py <결과 디렉터리> [--readme]`. `check_numbers.KEY_PHRASES`, `VERSION_PATTERNS`, `REQUIRED`, `check_benchmark(readme, changelog, scenarios, require_easy=True)`, `check_examples(readme, examples)`, `check_calibration(changelog, calibration=CALIBRATION)`, `check_rule_block(prompt_md, style_md, skill_md)`, `check_versions(texts)`, `main() -> int`. README 표시: `<!-- benchmark:start <결과 경로> -->`와 `<!-- benchmark:end -->`, `<!-- example:start -->`와 `<!-- example:end -->`, 인용 블록 `<!-- source: <원본 경로> -->` 다음 줄부터 꺼짐 표시 사이. CI 작업 `check`(Node 24, Python 3.12, kiwipiepy)와 `python39`.

- [ ] **Step 1: 실패하는 테스트를 쓴다**

`evals/tests/test_check_numbers.py`:

```python
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import check_numbers as cn  # noqa: E402
import hits  # noqa: E402  check_numbers가 evals/calibration을 경로에 넣는다
import make_examples as mx  # noqa: E402
import report  # noqa: E402

BLOCK = '서술형으로 답하세요. em-dash를 쓰지 마세요. 첫 문장에 답을 쓰세요. 코드는 바꾸지 마세요. "확인하다" 하나로 쓰세요. 레포지토리.'
SKILL = f'---\nname: simple-korean\nmetadata:\n  version: "1.0.0"\n---\n{BLOCK}\n'
ISO = {"found": True, "claude_code_version": "2.1.294", "model": "m", "mcp_servers": [], "plugins": [],
       "output_style": "default", "memory_paths": []}


def test_quote_round_trip_keeps_blank_lines_and_markers():
    text = "첫 줄\n\n> 이미 인용\n  들여쓴 줄\n- 목록 **굵게**\n"
    assert mx.unquote(mx.quote(text)) == text.rstrip("\n")
    assert mx.quote("a\n\nb") == "> a\n>\n> b"


def test_check_rule_block_flags_drift_and_missing_phrases():
    prompt = f"# 시스템 프롬프트\n\n---\n{BLOCK}\n---\n\n짧은 판본\n"
    style = f"---\nname: x\n---\n{BLOCK}\n"
    assert cn.check_rule_block(prompt, style, SKILL) == []
    assert any("규칙 블록이 다릅니다" in p for p in cn.check_rule_block(prompt, style + "더함\n", SKILL))
    missing = cn.check_rule_block(prompt, style, SKILL.replace("레포지토리", "저장소"))
    assert missing == ["SKILL.md에 핵심 문구가 없습니다: 레포지토리"]


def test_check_versions_requires_one_value_everywhere():
    texts = {
        "skills/simple-korean/SKILL.md": SKILL,
        ".claude-plugin/plugin.json": '{"version": "1.0.0"}',
        ".claude-plugin/marketplace.json": '{"plugins": [{"version": "1.0.0"}]}',
        ".codex-plugin/plugin.json": '{"version": "1.0.0"}',
        "README.md": "badge/version-1.0.0-blue",
        "CHANGELOG.md": "# 변경 기록\n\n## 1.0.0, 2026-10-09\n",
    }
    assert cn.check_versions(texts) == []
    assert cn.check_versions({**texts, "CHANGELOG.md": "## 1.0.1, 2026-10-10\n"}) != []
    assert cn.check_versions({**texts, "README.md": "배지 없음"}) != []


def _results(d):
    """ROOT 아래 임시 결과 디렉터리에 답변, 판정, 문서, meta.json을 쓴다."""
    root = Path(d)
    (root / "reply").mkdir()
    (root / "reply" / "baseline__oom__r1.txt").write_text("**네** — 메모리가 부족합니다.\n\n- 한도\n", encoding="utf-8")
    (root / "reply" / "plain__oom__r1.txt").write_text("메모리 한도를 넘어서 파드가 끝났습니다.", encoding="utf-8")
    (root / "judge").mkdir()
    (root / "judge" / "oom__r1.json").write_text(json.dumps({"winner": "plain"}), encoding="utf-8")
    (root / "docs").mkdir()
    for cond in ("baseline", "plain", "strict"):
        record = {"condition": cond, "scenario": "readme-intro", "text": "메세지를 보냅니다. 서버에 대해 설명합니다."}
        (root / "docs" / f"{cond}__readme-intro__r1.json").write_text(json.dumps(record, ensure_ascii=False), encoding="utf-8")
    meta = {"date": "2099-01-01", "model": "m", "effort": "low", "judge_model": "j", "isolation": ISO, "isolation_problems": []}
    (root / "meta.json").write_text(json.dumps(meta), encoding="utf-8")
    return root


def test_readme_example_is_verbatim_and_edits_are_caught():
    with tempfile.TemporaryDirectory(dir=str(cn.ROOT / "evals")) as d:
        readme = mx.replace_example_block("앞\n<!-- example:start -->\n\n<!-- example:end -->\n", mx.readme_example(_results(d)))
        assert cn.check_examples(readme, "") == []
        assert "<!-- simple-korean: off -->\n> **네** — 메모리가 부족합니다.\n>\n> - 한도" in readme
        edited = readme.replace("파드가 끝났습니다", "파드가 끝났어요")
        assert any("인용한 글이 원본과 다릅니다" in p for p in cn.check_examples(edited, ""))
    assert cn.check_examples("빈 README", "") == ["README.md에 원본 인용 블록이 없습니다"]


def test_check_benchmark_catches_stale_numbers_and_missing_changelog_path():
    scenarios = [{"id": "readme-intro", "type": "descriptive"}]
    with tempfile.TemporaryDirectory(dir=str(cn.ROOT / "evals")) as d:
        root = _results(d)
        rel = root.resolve().relative_to(cn.ROOT).as_posix()
        readme = report.replace_readme_block("<!-- benchmark:start x -->\n\n<!-- benchmark:end -->\n", root,
                                             report.readme_block(root, scenarios))
        (root / "RESULTS.md").write_text(report.results_md(root, scenarios), encoding="utf-8")
        changelog = f"결과는 {rel}/RESULTS.md에 있습니다."
        assert cn.check_benchmark(readme, changelog, scenarios, require_easy=False) == []
        stale = readme.replace("| 스킬 없음 | 1 |", "| 스킬 없음 | 2 |", 1)
        assert any("README 벤치마크 블록" in p for p in cn.check_benchmark(stale, changelog, scenarios, require_easy=False))
        assert any("CHANGELOG.md가 측정 결과" in p for p in cn.check_benchmark(readme, "", scenarios, require_easy=False))
    assert cn.check_benchmark("블록 없음", "", scenarios) == ["README.md에 벤치마크 블록이 없습니다"]


def test_check_calibration_rebuilds_record_and_needs_changelog_lines():
    with tempfile.TemporaryDirectory() as d:
        cal, base = Path(d), Path(d) / "baseline"
        (base / "docs").mkdir(parents=True)
        (base / "reply").mkdir()
        record = {"text": "이 문서는 sqlpipe에 대해 설명합니다.\n", "condition": "baseline", "scenario": "x",
                  "type": "descriptive", "run": 1}
        (base / "docs" / "baseline__x__r1.json").write_text(json.dumps(record, ensure_ascii=False), encoding="utf-8")
        (base / "meta.json").write_text(json.dumps({"date": "2026-10-09", "model": "m", "effort": "low"}), encoding="utf-8")
        rows = [{**r, "label": "TP"} for r in hits.doc_rows(base) + hits.reply_rows(base)]
        (cal / "hits.tsv").write_text(hits.to_tsv(rows), encoding="utf-8")
        text = hits.record_md(base, rows)
        (cal / "RECORD.md").write_text(text, encoding="utf-8")
        lines = text.split("## CHANGELOG에 옮길 줄", 1)[1].strip()
        assert cn.check_calibration(lines, cal) == []
        assert any("CHANGELOG.md에 보정 줄이 없습니다" in p for p in cn.check_calibration("", cal))
        (cal / "RECORD.md").write_text(text.replace("그대로입니다", "바뀌었습니다"), encoding="utf-8")
        assert any(p.startswith("evals/calibration/RECORD.md:") for p in cn.check_calibration(lines, cal))


def test_main_reports_missing_files():
    old = cn.ROOT
    with tempfile.TemporaryDirectory() as d:
        cn.ROOT = Path(d)
        try:
            assert cn.main() == 1
        finally:
            cn.ROOT = old
```

- [ ] **Step 2: 테스트를 돌려 실패를 확인한다**

Run: `python3 evals/tests/run.py evals/tests/test_check_numbers.py`
Expected: `ModuleNotFoundError: No module named 'check_numbers'`로 실패한다.

- [ ] **Step 3: 전후 예시 생성기와 수치 검증 도구를 쓴다**

인용 블록은 원본 출력을 한 글자도 바꾸지 않고 줄마다 `> `만 붙인다. 원본 출력에는 규칙 위반이 들어 있으므로 꺼짐 표시로 감싼다. 그래야 README가 린트 관문을 통과한다.

`evals/make_examples.py`:

```python
#!/usr/bin/env python3
"""전후 예시를 원본 출력에서 만든다. 고를 과제와 질문은 측정 전에 정했다(PICKS). 글은 고치지 않는다.

    python3 evals/make_examples.py evals/results/<날짜>            # examples/before-after.md를 쓴다
    python3 evals/make_examples.py evals/results/<날짜> --readme   # README.md의 보기 블록도 바꾼다
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
EXAMPLES = ROOT / "examples" / "before-after.md"
RUN = 1
DOC_PICKS = (
    ("readme-intro", "plain", "README 소개(설명문)"),
    ("troubleshooting", "plain", "문제 해결(절차문)"),
    ("error-message", "plain", "오류 메시지"),
    ("release-notes", "strict", "릴리스 노트(엄격 모드)"),
)
REPLY_PICKS = (("oom", "OOMKilled 질문"), ("cache", "캐시 무효화 질문"))
README_PICK = "oom"
COND_LABELS = {"plain": "기본 모드", "strict": "엄격 모드"}
EXAMPLE_BLOCK = re.compile(r"<!-- example:start -->\n(.*?)\n<!-- example:end -->", re.S)
SOURCE_BLOCK = re.compile(
    r"<!-- source: (\S+) -->\n<!-- simple-korean: off -->\n(.*?)\n<!-- simple-korean: on -->", re.S)


def quote(text):
    """원문을 인용 블록으로 바꾼다. 빈 줄에는 '>'만 남긴다."""
    return "\n".join(f"> {line}" if line else ">" for line in text.rstrip("\n").split("\n"))


def unquote(block):
    return "\n".join(re.sub(r"^> ?", "", line) for line in block.split("\n"))


def raw_text(rel):
    """레포지토리 기준 경로의 원본 출력. 문서는 JSON의 text, 답변은 파일 내용이다."""
    path = ROOT / rel
    data = path.read_text(encoding="utf-8")
    return json.loads(data)["text"] if path.suffix == ".json" else data


def source_block(rel):
    return f"<!-- source: {rel} -->\n<!-- simple-korean: off -->\n{quote(raw_text(rel))}\n<!-- simple-korean: on -->"


def _pair(results_dir, sub, item, cond, ext):
    base = Path(results_dir, sub).resolve().relative_to(ROOT).as_posix()
    return f"{base}/baseline__{item}__r{RUN}.{ext}", f"{base}/{cond}__{item}__r{RUN}.{ext}"


def _section(title, before, after, after_label):
    return "\n\n".join([f"## {title}", f"전: 스킬 없음, `{before}`", source_block(before),
                        f"후: {after_label}, `{after}`", source_block(after)])


def examples_md(results_dir):
    """examples/before-after.md 전체."""
    parts = ["# 전후 예시",
             "'전'은 스킬 없이 만든 원본 출력이고, '후'는 같은 과제를 스킬을 켜고 만든 원본 출력입니다. "
             "두 글 모두 고치지 않고 옮겼습니다. 과제와 질문은 측정 전에 정했습니다(`evals/make_examples.py`의 PICKS). "
             "`python3 evals/check_numbers.py`가 이 파일의 글을 원본 파일과 글자 하나까지 대조합니다."]
    for scenario, cond, title in DOC_PICKS:
        before, after = _pair(results_dir, "docs", scenario, cond, "json")
        parts.append(_section(title, before, after, COND_LABELS[cond]))
    for question, title in REPLY_PICKS:
        before, after = _pair(results_dir, "reply", question, "plain", "txt")
        parts.append(_section(f"답변: {title}", before, after, "SimpleKorean"))
    return "\n\n".join(parts) + "\n"


def readme_example(results_dir):
    """README 보기 블록의 본문."""
    before, after = _pair(results_dir, "reply", README_PICK, "plain", "txt")
    return "\n\n".join([f"스킬 없이 쓴 답변(`{before}`):", source_block(before),
                        f"같은 모델이 SimpleKorean을 켜고 쓴 답변(`{after}`):", source_block(after),
                        "문서 예시는 [`examples/before-after.md`](examples/before-after.md)에 있습니다."])


def replace_example_block(readme_text, body):
    """README의 보기 블록을 새 본문으로 바꾼 새 문자열."""
    if not EXAMPLE_BLOCK.search(readme_text):
        raise SystemExit("README.md에 <!-- example:start --> 블록이 없습니다")
    return EXAMPLE_BLOCK.sub(lambda m: f"<!-- example:start -->\n{body}\n<!-- example:end -->", readme_text, count=1)


def check_sources(markdown):
    """인용 블록마다 원본 파일과 같은지 확인해 문제 목록을 돌려준다."""
    problems = []
    for m in SOURCE_BLOCK.finditer(markdown):
        rel = m.group(1)
        try:
            expected = raw_text(rel).rstrip("\n")
        except (OSError, ValueError, KeyError) as err:
            problems.append(f"{rel}: 원본을 읽지 못했습니다({err})")
            continue
        if unquote(m.group(2)) != expected:
            problems.append(f"{rel}: 인용한 글이 원본과 다릅니다")
    return problems


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if not args:
        raise SystemExit("사용법: make_examples.py <결과 디렉터리> [--readme]")
    EXAMPLES.parent.mkdir(parents=True, exist_ok=True)
    EXAMPLES.write_text(examples_md(args[0]), encoding="utf-8")
    if "--readme" in args:
        readme = ROOT / "README.md"
        readme.write_text(replace_example_block(readme.read_text(encoding="utf-8"), readme_example(args[0])),
                          encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

`evals/check_numbers.py`:

```python
#!/usr/bin/env python3
"""공개한 수치와 글을 원본 파일에서 다시 만들어 대조한다. CI가 푸시마다 돌린다.

쉬운 단어 비율을 다시 계산하려면 kiwipiepy가 있어야 한다. 로컬에서는 측정용 가상 환경으로 돌린다.

    .venv/bin/python evals/check_numbers.py

검사하는 것:
- README의 벤치마크 블록과 RESULTS.md를 원본 출력에서 다시 만든 글과 비교한다(report.py).
- README와 examples/before-after.md의 인용 블록을 원본 출력과 비교한다(make_examples.py).
- 보정 기록 RECORD.md를 hits.tsv와 보정 출력에서 다시 만들어 비교하고, CHANGELOG에 보정 줄이 있는지 본다.
- 규칙 블록 두 벌이 같은지, 핵심 문구가 SKILL.md와 규칙 블록에 모두 있는지 본다.
- 버전 문자열이 SKILL.md, 매니페스트 세 개, README 배지, CHANGELOG 첫 항목에서 같은지 본다.
"""
import difflib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CALIBRATION = HERE / "calibration"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(CALIBRATION))
import bench_common  # noqa: E402
import hits  # noqa: E402
import make_examples  # noqa: E402
import metrics  # noqa: E402
import report  # noqa: E402

KEY_PHRASES = ("서술형으로 답하세요", "em-dash를 쓰지 마세요", "첫 문장에 답", "바꾸지 마세요", "확인하다", "레포지토리")
VERSION_PATTERNS = {
    "skills/simple-korean/SKILL.md": r'version:\s*"([^"]+)"',
    ".claude-plugin/plugin.json": r'"version":\s*"([^"]+)"',
    ".claude-plugin/marketplace.json": r'"version":\s*"([^"]+)"',
    ".codex-plugin/plugin.json": r'"version":\s*"([^"]+)"',
    "README.md": r"badge/version-([0-9.]+)-",
    "CHANGELOG.md": r"(?m)^## ([0-9]+\.[0-9]+\.[0-9]+)",
}


def _diff(label, expected, found):
    lines = difflib.unified_diff(found.splitlines(), expected.splitlines(), "지금 글", "다시 만든 글", lineterm="", n=1)
    return f"{label}: 원본에서 다시 만든 글과 다릅니다\n" + "\n".join(list(lines)[:40])


def check_benchmark(readme, changelog, scenarios, require_easy=True):
    """README 벤치마크 블록, RESULTS.md, CHANGELOG의 결과 경로를 확인한다.

    require_easy가 참이면 kiwipiepy가 없을 때 멈춘다. 없으면 쉬운 단어 비율이 '측정 안 함'으로 바뀌어
    공개한 표와 달라지기 때문이다. 단위 시험만 이 값을 끈다.
    """
    m = report.README_BLOCK.search(readme)
    if not m:
        return ["README.md에 벤치마크 블록이 없습니다"]
    rel, results_dir = m.group(1), ROOT / m.group(1)
    if require_easy and metrics.easy_word_counts("확인합니다.") is None:
        return ["kiwipiepy가 없어 쉬운 단어 비율을 다시 계산하지 못했습니다. .venv/bin/python으로 돌리세요"]
    problems = []
    block = report.readme_block(results_dir, scenarios)
    if m.group(2) != block:
        problems.append(_diff("README 벤치마크 블록", block, m.group(2)))
    rebuilt = report.results_md(results_dir, scenarios)
    current = (results_dir / "RESULTS.md").read_text(encoding="utf-8")
    if current != rebuilt:
        problems.append(_diff(f"{rel}/RESULTS.md", rebuilt, current))
    if rel not in changelog:
        problems.append(f"CHANGELOG.md가 측정 결과 {rel}을 가리키지 않습니다")
    return problems


def check_examples(readme, examples):
    problems = make_examples.check_sources(readme) + make_examples.check_sources(examples)
    if not make_examples.SOURCE_BLOCK.search(readme):
        problems.append("README.md에 원본 인용 블록이 없습니다")
    return problems


def check_calibration(changelog, calibration=CALIBRATION):
    """RECORD.md를 다시 만들어 비교하고, 'CHANGELOG에 옮길 줄'이 CHANGELOG에 있는지 본다."""
    try:
        rebuilt = hits.record_md(Path(calibration) / "baseline", hits.read_tsv(Path(calibration) / "hits.tsv"))
    except SystemExit as err:
        return [f"보정 기록을 다시 만들지 못했습니다: {err}"]
    current = (Path(calibration) / "RECORD.md").read_text(encoding="utf-8")
    problems = [] if current == rebuilt else [_diff("evals/calibration/RECORD.md", rebuilt, current)]
    for line in rebuilt.split("## CHANGELOG에 옮길 줄", 1)[1].strip().splitlines():
        text = line.lstrip("- ").strip()
        if text and text not in changelog:
            problems.append(f"CHANGELOG.md에 보정 줄이 없습니다: {text}")
    return problems


def check_rule_block(prompt_md, style_md, skill_md):
    """규칙 블록 두 벌이 같고, 핵심 문구가 SKILL.md와 규칙 블록에 모두 있는지 본다."""
    prompt = bench_common.rule_block(prompt_md)
    style = re.sub(r"\A---\n.*?\n---\n", "", style_md, count=1, flags=re.S).strip()
    problems = [] if prompt == style else ["prompts/system-prompt.md와 output-styles/simple-korean.md의 규칙 블록이 다릅니다"]
    for phrase in KEY_PHRASES:
        problems += [f"{name}에 핵심 문구가 없습니다: {phrase}"
                     for name, text in (("SKILL.md", skill_md), ("규칙 블록", prompt)) if phrase not in text]
    return problems


def check_versions(texts):
    """{경로: 글}에서 버전 문자열을 꺼내 모두 같은지 본다."""
    found = {}
    for name, pattern in VERSION_PATTERNS.items():
        m = re.search(pattern, texts[name])
        found[name] = m.group(1) if m else None
    return [] if None not in found.values() and len(set(found.values())) == 1 else [f"버전 문자열이 다릅니다: {found}"]


REQUIRED = ("README.md", "CHANGELOG.md", "examples/before-after.md", "evals/scenarios.json",
            "evals/calibration/RECORD.md", "evals/calibration/hits.tsv", "prompts/system-prompt.md",
            "output-styles/simple-korean.md") + tuple(VERSION_PATTERNS)


def _read(rel):
    return (ROOT / rel).read_text(encoding="utf-8")


def main():
    missing = sorted({rel for rel in REQUIRED if not (ROOT / rel).is_file()})
    if missing:
        print("MISMATCH")
        print("\n".join(f" - 파일이 없습니다: {rel}" for rel in missing))
        return 1
    readme, changelog = _read("README.md"), _read("CHANGELOG.md")
    problems = (check_benchmark(readme, changelog, json.loads(_read("evals/scenarios.json")))
                + check_examples(readme, _read("examples/before-after.md"))
                + check_calibration(changelog)
                + check_rule_block(_read("prompts/system-prompt.md"), _read("output-styles/simple-korean.md"),
                                   _read("skills/simple-korean/SKILL.md"))
                + check_versions({name: _read(name) for name in VERSION_PATTERNS}))
    if problems:
        print("MISMATCH")
        for problem in problems:
            print(" -", problem)
        return 1
    print("check_numbers OK: 공개한 수치와 글이 원본 파일과 같습니다")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: 테스트를 돌려 통과를 확인한다**

Run: `chmod +x evals/make_examples.py evals/check_numbers.py && python3 evals/tests/run.py evals/tests/test_check_numbers.py && /usr/bin/python3 evals/tests/run.py evals/tests/test_check_numbers.py && python3 evals/tests/run.py | grep -c '^ok' && .venv/bin/python evals/tests/run.py | grep -c '^ok'`
Expected: 앞의 두 번은 `ok` 7줄, 이어서 `109`와 `109`(kiwipiepy가 있는 가상 환경에서도 같다). Task 15 Step 7에서 회귀 시험을 더했으면 두 수 모두 그만큼 많다.

- [ ] **Step 5: CI 작업을 쓴다**

GitHub Actions 주 버전은 2026-10-08에 확인한 최신판이다(checkout v7.0.1, setup-node v7.1.0, setup-python v7.0.0). Python 3.9.25 빌드는 ubuntu 22.04와 24.04에 있다. `python39` 작업은 린터와 훅이 macOS 기본 Python 3.9에서 돈다는 Global Constraints를 지킨다.

`.github/workflows/check.yml`:

```yaml
name: check
on: [push, pull_request]
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - uses: actions/setup-node@v7
        with: { node-version: 24 }
      - uses: actions/setup-python@v7
        with: { python-version: "3.12" }
      - run: python3 -m pip install kiwipiepy==0.24.0
      - run: python3 evals/ko_lint.py --self-test
      - run: python3 evals/tests/run.py
      - run: node --test src/hooks/simple-korean-activate.test.js
      - run: python3 src/hooks/test_lint_hook.py
      - run: python3 evals/check_numbers.py
      - run: python3 evals/ko_lint.py --gate skills/simple-korean/SKILL.md skills/simple-korean/references/*.md prompts/system-prompt.md output-styles/simple-korean.md README.md
  python39:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - uses: actions/setup-python@v7
        with: { python-version: "3.9" }
      - run: python3 evals/ko_lint.py --self-test
      - run: python3 evals/tests/run.py
      - run: python3 src/hooks/test_lint_hook.py
```

Run: `ruby -ryaml -e 'y = YAML.load_file(".github/workflows/check.yml"); puts "yaml ok: #{y["jobs"].keys.join(",")}"' 2>/dev/null`
Expected: `yaml ok: check,python39`.

- [ ] **Step 6: 지금 상태를 수치 검증으로 확인한다**

Run: `.venv/bin/python evals/check_numbers.py; echo "exit=$?"`
Expected: README와 CHANGELOG와 전후 예시가 아직 없으므로 실패한다. 출력은 정확히 다음과 같다.

```text
MISMATCH
 - 파일이 없습니다: CHANGELOG.md
 - 파일이 없습니다: README.md
 - 파일이 없습니다: examples/before-after.md
exit=1
```

- [ ] **Step 7: 커밋한다**

```bash
git add evals/make_examples.py evals/check_numbers.py evals/tests/test_check_numbers.py .github/workflows/check.yml
git commit -m "ci: verify published numbers and quotes against raw files" -m $'Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01SanRSLxxVtkLMJh1wLGeGZ'
```

### Task 19: README, 전후 예시, CHANGELOG

스펙 12절이다. README는 한국어로 쓰고 맨 위에 영어 소개를 한 문단 둔다. README도 스킬 규칙을 지켜야 하므로 린트 관문을 통과해야 한다. 수치는 손으로 쓰지 않는다. 벤치마크 블록은 `report.py`가, 보기 블록은 `make_examples.py`가 원본 출력에서 만든다.

**Files:**
- Create: `README.md`, `CHANGELOG.md`, `examples/before-after.md`(생성물)

**Interfaces:**
- Consumes: Task 17의 `evals/results/<날짜>/`, Task 15의 `evals/calibration/RECORD.md`, Task 18의 `make_examples.py`, `check_numbers.py`, Task 14의 `report.py --readme`
- Produces: `README.md`(배지 `version-1.0.0`, 벤치마크 블록, 보기 블록), `CHANGELOG.md`(첫 항목 `## 1.0.0, <측정 날짜>`), `examples/before-after.md`. Task 20이 이 상태를 공개한다.

- [ ] **Step 1: README를 쓴다**

두 블록은 비워 둔다. 블록 안의 빈 줄은 지우지 않는다. 블록 정규식이 시작 표시와 끝 표시 사이의 줄바꿈 두 개를 찾기 때문이다.

`README.md`:

````markdown
<p align="center">
  <strong>AI가 쓴 한국어 기술 문서를 정비 매뉴얼처럼 읽히게 합니다.</strong>
</p>

<p align="center">
  <a href="https://agentskills.io"><img src="https://img.shields.io/badge/SKILL.md-open_standard-blue?style=flat" alt="Agent Skills"></a>
  <a href="skills/simple-korean/SKILL.md"><img src="https://img.shields.io/badge/version-1.0.0-blue?style=flat" alt="version 1.0.0"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-lightgrey?style=flat" alt="MIT"></a>
</p>

SimpleKorean is an agent skill that makes LLMs write plain Korean in technical documents and chat replies. It adapts the rules of ASD-STE100 Simplified Technical English, by way of the SimpleEnglish skill, to Korean grammar. It adds a loanword spelling list measured on real Korean developer text. The rest of this README is in Korean.

SimpleKorean은 LLM이 기술 문서와 채팅 답변을 쉬운 한국어로 쓰게 하는 에이전트 스킬입니다. 항공 정비 매뉴얼에 쓰는 통제 영어 ASD-STE100의 규칙을 [SimpleEnglish](https://github.com/AminBlg/SimpleEnglish)에서 가져와 한국어 문법에 맞게 다시 세웠습니다. 여기에 실제 한국어 개발 문서에서 잰 외래어 표기 목록을 더했습니다.

[Agent Skills 표준](https://agentskills.io)을 읽는 에이전트에서 돌아갑니다. Claude Code, Cursor, Codex, Gemini CLI, OpenCode가 그 예입니다.

## 설치

모든 에이전트에는 [skills CLI](https://github.com/vercel-labs/skills)로 설치하세요.

```bash
pnpm dlx skills add say8425/SimpleKorean
```

npm을 쓰면 `npx skills add say8425/SimpleKorean`을 실행하세요. 이 명령은 스킬만 설치합니다. 아래의 훅과 출력 스타일은 설치하지 않습니다.

Claude Code에는 플러그인으로 설치하세요. 플러그인에는 세션 시작 훅, 글쓰기 점검 훅, 출력 스타일이 들어 있습니다.

```bash
claude plugin marketplace add say8425/SimpleKorean && claude plugin install simple-korean@simple-korean
```

출력 스타일 이름은 `simple-korean:simple-korean`입니다. 짧은 이름으로는 찾지 못합니다. `/config`의 Output style에서 고르거나, `~/.claude/settings.json`에 `{"outputStyle": "simple-korean:simple-korean"}`을 넣으세요. 토큰 비용은 `claude plugin details simple-korean`으로 볼 수 있습니다.

Codex에는 플러그인으로 설치하세요. 세션 시작 훅이 함께 설치됩니다.

```bash
codex plugin marketplace add say8425/SimpleKorean
codex plugin add simple-korean@simple-korean
```

Codex는 훅을 처음 돌리기 전에 믿을지 묻습니다. 세션 시작 훅에는 Node.js가 필요하고, Claude Code의 글쓰기 점검 훅에는 Python 3.9 이상이 필요합니다. 자세한 내용은 [`src/hooks/README.md`](src/hooks/README.md)에 있습니다.

스킬을 지원하지 않는 도구에는 [`prompts/system-prompt.md`](prompts/system-prompt.md)의 규칙 블록을 붙여 넣으세요. 시스템 프롬프트, `AGENTS.md`, `.cursorrules`에 넣으면 됩니다. 이 파일 끝에는 약 120토큰짜리 짧은 판본도 있습니다.

설치한 뒤에는 기술 문서를 요청하세요. 이미 있는 글을 고치려면 "simple-korean으로 고쳐 줘"라고 말하세요.

## 보기

같은 질문에 같은 모델이 답한 원본 출력입니다. 두 답변 모두 고치지 않고 옮겼습니다.

<!-- example:start -->

<!-- example:end -->

## 벤치마크

아래 수치는 모두 커밋한 원본 출력에서 다시 계산한 값입니다. CI가 푸시마다 `evals/check_numbers.py`로 대조합니다. 모든 실행은 `claude-sonnet-5-5`, effort low이고, 사용자 설정과 MCP 서버를 읽지 않았습니다. 판정 모델도 Claude라서 같은 계열에 유리한 편향이 있을 수 있습니다.

<!-- benchmark:start evals/results/YYYY-MM-DD -->

<!-- benchmark:end -->

## 규칙

규칙은 [`SKILL.md`](skills/simple-korean/SKILL.md)에 있습니다. 점검 모드와 엄격 모드에서 쓰는 K 번호 규칙 전체는 [`rule-catalog.md`](skills/simple-korean/references/rule-catalog.md)에 있습니다.

채팅 답변에는 모든 모드에서 이 규칙을 씁니다.

| 규칙 | 막는 것 |
|---|---|
| 서술형으로 답합니다. 헤더, 불릿, 굵은 글씨, 표를 쓰지 않습니다 | 한 줄짜리 답을 둘러싼 서식 |
| 첫 문장에 답을 씁니다 | 질문을 되풀이하는 머리말 |
| em-dash를 쓰지 않습니다 | 반쯤 이어 붙인 생각 |
| 개념 용어는 처음 쓸 때 짧게 풀이합니다 | 독자가 찾아봐야 하는 용어 |
| 한 답변은 한 문체로 쓰고, 인사말과 맺음말을 쓰지 않습니다 | "좋은 질문입니다", "도움이 되셨기를 바랍니다" |

문서에는 이 규칙을 씁니다. README, 런북, 오류 메시지, 릴리스 노트, 장애 보고서가 여기에 들어갑니다.

| 규칙 | 막는 것 |
|---|---|
| 절차문은 15어절, 설명문은 20어절 이하로 씁니다 | 끝없이 이어지는 만연체 |
| 조건은 "-면"으로 명령 앞에 둡니다 | 명령 뒤에 붙어 늦게 읽히는 "단, ~경우" |
| 능동태와 단순 시제로 씁니다 | "되어지다", "~에 의해", "-고 있습니다" |
| 짐작과 권고 어미를 쓰지 않습니다 | "-ㄹ 수도 있습니다", "-것 같습니다", "-하는 것이 좋습니다" |
| 한 단어에는 한 뜻만 줍니다 | "확인", "검증", "점검", "체크"를 번갈아 쓰기 |
| 조사를 빼지 않고 명사형으로 끝내지 않습니다 | "백업 확인 필요" 같은 전보문 |
| 중요성 말고 사실을 씁니다 | "강력한", "원활한", "단순히 X가 아니라 Y" |
| 정해진 외래어 표기를 씁니다 | 한 문서 안에 섞인 "디렉토리"와 "디렉터리" |

## 모드

기본 모드는 위의 규칙 전부입니다. 따로 켜지 않아도 됩니다.

엄격 모드는 "엄격 모드", "통제 언어", "KS A 0001", "STE"라고 말하면 켜집니다. 엄격 모드는 문서의 문장 끝을 다섯 가지로 닫습니다. 의무는 "-해야 합니다", 금지는 "-하면 안 됩니다", 허용은 "-해도 됩니다", 능력은 "-ㄹ 수 있습니다", 사실은 현재형입니다. 접속어 "(이)나"를 쓰지 않고, 조건은 "-면"으로만 씁니다. 근거는 KS A 0001:2023 부속서 H와 I입니다. 답변은 엄격 모드에서도 기본 모드 규칙을 따릅니다.

점검 모드는 글 대신 점검을 요청하면 켜집니다. 위반마다 K 번호, 해당 문구, 고친 문장을 알려 줍니다.

## 표기 정책

외래어는 외래어 표기법과 국립국어원 용례를 따릅니다(디렉터리, 메시지, 애플리케이션). 원칙만으로 답이 나오지 않는 단어는 [`data/terms.json`](data/terms.json)의 목록을 따릅니다. 이 목록은 현지화 문서, 벤더 문서, 기업 기술 블로그, GitHub README에서 실제 표기를 세어 만들었습니다. 근거는 [`docs/research/loanword-spelling-usage.md`](docs/research/loanword-spelling-usage.md)에 있습니다.

| 무리 | 쓰는 형태 |
|---|---|
| 규범대로 쓰이는 단어 23개 | 규범형(메시지, 애플리케이션, 메서드, 라이선스) |
| 출처마다 갈리는 단어 4개 | 규범형(디렉터리, 릴리스, 셸, 리디렉션) |
| 관용이 굳은 단어 4개 | 레포지토리, 바디, 칼럼, 대상 |
| 공식 표기가 없는 단어 2개 | 리디렉션, 리팩터링 |
| 외래어와 우리말 가운데 고르는 단어 5개 | 오류, 매개변수, 사용자, 기본값, 배포 |
| 띄어쓰기 4개 | 기본값, 매개변수, 반환값, 오픈소스(붙여 씀) |

제품 이름, 화면 문구 인용, API 객체 이름, 코드는 원래 표기를 그대로 둡니다.

## 자주 묻는 질문

STE 한국어판입니까? 아니요. ASD-STE100에는 한국어판이 없고, 한국어 통제 언어 국가 표준도 없습니다. SimpleKorean은 STE 규칙의 목적을 한국어 문법으로 다시 세운 비공식 기준입니다. 엄격 모드의 문장 끝과 접속어 규칙은 KS A 0001:2023을 바탕으로 합니다.

레포지토리와 바디는 왜 규범과 다릅니까? 국립국어원 용례는 "리포지터리"와 "보디"입니다. 그런데 이 두 형태는 실제 문서에서 거의 쓰이지 않습니다. 벤더 문서 표본에서 "리포지터리"는 1,104회 가운데 0회였습니다. 그래서 독자가 알아보는 관용형을 지정형으로 정했습니다.

회사 표기가 다르면 어떻게 합니까? 레포지토리 맨 위에 `.simple-korean.json`을 두세요. 린터와 글쓰기 점검 훅이 이 파일의 지정형을 따릅니다.

```json
{"terms": {"release": {"write": "릴리즈"}, "column": "컬럼"}, "spacing": "attached"}
```

윤문 스킬과는 무엇이 다릅니까? im-not-ai 같은 윤문 스킬은 이미 쓴 글에서 AI 문체와 번역투를 지웁니다. SimpleKorean은 처음부터 규칙대로 쓰게 합니다. 문서 구조와 답변 형식도 정합니다. 예를 들어 조건을 명령 앞에 두고, 한 문장에는 동작 하나만 씁니다. 린터와 측정 결과도 함께 있습니다.

15/20어절은 어디서 나온 숫자입니까? 한국어 기술 문서의 문장 길이 상한을 정한 실증 연구는 찾지 못했습니다. 그래서 설계로 정한 값입니다. 보정에서 규칙을 지킨 예문과 기준선 출력의 문장 길이를 쟀습니다. 결과는 [`evals/calibration/RECORD.md`](evals/calibration/RECORD.md)에 있습니다.

엄격 모드에는 왜 한국어 승인 사전이 없습니까? 한국어에는 STE 사전처럼 승인어와 비승인어를 함께 정한 공개 목록이 없습니다. 조사 내용은 [`docs/research/korean-controlled-language.md`](docs/research/korean-controlled-language.md)에 있습니다. 한국어는 의무와 허용 같은 뜻을 단어보다 문장 끝에 싣습니다. 그래서 엄격 모드는 단어 대신 문장 끝과 접속어를 닫힌 목록으로 묶습니다.

## 원본과의 관계

SimpleKorean은 [AminBlg/SimpleEnglish](https://github.com/AminBlg/SimpleEnglish) v2.1.1(`a6fcb4f`)에서 갈라져 나온 비공식 파생 프로젝트입니다. 레포지토리 구조, 훅, 린터 인터페이스, 측정 방식은 원본에서 가져왔습니다. 규칙, 단어 목록, 측정 과제는 한국어에 맞게 새로 썼습니다. 원본의 영어 측정 결과는 가져오지 않았습니다.

## 기여

질문과 버그는 이슈로 알려 주세요. PR을 환영합니다. 공개한 수치를 바꾸는 변경은 원본 출력을 함께 올리고 수치 검증을 통과해야 합니다. 수치 검증에는 kiwipiepy가 필요합니다.

```bash
uv venv .venv --python 3.12 && uv pip install --python .venv/bin/python kiwipiepy==0.24.0
.venv/bin/python evals/check_numbers.py
```

올리기 전에 `python3 evals/ko_lint.py --self-test`와 `python3 evals/tests/run.py`를 돌리세요.

## 라이선스

코드와 단어 목록은 MIT입니다. [`data/basic-vocabulary/grades.tsv`](data/basic-vocabulary/grades.tsv)는 국립국어원의 국어 기초 어휘 등급 목록에서 가져왔고, 공공누리 제1유형(출처 표시)을 따릅니다. 제3자 출처는 [`NOTICE`](NOTICE)에 있습니다.

비공식 프로젝트입니다. ASD, 원본 저자, 국립국어원, 한국표준협회와 관계가 없습니다. ASD-STE100은 ASD의 등록 상표입니다.
````

Run: `python3 evals/ko_lint.py --gate=warning README.md | python3 -c "import json,sys; r=json.load(sys.stdin); print('errors', r['errors_total'], 'warnings', r['warnings_total'])"`
Expected: `errors 0 warnings 0`.

- [ ] **Step 2: 벤치마크 블록과 보기 블록을 채운다**

Run:

```bash
OUT=$(dirname "$(ls evals/results/20*/RESULTS.md | tail -1)")
.venv/bin/python evals/report.py "$OUT" --readme > /dev/null
python3 evals/make_examples.py "$OUT" --readme
grep -c "YYYY-MM-DD" README.md; ls examples
```

Expected: `0`(벤치마크 표시가 실제 결과 경로로 바뀌었다), 이어서 `before-after.md`. `OUT`은 RESULTS.md가 있는 결과 디렉터리다. 압력 시험만 있는 디렉터리에는 RESULTS.md가 없다.

- [ ] **Step 3: CHANGELOG를 쓰고 채운다**

`CHANGELOG.md`:

```markdown
# 변경 기록

항목마다 버전, 날짜, 측정한 효과를 적습니다.

## 1.0.0, <측정 날짜>

- 처음 공개합니다. [AminBlg/SimpleEnglish](https://github.com/AminBlg/SimpleEnglish) v2.1.1(`a6fcb4f`)의 구조를 따르고, 규칙, 단어 목록, 측정 과제는 한국어에 맞게 새로 썼습니다.
- 들어 있는 것은 SKILL.md와 레퍼런스 네 개, 출력 스타일, 시스템 프롬프트, 세션 시작 훅, 파일 점검 훅, 답변 점검 훅, 한국어 린터, 표기 단어 목록, 한국어 슬롭 어휘 목록, 벤치마크입니다.
- 측정 결과는 [`evals/results/<측정 날짜>/RESULTS.md`](evals/results/<측정 날짜>/RESULTS.md)에 있습니다.
- 압력 시험 결과는 [`evals/pressure-tests.md`](evals/pressure-tests.md)의 기록 절에 있습니다.

### 보정

보정 기록은 [`evals/calibration/RECORD.md`](evals/calibration/RECORD.md)에 있습니다.

<보정 줄>
```

Run:

```bash
DATE=$(grep -o 'benchmark:start evals/results/[0-9-]*' README.md | cut -d/ -f3)
echo "DATE=$DATE"
python3 - "$DATE" <<'PY'
import sys
from pathlib import Path
date = sys.argv[1]
if not date:
    raise SystemExit("README에서 측정 날짜를 찾지 못했습니다")
lines = Path("evals/calibration/RECORD.md").read_text(encoding="utf-8").split("## CHANGELOG에 옮길 줄", 1)[1].strip()
path = Path("CHANGELOG.md")
path.write_text(path.read_text(encoding="utf-8").replace("<측정 날짜>", date).replace("<보정 줄>", lines), encoding="utf-8")
PY
grep -c -E "<측정 날짜>|<보정 줄>" CHANGELOG.md
```

Expected: `DATE=2026-…`(Task 17의 측정 날짜), 이어서 `0`.

- [ ] **Step 4: 수치 검증과 관문을 돌린다**

Run:

```bash
.venv/bin/python evals/check_numbers.py; echo "exit=$?"
python3 evals/ko_lint.py --gate skills/simple-korean/SKILL.md skills/simple-korean/references/*.md prompts/system-prompt.md output-styles/simple-korean.md README.md > /dev/null; echo "gate=$?"
```

Expected: `check_numbers OK: 공개한 수치와 글이 원본 파일과 같습니다`, `exit=0`, `gate=0`. 계획 검증 때 가짜 결과로 이 흐름을 끝까지 돌렸다. README 표의 숫자 하나, 인용의 글자 하나, CHANGELOG의 보정 줄, 매니페스트 버전, RESULTS.md, RECORD.md, 규칙 블록을 하나씩 바꾸면 수치 검증이 모두 실패했다. 되돌리면 통과했다.

- [ ] **Step 5: CI와 같은 검사를 로컬에서 모두 돌린다**

Run:

```bash
.venv/bin/python evals/ko_lint.py --self-test && .venv/bin/python evals/tests/run.py > /dev/null \
  && node --test src/hooks/simple-korean-activate.test.js > /dev/null && .venv/bin/python src/hooks/test_lint_hook.py > /dev/null \
  && .venv/bin/python evals/check_numbers.py \
  && python3 evals/ko_lint.py --gate skills/simple-korean/SKILL.md skills/simple-korean/references/*.md prompts/system-prompt.md output-styles/simple-korean.md README.md > /dev/null \
  && /usr/bin/python3 evals/ko_lint.py --self-test && /usr/bin/python3 evals/tests/run.py > /dev/null && /usr/bin/python3 src/hooks/test_lint_hook.py > /dev/null; echo "exit=$?"
```

Expected: `self-test OK` 두 줄, `check_numbers OK` 한 줄, `exit=0`.

- [ ] **Step 6: 커밋한다**

```bash
git add README.md CHANGELOG.md examples/before-after.md
git commit -m "docs: add README, changelog, and before-after examples" -m $'Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01SanRSLxxVtkLMJh1wLGeGZ'
```

### Task 20: 공개

스펙 14절이다. 사용자 확인을 받기 전에는 GitHub 레포를 만들지 않는다(Global Constraints). 2026-10-08에 `say8425/SimpleKorean`은 없었다. 이 레포지토리의 기본 브랜치는 `main`이고 원격은 없다.

**Files:**
- 없음(원격 레포, 태그, CI 실행)

**Interfaces:**
- Consumes: Task 15~19의 커밋 전부
- Produces: `https://github.com/say8425/SimpleKorean`(public), `main` 브랜치, 태그 `v1.0.0`, 통과한 CI 실행

- [ ] **Step 1: 사용자에게 결과를 보이고 공개를 확인받는다**

Run:

```bash
sed -n '/benchmark:start/,/benchmark:end/p' README.md
sed -n '/## 범주별 정밀도/,/## 거짓 일치 목록/p' evals/calibration/RECORD.md
sed -n '/^## 기록/,$p' evals/pressure-tests.md
git log --oneline main..feat/v1
```

이 네 출력을 요약해서 보인다. 압력 시험에서 끝까지 X로 남은 기준이 있으면 따로 알린다. 그다음 이렇게 묻는다. "`say8425/SimpleKorean`을 public으로 만들고, `main`과 `v1.0.0` 태그를 올릴까요?" 사용자가 분명히 승인하기 전에는 다음 단계로 가지 않는다. 소유자나 공개 범위를 바꾸라고 하면 그 값으로 Step 2의 명령을 바꾼다.

- [ ] **Step 2: 레포를 만들고 올린다**

Run:

```bash
git switch main && git merge --ff-only feat/v1
gh repo create say8425/SimpleKorean --public --source=. --remote=origin \
  --description "LLM이 기술 문서와 채팅 답변을 쉬운 한국어로 쓰게 하는 에이전트 스킬. SimpleEnglish(ASD-STE100)의 한국어 파생 프로젝트."
git push -u origin main
git tag -a v1.0.0 -m "SimpleKorean 1.0.0" && git push origin v1.0.0
```

Expected: `gh`가 레포 주소를 출력하고, `main`과 `v1.0.0`이 올라간다.

- [ ] **Step 3: CI 결과를 확인한다**

Run:

```bash
RUN=$(gh run list --repo say8425/SimpleKorean --branch main --limit 1 --json databaseId --jq '.[0].databaseId')
gh run watch "$RUN" --repo say8425/SimpleKorean --exit-status; echo "exit=$?"
```

Expected: 작업 `check`와 `python39`가 모두 성공하고 `exit=0`이다. `RUN`이 비어 있으면 실행이 아직 목록에 없는 것이다. 몇 초 뒤 첫 명령을 다시 돌린다. CI가 실패하면 `gh run view "$RUN" --repo say8425/SimpleKorean --log-failed`로 원인을 읽는다. 그리고 `fix/ci` 브랜치에서 고쳐 PR로 올린다. 기본 브랜치에 바로 커밋하지 않는다(사용자 전역 규칙).

- [ ] **Step 4: 공개한 레포에서 플러그인을 확인한다**

Run:

```bash
TMP=$(mktemp -d) && git clone --depth 1 https://github.com/say8425/SimpleKorean.git "$TMP/SimpleKorean"
claude --plugin-dir "$TMP/SimpleKorean" plugin details simple-korean
gh repo view say8425/SimpleKorean --json visibility,url --jq '.visibility + " " + .url'
```

Expected: 플러그인 `simple-korean`의 정보가 나오고, 마지막 줄은 `PUBLIC https://github.com/say8425/SimpleKorean`이다.

- [ ] **Step 5: 결과를 알린다**

사용자에게 레포 주소, 태그, CI 결과를 알린다. Step 1에서 알린 압력 시험 실패가 있으면 다시 적는다.
