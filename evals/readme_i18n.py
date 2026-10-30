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
        "reply_intro_marked": ("### 답변\n\n전문용어가 하나씩 든 질문 {questions}개를 조건마다 {runs}번씩 물었습니다. "
                               "질문마다 em-dash와 가운뎃점(·)을 하나씩 넣었습니다. "
                               "가운뎃점은 답변 규칙이 막지 않으므로 결함에 넣지 않고 따로 셌습니다. 답변은 모두 {total}개입니다. "),
        "headline": ("스킬을 켜면 화면에 드러나는 결함(em-dash, 굵은 글씨, 표, 첫 줄의 헤더나 목록)이 {cut} 줄었습니다({base}개에서 {plain}개). "
                     "블라인드 판정에서 SimpleKorean 답변은 {n}쌍 가운데 {wins}쌍에서 이겼고, "
                     "{ties}쌍에서 비겼고, {losses}쌍에서 졌습니다."),
        "reply_no_dash": (" 질문에 em-dash가 있어도 스킬 없는 답변은 em-dash를 쓰지 않았습니다. "
                          "그래서 em-dash를 지우는지는 아래 문서의 다듬기 과제로 봅니다."),
        "reply_header": "| 조건 | 답변 수 | 평균 어절 | 평균 문장 | em-dash | 굵은 글씨 | 표 | 첫 줄 헤더·목록 | 가운뎃점 | 헤더 | 불릿 | 인사말과 맺음말 |",
        "doc_intro": ("### 문서\n\nsqlpipe 문서 과제 {tasks}개를 조건마다 {runs}번씩 썼습니다. 비율은 린터가 센 수를 어절 수로 나눈 값입니다. "
                      "린터는 정규식으로 세므로 순위로 읽지 말고 방향으로 읽으세요."),
        "doc_header": "| 조건 | 문서 수 | 100어절당 오류 | 100어절당 경고 | 100어절당 번역투 | 지정형 비율 | 쉬운 단어 비율 | 가장 긴 문장 |",
        "polish_intro": ("em-dash, 굵은 글씨, 가운뎃점을 일부러 넣은 초안을 다듬는 과제는 위 표에 넣지 않고 따로 셉니다. "
                         "초안에는 em-dash {dash}개, 굵은 글씨 {bold}개, 가운뎃점 {dot}개가 있습니다. "
                         "아래 표는 조건마다 다듬은 문서에 든 수를 더한 값입니다. "
                         "조건마다 {runs}번 다듬었으므로, 초안의 표시가 모두 남으면 em-dash {dash_all}개, 굵은 글씨 {bold_all}개, "
                         "가운뎃점 {dot_all}개입니다. 가운뎃점은 문서 규칙도 막지 않으므로 참고로 셉니다. "
                         "초안은 [`{src}`]({href})의 `polish` 과제에 있습니다."),
        "polish_header": "| 조건 | 문서 수 | em-dash | 굵은 글씨 | 가운뎃점 |",
        "longest": "{n}어절",
        "not_measured": "측정 안 함",
        "results_link": "원본 출력, 표기 분포, 측정 조건은 [`{rel}/RESULTS.md`]({href})에 있습니다.",
        "labels": {"baseline": "스킬 없음", "reply_plain": "SimpleKorean", "plain": "기본 모드", "strict": "엄격 모드"},
        "example_draft_head": "초안",
        "example_before": "스킬 없이 다듬은 문서",
        "example_after": "SimpleKorean을 켜고 다듬은 문서",
        "example_draft": "초안은 [`{src}`]({href})의 `{id}` 과제에 있습니다.",
        "example_files": "다듬은 문서의 원본 파일은 가운데가 `{before}`, 오른쪽이 `{after}`입니다.",
        "example_docs": "답변 예시와 나머지 문서 예시는 [`examples/before-after.md`]({href})에 있습니다. 예시마다 바뀐 곳은 [이 커밋의 diff]({diff})에서 볼 수 있습니다.",
        "block_size": "규칙 블록 {n}자",
    },
    "en": {
        "reply_intro": ("### Replies\n\nWe asked {questions} questions {runs} times in each condition. "
                        "Each question contains one technical term. There are {total} replies in total. "),
        "reply_intro_marked": ("### Replies\n\nWe asked {questions} questions {runs} times in each condition. "
                               "Each question contains one technical term, one em-dash, and one middle dot (·). "
                               "The reply rules do not ban the middle dot, so we counted it separately and left it out of the defects. "
                               "There are {total} replies in total. "),
        "headline": ("With the skill on, reader-visible defects (em-dashes, bold text, tables, a header or list on the first line) fell by {cut} "
                     "(from {base} to {plain}). In a blind judgment of {n} pairs, the SimpleKorean reply won {wins}, "
                     "tied {ties}, and lost {losses}."),
        "reply_no_dash": (" Even with an em-dash in every question, the replies without the skill used no em-dashes. "
                          "So the polishing task in the documents section below tests whether the skill removes them."),
        "reply_header": ("| Condition | Replies | Mean eojeol | Mean sentences | em-dash | Bold | Tables | First-line header or list | Middle dot | "
                         "Headers | Bullets | Greetings and sign-offs |"),
        "doc_intro": ("### Documents\n\nThe model wrote each of {tasks} sqlpipe documentation tasks {runs} times in each condition. "
                      "Each rate is the linter's count divided by the eojeol count. The linter is a regex check, "
                      "so read the numbers as a direction, not as a ranking."),
        "doc_header": ("| Condition | Documents | Errors per 100 eojeol | Warnings per 100 eojeol | "
                       "Translationese per 100 eojeol | Designated spelling rate | Easy word rate | Longest sentence |"),
        "polish_intro": ("The task of polishing a draft with deliberately added em-dashes, bold text, and middle dots "
                         "is counted separately, not in the table above. "
                         "The draft has these marks: em-dash {dash}, bold {bold}, middle dot {dot}. "
                         "The table below sums these marks in the polished documents of each condition. "
                         "Each condition polished the draft {runs} times, so if every mark stayed, the sums would be "
                         "em-dash {dash_all}, bold {bold_all}, and middle dot {dot_all}. "
                         "The document rules do not ban the middle dot either, so we count it for reference only. "
                         "The draft is the `polish` task in [`{src}`]({href})."),
        "polish_header": "| Condition | Documents | em-dash | Bold | Middle dot |",
        "longest": "{n} eojeol",
        "not_measured": "not measured",
        "results_link": ("The raw outputs, the spelling distribution, and the test conditions are in "
                         "[`{rel}/RESULTS.md`]({href})."),
        "labels": {"baseline": "No skill", "reply_plain": "SimpleKorean", "plain": "Default mode", "strict": "Strict mode"},
        "example_draft_head": "Draft",
        "example_before": "Polished without the skill",
        "example_after": "Polished with SimpleKorean on",
        "example_draft": "The draft is the `{id}` task in [`{src}`]({href}).",
        "example_files": "The raw files of the polished documents are `{before}` (middle) and `{after}` (right).",
        "example_docs": "Reply examples and more document examples are in [`examples/before-after.md`]({href}). [This commit's diff]({diff}) shows what changed in each example.",
        "block_size": "rule block of {n} characters",
    },
    "ja": {
        "reply_intro": "### 回答\n\n専門用語を1つずつ含む質問{questions}個を、条件ごとに{runs}回ずつ尋ねました。回答は全部で{total}個です。",
        "reply_intro_marked": ("### 回答\n\n専門用語を1つずつ含む質問{questions}個を、条件ごとに{runs}回ずつ尋ねました。"
                               "どの質問にも em-dash と中点（·）を1つずつ入れました。中点は回答ルールで禁止していないため、欠陥には含めず別に数えました。"
                               "回答は全部で{total}個です。"),
        "headline": ("スキルを有効にすると、読者に見える欠陥（em-dash、太字、表、先頭行の見出しや箇条書き）が{cut}減りました"
                     "（{base}個から{plain}個）。ブラインド判定では、SimpleKorean の回答が{n}組のうち{wins}組で勝ち、"
                     "{ties}組で引き分け、{losses}組で負けました。"),
        "reply_no_dash": ("質問に em-dash があっても、スキルなしの回答は em-dash を使いませんでした。"
                          "そのため、em-dash を取り除くかどうかは、下の文書の下書きを整える課題で確かめます。"),
        "reply_header": "| 条件 | 回答数 | 平均語節数 | 平均文数 | em-dash | 太字 | 表 | 先頭行の見出し・箇条書き | 中点 | 見出し | 箇条書き | 挨拶と結び |",
        "doc_intro": ("### 文書\n\nsqlpipe の文書課題{tasks}個を、条件ごとに{runs}回ずつ書きました。"
                      "比率は、リンターが数えた件数を語節数で割った値です。"
                      "リンターは正規表現による検査なので、順位ではなく傾向として読んでください。"),
        "doc_header": ("| 条件 | 文書数 | 100語節あたりのエラー | 100語節あたりの警告 | 100語節あたりの翻訳調 | "
                       "指定表記の比率 | やさしい語の比率 | 最長の文 |"),
        "polish_intro": ("em-dash、太字、中点をわざと入れた下書きを整える課題は、上の表に含めず別に数えます。"
                         "下書きには em-dash が{dash}個、太字が{bold}か所、中点が{dot}個あります。"
                         "下の表は、条件ごとに整えた文書に含まれる数の合計です。"
                         "条件ごとに{runs}回整えたので、下書きの印がすべて残れば em-dash {dash_all}個、太字 {bold_all}か所、"
                         "中点 {dot_all}個になります。中点は文書ルールでも禁止していないため、参考として数えます。"
                         "下書きは [`{src}`]({href}) の `polish` 課題にあります。"),
        "polish_header": "| 条件 | 文書数 | em-dash | 太字 | 中点 |",
        "longest": "{n}語節",
        "not_measured": "未測定",
        "results_link": "生の出力、表記の分布、測定条件は [`{rel}/RESULTS.md`]({href}) にあります。",
        "labels": {"baseline": "スキルなし", "reply_plain": "SimpleKorean", "plain": "基本モード", "strict": "厳格モード"},
        "example_draft_head": "下書き",
        "example_before": "スキルなしで整えた文書",
        "example_after": "SimpleKorean を有効にして整えた文書",
        "example_draft": "下書きは [`{src}`]({href}) の `{id}` 課題にあります。",
        "example_files": "整えた文書の元のファイルは、中央が `{before}`、右が `{after}` です。",
        "example_docs": "回答の例とほかの文書の例は [`examples/before-after.md`]({href}) にあります。例ごとの変更点は[このコミットの diff]({diff})で確認できます。",
        "block_size": "{n}文字のルールブロック",
    },
    "zh": {
        "reply_intro": "### 回答\n\n我们把 {questions} 个问题在每个条件下各问了 {runs} 次，每个问题含一个专业术语，共得到 {total} 个回答。",
        "reply_intro_marked": ("### 回答\n\n我们把 {questions} 个问题在每个条件下各问了 {runs} 次，每个问题含一个专业术语、一个 em-dash 和一个间隔号（·）。"
                               "回答规则不禁止间隔号，所以没有把它算作缺陷，而是单独统计。共得到 {total} 个回答。"),
        "headline": ("启用技能后，读者能看到的缺陷（em-dash、粗体、表格、第一行的标题或列表）减少了 {cut}（从 {base} 个降到 {plain} 个）。"
                     "在 {n} 组盲评中，SimpleKorean 的回答赢了 {wins} 组，平了 {ties} 组，输了 {losses} 组。"),
        "reply_no_dash": "即使问题里有 em-dash，未启用技能的回答也没有使用 em-dash。所以技能能否去掉 em-dash，要看下面文档部分的草稿润色任务。",
        "reply_header": "| 条件 | 回答数 | 平均语节数 | 平均句数 | em-dash | 粗体 | 表格 | 首行标题或列表 | 间隔号 | 标题 | 列表符号 | 问候语和结束语 |",
        "doc_intro": ("### 文档\n\nsqlpipe 的 {tasks} 个文档任务在每个条件下各写了 {runs} 次。比率是检查器的计数除以语节数得到的值。"
                      "检查器使用正则表达式，所以请把数字当作方向，而不是排名。"),
        "doc_header": ("| 条件 | 文档数 | 每 100 语节错误 | 每 100 语节警告 | 每 100 语节翻译腔 | 规定写法比例 | "
                       "简单词比例 | 最长句子 |"),
        "polish_intro": ("润色一份故意放入 em-dash、粗体和间隔号的草稿的任务不计入上表，而是单独统计。"
                         "草稿里有 {dash} 个 em-dash、{bold} 处粗体和 {dot} 个间隔号。"
                         "下表是每个条件下润色后的文档中这些标记的总数。"
                         "每个条件润色了 {runs} 次，所以如果草稿的标记全部保留，总数会是 {dash_all} 个 em-dash、{bold_all} 处粗体和 "
                         "{dot_all} 个间隔号。文档规则也不禁止间隔号，所以只作参考统计。"
                         "草稿见 [`{src}`]({href}) 中的 `polish` 任务。"),
        "polish_header": "| 条件 | 文档数 | em-dash | 粗体 | 间隔号 |",
        "longest": "{n} 个语节",
        "not_measured": "未测量",
        "results_link": "原始输出、写法分布和测量条件见 [`{rel}/RESULTS.md`]({href})。",
        "labels": {"baseline": "无技能", "reply_plain": "SimpleKorean", "plain": "基本模式", "strict": "严格模式"},
        "example_draft_head": "草稿",
        "example_before": "未启用技能时润色的文档",
        "example_after": "启用 SimpleKorean 后润色的文档",
        "example_draft": "草稿见 [`{src}`]({href}) 中的 `{id}` 任务。",
        "example_files": "润色后文档的原始文件：中间是 `{before}`，右边是 `{after}`。",
        "example_docs": "回答示例和更多文档示例见 [`examples/before-after.md`]({href})。每个示例的改动见[此提交的 diff]({diff})。",
        "block_size": "{n} 个字符的规则块",
    },
    "es": {
        "reply_intro": ("### Respuestas\n\nHicimos {questions} preguntas {runs} veces en cada condición. "
                        "Cada pregunta contiene un término técnico. En total hay {total} respuestas. "),
        "reply_intro_marked": ("### Respuestas\n\nHicimos {questions} preguntas {runs} veces en cada condición. "
                               "Cada pregunta contiene un término técnico, un em-dash y un punto medio (·). "
                               "Las reglas de respuesta no prohíben el punto medio, así que lo contamos aparte y no lo sumamos a los defectos. "
                               "En total hay {total} respuestas. "),
        "headline": ("Con la skill activada, los defectos visibles para el lector (em-dash, negritas, tablas, encabezado o lista en la primera línea) "
                     "bajaron un {cut} (de {base} a {plain}). En una evaluación a ciegas de {n} pares, la respuesta de "
                     "SimpleKorean ganó {wins}, empató {ties} y perdió {losses}."),
        "reply_no_dash": (" Aunque cada pregunta tenía un em-dash, las respuestas sin la skill no usaron ninguno. "
                          "Por eso, la tarea de pulido de la sección de documentos comprueba si la skill los quita."),
        "reply_header": ("| Condición | Respuestas | Media de eojeol | Media de oraciones | em-dash | Negritas | Tablas | "
                         "Encabezado o lista en la primera línea | Punto medio | Encabezados | Viñetas | Saludos y despedidas |"),
        "doc_intro": ("### Documentos\n\nEl modelo escribió cada una de las {tasks} tareas de documentación de sqlpipe {runs} veces "
                      "en cada condición. Cada tasa es el recuento del linter dividido entre el número de eojeol. "
                      "El linter es una comprobación con expresiones regulares, así que lea las cifras como una dirección, "
                      "no como una clasificación."),
        "doc_header": ("| Condición | Documentos | Errores por 100 eojeol | Avisos por 100 eojeol | Calcos por 100 eojeol | "
                       "Tasa de grafía designada | Tasa de palabras fáciles | Oración más larga |"),
        "polish_intro": ("La tarea de pulir un borrador con em-dash, negritas y puntos medios puestos a propósito "
                         "no está en la tabla anterior y se cuenta aparte. "
                         "El borrador tiene estas marcas: em-dash {dash}, negritas {bold}, punto medio {dot}. "
                         "La tabla siguiente suma estas marcas en los documentos pulidos de cada condición. "
                         "Cada condición pulió el borrador {runs} veces, así que si quedaran todas las marcas, las sumas serían "
                         "em-dash {dash_all}, negritas {bold_all} y punto medio {dot_all}. "
                         "Las reglas de documentos tampoco prohíben el punto medio, así que solo lo contamos como referencia. "
                         "El borrador es la tarea `polish` de [`{src}`]({href})."),
        "polish_header": "| Condición | Documentos | em-dash | Negritas | Punto medio |",
        "longest": "{n} eojeol",
        "not_measured": "no medido",
        "results_link": ("Las salidas originales, la distribución de grafías y las condiciones de medición están en "
                         "[`{rel}/RESULTS.md`]({href})."),
        "labels": {"baseline": "Sin skill", "reply_plain": "SimpleKorean", "plain": "Modo básico", "strict": "Modo estricto"},
        "example_draft_head": "Borrador",
        "example_before": "Pulido sin la skill",
        "example_after": "Pulido con SimpleKorean activado",
        "example_draft": "El borrador es la tarea `{id}` de [`{src}`]({href}).",
        "example_files": "Los archivos originales de los documentos pulidos son `{before}` (centro) y `{after}` (derecha).",
        "example_docs": "Los ejemplos de respuestas y más ejemplos de documentos están en [`examples/before-after.md`]({href}). Los cambios de cada ejemplo se ven en el [diff de este commit]({diff}).",
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
