# 외래어 표기 측정 자료

[`../../loanword-spelling-usage.md`](../../loanword-spelling-usage.md) 보고서의 원자료다. 2026-10-07~08에 같은 표기 목록과 같은 계수 규칙으로 셌다.

| 파일 | 내용 |
|---|---|
| `localization_counts.csv` | 현지화·번역 코퍼스 15개의 표기별 출현 수 |
| `vendors_counts.csv` | 벤더 공식 문서와 제품 UI 문자열의 표기별 출현 수 |
| `blogs_counts.csv` | 기업 기술 블로그 22곳의 표기별 출현 수 |
| `blogs_shares.csv` | 블로그별, 묶음별 첫 형태의 비율 |
| `blogs_posts.csv` | 블로그 표본 글 목록(URL, 날짜, 제목) |
| `community_counts.csv` | GitHub README, GitHub 코드 검색, velog, 교보문고 도서 제목의 표기별 출현 수 |
| `norms.csv` | 단어별 국립국어원 규범 표기와 출처 URL |

`*_counts.csv`의 열은 `corpus,set,variant,count`다. `X:`로 시작하는 행은 거짓 일치로 판정해 집계에서 뺀 원래 수다.

넣지 않은 것은 세 가지다. 블로그 문장 표본은 제3자 블로그의 원문이라 넣지 않았다. 규범표의 판정 메모 열에는 사전 뜻풀이(CC BY-SA)가 들어 있어서 뺐다. 내려받은 코퍼스 원문도 넣지 않았다.
