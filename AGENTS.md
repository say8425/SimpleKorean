# 에이전트 지침

이 레포지토리에서 한국어 글을 쓰거나 고치면 `simple-korean` 스킬의 규칙을 따르세요. 스킬을 설치했어도 작업 트리(지금 체크아웃한 파일)의 [`skills/simple-korean/SKILL.md`](skills/simple-korean/SKILL.md)를 따르세요. 이 레포지토리의 PR은 규칙 자체를 자주 바꾸기 때문입니다. 글을 쓰기 전에 그 `SKILL.md`를 읽으세요.

규칙을 적용하는 글은 레포지토리의 모든 한국어 마크다운 문서, 커밋 메시지, PR 제목과 본문입니다. `docs/`의 번역 README는 한국어 규칙의 대상이 아닙니다. 번역 README는 같은 원칙(짧은 문장, 능동태, 과장 없는 사실)으로 쓰세요. 영어판은 SimpleEnglish 규칙을 따르세요.

## 목적

이 레포지토리는 LLM이 기술 문서와 채팅 답변을 쉬운 한국어로 쓰게 하는 에이전트 스킬을 만듭니다. 읽는 사람은 분야 밖의 똑똑한 독자입니다. 규칙은 사실과 지시를 담은 글을 위한 것입니다. 마케팅과 브랜드 글은 범위 밖입니다. 규칙, 훅(정해진 때에 자동으로 실행하는 스크립트), 린터(규칙 위반을 세는 스크립트), 단어 목록, 측정은 모두 이 스킬을 위해 있습니다.

성공 기준은 다음 세 가지입니다:

- 스킬을 켜면 끈 때보다 독자가 보는 결함이 측정할 수 있을 만큼 줄어야 합니다. 결함은 서식, 번역투, AI 슬롭(AI 글에 흔한 빈말), 지정형(쓰라고 정한 표기)을 따르지 않은 표기입니다.
- README의 수치를 모두 커밋한 원본 출력에서 다시 계산할 수 있어야 합니다.
- 스킬 문서가 스킬 자신의 규칙을 지켜야 합니다.

## 요청과 리뷰 지적을 받는 기준

사용처는 스킬, 규칙 판본, 린터를 가져다 쓰는 곳입니다. 사용처의 요청과 리뷰 지적을 모두 받아들이면 스킬의 쓰임이 흐려집니다. 그래서 요청과 지적마다 위 목적에 맞는지 먼저 판단하세요. 맞지 않으면 거절하세요. 거절할 때는 이유를 밝히세요. 아래 목록의 요청은 리뷰 지적도 함께 가리킵니다.

다음 요청은 거절하세요:

- 사용처 한 곳에 맞춘 예외: 사용처 한 곳의 사정에 맞춰 규칙을 넓히거나 예외를 더하는 요청입니다. 지정형, 띄어쓰기, 건너뛸 문자열은 사용처가 `.simple-korean.json`으로 바꾸게 하세요. 그 밖의 사정은 사용처가 자기 지침에 적게 하세요.
- 근거 없는 규칙 변경: 측정이나 조사 근거 없이 규칙을 바꾸거나 늘리는 요청입니다. 규칙을 바꾸면 다시 측정해야 합니다. 규칙이 길어지면 규칙 블록(세션 시작 훅이 문맥에 넣는 규칙 요약)도 길어집니다.
- 새 규칙 묶음: 문서 규칙과 답변 규칙을 섞어 `SKILL.md`에 없는 규칙 묶음을 만드는 요청입니다. 답변 규칙의 기준은 규칙 블록의 답변 절입니다. 설계 문서(`docs/superpowers/specs/2026-10-08-simple-korean-design.md`) 5장에 따라 슬롭 어휘와 번역투 목록도 답변에 적용합니다.
- 요약에서 생긴 오독: 사용처가 규칙을 손으로 요약해 옮기다 생긴 오독을 규칙으로 막으려는 요청입니다. 사용처가 요약 대신 `prompts/`의 판본을 그대로 싣게 하세요.
- 참조용 고정: 외부에서 가리키려고 규칙의 절 이름이나 번호를 바꾸지 말라는 요청입니다. 사용처가 릴리스 태그로 버전을 고정하게 하세요.

같은 문제가 다른 사용처나 벤치마크 입력에서도 생기면 한 곳의 사정이 아닙니다. 판본을 그대로 실어도 같은 오독이 생기면 판본의 결함입니다. 이런 문제는 규칙의 결함으로 다루세요.

다음 요청은 받으세요:

- 린터의 오탐과 놓침: 오탐은 규칙에 맞는 글을 위반으로 세는 것입니다. 놓침은 규칙이 막는 글을 세지 못하는 것입니다. 둘 다 지금의 `SKILL.md`를 기준으로 판단하세요. 사용처의 제품 이름 같은 단어에서만 생기는 표기 오탐은 `.simple-korean.json`의 `skip`으로 돌리게 하세요.
- 원문을 그대로 싣는 방법: 사용처가 규칙을 손으로 옮기지 않고 판본을 그대로 싣게 돕는 요청입니다. 이때 규칙의 뜻은 바꾸지 마세요.

