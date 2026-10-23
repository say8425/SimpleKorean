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

Codex는 훅을 처음 실행하기 전에 그 훅을 믿을지 묻습니다. 승인하려면 Codex에서 `/hooks`를 여세요. 그다음 SimpleKorean 훅을 승인하세요.

## 훅이 보내는 내용

세션 시작 훅은 `prompts/system-prompt.md`의 규칙 블록을 표준 출력으로 씁니다. 규칙 블록은 두 `---` 줄 사이에 있습니다. 블록의 길이는 약 2,500자입니다. `claude plugin details simple-korean`이 보여 주는 토큰 수에는 이 블록이 들어가지 않습니다. 페이지 제목, 붙여 넣는 곳 안내, 짧은 판본은 보내지 않습니다. Claude Code는 훅 출력을 10,000자까지만 받으므로, 훅은 9,500자를 넘는 출력 대신 짧은 대체 규칙을 보냅니다.

전체 스킬은 `skills/simple-korean/SKILL.md`에 있습니다. 훅은 이 파일의 경로를 담은 안내 문단을 규칙 블록 앞에 넣습니다. 이 문단은 엄격 모드나 점검을 요청받은 모델에게 SKILL.md를 먼저 읽으라고 지시합니다.

Codex도 훅 문맥에 상한을 둡니다. `.codex-plugin/hooks.json`의 `additionalContextLimit: 0`은 파일로 빼는 문턱을 끕니다. 상한 자체를 없애지는 않습니다. 규칙 블록은 그 상한 안에 듭니다.

훅은 프롬프트 파일을 정해진 후보 위치에서 차례로 찾습니다. 모든 위치에서 읽지 못하면 짧은 대체 규칙을 냅니다. 이때도 훅은 종료 코드 0으로 끝나므로 세션은 그대로 시작됩니다.

## 하네스마다 훅을 읽는 곳

Claude Code는 `.claude-plugin/plugin.json`의 `hooks` 항목을 읽습니다.

Codex는 `.codex-plugin/hooks.json`을 읽습니다. `.codex-plugin/plugin.json`의 `hooks` 항목이 이 파일을 가리킵니다. 마켓플레이스 목록은 `.agents/plugins/marketplace.json`입니다.

## 테스트

레포지토리 최상위에서 실행하세요:

```bash
node --test src/hooks/simple-korean-activate.test.js
python3 src/hooks/test_lint_hook.py
```

## 글쓰기 점검 훅 (Claude Code)

Claude Code에서는 알림용 훅 두 개가 더 동작합니다. 두 훅 모두 작업을 막지 않습니다.

`PostToolUse` 훅은 `Write`와 `Edit` 뒤에 동작합니다. 쓴 파일의 이름이 `.md`로 끝나면 `src/hooks/lint_hook.py`가 린터(`src/simple_korean/ko_lint.py`)로 검사합니다. 그다음 위반의 줄 번호와 문구를 오류부터 12개까지 모델에 보여 줍니다.

`Edit` 뒤에는 이번 편집이 더한 위반만 보여 줍니다. 훅은 편집 전의 글도 검사해 두 결과를 견줍니다. 편집 전의 글은 Claude Code가 훅에 넘기는 `originalFile`에서 얻습니다. 그래서 기존 문서에 몇 줄을 더해도 새 줄의 위반이 기존 위반에 묻히지 않습니다. 편집이 다른 줄에 만든 위반(문체 혼용 같은 것)도 알립니다. 편집 전부터 있던 위반은 새 위반을 알릴 때 건수만 덧붙입니다.

훅은 편집 전과 뒤의 위반을 이렇게 짝짓습니다. 편집하지 않은 줄의 위반은 편집 전의 같은 줄에 같은 위반이 있으면 뺍니다. 편집한 줄의 위반은 종류와 문구가 같은 위반이 편집 전에 남아 있으면 그 수만큼 뺍니다. 이때 줄의 글이 같은 위반, 숫자만 다른 위반, 글자가 비슷한 위반 순서로 짝짓습니다. 그래서 옮긴 줄이나 번호만 고친 줄의 위반은 새 위반으로 알리지 않습니다.

이 짝짓기에는 한계가 있습니다. 한 편집이 위반 하나를 지우고 종류와 문구가 같은 위반을 새로 쓰면 그 위반은 알리지 않습니다. 숫자만 다른 줄이 여럿이거나 견줄 위반 쌍이 1만 개를 넘으면 남은 위반을 순서대로 짝짓습니다. 이때는 옛 줄의 번호를 알릴 수 있습니다. 알리는 위반의 수는 그대로 맞습니다.

