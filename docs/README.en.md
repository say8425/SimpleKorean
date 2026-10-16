<p align="center">
  <strong>Makes Korean technical documents written by AI read like a maintenance manual.</strong>
</p>

<p align="center">
  <a href="../README.md">한국어</a> | English | <a href="README.ja.md">日本語</a> | <a href="README.zh.md">中文</a> | <a href="README.es.md">Español</a>
</p>

<p align="center">
  <a href="https://agentskills.io"><img src="https://img.shields.io/badge/SKILL.md-open_standard-blue?style=flat" alt="Agent Skills"></a>
  <a href="https://github.com/say8425/SimpleKorean/releases/latest"><img src="https://img.shields.io/github/v/release/say8425/SimpleKorean?label=version&style=flat" alt="version"></a>
  <a href="../LICENSE"><img src="https://img.shields.io/badge/license-MIT-lightgrey?style=flat" alt="MIT"></a>
</p>

SimpleKorean is an agent skill that makes LLMs write plain Korean in technical documents and chat replies. Aircraft maintenance manuals use a controlled English called ASD-STE100. We took its rules from [SimpleEnglish](https://github.com/AminBlg/SimpleEnglish) and rebuilt them for Korean grammar. We also added a list of loanword spellings. We measured this list on real Korean developer documents.

The skill runs in agents that read the [Agent Skills standard](https://agentskills.io). Examples are Claude Code, Cursor, Codex, Gemini CLI, and OpenCode.

## Install

### Claude Code

For Claude Code, install the plugin. The plugin contains the session-start hook, the writing-check hook, and the output style. The session-start hook needs Node.js. The writing-check hook needs Python 3.9 or later.

```bash
claude plugin marketplace add say8425/SimpleKorean && claude plugin install simple-korean@simple-korean
```

The output style name is `simple-korean:simple-korean`. The short name does not work. Select it under Output style in `/config`, or put `{"outputStyle": "simple-korean:simple-korean"}` in `~/.claude/settings.json`.

The session-start hook adds a rule block of 2,271 characters to each session. The token count that `claude plugin details simple-korean` shows does not include this block.

### Codex

For Codex, install the plugin. The session-start hook installs with it. This hook needs Node.js.

```bash
codex plugin marketplace add say8425/SimpleKorean
codex plugin add simple-korean@simple-korean
```

Before Codex runs a hook for the first time, it asks if you trust the hook. For details, see [`src/hooks/README.md`](../src/hooks/README.md).

### Other agents

For other agents, install with the [skills CLI](https://github.com/vercel-labs/skills).

```bash
pnpm dlx skills add say8425/SimpleKorean
```

If you use npm, run `npx skills add say8425/SimpleKorean`. This command installs only the skill. It does not install the hooks and the output style above.

### Tools without skill support

For tools that do not support skills, paste the rule block from [`prompts/system-prompt.md`](../prompts/system-prompt.md). You can put it in a system prompt, `AGENTS.md`, or `.cursorrules`. The end of this file also has a short version of about 120 tokens.

### After installing

After you install, ask for a technical document. To fix existing text, say "simple-korean으로 고쳐 줘" (fix this with simple-korean).

## Example

Below are raw outputs from the same model for the same question. We copied both replies without changes. The replies are in Korean, because this skill makes the model write Korean.

<!-- example:start -->
Reply written without the skill (`evals/results/2026-10-08/reply/baseline__oom__r1.txt`):

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

Reply from the same model with SimpleKorean on (`evals/results/2026-10-08/reply/plain__oom__r1.txt`):

<!-- source: evals/results/2026-10-08/reply/plain__oom__r1.txt -->
<!-- simple-korean: off -->
> OOMKilled는 컨테이너가 메모리 한도(limit)를 넘어서 리눅스 커널이 프로세스를 강제로 종료했다는 뜻입니다. 쿠버네티스는 종료된 컨테이너를 `restartPolicy`에 따라 다시 시작하기 때문에, 메모리 사용량이 계속 한도를 넘으면 재시작이 반복되고 `CrashLoopBackOff`로 이어집니다.
>
> 원인은 크게 세 가지입니다. 첫째, `resources.limits.memory`가 애플리케이션의 실제 사용량보다 낮게 잡혔습니다. 둘째, 애플리케이션에 메모리 누수가 있어 시간이 지날수록 사용량이 늘어납니다. 셋째, JVM이나 Node.js 같은 런타임의 힙(heap, 런타임이 객체를 쌓는 메모리 영역) 크기가 컨테이너 한도보다 크게 설정되었습니다. 힙 외에 스레드 스택과 네이티브 메모리도 한도 안에 들어가므로, 힙을 한도와 같게 잡으면 초과합니다.
>
> 먼저 종료 사유와 현재 설정을 확인하세요. `<pod>`와 `<ns>`는 실제 값으로 바꾸세요.
>
> ```
> kubectl describe pod <pod> -n <ns>
> kubectl top pod <pod> -n <ns> --containers
> ```
>
> `describe` 출력의 `Last State: Terminated`에서 `Reason: OOMKilled`와 `Exit Code: 137`을 확인하세요. `kubectl top`은 metrics-server가 설치된 클러스터에서만 동작합니다. 재시작 직전 로그는 `kubectl logs <pod> -n <ns> --previous`로 볼 수 있습니다.
>
> 사용량이 한도에 못 미치는 수준에서 꾸준히 늘면 누수를 의심해야 합니다. 이 경우 한도를 올려도 재시작 주기만 길어집니다. 사용량이 시작 직후 한도 근처에서 안정되면 한도가 부족한 것입니다.
>
> 한도 부족이면 Deployment의 `resources`를 수정하세요.
>
> ```yaml
> resources:
>   requests:
>     memory: "512Mi"
>   limits:
>     memory: "1Gi"
> ```
>
> 값은 관찰한 최대 사용량보다 20~30% 높게 시작하는 것이 일반적입니다. `requests`는 스케줄링에 쓰이는 값이고, `limits`는 OOM 종료 기준이 되는 값입니다. 둘을 같게 두면 노드 메모리가 부족할 때 파드가 먼저 쫓겨나는 일을 줄일 수 있습니다.
>
> 런타임 힙이 원인이면 힙을 한도의 70~75% 수준으로 제한하세요. 예를 들어 JVM은 `-XX:MaxRAMPercentage=75.0`, Node.js는 `--max-old-space-size`로 지정합니다.
>
> 누수가 원인이면 한도 조정만으로는 해결되지 않습니다. 힙 덤프나 프로파일러로 누수 지점을 찾아 코드를 고쳐야 합니다.
>
> 어떤 언어와 런타임을 쓰는지, `kubectl describe`의 `Last State` 출력을 알려 주시면 원인을 더 좁힐 수 있습니다.
<!-- simple-korean: on -->

Document examples are in [`examples/before-after.md`](../examples/before-after.md).
<!-- example:end -->

## Benchmark

We calculated all numbers below again from the committed raw outputs. On each push, CI compares them with `evals/check_numbers.py`. `claude-sonnet-5-5` (effort low) wrote the documents and the replies, and `claude-opus-5-5` judged them. No run read user settings, MCP servers, or instruction files such as AGENTS.md. The judge model is also Claude, so it can favor replies from the same model family. An eojeol is a Korean word unit separated by spaces.

<!-- benchmark:start evals/results/2026-10-08 -->
### Replies

We asked 8 questions 2 times in each condition. Each question contains one technical term. There are 32 replies in total. With the skill on, reader-visible defects (em-dashes, bold text, headers, bullets) fell by 100% (from 394 to 0). In a blind judgment of 16 pairs, the SimpleKorean reply won 15, tied 1, and lost 0.

| Condition | Replies | Mean eojeol | Mean sentences | em-dash | Bold | Headers | Bullets | Greetings and sign-offs |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| No skill | 16 | 246 | 30.9 | 0 | 141 | 45 | 208 | 12 |
| SimpleKorean | 16 | 179 | 18.6 | 0 | 0 | 0 | 0 | 1 |

### Documents

The model wrote each of 8 sqlpipe documentation tasks 2 times in each condition. Each rate is the linter's count divided by the eojeol count. The linter is a regex check, so read the numbers as a direction, not as a ranking.

| Condition | Documents | Errors per 100 eojeol | Warnings per 100 eojeol | Translationese per 100 eojeol | Designated spelling rate | Easy word rate | Longest sentence |
|---|---:|---:|---:|---:|---:|---:|---:|
| No skill | 16 | 0.00 | 1.09 | 0.14 | 95.0% | 40.2% | 18 eojeol |
| Default mode | 16 | 0.00 | 0.00 | 0.00 | 100.0% | 44.8% | 16 eojeol |
| Strict mode | 16 | 0.00 | 0.00 | 0.00 | 100.0% | 45.5% | 17 eojeol |

The raw outputs, the spelling distribution, and the test conditions are in [`evals/results/2026-10-08/RESULTS.md`](../evals/results/2026-10-08/RESULTS.md).
<!-- benchmark:end -->

## Rules

The rules are in [`SKILL.md`](../skills/simple-korean/SKILL.md). Review mode and strict mode use the full list of K-numbered rules in [`rule-catalog.md`](../skills/simple-korean/references/rule-catalog.md).

### Reply rules

Chat replies use these rules in all modes.

| Rule | What it stops |
|---|---|
| Answer in prose. Do not use headers, bullets, bold text, or tables | Formatting around a one-line answer |
| Put the answer in the first sentence | An opening that repeats the question |
| Do not use em-dashes | Thoughts that are only half joined |
| Explain a concept term briefly when you first use it | Terms that the reader must look up |
| Use one writing style in one reply. Do not use greetings and sign-offs | "좋은 질문입니다" (Good question), "도움이 되셨기를 바랍니다" (I hope this helped) |

### Document rules

Documents use these rules. Documents include READMEs, runbooks, error messages, release notes, and incident reports.

| Rule | What it stops |
|---|---|
| Write procedures in 15 eojeol or fewer, and descriptions in 20 eojeol or fewer | Long sentences that do not end |
| Put conditions before the command with "-면" (if) | "단, ~경우" (however, in case of ~) after the command, which the reader sees too late |
| Use the active voice and simple tenses | "되어지다" (double passive), "~에 의해" (by ~), "-고 있습니다" (is doing) |
| Do not use guessing or advice endings | "-ㄹ 수도 있습니다" (may), "-것 같습니다" (seems), "-하는 것이 좋습니다" (it is better to) |
| Give one word only one meaning | Switching between "확인", "검증", "점검", and "체크" (all mean "check") |
| Do not drop particles, and do not end with a noun form | Telegram style such as "백업 확인 필요" (backup check needed) |
| Write facts, not importance | "강력한" (powerful), "원활한" (seamless), "단순히 X가 아니라 Y" (not just X but Y) |
| Use the designated spelling of loanwords | "디렉토리" and "디렉터리" (directory) mixed in one document |

## Modes

### Default mode

The default mode is all the rules above. You do not need to turn it on.

### Strict mode

Strict mode turns on when you say "엄격 모드" (strict mode), "통제 언어" (controlled language), "KS A 0001", or "STE". Strict mode limits the sentence endings in documents to five forms. Obligation is "-해야 합니다" (must). Prohibition is "-하면 안 됩니다" (must not). Permission is "-해도 됩니다" (may). Ability is "-ㄹ 수 있습니다" (can). Facts use the present tense. Strict mode does not use the connective "(이)나" (or), and it writes conditions only with "-면" (if). The source is Annexes H and I of KS A 0001:2023. In strict mode, replies still follow the default mode rules.

### Review mode

Review mode turns on when you ask for a review instead of new text. For each violation, it gives the K number, the text, and a corrected sentence.

## Spelling policy

Loanwords follow the Korean loanword orthography and the usage examples of the National Institute of Korean Language (디렉터리, 메시지, 애플리케이션). When these principles do not give an answer, the list in [`data/terms.json`](../data/terms.json) decides. We made this list from real spellings that we counted in localized documents, vendor documents, company tech blogs, and GitHub READMEs. The evidence is in [`docs/research/loanword-spelling-usage.md`](../docs/research/loanword-spelling-usage.md).

| Group | Form to use |
|---|---|
| 23 words used as the standard says | Standard form (메시지 message, 애플리케이션 application, 메서드 method, 라이선스 license) |
| 4 words that differ by source | Standard form (디렉터리 directory, 릴리스 release, 셸 shell, 리디렉션 redirection) |
| 4 words with a fixed common form | 레포지토리 (repository), 바디 (body), 칼럼 (column), 대상 (target) |
| 2 words with no official spelling | 리디렉션 (redirection), 리팩터링 (refactoring) |
| 5 words with a choice between a loanword and a native word | 오류 (error), 매개변수 (parameter), 사용자 (user), 기본값 (default value), 배포 (deployment) |
| 4 spacing cases | 기본값, 매개변수, 반환값, 오픈소스 (written without spaces) |

Product names, quoted screen text, API object names, and code keep their original spelling.

## FAQ

### Is this a Korean edition of STE?

No. ASD-STE100 has no Korean edition, and Korea has no national standard for a controlled language. SimpleKorean is an unofficial standard. It rebuilds the purpose of the STE rules for Korean grammar. The sentence-ending and connective rules of strict mode are based on KS A 0001:2023.

### Why do 레포지토리 and 바디 differ from the standard?

The usage examples of the National Institute of Korean Language are "리포지터리" (repository) and "보디" (body). But real documents almost never use these two forms. In a sample of vendor documents, "리포지터리" appeared 0 times in 1,104 cases. So we chose the common forms that readers recognize as the designated spelling.

### What if my company uses different spellings?

Put `.simple-korean.json` at the top of your repository. The session-start hook finds this file and tells the model the changed designated spellings. The linter and the writing-check hook also follow this file. They warn when you use the designated spelling from before the change. A designated spelling can use only Hangul, Latin letters, digits, and spaces, up to 20 characters. You can list up to 100 strings to skip (`skip`). The skill ignores settings with a wrong format and concepts that are not in the word list.

```json
{"terms": {"release": {"write": "릴리즈"}, "column": "컬럼"}, "spacing": "attached"}
```

In this example, "릴리즈" means release and "컬럼" means column.

### How is this different from a text-polishing skill?

Polishing skills such as im-not-ai remove AI style and translationese from text that already exists. SimpleKorean makes the model follow the rules from the start. It also sets the document structure and the reply format. For example, it puts conditions before the command, and it puts only one action in a sentence. It also comes with a linter and measurement results.

### Where do the 15 and 20 eojeol limits come from?

We did not find an empirical study that sets a sentence length limit for Korean technical documents. So these values are a design choice. During calibration, we measured sentence lengths in example sentences that follow the rules and in baseline outputs. The results are in [`evals/calibration/RECORD.md`](../evals/calibration/RECORD.md).

### Why does strict mode have no Korean approved dictionary?

Korean has no public list that sets both approved and unapproved words, like the STE dictionary. Our research is in [`docs/research/korean-controlled-language.md`](../docs/research/korean-controlled-language.md). Korean puts meanings such as obligation and permission in the sentence ending more than in words. So strict mode puts sentence endings and connectives in closed lists, instead of words.

## Relation to the original

SimpleKorean is an unofficial derived project. It forked from [AminBlg/SimpleEnglish](https://github.com/AminBlg/SimpleEnglish) v2.1.1 (`a6fcb4f`). We took the repository structure, the hooks, the linter interface, and the measurement method from the original. We wrote the rules, the word list, and the measurement tasks again for Korean. We did not take the English measurement results of the original.

## Contributing

Report questions and bugs in an issue. PRs are welcome. A change to published numbers must include the raw outputs and pass the number check. The number check needs kiwipiepy.

Run these commands from the repository root:

```bash
uv venv .venv --python 3.12 && uv pip install --python .venv/bin/python kiwipiepy==0.24.0 kiwipiepy-model==0.24.0
.venv/bin/python evals/check_numbers.py
```

Before you submit, run `python3 evals/ko_lint.py --self-test` and `python3 evals/tests/run.py`.

Write the PR title as `<type>: <Korean sentence>`, for example `fix: 설정 파일의 지정형을 20자로 제한한다`. The sentence ends in the plain declarative form (`-ㄴ다`). The type is one of feat, fix, perf, refactor, docs, test, chore, and ci. When we merge a PR, its title becomes one line of the changelog. Only feat, fix, and perf make a new release. If you cannot write the title in Korean, write it in English. The maintainer will change it before the merge, and the title check fails until then.

## License

The code and the word lists use the MIT license. [`data/basic-vocabulary/grades.tsv`](../data/basic-vocabulary/grades.tsv) comes from the basic Korean vocabulary grade list of the National Institute of Korean Language. It follows KOGL Type 1 (attribution). Third-party sources are in [`NOTICE`](../NOTICE).

This is an unofficial project. It has no relation to ASD, the original author, the National Institute of Korean Language, or the Korean Standards Association. ASD-STE100 is a registered trademark of ASD.

This translation was not reviewed by a native speaker. Please report errors in an [issue](https://github.com/say8425/SimpleKorean/issues).