## 레포지토리 지도

디렉터리마다 맡은 일은 다음과 같습니다:

- `skills/simple-korean/`: 스킬 원문(`SKILL.md`)과 참고 파일
- `src/hooks/`: 훅 세 개(Claude Code나 Codex가 정해진 때에 실행하는 스크립트)
- `prompts/system-prompt.md`, `output-styles/simple-korean.md`: 규칙 블록(세션 시작 훅이 문맥에 넣는 규칙 요약)을 담은 두 파일
- `prompts/sentence-rules.*.md`, `prompts/format-rules.*.md`: 봇에 넣는 답변 판본. 규칙 블록의 답변 절을 문장 규칙과 서식 규칙으로 나눴습니다. 한국어판과 영어판이 있습니다.
- `src/simple_korean/`, `pyproject.toml`: 답변 판본을 읽는 Python 패키지
- `.claude-plugin/`, `.codex-plugin/`, `.agents/plugins/`: 플러그인 매니페스트와 마켓플레이스 목록
- `evals/`: 린터(규칙 위반을 세는 스크립트), 측정 스크립트, 수치 확인 스크립트, 테스트
- `evals/results/`, `evals/calibration/`: 측정 결과와 린터 보정 기록
- `data/terms.json`: 외래어 단어 목록과 근거
- `tools/`: 슬롭 어휘(AI 글에 흔한 빈말) 목록과 기초 어휘 목록을 만드는 스크립트
- `docs/research/`, `docs/superpowers/`: 조사 보고서, 설계 문서, 구현 계획

린터는 `evals/ko_lint.py`, `ko_rules.py`, `ko_terms.py`, `ko_text.py`입니다.

## 문체

커밋 제목과 PR 제목은 `fix: 설정 파일의 지정형을 20자로 제한한다`처럼 `<유형>: <해라체 문장>`으로 쓰세요. 유형은 feat, fix, perf, refactor, docs, test, chore, ci 가운데 하나입니다. 이 형식은 `references/use-cases.md`의 커밋 제목 형식보다 앞섭니다. 커밋 본문도 해라체로 쓰세요. 기존 문서를 고칠 때는 그 문서의 문체를 따르세요.

## 고치지 않는 글

글을 규칙에 맞게 고칠 때 다음은 바꾸지 마세요:

- 코드, 명령, 식별자
- 원본 출력의 인용
- `<!-- simple-korean: off -->`와 `<!-- simple-korean: on -->` 사이의 글

이 표지는 일부러 틀린 예시와 원본 출력의 인용에만 쓰세요. 린터를 피하려고 쓰지 마세요.

다음 파일과 블록은 스크립트가 만듭니다. 손으로 고치지 말고 그 스크립트를 다시 실행하세요:

- README의 `benchmark` 블록과 `RESULTS.md`: `evals/report.py`
- README의 `example` 블록과 `examples/before-after.md`: `evals/make_examples.py`
- `evals/calibration/RECORD.md`: `evals/calibration/hits.py`
- `evals/slop.tsv`: `tools/slop-lexicon/build_slop.py`

README 블록의 문장 틀은 `evals/readme_i18n.py`에 있습니다. 스크립트마다 사용법은 파일 머리의 설명에 있습니다.

## 번역 README

한국어 `README.md`를 고치면 `docs/`의 번역 README 네 개도 같은 내용과 구조로 고치세요.

## 규칙을 세울 때

