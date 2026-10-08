# 변경 기록

항목마다 버전, 날짜, 측정한 효과를 적습니다.

## 1.0.0, 2026-10-08

- 처음 공개합니다. [AminBlg/SimpleEnglish](https://github.com/AminBlg/SimpleEnglish) v2.1.1(`a6fcb4f`)의 구조를 따르고, 규칙, 단어 목록, 측정 과제는 한국어에 맞게 새로 썼습니다.
- 들어 있는 것은 SKILL.md와 레퍼런스 네 개, 출력 스타일, 시스템 프롬프트, 세션 시작 훅, 파일 점검 훅, 답변 점검 훅, 한국어 린터, 표기 단어 목록, 한국어 슬롭 어휘 목록, 벤치마크입니다.
- 측정 결과는 [`evals/results/2026-10-08/RESULTS.md`](evals/results/2026-10-08/RESULTS.md)에 있습니다.
- 압력 시험 결과는 [`evals/pressure-tests.md`](evals/pressure-tests.md)의 기록 절에 있습니다.

### 보정

보정 기록은 [`evals/calibration/RECORD.md`](evals/calibration/RECORD.md)에 있습니다.

- 문장 길이 상한은 절차문 15어절, 설명문 20어절 그대로입니다. 규칙을 지킨 예문은 모두 상한 안이었습니다.
- 엄격: 접속어: 판정한 4건 가운데 거짓 일치 1건을 찾아 1건을 고쳤습니다. 원인: '-나다' 동사 어간 뒤 보조 용언(어긋나 있다).
