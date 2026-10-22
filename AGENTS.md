# 에이전트 지침

이 레포지토리에서 한국어 글을 쓰거나 고치면 `simple-korean` 스킬의 규칙을 따르세요. 스킬을 설치했어도 작업 트리(지금 체크아웃한 파일)의 [`skills/simple-korean/SKILL.md`](skills/simple-korean/SKILL.md)를 따르세요. 이 레포지토리의 PR은 규칙 자체를 자주 바꾸기 때문입니다. 글을 쓰기 전에 그 `SKILL.md`를 읽으세요.

규칙을 적용하는 글은 레포지토리의 모든 한국어 마크다운 문서, 커밋 메시지, PR 제목과 본문입니다. `docs/`의 번역 README는 한국어 규칙의 대상이 아닙니다. 번역 README는 같은 원칙(짧은 문장, 능동태, 과장 없는 사실)으로 쓰세요. 영어판은 SimpleEnglish 규칙을 따르세요.

## 레포지토리 지도

디렉터리마다 맡은 일은 다음과 같습니다:

- `skills/simple-korean/`: 스킬 원문(`SKILL.md`)과 참고 파일
- `prompts/system-prompt.md`, `output-styles/simple-korean.md`: `SKILL.md`를 줄인 규칙 블록 두 벌
- `src/hooks/`: 세션 시작 훅과 점검 훅(정해진 때에 에이전트가 자동으로 실행하는 스크립트)
- `evals/`: 린터, 벤치마크, 수치 확인 스크립트, 테스트
- `data/terms.json`: 외래어 단어 목록과 근거
- `docs/research/`, `docs/superpowers/`: 조사 보고서, 설계 문서, 구현 계획