`originalFile`이 없으면 훅은 `new_string`을 `old_string`으로 되돌려 편집 전의 글을 만듭니다. `new_string`이 비었거나, 파일에 없거나, 두 번 이상 나오면 되돌릴 자리를 하나로 정하지 못합니다. `replace_all` 편집도 같습니다. 이때는 파일 전체의 위반을 보여 줍니다.

`Stop` 훅에서는 같은 스크립트가 마지막 답변을 읽습니다. 답변에 em-dash, 굵은 글씨, 표, 슬롭 어휘, 인사말, 맺음말이 있으면 시스템 메시지를 더합니다. 답변이 헤더나 목록으로 시작해도 알립니다. 그 밖의 헤더와 목록 항목은 알리지 않습니다. 답변은 내용과 길이를 보고 헤더와 목록을 쓸 수 있기 때문입니다.

코드, HTML 주석, URL, 따옴표 인용 안의 em-dash, 슬롭 어휘, 인사말, 맺음말은 세지 않습니다. 인용한 오류 문구는 줄이거나 바꾸지 않기 때문입니다. 굵은 글씨와 표는 따옴표 안에 있어도 셉니다.

Codex에서는 세션 시작 훅만 동작합니다.

## 점검 훅이 건너뛰는 것

글쓰기 규칙은 사람이 읽을 문서에 적용합니다. 에이전트가 자기용으로 쓰는 메모리 파일에는 적용하지 않습니다. 그래서 점검 훅은 다음을 건너뜁니다:

- 한글 비율이 30%보다 낮은 파일(영어 문서)과 답변
- Claude 설정 디렉터리 아래의 모든 경로(`CLAUDE_CONFIG_DIR`, 없으면 `~/.claude`)
- `.claude` 디렉터리가 들어간 모든 경로(예: `my-project/.claude/agent-memory/reviewer/MEMORY.md`)
- `SIMPLE_KOREAN_LINT_EXCLUDE`의 글롭에 맞는 경로
- UTF-8로 읽지 못한 파일(CP949나 UTF-16으로 저장한 파일)

심볼릭 링크로는 건너뛰기를 피할 수 없습니다. 점검은 적힌 그대로의 절대 경로와 링크를 푼 경로를 모두 대조합니다. 둘 중 하나만 맞아도 건너뜁니다.

`SIMPLE_KOREAN_LINT_EXCLUDE`에는 글롭을 플랫폼의 경로 구분자로 나눠 적습니다(Linux와 macOS는 `:`, Windows는 `;`). 패턴의 `*`는 `/`에도 맞습니다. 맨 앞의 `~`는 홈 디렉터리로 바뀝니다.

```bash
export SIMPLE_KOREAN_LINT_EXCLUDE="$HOME/notes/*:*/CHANGELOG.md"
```

파일 점검을 끄려면 이 변수를 `*`로 설정하세요. 답변 점검은 계속 동작합니다.

## 프로젝트 설정

점검 훅은 검사하는 파일의 디렉터리부터 위로 올라가며 `.simple-korean.json`을 찾습니다. 이 파일로 지정형(단어 목록이 쓰라고 정한 표기)을 바꿀 수 있습니다. 건너뛸 문자열도 더할 수 있습니다. 파일이 깨져 있거나 값의 형식이 틀리면 점검 훅은 기본 설정으로 검사합니다. 그리고 그 사실을 한 줄로 알립니다. 지정형을 바꾸면 바꾸기 전의 지정형도 경고합니다.

세션 시작 훅도 작업 디렉터리(`CLAUDE_PROJECT_DIR`)에서 위로 올라가며 이 파일을 찾습니다. 찾으면 바뀐 지정형을 규칙 블록 뒤에 한 줄로 덧붙입니다. 모델은 설정 파일을 스스로 읽지 않기 때문입니다.

설정 값은 레포지토리가 정합니다. 이 값은 모델의 문맥에 그대로 들어갑니다. 그래서 두 훅은 같은 기준으로 값을 검사합니다.

지정형에는 한글, 영문, 숫자, 공백만 20자까지 쓸 수 있습니다. 건너뛸 문자열(`skip`)은 한 줄짜리 문자열 100개까지입니다. 두 훅은 형식이 틀린 설정을 통째로 무시합니다. 세션 시작 훅은 단어 목록에 있는 개념만 알립니다.

```json
{
  "terms": {"release": "릴리즈", "method": {"write": "메소드", "reason": "TTA 정보통신용어사전을 따름"}},
  "skip": ["디렉토리 유틸리티"],
  "spacing": "attached"
}
```

예시를 일부러 틀리게 써야 하면 그 부분을 `<!-- simple-korean: off -->`와 `<!-- simple-korean: on -->` 사이에 두세요. 그 사이는 검사하지 않습니다.
