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
스킬 없이 쓴 답변(`evals/results/2026-10-08/reply/baseline__oom__r1.txt`):

<!-- source: evals/results/2026-10-08/reply/baseline__oom__r1.txt -->
<!-- simple-korean: off -->
> ## 무슨 일이 일어나는 건가
>
> `OOMKilled`는 컨테이너가 **메모리 limit(`resources.limits.memory`)을 초과**해서 리눅스 커널의 OOM killer가 프로세스를 강제 종료(exit code 137, SIGKILL)했다는 뜻입니다. kubelet이 컨테이너를 재시작하고, 같은 일이 반복되면 `CrashLoopBackOff`로 보입니다.
>
> 원인은 크게 네 가지입니다.
>
> 1. **limit이 너무 낮음**: 앱의 정상적인 메모리 사용량이 limit보다 큽니다.
> 2. **메모리 누수 또는 사용량 급증**: 시간이 지나며 늘어나거나, 큰 요청, 배치, 캐시 때문에 순간적으로 치솟습니다.
> 3. **런타임 설정이 컨테이너 limit과 안 맞음**
>    - JVM: 힙(`-Xmx`)에 메타스페이스, 스레드 스택, 네이티브 메모리가 더해져 limit을 넘습니다.
>    - Node.js: `--max-old-space-size`가 limit보다 큽니다.
>    - Go, Python: GC 특성이나 `GOMEMLIMIT` 미설정이 원인일 수 있습니다.
> 4. **노드 메모리 부족**: 이 경우는 파드가 Evicted되는 경우가 많고, 컨테이너 limit 초과와는 구분됩니다.
>
> ## 확인 방법
>
> ```bash
> # 종료 원인 확인 (Last State: Terminated, Reason: OOMKilled, Exit Code: 137)
> kubectl describe pod <pod> -n <ns>
>
> # 현재 사용량 (metrics-server 필요)
> kubectl top pod <pod> -n <ns> --containers
>
> # 직전 컨테이너의 로그
> kubectl logs <pod> -n <ns> --previous
>
> # 설정된 requests/limits
> kubectl get pod <pod> -n <ns> -o jsonpath='{.spec.containers[*].resources}'
> ```
>
> Prometheus를 쓴다면 `container_memory_working_set_bytes`의 추이를 보세요. 이 값이 limit에 닿으면서 톱니 모양이면 limit 부족이거나 누수입니다. 재시작 직후부터 계속 오르기만 하면 누수일 가능성이 큽니다.
>
> ## 무엇을 바꿔야 하나
>
> **1. limit과 request 조정(가장 빠른 조치)**
>
> ```yaml
> resources:
>   requests:
>     memory: "512Mi"
>   limits:
>     memory: "1Gi"   # 관측된 피크 사용량 + 20~30% 여유
> ```
>
> - 메모리는 압축할 수 없는 자원이라 초과하면 바로 kill됩니다. request와 limit을 같게 두면 QoS가 안정적입니다.
> - limit만 무작정 올리면 누수를 가릴 뿐입니다. 먼저 피크 사용량을 측정하세요.
>
> **2. 런타임을 컨테이너에 맞추기**
>
> - JVM: `-XX:MaxRAMPercentage=70` 정도로 설정합니다. 힙 외 영역을 위해 100%는 피하세요.
> - Node.js: `--max-old-space-size`를 limit의 약 75%로 맞춥니다.
> - Go: `GOMEMLIMIT`을 limit의 약 90%로 설정합니다.
>
> **3. 근본 원인 해결**
>
> - 힙 덤프나 프로파일링으로 누수를 찾습니다(JVM이면 heap dump, Go면 pprof 등).
> - 무제한 캐시, 큰 파일이나 응답을 통째로 메모리에 올리는 코드, 커넥션이나 스레드 누수를 점검합니다.
> - 부하가 원인이면 HPA로 파드를 늘려 파드당 부하를 줄입니다.
>
> ## 다음 단계
>
> 사용하는 언어와 런타임, 현재 `resources` 설정, `kubectl describe pod`의 `Last State` 부분과 `kubectl top` 결과를 알려주시면 구체적인 값을 제안해 드릴 수 있습니다.
<!-- simple-korean: on -->

같은 모델이 SimpleKorean을 켜고 쓴 답변(`evals/results/2026-10-08/reply/plain__oom__r1.txt`):

