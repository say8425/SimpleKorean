# 에이전트 지침

이 레포지토리에서 한국어 글을 쓰거나 고치면 `simple-korean` 스킬의 규칙을 따르세요. 규칙 원문은 [`skills/simple-korean/SKILL.md`](skills/simple-korean/SKILL.md)에 있습니다. 스킬을 설치하지 않았으면 글을 쓰기 전에 `SKILL.md`를 읽으세요.

규칙을 적용하는 글은 다음과 같습니다:

- 마크다운 문서: README 다섯 언어판, `docs/`, `skills/`, `prompts/`, `src/hooks/README.md`, `evals/`의 문서
- 커밋 메시지, PR 제목과 본문
- 사용자에게 보내는 채팅 답변

커밋 메시지와 PR 제목은 해라체("-한다")로 쓰세요. 기존 문서를 고칠 때는 그 문서의 문체를 따르세요. 코드, 원본 출력의 인용, `<!-- simple-korean: off -->`와 `<!-- simple-korean: on -->` 사이의 글은 고치지 마세요.

한국어 README를 고치면 `docs/`의 번역 README 네 개도 같은 내용과 구조로 고치세요.

## 확인

글을 고친 뒤 고친 파일을 린터(규칙 위반을 세는 스크립트)로 확인하세요:

```bash
python3 evals/ko_lint.py --gate=warning <파일>
```

린터는 정해진 문자열 패턴만 찾습니다. 그래서 용어 풀이 누락이나 한 문장에 든 두 동작은 잡지 못합니다. 린터를 통과한 뒤에도 `SKILL.md`의 "내기 전 자가 점검"을 하세요. 새로 쓴 문장마다 규칙 1(문장 길이, 동작 하나)과 규칙 9(용어 풀이)를 확인하세요.
