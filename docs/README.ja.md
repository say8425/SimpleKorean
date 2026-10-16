<p align="center">
  <strong>AIが書いた韓国語の技術文書を、整備マニュアルのように読めるようにします。</strong>
</p>

<p align="center">
  <a href="../README.md">한국어</a> | <a href="README.en.md">English</a> | 日本語 | <a href="README.zh.md">中文</a> | <a href="README.es.md">Español</a>
</p>

<p align="center">
  <a href="https://agentskills.io"><img src="https://img.shields.io/badge/SKILL.md-open_standard-blue?style=flat" alt="Agent Skills"></a>
  <a href="https://github.com/say8425/SimpleKorean/releases/latest"><img src="https://img.shields.io/github/v/release/say8425/SimpleKorean?label=version&style=flat" alt="version"></a>
  <a href="../LICENSE"><img src="https://img.shields.io/badge/license-MIT-lightgrey?style=flat" alt="MIT"></a>
</p>

SimpleKorean は、LLM が技術文書とチャットの回答をやさしい韓国語で書くようにするエージェントスキルです。航空機の整備マニュアルでは、ASD-STE100 という統制英語を使います。そのルールを [SimpleEnglish](https://github.com/AminBlg/SimpleEnglish) から取り入れ、韓国語の文法に合わせて作り直しました。さらに、実際の韓国語の開発文書で測った外来語の表記リストを加えました。

[Agent Skills 標準](https://agentskills.io)を読み込むエージェントで動きます。たとえば Claude Code、Cursor、Codex、Gemini CLI、OpenCode です。

## インストール

### Claude Code

Claude Code には、プラグインとしてインストールしてください。プラグインには、セッション開始フック、執筆チェックフック、出力スタイルが入っています。

```bash
claude plugin marketplace add say8425/SimpleKorean && claude plugin install simple-korean@simple-korean
```

出力スタイルの名前は `simple-korean:simple-korean` です。短い名前では見つかりません。`/config` の Output style で選ぶか、`~/.claude/settings.json` に `{"outputStyle": "simple-korean:simple-korean"}` を書いてください。セッション開始フックは、セッションごとに2,271文字のルールブロックを追加します。`claude plugin details simple-korean` が表示するトークン数には、このブロックは含まれません。

### Codex

Codex には、プラグインとしてインストールしてください。セッション開始フックも一緒にインストールされます。

```bash
codex plugin marketplace add say8425/SimpleKorean
codex plugin add simple-korean@simple-korean
```

Codex は、フックを初めて実行する前に、信頼するかどうかを尋ねます。セッション開始フックには Node.js が必要です。Claude Code の執筆チェックフックには Python 3.9 以上が必要です。詳しくは [`src/hooks/README.md`](../src/hooks/README.md) を参照してください。

### その他のエージェント

その他のエージェントには、[skills CLI](https://github.com/vercel-labs/skills) でインストールしてください。

```bash
pnpm dlx skills add say8425/SimpleKorean
```

npm を使う場合は `npx skills add say8425/SimpleKorean` を実行してください。このコマンドはスキルだけをインストールします。上で説明したフックと出力スタイルはインストールしません。

### スキルに対応していないツール

スキルに対応していないツールには、[`prompts/system-prompt.md`](../prompts/system-prompt.md) のルールブロックを貼り付けてください。システムプロンプト、`AGENTS.md`、`.cursorrules` に入れてください。このファイルの最後には、約120トークンの短い版もあります。

### インストールした後

インストールしたら、技術文書を依頼してください。すでにある文章を直すときは、「simple-korean으로 고쳐 줘」（simple-korean で直して）と伝えてください。

## 例

同じ質問に同じモデルが答えた生の出力です。どちらの回答も手を加えずに載せました。このスキルはモデルに韓国語を書かせるものなので、回答は韓国語のままです。

<!-- example:start -->
スキルなしで書いた回答（`evals/results/2026-10-08/reply/baseline__oom__r1.txt`）：

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

同じモデルが SimpleKorean を有効にして書いた回答（`evals/results/2026-10-08/reply/plain__oom__r1.txt`）：

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

文書の例は [`examples/before-after.md`](../examples/before-after.md) にあります。
<!-- example:end -->

## ベンチマーク

下の数値はすべて、コミットした生の出力から計算し直した値です。CI がプッシュのたびに `evals/check_numbers.py` で照合します。文書と回答は `claude-sonnet-5-5`（effort low）が書き、判定は `claude-opus-5-5` が行いました。どの実行も、ユーザー設定、MCP サーバー、AGENTS.md のような指示ファイルを読み込んでいません。判定モデルも Claude なので、同じ系列に有利な偏りがあるかもしれません。語節（어절）は、韓国語で空白によって区切られる単位です。

<!-- benchmark:start evals/results/2026-10-08 -->
### 回答

専門用語を1つずつ含む質問8個を、条件ごとに2回ずつ尋ねました。回答は全部で32個です。スキルを有効にすると、読者に見える欠陥（em-dash、太字、見出し、箇条書き）が100%減りました（394個から0個）。ブラインド判定では、SimpleKorean の回答が16組のうち15組で勝ち、1組で引き分け、0組で負けました。

| 条件 | 回答数 | 平均語節数 | 平均文数 | em-dash | 太字 | 見出し | 箇条書き | 挨拶と結び |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| スキルなし | 16 | 246 | 30.9 | 0 | 141 | 45 | 208 | 12 |
| SimpleKorean | 16 | 179 | 18.6 | 0 | 0 | 0 | 0 | 1 |

### 文書

sqlpipe の文書課題8個を、条件ごとに2回ずつ書きました。比率は、リンターが数えた件数を語節数で割った値です。リンターは正規表現による検査なので、順位ではなく傾向として読んでください。

| 条件 | 文書数 | 100語節あたりのエラー | 100語節あたりの警告 | 100語節あたりの翻訳調 | 指定表記の比率 | やさしい語の比率 | 最長の文 |
|---|---:|---:|---:|---:|---:|---:|---:|
| スキルなし | 16 | 0.00 | 1.09 | 0.14 | 95.0% | 40.2% | 18語節 |
| 基本モード | 16 | 0.00 | 0.00 | 0.00 | 100.0% | 44.8% | 16語節 |
| 厳格モード | 16 | 0.00 | 0.00 | 0.00 | 100.0% | 45.5% | 17語節 |

生の出力、表記の分布、測定条件は [`evals/results/2026-10-08/RESULTS.md`](../evals/results/2026-10-08/RESULTS.md) にあります。
<!-- benchmark:end -->

## ルール

ルールは [`SKILL.md`](../skills/simple-korean/SKILL.md) にあります。点検モードと厳格モードで使う K 番号のルールの全体は、[`rule-catalog.md`](../skills/simple-korean/references/rule-catalog.md) にあります。

### 回答のルール

チャットの回答には、どのモードでも次のルールを使います。

| ルール | 防ぐもの |
|---|---|
| 地の文で答えます。見出し、箇条書き、太字、表を使いません | 1行で済む答えを囲む書式 |
| 最初の文に答えを書きます | 質問を繰り返す前置き |
| em-dash を使いません | 半分だけつなげた考え |
| 概念を表す用語は、初めて使うときに短く説明します | 読者が調べなければならない用語 |
| 1つの回答は1つの文体で書き、挨拶と結びを書きません | 「좋은 질문입니다」（良い質問です）、「도움이 되셨기를 바랍니다」（お役に立てば幸いです） |

### 文書のルール

文書には次のルールを使います。README、ランブック、エラーメッセージ、リリースノート、障害報告書が対象です。

| ルール | 防ぐもの |
|---|---|
| 手順文は15語節以下、説明文は20語節以下で書きます | どこまでも続く冗長な文 |
| 条件は「-면」（〜なら）で命令の前に置きます | 命令の後ろに付いて遅れて読まれる「단, ~경우」（ただし〜の場合） |
| 能動態と単純な時制で書きます | 「되어지다」（二重受動）、「~에 의해」（〜によって）、「-고 있습니다」（〜しています） |
| 推測と勧めの語尾を使いません | 「-ㄹ 수도 있습니다」（〜かもしれません）、「-것 같습니다」（〜ようです）、「-하는 것이 좋습니다」（〜するのがよいです） |
| 1つの語には1つの意味だけを与えます | 「확인」「검증」「점검」「체크」（どれも「確認」の意）を入れ替えて使うこと |
| 助詞を省かず、名詞形で文を終えません | 「백업 확인 필요」（バックアップ確認必要）のような電報文 |
| 重要さではなく事実を書きます | 「강력한」（強力な）、「원활한」（円滑な）、「단순히 X가 아니라 Y」（単に X ではなく Y） |
| 決められた外来語の表記を使います | 1つの文書の中で混ざる「디렉토리」と「디렉터리」（どちらも「ディレクトリ」） |

## モード

### 基本モード

基本モードは、上のルールのすべてです。特に有効にする必要はありません。

### 厳格モード

厳格モードは、「엄격 모드」（厳格モード）、「통제 언어」（統制言語）、「KS A 0001」、「STE」と言うと有効になります。厳格モードでは、文書の文末を5つの形に限ります。義務は「-해야 합니다」（〜しなければなりません）、禁止は「-하면 안 됩니다」（〜してはいけません）、許可は「-해도 됩니다」（〜してもかまいません）、能力は「-ㄹ 수 있습니다」（〜できます）、事実は現在形です。接続語「(이)나」（〜や、〜か）を使わず、条件は「-면」だけで書きます。根拠は KS A 0001:2023 の附属書 H と I です。回答は、厳格モードでも基本モードのルールに従います。

### 点検モード

点検モードは、文章を書く代わりに点検を依頼すると有効になります。違反ごとに、K 番号、該当する語句、直した文を示します。

## 表記方針

外来語は、外来語表記法と国立国語院の用例に従います（디렉터리、메시지、애플리케이션。ディレクトリ、メッセージ、アプリケーション）。原則だけで答えが出ない語は、[`data/terms.json`](../data/terms.json) のリストに従います。このリストは、ローカライズ文書、ベンダー文書、企業の技術ブログ、GitHub の README での実際の表記を数えて作りました。根拠は [`docs/research/loanword-spelling-usage.md`](../docs/research/loanword-spelling-usage.md) にあります。

| グループ | 使う形 |
|---|---|
| 規範どおりに使われる語23個 | 規範形（메시지、애플리케이션、메서드、라이선스。メッセージ、アプリケーション、メソッド、ライセンス） |
| 出典によって分かれる語4個 | 規範形（디렉터리、릴리스、셸、리디렉션。ディレクトリ、リリース、シェル、リダイレクト） |
| 慣用が定着した語4個 | 레포지토리、바디、칼럼、대상（リポジトリ、ボディ、カラム、ターゲット） |
| 公式の表記がない語2個 | 리디렉션、리팩터링（リダイレクト、リファクタリング） |
| 外来語と固有語から選ぶ語5個 | 오류、매개변수、사용자、기본값、배포（エラー、パラメーター、ユーザー、デフォルト値、デプロイ） |
| 分かち書き4個 | 기본값、매개변수、반환값、오픈소스（デフォルト値、パラメーター、戻り値、オープンソース。続けて書く） |

製品名、画面の文言の引用、API のオブジェクト名、コードは、元の表記のまま残します。

## よくある質問

### STE の韓国語版ですか？

いいえ。ASD-STE100 には韓国語版がなく、韓国語の統制言語の国家標準もありません。SimpleKorean は、STE のルールの目的を韓国語の文法で作り直した非公式の基準です。厳格モードの文末と接続語のルールは、KS A 0001:2023 に基づいています。

### 레포지토리（リポジトリ）と바디（ボディ）は、なぜ規範と違うのですか？

国立国語院の用例は「리포지터리」（リポジトリ）と「보디」（ボディ）です。しかし、この2つの形は実際の文書ではほとんど使われません。ベンダー文書のサンプルでは、「리포지터리」は1,104回のうち0回でした。そこで、読者が見てわかる慣用形を指定表記にしました。

### 会社の表記が違う場合はどうしますか？

リポジトリの最上位に `.simple-korean.json` を置いてください。セッション開始フックがこのファイルを見つけ、変更された指定表記をモデルに伝えます。リンターと執筆チェックフックもこのファイルに従い、変更前の指定表記を使うと警告します。指定表記には、ハングル、英字、数字、空白だけを20文字まで使えます。スキップする文字列（`skip`）は100個までです。形式の誤った設定と、語のリストにない概念は無視します。

```json
{"terms": {"release": {"write": "릴리즈"}, "column": "컬럼"}, "spacing": "attached"}
```

この例の「릴리즈」は release、「컬럼」は column のことです。

### 文章を整えるスキルとは何が違いますか？

im-not-ai のような文章を整えるスキルは、すでに書いた文章から AI らしい文体と翻訳調を取り除きます。SimpleKorean は、最初からルールどおりに書かせます。文書の構成と回答の形式も決めます。たとえば、条件を命令の前に置き、1つの文には動作を1つだけ書きます。リンターと測定結果も一緒にあります。

### 15/20語節という数字はどこから来たのですか？

韓国語の技術文書について、文の長さの上限を決めた実証研究は見つかりませんでした。そのため、設計として決めた値です。調整の段階で、ルールを守った例文と基準となる出力の文の長さを測りました。結果は [`evals/calibration/RECORD.md`](../evals/calibration/RECORD.md) にあります。

### 厳格モードには、なぜ韓国語の承認辞書がないのですか？

韓国語には、STE の辞書のように承認語と非承認語をまとめて決めた公開リストがありません。調査の内容は [`docs/research/korean-controlled-language.md`](../docs/research/korean-controlled-language.md) にあります。韓国語は、義務や許可のような意味を、語よりも文末で表します。そこで厳格モードでは、語の代わりに文末と接続語を閉じたリストにまとめます。

## 元のプロジェクトとの関係

SimpleKorean は、[AminBlg/SimpleEnglish](https://github.com/AminBlg/SimpleEnglish) v2.1.1（`a6fcb4f`）から分かれた非公式の派生プロジェクトです。リポジトリの構成、フック、リンターのインターフェース、測定の方法は、元のプロジェクトから取り入れました。ルール、語のリスト、測定の課題は、韓国語に合わせて新しく書きました。元のプロジェクトの英語の測定結果は取り入れていません。

## 貢献

質問とバグは Issue で知らせてください。PR を歓迎します。公開した数値を変える変更では、生の出力も一緒にコミットし、数値の検証に通る必要があります。数値の検証には kiwipiepy が必要です。

```bash
uv venv .venv --python 3.12 && uv pip install --python .venv/bin/python kiwipiepy==0.24.0 kiwipiepy-model==0.24.0
.venv/bin/python evals/check_numbers.py
```

PR を出す前に、`python3 evals/ko_lint.py --self-test` と `python3 evals/tests/run.py` を実行してください。

PR のタイトルは `fix: 설정 파일의 지정형을 20자로 제한한다` のように `<種類>: <韓国語の文>` の形で書いてください。文は韓国語の平叙形（`-ㄴ다`）で終えます。種類は feat、fix、perf、refactor、docs、test、chore、ci のいずれかです。PR をマージすると、タイトルがそのまま変更履歴の 1 行になります。新しいリリースを作るのは feat、fix、perf だけです。韓国語でタイトルを書けない場合は英語で書いてください。マージの前にメンテナーが書き直します。それまではタイトルの検査が失敗します。

## ライセンス

コードと語のリストは MIT です。[`data/basic-vocabulary/grades.tsv`](../data/basic-vocabulary/grades.tsv) は国立国語院の「国語基礎語彙等級リスト」から取り入れたもので、公共ヌリ第1類型（出典表示）に従います。第三者の出典は [`NOTICE`](../NOTICE) にあります。

非公式のプロジェクトです。ASD、元のプロジェクトの作者、国立国語院、韓国標準協会とは関係がありません。ASD-STE100 は ASD の登録商標です。

この翻訳はネイティブスピーカーの確認を受けていません。誤りは [Issue](https://github.com/say8425/SimpleKorean/issues) でお知らせください。
