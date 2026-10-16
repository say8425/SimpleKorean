<p align="center">
  <strong>Hace que los documentos técnicos en coreano escritos por IA se lean como un manual de mantenimiento.</strong>
</p>

<p align="center">
  <a href="../README.md">한국어</a> | <a href="README.en.md">English</a> | <a href="README.ja.md">日本語</a> | <a href="README.zh.md">中文</a> | Español
</p>

<p align="center">
  <a href="https://agentskills.io"><img src="https://img.shields.io/badge/SKILL.md-open_standard-blue?style=flat" alt="Agent Skills"></a>
  <a href="https://github.com/say8425/SimpleKorean/releases/latest"><img src="https://img.shields.io/github/v/release/say8425/SimpleKorean?label=version&style=flat" alt="version"></a>
  <a href="../LICENSE"><img src="https://img.shields.io/badge/license-MIT-lightgrey?style=flat" alt="MIT"></a>
</p>

SimpleKorean es una skill de agente que hace que los LLM escriban en un coreano sencillo en documentos técnicos y respuestas de chat. Los manuales de mantenimiento aeronáutico usan un inglés controlado llamado ASD-STE100. Tomamos sus reglas de [SimpleEnglish](https://github.com/AminBlg/SimpleEnglish) y las reconstruimos para la gramática coreana. También añadimos una lista de grafías de préstamos. Medimos esta lista en documentos reales de desarrollo escritos en coreano.

La skill funciona en los agentes que leen el [estándar Agent Skills](https://agentskills.io). Algunos ejemplos son Claude Code, Cursor, Codex, Gemini CLI y OpenCode.

## Instalación

En Claude Code, instálela como plugin. El plugin incluye el hook de inicio de sesión, el hook de revisión de escritura y el estilo de salida.

```bash
claude plugin marketplace add say8425/SimpleKorean && claude plugin install simple-korean@simple-korean
```

El nombre del estilo de salida es `simple-korean:simple-korean`. Con el nombre corto no se encuentra. Elíjalo en Output style de `/config` o añada `{"outputStyle": "simple-korean:simple-korean"}` a `~/.claude/settings.json`. El hook de inicio de sesión añade un bloque de reglas de 2271 caracteres en cada sesión. El número de tokens que muestra `claude plugin details simple-korean` no incluye este bloque.

En Codex, instálela como plugin. El hook de inicio de sesión se instala con ella.

```bash
codex plugin marketplace add say8425/SimpleKorean
codex plugin add simple-korean@simple-korean
```

Antes de ejecutar un hook por primera vez, Codex pregunta si usted confía en él. El hook de inicio de sesión necesita Node.js, y el hook de revisión de escritura de Claude Code necesita Python 3.9 o posterior. Los detalles están en [`src/hooks/README.md`](../src/hooks/README.md).

En otros agentes, instale la skill con [skills CLI](https://github.com/vercel-labs/skills).

```bash
pnpm dlx skills add say8425/SimpleKorean
```

Si usa npm, ejecute `npx skills add say8425/SimpleKorean`. Este comando solo instala la skill. No instala los hooks ni el estilo de salida que se describen más arriba.

En las herramientas que no admiten skills, pegue el bloque de reglas de [`prompts/system-prompt.md`](../prompts/system-prompt.md). Puede ponerlo en el prompt del sistema, en `AGENTS.md` o en `.cursorrules`. Al final de este archivo también hay una versión corta de unos 120 tokens.

Después de instalarla, pida un documento técnico. Para corregir un texto que ya existe, diga "simple-korean으로 고쳐 줘" (corríjalo con simple-korean).

## Ejemplo

Estas son salidas originales del mismo modelo para la misma pregunta. Copiamos las dos respuestas sin cambios. Las respuestas están en coreano, porque esta skill hace que el modelo escriba en coreano.

<!-- example:start -->
Respuesta escrita sin la skill (`evals/results/2026-10-08/reply/baseline__oom__r1.txt`):

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

Respuesta del mismo modelo con SimpleKorean activado (`evals/results/2026-10-08/reply/plain__oom__r1.txt`):

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

Los ejemplos de documentos están en [`examples/before-after.md`](../examples/before-after.md).
<!-- example:end -->

## Benchmark

Volvimos a calcular todas las cifras de abajo a partir de las salidas originales guardadas en los commits. En cada push, la CI las compara con `evals/check_numbers.py`. `claude-sonnet-5-5` (effort low) escribió los documentos y las respuestas, y `claude-opus-5-5` hizo la evaluación. Ninguna ejecución leyó la configuración del usuario, servidores MCP ni archivos de instrucciones como AGENTS.md. El modelo evaluador también es Claude, así que puede tener un sesgo a favor de su misma familia de modelos. Un eojeol es una unidad del coreano separada por espacios.

<!-- benchmark:start evals/results/2026-10-08 -->
Respuestas: hicimos 8 preguntas 2 veces en cada condición. Cada pregunta contiene un término técnico. En total hay 32 respuestas. Con la skill activada, los defectos visibles para el lector (em-dash, negritas, encabezados, viñetas) bajaron un 100 % (de 394 a 0). En una evaluación a ciegas de 16 pares, la respuesta de SimpleKorean ganó 15, empató 1 y perdió 0.

| Condición | Respuestas | Media de eojeol | Media de oraciones | em-dash | Negritas | Encabezados | Viñetas | Saludos y despedidas |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Sin skill | 16 | 246 | 30.9 | 0 | 141 | 45 | 208 | 12 |
| SimpleKorean | 16 | 179 | 18.6 | 0 | 0 | 0 | 0 | 1 |

Documentos: el modelo escribió cada una de las 8 tareas de documentación de sqlpipe 2 veces en cada condición. Cada tasa es el recuento del linter dividido entre el número de eojeol. El linter es una comprobación con expresiones regulares, así que lea las cifras como una dirección, no como una clasificación.

| Condición | Documentos | Errores por 100 eojeol | Avisos por 100 eojeol | Calcos por 100 eojeol | Tasa de grafía designada | Tasa de palabras fáciles | Oración más larga |
|---|---:|---:|---:|---:|---:|---:|---:|
| Sin skill | 16 | 0.00 | 1.09 | 0.14 | 95.0 % | 40.2 % | 18 eojeol |
| Modo básico | 16 | 0.00 | 0.00 | 0.00 | 100.0 % | 44.8 % | 16 eojeol |
| Modo estricto | 16 | 0.00 | 0.00 | 0.00 | 100.0 % | 45.5 % | 17 eojeol |

Las salidas originales, la distribución de grafías y las condiciones de medición están en [`evals/results/2026-10-08/RESULTS.md`](../evals/results/2026-10-08/RESULTS.md).
<!-- benchmark:end -->

## Reglas

Las reglas están en [`SKILL.md`](../skills/simple-korean/SKILL.md). La lista completa de reglas con número K que usan el modo de revisión y el modo estricto está en [`rule-catalog.md`](../skills/simple-korean/references/rule-catalog.md).

Las respuestas de chat usan estas reglas en todos los modos.

| Regla | Lo que evita |
|---|---|
| Responda en prosa. No use encabezados, viñetas, negritas ni tablas | Formato alrededor de una respuesta de una sola línea |
| Escriba la respuesta en la primera oración | Una introducción que repite la pregunta |
| No use em-dash | Ideas unidas solo a medias |
| Explique brevemente un término conceptual la primera vez que lo use | Términos que el lector tiene que buscar |
| Use un solo estilo en cada respuesta. No use saludos ni despedidas | "좋은 질문입니다" (Buena pregunta), "도움이 되셨기를 바랍니다" (Espero que le haya servido) |

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

El modo básico son todas las reglas de arriba. No hace falta activarlo.

El modo estricto se activa cuando usted dice "엄격 모드" (modo estricto), "통제 언어" (lenguaje controlado), "KS A 0001" o "STE". El modo estricto limita los finales de oración de los documentos a cinco formas. La obligación es "-해야 합니다" (debe). La prohibición es "-하면 안 됩니다" (no debe). El permiso es "-해도 됩니다" (puede). La capacidad es "-ㄹ 수 있습니다" (es capaz de). Los hechos van en presente. El modo estricto no usa el conectivo "(이)나" (o) y escribe las condiciones solo con "-면" (si). La base son los anexos H e I de KS A 0001:2023. En modo estricto, las respuestas siguen igualmente las reglas del modo básico.

El modo de revisión se activa cuando usted pide una revisión en lugar de un texto. Para cada infracción, indica el número K, el fragmento afectado y la oración corregida.

## Política de grafía

Los préstamos siguen las normas de transcripción de préstamos del coreano y los ejemplos de uso del Instituto Nacional de la Lengua Coreana (디렉터리 directorio, 메시지 mensaje, 애플리케이션 aplicación). Cuando esos principios no dan una respuesta, decide la lista de [`data/terms.json`](../data/terms.json). Hicimos esta lista contando las grafías reales en documentos localizados, documentación de proveedores, blogs técnicos de empresas y archivos README de GitHub. La evidencia está en [`docs/research/loanword-spelling-usage.md`](../docs/research/loanword-spelling-usage.md).

| Grupo | Forma que se usa |
|---|---|
| 23 palabras que se usan según la norma | Forma normativa (메시지 mensaje, 애플리케이션 aplicación, 메서드 método, 라이선스 licencia) |
| 4 palabras que varían según la fuente | Forma normativa (디렉터리 directorio, 릴리스 release, 셸 shell, 리디렉션 redirección) |
| 4 palabras con una forma habitual ya fijada | 레포지토리 (repositorio), 바디 (cuerpo), 칼럼 (columna), 대상 (destino) |
| 2 palabras sin grafía oficial | 리디렉션 (redirección), 리팩터링 (refactorización) |
| 5 palabras en las que se elige entre un préstamo y una palabra coreana | 오류 (error), 매개변수 (parámetro), 사용자 (usuario), 기본값 (valor predeterminado), 배포 (despliegue) |
| 4 casos de espaciado | 기본값, 매개변수, 반환값, 오픈소스 (se escriben sin espacios) |

Los nombres de productos, las citas de textos de pantalla, los nombres de objetos de API y el código conservan su grafía original.

## Preguntas frecuentes

¿Es una edición coreana de STE? No. ASD-STE100 no tiene edición coreana, y tampoco existe una norma nacional de lenguaje controlado para el coreano. SimpleKorean es una guía no oficial. Reconstruye el propósito de las reglas de STE con la gramática coreana. Las reglas de finales de oración y de conectivos del modo estricto se basan en KS A 0001:2023.

¿Por qué 레포지토리 y 바디 no siguen la norma? Los ejemplos de uso del Instituto Nacional de la Lengua Coreana son "리포지터리" (repositorio) y "보디" (cuerpo). Pero estas dos formas casi no se usan en documentos reales. En una muestra de documentación de proveedores, "리포지터리" apareció en 0 de 1104 casos. Por eso elegimos como grafía designada las formas habituales que el lector reconoce.

¿Qué hago si mi empresa usa otras grafías? Ponga `.simple-korean.json` en la raíz del repositorio. El hook de inicio de sesión busca este archivo e informa al modelo de las grafías designadas que cambiaron. El linter y el hook de revisión de escritura también siguen este archivo. Avisan cuando se usa la grafía designada de antes del cambio. En una grafía designada use solo hangul, letras latinas, dígitos y espacios, hasta 20 caracteres. Puede indicar hasta 100 cadenas que se omiten (`skip`). Se ignoran las configuraciones con un formato incorrecto y los conceptos que no están en la lista de palabras.

```json
{"terms": {"release": {"write": "릴리즈"}, "column": "컬럼"}, "spacing": "attached"}
```

En este ejemplo, "릴리즈" significa release y "컬럼" significa column.

¿En qué se diferencia de una skill de pulido de textos? Las skills de pulido de textos, como im-not-ai, eliminan el estilo de IA y los calcos de un texto ya escrito. SimpleKorean hace que el modelo escriba según las reglas desde el principio. También fija la estructura del documento y el formato de las respuestas. Por ejemplo, pone las condiciones antes de la orden y escribe una sola acción en cada oración. Además, incluye un linter y resultados de medición.

¿De dónde salen los límites de 15 y 20 eojeol? No encontramos ningún estudio empírico que fije un límite de longitud de oración para documentos técnicos en coreano. Por eso son valores elegidos por diseño. En la calibración medimos la longitud de las oraciones en oraciones de ejemplo que siguen las reglas y en la salida de referencia (línea base). Los resultados están en [`evals/calibration/RECORD.md`](../evals/calibration/RECORD.md).

¿Por qué el modo estricto no tiene un diccionario coreano de palabras aprobadas? El coreano no tiene una lista pública que fije a la vez las palabras aprobadas y las no aprobadas, como el diccionario de STE. La investigación está en [`docs/research/korean-controlled-language.md`](../docs/research/korean-controlled-language.md). El coreano expresa significados como la obligación y el permiso más en el final de la oración que en las palabras. Por eso el modo estricto agrupa en listas cerradas los finales de oración y los conectivos, en lugar de las palabras.

## Relación con el proyecto original

SimpleKorean es un proyecto derivado no oficial. Se separó de [AminBlg/SimpleEnglish](https://github.com/AminBlg/SimpleEnglish) v2.1.1 (`a6fcb4f`). Del original tomamos la estructura del repositorio, los hooks, la interfaz del linter y el método de medición. Las reglas, la lista de palabras y las tareas de medición las escribimos de nuevo para el coreano. No tomamos los resultados de medición en inglés del original.

## Contribuir

Comunique sus preguntas y los errores en un issue. Los PR son bienvenidos. Un cambio que modifique las cifras publicadas debe incluir las salidas originales y pasar la verificación de cifras. La verificación de cifras necesita kiwipiepy.

```bash
uv venv .venv --python 3.12 && uv pip install --python .venv/bin/python kiwipiepy==0.24.0 kiwipiepy-model==0.24.0
.venv/bin/python evals/check_numbers.py
```

Antes de enviar los cambios, ejecute `python3 evals/ko_lint.py --self-test` y `python3 evals/tests/run.py`.

Escriba el título del PR como `<tipo>: <oración en coreano>`, por ejemplo `fix: 설정 파일의 지정형을 20자로 제한한다`. La oración termina en la forma declarativa llana del coreano (`-ㄴ다`). El tipo es uno de feat, fix, perf, refactor, docs, test, chore y ci. Al fusionar un PR, su título pasa a ser una línea del registro de cambios. Solo feat, fix y perf crean una nueva versión. Si no puede escribir el título en coreano, escríbalo en inglés. El mantenedor lo cambiará antes de fusionar y, hasta entonces, la comprobación del título fallará.

## Licencia

El código y la lista de palabras usan la licencia MIT. [`data/basic-vocabulary/grades.tsv`](../data/basic-vocabulary/grades.tsv) procede de la lista de niveles del vocabulario básico del coreano del Instituto Nacional de la Lengua Coreana. Sigue el tipo 1 de KOGL (Korea Open Government License), con atribución de la fuente. Las fuentes de terceros están en [`NOTICE`](../NOTICE).

Este es un proyecto no oficial. No tiene relación con ASD, con el autor original, con el Instituto Nacional de la Lengua Coreana ni con la Asociación Coreana de Normalización (Korean Standards Association). ASD-STE100 es una marca registrada de ASD.

Esta traducción no la ha revisado un hablante nativo. Informe de los errores en un [issue](https://github.com/say8425/SimpleKorean/issues).
