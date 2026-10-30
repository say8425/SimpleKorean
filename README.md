<p align="center">
  AI가 쓴 한국어 기술 문서를 정비 매뉴얼처럼 읽히게 합니다.
</p>

<p align="center">
  한국어 | <a href="docs/README.en.md">English</a> | <a href="docs/README.ja.md">日本語</a> | <a href="docs/README.zh.md">中文</a> | <a href="docs/README.es.md">Español</a>
</p>

<p align="center">
  <a href="https://agentskills.io"><img src="https://img.shields.io/badge/SKILL.md-open_standard-blue?style=flat" alt="Agent Skills"></a>
  <a href="https://github.com/say8425/SimpleKorean/releases/latest"><img src="https://img.shields.io/github/v/release/say8425/SimpleKorean?label=version&style=flat" alt="version"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-lightgrey?style=flat" alt="MIT"></a>
</p>

SimpleKorean은 LLM이 기술 문서와 채팅 답변을 쉬운 한국어로 쓰게 하는 에이전트 스킬입니다. 항공 정비 매뉴얼에 쓰는 통제 영어(controlled English, 쓸 단어와 문법을 정해 둔 영어) ASD-STE100의 규칙을 [SimpleEnglish](https://github.com/AminBlg/SimpleEnglish)에서 가져와 한국어 문법에 맞게 다시 세웠습니다. 여기에 외래어 표기 목록을 더했습니다. 이 목록은 실제 한국어 개발 문서에서 쓰는 표기를 세어 만들었습니다.

[Agent Skills 표준](https://agentskills.io)을 읽는 에이전트에서 동작합니다. Claude Code, Cursor, Codex, Gemini CLI, OpenCode가 그 예입니다.

## 설치하지 않고 따르게 할 때

에이전트에게 이 레포지토리 주소만 주고 따르라고 할 수 있습니다. 이 절은 그때 에이전트가 읽을 지시입니다.

사용자가 설치 없이 이 레포지토리의 규칙대로 글을 쓰라고 하면 이 절을 따르세요. 이 README의 규칙 표는 요약입니다. 규칙 원문은 `https://raw.githubusercontent.com/say8425/SimpleKorean/main/skills/simple-korean/SKILL.md`에 있습니다.

셸과 Node.js가 있으면 다음 명령을 사용자에게 알리세요. 그다음 그 명령을 실행하세요. 이 명령은 `SKILL.md` 전체를 출력합니다. 참고 파일을 받은 디렉터리도 알려 줍니다.

```bash
npx skills use say8425/SimpleKorean@simple-korean
```

명령이 실패하거나 셸을 쓸 수 없으면 위의 raw 주소(파일 원문만 주는 주소)에서 `SKILL.md`를 끝까지 읽으세요. 가져오는 도구가 원문 대신 요약을 주면 원문을 그대로 달라고 요청하세요. `curl`이 있으면 `curl`로 받으세요.

`SKILL.md`에서 `references/`로 시작하는 경로는 `SKILL.md`가 있는 디렉터리를 기준으로 읽으세요. 예를 들어 `references/strict-mode.md`는 `https://raw.githubusercontent.com/say8425/SimpleKorean/main/skills/simple-korean/references/strict-mode.md`입니다. 단어 목록 전체는 `https://raw.githubusercontent.com/say8425/SimpleKorean/main/data/terms.json`에 있습니다. GitHub의 `blob` 주소 대신 raw 주소를 쓰세요. `blob` 주소는 원문 대신 HTML 페이지를 줍니다.

설치하지 않으면 훅(정해진 때에 에이전트가 자동으로 실행하는 스크립트)이 동작하지 않습니다. 그래서 훅이 하는 일을 직접 해야 합니다:

- 에이전트가 긴 대화를 요약해 줄이면 `SKILL.md`를 다시 읽으세요.
- 답변이나 문서를 내기 전에 `SKILL.md`의 "내기 전 자가 점검"을 하세요.
- 셸, git, Python 3.9 이상이 있으면 쓴 글을 린터(규칙 위반을 세는 스크립트)로 확인하세요.

`/tmp/SimpleKorean`이 없으면 먼저 레포지토리를 받으세요:

```bash
git clone --depth 1 https://github.com/say8425/SimpleKorean.git /tmp/SimpleKorean
```

문서는 첫째 명령으로, 답변은 둘째 명령으로 확인하세요. 절차를 담은 문서는 첫째 명령에 `--type procedural`을 붙이세요:

```bash
python3 /tmp/SimpleKorean/evals/ko_lint.py 문서.md
python3 /tmp/SimpleKorean/evals/ko_lint.py --type reply - < 답변.txt
```

린터는 위반 수를 JSON으로 출력합니다. 문서는 `errors_total`과 `warnings_total`이 0이어야 합니다. 답변은 `visible_total`이 0이어야 합니다.

## 설치

### Claude Code

Claude Code에는 플러그인으로 설치하세요.

```bash
claude plugin marketplace add say8425/SimpleKorean
claude plugin install simple-korean@simple-korean
```

플러그인에는 아래 다섯 가지가 들어 있습니다. 스킬 하나와 훅 세 개는 설치한 뒤 새 세션부터 자동으로 동작합니다. 출력 스타일은 직접 적용할 때만 동작합니다. 세션 시작 훅과 출력 스타일이 넣는 규칙 블록은 스킬의 규칙을 줄인 판본입니다.

| 구성 요소 | 하는 일 | 적용 | 필요한 것 |
|---|---|---|---|
| 스킬 | 전체 규칙, 엄격 모드, 점검 모드를 담습니다. 모델이 필요할 때 읽습니다. | 자동 | 없음 |
| 세션 시작 훅 | 세션마다 규칙 블록을 넣습니다. 스킬 이름을 말하지 않아도 모델이 규칙을 따릅니다. | 자동 | Node.js |
| 파일 점검 훅 | 모델이 쓰거나 고친 마크다운 파일을 확인합니다. 위반은 모델에 알립니다. | 자동 | Python 3.9 이상 |
| 답변 점검 훅 | 모델의 마지막 답변을 확인합니다. 위반은 화면에 알립니다. | 자동 | Python 3.9 이상 |
| 출력 스타일 | 세션 시작 훅과 같은 규칙 블록을 시스템 프롬프트에 넣습니다. | 선택 | 없음 |

출력 스타일 없이도 규칙은 적용됩니다. 세션 시작 훅이 같은 규칙 블록을 이미 넣기 때문입니다. Node.js가 없어 세션 시작 훅이 동작하지 않으면 출력 스타일을 적용하세요. 출력 스타일을 적용하려면 `/config`의 Output style에서 고르세요. 또는 `~/.claude/settings.json`에 `{"outputStyle": "simple-korean:simple-korean"}`을 넣으세요.

세션 시작 훅은 세션마다 규칙 블록 2,476자를 넣습니다. 자세한 내용은 [`src/hooks/README.md`](src/hooks/README.md)에 있습니다.

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

설치하지 않고 한 번만 쓰려면 `npx skills use say8425/SimpleKorean@simple-korean`을 실행하세요. 이 명령은 스킬을 담은 프롬프트를 출력합니다. `--agent claude-code`를 붙이면 그 프롬프트로 Claude Code를 실행합니다.

### 스킬을 지원하지 않는 도구

스킬을 지원하지 않는 도구에는 [`prompts/system-prompt.md`](prompts/system-prompt.md)의 규칙 블록을 붙여 넣으세요. 규칙 블록은 시스템 프롬프트, `AGENTS.md`, `.cursorrules`에 넣을 수 있습니다. `prompts/system-prompt.md` 끝에는 약 120토큰짜리 짧은 판본도 있습니다.

### 봇과 프로그램

봇의 시스템 프롬프트에는 답변 판본을 넣으세요. 답변 판본은 규칙 블록의 답변 규칙을 둘로 나눈 파일입니다. [`prompts/sentence-rules.ko.md`](prompts/sentence-rules.ko.md)는 문장 규칙을 담습니다. 슬롭 어휘(AI 글에 흔한 빈말)와 번역투를 지우라는 문장도 여기에 있습니다. [`prompts/format-rules.ko.md`](prompts/format-rules.ko.md)는 헤더, 굵은 글씨, 표 같은 서식 규칙을 담습니다. 두 파일을 이어 붙이면 답변 규칙 전체가 됩니다.

답변 판본은 슬롭 어휘와 번역투 문장 말고는 문서 규칙을 담지 않습니다. 이름이 `.en.md`로 끝나는 파일은 같은 규칙을 영어로 적은 판본입니다. 파일의 첫 줄은 판본, 언어, 버전을 적은 HTML 주석입니다.

판본을 고정하려면 릴리스 태그의 raw 주소에서 받으세요. 예를 들어 `https://raw.githubusercontent.com/say8425/SimpleKorean/<태그>/prompts/sentence-rules.ko.md`입니다. 판본 파일의 경로는 태그마다 같습니다.

Python에서는 PyPI의 `simple-korean` 패키지를 설치하세요. 패키지는 표준 라이브러리만 씁니다. `<버전>` 자리에 릴리스 버전을 쓰세요:

```bash
pip install "simple-korean==<버전>"
```

PyPI에 접근할 수 없으면 GitHub의 릴리스 태그에서 설치하세요:

```bash
pip install "git+https://github.com/say8425/SimpleKorean@<태그>"
```

```python
from simple_korean import __version__, prompt_block

prompt = prompt_block(variant="sentences", lang="en")
```

`variant`는 `sentences`나 `format`입니다. `lang`은 규칙을 적은 언어이고 `ko`나 `en`입니다. `lang`은 답변의 언어를 정하지 않습니다.

패키지에는 린터도 들어 있습니다. `lint_detail(text, "reply")`는 답변에서 em-dash, 슬롭 어휘, 인사말, 맺음말, 굵은 글씨, 표, 첫 줄의 헤더나 목록을 찾습니다. `formatting=False`를 주면 굵은 글씨, 표, 첫 줄은 찾지 않습니다. 번역투와 문체 혼용은 찾지 않습니다.

문서 규칙으로 확인하려면 `"reply"` 대신 `"descriptive"`나 `"procedural"`을 쓰세요. 위반마다 `category`, `severity`, `line`, `text`를 돌려줍니다.

### 설치한 뒤

설치한 뒤에는 기술 문서를 요청하세요. 이미 있는 글을 고치려면 "simple-korean으로 고쳐 줘"라고 말하세요.

## 보기

같은 모델이 같은 초안을 다듬은 문서 두 개입니다. 초안은 CLI 도구의 문제 해결 절입니다. 이 초안에는 em-dash, 굵은 글씨, 가운뎃점을 일부러 넣었습니다. 표의 첫째 칸은 초안입니다. 둘째 칸은 스킬 없이, 셋째 칸은 SimpleKorean의 기본 모드를 켜고 다듬은 문서입니다. 세 글 모두 고치지 않고 옮겼습니다.

<!-- example:start -->
<table>
<tr>
<th width="34%">초안</th>
<th width="33%">스킬 없이 다듬은 문서</th>
<th width="33%">SimpleKorean을 켜고 다듬은 문서</th>
</tr>
<tr>
<td valign="top">

<!-- draft: evals/results/2026-10-21/inputs/scenarios.json#polish -->
<!-- simple-korean: off -->
> ## 문제 해결
>
> **Postgres 연결 타임아웃** — sqlpipe가 `connection timed out` 오류를 내면 대부분 방화벽·보안 그룹이 5432 포트를 막고 있는 것입니다. `nc -zv <호스트> 5432`로 연결되는지 확인해 보시기 바랍니다.
>
> **S3 권한 오류** — `AccessDenied`가 나면 IAM 정책·버킷 정책에 읽기·쓰기 권한(`s3:GetObject`, `s3:PutObject`)이 있는지 확인하세요. 먼저 `aws sts get-caller-identity`로 지금 쓰는 자격 증명을 확인하는 것이 좋습니다.
<!-- simple-korean: on -->

</td>
<td valign="top">

<!-- source: evals/results/2026-10-21/docs/baseline__polish__r1.json -->
<!-- simple-korean: off -->
> ## 문제 해결
>
> **Postgres 연결 타임아웃** — sqlpipe에서 `connection timed out` 오류가 나면 대개 방화벽이나 보안 그룹이 5432 포트를 막고 있는 경우입니다. `nc -zv <호스트> 5432`로 연결 가능 여부를 먼저 확인하세요.
>
> **S3 권한 오류** — `AccessDenied`가 나면 IAM 정책과 버킷 정책에 읽기·쓰기 권한(`s3:GetObject`, `s3:PutObject`)이 있는지 확인하세요. 그 전에 `aws sts get-caller-identity`로 현재 사용 중인 자격 증명이 맞는지 먼저 확인하는 것이 좋습니다.
<!-- simple-korean: on -->

</td>
<td valign="top">

<!-- source: evals/results/2026-10-21/docs/plain__polish__r1.json -->
<!-- simple-korean: off -->
> ## 문제 해결
>
> ### Postgres 연결 타임아웃
>
> sqlpipe가 `connection timed out` 오류를 내면 대부분 방화벽이나 보안 그룹이 5432 포트를 막습니다. sqlpipe를 실행하는 호스트에서 `nc -zv <호스트> 5432`로 연결되는지 확인하세요.
>
> ### S3 권한 오류
>
> sqlpipe가 `AccessDenied` 오류를 내면 먼저 `aws sts get-caller-identity`로 현재 쓰는 자격 증명을 확인하세요. 그다음 IAM 정책과 버킷 정책에 읽기와 쓰기 권한(`s3:GetObject`, `s3:PutObject`)이 있는지 확인하세요.
<!-- simple-korean: on -->

</td>
</tr>
</table>

다듬은 문서의 원본 파일은 가운데가 `evals/results/2026-10-21/docs/baseline__polish__r1.json`, 오른쪽이 `evals/results/2026-10-21/docs/plain__polish__r1.json`입니다.

초안은 [`evals/results/2026-10-21/inputs/scenarios.json`](evals/results/2026-10-21/inputs/scenarios.json)의 `polish` 과제에 있습니다.

답변 예시와 나머지 문서 예시는 [`examples/before-after.md`](examples/before-after.md)에 있습니다. 예시마다 바뀐 곳은 [이 커밋의 diff](https://github.com/say8425/SimpleKorean/commit/ca720c2beaed9572581ed132e99237ad2e3d794a)에서 볼 수 있습니다.
<!-- example:end -->

## 벤치마크

아래 수치는 모두 커밋한 원본 출력에서 다시 계산한 값입니다. CI가 푸시마다 `evals/check_numbers.py`로 대조합니다. 문서와 답변은 `claude-sonnet-5-5`(effort low)가 썼습니다. 판정은 `claude-opus-5-5`가 했습니다.

모든 실행은 사용자 설정, MCP 서버, AGENTS.md 같은 지침 파일을 읽지 않았습니다. 판정 모델도 Claude라서 같은 계열에 유리한 편향이 있을 수 있습니다.

어절은 띄어쓰기로 나눈 단위입니다. 지정형은 단어 목록이 쓰라고 정한 표기입니다.

<!-- benchmark:start evals/results/2026-10-21 -->
### 답변

전문용어가 하나씩 든 질문 8개를 조건마다 2번씩 물었습니다. 질문마다 em-dash와 가운뎃점(·)을 하나씩 넣었습니다. 가운뎃점은 답변 규칙이 막지 않으므로 결함에 넣지 않고 따로 셌습니다. 답변은 모두 32개입니다. 스킬을 켜면 화면에 드러나는 결함(em-dash, 굵은 글씨, 표, 첫 줄의 헤더나 목록)이 100% 줄었습니다(162개에서 0개). 블라인드 판정에서 SimpleKorean 답변은 16쌍 가운데 12쌍에서 이겼고, 3쌍에서 비겼고, 1쌍에서 졌습니다. 질문에 em-dash가 있어도 스킬 없는 답변은 em-dash를 쓰지 않았습니다. 그래서 em-dash를 지우는지는 아래 문서의 다듬기 과제로 봅니다.

| 조건 | 답변 수 | 평균 어절 | 평균 문장 | em-dash | 굵은 글씨 | 표 | 첫 줄 헤더·목록 | 가운뎃점 | 헤더 | 불릿 | 인사말과 맺음말 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 스킬 없음 | 16 | 266 | 31.2 | 0 | 155 | 3 | 4 | 26 | 36 | 211 | 13 |
| SimpleKorean | 16 | 223 | 31.0 | 0 | 0 | 0 | 0 | 2 | 54 | 173 | 5 |

### 문서

sqlpipe 문서 과제 8개를 조건마다 2번씩 썼습니다. 비율은 린터가 센 수를 어절 수로 나눈 값입니다. 린터는 정규식으로 세므로 순위로 읽지 말고 방향으로 읽으세요.

| 조건 | 문서 수 | 100어절당 오류 | 100어절당 경고 | 100어절당 번역투 | 지정형 비율 | 쉬운 단어 비율 | 가장 긴 문장 |
|---|---:|---:|---:|---:|---:|---:|---:|
| 스킬 없음 | 16 | 0.14 | 0.71 | 0.42 | 100.0% | 41.9% | 18어절 |
| 기본 모드 | 16 | 0.00 | 0.17 | 0.17 | 100.0% | 45.3% | 15어절 |
| 엄격 모드 | 16 | 0.00 | 0.00 | 0.00 | 100.0% | 39.6% | 13어절 |

em-dash, 굵은 글씨, 가운뎃점을 일부러 넣은 초안을 다듬는 과제는 위 표에 넣지 않고 따로 셉니다. 초안에는 em-dash 2개, 굵은 글씨 2개, 가운뎃점 3개가 있습니다. 아래 표는 조건마다 다듬은 문서에 든 수를 더한 값입니다. 조건마다 2번 다듬었으므로, 초안의 표시가 모두 남으면 em-dash 4개, 굵은 글씨 4개, 가운뎃점 6개입니다. 가운뎃점은 문서 규칙도 막지 않으므로 참고로 셉니다. 초안은 [`evals/results/2026-10-21/inputs/scenarios.json`](evals/results/2026-10-21/inputs/scenarios.json)의 `polish` 과제에 있습니다.

| 조건 | 문서 수 | em-dash | 굵은 글씨 | 가운뎃점 |
|---|---:|---:|---:|---:|
| 스킬 없음 | 2 | 4 | 4 | 1 |
| 기본 모드 | 2 | 0 | 0 | 0 |
| 엄격 모드 | 2 | 0 | 0 | 0 |

원본 출력, 표기 분포, 측정 조건은 [`evals/results/2026-10-21/RESULTS.md`](evals/results/2026-10-21/RESULTS.md)에 있습니다.
<!-- benchmark:end -->

## 규칙

규칙은 [`SKILL.md`](skills/simple-korean/SKILL.md)에 있습니다. 점검 모드와 엄격 모드에서 쓰는 규칙 전체는 [`rule-catalog.md`](skills/simple-korean/references/rule-catalog.md)에 있습니다. 기본 모드 규칙에는 K1.1 같은 K 번호가 붙어 있습니다. 엄격 모드 규칙에는 S1 같은 S 번호가 붙어 있습니다.

### 답변 규칙

채팅 답변에는 모든 모드에서 이 규칙을 씁니다.

| 규칙 | 막는 것 |
|---|---|
| 헤더와 목록은 답의 내용과 길이를 보고 씁니다. 굵은 글씨와 표는 쓰지 않습니다 | 한 줄짜리 답을 둘러싼 서식 |
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

기본 모드는 위의 규칙 전부입니다. 기본 모드는 따로 켜지 않아도 적용됩니다.

### 엄격 모드

엄격 모드는 "엄격 모드", "통제 언어", "KS A 0001", "STE", "ASD-STE100"이라고 말하면 켜집니다. 엄격 모드는 문서의 문장 끝을 다섯 가지로 닫습니다. 의무는 "-해야 합니다", 금지는 "-하면 안 됩니다", 허용은 "-해도 됩니다", 능력은 "-ㄹ 수 있습니다", 사실은 현재형입니다.

엄격 모드에서는 접속어 "(이)나"를 쓰지 않습니다. 조건은 "-면"으로만 씁니다. 근거는 KS A 0001:2023 부속서 H와 I입니다. 답변은 엄격 모드에서도 기본 모드 규칙을 따릅니다.

### 점검 모드

점검 모드는 글 대신 점검을 요청하면 켜집니다. 위반마다 K 번호, 해당 문구, 고친 문장을 알려 줍니다.

## 표기 정책

외래어는 외래어 표기법과 국립국어원 용례를 따릅니다(디렉터리, 메시지, 애플리케이션). 원칙만으로 답이 나오지 않는 단어는 [`data/terms.json`](data/terms.json)의 목록을 따릅니다. 이 목록은 현지화 문서, 벤더 문서, 기업 기술 블로그, GitHub README에서 실제 표기를 세어 만들었습니다. 근거는 [`docs/research/loanword-spelling-usage.md`](docs/research/loanword-spelling-usage.md)에 있습니다.

| 무리 | 쓰는 형태 |
|---|---|
| 규범대로 쓰이는 단어 23개 | 규범형(메시지, 애플리케이션, 메서드, 라이선스) |
| 출처마다 갈리는 단어 4개 | 규범형(디렉터리, 릴리스, 셸, 리디렉션(redirection)) |
| 관용이 굳은 단어 4개 | 레포지토리, 바디, 칼럼, 대상 |
| 공식 표기가 없는 단어 2개 | 리디렉션(redirect), 리팩터링(refactoring) |
| 외래어와 우리말 가운데 고르는 단어 5개 | 오류, 매개변수, 사용자, 기본값, 배포 |
| 띄어쓰기 4개 | 기본값, 매개변수, 반환값, 오픈소스(붙여 씀) |

제품 이름, 화면 문구 인용, API 객체 이름, 코드는 원래 표기를 그대로 둡니다.

## 자주 묻는 질문

### STE 한국어판입니까?

아니요. ASD-STE100에는 한국어판이 없습니다. 한국어 통제 언어(controlled language)의 국가 표준도 없습니다. SimpleKorean은 STE 규칙의 목적을 한국어 문법으로 다시 세운 비공식 기준입니다. 엄격 모드의 문장 끝과 접속어 규칙은 KS A 0001:2023을 바탕으로 합니다.

### 레포지토리와 바디는 왜 규범과 다릅니까?

국립국어원 용례는 "리포지터리"와 "보디"입니다. 그런데 이 두 형태는 실제 문서에서 거의 쓰이지 않습니다. 벤더 문서 표본에서 "리포지터리"는 1,104회 가운데 0회였습니다. 그래서 읽는 사람이 바로 알아보는 관용형을 지정형으로 정했습니다.

### 회사 표기가 다르면 어떻게 합니까?

레포지토리 최상위에 `.simple-korean.json`을 두세요. 세션 시작 훅이 이 파일을 찾아 바뀐 지정형을 모델에게 알립니다. 린터와 파일 점검 훅도 이 파일을 따릅니다. 바꾸기 전의 지정형을 쓰면 두 도구가 경고합니다.

지정형에는 한글, 영문, 숫자, 공백만 20자까지 쓰세요. 건너뛸 문자열(`skip`)은 100개까지입니다. 세션 시작 훅과 파일 점검 훅은 형식이 틀린 설정 대신 기본 설정을 씁니다. 린터는 그런 설정을 받으면 오류를 내고 멈춥니다. 단어 목록에 없는 개념은 훅과 린터 모두 적용하지 않습니다.

```json
{"terms": {"release": {"write": "릴리즈"}, "column": "컬럼"}, "spacing": "attached"}
```

### 윤문 스킬과는 무엇이 다릅니까?

im-not-ai 같은 윤문 스킬은 이미 쓴 글에서 AI 문체와 번역투를 지웁니다. SimpleKorean은 처음부터 규칙대로 쓰게 합니다. 문서 구조와 답변 형식도 정합니다. 예를 들어 조건은 명령 앞에 둡니다. 한 문장에는 동작을 하나만 씁니다. 린터와 측정 결과도 함께 있습니다.

### 15/20어절은 어디서 나온 숫자입니까?

한국어 기술 문서의 문장 길이 상한을 정한 실증 연구는 찾지 못했습니다. 그래서 설계로 정한 값입니다. 보정(calibration, 린터 기준을 실제 출력으로 확인하는 작업)에서 규칙을 지킨 예문과 스킬 없이 만든 출력의 문장 길이를 쟀습니다. 결과는 [`evals/calibration/RECORD.md`](evals/calibration/RECORD.md)에 있습니다.

### 엄격 모드에는 왜 한국어 승인 사전이 없습니까?

한국어에는 STE 사전처럼 승인어와 비승인어를 함께 정한 공개 목록이 없습니다. 조사 내용은 [`docs/research/korean-controlled-language.md`](docs/research/korean-controlled-language.md)에 있습니다. 한국어는 의무와 허용 같은 뜻을 단어보다 문장 끝에 싣습니다. 그래서 엄격 모드는 단어 대신 문장 끝과 접속어를 닫힌 목록으로 묶습니다.

## 원본과의 관계

SimpleKorean은 [AminBlg/SimpleEnglish](https://github.com/AminBlg/SimpleEnglish) v2.1.1(`a6fcb4f`)에서 갈라져 나온 비공식 파생 프로젝트입니다. 레포지토리 구조, 훅, 린터 인터페이스, 측정 방식은 원본에서 가져왔습니다. 규칙, 단어 목록, 측정 과제는 한국어에 맞게 새로 썼습니다. 원본의 영어 측정 결과는 가져오지 않았습니다.

답변 규칙도 원본과 다릅니다. 원본은 답변에서 헤더와 불릿을 모두 막습니다. SimpleKorean은 헤더와 목록을 쓸지 답의 내용과 길이를 보고 정하게 합니다. 이렇게 정한 근거는 [답변 서식 연구](docs/research/reply-formatting.md)에 있습니다.

답변 규칙이 다르므로 벤치마크가 세는 답변 결함도 다릅니다. 원본은 em-dash, 굵은 글씨, 헤더, 불릿을 셉니다. SimpleKorean은 em-dash, 굵은 글씨, 표, 첫 줄의 헤더나 목록을 셉니다.

## 기여

질문과 버그는 이슈로 알려 주세요. PR을 환영합니다. 공개한 수치를 바꾸면 원본 출력을 함께 올리세요. 그 변경은 수치 확인을 통과해야 합니다. 수치 확인에는 kiwipiepy가 필요합니다.

레포지토리 최상위에서 다음을 실행하세요:

```bash
uv venv .venv --python 3.12
uv pip install --python .venv/bin/python kiwipiepy==0.24.0 kiwipiepy-model==0.24.0
.venv/bin/python evals/check_numbers.py
```

올리기 전에 `python3 evals/ko_lint.py --self-test`와 `python3 evals/tests/run.py`를 실행하세요.

PR 제목은 `fix: 설정 파일의 지정형을 20자로 제한한다`처럼 `<유형>: <해라체 문장>`으로 쓰세요. 유형은 feat, fix, perf, refactor, docs, test, chore, ci 가운데 하나입니다. 병합하면 PR 제목이 그대로 변경 기록의 한 줄이 됩니다. feat, fix, perf만 새 릴리스를 만듭니다.

## 라이선스

코드와 단어 목록은 MIT입니다. [`data/basic-vocabulary/grades.tsv`](data/basic-vocabulary/grades.tsv)는 국립국어원의 국어 기초 어휘 등급 목록에서 가져왔습니다. 이 파일은 공공누리 제1유형(출처 표시)을 따릅니다. 제3자 출처는 [`NOTICE`](NOTICE)에 있습니다.

비공식 프로젝트입니다. ASD, 원본 저자, 국립국어원, 한국표준협회와 관계가 없습니다. ASD-STE100은 ASD의 등록 상표입니다.
