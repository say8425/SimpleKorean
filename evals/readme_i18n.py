"""README 다섯 언어판의 언어 표와 생성 블록의 문장 틀.

report.py와 make_examples.py는 이 틀로 언어마다 블록을 만들고, check_numbers.py는 같은 틀로 대조한다.
틀을 고치면 `report.py <결과 디렉터리> --readme`와 `make_examples.py <결과 디렉터리> --readme`로 README를 다시 쓴다.
"""

LANGS = ("ko", "en", "ja", "zh", "es")
README = {"ko": "README.md", "en": "docs/README.en.md", "ja": "docs/README.ja.md",
          "zh": "docs/README.zh.md", "es": "docs/README.es.md"}
NAMES = {"ko": "한국어", "en": "English", "ja": "日本語", "zh": "中文", "es": "Español"}
NBSP = " "

TEXT = {
    "ko": {
        "reply_intro": "### 답변\n\n전문용어가 하나씩 든 질문 {questions}개를 조건마다 {runs}번씩 물었습니다. 답변은 모두 {total}개입니다. ",
        "headline": ("스킬을 켜면 화면에 드러나는 결함(em-dash, 굵은 글씨, 표, 첫 줄의 헤더나 목록)이 {cut} 줄었습니다({base}개에서 {plain}개). "
                     "블라인드 판정에서 SimpleKorean 답변은 {n}쌍 가운데 {wins}쌍에서 이겼고, "
                     "{ties}쌍에서 비겼고, {losses}쌍에서 졌습니다."),
        "reply_header": "| 조건 | 답변 수 | 평균 어절 | 평균 문장 | em-dash | 굵은 글씨 | 표 | 첫 줄 헤더·목록 | 헤더 | 불릿 | 인사말과 맺음말 |",
        "doc_intro": ("### 문서\n\nsqlpipe 문서 과제 {tasks}개를 조건마다 {runs}번씩 썼습니다. 비율은 린터가 센 수를 어절 수로 나눈 값입니다. "
                      "린터는 정규식으로 세므로 순위로 읽지 말고 방향으로 읽으세요."),
        "doc_header": "| 조건 | 문서 수 | 100어절당 오류 | 100어절당 경고 | 100어절당 번역투 | 지정형 비율 | 쉬운 단어 비율 | 가장 긴 문장 |",
        "longest": "{n}어절",
        "not_measured": "측정 안 함",
        "results_link": "원본 출력, 표기 분포, 측정 조건은 [`{rel}/RESULTS.md`]({href})에 있습니다.",
        "labels": {"baseline": "스킬 없음", "reply_plain": "SimpleKorean", "plain": "기본 모드", "strict": "엄격 모드"},
        "example_before": "스킬 없이 쓴 문서",
        "example_after": "SimpleKorean을 켜고 쓴 문서",
        "example_files": "원본 파일은 왼쪽이 `{before}`, 오른쪽이 `{after}`입니다.",
        "example_docs": "답변 예시와 나머지 문서 예시는 [`examples/before-after.md`]({href})에 있습니다.",
        "block_size": "규칙 블록 {n}자",
    },
    "en": {
        "reply_intro": ("### Replies\n\nWe asked {questions} questions {runs} times in each condition. "
                        "Each question contains one technical term. There are {total} replies in total. "),
        "headline": ("With the skill on, reader-visible defects (em-dashes, bold text, tables, a header or list on the first line) fell by {cut} "
                     "(from {base} to {plain}). In a blind judgment of {n} pairs, the SimpleKorean reply won {wins}, "
                     "tied {ties}, and lost {losses}."),
        "reply_header": ("| Condition | Replies | Mean eojeol | Mean sentences | em-dash | Bold | Tables | First-line header or list | Headers | Bullets | "
                         "Greetings and sign-offs |"),
        "doc_intro": ("### Documents\n\nThe model wrote each of {tasks} sqlpipe documentation tasks {runs} times in each condition. "
                      "Each rate is the linter's count divided by the eojeol count. The linter is a regex check, "
                      "so read the numbers as a direction, not as a ranking."),
        "doc_header": ("| Condition | Documents | Errors per 100 eojeol | Warnings per 100 eojeol | "
                       "Translationese per 100 eojeol | Designated spelling rate | Easy word rate | Longest sentence |"),
        "longest": "{n} eojeol",
        "not_measured": "not measured",
        "results_link": ("The raw outputs, the spelling distribution, and the test conditions are in "
                         "[`{rel}/RESULTS.md`]({href})."),
        "labels": {"baseline": "No skill", "reply_plain": "SimpleKorean", "plain": "Default mode", "strict": "Strict mode"},
        "example_before": "Written without the skill",
        "example_after": "Written with SimpleKorean on",
        "example_files": "The raw files are `{before}` (left) and `{after}` (right).",
        "example_docs": "Reply examples and more document examples are in [`examples/before-after.md`]({href}).",
        "block_size": "rule block of {n} characters",
    },
    "ja": {
        "reply_intro": "### 回答\n\n専門用語を1つずつ含む質問{questions}個を、条件ごとに{runs}回ずつ尋ねました。回答は全部で{total}個です。",
        "headline": ("スキルを有効にすると、読者に見える欠陥（em-dash、太字、表、先頭行の見出しや箇条書き）が{cut}減りました"
                     "（{base}個から{plain}個）。ブラインド判定では、SimpleKorean の回答が{n}組のうち{wins}組で勝ち、"
                     "{ties}組で引き分け、{losses}組で負けました。"),
        "reply_header": "| 条件 | 回答数 | 平均語節数 | 平均文数 | em-dash | 太字 | 表 | 先頭行の見出し・箇条書き | 見出し | 箇条書き | 挨拶と結び |",
        "doc_intro": ("### 文書\n\nsqlpipe の文書課題{tasks}個を、条件ごとに{runs}回ずつ書きました。"
                      "比率は、リンターが数えた件数を語節数で割った値です。"
                      "リンターは正規表現による検査なので、順位ではなく傾向として読んでください。"),
        "doc_header": ("| 条件 | 文書数 | 100語節あたりのエラー | 100語節あたりの警告 | 100語節あたりの翻訳調 | "
                       "指定表記の比率 | やさしい語の比率 | 最長の文 |"),
        "longest": "{n}語節",
        "not_measured": "未測定",
        "results_link": "生の出力、表記の分布、測定条件は [`{rel}/RESULTS.md`]({href}) にあります。",
        "labels": {"baseline": "スキルなし", "reply_plain": "SimpleKorean", "plain": "基本モード", "strict": "厳格モード"},
        "example_before": "スキルなしで書いた文書",
        "example_after": "SimpleKorean を有効にして書いた文書",
        "example_files": "元のファイルは、左が `{before}`、右が `{after}` です。",
        "example_docs": "回答の例とほかの文書の例は [`examples/before-after.md`]({href}) にあります。",
        "block_size": "{n}文字のルールブロック",
    },
    "zh": {
        "reply_intro": "### 回答\n\n我们把 {questions} 个问题在每个条件下各问了 {runs} 次，每个问题含一个专业术语，共得到 {total} 个回答。",
        "headline": ("启用技能后，读者能看到的缺陷（em-dash、粗体、表格、第一行的标题或列表）减少了 {cut}（从 {base} 个降到 {plain} 个）。"
                     "在 {n} 组盲评中，SimpleKorean 的回答赢了 {wins} 组，平了 {ties} 组，输了 {losses} 组。"),
        "reply_header": "| 条件 | 回答数 | 平均语节数 | 平均句数 | em-dash | 粗体 | 表格 | 首行标题或列表 | 标题 | 列表符号 | 问候语和结束语 |",
        "doc_intro": ("### 文档\n\nsqlpipe 的 {tasks} 个文档任务在每个条件下各写了 {runs} 次。比率是检查器的计数除以语节数得到的值。"
                      "检查器使用正则表达式，所以请把数字当作方向，而不是排名。"),
        "doc_header": ("| 条件 | 文档数 | 每 100 语节错误 | 每 100 语节警告 | 每 100 语节翻译腔 | 规定写法比例 | "
                       "简单词比例 | 最长句子 |"),
        "longest": "{n} 个语节",
        "not_measured": "未测量",
        "results_link": "原始输出、写法分布和测量条件见 [`{rel}/RESULTS.md`]({href})。",
        "labels": {"baseline": "无技能", "reply_plain": "SimpleKorean", "plain": "基本模式", "strict": "严格模式"},
        "example_before": "未启用技能时写的文档",
        "example_after": "启用 SimpleKorean 后写的文档",
        "example_files": "左边的原始文件是 `{before}`，右边的是 `{after}`。",
        "example_docs": "回答示例和更多文档示例见 [`examples/before-after.md`]({href})。",
        "block_size": "{n} 个字符的规则块",
    },
    "es": {
        "reply_intro": ("### Respuestas\n\nHicimos {questions} preguntas {runs} veces en cada condición. "
                        "Cada pregunta contiene un término técnico. En total hay {total} respuestas. "),
        "headline": ("Con la skill activada, los defectos visibles para el lector (em-dash, negritas, tablas, encabezado o lista en la primera línea) "
                     "bajaron un {cut} (de {base} a {plain}). En una evaluación a ciegas de {n} pares, la respuesta de "
                     "SimpleKorean ganó {wins}, empató {ties} y perdió {losses}."),
        "reply_header": ("| Condición | Respuestas | Media de eojeol | Media de oraciones | em-dash | Negritas | Tablas | "
                         "Encabezado o lista en la primera línea | Encabezados | Viñetas | Saludos y despedidas |"),
        "doc_intro": ("### Documentos\n\nEl modelo escribió cada una de las {tasks} tareas de documentación de sqlpipe {runs} veces "
                      "en cada condición. Cada tasa es el recuento del linter dividido entre el número de eojeol. "
                      "El linter es una comprobación con expresiones regulares, así que lea las cifras como una dirección, "
                      "no como una clasificación."),
        "doc_header": ("| Condición | Documentos | Errores por 100 eojeol | Avisos por 100 eojeol | Calcos por 100 eojeol | "
                       "Tasa de grafía designada | Tasa de palabras fáciles | Oración más larga |"),
        "longest": "{n} eojeol",
        "not_measured": "no medido",
        "results_link": ("Las salidas originales, la distribución de grafías y las condiciones de medición están en "
                         "[`{rel}/RESULTS.md`]({href})."),
        "labels": {"baseline": "Sin skill", "reply_plain": "SimpleKorean", "plain": "Modo básico", "strict": "Modo estricto"},
        "example_before": "Escrito sin la skill",
        "example_after": "Escrito con SimpleKorean activado",
        "example_files": "Los archivos originales son `{before}` (izquierda) y `{after}` (derecha).",
        "example_docs": "Los ejemplos de respuestas y más ejemplos de documentos están en [`examples/before-after.md`]({href}).",
        "block_size": "bloque de reglas de {n} caracteres",
    },
}


