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

점검 훅은 검사하는 파일의 디렉터리부터 위로 올라가며 `.simple-korean.json`을 찾습니다. 이 파일로 단어 목록의 지정형을 바꾸고 건너뛸 문자열을 더할 수 있습니다. 파일이 깨져 있거나 값의 형식이 틀리면 기본 설정으로 검사하고 그 사실을 한 줄 알립니다. 지정형을 바꾸면 바꾸기 전의 지정형도 경고합니다.

세션 시작 훅도 작업 디렉터리(`CLAUDE_PROJECT_DIR`)에서 위로 올라가며 이 파일을 찾습니다. 찾으면 바뀐 지정형을 규칙 블록 뒤에 한 줄로 덧붙입니다. 모델은 설정 파일을 스스로 읽지 않기 때문입니다.

설정 값은 레포지토리가 정하고 모델의 문맥에 그대로 들어갑니다. 그래서 두 훅은 같은 기준으로 값을 검사합니다. 지정형에는 한글, 영문, 숫자, 공백만 20자까지 쓸 수 있습니다. 건너뛸 문자열(`skip`)은 한 줄짜리 문자열 100개까지입니다. 형식이 틀린 설정은 통째로 무시하고, 세션 시작 훅은 단어 목록에 있는 개념만 알립니다.

```json
{
  "terms": {"release": "릴리즈", "method": {"write": "메소드", "reason": "TTA 정보통신용어사전을 따름"}},
  "skip": ["디렉토리 유틸리티"],
  "spacing": "attached"
}
```

예시를 일부러 틀리게 써야 하면 그 부분을 `<!-- simple-korean: off -->`와 `<!-- simple-korean: on -->` 사이에 두세요. 그 사이는 검사하지 않습니다.
