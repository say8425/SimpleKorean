<p align="center">
  Makes Korean technical documents written by AI read like a maintenance manual.
</p>

<p align="center">
  <a href="../README.md">한국어</a> | English | <a href="README.ja.md">日本語</a> | <a href="README.zh.md">中文</a> | <a href="README.es.md">Español</a>
</p>

<p align="center">
  <a href="https://agentskills.io"><img src="https://img.shields.io/badge/SKILL.md-open_standard-blue?style=flat" alt="Agent Skills"></a>
  <a href="https://github.com/say8425/SimpleKorean/releases/latest"><img src="https://img.shields.io/github/v/release/say8425/SimpleKorean?label=version&style=flat" alt="version"></a>
  <a href="../LICENSE"><img src="https://img.shields.io/badge/license-MIT-lightgrey?style=flat" alt="MIT"></a>
</p>

SimpleKorean is an agent skill that makes LLMs write plain Korean in technical documents and chat replies. Aircraft maintenance manuals use a controlled English called ASD-STE100. We took its rules from [SimpleEnglish](https://github.com/AminBlg/SimpleEnglish) and rebuilt them for Korean grammar. We also added a list of loanword spellings. We built this list by counting the spellings used in real Korean developer documents.

The skill runs in agents that read the [Agent Skills standard](https://agentskills.io). Examples are Claude Code, Cursor, Codex, Gemini CLI, and OpenCode.

## Letting an agent follow it without installing

You can give an agent only the address of this repository and tell it to follow it. This section is the instruction that the agent reads in that case.

Follow this section when a user asks you to write by the rules of this repository without installing it. The rule tables in this README are summaries. The full rules are at `https://raw.githubusercontent.com/say8425/SimpleKorean/main/skills/simple-korean/SKILL.md`.

If you have a shell and Node.js, tell the user about the command below. Then run it. It prints all of `SKILL.md`. It also tells you the directory where it downloaded the reference files.

```bash
npx skills use say8425/SimpleKorean@simple-korean
```

If the command fails or you cannot use a shell, read `SKILL.md` to the end from the raw URL above (a URL that returns only the file text). If your fetch tool summarizes the content, ask it for the original text. If you have `curl`, use `curl`.

In `SKILL.md`, read paths that start with `references/` from the directory of `SKILL.md`. For example, `references/strict-mode.md` is `https://raw.githubusercontent.com/say8425/SimpleKorean/main/skills/simple-korean/references/strict-mode.md`. The full word list is at `https://raw.githubusercontent.com/say8425/SimpleKorean/main/data/terms.json`. Use raw URLs, not GitHub `blob` URLs. A `blob` URL returns an HTML page instead of the source text.

Without installation, the hooks (scripts that the agent runs automatically at set times) do not run. So you must do their work yourself:

- If the agent summarizes a long conversation to shorten it, read `SKILL.md` again.
- Before you send a reply or a document, do the self-check in `SKILL.md` (the section "내기 전 자가 점검").
- If you have a shell, git, and Python 3.9 or later, check what you wrote with the linter (a script that counts rule violations).

If `/tmp/SimpleKorean` does not exist, get the repository first:

```bash
git clone --depth 1 https://github.com/say8425/SimpleKorean.git /tmp/SimpleKorean
```

Check a document with the first command and a reply with the second. For a document with procedures, add `--type procedural` to the first command:

```bash
python3 /tmp/SimpleKorean/evals/ko_lint.py doc.md
python3 /tmp/SimpleKorean/evals/ko_lint.py --type reply - < reply.txt
```

The linter prints violation counts as JSON. For a document, `errors_total` and `warnings_total` must be 0. For a reply, `visible_total` must be 0.

## Install

### Claude Code

For Claude Code, install the plugin.

```bash
claude plugin marketplace add say8425/SimpleKorean
claude plugin install simple-korean@simple-korean
```

The plugin contains the five parts below. The skill and the three hooks work automatically in new sessions after you install the plugin. The output style works only when you apply it yourself. The rule block that the session-start hook and the output style add is a condensed version of the skill's rules.

| Part | What it does | Activation | Needs |
|---|---|---|---|
| Skill | Holds the full rules, strict mode, and review mode. The model reads it when it needs it. | Automatic | None |
| Session-start hook | Adds the rule block to each session. The model follows the rules even if you do not name the skill. | Automatic | Node.js |
| File-check hook | Checks the Markdown files that the model writes or edits. It reports violations to the model. | Automatic | Python 3.9 or later |
| Reply-check hook | Checks the model's last reply. It reports violations on the screen. | Automatic | Python 3.9 or later |
| Output style | Puts the same rule block as the session-start hook in the system prompt. | Optional | None |

The rules apply without the output style, because the session-start hook already adds the same rule block. If the session-start hook does not run because Node.js is missing, apply the output style. To apply the output style, select it under Output style in `/config`. Or put `{"outputStyle": "simple-korean:simple-korean"}` in `~/.claude/settings.json`.

The session-start hook adds a rule block of 2,476 characters to each session. For details, see [`src/hooks/README.md`](../src/hooks/README.md).

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

To use the skill once without installing it, run `npx skills use say8425/SimpleKorean@simple-korean`. This command prints a prompt that contains the skill. Add `--agent claude-code` to run Claude Code with that prompt.

### Tools without skill support

For tools that do not support skills, paste the rule block from [`prompts/system-prompt.md`](../prompts/system-prompt.md). You can put it in a system prompt, `AGENTS.md`, or `.cursorrules`. The end of `prompts/system-prompt.md` also has a short version of about 120 tokens.

### Bots and programs

Put a reply variant in the system prompt of a bot. The reply variants split the reply rules of the rule block into two files. [`prompts/sentence-rules.ko.md`](../prompts/sentence-rules.ko.md) has the sentence rules. It also has the rule that removes slop words (empty words common in AI text) and translationese. [`prompts/format-rules.ko.md`](../prompts/format-rules.ko.md) has the formatting rules, such as headers, bold text, and tables. The two files together make the full reply rules.

Apart from the slop and translationese rule, the reply variants do not have the document rules. The files whose names end in `.en.md` have the same rules, written in English. The first line of each file is an HTML comment with the variant, the language, and the version.

To pin a variant, download it from the raw URL of a release tag, for example `https://raw.githubusercontent.com/say8425/SimpleKorean/<tag>/prompts/sentence-rules.ko.md`. The variant files keep the same path in every tag.

In Python, install the `simple-korean` package from PyPI. The package uses only the standard library. Replace `<version>` with a release version:

```bash
pip install "simple-korean==<version>"
```

If you cannot reach PyPI, install from a release tag on GitHub:

```bash
pip install "git+https://github.com/say8425/SimpleKorean@<tag>"
```

```python
from simple_korean import __version__, prompt_block

prompt = prompt_block(variant="sentences", lang="en")
```

`variant` is `sentences` or `format`. `lang` is the language of the rule text, `ko` or `en`. `lang` does not set the language of the reply.

The package also has the linter. `lint_detail(text, "reply")` finds em-dashes, slop words, greetings, sign-offs, bold text, tables, and a header or list on the first line of a reply. With `formatting=False`, it does not look for bold text, tables, or the first line. It does not look for translationese or a mix of writing styles.

To check against the document rules, use `"descriptive"` or `"procedural"` instead of `"reply"`. Each hit has `category`, `severity`, `line`, and `text`.

### After installing

After you install, ask for a technical document. To fix existing text, say "simple-korean으로 고쳐 줘" (fix this with simple-korean).

## Example

Below are two documents in which the same model polished the same draft: a troubleshooting section for a CLI tool. We put em-dashes, bold text, and middle dots in the draft on purpose. The first column of the table is the draft. The second was polished without the skill, and the third with the default mode of SimpleKorean on. We copied all three texts without changes. They are in Korean, because this skill makes the model write Korean.

<!-- example:start -->
<table>
<tr>
<th width="34%">Draft</th>
<th width="33%">Polished without the skill</th>
<th width="33%">Polished with SimpleKorean on</th>
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

The raw files of the polished documents are `evals/results/2026-10-21/docs/baseline__polish__r1.json` (middle) and `evals/results/2026-10-21/docs/plain__polish__r1.json` (right).

The draft is the `polish` task in [`evals/results/2026-10-21/inputs/scenarios.json`](../evals/results/2026-10-21/inputs/scenarios.json).

Reply examples and more document examples are in [`examples/before-after.md`](../examples/before-after.md). [This commit's diff](https://github.com/say8425/SimpleKorean/commit/ca720c2beaed9572581ed132e99237ad2e3d794a) shows what changed in each example.
<!-- example:end -->

## Benchmark

We calculated all numbers below again from the committed raw outputs. On each push, CI compares them with `evals/check_numbers.py`. `claude-sonnet-5-5` (effort low) wrote the documents and the replies, and `claude-opus-5-5` judged them. No run read user settings, MCP servers, or instruction files such as AGENTS.md. The judge model is also Claude, so it can favor replies from the same model family. An eojeol is a Korean word unit separated by spaces.

<!-- benchmark:start evals/results/2026-10-21 -->
### Replies

We asked 8 questions 2 times in each condition. Each question contains one technical term, one em-dash, and one middle dot (·). The reply rules do not ban the middle dot, so we counted it separately and left it out of the defects. There are 32 replies in total. With the skill on, reader-visible defects (em-dashes, bold text, tables, a header or list on the first line) fell by 100% (from 162 to 0). In a blind judgment of 16 pairs, the SimpleKorean reply won 12, tied 3, and lost 1. Even with an em-dash in every question, the replies without the skill used no em-dashes. So the polishing task in the documents section below tests whether the skill removes them.

| Condition | Replies | Mean eojeol | Mean sentences | em-dash | Bold | Tables | First-line header or list | Middle dot | Headers | Bullets | Greetings and sign-offs |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| No skill | 16 | 266 | 31.2 | 0 | 155 | 3 | 4 | 26 | 36 | 211 | 13 |
| SimpleKorean | 16 | 223 | 31.0 | 0 | 0 | 0 | 0 | 2 | 54 | 173 | 5 |

### Documents

The model wrote each of 8 sqlpipe documentation tasks 2 times in each condition. Each rate is the linter's count divided by the eojeol count. The linter is a regex check, so read the numbers as a direction, not as a ranking.

| Condition | Documents | Errors per 100 eojeol | Warnings per 100 eojeol | Translationese per 100 eojeol | Designated spelling rate | Easy word rate | Longest sentence |
|---|---:|---:|---:|---:|---:|---:|---:|
| No skill | 16 | 0.14 | 0.71 | 0.42 | 100.0% | 41.9% | 18 eojeol |
| Default mode | 16 | 0.00 | 0.17 | 0.17 | 100.0% | 45.3% | 15 eojeol |
| Strict mode | 16 | 0.00 | 0.00 | 0.00 | 100.0% | 39.6% | 13 eojeol |

The task of polishing a draft with deliberately added em-dashes, bold text, and middle dots is counted separately, not in the table above. The draft has these marks: em-dash 2, bold 2, middle dot 3. The table below sums these marks in the polished documents of each condition. Each condition polished the draft 2 times, so if every mark stayed, the sums would be em-dash 4, bold 4, and middle dot 6. The document rules do not ban the middle dot either, so we count it for reference only. The draft is the `polish` task in [`evals/results/2026-10-21/inputs/scenarios.json`](../evals/results/2026-10-21/inputs/scenarios.json).

| Condition | Documents | em-dash | Bold | Middle dot |
|---|---:|---:|---:|---:|
| No skill | 2 | 4 | 4 | 1 |
| Default mode | 2 | 0 | 0 | 0 |
| Strict mode | 2 | 0 | 0 | 0 |

The raw outputs, the spelling distribution, and the test conditions are in [`evals/results/2026-10-21/RESULTS.md`](../evals/results/2026-10-21/RESULTS.md).
<!-- benchmark:end -->

## Rules

The rules are in [`SKILL.md`](../skills/simple-korean/SKILL.md). Review mode and strict mode use the full list of rules in [`rule-catalog.md`](../skills/simple-korean/references/rule-catalog.md). Default-mode rules have K numbers, such as K1.1. Strict-mode rules have S numbers, such as S1.

### Reply rules

Chat replies use these rules in all modes.

| Rule | What it stops |
|---|---|
| Use headers and lists when the content and length of the answer call for them. Do not use bold text or tables | Formatting around a one-line answer |
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

Strict mode turns on when you say "엄격 모드" (strict mode), "통제 언어" (controlled language), "KS A 0001", "STE", or "ASD-STE100". Strict mode limits the sentence endings in documents to five forms. Obligation is "-해야 합니다" (must). Prohibition is "-하면 안 됩니다" (must not). Permission is "-해도 됩니다" (may). Ability is "-ㄹ 수 있습니다" (can). Facts use the present tense. Strict mode does not use the connective "(이)나" (or), and it writes conditions only with "-면" (if). The source is Annexes H and I of KS A 0001:2023. In strict mode, replies still follow the default mode rules.

### Review mode

Review mode turns on when you ask for a review instead of new text. For each violation, it gives the K number, the text, and a corrected sentence.

## Spelling policy

Loanwords follow the Korean loanword orthography and the usage examples of the National Institute of Korean Language (디렉터리, 메시지, 애플리케이션). When these principles do not give an answer, the list in [`data/terms.json`](../data/terms.json) decides. We made this list from real spellings that we counted in localized documents, vendor documents, company tech blogs, and GitHub READMEs. The evidence is in [`docs/research/loanword-spelling-usage.md`](../docs/research/loanword-spelling-usage.md).

| Group | Form to use |
|---|---|
| 23 words used as the standard says | Standard form (메시지 message, 애플리케이션 application, 메서드 method, 라이선스 license) |
| 4 words that differ by source | Standard form (디렉터리 directory, 릴리스 release, 셸 shell, 리디렉션 redirection) |
| 4 words with a fixed common form | 레포지토리 (repository), 바디 (body), 칼럼 (column), 대상 (target) |
| 2 words with no official spelling | 리디렉션 (redirect), 리팩터링 (refactoring) |
| 5 words with a choice between a loanword and a native word | 오류 (error), 매개변수 (parameter), 사용자 (user), 기본값 (default value), 배포 (deployment) |
| 4 spacing cases | 기본값, 매개변수, 반환값, 오픈소스 (written without spaces) |

Product names, quoted screen text, API object names, and code keep their original spelling.

## FAQ

### Is this a Korean edition of STE?

No. ASD-STE100 has no Korean edition, and Korea has no national standard for a controlled language. SimpleKorean is an unofficial standard. It rebuilds the purpose of the STE rules for Korean grammar. The sentence-ending and connective rules of strict mode are based on KS A 0001:2023.

### Why do 레포지토리 and 바디 differ from the standard?

The usage examples of the National Institute of Korean Language are "리포지터리" (repository) and "보디" (body). But real documents almost never use these two forms. In a sample of vendor documents, "리포지터리" appeared 0 times in 1,104 cases. So we chose the common forms that readers recognize as the designated spelling.

### What if my company uses different spellings?

Put `.simple-korean.json` at the top of your repository. The session-start hook finds this file and tells the model the changed designated spellings. The linter and the file-check hook also follow this file. They warn when you use the designated spelling from before the change. A designated spelling can use only Hangul, Latin letters, digits, and spaces, up to 20 characters. You can list up to 100 strings to skip (`skip`). The session-start hook and the file-check hook use the default settings instead of settings with a wrong format. The linter stops with an error on such settings. The hooks and the linter both ignore concepts that are not in the word list.

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

The reply rules also differ from the original. The original bans headers and bullets in every reply. SimpleKorean lets the model decide from the content and length of each answer whether to use headers and lists. The evidence for this choice is in the [reply formatting study](../docs/research/reply-formatting.md) (in Korean).

Because the reply rules differ, the benchmark also counts different reply defects. The original counts em-dashes, bold text, headers, and bullets. SimpleKorean counts em-dashes, bold text, tables, and a header or list on the first line.

## Contributing

Report questions and bugs in an issue. PRs are welcome. A change to published numbers must include the raw outputs and pass the number check. The number check needs kiwipiepy.

Run these commands from the repository root:

```bash
uv venv .venv --python 3.12
uv pip install --python .venv/bin/python kiwipiepy==0.24.0 kiwipiepy-model==0.24.0
.venv/bin/python evals/check_numbers.py
```

Before you submit, run `python3 evals/ko_lint.py --self-test` and `python3 evals/tests/run.py`.

Write the PR title as `<type>: <Korean sentence>`, for example `fix: 설정 파일의 지정형을 20자로 제한한다`. The sentence ends in the plain declarative form (`-ㄴ다`). The type is one of feat, fix, perf, refactor, docs, test, chore, and ci. When we merge a PR, its title becomes one line of the changelog. Only feat, fix, and perf make a new release. If you cannot write the title in Korean, write it in English. The maintainer will change it before the merge, and the title check fails until then.

## License

The code and the word lists use the MIT license. [`data/basic-vocabulary/grades.tsv`](../data/basic-vocabulary/grades.tsv) comes from the basic Korean vocabulary grade list of the National Institute of Korean Language. It follows KOGL Type 1 (attribution). Third-party sources are in [`NOTICE`](../NOTICE).

This is an unofficial project. It has no relation to ASD, the original author, the National Institute of Korean Language, or the Korean Standards Association. ASD-STE100 is a registered trademark of ASD.

This translation was not reviewed by a native speaker. Please report errors in an [issue](https://github.com/say8425/SimpleKorean/issues).