이 레포지토리는 [AminBlg/SimpleEnglish](https://github.com/AminBlg/SimpleEnglish) v2.1.1(`a6fcb4f`)에서 갈라졌습니다. 규칙을 새로 세울 때 영어 규칙을 번역하지 마세요. 원본 규칙이 막으려던 오독을 먼저 찾으세요. 그다음 한국어 문법으로 같은 오독을 막는 규칙을 세우세요.

## 함께 고칠 파일

`evals/check_numbers.py`는 공개한 수치, 버전, 규칙 블록 두 벌 같은 여러 파일의 일치를 확인합니다. 확인하는 항목은 그 파일 머리의 설명에 있습니다. 호출 문구(스킬을 부르는 말)와 핵심 문구의 목록은 그 파일의 `SKILL_TRIGGERS`와 `KEY_PHRASES`입니다. 이 문구를 바꾸면 두 상수도 고치세요.

규칙 블록의 답변 절을 바꾸면 `prompts/`의 답변 판본 네 개도 고치세요. 한국어판은 답변 절의 문장을 한 줄에 하나씩 그대로 담습니다. 문장 판본은 설계 문서 5장에 따라 슬롭 어휘와 번역투를 지우라는 규칙 블록의 문장도 담습니다. 영어판은 한국어판의 줄마다 같은 규칙을 영어로 적습니다. `check_numbers.py`는 한국어판이 답변 절을 빠짐없이 담는지 확인합니다. 영어판은 줄 구조와 따옴표 안의 한국어만 확인합니다. 그래서 영어판의 뜻은 직접 맞추세요. 판본 파일의 경로는 바꾸지 마세요. 봇이 태그마다 같은 경로로 판본을 읽습니다.

다음은 어떤 검사도 확인하지 않습니다. 그래서 직접 맞추세요:

- `SKILL.md`의 규칙을 바꾸면 `references/rule-catalog.md`의 규칙 번호와 원본 STE 번호를 고치세요.
- 엄격 모드 규칙을 바꾸면 `references/strict-mode.md`를 고치세요.
- 규칙을 바꾸면 README 다섯 언어판의 규칙 표를 고치세요.
- `data/terms.json`을 바꾸면 단어를 옮겨 적은 곳도 고치세요. `SKILL.md`의 네 무리 단어, 규칙 블록의 지정형(쓰라고 정한 표기) 문장, README 다섯 언어판의 "표기 정책" 표입니다.
- 규칙 블록의 길이를 바꾸면 `src/hooks/README.md`의 "약 2,500자"를 확인하세요.

## 측정과 수치

README와 `RESULTS.md`의 수치는 커밋한 원본 출력에서 다시 만듭니다. 그래서 다음을 지키세요:

- `evals/results/<날짜>/`의 원본 출력을 손으로 고치지 마세요.
- 새로 측정하면 결과를 새 날짜 디렉터리에 저장하세요. 멈춘 측정을 이어 잴 때만 같은 디렉터리를 쓰세요.
- 비용이 드는 스크립트는 실행하기 전에 사용자에게 물으세요. `evals/run_bench.py`, `evals/run_reply_bench.py`, `evals/run_pressure.py`는 `claude` CLI를 부릅니다. `docs/research/data/`의 생성 스크립트와 판정 스크립트도 외부 API를 부릅니다.

## 버전과 릴리스

버전은 release-please(커밋 제목으로 릴리스 PR을 만드는 도구)가 올립니다. `release-please-config.json`의 `extra-files`에 적힌 파일의 버전을 손으로 고치지 마세요.

feat, fix, perf 커밋만 새 릴리스를 만듭니다. 사용자가 받는 것을 바꾸면 docs 대신 feat나 fix를 쓰세요. 규칙, 훅, 린터, 단어 목록, 슬롭 어휘가 사용자가 받는 것입니다.

release-please는 커밋 제목만 `CHANGELOG.md`로 옮깁니다. 그래서 릴리스 PR 브랜치의 `CHANGELOG.md` 항목에 "측정" 절을 손으로 더하세요. 이 절에는 README가 가리키는 결과 경로와 `evals/calibration/RECORD.md`의 "CHANGELOG에 옮길 줄"을 넣으세요. 다시 재지 않았으면 그 이유도 적으세요. `check_numbers.py`가 결과 경로와 보정 줄을 확인합니다.

## 코드 제약

코드를 고칠 때 다음을 지키세요:

- 린터와 `src/hooks/lint_hook.py`는 Python 3.9에서 동작해야 합니다.
- 린터와 `lint_hook.py`에는 표준 라이브러리만 쓰세요. 사용자는 아무것도 설치하지 않고 훅을 실행합니다.
- kiwipiepy(한국어 형태소 분석기)는 측정 코드인 `evals/metrics.py`에만 쓰세요.
- `src/simple_korean/` 패키지도 Python 3.9에서 동작해야 하고 표준 라이브러리만 써야 합니다.
- 세션 시작 훅(`src/hooks/simple-korean-activate.js`)은 의존성 없는 Node 스크립트로 두세요.
- `.simple-korean.json`의 값 검사(지정형 20자, `skip` 100개)를 느슨하게 하지 마세요. `simple-korean-activate.js`와 `evals/ko_terms.py`는 같은 기준을 써야 합니다. 지정형은 세션 시작 훅을 거쳐 모델 문맥에 들어갑니다.
- 세션 시작 훅의 출력은 9,500자 이하여야 합니다. 더 길면 훅은 규칙 블록 대신 짧은 대체 규칙을 보냅니다.

## 확인

PR을 올리기 전에 레포지토리 최상위에서 `.github/workflows/check.yml`의 명령을 실행하세요. `evals/check_numbers.py`에는 kiwipiepy가 필요합니다. 그래서 이 스크립트는 `.venv/bin/python`으로 실행하세요. `.venv`가 없으면 README의 "기여" 절을 보고 만드세요. 한국어 마크다운 문서를 새로 더하면 `check.yml`의 린터 목록에도 더하세요.

고친 문서는 린터로 확인하세요. 절차를 담은 문서에는 `--type procedural`을 붙이세요:

```bash
python3 evals/ko_lint.py --gate=warning <파일>
```

린터가 오류나 경고를 내면 고친 뒤 다시 실행하세요. PR 제목은 다음 명령으로 확인하세요:

```bash
PR_TITLE='<제목>' python3 evals/check_pr_title.py
```

린터는 정해진 문자열 패턴만 찾습니다. 그래서 용어 풀이 누락이나 한 문장에 든 두 동작은 잡지 못합니다. 린터를 통과한 뒤에도 `SKILL.md`의 "내기 전 자가 점검"을 하세요. 새로 쓴 문장마다 길이, 동작이나 명제가 하나인지, 처음 쓴 용어를 풀이했는지 확인하세요.
