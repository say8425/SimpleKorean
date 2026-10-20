# 답변 표 실험 자료

[`../../reply-tables.md`](../../reply-tables.md) 연구의 원자료다. 2026-10-19에 같은 질문, 같은 모델, 같은 판정 규칙으로 만들었다. 연구 문서의 답 모양, 표 폭, 판정 수, 채택 조건의 결과는 `python3 docs/research/data/reply-tables/analyze.py`로 다시 계산할 수 있다. 판정 이유는 `judge-opus.jsonl`의 `reason`에 있다.

| 파일 | 내용 |
|---|---|
| `criteria.md` | 판정 전에 정한 채택 조건 |
| `prompts.json` | 질문 20개. `id`, 질문 유형(`type`), 출처(`source`), 표가 맞는 질문인지(`table_fit`), 질문 문장(`prompt`), 답에 남아야 할 자료값(`targets`) |
| `base-rule-block.md` | 1.1.0 규칙 블록 |
| `policies.json` | 정책마다 바꾼 답변 문단 두 개(`format`, `lead`) |
| `generate.py` | 답을 만드는 스크립트 |
| `answers.jsonl` | `claude-sonnet-5-5`의 답 160개. 조건(`cond`), 질문(`id`), 회차(`run`), 답(`text`) |
| `answers-opus.jsonl` | `claude-opus-5-5`의 답 80개. 모양만 셌고 판정하지 않았다 |
| `judge-prompts.json` | Opus 판정 문장의 틀과 Jev 질문 세 개 |
| `judge.py` | 쌍 판정 스크립트 |
| `judge-opus.jsonl` | `claude-opus-5-5`의 쌍 판정 140개 |
| `judge-jev.jsonl` | `jev-1.14.0`의 쌍 판정 140개 |
| `analyze.py` | 위 자료로 수치를 세는 스크립트 |
| `meta.json` | 격리 실행을 확인한 결과 |
| `render/` | 터미널 두 곳에서 표가 보이는 모양 |

## 만든 방법

정책마다 `base-rule-block.md`에서 답변 문단 두 개만 `policies.json`의 문장으로 바꿨다. 나머지 문장은 모든 정책에서 같다. `prohibit`의 블록은 1.1.0 규칙 블록 그대로다. 조건은 네 가지다:

- `baseline`: 규칙 블록 없음
- `prohibit`: 현행 규칙. 굵은 글씨와 표를 막음
- `permit`: 표를 쓸지 모델이 정함
- `conditional`: 여러 항목을 같은 기준 여러 개로 견주거나 항목마다 숫자를 나란히 보일 때만 표를 씀. 셀에는 짧은 값만 넣음

답은 `evals/bench_common.py`의 격리 실행(`claude -p`, 사용자 설정과 MCP 서버 없음)으로 만들었다. 실행한 명령은 다음과 같다:

```sh
python3 docs/research/data/reply-tables/generate.py --out answers.jsonl --runs 2
python3 docs/research/data/reply-tables/generate.py --model claude-opus-5-5 --runs 1 --out answers-opus.jsonl
```

질문 20개 가운데 10개는 표가 맞는 질문(`table_fit: true`)이다. 9개는 이 연구에서 새로 썼고, 1개(`probes`)는 [답변 서식 실험](../reply-format/)의 질문이다. 나머지 10개는 표가 맞지 않는 질문으로, 모두 답변 서식 실험의 질문이다. 질문 4개(`hook-bench`, `ci-matrix`, `pr-status`, `cloud-cost`)는 질문 안에 자료를 준다. 이 질문에는 답에 남아야 할 값(`targets`)을 적었다.

## 판정

판정은 같은 질문, 같은 회차의 두 답을 비교했다. 판정 기록의 `pair`는 [앞 조건, 뒤 조건]이다. 첫 순서(`order1`)는 앞 조건의 답을 A로, 둘째 순서(`order2`)는 뒤 조건의 답을 A로 보였다. 두 순서에서 같은 조건을 고르면 그 조건이 이긴다. 두 순서의 선택이 다르거나 한쪽이 tie면 무승부(`tie`)다.

