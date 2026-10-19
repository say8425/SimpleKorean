# 채팅 답변의 표는 아직 허용하지 않는다

SimpleKorean의 채팅 답변 규칙은 표 금지를 그대로 둔다. 표를 허용한 정책 두 개를 현행 금지와 비교했다. 두 정책 모두 판정 전에 정한 채택 조건 일곱 개를 다 만족하지 못했다. 그래서 미리 정한 대로 현행 규칙을 유지한다.

판정 모델(두 답 가운데 나은 쪽을 고르는 모델)은 표가 찾기를 돕는다고 판정했다. 표가 맞는 질문에서 두 판정 모델은 모두 표 정책의 답을 찾기에서 크게 앞세웠다. 하지만 이해에서는 Opus가 표 없는 답을 뚜렷이 더 골랐다. 전체 선호의 차이는 작았다. 같은 정책의 두 답을 비교할 때 생기는 흔들림과 크기가 비슷했다.

정책마다 걸린 조건도 달랐다. 허용은 표가 맞지 않는 질문의 답 20개 가운데 10개에도 표를 썼다. 허용이 쓴 표의 43%는 렌더링 폭이 100칸을 넘었다. 조건부 허용은 표를 맞는 질문에만 짧은 셀로 썼다. 하지만 전체 선호의 이득이 없었고, 이해에서도 금지 쪽으로 기울었다.

문헌은 조건을 걸어 허용하는 쪽을 가리킨다. 여러 항목을 같은 기준으로 견주는 내용에서 표가 사람의 이해를 높인 무작위 실험이 있다. 확인한 작성 지침 가운데 표를 막은 곳은 없다. 현행 금지도 독자 실험이 아니라 원본 SimpleEnglish의 문장 수 규칙에서 왔다. 하지만 채팅 답변의 표를 사람에게 시험한 연구는 찾지 못했다. 판정 모델이 서식 있는 답 쪽으로 기운다는 연구도 있다.

터미널도 확인했다. Claude Code와 Codex CLI는 모두 표를 그린다. 하지만 표가 폭에 맞지 않으면 Claude Code는 표를 "머리글: 값" 줄로 바꿨다. Codex CLI는 셀 안의 한글 낱말을 중간에서 끊었다.

실험과 문헌이 갈리는 곳은 사람 독자다. 다음 판단은 여러 개발자가 80칸 터미널에서 답의 값을 찾고 이유를 맞히는 과제 시험으로 내려야 한다. 그 시험의 후보는 조건부 허용 문구다.

## 표 정책은 찾기 판정에서 앞섰지만 채택 조건을 넘지 못했다

실험은 2026-10-19에 했다. 같은 질문에 정책마다 답을 만들고, 판정 모델에게 두 답을 비교하게 했다. 답, 판정 기록, 스크립트는 이 저장소에 있다 ([`data/reply-tables/`](data/reply-tables/)). 방법은 [답변 서식 연구](reply-formatting.md)를 따랐다.

### 세 정책은 표 문장만 달랐다

규칙 블록(스킬이 시스템 프롬프트에 붙이는 규칙 글)은 현행 1.1.0 블록을 그대로 썼다 ([`base-rule-block.md`](data/reply-tables/base-rule-block.md)). 정책마다 표를 다룬 문장만 바꿨다:

<!-- simple-korean: off -->
- 금지(현행): "답변에는 굵은 글씨와 표를 쓰지 마세요."
- 허용: "답변에는 굵은 글씨를 쓰지 마세요. 표는 써도 됩니다. 쓸지는 답의 내용을 보고 정하세요."
- 조건부 허용: "답변에는 굵은 글씨를 쓰지 마세요. 표는 여러 항목을 같은 기준 여러 개로 견주거나 항목마다 숫자를 나란히 보일 때만 쓰세요. 칸에는 짧은 값만 넣고, 이유와 설명은 표 밖의 문장으로 쓰세요."
<!-- simple-korean: on -->

조건부 허용 문구의 "칸"은 표의 셀을 뜻한다. 이 문서는 셀을 "셀"로, 터미널의 글자 자리를 "칸"으로 쓴다. 두 표 정책은 "헤더와 목록은 첫 문장 뒤에 두세요."도 "헤더, 목록, 표는 첫 문장 뒤에 두세요."로 바꿨다. 기준선(규칙 블록 없이 만든 답)은 답 모양만 비교하고 판정에는 넣지 않았다.

