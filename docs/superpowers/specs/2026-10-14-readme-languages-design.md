# README 다국어판과 릴리스 자동화 설계

- 날짜: 2026-10-14
- 상태: 설계 확정, 구현 계획 전
- 앞선 설계: [`2026-10-08-simple-korean-design.md`](2026-10-08-simple-korean-design.md). 이 설계는 그 12절의 "맨 위에 영어 소개를 한 문단 둔다"를 영어판 README로 바꾼다. 13절의 CI와 14절의 공개 절차에는 릴리스 단계를 더한다.
- 관련 PR: [#1](https://github.com/say8425/SimpleKorean/pull/1) `ci: python39 작업을 ubuntu-24.04에 고정한다`

## 1. 목표

두 가지를 한다.

1. README를 영어, 일본어, 중국어(간체), 스페인어로 옮긴다. 한국어를 읽지 못하는 독자도 이 스킬이 무엇을 하고, 무엇을 어떻게 쟀는지 읽을 수 있게 한다.
2. 버전 올리기, 변경 기록, 태그, GitHub Release를 release-please로 자동화한다.

성공 기준:

1. 다섯 README의 벤치마크 블록과 보기 블록이 원본 출력에서 다시 만든 글과 글자 하나까지 같다. CI가 푸시마다 대조한다.
2. 한국어판에 절이나 레포 파일 링크를 더하고 번역판을 고치지 않으면 CI가 실패한다.
3. `feat`, `fix`, `perf` 커밋이 `main`에 들어가면 릴리스 PR이 열린다. 그 PR을 병합하면 모든 버전 문자열이 함께 오르고, 태그와 GitHub Release가 생긴다.
4. 커밋 규칙이나 문서 관문을 어기는 커밋 제목은 PR 단계에서 걸린다.

## 2. 결정 기록

| 질문 | 고른 것 | 버린 것과 이유 |
|---|---|---|
| 번역판의 측정 수치 | 생성기가 언어별 문장 틀로 다섯 README의 블록을 쓰고, CI가 다섯 블록을 글자 하나까지 대조한다 | 사람이 번역하고 숫자만 대조하면 숫자 둘레의 문장이 낡아도 못 잡는다. 언어마다 숫자 순서가 달라 대조도 느슨하다. 번역판에서 수치를 빼면 외국어 독자가 핵심 근거를 못 본다 |
| 파일 위치 | `README.md`(한국어 원본)와 `docs/README.<언어>.md` | diffdeck과 같은 배치다 |
| 중국어 | 간체 | diffdeck과 같다 |
| 버전 배지 | GitHub Release를 읽는 동적 배지 | 정적 배지에 버전 표시를 붙이면 릴리스 PR마다 README 다섯 개가 바뀐다 |
| release-type | `simple`과 extra-files | `node`는 버전만 담은 package.json을 새로 만들어야 하고, 레포가 npm 패키지처럼 보인다 |
| `version.txt` | 만들지 않는다 | `simple`은 이 파일이 있을 때만 올리고, 없으면 만들지 않는다. 버전은 extra-files가 담는다 |
| CHANGELOG 절 이름 | 한국어(기능, 고친 것, 성능) | 기본 영어 이름은 한국어 변경 기록과 섞인다 |
| 병합 방식 | squash만 쓰고, 커밋 제목은 PR 제목으로 한다 | 이렇게 하면 PR 제목 하나만 검사하면 된다 |
| PR 제목 검사의 위치 | 별도 워크플로 `pr-title.yml` | `check.yml`에 넣으면 제목을 고쳐도 다시 돌지 않는다. 실패한 실행을 다시 돌려도 처음 이벤트의 제목을 읽는다 |
| 측정 기록 검사 | 마지막 릴리스보다 늦은 측정은 CHANGELOG 검사를 건너뛴다 | 지금 규칙대로면 다시 잰 PR이 릴리스 전까지 CI를 통과하지 못한다(5.6절) |
| 릴리스 PR의 CI | 돌리지 않고, 별도 토큰도 두지 않는다 | 릴리스 PR은 버전 문자열과 CHANGELOG만 바꾸고, 병합 뒤 `main`에서 CI가 다시 돈다 |

## 3. README 구성

### 3.1 파일

| 파일 | 언어 |
|---|---|
| `README.md` | 한국어. 원본이고, 레포 첫 화면에 뜬다 |
| `docs/README.en.md` | 영어 |
| `docs/README.ja.md` | 일본어 |
| `docs/README.zh.md` | 중국어 간체 |
| `docs/README.es.md` | 스페인어. 지역색이 없는 표준 스페인어로 쓴다 |

### 3.2 언어 선택 줄

다섯 파일 모두 첫머리 문구 바로 아래, 배지 줄 위에 언어 선택 줄을 둔다. 앞뒤 블록이 가운데 정렬한 `<p>`라서 이 줄도 가운데 정렬한 HTML로 쓴다. 언어 순서는 한국어, English, 日本語, 中文, Español이다. 현재 언어는 링크 없이 쓴다.

```html
<p align="center">
  한국어 | <a href="docs/README.en.md">English</a> | <a href="docs/README.ja.md">日本語</a> | <a href="docs/README.zh.md">中文</a> | <a href="docs/README.es.md">Español</a>
</p>
```

번역판의 링크는 `../README.md`와 같은 폴더의 `README.<언어>.md`를 가리킨다. 이 블록은 `evals/readme_i18n.py`의 `language_line(lang)`이 만들고, 구조 검사가 각 README에 그대로 있는지 본다(4.4절).

한국어 README 첫머리의 영어 문단("The rest of this README is in Korean")은 지운다. 영어판이 그 역할을 맡는다.

### 3.3 링크

- 번역판은 `docs/`에 있으므로 레포 파일 링크 앞에 `../`를 붙인다. 마크다운 링크와 HTML의 `href`, `src`에 모두 붙인다. 예: `../skills/simple-korean/SKILL.md`, `<a href="../LICENSE">`.
- 외부 링크는 그대로 둔다.
- 같은 문서 안의 앵커 링크는 그 언어의 제목을 가리킨다. 지금 README에는 앵커 링크가 없다.

### 3.4 번역하는 것과 그대로 두는 것

번역하는 것: 설명 문장, 제목, 표의 머리글, 규칙 설명, FAQ.

그대로 두는 것:

- 보기 블록의 모델 출력 두 개. 한국어 출력이 이 스킬의 결과물이므로 원문 그대로 싣는다. 생성기가 쓰는 설명 문장만 번역한다. 보기 절의 소개 문장에는 아래 답변이 한국어라고 적는다.
- 규칙 표의 한국어 예시("-면", "되어지다", "백업 확인 필요")와 표기 정책 표의 한국어 형태(디렉터리, 레포지토리). 한국어 원문을 두고, 그 언어로 짧은 풀이를 붙인다.
- 명령어, 코드, JSON 예시, 파일 경로, 백틱으로 감싼 모델 이름.

### 3.5 문체와 검토

- 한국어 README는 지금처럼 `ko_lint.py --gate=warning`을 통과해야 한다.
- 번역판에는 린터가 없다. 같은 원칙(짧은 문장, 능동태, 과장 없는 사실)으로 쓴다. 영어판은 SimpleEnglish 규칙을 따른다.
- 번역은 Claude가 쓰고, 원어민 검토 없이 공개한다. 그래서 번역판마다 끝에 그 언어로 한 줄을 둔다. 뜻은 "이 번역은 원어민이 검토하지 않았습니다. 오류는 이슈로 알려 주세요"이고, 이슈 목록을 링크한다.

### 3.6 동기화

- 한국어 README가 원본이다. 한국어판을 바꾸는 PR이 번역판도 함께 고친다.
- 생성 블록은 생성기가 다섯 파일에 함께 쓴다(4.2절).
- 생성 블록 밖의 구조는 구조 검사가 지킨다(4.4절). 문장 내용은 검사하지 않는다.

## 4. 생성 블록과 검사

### 4.1 언어 표 `evals/readme_i18n.py`

새 파일에 언어별 정보를 모은다.

- 언어 목록은 `ko`, `en`, `ja`, `zh`, `es` 순서다. 언어마다 README 경로, 언어 선택 줄의 이름, 링크 앞붙이(`""` 또는 `"../"`)를 둔다.
- 벤치마크 블록의 문장 틀: 답변 측정 소개, 결과 요약(감소율, 판정의 승·무·패), 문서 측정 소개, 두 표의 머리글, 조건 이름(스킬 없음, SimpleKorean, 기본 모드, 엄격 모드), "측정 안 함", 가장 긴 문장 칸의 단위, RESULTS.md 링크 문장.
- 보기 블록의 문장 틀: 두 출력의 설명 문장, 문서 예시 링크 문장.
- 규칙 블록 글자 수 문구. 설치 절의 문장이 이 문구를 그대로 담는다.

| 언어 | 글자 수 문구 | 가장 긴 문장 칸 |
|---|---|---|
| ko | 규칙 블록 2,271자 | 18어절 |
| en | rule block of 2,271 characters | 18 eojeol |
| ja | 2,271文字のルールブロック | 18語節 |
| zh | 2,271 个字符的规则块 | 18 个语节 |
| es | bloque de reglas de 2271 caracteres | 18 eojeol |

숫자 표기:

- ko, en, ja, zh: 천 단위마다 쉼표를 둔다(2,271). 퍼센트는 붙여 쓴다(100%). 소수점은 점이다.
- es: RAE 관례를 따른다. 네 자리 수에는 구분 기호를 쓰지 않는다(2271). 다섯 자리부터는 세 자리마다 줄바꿈 없는 공백(U+00A0)을 둔다(12 345). 퍼센트 앞에도 줄바꿈 없는 공백을 둔다(100 %). 소수점은 RAE가 권하는 점을 쓴다(95.0 %).

그 밖의 규칙:

- "어절"은 en과 es에서 eojeol, ja에서 語節, zh에서 语节로 쓴다. 번역판은 벤치마크 절의 소개 문단에서 이 단위를 한 번 풀이한다.
- 조건 이름은 번역판의 "모드" 절에서 쓰는 이름과 같게 한다.
- 한국어 문장 틀은 지금 코드의 문장을 그대로 옮긴다. 그래서 한국어 README의 블록은 한 글자도 바뀌지 않는다.

### 4.2 생성기

- `report.readme_block(results_dir, scenarios, lang="ko")`와 `make_examples.readme_example(results_dir, lang="ko")`가 언어 인자를 받는다. 기본값이 `ko`라서 지금 호출은 그대로 돈다.
- 블록 안의 레포 링크 대상에는 그 언어의 링크 앞붙이를 붙인다. 링크 글자(예: `` `evals/results/2026-10-08/RESULTS.md` ``)는 레포 기준 경로 그대로 둔다.
- `report.py <결과 디렉터리> --readme`와 `make_examples.py <결과 디렉터리> --readme`는 다섯 README의 블록을 모두 고쳐 쓴다. 블록 표시가 없는 README가 있으면 그 파일 이름을 밝히고 멈춘다.
- 블록 표시 `<!-- benchmark:start evals/results/2026-10-08 -->`의 결과 경로와 `<!-- source: ... -->`의 경로는 레포 기준이고, 다섯 파일에서 같다.
- 인용한 모델 출력은 다섯 파일 모두 한국어 원문이다.
- `RESULTS.md`와 `examples/before-after.md`는 지금처럼 한국어로만 만든다.

### 4.3 수치 검증 `check_numbers.py`

README 다섯 개마다 확인하는 것:

- 벤치마크 블록이 그 언어의 `readme_block`과 같다.
- 보기 블록 전체가 그 언어의 `readme_example`과 같다. 지금은 인용한 출력만 대조하고 설명 문장은 대조하지 않는다. 결과 디렉터리는 같은 README의 벤치마크 블록 표시에서 읽는다.
- 인용한 출력이 원본 파일과 같다(지금 하는 검사).
- 작성 모델과 판정 모델의 이름이 백틱으로 있다(지금 하는 검사).
- 그 언어의 규칙 블록 글자 수 문구가 있고, 숫자가 실제 길이와 같다.

한 번만 확인하는 것: RESULTS.md, CHANGELOG의 측정 기록(5.6절), 보정 기록, 규칙 블록 두 벌, SKILL.md 호출 문구, 버전 대조(5.3절).

### 4.4 구조 검사

`check_numbers.py`에 구조 검사를 더한다. 번역판 네 개를 한국어판과 대조한다.

- 제목(`#`부터 `######`까지)의 수준 순서가 같다. 코드 블록과 인용 블록 안의 줄은 세지 않는다. 지금은 `##`가 10개다.
- 레포 파일 링크(마크다운 링크와 HTML의 `href`, `src`)의 대상 목록이 순서까지 같다. 번역판은 `../`를 떼고 비교한다. 외부 링크, 앵커, 언어 선택 줄은 빼고 센다. 링크한 파일이 실제로 있는지도 본다.
- 언어 선택 줄이 그 언어의 `language_line(lang)`과 같은 블록으로 한 번 있다. 한국어판에도 이 검사를 한다.
- 벤치마크 블록 표시와 보기 블록 표시가 각각 한 번 있다.

이 검사는 문장 내용을 보지 않는다. 한국어판에 절이나 링크를 더하고 번역판을 고치지 않으면 CI가 실패한다.

### 4.5 린터 관문

`check.yml`의 문서 관문은 지금처럼 한국어 `README.md`만 검사한다. 번역판은 관문에 넣지 않는다.

### 4.6 한국어로만 두는 문서

`examples/before-after.md`, `RESULTS.md`, `CHANGELOG.md`, SKILL.md와 레퍼런스, 훅 README는 한국어로만 둔다. 번역판은 이 파일들을 그대로 링크한다.

### 4.7 시험

- 다섯 언어 모두 두 블록을 만든다. 한국어 블록은 지금 README의 블록과 같다.
- 숫자 표기: es는 2271, 12 345, 100 %로 쓰고, 다른 언어는 2,271과 100%로 쓴다.
- 구조 검사가 빠진 제목, 깨진 링크, 순서가 틀린 언어 선택 줄, 두 번 나온 블록 표시를 잡는다.
- 레포 전체로 `check_numbers.py`를 돌리면 통과한다.

## 5. 릴리스

### 5.1 워크플로 `.github/workflows/release.yml`

```yaml
name: release
on:
  push:
    branches: [main]
  workflow_dispatch:
permissions:
  contents: write
  issues: write
  pull-requests: write
jobs:
  release-please:
    runs-on: ubuntu-latest
    steps:
      - uses: googleapis/release-please-action@v5
        with:
          config-file: release-please-config.json
          manifest-file: .release-please-manifest.json
```

- `main`에 push될 때마다 돈다. 릴리스할 커밋이 쌓이면 릴리스 PR을 열거나 고친다. 그 PR을 병합하면 태그(`v1.0.1` 형식)와 GitHub Release를 만든다.
- 권한 세 가지는 release-please-action README가 요구하는 그대로다. `workflow_dispatch`는 실패한 실행을 다시 돌릴 때 쓴다.
- 릴리스 PR은 `GITHUB_TOKEN`이 만들므로 그 PR에서는 다른 워크플로가 돌지 않는다. 별도 토큰은 두지 않는다. 릴리스 PR은 버전 문자열과 CHANGELOG만 바꾸고, 병합 뒤 `main`에서 CI가 다시 돈다.

### 5.2 설정 파일

`release-please-config.json`:

```json
{
  "$schema": "https://raw.githubusercontent.com/googleapis/release-please/main/schemas/config.json",
  "include-component-in-tag": false,
  "changelog-sections": [
    {"type": "feat", "section": "기능"},
    {"type": "fix", "section": "고친 것"},
    {"type": "perf", "section": "성능"},
    {"type": "refactor", "section": "리팩터링", "hidden": true},
    {"type": "docs", "section": "문서", "hidden": true},
    {"type": "test", "section": "시험", "hidden": true},
    {"type": "chore", "section": "기타", "hidden": true},
    {"type": "ci", "section": "CI", "hidden": true}
  ],
  "packages": {
    ".": {
      "release-type": "simple",
      "extra-files": [
        {"type": "json", "path": ".claude-plugin/plugin.json", "jsonpath": "$.version"},
        {"type": "json", "path": ".claude-plugin/marketplace.json", "jsonpath": "$.plugins[0].version"},
        {"type": "json", "path": ".codex-plugin/plugin.json", "jsonpath": "$.version"},
        "skills/simple-korean/SKILL.md"
      ]
    }
  }
}
```

`.release-please-manifest.json`은 `{".": "1.0.0"}`으로 시작한다.

- 태그에 컴포넌트 이름을 넣지 않는다. 그래서 태그 형식이 지금 태그 `v1.0.0`과 같다.
- 릴리스 PR 제목은 release-please 기본값(`chore(main): release 1.0.1`)을 쓴다. 이 PR에서는 PR 제목 검사가 돌지 않는다(5.1절).
- `feat`는 부 버전을, `fix`와 `perf`는 수 버전을 올린다. 숨긴 유형만 쌓이면 release-please는 사용자에게 보이는 커밋이 없다고 보고 릴리스 PR을 만들지 않는다.

### 5.3 버전 문자열

release-please가 릴리스 PR에서 함께 올리는 곳:

- `.release-please-manifest.json`
- `.claude-plugin/plugin.json`과 `.codex-plugin/plugin.json`의 `$.version`
- `.claude-plugin/marketplace.json`의 `$.plugins[0].version`
- `skills/simple-korean/SKILL.md` frontmatter의 `metadata.version` 줄. 줄 끝에 `# x-release-please-version` 주석을 붙인다(`  version: "1.0.0" # x-release-please-version`). YAML 주석이라 스킬 로더는 이 주석을 무시한다. 이것은 6.2절에서 확인한다.
- `CHANGELOG.md`의 새 항목 제목

`check_numbers.py`의 버전 대조를 이렇게 바꾼다.

- README 배지를 대조에서 뺀다. 배지에 버전 문자열이 없어지기 때문이다(5.4절).
- `.release-please-manifest.json`을 대조에 넣는다.
- CHANGELOG 첫 항목은 `## 1.0.0, 2026-10-10`과 `## [1.0.1](...) (2026-10-20)` 두 형식을 모두 읽는다.

### 5.4 배지

다섯 README의 버전 배지를 GitHub Release를 읽는 동적 배지로 바꾼다.

```html
<a href="https://github.com/say8425/SimpleKorean/releases/latest"><img src="https://img.shields.io/github/v/release/say8425/SimpleKorean?label=version&style=flat" alt="version"></a>
```

- 링크는 SKILL.md 대신 최신 Release를 가리킨다.
- Release가 하나도 없으면 배지에 "no releases found"가 뜬다. 그래서 PR 2를 병합하기 전에 `v1.0.0` Release를 만든다(6.3절).

### 5.5 CHANGELOG

- release-please는 첫 버전 제목(`## 1.0.0, ...`) 앞에 새 항목을 넣는다. `# 변경 기록` 제목, 머리말, 1.0.0 항목은 그대로 남는다.
- 새 항목은 이런 모양이다.

  ```markdown
  ## [1.0.1](https://github.com/say8425/SimpleKorean/compare/v1.0.0...v1.0.1) (2026-10-20)

  ### 고친 것

  * 설정 파일의 지정형을 20자로 제한한다 ([#3](https://github.com/say8425/SimpleKorean/issues/3)) ([abc1234](https://github.com/say8425/SimpleKorean/commit/abc1234))
  ```

- CHANGELOG는 문서 관문에 남는다. 이 모양으로 흉내 낸 항목을 넣고 관문을 돌리면 경고 없이 통과한다. 각 줄이 링크로 끝나서 문체 혼용 검사는 이 줄의 문체를 가리지 않는다. 그래서 문장 자체는 PR 제목 검사가 미리 본다(5.7절).
- 머리말을 바꾼다. 지금은 "항목마다 버전, 날짜, 측정한 효과를 적습니다."이다. 바꾼 뒤에는 "항목마다 버전, 날짜, 바뀐 것을 적습니다. 측정 결과가 바뀌면 그 릴리스에 결과 경로를 적습니다."이다.

### 5.6 측정 기록과 CHANGELOG

지금 `check_numbers.py`는 CHANGELOG를 두 가지로 검사한다.

- README 벤치마크 블록이 가리키는 결과 경로(`evals/results/<날짜>`)가 CHANGELOG에 있다.
- 보정 기록 `RECORD.md`의 "CHANGELOG에 옮길 줄"이 CHANGELOG에 있다.

release-please를 쓰면 이 검사가 길을 막는다. 다시 잰 PR에는 그 결과를 실을 릴리스 항목이 아직 없다. 그래서 CHANGELOG에 줄을 넣을 곳이 없고, PR의 CI가 릴리스 전까지 실패한다.

규칙을 이렇게 바꾼다.

- 결과의 날짜(`meta.json`의 `date`)가 CHANGELOG 첫 항목의 날짜보다 늦으면, 아직 릴리스하지 않은 측정으로 보고 결과 경로 검사를 건너뛴다. 날짜가 같으면 릴리스한 측정으로 본다.
- 보정 기록도 같은 규칙을 따른다. 날짜는 `RECORD.md` 제목(`# 보정 기록 (2026-10-08)`)에서 읽는다.
- 새 결과나 보정을 싣는 릴리스에서는 릴리스 PR을 병합하기 직전에 그 항목에 결과 경로 줄과 보정 줄을 더한다. 릴리스 PR은 `main`이 바뀔 때마다 다시 만들어지므로, 병합 직전에 더한다.
- 이 줄을 잊으면 병합 뒤 `main`의 CI가 실패하고, 메시지가 더할 줄을 알려 준다. 그때 `docs:` 커밋으로 그 항목에 줄을 더한다.
- 지금은 결과와 보정이 모두 2026-10-08이고 1.0.0은 2026-10-10이다. 그래서 지금처럼 검사하고, 두 검사 모두 통과한다.
- `hits.py`의 설명 "CHANGELOG 1.0.0 항목의 보정 절에 그대로 옮길 줄"을 "그 보정을 싣는 릴리스 항목에 옮길 줄"로 고친다.

### 5.7 커밋 규칙과 PR 제목 검사

커밋 제목은 `<유형>: <한국어 해라체 한 문장>`으로 쓴다. 유형은 feat, fix, perf, refactor, docs, test, chore, ci다. 범위(`fix(hooks):`)와 `!`는 쓰지 않는다.

squash 병합만 쓰므로 PR 제목이 `main`의 커밋 제목이 되고, CHANGELOG의 한 줄이 된다. 그래서 PR 제목을 검사한다.

새 스크립트 `evals/check_pr_title.py`:

- 환경 변수 `PR_TITLE`을 읽는다. PR 제목은 외부 입력이므로 워크플로의 스크립트 안에 끼워 넣지 않고 환경 변수로 넘긴다.
- 형식이 `^(feat|fix|perf|refactor|docs|test|chore|ci): \S`인지 본다.
- 유형 뒤의 내용이 해라체인지 `ko_text.register()`로 본다. 린터 관문은 "README 번역 추가" 같은 명사형 제목과 "제한합니다" 같은 합쇼체 제목을 통과시킨다. 그래서 이 확인이 따로 있어야 한다.
- 내용을 린터로 검사한다. `--gate=warning`과 같은 기준으로 경고까지 없어야 한다.
- 실패하면 이유와 예시를 한국어로 출력하고 1로 끝난다.

새 워크플로 `.github/workflows/pr-title.yml`:

```yaml
name: pr-title
on:
  pull_request:
    types: [opened, edited, synchronize, reopened]
permissions:
  contents: read
jobs:
  title:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - uses: actions/setup-python@v7
        with: { python-version: "3.12" }
      - run: python3 evals/check_pr_title.py
        env:
          PR_TITLE: ${{ github.event.pull_request.title }}
```

- `edited`가 있으므로 제목을 고치면 검사가 다시 돈다.
- 릴리스 PR에서는 돌지 않는다(5.1절).
- 한국어 README의 기여 절에 이 규칙을 적는다. 예시 제목, 유형 목록, feat·fix·perf만 릴리스를 만든다는 점을 쓴다. 번역판의 기여 절에는 이 규칙에 더해, 한국어 제목을 쓰지 못하면 메인테이너가 병합 전에 고친다고 적는다.

### 5.8 레포 설정

PR 2를 병합하기 직전에 바꾼다(6.3절).

- Actions: "Allow GitHub Actions to create and approve pull requests"를 켠다. 워크플로 기본 권한은 `read`로 둔다. 쓰기 권한은 `release.yml`에만 준다.
- 병합: squash만 허용한다. merge commit과 rebase 병합은 끈다. squash 커밋 제목은 PR 제목(`PR_TITLE`)이고, 본문은 커밋 메시지 목록(`COMMIT_MESSAGES`)이다. 그래서 커밋의 `Co-Authored-By` 줄이 남는다. GitHub는 제목 끝에 ` (#번호)`를 붙이고, release-please는 이것을 PR 링크로 바꾼다.

### 5.9 1.0.0과 잇기

- `v1.0.0` 태그는 있지만 GitHub Release는 없다. release-please는 Release를 찾지 못하면 매니페스트의 버전으로 태그를 찾으므로, 이대로도 돈다.
- 배지가 Release를 읽으므로 `v1.0.0` Release를 먼저 만든다. 제목은 `v1.0.0`이고, 본문은 CHANGELOG의 1.0.0 항목이다. 상대 링크는 `https://github.com/say8425/SimpleKorean/blob/v1.0.0/...` 형식의 절대 링크로 바꾼다.

## 6. 공개 절차

### 6.1 PR 세 개

모두 squash로 병합한다.

| PR | 제목 | 담는 것 |
|---|---|---|
| 1 ([#1](https://github.com/say8425/SimpleKorean/pull/1)) | `ci: python39 작업을 ubuntu-24.04에 고정한다` | `python39` 러너 고정. 2026-10-19 전에 병합한다 |
| 2 | `ci: release-please로 릴리스 PR을 만든다` | 5장 전체(README는 한국어판의 배지와 기여 절만 바꾼다), 이 스펙과 구현 계획 |
| 3 | `docs: README를 영어, 일본어, 중국어, 스페인어로 옮긴다` | 3장과 4장 전체, 번역판 네 개 |

- PR 1은 2026-10-14에 열었다. CI가 통과했다. 임시 브랜치에서 두 작업을 `ubuntu-26.04` 러너로 돌려서, `check`는 통과하고 고정하지 않은 `python39`는 Python 3.9를 찾지 못해 실패하는 것을 확인했다.
- 세 PR의 유형(ci, docs)은 CHANGELOG에서 숨기는 유형이다. 병합해도 릴리스 PR이 생기지 않고, 플러그인 버전도 그대로다. 첫 릴리스 PR은 다음 `feat`, `fix`, `perf` 커밋에서 열린다.
- PR 2는 PR 1 뒤에, PR 3은 PR 2 뒤에 병합한다. PR 3의 번역판은 PR 2의 동적 배지와 기여 절을 옮긴다.

### 6.2 병합 전 확인

세 PR 모두 확인하는 것:

- CI가 통과한다. PR 2부터는 `pr-title`도 돈다.
- PR마다 코드 리뷰 스킬로 검토한다.

PR 2에서 확인하는 것:

- release-please CLI를 `--dry-run`으로 돌려서, 릴리스 PR이 만들 diff를 본다. 숨긴 유형의 커밋만 있으면 `--release-as`를 줘도 릴리스 PR이 생기지 않는다. 그래서 임시 브랜치에 빈 `fix:` 커밋 하나를 얹어서 돌리고, 끝나면 임시 브랜치를 지운다.
- dry-run 결과에서 확인하는 것:
  - CHANGELOG의 새 항목이 1.0.0 항목 앞에 들어간다.
  - 절 이름이 한국어다.
  - 5.3절의 버전 문자열이 모두 1.0.1이 되고, JSON 파일에서는 버전 줄만 바뀐다.
  - 태그 이름이 `v1.0.1`이다.
  - `version.txt`가 생기지 않는다.
  - 바뀐 CHANGELOG가 문서 관문을 통과한다.
- 주석을 붙인 SKILL.md를 Claude Code, Codex, skills CLI가 읽는지 본다. 로컬 체크아웃에서 설치해서 스킬이 목록에 뜨는지 본다.

PR 3에서 확인하는 것:

- GitHub의 브랜치 화면에서 다섯 README를 연다. 언어 링크, 배지, 표, 상대 링크를 본다.
- 한국어 README 첫머리의 바뀌기 전과 뒤, 번역판 네 개의 첫머리를 찍어서 PR 본문에 넣는다.

### 6.3 PR 2를 병합하기 직전의 레포 작업

1. `v1.0.0` GitHub Release를 만든다(5.9절).
2. Actions가 PR을 만들 수 있게 한다(5.8절).
3. 병합 방식을 squash만으로 정한다(5.8절).

### 6.4 병합 뒤 확인

- PR 2를 병합한 뒤 `main`에서 `release` 워크플로가 성공한다. 로그에는 `v1.0.0`을 찾았고, 사용자에게 보이는 커밋이 없어 건너뛰었다는 기록이 있다.
- 배지가 v1.0.0을 보인다. PR 3을 병합한 뒤에는 다섯 README 모두에서 본다.

### 6.5 역할

- Claude는 브랜치 push, PR 생성, 검사, 리뷰를 한다.
- PR 병합과 6.3절의 레포 작업 세 가지는 Claude가 결과를 보고하고 사용자의 확인을 받은 뒤에 한다.

## 7. 범위 밖

- SKILL.md, 레퍼런스, 규칙 블록, 출력 스타일, 예시, RESULTS.md, CHANGELOG, 훅 README의 번역
- 원어민 검토
- 번역 문장의 내용 대조. 구조만 검사한다
- 릴리스 노트의 번역
- 릴리스 PR에서 CI를 돌리기 위한 별도 토큰
- npm 같은 패키지 레지스트리 배포. skills CLI와 플러그인은 GitHub 레포를 바로 읽는다
- 범위가 있는 커밋 제목과 `!`(주 버전 올림). 주 버전이 필요해지면 그때 설계한다

## 8. 구현 중 확인할 것

- release-please의 실제 출력: 새 항목 제목의 형식, 한국어 절 이름, 태그 이름, JSON 파일의 서식 유지. PR 2의 dry-run으로 본다.
- release-please CLI는 버전을 고정해서 돌린다.
- skills CLI가 주석을 붙인 frontmatter를 읽는지.
- `gh api`로 바꾼 레포 설정 두 가지가 GitHub 화면에서도 그렇게 보이는지.
- 번역판의 표가 GitHub에서 깨지지 않는지. 전각 문자와 세로 막대가 섞인 칸을 본다.