정책 쌍은 세 개이고, 쌍마다 40번 판정했다. 같은 정책 두 답의 판정도 20번 했다. 이 판정은 `prohibit`의 1회차 답과 2회차 답을 비교하고, `pair`를 `["prohibit@1", "prohibit@2"]`로, `run`을 0으로 적었다.

Opus의 판정 문장은 답변 서식 실험과 같다. Jev의 질문은 찾기 하나만 바꿨다. 찾을 정보의 예에 값(value)을 더했고, 헤더와 목록에 더해 표도 화면에 렌더링된다고 적었다. 실행한 명령은 다음과 같다:

```sh
python3 docs/research/data/reply-tables/judge.py --judge opus --out judge-opus.jsonl
python3 docs/research/data/reply-tables/judge.py --judge jev --out judge-jev.jsonl
```

`judge.py`는 Jev를 부를 때 환경 변수 `TYPESAFE_API_KEY`를 쓴다. `p_x`는 앞 조건의 선택지에 Jev가 준 확률을 두 순서에서 평균한 값이다.

## 분석에 쓴 정의

- 표: 코드 블록 밖에서 구분 줄(`|---|`) 바로 위에 머리글 행이 있는 블록이다. 구분 줄 아래로 `|`가 든 줄이 이어지는 데까지를 한 표로 센다.
- 렌더링 폭: 열마다 가장 넓은 셀의 표시 폭을 더하고, 열 수의 3배와 1을 더한 값이다. 표시 폭은 유니코드 동아시아 폭(East Asian Width)이 W나 F인 글자를 2칸, 결합 문자를 0칸, 나머지를 1칸으로 센다. 렌더링되면 사라지는 표시는 세지 않는다. 백틱, 굵은 글씨 표시(`**`, `__`), 링크의 주소 부분이 그렇다.
- 셀 글자 수: 머리글 행을 뺀 셀의 글자 수다. 렌더링 폭과 같은 표시는 세지 않는다.
- 자료값이 남은 비율: `targets`의 값 가운데 답에 나온 값의 비율이다. 쉼표를 뺀 뒤 찾는다. 숫자는 앞뒤에 다른 숫자가 붙지 않을 때만 센다.
- 연결어, 문장 수, 길이 통제: 답변 서식 실험과 같다. 길이 통제는 두 답의 글자 수 차이가 긴 쪽의 20% 미만인 쌍만 센다.

## 터미널 렌더링

`render/`의 `numeric.md`, `wide.md`, `code.md`는 시험에 쓴 표다. 나머지 파일은 표가 화면에 보인 모양을 텍스트로 떠서 표 부분만 남긴 것이다. 파일 이름은 `<도구>-<폭>-<표>.txt`다.

화면은 tmux로 폭 80칸과 120칸의 창을 만들어 떴다. Claude Code 2.1.303에서는 `claude-haiku-5-5`가, Codex CLI 0.160.0에서는 `gpt-6.1-sol`이 표를 그대로 출력하게 했다. Codex에는 `code.md`를 시험하지 않았다.

넣지 않은 것은 Jev 응답 캐시와 판정 모델의 원래 출력 전문이다. 판정 결과는 판정 기록에 모두 들어 있다.

## 실행 순서

답과 판정 기록에는 시각이 없다. 그래서 `criteria.md`를 판정 전에 커밋했다는 순서는 저장소 자료만으로는 확인할 수 없다. 실행한 컴퓨터에서 본 시각은 다음과 같다:

- `criteria.md`의 커밋(`0125b62`): 2026-10-19 18:15:49
- Jev 응답 캐시의 가장 이른 파일: 18:22:04
- 판정 기록의 마지막 쓰기: `judge-jev.jsonl` 18:22:18, `judge-opus.jsonl` 18:26:55

`judge.py`는 판정을 마친 뒤 고쳤다. 네트워크 오류의 재시도 범위를 넓히고, API 키를 먼저 확인하게 했다. 판정 결과를 만드는 부분은 바꾸지 않았다.