### 방법

질문은 20개다. 10개는 표가 맞는 질문(아래 T)이다. 여러 선택지 비교, 옵션과 상태 코드 정리, 명령 대응, 측정값과 테스트 결과 보고를 묻는다. 그 가운데 4개는 측정값, CI 결과, PR 상태, 요금 같은 자료를 질문 안에 준다. 나머지 10개는 표가 맞지 않는 질문(아래 N)이다. 짧은 설명, 문제 해결, 긴 절차, 비개발자 설명, 계획을 묻고, 모두 답변 서식 실험의 질문이다. 묶음은 답을 보기 전에 정했다.

답은 `claude-sonnet-5-5`가 effort(생각에 들이는 노력의 수준) low로 썼다. 사용자 설정과 MCP 서버를 읽지 않는 격리된 `claude -p`로 질문마다 두 번 답하게 했다. 그래서 정책마다 답이 40개다. `claude-opus-5-5`로도 질문마다 한 번씩 답을 만들었고, 이 답은 모양만 셌다.

판정 모델은 `claude-opus-5-5`(아래 Opus, effort low)와 TypeSafe의 `jev-1.14.0`(아래 Jev)이다. 같은 질문, 같은 회차의 두 답을 순서를 바꿔 두 번 물었다. 두 번 모두 같은 쪽을 고르면 그쪽의 승으로 셌다. 아니면 무승부로 셌다. 기준은 답변 서식 실험과 같은 세 가지다:

- 이해: 분야를 잘 모르는 독자가 한 번 읽고 내용과 이유를 정확히 이해하기 쉬운 답
- 찾기: 나중에 다시 볼 때 필요한 정보를 빨리 찾을 수 있는 답
- 전체 선호: 질문한 사람이 받고 싶은 답

Opus의 판정 문장은 답변 서식 실험과 같다. Jev의 질문은 찾기 하나만 고쳤다. 찾을 정보의 예에 값을 더했고, 헤더와 목록에 더해 표도 화면에 렌더링된다고 적었다.

정책 쌍 세 개를 쌍마다 40번 판정했다. 현행 금지의 1회차 답과 2회차 답도 질문마다 비교했다. 이 비교는 서식이 같을 때 판정 모델이 얼마나 한쪽을 고르는지 보여 준다. 아래에서는 이것을 같은 정책 비교라고 부른다.

채택 조건은 판정 전에 정해 커밋했다 ([`criteria.md`](data/reply-tables/criteria.md)). T에서 표 정책은 두 판정 모델 모두에게 찾기 5쌍, 전체 선호 3쌍 이상 앞서야 한다. N에서는 찾기와 전체 선호 모두 3쌍보다 많이 지면 안 된다. 그 밖에 이해, 길이 통제, 과용, 폭에 조건이 있다.

### 허용은 표가 맞지 않는 질문에도 표를 썼다

조건마다 답 40개를 센 결과는 다음과 같다. 렌더링 폭은 상자 테두리로 그릴 때 표가 차지하는 터미널 칸 수다. 한글은 한 글자에 2칸으로 센다.

| 조건 | 표 있는 답(T, N) | 표 수 | 폭 중앙값 | 100칸 이하 | 셀 글자 수 중앙값 |
|---|---|---|---|---|---|
| 기준선 | 13, 5 | 18 | 133.5칸 | 4개 | 19자 |
| 금지 | 0, 0 | 0 | 없음 | 없음 | 없음 |
| 허용 | 20, 10 | 30 | 97.5칸 | 17개 | 13자 |
| 조건부 허용 | 14, 0 | 14 | 63칸 | 14개 | 6자 |

허용은 T의 답 20개 모두에 표를 썼다. N에서도 답 20개 가운데 10개에 표를 썼다. 질문으로 세면 N 10개 가운데 6개다. 예를 들어 인증서 오류 질문의 답은 원인과 증상을 표로 나눴다. 허용의 표 30개 가운데 13개는 100칸을 넘었고, 가장 넓은 표는 221칸이었다.