<!-- source: evals/results/2026-10-08/reply/plain__oom__r1.txt -->
<!-- simple-korean: off -->
> 파드가 OOMKilled로 재시작되면 컨테이너가 메모리 한도(`limits.memory`)를 넘겨 커널이 프로세스를 강제 종료한 것입니다. 해결하려면 한도를 올리거나 애플리케이션의 메모리 사용량을 줄여야 합니다.
>
> 컨테이너는 cgroup(프로세스의 자원 사용을 제한하는 리눅스 기능)으로 메모리 한도를 받습니다. 사용량이 한도를 넘으면 커널의 OOM killer가 프로세스에 SIGKILL을 보냅니다. 이때 종료 코드는 137입니다. kubelet은 종료된 컨테이너를 `restartPolicy`에 따라 다시 시작합니다. 같은 일이 반복되면 대기 시간이 늘어나며 CrashLoopBackOff 상태가 됩니다.
>
> 먼저 원인이 한도 초과인지 확인하세요. 아래 명령에서 `<파드>`는 실제 파드 이름으로 바꾸세요.
>
> ```
> kubectl describe pod <파드>
> kubectl top pod <파드> --containers
> ```
>
> describe 출력의 `Last State: Terminated`에 `Reason: OOMKilled`가 보이면 한도 초과입니다. `kubectl top`은 metrics-server가 설치되어 있어야 동작합니다.
>
> 한도가 너무 낮으면 `limits.memory`를 올리세요. 평소 사용량보다 여유를 두고 정하세요. `requests.memory`는 실제 사용량에 가깝게 설정해야 합니다. 그래야 스케줄러가 노드를 정확히 고릅니다.
>
> ```
> resources:
>   requests:
>     memory: "512Mi"
>   limits:
>     memory: "1Gi"
> ```
>
> 한도를 올려도 사용량이 계속 늘면 메모리 누수를 의심해야 합니다. 시간에 따른 사용량 그래프가 우상향하면 누수입니다. 이 경우 한도를 올려도 재시작 간격만 늘어납니다. 애플리케이션의 힙 프로파일을 보고 코드를 고치세요.
>
> 런타임 설정도 확인해야 합니다. 예를 들어 JVM은 컨테이너 한도보다 큰 힙을 잡으면 종료됩니다. `-XX:MaxRAMPercentage=75` 같은 옵션으로 힙을 한도의 일부로 제한하세요. Node.js는 `--max-old-space-size`로 제한할 수 있습니다. 힙 밖에도 스레드 스택, 네이티브 메모리, 파일 캐시가 한도에 포함됩니다. 메모리 기반 `emptyDir`(`medium: Memory`)에 쓴 데이터도 포함됩니다.
>
> 노드 전체의 메모리가 부족해 쫓겨난 경우는 다릅니다. 그때는 상태가 OOMKilled가 아니라 Evicted로 표시됩니다. 이 경우 노드의 자원 압박과 다른 파드의 requests 설정을 점검해야 합니다.
>
> describe 출력이나 사용량 추이를 알려 주시면 한도를 얼마로 잡을지 구체적으로 계산해 드릴 수 있습니다.
<!-- simple-korean: on -->

문서 예시는 [`examples/before-after.md`](examples/before-after.md)에 있습니다.
<!-- example:end -->

## 벤치마크

아래 수치는 모두 커밋한 원본 출력에서 다시 계산한 값입니다. CI가 푸시마다 `evals/check_numbers.py`로 대조합니다. 모든 실행은 `claude-sonnet-5-5`, effort low이고, 사용자 설정과 MCP 서버를 읽지 않았습니다. 판정 모델도 Claude라서 같은 계열에 유리한 편향이 있을 수 있습니다.

<!-- benchmark:start evals/results/2026-10-08 -->
답변: 전문용어가 하나씩 든 질문 8개를 조건마다 2번씩 물었습니다. 답변은 모두 32개입니다. 스킬을 켜면 독자가 보는 결함(em-dash, 굵은 글씨, 헤더, 불릿)이 99% 줄었습니다(394개에서 3개). 블라인드 판정에서 SimpleKorean 답변은 16쌍 가운데 16쌍에서 이겼고, 0쌍에서 비겼고, 0쌍에서 졌습니다.

| 조건 | 답변 수 | 평균 어절 | 평균 문장 | em-dash | 굵은 글씨 | 헤더 | 불릿 | 인사말과 맺음말 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 스킬 없음 | 16 | 246 | 30.9 | 0 | 141 | 45 | 208 | 12 |
| SimpleKorean | 16 | 187 | 20.6 | 0 | 0 | 0 | 3 | 2 |

문서: sqlpipe 문서 과제 8개를 조건마다 2번씩 썼습니다. 비율은 린터가 센 수를 어절 수로 나눈 값입니다. 린터는 정규식 검사이므로 순위로 읽지 말고 방향으로 읽으세요.

| 조건 | 문서 수 | 100어절당 오류 | 100어절당 경고 | 100어절당 번역투 | 지정 표기 비율 | 쉬운 단어 비율 | 가장 긴 문장 |
|---|---:|---:|---:|---:|---:|---:|---:|
| 스킬 없음 | 16 | 0.00 | 1.09 | 0.14 | 95.0% | 40.2% | 18어절 |
| 기본 모드 | 16 | 0.00 | 0.00 | 0.00 | 100.0% | 44.6% | 15어절 |
| 엄격 모드 | 16 | 0.00 | 0.00 | 0.00 | 100.0% | 41.6% | 20어절 |

원본 출력, 표기 분포, 측정 조건은 [`evals/results/2026-10-08/RESULTS.md`](evals/results/2026-10-08/RESULTS.md)에 있습니다.
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
