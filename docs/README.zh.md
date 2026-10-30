<p align="center">
  让 AI 写的韩语技术文档读起来像维修手册。
</p>

<p align="center">
  <a href="../README.md">한국어</a> | <a href="README.en.md">English</a> | <a href="README.ja.md">日本語</a> | 中文 | <a href="README.es.md">Español</a>
</p>

<p align="center">
  <a href="https://agentskills.io"><img src="https://img.shields.io/badge/SKILL.md-open_standard-blue?style=flat" alt="Agent Skills"></a>
  <a href="https://github.com/say8425/SimpleKorean/releases/latest"><img src="https://img.shields.io/github/v/release/say8425/SimpleKorean?label=version&style=flat" alt="version"></a>
  <a href="../LICENSE"><img src="https://img.shields.io/badge/license-MIT-lightgrey?style=flat" alt="MIT"></a>
</p>

SimpleKorean 是一个智能体技能，让 LLM 用简单的韩语写技术文档和聊天回答。航空维修手册使用受控英语 ASD-STE100。我们从 [SimpleEnglish](https://github.com/AminBlg/SimpleEnglish) 取来它的规则，按韩语语法重新制定。我们还加入了一份外来语写法列表，这份列表是在真实的韩语开发文档中统计得出的。

它可以在读取 [Agent Skills 标准](https://agentskills.io) 的智能体中运行，例如 Claude Code、Cursor、Codex、Gemini CLI、OpenCode。

## 不安装就让它照做

你可以只把这个仓库的地址交给智能体，让它照做。本节就是智能体这时要读的指示。

如果用户要求你不安装就按这个仓库的规则写作，请照本节去做。这份 README 中的规则表只是摘要。规则原文在 `https://raw.githubusercontent.com/say8425/SimpleKorean/main/skills/simple-korean/SKILL.md`。

如果有 shell 和 Node.js，请先把下面的命令告诉用户，然后运行它。这个命令会输出 `SKILL.md` 全文，还会告诉你参考文件下载到了哪个目录。

```bash
npx skills use say8425/SimpleKorean@simple-korean
```

如果命令失败或不能使用 shell，请从上面的 raw 地址（只返回文件原文的地址）把 `SKILL.md` 读到最后。如果抓取工具会总结内容，请要求它返回原文。如果有 `curl`，请用 `curl` 获取。

`SKILL.md` 中以 `references/` 开头的路径，以 `SKILL.md` 所在的目录为基准。例如 `references/strict-mode.md` 是 `https://raw.githubusercontent.com/say8425/SimpleKorean/main/skills/simple-korean/references/strict-mode.md`。完整的词表在 `https://raw.githubusercontent.com/say8425/SimpleKorean/main/data/terms.json`。请使用 raw 地址，不要用 GitHub 的 `blob` 地址。`blob` 地址返回的是 HTML 页面，不是原文。

不安装时钩子（智能体在固定时机自动运行的脚本）不会运行，所以你要自己完成钩子的工作：

- 智能体把长对话总结缩短后，请重新阅读 `SKILL.md`。
- 发出回答或文档之前，请做 `SKILL.md` 中的自查（“내기 전 자가 점검”一节）。
- 如果有 shell、git 和 Python 3.9 或更高版本，请用检查工具（统计规则违规的脚本）确认你写的内容。

如果没有 `/tmp/SimpleKorean`，请先获取仓库：

```bash
git clone --depth 1 https://github.com/say8425/SimpleKorean.git /tmp/SimpleKorean
```

文档用第一条命令检查，回答用第二条命令检查。写有操作步骤的文档，请在第一条命令中加上 `--type procedural`：

```bash
python3 /tmp/SimpleKorean/evals/ko_lint.py doc.md
python3 /tmp/SimpleKorean/evals/ko_lint.py --type reply - < reply.txt
```

检查工具以 JSON 输出违规数量。文档的 `errors_total` 和 `warnings_total` 必须为 0。回答的 `visible_total` 必须为 0。

## 安装

### Claude Code

在 Claude Code 中，请以插件方式安装。

```bash
claude plugin marketplace add say8425/SimpleKorean
claude plugin install simple-korean@simple-korean
```

插件包含下面五个部分。技能和三个钩子在安装后的新会话中自动生效。输出样式只有手动应用后才生效。会话启动钩子和输出样式加入的规则块是技能规则的精简版。

| 组成部分 | 作用 | 启用方式 | 需要 |
|---|---|---|---|
| 技能 | 包含全部规则、严格模式和检查模式。模型在需要时读取。 | 自动 | 无 |
| 会话启动钩子 | 在每个会话中加入规则块。即使不提技能名称，模型也会遵守规则。 | 自动 | Node.js |
| 文件检查钩子 | 检查模型写入或修改的 Markdown 文件，并把违规告诉模型。 | 自动 | Python 3.9 或更高版本 |
| 回答检查钩子 | 检查模型的最后一条回答，并在屏幕上显示违规。 | 自动 | Python 3.9 或更高版本 |
| 输出样式 | 把与会话启动钩子相同的规则块放进系统提示词。 | 可选 | 无 |

不用输出样式，规则也会生效，因为会话启动钩子已经加入了同一个规则块。如果没有 Node.js，会话启动钩子无法运行，这时请应用输出样式。要应用输出样式，请在 `/config` 的 Output style 中选择。或者在 `~/.claude/settings.json` 中写入 `{"outputStyle": "simple-korean:simple-korean"}`。

会话启动钩子会在每个会话中加入 2,476 个字符的规则块。详情见 [`src/hooks/README.md`](../src/hooks/README.md)。

### Codex

在 Codex 中，请以插件方式安装。会话启动钩子会一起安装。这个钩子需要 Node.js。

```bash
codex plugin marketplace add say8425/SimpleKorean
codex plugin add simple-korean@simple-korean
```

Codex 第一次运行钩子之前，会询问是否信任它。详情见 [`src/hooks/README.md`](../src/hooks/README.md)。

### 其他智能体

其他智能体可以用 [skills CLI](https://github.com/vercel-labs/skills) 安装。

```bash
pnpm dlx skills add say8425/SimpleKorean
```

如果使用 npm，请运行 `npx skills add say8425/SimpleKorean`。这个命令只安装技能，不安装上面介绍的钩子和输出样式。

如果不安装、只用一次，请运行 `npx skills use say8425/SimpleKorean@simple-korean`。这个命令会输出包含技能的提示词。加上 `--agent claude-code`，就会用这个提示词运行 Claude Code。

### 不支持技能的工具

对于不支持技能的工具，请粘贴 [`prompts/system-prompt.md`](../prompts/system-prompt.md) 中的规则块。可以放进系统提示词、`AGENTS.md` 或 `.cursorrules`。`prompts/system-prompt.md` 末尾还有一个约 120 token 的简短版本。

### 机器人和程序

请把回答用的版本放进机器人的系统提示词。回答用的版本把规则块中的回答规则分成了两个文件。[`prompts/sentence-rules.ko.md`](../prompts/sentence-rules.ko.md) 包含句子规则。删除套话（slop）词汇和翻译腔的规则也在这里。[`prompts/format-rules.ko.md`](../prompts/format-rules.ko.md) 包含标题、粗体、表格等格式规则。把两个文件拼在一起，就是完整的回答规则。

除了删除套话词汇和翻译腔的规则，回答用的版本不包含文档规则。文件名以 `.en.md` 结尾的文件用英语写了同样的规则。每个文件的第一行是 HTML 注释，写着版本类型、语言和版本号。

要固定版本，请从发布标签的 raw 地址下载，例如 `https://raw.githubusercontent.com/say8425/SimpleKorean/<tag>/prompts/sentence-rules.ko.md`。这些文件的路径在每个标签中都相同。

在 Python 中请从 PyPI 安装 `simple-korean` 软件包。软件包只使用标准库。请把 `<version>` 换成发布版本：

```bash
pip install "simple-korean==<version>"
```

如果无法访问 PyPI，请从 GitHub 的发布标签安装：

```bash
pip install "git+https://github.com/say8425/SimpleKorean@<tag>"
```

```python
from simple_korean import __version__, prompt_block

prompt = prompt_block(variant="sentences", lang="en")
```

`variant` 是 `sentences` 或 `format`。`lang` 是规则文字所用的语言，取 `ko` 或 `en`。`lang` 不决定回答的语言。

软件包里也有检查器（linter）。`lint_detail(text, "reply")` 在回答中查找 em-dash、套话词汇、问候语、结束语、粗体、表格，以及第一行的标题或列表。传入 `formatting=False` 时，不查找粗体、表格和第一行。它不查找翻译腔和文体混用。

要按文档规则检查，请把 `"reply"` 换成 `"descriptive"` 或 `"procedural"`。每条结果都有 `category`、`severity`、`line` 和 `text`。

### 安装之后

安装后，请让模型写技术文档。如果要修改已有的文字，请说“simple-korean으로 고쳐 줘”（用 simple-korean 修改）。

## 示例

以下是同一模型润色同一份草稿（CLI 工具的故障排查一节）得到的两份文档。我们故意在草稿里放了 em-dash、粗体和间隔号。表格第一列是草稿，第二列未启用技能，第三列启用了 SimpleKorean 的基本模式。三段文字都未作修改。本技能让模型写韩语，所以文档保持韩语原文。

<!-- example:start -->
<table>
<tr>
<th width="34%">草稿</th>
<th width="33%">未启用技能时润色的文档</th>
<th width="33%">启用 SimpleKorean 后润色的文档</th>
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

润色后文档的原始文件：中间是 `evals/results/2026-10-21/docs/baseline__polish__r1.json`，右边是 `evals/results/2026-10-21/docs/plain__polish__r1.json`。

草稿见 [`evals/results/2026-10-21/inputs/scenarios.json`](../evals/results/2026-10-21/inputs/scenarios.json) 中的 `polish` 任务。

回答示例和更多文档示例见 [`examples/before-after.md`](../examples/before-after.md)。每个示例的差异见[这个提交的 diff](https://github.com/say8425/SimpleKorean/commit/ca720c2beaed9572581ed132e99237ad2e3d794a)。
<!-- example:end -->

## 基准测试

下面的数字都是从已提交的原始输出重新计算的。每次推送时，CI 都会用 `evals/check_numbers.py` 核对这些数字。文档和回答由 `claude-sonnet-5-5`（effort low）编写，由 `claude-opus-5-5` 评判。所有运行都没有读取用户设置、MCP 服务器或 AGENTS.md 这类指令文件。评判模型也是 Claude，所以可能偏向同一系列的模型。语节（어절）是韩语中以空格分隔的单位。

<!-- benchmark:start evals/results/2026-10-21 -->
### 回答

我们把 8 个问题在每个条件下各问了 2 次，每个问题含一个专业术语、一个 em-dash 和一个间隔号（·）。回答规则不禁止间隔号，所以没有把它算作缺陷，而是单独统计。共得到 32 个回答。启用技能后，读者能看到的缺陷（em-dash、粗体、表格、第一行的标题或列表）减少了 100%（从 162 个降到 0 个）。在 16 组盲评中，SimpleKorean 的回答赢了 12 组，平了 3 组，输了 1 组。即使问题里有 em-dash，未启用技能的回答也没有使用 em-dash。所以技能能否去掉 em-dash，要看下面文档部分的草稿润色任务。

| 条件 | 回答数 | 平均语节数 | 平均句数 | em-dash | 粗体 | 表格 | 首行标题或列表 | 间隔号 | 标题 | 列表符号 | 问候语和结束语 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 无技能 | 16 | 266 | 31.2 | 0 | 155 | 3 | 4 | 26 | 36 | 211 | 13 |
| SimpleKorean | 16 | 223 | 31.0 | 0 | 0 | 0 | 0 | 2 | 54 | 173 | 5 |

### 文档

sqlpipe 的 8 个文档任务在每个条件下各写了 2 次。比率是检查器的计数除以语节数得到的值。检查器使用正则表达式，所以请把数字当作方向，而不是排名。

| 条件 | 文档数 | 每 100 语节错误 | 每 100 语节警告 | 每 100 语节翻译腔 | 规定写法比例 | 简单词比例 | 最长句子 |
|---|---:|---:|---:|---:|---:|---:|---:|
| 无技能 | 16 | 0.14 | 0.71 | 0.42 | 100.0% | 41.9% | 18 个语节 |
| 基本模式 | 16 | 0.00 | 0.17 | 0.17 | 100.0% | 45.3% | 15 个语节 |
| 严格模式 | 16 | 0.00 | 0.00 | 0.00 | 100.0% | 39.6% | 13 个语节 |

润色一份故意放入 em-dash、粗体和间隔号的草稿的任务不计入上表，而是单独统计。草稿里有 2 个 em-dash、2 处粗体和 3 个间隔号。下表是每个条件下润色后的文档中这些标记的总数。每个条件润色了 2 次，所以如果草稿的标记全部保留，总数会是 4 个 em-dash、4 处粗体和 6 个间隔号。文档规则也不禁止间隔号，所以只作参考统计。草稿见 [`evals/results/2026-10-21/inputs/scenarios.json`](../evals/results/2026-10-21/inputs/scenarios.json) 中的 `polish` 任务。

| 条件 | 文档数 | em-dash | 粗体 | 间隔号 |
|---|---:|---:|---:|---:|
| 无技能 | 2 | 4 | 4 | 1 |
| 基本模式 | 2 | 0 | 0 | 0 |
| 严格模式 | 2 | 0 | 0 | 0 |

原始输出、写法分布和测量条件见 [`evals/results/2026-10-21/RESULTS.md`](../evals/results/2026-10-21/RESULTS.md)。
<!-- benchmark:end -->

## 规则

规则在 [`SKILL.md`](../skills/simple-korean/SKILL.md) 中。检查模式和严格模式使用的全部规则在 [`rule-catalog.md`](../skills/simple-korean/references/rule-catalog.md) 中。基本模式的规则有 K 编号，例如 K1.1。严格模式的规则有 S 编号，例如 S1。

### 回答规则

在所有模式下，聊天回答都使用以下规则。

| 规则 | 防止的问题 |
|---|---|
| 根据回答的内容和长度决定是否使用标题和列表，不用粗体和表格 | 一行就能回答的内容外面套着格式 |
| 在第一句写出答案 | 重复问题的开场白 |
| 不用 em-dash | 只连接了一半的想法 |
| 概念术语第一次出现时，简短解释 | 读者需要另外查的术语 |
| 一个回答只用一种文体，不写问候语和结束语 | “좋은 질문입니다”（好问题）、“도움이 되셨기를 바랍니다”（希望对您有帮助） |

### 文档规则

文档使用以下规则。README、运行手册、错误消息、发布说明、故障报告都属于文档。

| 规则 | 防止的问题 |
|---|---|
| 步骤句不超过 15 个语节，说明句不超过 20 个语节 | 没完没了的冗长句子 |
| 用“-면”（如果……）把条件放在命令前面 | 跟在命令后面、读到时已经晚了的“단, ~경우”（但是，……的情况） |
| 使用主动语态和简单时态 | “되어지다”（双重被动）、“~에 의해”（由……）、“-고 있습니다”（正在……） |
| 不用推测和建议的词尾 | “-ㄹ 수도 있습니다”（也许会……）、“-것 같습니다”（好像……）、“-하는 것이 좋습니다”（最好……） |
| 一个词只给一个意思 | 交替使用“확인”（确认）、“검증”（验证）、“점검”（检查）、“체크”（check） |
| 不省略助词，不用名词形结尾 | “백업 확인 필요”（备份确认需要）这样的电报体 |
| 写事实，不写重要性 | “강력한”（强大的）、“원활한”（顺畅的）、“단순히 X가 아니라 Y”（不仅仅是 X，而是 Y） |
| 使用规定的外来语写法 | 同一篇文档里混用“디렉토리”和“디렉터리”（都指“目录”） |

## 模式

### 基本模式

基本模式就是上面的全部规则，不需要另外开启。

### 严格模式

说“엄격 모드”（严格模式）、“통제 언어”（受控语言）、“KS A 0001”、“STE”或“ASD-STE100”时，严格模式会开启。严格模式把文档的句尾限定为五种。义务用“-해야 합니다”（必须……），禁止用“-하면 안 됩니다”（不得……），许可用“-해도 됩니다”（可以……），能力用“-ㄹ 수 있습니다”（能够……），事实用现在时。不用连接词“(이)나”（或），条件只用“-면”。依据是 KS A 0001:2023 的附录 H 和 I。在严格模式下，回答也遵守基本模式的规则。

### 检查模式

请求检查而不是写作时，检查模式会开启。每处违规都会给出 K 编号、相关文字和修改后的句子。

## 写法规范

外来语遵守外来语标记法和国立国语院的用例（디렉터리、메시지、애플리케이션，即目录、消息、应用程序）。只靠原则得不出答案的词，遵守 [`data/terms.json`](../data/terms.json) 中的列表。这份列表统计了本地化文档、厂商文档、企业技术博客和 GitHub README 中的实际写法。依据见 [`docs/research/loanword-spelling-usage.md`](../docs/research/loanword-spelling-usage.md)。

| 类别 | 使用的形式 |
|---|---|
| 按规范使用的词 23 个 | 规范形（메시지、애플리케이션、메서드、라이선스，即消息、应用程序、方法、许可证） |
| 不同来源写法不同的词 4 个 | 规范形（디렉터리、릴리스、셸、리디렉션，即目录、发布、shell、redirection） |
| 惯用写法已经固定的词 4 个 | 레포지토리、바디、칼럼、대상（仓库、正文、列、目标） |
| 没有官方写法的词 2 个 | 리디렉션、리팩터링（redirect、重构） |
| 在外来语和韩语固有词之间选择的词 5 个 | 오류、매개변수、사용자、기본값、배포（错误、参数、用户、默认值、部署） |
| 空格规则 4 个 | 기본값、매개변수、반환값、오픈소스（默认值、参数、返回值、开源；连写） |

产品名称、引用的界面文字、API 对象名称和代码保留原来的写法。

## 常见问题

### 这是 STE 的韩语版吗？

不是。ASD-STE100 没有韩语版，韩国也没有韩语受控语言的国家标准。SimpleKorean 是一套非官方的准则，按韩语语法重新确立了 STE 规则的目的。严格模式的句尾规则和连接词规则以 KS A 0001:2023 为基础。

### 为什么 레포지토리（仓库）和 바디（正文）与规范不同？

国立国语院的用例是“리포지터리”（仓库）和“보디”（正文）。但是这两种形式在实际文档中几乎不用。在厂商文档样本中，1,104 次里“리포지터리”出现了 0 次。所以我们把读者认得出的惯用形定为规定写法。

### 如果公司的写法不同，怎么办？

请在仓库的根目录放一个 `.simple-korean.json`。会话启动钩子会找到这个文件，并把修改后的规定写法告诉模型。检查器和文件检查钩子也遵守这个文件，使用修改前的规定写法时会发出警告。规定写法只能用韩文、英文字母、数字和空格，最多 20 个字符。要跳过的字符串（`skip`）最多 100 个。会话启动钩子和文件检查钩子遇到格式错误的设置时改用默认设置。检查器遇到这种设置会报错并停止。词表中没有的概念，钩子和检查器都会忽略。

```json
{"terms": {"release": {"write": "릴리즈"}, "column": "컬럼"}, "spacing": "attached"}
```

这个例子中的“릴리즈”是 release，“컬럼”是 column。

### 它和润色技能有什么不同？

im-not-ai 这类润色技能会从已经写好的文字中去掉 AI 文风和翻译腔。SimpleKorean 让模型从一开始就按规则写。它还规定文档结构和回答格式。例如，条件放在命令前面，一个句子只写一个动作。它还附带检查器和测量结果。

### 15/20 个语节这个数字从哪里来？

我们没有找到为韩语技术文档规定句子长度上限的实证研究。所以这是设计时定的值。在校准时，我们测量了遵守规则的例句和基线输出的句子长度。结果见 [`evals/calibration/RECORD.md`](../evals/calibration/RECORD.md)。

### 为什么严格模式没有韩语的批准词典？

韩语没有像 STE 词典那样同时规定批准词和非批准词的公开列表。调查内容见 [`docs/research/korean-controlled-language.md`](../docs/research/korean-controlled-language.md)。韩语把义务、许可这类意思放在句尾，而不是放在词上。所以严格模式不限定词，而是把句尾和连接词限定为封闭列表。

## 与原项目的关系

SimpleKorean 是从 [AminBlg/SimpleEnglish](https://github.com/AminBlg/SimpleEnglish) v2.1.1（`a6fcb4f`）分出来的非官方派生项目。仓库结构、钩子、检查器接口和测量方法来自原项目。规则、词表和测量任务按韩语重新编写。我们没有沿用原项目的英语测量结果。

回答规则也与原项目不同。原项目在所有回答中都禁止标题和列表符号。SimpleKorean 让模型根据回答的内容和长度决定是否使用标题和列表。依据见[回答格式研究](../docs/research/reply-formatting.md)（韩语）。

由于回答规则不同，基准测试统计的回答缺陷也不同。原项目统计 em-dash、粗体、标题和列表符号。SimpleKorean 统计 em-dash、粗体、表格，以及第一行的标题或列表。

## 贡献

问题和 bug 请通过 Issue 告诉我们。欢迎提交 PR。如果修改会改变已公开的数字，请同时提交原始输出，并且必须通过数字核对。数字核对需要 kiwipiepy。

请在仓库根目录运行以下命令：

```bash
uv venv .venv --python 3.12
uv pip install --python .venv/bin/python kiwipiepy==0.24.0 kiwipiepy-model==0.24.0
.venv/bin/python evals/check_numbers.py
```

提交之前，请运行 `python3 evals/ko_lint.py --self-test` 和 `python3 evals/tests/run.py`。

PR 标题请写成 `<类型>: <韩语句子>`，例如 `fix: 설정 파일의 지정형을 20자로 제한한다`。句子用韩语的平述形（`-ㄴ다`）结尾。类型是 feat、fix、perf、refactor、docs、test、chore、ci 之一。合并 PR 后，标题会原样成为变更记录中的一行。只有 feat、fix、perf 会产生新版本。如果不会用韩语写标题，可以用英语写，维护者会在合并前改写，在此之前标题检查会失败。

## 许可证

代码和词表采用 MIT 许可证。[`data/basic-vocabulary/grades.tsv`](../data/basic-vocabulary/grades.tsv) 来自国立国语院的韩语基础词汇等级列表，遵守公共 Nuri 第 1 类型（注明出处）。第三方来源见 [`NOTICE`](../NOTICE)。

这是一个非官方项目，与 ASD、原项目作者、国立国语院和韩国标准协会都没有关系。ASD-STE100 是 ASD 的注册商标。

本译文未经母语者审校。如发现错误，请通过 [Issue](https://github.com/say8425/SimpleKorean/issues) 告诉我们。