조건부 허용은 N에 표를 쓰지 않았다. 표 14개는 모두 100칸 안에 들었고, 가장 넓은 표도 82칸이었다. 20자를 넘는 셀은 181개 가운데 6개였다. 하지만 T 가운데 두 질문에서는 네 번 모두 표 대신 목록을 썼다. 측정값을 준 질문과 CI 결과를 준 질문이다.

표는 질문에 준 자료를 더 많이 남기지 않았다. 자료를 준 질문 4개에서 답에 남은 값의 비율은 금지와 허용이 0.84, 조건부 허용이 0.79였다. 글자 수 중앙값은 금지 1,125.5자, 허용 1,106자, 조건부 허용 1,129.5자로 비슷했다. 첫 줄에 표를 둔 답은 어느 조건에도 없었다.

Opus의 답도 같은 모양이었다. 허용에서 Opus는 N의 답 10개 가운데 5개에 표를 썼다. 표 15개 가운데 100칸 이하는 4개뿐이었다. 조건부 허용에서는 N에 표를 쓰지 않았고, 표 8개 가운데 7개가 100칸 안에 들었다.

### 표 정책은 찾기 판정에서 크게 앞섰다

T 20쌍의 판정은 다음과 같다. 각 칸은 표 정책의 승, 금지의 승, 무승부 순서다.

| 비교 | 판정 모델 | 이해 | 찾기 | 전체 선호 |
|---|---|---|---|---|
| 허용 대 금지 | Opus | 2, 9, 9 | 15, 0, 5 | 8, 3, 9 |
| 허용 대 금지 | Jev | 2, 6, 12 | 18, 0, 2 | 5, 2, 13 |
| 조건부 허용 대 금지 | Opus | 3, 5, 12 | 12, 2, 6 | 6, 3, 11 |
| 조건부 허용 대 금지 | Jev | 5, 7, 8 | 10, 0, 10 | 4, 6, 10 |

찾기의 차이는 같은 정책 비교의 흔들림보다 컸다. 같은 정책 비교 20쌍에서 찾기의 차이는 Opus 6쌍(8 대 2), Jev 1쌍(2 대 3)이었다. 표 정책은 T 20쌍에서 Opus에게 10~15쌍, Jev에게 10~18쌍 앞섰다. 다만 조건부 허용의 Opus 차이 10쌍은 Opus의 흔들림 6쌍보다 조금 클 뿐이다.

Opus의 판정 이유도 같은 쪽이다. 표 있는 답은 "표 하나로 네 기준을 한눈에 비교할 수 있어 다시 찾아보기 좋다"는 이유로 찾기를 이겼다. N에서도 허용은 찾기에서 앞섰다(Opus 13 대 3, Jev 11 대 2). 허용이 N에 쓴 표 10개가 이 결과에 섞여 있다.

### 이해는 Opus가 표 없는 답을 골랐다

T와 N을 합친 40쌍의 이해 판정에서 Opus는 금지 20, 허용 5, 무승부 15로 판정했다. Jev는 금지 10, 허용 6, 무승부 24였다. 조건부 허용을 상대로는 Opus가 금지 13, 조건부 허용 5, 무승부 22였다. Jev는 금지 12, 조건부 허용 7, 무승부 21이었다.

Opus의 결과는 길이를 맞춰도 남았다. 두 답의 글자 수 차이가 긴 쪽의 20% 미만인 33쌍만 셌다. 이 33쌍에서 Opus는 금지 17, 허용 3, 무승부 13으로 판정했다. 같은 33쌍에서 Jev는 금지 6, 허용 5, 무승부 22였다.

Jev의 이해 판정은 흔들림이 컸다. 같은 정책 비교에서 Jev는 1회차 답을 9번, 2회차 답을 2번 골랐다. 그래서 Jev의 이해 차이는 이 실험으로 가를 수 없다. Opus의 같은 정책 비교는 6 대 7이었다.

Opus의 이유는 답변 서식 실험과 같은 모양이다. 표 없는 답은 "원인을 문단으로 풀어 써서 처음 읽는 사람이 이유를 따라가기 쉽다"는 이유로 이해를 이겼다. 같은 쌍에서 표 있는 답은 다시 찾아보기 쉽다는 이유로 찾기를 이겼다. 처음 읽기와 다시 찾기가 서로 맞바꾸는 관계로 나타났다.