def prefix(lang):
    """README에서 레포 루트까지의 상대 경로. 번역판은 docs/에 있다."""
    return "" if lang == "ko" else "../"


def link(lang, rel):
    """레포 기준 경로를 그 언어의 README에서 쓸 링크 대상으로 바꾼다."""
    return prefix(lang) + rel


def readme_link(src, dst):
    """src 언어의 README에서 dst 언어의 README로 가는 상대 링크. 번역판끼리는 같은 폴더에 있다."""
    if src == "ko":
        return README[dst]
    return "../" + README[dst] if dst == "ko" else README[dst].split("/")[-1]


def language_line(lang):
    """언어 선택 줄. 순서는 LANGS를 따르고, 현재 언어는 링크 없이 쓴다."""
    items = [NAMES[other] if other == lang else f'<a href="{readme_link(lang, other)}">{NAMES[other]}</a>'
             for other in LANGS]
    return '<p align="center">\n  ' + " | ".join(items) + "\n</p>"


def grouped(n, lang):
    """큰 정수를 그 언어의 관례대로 쓴다. es는 네 자리까지 묶지 않고, 다섯 자리부터 줄바꿈 없는 공백으로 묶는다(RAE)."""
    if lang != "es":
        return f"{n:,}"
    return str(n) if abs(n) < 10000 else f"{n:,}".replace(",", NBSP)


def percent(number, lang):
    """숫자에 퍼센트 기호를 붙인다. es는 기호 앞에 줄바꿈 없는 공백을 둔다(RAE)."""
    return f"{number}{NBSP}%" if lang == "es" else f"{number}%"
