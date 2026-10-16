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

For Claude Code, install the plugin. The plugin contains the session-start hook, the writing-check hook, and the output style.

```bash
claude plugin marketplace add say8425/SimpleKorean && claude plugin install simple-korean@simple-korean
```

The output style name is `simple-korean:simple-korean`. The short name does not work. Select it under Output style in `/config`, or put `{"outputStyle": "simple-korean:simple-korean"}` in `~/.claude/settings.json`. The session-start hook adds a rule block of 2,271 characters to each session. The token count that `claude plugin details simple-korean` shows does not include this block.

### Codex

For Codex, install the plugin. The session-start hook installs with it.

```bash
codex plugin marketplace add say8425/SimpleKorean
codex plugin add simple-korean@simple-korean
```

Before Codex runs a hook for the first time, it asks if you trust the hook. The session-start hook needs Node.js. The writing-check hook for Claude Code needs Python 3.9 or later. For details, see [`src/hooks/README.md`](../src/hooks/README.md).

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

Below are two documents that the same model wrote for the same task: a troubleshooting section for a CLI tool. The left one was written without the skill, and the right one with the default mode of SimpleKorean on. We copied both documents without changes. They are in Korean, because this skill makes the model write Korean.

<!-- example:start -->
<table>
<tr>
<th width="50%">Written without the skill</th>
<th width="50%">Written with SimpleKorean on</th>
</tr>
<tr>
<td valign="top">

<!-- source: evals/results/2026-10-08/docs/baseline__troubleshooting__r1.json -->
<!-- simple-korean: off -->
> ## 문제 해결
>
> **Postgres 연결 타임아웃**
> `connection timed out` 오류가 나면 먼저 호스트와 포트(기본 5432)에 네트워크로 접근할 수 있는지 확인하세요. 방화벽, 보안 그룹, VPN 설정이 흔한 원인입니다. 서버가 느리게 응답하는 환경이라면 `--connect-timeout 30`처럼 제한 시간을 늘려 보세요. 클라우드 DB를 쓴다면 접속하는 IP가 허용 목록에 있는지도 확인하세요. 연결 문자열의 `sslmode` 값이 서버 설정과 맞는지도 점검하세요.
>
> **S3 권한 오류**
> `AccessDenied`나 `403`이 나오면 사용 중인 자격 증명이 맞는지 `aws sts get-caller-identity`로 확인하세요. 해당 IAM 역할에 대상 버킷의 `s3:GetObject`, `s3:PutObject`, `s3:ListBucket` 권한이 있어야 합니다. 버킷 정책이나 리전 설정이 다르지 않은지도 살펴보세요. 임시 자격 증명을 쓴다면 만료 여부도 확인하세요.
<!-- simple-korean: on -->

</td>
<td valign="top">

<!-- source: evals/results/2026-10-08/docs/plain__troubleshooting__r1.json -->
<!-- simple-korean: off -->
> ## 연결 타임아웃
>
> sqlpipe가 `dial tcp: i/o timeout` 오류를 내면 Postgres 연결이 실패한 것입니다.
>
> 1. sqlpipe를 실행하는 호스트가 Postgres 포트(기본값 5432)에 연결할 수 있는지 확인하세요.
> 2. 방화벽이나 보안 그룹이 연결을 막으면 규칙을 고치세요.
> 3. 데이터베이스가 관리형(RDS, Cloud SQL)이면 인스턴스가 sqlpipe의 IP에서 오는 연결을 허용하는지 확인하세요.
>
> ## S3 권한 오류
>
> sqlpipe가 S3에 쓰지 못하면 `AccessDenied` 오류를 냅니다. 이 오류는 sqlpipe가 쓰는 자격 증명에 권한이 없다는 뜻입니다.
>
> 1. sqlpipe를 실행하는 호스트에서 자격 증명이 올바른 계정을 가리키는지 확인하세요.
> 2. 대상 버킷에 `s3:PutObject` 권한이 있는지 확인하세요.
> 3. 버킷 정책이 해당 자격 증명을 거부하면 정책을 고치세요.
<!-- simple-korean: on -->

</td>
</tr>
</table>

The raw files are `evals/results/2026-10-08/docs/baseline__troubleshooting__r1.json` (left) and `evals/results/2026-10-08/docs/plain__troubleshooting__r1.json` (right).

Reply examples and more document examples are in [`examples/before-after.md`](../examples/before-after.md).
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