### 전체 선호의 차이는 흔들림과 비슷했다

T의 전체 선호에서 허용은 두 판정 모델 모두에게 앞섰다(Opus 8 대 3, Jev 5 대 2). 조건부 허용은 Opus에게 앞서고(6 대 3) Jev에게 뒤졌다(4 대 6). 이 차이는 같은 정책 비교의 차이와 크기가 비슷하다. 같은 정책 비교의 전체 선호에서 Opus는 6 대 2, Jev는 8 대 4로 한쪽을 골랐다.

N의 전체 선호에서 Opus는 조건부 허용을 상대로 금지를 8번 골랐다(조건부 허용 0, 무승부 12). 조건부 허용은 N에 표를 하나도 쓰지 않았다. Opus의 이유도 표가 아니라 내용이었다. 예를 들어 커밋 메시지를 고치는 질문의 2회차에서는 금지의 답만 `git commit --amend --only`와 `git rebase -i`의 reword를 알려 줬다.

판정 모델은 대체로 긴 답을 골랐다. 전체 선호에서 승패가 난 쌍 가운데 긴 답이 이긴 쌍은 Opus 62쌍 중 45쌍, Jev 55쌍 중 42쌍이었다. 두 판정 모델의 판정이 같은 쌍은 정책 쌍 120쌍 가운데 이해 58쌍, 찾기 75쌍, 전체 선호 65쌍이었다.

### 두 정책 모두 채택 조건에 못 미쳤다

채택 조건 일곱 개의 결과는 다음과 같다. 값은 표 정책이 금지보다 앞선 쌍의 수이고, Opus와 Jev 순서다.

| 조건 | 허용 | 조건부 허용 |
|---|---|---|
| 1. T 찾기 5쌍 이상 | 통과(15, 18) | 통과(10, 10) |
| 2. T 전체 선호 3쌍 이상 | 통과(5, 3) | 실패(3, -2) |
| 3. N에서 3쌍보다 많이 지지 않음 | 통과 | 실패(Opus 전체 선호 -8) |
| 4. 두 모델 모두 이해에서 4쌍 이상 지면 실패 | 실패(-15, -4) | 실패(-8, -5) |
| 5. T 길이 통제 쌍의 전체 선호 | 통과(6, 5) | 실패(2, -1) |
| 6. N에 표를 쓴 답 4개 이하 | 실패(10개) | 통과(0개) |
| 7. 표의 75% 이상이 100칸 이하 | 실패(57%) | 통과(100%) |

허용은 과용, 폭, 이해에서 걸렸다. 조건부 허용은 과용과 폭을 지켰지만, 전체 선호의 이득을 보이지 못했다. 조건 4의 Jev 값(-4, -5)은 Jev의 같은 정책 흔들림(7쌍) 안에 있다. 하지만 이 값을 빼도 결론은 같다. 허용은 조건 6과 7에서, 조건부 허용은 조건 2, 3, 5에서도 걸렸다. 그래서 판정 전에 정한 대로 현행 금지를 그대로 둔다.

## 터미널은 표를 그리지만 폭이 모자라면 모양을 바꾼다