이 레포지토리는 [AminBlg/SimpleEnglish](https://github.com/AminBlg/SimpleEnglish) v2.1.1(`a6fcb4f`)에서 갈라졌습니다. 규칙을 새로 세울 때 영어 규칙을 번역하지 마세요. 원본 규칙이 막으려던 오독을 찾고, 한국어 문법으로 같은 오독을 막으세요.

## 문체

커밋 제목과 PR 제목은 `fix: 설정 파일의 지정형을 20자로 제한한다`처럼 `<유형>: <해라체 문장>`으로 쓰세요. 유형은 feat, fix, perf, refactor, docs, test, chore, ci 가운데 하나입니다. 이 형식은 `references/use-cases.md`의 커밋 제목 형식보다 앞섭니다. 커밋 본문도 해라체로 쓰세요. 기존 문서를 고칠 때는 그 문서의 문체를 따르세요.

## 고치지 않는 글

글을 규칙에 맞게 고칠 때 다음은 바꾸지 마세요:

- 코드, 명령, 식별자
- 원본 출력의 인용
- `<!-- simple-korean: off -->`와 `<!-- simple-korean: on -->` 사이의 글

이 표지는 일부러 틀린 예시와 원본 출력의 인용에만 쓰세요. 린터를 피하려고 쓰지 마세요.

README의 `<!-- benchmark:start -->`와 `<!-- example:start -->` 블록은 생성기(원본 출력에서 README 블록을 만드는 스크립트)가 씁니다. 이 블록을 손으로 고치면 `evals/check_numbers.py`가 실패합니다. 블록을 바꾸려면 `evals/readme_i18n.py`의 문장 틀을 고치세요. 그다음 `evals/report.py <결과 디렉터리> --readme`와 `evals/make_examples.py <결과 디렉터리> --readme`를 실행하세요.

## 번역 README

한국어 `README.md`를 고치면 `docs/`의 번역 README 네 개도 같은 내용과 구조로 고치세요.

## 규칙을 바꿀 때

`SKILL.md`의 규칙을 바꾸면 다음도 함께 확인하세요:

- `skills/simple-korean/references/rule-catalog.md`의 K 번호
- 규칙 블록 두 벌
- README 다섯 언어판의 규칙 표
- `SKILL.md` description의 호출 문구(스킬을 부르는 말)

두 규칙 블록은 글자까지 같아야 합니다. 규칙 블록의 핵심 문구는 `SKILL.md`에도 있어야 합니다. description은 [설계 문서](docs/superpowers/specs/2026-10-08-simple-korean-design.md) 10절의 호출 문구를 모두 담아야 합니다. `evals/check_numbers.py`가 이 세 가지를 확인합니다.

규칙 블록의 길이를 바꾸면 README 다섯 언어판의 "규칙 블록 2,476자" 같은 글자 수도 고치세요. 세션 시작 훅은 출력이 9,500자를 넘으면 규칙 블록 대신 짧은 대체 규칙을 보냅니다. 그래서 규칙 블록은 이 길이 안에 들어야 합니다.

## 측정과 수치

README와 `RESULTS.md`의 수치는 커밋한 원본 출력에서 다시 만듭니다. 그래서 다음을 지키세요:

- `evals/results/<날짜>/`의 원본 출력과 `RESULTS.md`를 손으로 고치지 마세요.
- 새로 측정하면 결과를 새 날짜 디렉터리에 저장하세요.
- 벤치마크 스크립트(`run_bench.py`, `run_reply_bench.py`, `run_pressure.py`)는 사용자에게 묻고 실행하세요. 이 스크립트는 `claude` CLI를 부르므로 비용이 듭니다.

## 버전과 릴리스

버전은 release-please가 올립니다. `SKILL.md`, 플러그인 매니페스트 세 개, `.release-please-manifest.json`의 버전을 손으로 고치지 마세요.

feat, fix, perf 커밋만 새 릴리스를 만듭니다. 사용자가 받는 규칙, 훅, 린터를 바꾸면 docs 대신 feat나 fix를 쓰세요.

release-please는 커밋 제목만 `CHANGELOG.md`로 옮깁니다. 그래서 릴리스 PR의 "측정" 절은 손으로 쓰세요. 다시 재지 않았으면 그 이유를 적으세요.

## 코드 제약

코드를 고칠 때 다음을 지키세요:

- 린터와 점검 훅은 Python 3.9에서 돌아야 합니다.
- 린터와 점검 훅에는 표준 라이브러리만 쓰세요. 사용자는 아무것도 설치하지 않고 훅을 돌립니다. kiwipiepy는 측정 코드에만 쓰세요.
- 세션 시작 훅은 의존성 없는 Node 스크립트로 두세요.
- 두 훅의 `.simple-korean.json` 값 검사(20자, 100개)를 느슨하게 하지 마세요. 이 값은 모델 문맥에 그대로 들어갑니다.

## 확인

PR을 올리기 전에 레포지토리 최상위에서 CI가 돌리는 테스트를 실행하세요:

```bash
python3 evals/ko_lint.py --self-test
python3 evals/tests/run.py
node --test src/hooks/simple-korean-activate.test.js
python3 src/hooks/test_lint_hook.py
.venv/bin/python evals/check_numbers.py
```

`check_numbers.py`에는 kiwipiepy가 필요합니다. `.venv`가 없으면 README의 "기여" 절을 보고 만드세요.

고친 문서는 린터(규칙 위반을 세는 스크립트)로 확인하세요. 절차를 담은 문서에는 `--type procedural`을 붙이세요:

```bash
python3 evals/ko_lint.py --gate=warning <파일>
```

린터가 오류나 경고를 내면 고친 뒤 다시 실행하세요. PR 제목은 다음 명령으로 확인하세요:

```bash
PR_TITLE='<제목>' python3 evals/check_pr_title.py
```

린터는 정해진 문자열 패턴만 찾습니다. 그래서 용어 풀이 누락이나 한 문장에 든 두 동작은 잡지 못합니다. 린터를 통과한 뒤에도 `SKILL.md`의 "내기 전 자가 점검"을 하세요. 새로 쓴 문장마다 길이, 동작이나 명제가 하나인지, 처음 쓴 용어를 풀이했는지 확인하세요.
