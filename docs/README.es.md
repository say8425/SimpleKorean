<p align="center">
  Hace que los documentos técnicos en coreano escritos por IA se lean como un manual de mantenimiento.
</p>

<p align="center">
  <a href="../README.md">한국어</a> | <a href="README.en.md">English</a> | <a href="README.ja.md">日本語</a> | <a href="README.zh.md">中文</a> | Español
</p>

<p align="center">
  <a href="https://agentskills.io"><img src="https://img.shields.io/badge/SKILL.md-open_standard-blue?style=flat" alt="Agent Skills"></a>
  <a href="https://github.com/say8425/SimpleKorean/releases/latest"><img src="https://img.shields.io/github/v/release/say8425/SimpleKorean?label=version&style=flat" alt="version"></a>
  <a href="../LICENSE"><img src="https://img.shields.io/badge/license-MIT-lightgrey?style=flat" alt="MIT"></a>
</p>

SimpleKorean es una skill de agente que hace que los LLM escriban en un coreano sencillo en documentos técnicos y respuestas de chat. Los manuales de mantenimiento aeronáutico usan un inglés controlado llamado ASD-STE100. Tomamos sus reglas de [SimpleEnglish](https://github.com/AminBlg/SimpleEnglish) y las reconstruimos para la gramática coreana. También añadimos una lista de grafías de préstamos. La elaboramos contando las grafías que se usan en documentos reales de desarrollo escritos en coreano.

La skill funciona en los agentes que leen el [estándar Agent Skills](https://agentskills.io). Algunos ejemplos son Claude Code, Cursor, Codex, Gemini CLI y OpenCode.

## Hacer que un agente lo siga sin instalar

Puede dar a un agente solo la dirección de este repositorio y pedirle que lo siga. Esta sección es la instrucción que el agente lee en ese caso.

Siga esta sección cuando un usuario le pida escribir según las reglas de este repositorio sin instalarlo. Las tablas de reglas de este README son resúmenes. Las reglas completas están en `https://raw.githubusercontent.com/say8425/SimpleKorean/main/skills/simple-korean/SKILL.md`.

Si tiene una shell y Node.js, informe al usuario del comando siguiente. Después, ejecútelo. El comando imprime todo `SKILL.md`. También indica el directorio donde descargó los archivos de referencia.

```bash
npx skills use say8425/SimpleKorean@simple-korean
```

Si el comando falla o no puede usar una shell, lea `SKILL.md` hasta el final desde la URL raw de arriba (una URL que devuelve solo el texto del archivo). Si su herramienta de descarga resume el contenido, pídale el texto original. Si tiene `curl`, use `curl`.

En `SKILL.md`, lea las rutas que empiezan por `references/` desde el directorio de `SKILL.md`. Por ejemplo, `references/strict-mode.md` es `https://raw.githubusercontent.com/say8425/SimpleKorean/main/skills/simple-korean/references/strict-mode.md`. La lista completa de palabras está en `https://raw.githubusercontent.com/say8425/SimpleKorean/main/data/terms.json`. Use URL raw, no las URL `blob` de GitHub. Una URL `blob` devuelve una página HTML en lugar del texto original.

Sin instalación, los hooks (scripts que el agente ejecuta automáticamente en momentos fijos) no se ejecutan. Por eso debe hacer usted mismo su trabajo:

- Si el agente resume una conversación larga para acortarla, vuelva a leer `SKILL.md`.
- Antes de enviar una respuesta o un documento, haga la autorrevisión de `SKILL.md` (la sección "내기 전 자가 점검").
- Si tiene una shell, git y Python 3.9 o posterior, revise lo que escribió con el linter (un script que cuenta las infracciones de las reglas).

Si `/tmp/SimpleKorean` no existe, descargue primero el repositorio:

```bash
git clone --depth 1 https://github.com/say8425/SimpleKorean.git /tmp/SimpleKorean
```

Revise un documento con el primer comando y una respuesta con el segundo. En un documento con procedimientos, añada `--type procedural` al primer comando:

```bash
python3 /tmp/SimpleKorean/evals/ko_lint.py doc.md
python3 /tmp/SimpleKorean/evals/ko_lint.py --type reply - < reply.txt
```

El linter imprime el número de infracciones en JSON. En un documento, `errors_total` y `warnings_total` deben ser 0. En una respuesta, `visible_total` debe ser 0.

## Instalación

### Claude Code

En Claude Code, instálela como plugin.

```bash
claude plugin marketplace add say8425/SimpleKorean
claude plugin install simple-korean@simple-korean
```

El plugin incluye las cinco partes de abajo. La skill y los tres hooks funcionan automáticamente en las sesiones nuevas que inicie después de instalar el plugin. El estilo de salida solo funciona si usted lo aplica. El bloque de reglas que añaden el hook de inicio de sesión y el estilo de salida es una versión resumida de las reglas de la skill.

| Parte | Qué hace | Activación | Necesita |
|---|---|---|---|
| Skill | Contiene todas las reglas, el modo estricto y el modo de revisión. El modelo la lee cuando la necesita. | Automática | Nada |
| Hook de inicio de sesión | Añade el bloque de reglas a cada sesión. El modelo sigue las reglas aunque usted no nombre la skill. | Automática | Node.js |
| Hook de revisión de archivos | Revisa los archivos Markdown que el modelo escribe o edita. Avisa al modelo de las infracciones. | Automática | Python 3.9 o posterior |
| Hook de revisión de respuestas | Revisa la última respuesta del modelo. Muestra las infracciones en pantalla. | Automática | Python 3.9 o posterior |
| Estilo de salida | Pone en el prompt del sistema el mismo bloque de reglas que el hook de inicio de sesión. | Opcional | Nada |

Las reglas se aplican sin el estilo de salida, porque el hook de inicio de sesión ya añade el mismo bloque de reglas. Si el hook de inicio de sesión no se ejecuta porque falta Node.js, aplique el estilo de salida. Para aplicarlo, elíjalo en Output style de `/config`. O bien, añada `{"outputStyle": "simple-korean:simple-korean"}` a `~/.claude/settings.json`.

El hook de inicio de sesión añade un bloque de reglas de 2476 caracteres en cada sesión. Los detalles están en [`src/hooks/README.md`](../src/hooks/README.md).

### Codex

En Codex, instálela como plugin. El hook de inicio de sesión se instala con ella. Este hook necesita Node.js.

```bash
codex plugin marketplace add say8425/SimpleKorean
codex plugin add simple-korean@simple-korean
```

Antes de ejecutar un hook por primera vez, Codex pregunta si usted confía en él. Los detalles están en [`src/hooks/README.md`](../src/hooks/README.md).

### Otros agentes

En otros agentes, instale la skill con [skills CLI](https://github.com/vercel-labs/skills).

```bash
pnpm dlx skills add say8425/SimpleKorean
```

Si usa npm, ejecute `npx skills add say8425/SimpleKorean`. Este comando solo instala la skill. No instala los hooks ni el estilo de salida que se describen más arriba.

Para usar la skill una sola vez sin instalarla, ejecute `npx skills use say8425/SimpleKorean@simple-korean`. Este comando imprime un prompt que contiene la skill. Añada `--agent claude-code` para ejecutar Claude Code con ese prompt.

### Herramientas sin soporte de skills

En las herramientas que no admiten skills, pegue el bloque de reglas de [`prompts/system-prompt.md`](../prompts/system-prompt.md). Puede ponerlo en el prompt del sistema, en `AGENTS.md` o en `.cursorrules`. Al final de `prompts/system-prompt.md` también hay una versión corta de unos 120 tokens.

### Bots y programas

Ponga una variante de respuesta en el prompt del sistema de un bot. Las variantes de respuesta dividen en dos archivos las reglas de respuesta del bloque de reglas. [`prompts/sentence-rules.ko.md`](../prompts/sentence-rules.ko.md) contiene las reglas de oraciones. También contiene la regla de quitar palabras vacías (slop) y calcos de traducción. [`prompts/format-rules.ko.md`](../prompts/format-rules.ko.md) contiene las reglas de formato, como encabezados, negrita y tablas. Los dos archivos juntos forman las reglas completas de respuesta.

Aparte de la regla sobre palabras vacías y calcos de traducción, las variantes de respuesta no contienen las reglas de documentos. Los archivos cuyo nombre termina en `.en.md` tienen las mismas reglas, escritas en inglés. La primera línea de cada archivo es un comentario HTML con la variante, el idioma y la versión.

Para fijar una variante, descárguela de la URL raw de una etiqueta de versión, por ejemplo `https://raw.githubusercontent.com/say8425/SimpleKorean/<etiqueta>/prompts/sentence-rules.ko.md`. Los archivos de variantes tienen la misma ruta en todas las etiquetas.

En Python, instale el paquete. El paquete usa solo la biblioteca estándar. Cambie `<etiqueta>` por una etiqueta de versión:

```bash
pip install "git+https://github.com/say8425/SimpleKorean@<etiqueta>"
```

```python
from simple_korean import __version__, prompt_block

prompt = prompt_block(variant="sentences", lang="en")
```

`variant` es `sentences` o `format`. `lang` es el idioma en que están escritas las reglas, `ko` o `en`. `lang` no fija el idioma de la respuesta.

### Después de instalar

Después de instalarla, pida un documento técnico. Para corregir un texto que ya existe, diga "simple-korean으로 고쳐 줘" (corríjalo con simple-korean).

## Ejemplo

Estos son dos documentos en los que el mismo modelo pulió el mismo borrador: una sección de solución de problemas de una herramienta CLI. Pusimos a propósito em-dash, negritas y puntos medios en el borrador. La primera columna de la tabla es el borrador. La segunda se pulió sin la skill y la tercera, con el modo básico de SimpleKorean activado. Copiamos los tres textos sin cambios. Están en coreano, porque esta skill hace que el modelo escriba en coreano.

<!-- example:start -->
<table>
<tr>
<th width="34%">Borrador</th>
<th width="33%">Pulido sin la skill</th>
<th width="33%">Pulido con SimpleKorean activado</th>
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

Los archivos originales de los documentos pulidos son `evals/results/2026-10-21/docs/baseline__polish__r1.json` (centro) y `evals/results/2026-10-21/docs/plain__polish__r1.json` (derecha).

El borrador es la tarea `polish` de [`evals/results/2026-10-21/inputs/scenarios.json`](../evals/results/2026-10-21/inputs/scenarios.json).

Los ejemplos de respuestas y más ejemplos de documentos están en [`examples/before-after.md`](../examples/before-after.md).
<!-- example:end -->

## Benchmark

Volvimos a calcular todas las cifras de abajo a partir de las salidas originales guardadas en los commits. En cada push, la CI las compara con `evals/check_numbers.py`. `claude-sonnet-5-5` (effort low) escribió los documentos y las respuestas, y `claude-opus-5-5` hizo la evaluación. Ninguna ejecución leyó la configuración del usuario, servidores MCP ni archivos de instrucciones como AGENTS.md. El modelo evaluador también es Claude, así que puede tener un sesgo a favor de su misma familia de modelos. Un eojeol es una unidad del coreano separada por espacios.

<!-- benchmark:start evals/results/2026-10-21 -->
### Respuestas

Hicimos 8 preguntas 2 veces en cada condición. Cada pregunta contiene un término técnico, un em-dash y un punto medio (·). Las reglas de respuesta no prohíben el punto medio, así que lo contamos aparte y no lo sumamos a los defectos. En total hay 32 respuestas. Con la skill activada, los defectos visibles para el lector (em-dash, negritas, tablas, encabezado o lista en la primera línea) bajaron un 100 % (de 162 a 0). En una evaluación a ciegas de 16 pares, la respuesta de SimpleKorean ganó 12, empató 3 y perdió 1. Aunque cada pregunta tenía un em-dash, las respuestas sin la skill no usaron ninguno. Por eso, la tarea de pulido de la sección de documentos comprueba si la skill los quita.

| Condición | Respuestas | Media de eojeol | Media de oraciones | em-dash | Negritas | Tablas | Encabezado o lista en la primera línea | Punto medio | Encabezados | Viñetas | Saludos y despedidas |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Sin skill | 16 | 266 | 31.2 | 0 | 155 | 3 | 4 | 26 | 36 | 211 | 13 |
| SimpleKorean | 16 | 223 | 31.0 | 0 | 0 | 0 | 0 | 2 | 54 | 173 | 5 |

### Documentos

El modelo escribió cada una de las 8 tareas de documentación de sqlpipe 2 veces en cada condición. Cada tasa es el recuento del linter dividido entre el número de eojeol. El linter es una comprobación con expresiones regulares, así que lea las cifras como una dirección, no como una clasificación.

| Condición | Documentos | Errores por 100 eojeol | Avisos por 100 eojeol | Calcos por 100 eojeol | Tasa de grafía designada | Tasa de palabras fáciles | Oración más larga |
|---|---:|---:|---:|---:|---:|---:|---:|
| Sin skill | 16 | 0.14 | 0.71 | 0.42 | 100.0 % | 41.9 % | 18 eojeol |
| Modo básico | 16 | 0.00 | 0.17 | 0.17 | 100.0 % | 45.3 % | 15 eojeol |
| Modo estricto | 16 | 0.00 | 0.00 | 0.00 | 100.0 % | 39.6 % | 13 eojeol |

La tarea de pulir un borrador con em-dash, negritas y puntos medios puestos a propósito no está en la tabla anterior y se cuenta aparte. El borrador tiene estas marcas: em-dash 2, negritas 2, punto medio 3. La tabla siguiente suma estas marcas en los documentos pulidos de cada condición. Cada condición pulió el borrador 2 veces, así que si quedaran todas las marcas, las sumas serían em-dash 4, negritas 4 y punto medio 6. Las reglas de documentos tampoco prohíben el punto medio, así que solo lo contamos como referencia. El borrador es la tarea `polish` de [`evals/results/2026-10-21/inputs/scenarios.json`](../evals/results/2026-10-21/inputs/scenarios.json).

| Condición | Documentos | em-dash | Negritas | Punto medio |
|---|---:|---:|---:|---:|
| Sin skill | 2 | 4 | 4 | 1 |
| Modo básico | 2 | 0 | 0 | 0 |
| Modo estricto | 2 | 0 | 0 | 0 |

Las salidas originales, la distribución de grafías y las condiciones de medición están en [`evals/results/2026-10-21/RESULTS.md`](../evals/results/2026-10-21/RESULTS.md).
<!-- benchmark:end -->

## Reglas

Las reglas están en [`SKILL.md`](../skills/simple-korean/SKILL.md). La lista completa de reglas que usan el modo de revisión y el modo estricto está en [`rule-catalog.md`](../skills/simple-korean/references/rule-catalog.md). Las reglas del modo básico tienen un número K, como K1.1. Las reglas del modo estricto tienen un número S, como S1.

### Reglas para respuestas

Las respuestas de chat usan estas reglas en todos los modos.

| Regla | Lo que evita |
|---|---|
| Use encabezados y listas cuando el contenido y la extensión de la respuesta lo pidan. No use negritas ni tablas | Formato alrededor de una respuesta de una sola línea |
| Escriba la respuesta en la primera oración | Una introducción que repite la pregunta |
| No use em-dash | Ideas unidas solo a medias |
| Explique brevemente un término conceptual la primera vez que lo use | Términos que el lector tiene que buscar |
| Use un solo estilo en cada respuesta. No use saludos ni despedidas | "좋은 질문입니다" (Buena pregunta), "도움이 되셨기를 바랍니다" (Espero que le haya servido) |

### Reglas para documentos

Los documentos usan estas reglas. Aquí entran los README, los runbooks, los mensajes de error, las notas de versión y los informes de incidentes.

| Regla | Lo que evita |
|---|---|
| Escriba los procedimientos en 15 eojeol o menos y las explicaciones en 20 eojeol o menos | Oraciones largas que no terminan nunca |
| Ponga las condiciones con "-면" (si) antes de la orden | "단, ~경우" (pero, en caso de ~) después de la orden, que se lee demasiado tarde |
| Use la voz activa y tiempos simples | "되어지다" (doble pasiva), "~에 의해" (por ~), "-고 있습니다" (está haciendo) |
| No use terminaciones de suposición ni de recomendación | "-ㄹ 수도 있습니다" (puede que), "-것 같습니다" (parece que), "-하는 것이 좋습니다" (es mejor ~) |
| Dé un solo significado a cada palabra | Alternar "확인" (confirmación), "검증" (verificación), "점검" (inspección) y "체크" (chequeo) |
| No omita partículas ni termine con una forma nominal | Estilo telegráfico como "백업 확인 필요" (comprobación de copia de seguridad necesaria) |
| Escriba hechos, no importancia | "강력한" (potente), "원활한" (fluido), "단순히 X가 아니라 Y" (no solo X, sino Y) |
| Use la grafía designada de los préstamos | "디렉토리" y "디렉터리" (directorio) mezclados en un mismo documento |

## Modos

### Modo básico

El modo básico son todas las reglas de arriba. No hace falta activarlo.

### Modo estricto

El modo estricto se activa cuando usted dice "엄격 모드" (modo estricto), "통제 언어" (lenguaje controlado), "KS A 0001", "STE" o "ASD-STE100". El modo estricto limita los finales de oración de los documentos a cinco formas. La obligación es "-해야 합니다" (debe). La prohibición es "-하면 안 됩니다" (no debe). El permiso es "-해도 됩니다" (puede). La capacidad es "-ㄹ 수 있습니다" (es capaz de). Los hechos van en presente. El modo estricto no usa el conectivo "(이)나" (o) y escribe las condiciones solo con "-면" (si). La base son los anexos H e I de KS A 0001:2023. En modo estricto, las respuestas siguen igualmente las reglas del modo básico.

### Modo de revisión

El modo de revisión se activa cuando usted pide una revisión en lugar de un texto. Para cada infracción, indica el número K, el fragmento afectado y la oración corregida.

## Política de grafía

Los préstamos siguen las normas de transcripción de préstamos del coreano y los ejemplos de uso del Instituto Nacional de la Lengua Coreana (디렉터리 directorio, 메시지 mensaje, 애플리케이션 aplicación). Cuando esos principios no dan una respuesta, decide la lista de [`data/terms.json`](../data/terms.json). Hicimos esta lista contando las grafías reales en documentos localizados, documentación de proveedores, blogs técnicos de empresas y archivos README de GitHub. La evidencia está en [`docs/research/loanword-spelling-usage.md`](../docs/research/loanword-spelling-usage.md).

| Grupo | Forma que se usa |
|---|---|
| 23 palabras que se usan según la norma | Forma normativa (메시지 mensaje, 애플리케이션 aplicación, 메서드 método, 라이선스 licencia) |
| 4 palabras que varían según la fuente | Forma normativa (디렉터리 directorio, 릴리스 release, 셸 shell, 리디렉션 redirección) |
| 4 palabras con una forma habitual ya fijada | 레포지토리 (repositorio), 바디 (cuerpo), 칼럼 (columna), 대상 (destino) |
| 2 palabras sin grafía oficial | 리디렉션 (redirect), 리팩터링 (refactorización) |
| 5 palabras en las que se elige entre un préstamo y una palabra coreana | 오류 (error), 매개변수 (parámetro), 사용자 (usuario), 기본값 (valor predeterminado), 배포 (despliegue) |
| 4 casos de espaciado | 기본값, 매개변수, 반환값, 오픈소스 (se escriben sin espacios) |

Los nombres de productos, las citas de textos de pantalla, los nombres de objetos de API y el código conservan su grafía original.

## Preguntas frecuentes

### ¿Es una edición coreana de STE?

No. ASD-STE100 no tiene edición coreana, y tampoco existe una norma nacional de lenguaje controlado para el coreano. SimpleKorean es una guía no oficial. Reconstruye el propósito de las reglas de STE con la gramática coreana. Las reglas de finales de oración y de conectivos del modo estricto se basan en KS A 0001:2023.

### ¿Por qué 레포지토리 y 바디 no siguen la norma?

Los ejemplos de uso del Instituto Nacional de la Lengua Coreana son "리포지터리" (repositorio) y "보디" (cuerpo). Pero estas dos formas casi no se usan en documentos reales. En una muestra de documentación de proveedores, "리포지터리" apareció en 0 de 1104 casos. Por eso elegimos como grafía designada las formas habituales que el lector reconoce.

### ¿Qué hago si mi empresa usa otras grafías?

Ponga `.simple-korean.json` en la raíz del repositorio. El hook de inicio de sesión busca este archivo e informa al modelo de las grafías designadas que cambiaron. El linter y el hook de revisión de archivos también siguen este archivo. Avisan cuando se usa la grafía designada de antes del cambio. En una grafía designada use solo hangul, letras latinas, dígitos y espacios, hasta 20 caracteres. Puede indicar hasta 100 cadenas que se omiten (`skip`). El hook de inicio de sesión y el hook de revisión de archivos usan la configuración predeterminada en lugar de una configuración con un formato incorrecto. El linter se detiene con un error ante esa configuración. Los hooks y el linter ignoran los conceptos que no están en la lista de palabras.

```json
{"terms": {"release": {"write": "릴리즈"}, "column": "컬럼"}, "spacing": "attached"}
```

En este ejemplo, "릴리즈" significa release y "컬럼" significa column.

### ¿En qué se diferencia de una skill de pulido de textos?

Las skills de pulido de textos, como im-not-ai, eliminan el estilo de IA y los calcos de un texto ya escrito. SimpleKorean hace que el modelo escriba según las reglas desde el principio. También fija la estructura del documento y el formato de las respuestas. Por ejemplo, pone las condiciones antes de la orden y escribe una sola acción en cada oración. Además, incluye un linter y resultados de medición.

### ¿De dónde salen los límites de 15 y 20 eojeol?

No encontramos ningún estudio empírico que fije un límite de longitud de oración para documentos técnicos en coreano. Por eso son valores elegidos por diseño. En la calibración medimos la longitud de las oraciones en oraciones de ejemplo que siguen las reglas y en la salida de referencia (línea base). Los resultados están en [`evals/calibration/RECORD.md`](../evals/calibration/RECORD.md).

### ¿Por qué el modo estricto no tiene un diccionario coreano de palabras aprobadas?

El coreano no tiene una lista pública que fije a la vez las palabras aprobadas y las no aprobadas, como el diccionario de STE. La investigación está en [`docs/research/korean-controlled-language.md`](../docs/research/korean-controlled-language.md). El coreano expresa significados como la obligación y el permiso más en el final de la oración que en las palabras. Por eso el modo estricto agrupa en listas cerradas los finales de oración y los conectivos, en lugar de las palabras.

## Relación con el proyecto original

SimpleKorean es un proyecto derivado no oficial. Se separó de [AminBlg/SimpleEnglish](https://github.com/AminBlg/SimpleEnglish) v2.1.1 (`a6fcb4f`). Del original tomamos la estructura del repositorio, los hooks, la interfaz del linter y el método de medición. Las reglas, la lista de palabras y las tareas de medición las escribimos de nuevo para el coreano. No tomamos los resultados de medición en inglés del original.

Las reglas de respuesta también difieren del original. El original prohíbe encabezados y viñetas en todas las respuestas. SimpleKorean deja que el modelo decida, según el contenido y la extensión de cada respuesta, si usa encabezados y listas. La evidencia de esta decisión está en el [estudio sobre el formato de las respuestas](../docs/research/reply-formatting.md) (en coreano).

Como las reglas de respuesta difieren, el benchmark también cuenta defectos distintos en las respuestas. El original cuenta em-dash, negritas, encabezados y viñetas. SimpleKorean cuenta em-dash, negritas, tablas y un encabezado o una lista en la primera línea.

## Contribuir

Comunique sus preguntas y los errores en un issue. Los PR son bienvenidos. Un cambio que modifique las cifras publicadas debe incluir las salidas originales y pasar la verificación de cifras. La verificación de cifras necesita kiwipiepy.

Ejecute estos comandos desde la raíz del repositorio:

```bash
uv venv .venv --python 3.12
uv pip install --python .venv/bin/python kiwipiepy==0.24.0 kiwipiepy-model==0.24.0
.venv/bin/python evals/check_numbers.py
```

Antes de enviar los cambios, ejecute `python3 evals/ko_lint.py --self-test` y `python3 evals/tests/run.py`.

Escriba el título del PR como `<tipo>: <oración en coreano>`, por ejemplo `fix: 설정 파일의 지정형을 20자로 제한한다`. La oración termina en la forma declarativa llana del coreano (`-ㄴ다`). El tipo es uno de feat, fix, perf, refactor, docs, test, chore y ci. Al fusionar un PR, su título pasa a ser una línea del registro de cambios. Solo feat, fix y perf crean una nueva versión. Si no puede escribir el título en coreano, escríbalo en inglés. El mantenedor lo cambiará antes de fusionar y, hasta entonces, la comprobación del título fallará.

## Licencia

El código y la lista de palabras usan la licencia MIT. [`data/basic-vocabulary/grades.tsv`](../data/basic-vocabulary/grades.tsv) procede de la lista de niveles del vocabulario básico del coreano del Instituto Nacional de la Lengua Coreana. Sigue el tipo 1 de KOGL (Korea Open Government License), con atribución de la fuente. Las fuentes de terceros están en [`NOTICE`](../NOTICE).

Este es un proyecto no oficial. No tiene relación con ASD, con el autor original, con el Instituto Nacional de la Lengua Coreana ni con la Asociación Coreana de Normalización (Korean Standards Association). ASD-STE100 es una marca registrada de ASD.

Esta traducción no la ha revisado un hablante nativo. Informe de los errores en un [issue](https://github.com/say8425/SimpleKorean/issues).