SimpleKorean이 도는 두 도구는 모두 마크다운 표를 그린다. Claude Code는 1.0.10(2025-06-04)부터 표를 그렸다 ([Claude Code changelog](https://code.claude.com/docs/en/changelog)). Codex CLI는 0.131.0(2026-05-18)부터 그린다 ([Codex rust-v0.131.0](https://github.com/openai/codex/releases/tag/rust-v0.131.0)). 그 전에는 표가 파이프 원문으로 보였고, 그래서 에이전트가 표를 피해야 한다는 신고가 있었다 ([Codex #8259](https://github.com/openai/codex/issues/8259)).

이 연구는 두 도구의 화면을 직접 떴다. tmux로 80칸과 120칸 창을 만들고, Claude Code에는 표 세 개를, Codex CLI에는 표 두 개를 그대로 출력하게 했다. Claude Code는 2.1.303, Codex CLI는 0.160.0이다 ([`render/`](data/reply-tables/render/)). 숫자만 든 표는 두 도구 모두 두 폭에서 열을 맞춰 그렸다. 한글이 섞여도 열이 어긋나지 않았다.

셀에 문장이 든 표(렌더링 폭 198칸)는 모양이 갈렸다. Claude Code는 120칸에서 셀 안의 줄을 띄어쓰기에서 바꿨다. 80칸에서는 표를 행마다 "머리글: 값" 줄로 바꿨다:

```text
⏺ 선택지: SQLite
  운영 부담: 서버가 없어 운영할 것이 거의 없지만 파일 백업과 동시 쓰기 제한을
  직접 챙겨야 합니다
  비용: 추가 비용이 없습니다
  확장성: 쓰기가 몰리면 잠금 때문에 한계가 빨리 옵니다
  ────────────────────────────────────────
```

Codex CLI는 같은 표를 80칸과 120칸 모두에서 격자로 그렸다. 하지만 셀 안의 한글 낱말을 중간에서 끊었다:

```text
   SQLite      서버가 없어 운영할    추가 비용이 없습니     쓰기가 몰리면 잠금
               것이 거의 없지만      다                     때문에 한계가 빨리
               파일 백업과 동시                             옵니다
```

이 동작은 사용자 신고와 맞는다. Claude Code 사용자는 표가 격자로 남을지가 열 수보다 셀 길이에 달렸다고 신고했다. 이 전환을 끄는 설정은 없다고도 적었다 ([Claude Code #82950](https://github.com/anthropics/claude-code/issues/82950)). Codex는 좁게 눌린 표를 키와 값의 목록으로 바꾸는 기능을 넣었다 ([Codex PR #24636](https://github.com/openai/codex/pull/24636)). 이번 시험의 표는 그 목록으로 바뀌지 않고 격자로 남았다.

한글 음절은 유니코드 동아시아 폭(East Asian Width)이 W라서 터미널에서 2칸을 쓴다 ([UAX #11](https://www.unicode.org/reports/tr11/tr11-44.html)). 그래서 기본 80칸 터미널 한 줄에는 한글이 40자까지 들어간다. GNOME Terminal의 기본 크기는 80칸이고, Windows Terminal은 120칸이다 ([GNOME Terminal 설정 스키마](https://gitlab.gnome.org/GNOME/gnome-terminal/-/raw/master/src/org.gnome.Terminal.gschema.xml), [Windows Terminal](https://learn.microsoft.com/en-us/windows/terminal/customize-settings/startup)). 개발자가 실제로 쓰는 폭을 조사한 자료는 찾지 못했다. 이 실험의 폭 조건 100칸은 80칸보다 넓다. 그래서 조건을 통과한 표도 80칸 터미널에서는 모양이 바뀔 수 있다.

## 문헌은 조건을 건 허용을 가리킨다

문헌 조사는 읽기 연구, 작성 지침, 공급사 지침, 판정 모델의 편향 연구, 터미널 자료를 다뤘다. 여기에는 이 문서의 논증에 쓰는 자료만 남겼다. 수치와 인용은 2026-10-19에 출처를 열어 확인했다.

### 여러 항목을 견주는 내용에서 표는 사람의 이해를 높였다

가장 강한 근거는 Brick 외(2020)의 사전 등록 무작위 실험이다 ([Brick 외 2020](https://doi.org/10.1098/rsos.190876)). 영국 성인 2,305명이 의료 선택지의 이득과 위해를 표나 줄글로 읽었다. 줄글에는 표의 내용을 모두 담았다. 이해 정답률은 표 79.6%, 줄글 69.7%였다(d=0.39). 하지만 가상의 치료 결정과 신뢰는 형식에 따라 달라지지 않았다.

표가 늘 이기지는 않았다. Tait 외(2010b)는 부모 4,685명의 온라인 실험에서 요지 이해가 표 62.9%, 줄글 61.3%로 같다고 보고했다 ([Tait 외 2010b](https://pmc.ncbi.nlm.nih.gov/articles/PMC2915576/)). 화면 낭독기를 쓰는 맹인 21명의 실험에서 표 마크업은 두 조건을 함께 맞추는 찾기 시간을 265.9초에서 146.9초로 줄였다 ([Williams 외 2019](https://doi.org/10.1145/3342282)). 하지만 값 하나를 찾는 과제에서는 차이가 없었다(119.2초 대 114.6초). 이 실험의 비교 대상은 줄글이 아니라 격자 배치였다.

원인과 이유를 표와 줄글로 견준 통제 실험은 찾지 못했다. 가까운 신호는 간접 근거다. 환율표 실험은 "Juxtaposition of the items was more easily achieved than a synthesis."라고 보고했다 ([Wright & Fox 1972](https://doi.org/10.1080/00140137208924422)). 항목을 나란히 놓기는 쉬웠지만 엮어서 결론을 내기는 어려웠다는 뜻이다. 이 결과는 이 실험에서 Opus가 이해에서 표 없는 답을 고른 이유와 같은 쪽을 가리킨다.

LLM 답변의 표를 사람에게 보인 연구는 작다. STRUCTSUM에서는 LLM이 만든 표 요약을 쓰면 특정 질문의 답을 찾는 시간이 줄글보다 42.9% 줄었다 ([STRUCTSUM](https://arxiv.org/abs/2401.06837)). 참가자는 12명이었다. 채팅 답변의 표와 줄글을 비교 과제로 견준 연구는 찾지 못했다. 한국어 독자에게 표와 줄글을 견준 연구도 찾지 못했다.

### 작성 지침은 표를 막지 않고 조건을 건다

확인한 영어권 지침 열세 곳 가운데 표를 막은 곳은 없다. 열세 곳은 정부 기관 다섯 곳, 표준 단체 한 곳, 기업 일곱 곳의 지침이다. 정부 기관은 [GOV.UK](https://guidance.publishing.service.gov.uk/formatting-content/text-formatting/tables/), [미국 연방 쉬운 글 지침](https://github.com/GSA/plainlanguage.gov/blob/main/_pages/guidelines/design/use-tables-to-make-complex-material-easier-to-understand.md), [NHS](https://service-manual.nhs.uk/design-system/components/table), [USWDS](https://designsystem.digital.gov/components/table/), [Canada.ca](https://design.canada.ca/style-guide/)이고, 표준 단체는 [W3C WAI](https://www.w3.org/WAI/tutorials/tables/)다. 기업은 [Google](https://developers.google.com/style/tables), [Microsoft](https://learn.microsoft.com/en-us/style-guide/scannable-content/tables), [Apple](https://support.apple.com/guide/applestyleguide/t-apsg841c3645/web), [Splunk](https://help.splunk.com/en/splunk-style-guide/tables), [GitLab](https://docs.gitlab.com/development/documentation/styleguide/#tables), [Red Hat](https://redhat-documentation.github.io/supplementary-style-guide/), [IBM Carbon](https://carbondesignsystem.com/components/data-table/usage/)이다.

조건은 거의 같다. 항목이 여럿이고 항목마다 같은 속성이 둘 이상인 자료에만 표를 쓴다. Google은 "Use tables only to present two-dimensional data"라고 쓴다 ([Google 개발자 문서 스타일 가이드](https://developers.google.com/style/tables)). GOV.UK는 머리글을 포함해 2열 3행보다 작은 표는 일반 글로 쓸 수 있다고 한다 ([GOV.UK publishing guidance](https://guidance.publishing.service.gov.uk/formatting-content/text-formatting/tables/)).

셀은 짧게 쓰라는 조건도 겹친다. Microsoft는 셀을 "ideally one line"으로 쓰라고 한다 ([Microsoft Writing Style Guide](https://learn.microsoft.com/en-us/style-guide/scannable-content/tables)). USWDS는 "Table cell content should be brief and scannable."이라고 한다 ([USWDS Table](https://designsystem.digital.gov/components/table/)). NN/g는 비교표에서 "Whenever possible, avoid full sentences."라고 조언한다 ([NN/g Comparison Tables](https://www.nngroup.com/articles/comparison-tables/)). 좁은 화면을 다룬 지침은 더 조심스럽다. Microsoft는 "Tables with more than a few narrow columns might be hard to read."라고 쓴다 ([Microsoft Responsive content](https://learn.microsoft.com/en-us/style-guide/responsive-content/)).

한국 공공 지침도 표를 남긴다. 행정안전부의 'AI 친화적 보고서' 원칙은 "표·그림은 상단에 제목을 표기하고 번호 등으로 순서 표시, 셀은 단순하게 병합"이다 ([행정안전부 2026-08 보도자료](https://www.mois.go.kr/frt/bbs/type010/commonSelectBoardArticle.do?bbsId=BBSMSTR_000000000008&nttId=128940)). 근거는 AI가 표를 읽는 능력과 직원 의견이고, 사람 독자의 이해를 잰 수치는 없다. 국립국어원의 2021년 지침은 "도표나 사진 등의 보조 자료도 적절히 활용한다"라고 권한다 ([국립국어원 2021](https://www.korean.go.kr/front/reportData/reportDataView.do?mn_id=45&searchOrder=&report_seq=1122&pageIndex=1)).

현행 금지는 독자 실험에서 나오지 않았다. SimpleEnglish 2.0.1은 답변의 목록 항목을 문장 수 상한에 세게 바꾸면서 헤더, 목록, 굵은 글씨, 표를 함께 막았다 ([SimpleEnglish d2a51b7](https://github.com/AminBlg/SimpleEnglish/commit/d2a51b7bd4b85423fa8cf33ac0e1b47887952663)). SimpleKorean은 이 금지를 물려받았다. ASD-STE100의 공개 페이지에서도 표 규칙은 찾지 못했다 ([About STE](https://www.asd-ste100.org/about_STE.html)).

### 공급사는 비교에 표를 권하고, 판정 모델은 서식 쪽으로 기운다

OpenAI의 GPT-5.2 프롬프트 가이드는 표를 쓸 때를 가장 구체적으로 적었다 ([GPT-5.2 prompting guide](https://github.com/openai/openai-cookbook/blob/main/examples/gpt-5/gpt-5-2_prompting_guide.ipynb)). "Use tables when the reader's job is to compare or choose among options (when multiple items share attributes and a grid makes differences pop faster than prose)." Anthropic 문서는 표를 따로 다루지 않는다. 대신 Fable 5.1 가이드는 서식 금지 문구를 "a rule that says when specific formatting is appropriate"로 바꾸라고 권한다 ([Prompting Claude Fable 5.1](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1)).

공급사의 제품도 셀 길이를 조건으로 다룬다. Claude Code 2.1.268은 Slack용 Claude Tag의 답을 이렇게 바꿨다 ([Claude Code CHANGELOG](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md)). "sentence-length comparisons now come as lists instead of wide tables that scroll sideways, and long table cells wrap". 문장 길이의 셀을 넣은 표를 목록으로 돌린 것이다.

판정 모델이 마크다운 있는 답을 편애한다는 근거는 강하다. 서식 하나만 다른 답 쌍에서 GPT-4 Turbo 판정 모델의 승률은 굵은 글씨가 있는 답 89.5%, 목록이 있는 답 75.75%였다 ([Zhang 외 2024](https://arxiv.org/abs/2409.11704)). 이 승률은 무승부를 반 승으로 셌다. 내용이 같은 마크다운 답과 평문 답 30쌍에서 Claude Sonnet 4는 마크다운 쪽을 0.83 비율로 골랐다 ([Soumik 2026](https://arxiv.org/abs/2604.23178)). 사람 두 명은 0.57이었다. 하지만 표만 따로 잰 연구는 찾지 못했다. Soumik(2026)도 "tables in isolation"을 재지 않았다고 밝혔다.

이 편향은 실험을 읽는 방법을 정한다. 순서 바꾸기는 위치 편향을, 길이 통제는 길이 편향을 줄인다. 하지만 서식 편향은 줄이지 못한다. 그래서 표 정책의 찾기 승리에는 서식 편향이 섞였을 수 있다. 반대로 이해와 전체 선호에서 표 정책이 이기지 못한 결과는 이 편향으로 설명되지 않는다. 편향은 표 쪽으로 기울기 때문이다.

## 판단: 표의 쓸모는 확인했지만 이 실험으로는 규칙을 바꾸지 않는다

금지를 유지하는 근거는 미리 정한 조건이다. 허용은 표가 맞지 않는 질문에도 표를 쓰고, 표가 넓었다. 조건부 허용은 그 두 문제를 풀었지만, 전체 선호에서 금지를 이기지 못했다. 두 정책 모두 Opus의 이해 판정에서 졌다. 조건을 판정 뒤에 고치면 실험의 의미가 사라지므로 결과를 그대로 받는다.

문헌은 금지를 지지하지 않는다. 비교 내용에서 표가 이해를 높인 실험이 있고, 확인한 지침은 모두 조건을 걸어 표를 허용한다. 이 실험의 조건부 허용도 지침이 거는 조건을 지켰다. 표를 비교 질문에만 썼고, 셀은 짧았고, 표는 100칸 안에 들었다. 그래서 금지를 유지하는 근거는 표 자체보다 이 실험의 두 문구가 낸 결과다. 허용 문구는 표를 맞지 않는 곳에도 넓게 쓰게 했다. 두 문구 모두 Opus의 이해 판정에서 졌고, 조건부 허용은 전체 선호의 이득을 보이지 못했다.

실험과 문헌이 갈리는 곳은 사람 독자다. 판정 모델은 표 있는 답을 찾기에서 고르고 이해에서는 고르지 않았다. 사람 독자에게도 그런지는 모델 판정으로 알 수 없다. 그래서 다음 판단은 개발자 과제 시험으로 내려야 한다. 시험의 설계는 다음과 같다:

1. 여러 개발자가 80칸 터미널에서 T 질문의 답을 읽는다. 답은 금지와 조건부 허용의 답을 무작위로 나눠 준다.
2. 답에서 값 하나를 찾는 시간과 정답률을 잰다. 이유를 묻는 질문의 정답률도 잰다.
3. 채택 조건은 시험 전에 정한다. 예를 들어 찾기 시간이 줄고 이유 정답률이 떨어지지 않아야 한다.

시험할 후보는 조건부 허용 문구다. 이 실험에서 과용과 폭의 문제를 일으키지 않은 문구이기 때문이다. 대화형 화면을 다룬 지침은 열 수도 줄이게 한다. 예를 들어 2023년에 폐지된 Google Assistant의 표 카드는 열과 행을 "up to 3 each"로 정했다 ([Google Assistant rich responses](https://developers.google.com/assistant/conversational/prompts-rich)). 그래서 시험 전에 열을 세 개 이하로 두는 문장을 더할지도 정해야 한다. 이 실험의 조건부 허용 표는 열 수 중앙값이 3이었고, 가장 넓은 표도 82칸이었다.

## 한계

판정은 사람이 아니라 모델이 했다. 판정 모델은 마크다운 있는 답과 긴 답 쪽으로 기운다. Opus는 같은 회사의 모델이 쓴 답을 판정했다. Jev에게는 한국어 답을 영어 질문으로 물었고, Jev의 이해 판정은 같은 정책 비교에서도 크게 흔들렸다.

채택 조건의 문턱값은 관례로 정했다. 같은 정책 비교의 전체 선호에서도 두 판정 모델은 모두 4쌍 차이로 한쪽을 골랐다. 그래서 전체 선호의 문턱값 3쌍은 이 흔들림보다 작다. 작은 이득이나 손해는 이 실험으로 가를 수 없다.

판정의 약 30%는 두 순서에서 같은 자리를 골랐다. Opus는 420번 가운데 125번, Jev는 136번이었고, 대부분 두 번 모두 B를 골랐다. 이런 판정은 무승부로 셌다. 그래서 고정된 문턱값 아래에서는 결과가 현행 쪽으로 밀린다.

답은 `claude-sonnet-5-5` 하나가 effort low로 썼고, 판정도 그 답만 했다. 질문 20개를 두 번씩 돌린 작은 표본이다. T와 N의 구분은 질문을 만든 사람이 정했다. 허용이 N에 쓴 표 가운데 일부는 원인과 증상을 나란히 놓은 표처럼 비교로 볼 수 있다.

터미널은 Claude Code에서 표 세 개, Codex CLI에서 표 두 개를 두 폭으로만 시험했다. Claude Code가 격자와 세로 배치를 고르는 기준은 공개되지 않았다. 한국어 독자에게 표를 시험한 자료는 없다.
