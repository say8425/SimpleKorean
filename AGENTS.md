# 에이전트 지침

이 레포지토리에서 한국어 글을 쓰거나 고치면 `simple-korean` 스킬의 규칙을 따르세요. 스킬을 설치했어도 작업 트리(지금 체크아웃한 파일)의 [`skills/simple-korean/SKILL.md`](skills/simple-korean/SKILL.md)를 따르세요. 이 레포지토리의 PR은 규칙 자체를 자주 바꾸기 때문입니다. 글을 쓰기 전에 그 `SKILL.md`를 읽으세요.

규칙을 적용하는 글은 레포지토리의 모든 한국어 마크다운 문서, 커밋 메시지, PR 제목과 본문입니다. `docs/`의 번역 README는 한국어 규칙의 대상이 아닙니다. 번역 README는 같은 원칙(짧은 문장, 능동태, 과장 없는 사실)으로 쓰세요. 영어판은 SimpleEnglish 규칙을 따르세요.

## 문체

커밋 제목과 PR 제목은 `fix: 설정 파일의 지정형을 20자로 제한한다`처럼 `<유형>: <해라체 문장>`으로 쓰세요. 유형은 feat, fix, perf, refactor, docs, test, chore, ci 가운데 하나입니다. 이 형식은 `references/use-cases.md`의 커밋 제목 형식보다 앞섭니다. 커밋 본문도 해라체로 쓰세요. 기존 문서를 고칠 때는 그 문서의 문체를 따르세요.

## 고치지 않는 글

글을 규칙에 맞게 고칠 때 다음은 바꾸지 마세요:

- 코드, 명령, 식별자
- 원본 출력의 인용
- `<!-- simple-korean: off -->`와 `<!-- simple-korean: on -->` 사이의 글

이 표지는 일부러 틀린 예시와 원본 출력의 인용에만 쓰세요. 린터를 피하려고 쓰지 마세요.

README의 `<!-- benchmark:start -->`와 `<!-- example:start -->` 블록은 생성기(원본 출력에서 README 블록을 만드는 스크립트)가 씁니다. 이 블록을 손으로 고치면 `evals/check_numbers.py`가 실패합니다. 블록을 바꾸려면 `evals/readme_i18n.py`의 문장 틀을 고치세요. 그다음 `evals/report.py <결과 디렉터리> --readme`와 `evals/make_examples.py <결과 디렉터리> --readme`를 실행하세요.

## 번역 README

한국어 `README.md`를 고치면 `docs/`의 번역 README 네 개도 같은 내용과 구조로 고치세요.

## 확인

글을 고친 뒤 고친 파일을 린터(규칙 위반을 세는 스크립트)로 확인하세요. 절차를 담은 문서에는 `--type procedural`을 붙이세요:

```bash
python3 evals/ko_lint.py --gate=warning <파일>
```

린터가 오류나 경고를 내면 고친 뒤 다시 실행하세요. PR 제목은 다음 명령으로 확인하세요:

```bash
PR_TITLE='<제목>' python3 evals/check_pr_title.py
```

린터는 정해진 문자열 패턴만 찾습니다. 그래서 용어 풀이 누락이나 한 문장에 든 두 동작은 잡지 못합니다. 린터를 통과한 뒤에도 `SKILL.md`의 "내기 전 자가 점검"을 하세요. 새로 쓴 문장마다 길이, 동작이나 명제가 하나인지, 처음 쓴 용어를 풀이했는지 확인하세요.
