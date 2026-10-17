<p align="center">
  <strong>AI가 쓴 한국어 기술 문서를 정비 매뉴얼처럼 읽히게 합니다.</strong>
</p>

<p align="center">
  한국어 | <a href="docs/README.en.md">English</a> | <a href="docs/README.ja.md">日本語</a> | <a href="docs/README.zh.md">中文</a> | <a href="docs/README.es.md">Español</a>
</p>

<p align="center">
  <a href="https://agentskills.io"><img src="https://img.shields.io/badge/SKILL.md-open_standard-blue?style=flat" alt="Agent Skills"></a>
  <a href="https://github.com/say8425/SimpleKorean/releases/latest"><img src="https://img.shields.io/github/v/release/say8425/SimpleKorean?label=version&style=flat" alt="version"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-lightgrey?style=flat" alt="MIT"></a>
</p>

SimpleKorean은 LLM이 기술 문서와 채팅 답변을 쉬운 한국어로 쓰게 하는 에이전트 스킬입니다. 항공 정비 매뉴얼에 쓰는 통제 영어(쓸 단어와 문법을 정해 둔 영어) ASD-STE100의 규칙을 [SimpleEnglish](https://github.com/AminBlg/SimpleEnglish)에서 가져와 한국어 문법에 맞게 다시 세웠습니다. 여기에 실제 한국어 개발 문서에서 잰 외래어 표기 목록을 더했습니다.

[Agent Skills 표준](https://agentskills.io)을 읽는 에이전트에서 동작합니다. Claude Code, Cursor, Codex, Gemini CLI, OpenCode가 그 예입니다.

## 설치

### Claude Code

Claude Code에는 플러그인으로 설치하세요. 플러그인에는 세션 시작 훅, 글쓰기 점검 훅, 출력 스타일이 들어 있습니다. 세션 시작 훅에는 Node.js가 필요합니다. 글쓰기 점검 훅에는 Python 3.9 이상이 필요합니다.

```bash
claude plugin marketplace add say8425/SimpleKorean && claude plugin install simple-korean@simple-korean
```

출력 스타일 이름은 `simple-korean:simple-korean`입니다. Claude Code는 짧은 이름으로는 이 스타일을 찾지 못합니다. `/config`의 Output style에서 고르거나, `~/.claude/settings.json`에 `{"outputStyle": "simple-korean:simple-korean"}`을 넣으세요.

세션 시작 훅은 세션마다 규칙 블록 2,583자를 넣습니다. `claude plugin details simple-korean`이 보여 주는 토큰 수에는 이 블록이 들어가지 않습니다.

### Codex

Codex에는 플러그인으로 설치하세요. 세션 시작 훅이 함께 설치됩니다. 이 훅에는 Node.js가 필요합니다.

```bash
codex plugin marketplace add say8425/SimpleKorean
codex plugin add simple-korean@simple-korean
```

Codex는 훅을 처음 실행하기 전에 그 훅을 믿을지 묻습니다. 자세한 내용은 [`src/hooks/README.md`](src/hooks/README.md)에 있습니다.

### 그 밖의 에이전트

그 밖의 에이전트에는 [skills CLI](https://github.com/vercel-labs/skills)로 설치하세요.

```bash
pnpm dlx skills add say8425/SimpleKorean
```

npm을 쓰면 `npx skills add say8425/SimpleKorean`을 실행하세요. 이 명령은 스킬만 설치합니다. 위의 훅과 출력 스타일은 설치하지 않습니다.

### 스킬을 지원하지 않는 도구

스킬을 지원하지 않는 도구에는 [`prompts/system-prompt.md`](prompts/system-prompt.md)의 규칙 블록을 붙여 넣으세요. 시스템 프롬프트, `AGENTS.md`, `.cursorrules`에 넣으면 됩니다. 이 파일 끝에는 약 120토큰짜리 짧은 판본도 있습니다.

### 설치한 뒤

설치한 뒤에는 기술 문서를 요청하세요. 이미 있는 글을 고치려면 "simple-korean으로 고쳐 줘"라고 말하세요.

## 보기

같은 모델이 같은 과제(CLI 도구의 문제 해결 절)로 쓴 문서 두 개입니다. 왼쪽은 스킬 없이, 오른쪽은 SimpleKorean의 기본 모드를 켜고 썼습니다. 두 문서 모두 고치지 않고 옮겼습니다.

<!-- example:start -->
<table>
<tr>
<th width="50%">스킬 없이 쓴 문서</th>
<th width="50%">SimpleKorean을 켜고 쓴 문서</th>
</tr>
<tr>
<td valign="top">

<!-- source: evals/results/2026-10-17/docs/baseline__troubleshooting__r1.json -->
<!-- simple-korean: off -->
> ## 문제 해결
>
> ### Postgres 연결 타임아웃
>
> `connection timed out` 오류가 나면 먼저 호스트와 포트(기본 5432)에 네트워크로 접근할 수 있는지 확인하세요. VPN, 방화벽, 보안 그룹의 인바운드 규칙이 흔한 원인입니다. 접근에 문제가 없다면 연결 대기 시간을 늘려 보세요.
>
> ```
> sqlpipe run --timeout 30s ...
> ```
>
> 접속 문자열의 호스트, 포트, `sslmode` 값도 다시 확인하세요. 서버가 SSL을 요구하는데 `sslmode=disable`로 되어 있으면 연결이 멈춘 것처럼 보일 수 있습니다.
>
> ### S3 권한 오류
>
> `AccessDenied` 또는 `403`이 나오면 자격 증명이 올바른지 먼저 확인하세요. `aws sts get-caller-identity`로 현재 사용 중인 계정을 볼 수 있습니다. 그다음 IAM 정책에 대상 버킷의 `s3:GetObject`, `s3:PutObject`, `s3:ListBucket` 권한이 있는지 확인하세요. 버킷 정책과 리전 설정도 함께 점검해야 합니다.
<!-- simple-korean: on -->

</td>
<td valign="top">

<!-- source: evals/results/2026-10-17/docs/plain__troubleshooting__r1.json -->
<!-- simple-korean: off -->
> ## 문제 해결
>
> ### Postgres 연결 타임아웃
>
> sqlpipe는 Postgres 포트(기본값 5432)에 연결하지 못하면 `dial tcp: i/o timeout` 오류를 내고 멈춥니다.
>
> 1. sqlpipe를 실행하는 호스트가 Postgres 포트에 연결할 수 있는지 확인하세요.
> 2. 방화벽과 보안 그룹 규칙을 확인하세요. 보통 이 규칙이 연결을 막습니다.
> 3. 데이터베이스가 관리형(RDS, Cloud SQL)이면, 인스턴스가 sqlpipe의 IP에서 오는 연결을 허용하는지 확인하세요.
>
> ### S3 권한 오류
>
> S3 요청이 `AccessDenied` 오류로 실패하면 sqlpipe가 사용하는 자격 증명에 권한이 없다는 뜻입니다.
>
> 1. sqlpipe를 실행하는 호스트에서 `aws sts get-caller-identity`를 실행하세요. 이 명령은 현재 자격 증명의 계정과 역할을 보여 줍니다.
> 2. 그 역할의 IAM 정책이 대상 버킷에 `s3:GetObject`와 `s3:PutObject`를 허용하는지 확인하세요.
> 3. 버킷 정책이 해당 역할을 거부하는지 확인하세요.
<!-- simple-korean: on -->

</td>
</tr>
</table>

원본 파일은 왼쪽이 `evals/results/2026-10-17/docs/baseline__troubleshooting__r1.json`, 오른쪽이 `evals/results/2026-10-17/docs/plain__troubleshooting__r1.json`입니다.

답변 예시와 나머지 문서 예시는 [`examples/before-after.md`](examples/before-after.md)에 있습니다.
<!-- example:end -->

## 벤치마크

아래 수치는 모두 커밋한 원본 출력에서 다시 계산한 값입니다. CI가 푸시마다 `evals/check_numbers.py`로 대조합니다. 문서와 답변은 `claude-sonnet-5-5`(effort low)가 썼습니다. 판정은 `claude-opus-5-5`가 했습니다.

모든 실행은 사용자 설정, MCP 서버, AGENTS.md 같은 지침 파일을 읽지 않았습니다. 판정 모델도 Claude라서 같은 계열에 유리한 편향이 있을 수 있습니다.

어절은 띄어쓰기로 나눈 단위입니다. 지정형은 단어 목록이 쓰라고 정한 표기입니다.

<!-- benchmark:start evals/results/2026-10-17 -->
### 답변

전문용어가 하나씩 든 질문 8개를 조건마다 2번씩 물었습니다. 답변은 모두 32개입니다. 스킬을 켜면 화면에 드러나는 결함(em-dash, 굵은 글씨, 표, 첫 줄의 헤더나 목록)이 100% 줄었습니다(130개에서 0개). 블라인드 판정에서 SimpleKorean 답변은 16쌍 가운데 16쌍에서 이겼고, 0쌍에서 비겼고, 0쌍에서 졌습니다.

| 조건 | 답변 수 | 평균 어절 | 평균 문장 | em-dash | 굵은 글씨 | 표 | 첫 줄 헤더·목록 | 헤더 | 불릿 | 인사말과 맺음말 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 스킬 없음 | 16 | 238 | 29.6 | 0 | 122 | 2 | 6 | 41 | 186 | 11 |
| SimpleKorean | 16 | 167 | 20.8 | 0 | 0 | 0 | 0 | 12 | 73 | 0 |

### 문서

sqlpipe 문서 과제 8개를 조건마다 2번씩 썼습니다. 비율은 린터가 센 수를 어절 수로 나눈 값입니다. 린터는 정규식 검사이므로 순위로 읽지 말고 방향으로 읽으세요.

| 조건 | 문서 수 | 100어절당 오류 | 100어절당 경고 | 100어절당 번역투 | 지정형 비율 | 쉬운 단어 비율 | 가장 긴 문장 |
|---|---:|---:|---:|---:|---:|---:|---:|
| 스킬 없음 | 16 | 0.00 | 0.96 | 0.28 | 95.1% | 42.2% | 21어절 |
| 기본 모드 | 16 | 0.00 | 0.00 | 0.00 | 100.0% | 43.3% | 12어절 |
| 엄격 모드 | 16 | 0.00 | 0.00 | 0.00 | 100.0% | 42.2% | 15어절 |

원본 출력, 표기 분포, 측정 조건은 [`evals/results/2026-10-17/RESULTS.md`](evals/results/2026-10-17/RESULTS.md)에 있습니다.
<!-- benchmark:end -->

## 규칙

규칙은 [`SKILL.md`](skills/simple-korean/SKILL.md)에 있습니다. 점검 모드와 엄격 모드에서 쓰는 K 번호 규칙 전체는 [`rule-catalog.md`](skills/simple-korean/references/rule-catalog.md)에 있습니다.

### 답변 규칙

채팅 답변에는 모든 모드에서 이 규칙을 씁니다.

| 규칙 | 막는 것 |
|---|---|
| 헤더와 목록은 구조를 나타낼 때만 씁니다. 굵은 글씨와 표는 쓰지 않습니다 | 한 줄짜리 답을 둘러싼 서식 |
| 첫 문장에 답을 씁니다 | 질문을 되풀이하는 머리말 |
| em-dash를 쓰지 않습니다 | 반쯤 이어 붙인 생각 |
| 개념 용어는 처음 쓸 때 짧게 풀이합니다 | 따로 찾아봐야 하는 용어 |
| 인사말과 맺음말 없이 한 문체로 씁니다 | "좋은 질문입니다", "도움이 되셨기를 바랍니다" |

### 문서 규칙

문서에는 이 규칙을 씁니다. README, 런북, 오류 메시지, 릴리스 노트, 장애 보고서가 여기에 들어갑니다. 절차문은 할 일을 시키는 문장입니다. 설명문은 사실을 알리는 문장입니다.

| 규칙 | 막는 것 |
|---|---|
| 절차문은 15어절, 설명문은 20어절 이하로 씁니다 | 끝없이 이어지는 만연체 |
| 조건은 "-면"으로 명령 앞에 둡니다 | 명령 뒤에 붙어 늦게 읽히는 "단, ~경우" |
| 능동태와 단순 시제로 씁니다 | "되어지다", "~에 의해", "-고 있습니다" |
| 짐작과 권고 어미를 쓰지 않습니다 | "-ㄹ 수도 있습니다", "-것 같습니다", "-하는 것이 좋습니다" |
| 한 단어에는 한 뜻만 줍니다 | "확인", "검증", "점검", "체크"를 번갈아 쓰기 |
| 조사와 문장 끝 어미를 빼지 않습니다 | "백업 확인 필요" 같은 전보문 |
| 중요성 말고 사실을 씁니다 | "강력한", "원활한", "단순히 X가 아니라 Y" |
| 정해진 외래어 표기를 씁니다 | 한 문서 안에 섞인 "디렉토리"와 "디렉터리" |

## 모드

### 기본 모드

기본 모드는 위의 규칙 전부입니다. 따로 켜지 않아도 됩니다.

### 엄격 모드

엄격 모드는 "엄격 모드", "통제 언어", "KS A 0001", "STE"라고 말하면 켜집니다. 엄격 모드는 문서의 문장 끝을 다섯 가지로 닫습니다. 의무는 "-해야 합니다", 금지는 "-하면 안 됩니다", 허용은 "-해도 됩니다", 능력은 "-ㄹ 수 있습니다", 사실은 현재형입니다.

엄격 모드에서는 접속어 "(이)나"를 쓰지 않습니다. 조건은 "-면"으로만 씁니다. 근거는 KS A 0001:2023 부속서 H와 I입니다. 답변은 엄격 모드에서도 기본 모드 규칙을 따릅니다.

### 점검 모드

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

### STE 한국어판입니까?

아니요. ASD-STE100에는 한국어판이 없습니다. 한국어 통제 언어의 국가 표준도 없습니다. SimpleKorean은 STE 규칙의 목적을 한국어 문법으로 다시 세운 비공식 기준입니다. 엄격 모드의 문장 끝과 접속어 규칙은 KS A 0001:2023을 바탕으로 합니다.

### 레포지토리와 바디는 왜 규범과 다릅니까?

국립국어원 용례는 "리포지터리"와 "보디"입니다. 그런데 이 두 형태는 실제 문서에서 거의 쓰이지 않습니다. 벤더 문서 표본에서 "리포지터리"는 1,104회 가운데 0회였습니다. 그래서 읽는 사람이 바로 알아보는 관용형을 지정형으로 정했습니다.

### 회사 표기가 다르면 어떻게 합니까?

레포지토리 최상위에 `.simple-korean.json`을 두세요. 세션 시작 훅이 이 파일을 찾아 바뀐 지정형을 모델에게 알립니다. 린터와 글쓰기 점검 훅도 이 파일을 따릅니다. 바꾸기 전의 지정형을 쓰면 두 도구가 경고합니다.

지정형에는 한글, 영문, 숫자, 공백만 20자까지 쓰세요. 건너뛸 문자열(`skip`)은 100개까지입니다. 두 훅은 형식이 틀린 설정 대신 기본 설정을 씁니다. 린터는 그런 설정을 받으면 오류를 내고 멈춥니다. 단어 목록에 없는 개념은 훅과 린터 모두 적용하지 않습니다.

```json
{"terms": {"release": {"write": "릴리즈"}, "column": "컬럼"}, "spacing": "attached"}
```

### 윤문 스킬과는 무엇이 다릅니까?

im-not-ai 같은 윤문 스킬은 이미 쓴 글에서 AI 문체와 번역투를 지웁니다. SimpleKorean은 처음부터 규칙대로 쓰게 합니다. 문서 구조와 답변 형식도 정합니다. 예를 들어 조건은 명령 앞에 둡니다. 한 문장에는 동작을 하나만 씁니다. 린터와 측정 결과도 함께 있습니다.

### 15/20어절은 어디서 나온 숫자입니까?

한국어 기술 문서의 문장 길이 상한을 정한 실증 연구는 찾지 못했습니다. 그래서 설계로 정한 값입니다. 보정(린터 기준을 실제 출력으로 확인하는 작업)에서 규칙을 지킨 예문과 스킬 없이 만든 출력의 문장 길이를 쟀습니다. 결과는 [`evals/calibration/RECORD.md`](evals/calibration/RECORD.md)에 있습니다.

### 엄격 모드에는 왜 한국어 승인 사전이 없습니까?

한국어에는 STE 사전처럼 승인어와 비승인어를 함께 정한 공개 목록이 없습니다. 조사 내용은 [`docs/research/korean-controlled-language.md`](docs/research/korean-controlled-language.md)에 있습니다. 한국어는 의무와 허용 같은 뜻을 단어보다 문장 끝에 싣습니다. 그래서 엄격 모드는 단어 대신 문장 끝과 접속어를 닫힌 목록으로 묶습니다.

## 원본과의 관계

SimpleKorean은 [AminBlg/SimpleEnglish](https://github.com/AminBlg/SimpleEnglish) v2.1.1(`a6fcb4f`)에서 갈라져 나온 비공식 파생 프로젝트입니다. 레포지토리 구조, 훅, 린터 인터페이스, 측정 방식은 원본에서 가져왔습니다. 규칙, 단어 목록, 측정 과제는 한국어에 맞게 새로 썼습니다. 원본의 영어 측정 결과는 가져오지 않았습니다.

답변 규칙도 원본과 다릅니다. 원본은 답변에서 헤더와 불릿을 모두 막습니다. SimpleKorean은 구조를 나타내는 헤더와 목록을 허용합니다. 그래서 벤치마크가 세는 답변 결함도 다릅니다. 원본은 em-dash, 굵은 글씨, 헤더, 불릿을 셉니다. SimpleKorean은 em-dash, 굵은 글씨, 표, 첫 줄의 헤더나 목록을 셉니다.

## 기여

질문과 버그는 이슈로 알려 주세요. PR을 환영합니다. 공개한 수치를 바꾸면 원본 출력을 함께 올리세요. 그 변경은 수치 확인을 통과해야 합니다. 수치 확인에는 kiwipiepy가 필요합니다.

레포지토리 최상위에서 다음을 실행하세요:

```bash
uv venv .venv --python 3.12 && uv pip install --python .venv/bin/python kiwipiepy==0.24.0 kiwipiepy-model==0.24.0
.venv/bin/python evals/check_numbers.py
```

올리기 전에 `python3 evals/ko_lint.py --self-test`와 `python3 evals/tests/run.py`를 실행하세요.

PR 제목은 `fix: 설정 파일의 지정형을 20자로 제한한다`처럼 `<유형>: <해라체 문장>`으로 쓰세요. 유형은 feat, fix, perf, refactor, docs, test, chore, ci 가운데 하나입니다. 병합하면 PR 제목이 그대로 변경 기록의 한 줄이 됩니다. feat, fix, perf만 새 릴리스를 만듭니다.

## 라이선스

코드와 단어 목록은 MIT입니다. [`data/basic-vocabulary/grades.tsv`](data/basic-vocabulary/grades.tsv)는 국립국어원의 국어 기초 어휘 등급 목록에서 가져왔습니다. 이 파일은 공공누리 제1유형(출처 표시)을 따릅니다. 제3자 출처는 [`NOTICE`](NOTICE)에 있습니다.

비공식 프로젝트입니다. ASD, 원본 저자, 국립국어원, 한국표준협회와 관계가 없습니다. ASD-STE100은 ASD의 등록 상표입니다.
