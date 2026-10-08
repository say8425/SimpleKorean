# IT 외래어 33개 중 열 개만 규범과 갈린다

한국 IT 업계에는 규범과 다르게 쓰는 단어가 분명히 있지만, 그런 단어는 몇 개로 좁혀지고 어디서 갈리는지도 예측할 수 있다. 2026년 10월 7~8일 현지화·번역 코퍼스 15개(한글 826만 음절), 벤더 9곳의 공식 문서 약 1,000쪽과 제품 UI 문자열 3종, 기업 기술 블로그 22곳의 글 728편, GitHub README 1,317개와 velog 글에서 같은 규칙으로 표기를 센 결과, 철자 변이형이 있는 단어 33개 가운데 **23개**는 벤더 문서·현지화·블로그·편집 안 된 글 어디서나 합산으로 규범형이 다수였다. **4개**(디렉터리·릴리스·셸·리디렉션)는 벤더 문서와 현지화에서는 규범형이, 블로그나 편집 안 된 글에서는 업계형이 우세하고, **4개**(리포지토리·바디·컬럼·타겟)는 편집된 문서에서도 업계형이 굳었으며, 공식 표기가 없는 **2개**는 리다이렉트·리팩토링이 차지했다. 규범이 두 형태를 다 허용하는 선택은 회사가 가른다. 에러와 파라미터는 카카오·토스 개발자 문서와 각각 블로그 22곳 중 14곳의 다수형이고, Microsoft·GitHub·Google 문서는 오류·매개변수를 쓴다. 국립국어원은 확인할 수 있는 범위에서 업계 철자를 인정한 적이 없고, 표기를 정하지 않은 method·redirect에서만 관행이나 발음을 따르라고 했다. 2026년 velog 글의 약 19%에 LLM풍 em dash가 나타나(2019~2025년 0~2%) 최근의 규범 쪽 이동이 사람의 변화인지 모델의 습관인지 가를 수 없지만, 관용 6개는 2023년 이전 사람 글에서도 업계형이 다수였고 규범 23개는 그 전부터 편집된 출처에서 우세했으므로 분류는 흔들리지 않는다. 그러므로 SimpleKorean은 초안의 원칙을 유지하되 여섯 무리로 나눈 단어 목록을 붙여, 23개의 변이형만 두 모드 모두 오류로, 갈리거나 관용이 굳은 8개는 기본 모드 경고·엄격 모드 오류로 두고, 관용이 굳은 4개는 저장소·본문·열·대상 같은 우리말 대응어로 비켜 가며, 문서 안 일관성은 규범과 따로 검사해야 한다.

## 국립국어원은 업계 철자를 받아들인 적이 없고 미정어만 관행에 맡긴다

규범의 근거는 단어마다 무게가 다르다. 조사한 33개 가운데 **25개**는 국립국어원 「외래어 표기 용례」에 실려 있고, 상당수는 업계형을 직접 오표기로 적는다. 디렉토리·메세지·쉘·타겟·릴리즈·쓰레드·라이센스·스케쥴·해더·데이타·버젼·바디가 '(X)'로 표시되고, 디렉터리는 **1993년 제5차 외래어 심의회**, 애플리케이션과 준말 앱은 **2012년 제104차 심의회**에서 정했다 ([용례 directory](https://korean.go.kr/kornorms/example/exampleList.do?regltn_code=0003&pageUnit=100&pageIndex=1&example_search_list%5B0%5D.searchCondition=srclang_mark&example_search_list%5B0%5D.searchEquals=equal&example_search_list%5B0%5D.searchKeyword=directory), [용례 application](https://korean.go.kr/kornorms/example/exampleList.do?regltn_code=0003&pageUnit=100&pageIndex=1&example_search_list%5B0%5D.searchCondition=srclang_mark&example_search_list%5B0%5D.searchEquals=equal&example_search_list%5B0%5D.searchKeyword=application)). 우리말샘은 비규범형을 표제어로 올린 뒤 "⇒규범 표기는 …이다"로 바로잡는다. 리포지토리→리포지터리, 메소드→메서드, 컬럼→칼럼, 타겟→타깃이 그렇다 ([우리말샘 리포지토리](https://opendict.korean.go.kr/dictionary/view?sense_no=724814&viewType=confirm), [메소드](https://opendict.korean.go.kr/dictionary/view?sense_no=800024&viewType=confirm), [컬럼](https://opendict.korean.go.kr/dictionary/view?sense_no=776168&viewType=confirm), [타겟](https://opendict.korean.go.kr/dictionary/view?sense_no=804570&viewType=confirm)). 다만 리포지터리와 메서드는 용례와 표준국어대사전에 없고 우리말샘의 지시만 있으며, redirect와 refactoring은 세 자료 어디에도 없다. 고유 명칭에는 국립국어원도 예외를 둔다. 용례는 회사 Shell을 '셸 (사)'로 적으면서 "국내 고유명사는 '쉘 (사)'"라는 단서를 단다 ([용례 shell](https://korean.go.kr/kornorms/example/exampleList.do?regltn_code=0003&pageUnit=100&example_search_list%5B0%5D.searchCondition=srclang_mark&example_search_list%5B0%5D.searchEquals=equal&example_search_list%5B0%5D.searchKeyword=shell)).

온라인가나다 공개분과 상담 사례 2,452건, 다듬은 말을 함께 뒤져도 업계 철자를 표준으로 받아들인 사례는 없었다. 온라인가나다는 2024년 10월 이후 글 3만여 건만 공개되어 있어 그 이전의 입장 변화는 추적할 수 없다 ([온라인가나다](https://korean.go.kr/front/onlineQna/onlineQnaList.do?mn_id=216), [상담 사례 모음](https://korean.go.kr/front/mcfaq/mcfaqList.do?mn_id=217)). 공개된 범위에서 국립국어원은 '어플리케이션'의 규범 표기가 '애플리케이션'이고 준말도 '애플'이나 '앱'이 맞다고 했고(2026-03-18, [328268](https://korean.go.kr/front/onlineQna/onlineQnaView.do?mn_id=216&qna_seq=328268&pageIndex=1)), '셋팅'은 '세팅'(2025-04-09, [312618](https://korean.go.kr/front/onlineQna/onlineQnaView.do?mn_id=216&qna_seq=312618&pageIndex=1)), targeting은 '타기팅'(2026-07-07, [333450](https://korean.go.kr/front/onlineQna/onlineQnaView.do?mn_id=216&qna_seq=333450&pageIndex=1))이라고 답했다. 이미 굳은 외래어의 관용을 존중한다는 외래어 표기법 제1장 제5항을 IT 단어에 직접 든 답변은 '보디' 하나다. 여기서 관용은 1999년 국어순화자료집이 정한 '보디'를 가리킬 뿐 업계의 '바디'가 아니다 ([330205](https://korean.go.kr/front/onlineQna/onlineQnaView.do?mn_id=216&qna_seq=330205&pageIndex=1)). 국립국어원이 관행에 기대는 것은 표기를 정하지 않은 단어뿐이다. method에는 "규범 표기가 아직까지 상정되지 않아 … 관행적으로 쓰고 있는 표기 방식이 있다면 그에 따르시기를" 권했고(2025-02-04, [309723](https://korean.go.kr/front/onlineQna/onlineQnaView.do?mn_id=216&qna_seq=309723&pageIndex=1)), redirect에는 "따로 규정된 바가 없어" 발음을 따르라고 했으며(2025-04-16, [313045](https://korean.go.kr/front/onlineQna/onlineQnaView.do?mn_id=216&qna_seq=313045&pageIndex=1)), refactoring에는 factoring이 '팩터링'으로 심의되었으니 "'리팩터링'으로 표기할 수 있을 듯"하다고 했다(2026-08-10, [334621](https://korean.go.kr/front/onlineQna/onlineQnaView.do?mn_id=216&qna_seq=334621&pageIndex=1)). method 답변은 우리말샘의 '메소드 ⇒ 메서드'와 어긋나므로 국립국어원 자료끼리도 충돌한다. release도 용례는 '릴리즈(X)'로 적지만, 우리말샘은 소리 뜻의 release에 한해 '릴리스'와 '릴리즈'를 모두 "규범 표기는 미확정"으로 둔다 ([우리말샘 릴리스](https://opendict.korean.go.kr/dictionary/view?sense_no=982259&viewType=confirm)).

띄어쓰기는 한 갈래로 정리되지 않는다. 한글 맞춤법 제50항은 "전문 용어는 단어별로 띄어 씀을 원칙으로 하되, 붙여 쓸 수 있다"고 하고 ([한글 맞춤법](https://korean.go.kr/kornorms/regltn/regltnView.do?regltn_code=0001)), 외래어 표기법 제3장 제1절 제10항은 원어에서 띄어 쓴 말을 띄어 쓰되 붙여 쓸 수도 있다고 한다 ([외래어 표기법](https://korean.go.kr/kornorms/regltn/regltnView.do?regltn_code=0003)). 그래서 표준국어대사전의 '매개^변수'와 우리말샘의 '오픈^소스'는 띄어도 붙여도 맞다 ([매개^변수](https://stdict.korean.go.kr/search/searchView.do?word_no=111708&searchKeywordTo=3), [오픈^소스](https://opendict.korean.go.kr/dictionary/view?sense_no=832806&viewType=confirm)). '기본값'은 우리말샘에 '기본-값' 한 단어로 올라 있어 붙여 써야 하고 ([기본-값](https://opendict.korean.go.kr/dictionary/view?sense_no=750266&viewType=confirm)), '반환값'은 어느 사전에도 없다. 수치를 뜻하는 '값'은 앞말에 붙인다는 표준국어대사전 '값'「8」은 붙여 쓰기를, 사전에 없는 결합은 명사구로 본다는 온라인가나다 답변은 띄어 쓰기를 지지한다 ([값](https://stdict.korean.go.kr/search/searchView.do?word_no=388727&searchKeywordTo=3), [331647](https://korean.go.kr/front/onlineQna/onlineQnaView.do?mn_id=216&pageIndex=1&qna_seq=331647)).

정리하면 규범이 주는 판정은 세 등급이다. 국립국어원 자료가 규범 표기를 정한 **31개** 단어에서는 다른 철자를 틀렸다고 말할 수 있다(그중 리포지터리와 메서드는 근거가 우리말샘 하나뿐이다). redirect·refactoring에서는 어느 형태도 틀렸다고 할 근거가 없다. 띄어쓰기 허용형, 그리고 오류/에러·매개변수/파라미터 같은 고유어·한자어 대 외래어 선택은 양쪽 모두 규범에 맞다. 에러와 파라미터도 표준국어대사전 표제어다 ([표준 에러](https://stdict.korean.go.kr/search/searchView.do?word_no=456141&searchKeywordTo=3), [표준 파라미터](https://stdict.korean.go.kr/search/searchView.do?word_no=498269&searchKeywordTo=3)). 린터의 강도는 이 근거의 무게를 넘어서는 안 된다.

## 33개 가운데 23개는 규범대로, 4개는 갈리고, 6개는 관용이 차지했다

측정은 출처 유형마다 따로 했다(2026-10-07~08). 현지화·번역은 용어집과 리뷰가 있는 오픈 소스 15개의 고정 커밋을 썼다 ([Kubernetes](https://github.com/kubernetes/website/tree/3e3fcc9b5e530cb8e6fa5573e53de3c8af3c9df5/content/ko), [MDN](https://github.com/mdn/translated-content/tree/d039df688593089a43fb7cdca456567549bca360/files/ko), [React](https://github.com/reactjs/ko.react.dev/tree/89f79e9e971e9ad424ea5ebabdf8d5fa66c87375/src/content), [Vue](https://github.com/vuejs-translations/docs-ko/tree/6e646acb5687510feda533281faa546b26ea243c/src), [Python 3.14](https://github.com/python/python-docs-ko/tree/242bdce63d20a3042fa438fea9677f289d7a6d0c), [PyTorch](https://github.com/PyTorchKR/tutorials-kr/tree/84b7db6e020c098cf38a0dfaf036007c24057bb1), [VS Code](https://github.com/microsoft/vscode-loc/tree/0f157dee0cdcbf58cdf51a221ee94751c7f35e75/i18n/vscode-language-pack-ko/translations), [Firefox](https://github.com/mozilla-l10n/firefox-l10n/tree/0da379c064af4968c17feca6128a1290adfb3009/ko), [AOSP](https://android.googlesource.com/platform/frameworks/base/+/1cdfff555f4a21f71ccc978290e2e212e2f8b168/core/res/res/values-ko/strings.xml), [Chromium](https://chromium.googlesource.com/chromium/src/+/e75d6d04bbcae954543287a14523bcc5e97ba7a0/chrome/app/resources/generated_resources_ko.xtb), [LibreOffice](https://github.com/LibreOffice/translations/tree/eb0ac524bb996151fdbc4e78ec1f28effbc0c5b9/source/ko), [Rust 책](https://github.com/rust-kr/doc.rust-kr.org/tree/cbbea2ca830cb0c090651111b3a18f5d5beabace/src), [javascript.info](https://github.com/javascript-tutorial/ko.javascript.info/tree/2489814d15d09791bf6edfe00774ce0171e3bd1e), [Pro Git](https://github.com/progit/progit2-ko/tree/f50647da032bf210ef91802290d60d05da1a9416), [TypeScript-KR](https://github.com/typescript-kr/typescript-kr.github.io/tree/3fad5f8dab80e88a9190aae8c3256ce0b9bc7869/pages)). 벤더 문서는 [Microsoft Learn](https://learn.microsoft.com/ko-kr/), [GitHub Docs](https://docs.github.com/ko), [AWS](https://docs.aws.amazon.com/ko_kr/), [Google 개발자 문서](https://developer.android.com/develop/background-work/services/bound-services?hl=ko), [Apple 개발자 도움말](https://developer.apple.com/kr/help/account/basics/about-your-developer-account), [NAVER Cloud](https://guide.ncloud-docs.com/docs/sourcecommit-overview), [카카오](https://developers.kakao.com/docs/ko/kakaologin/common), [토스페이먼츠](https://docs.tosspayments.com/guides/learn/payment-flow), [삼성](https://developer.samsung.com/watch-face-studio/ko/overview.html)에서 뽑은 무작위·등간격 표본 12개와 [Android](https://android.googlesource.com/platform/packages/apps/Settings/+/refs/heads/main/res/values-ko/strings.xml)·[JetBrains](https://plugins.jetbrains.com/plugin/13711)·[Windows Terminal](https://github.com/microsoft/terminal/blob/main/src/cascadia/TerminalApp/Resources/ko-KR/Resources.resw)의 한국어 문자열 파일이다. 기업 블로그는 [토스](https://toss.tech)·[카카오](https://tech.kakao.com)·[카카오페이](https://tech.kakaopay.com)·[네이버 D2](https://d2.naver.com)·[우아한형제들](https://techblog.woowahan.com)·[NHN Cloud](https://meetup.nhncloud.com) 등 22곳의 최신 한국어 글이다(Medium에 있는 6곳은 수집 제한으로 9~28편). 편집 안 된 글은 GitHub README 1,317개와 velog의 최근·인기 글, 2019~2026년 스냅숏 9개다 ([GitHub REST 검색](https://docs.github.com/en/rest/search/search#search-repositories), [velog GraphQL](https://v3.velog.io/graphql)). 코드 블록을 빼고 NFC로 정규화해 부분 문자열을 셌고, 캐시백·캄보디아·브리티시컬럼비아 같은 거짓 일치는 걸렀다. 표의 비율은 묶음 전체 출현 가운데 규범형의 몫이고, 괄호의 'n:m'은 그 단어가 5회 이상 나온 코퍼스·벤더 표본·블로그 가운데 규범형이 과반인 곳과 업계형이 과반인 곳의 수다. 단어별 원자료는 [`data/loanword-usage/`](data/loanword-usage/)의 CSV 네 개(`*_counts.csv`)에 있다.

### 23개는 출처 유형마다 규범형이 다수다

| 규범형 ← 주된 변이형 | 현지화 15개 | 벤더 문서 12개 표본 | 기업 블로그 22곳 | README / velog 2019–22 | 메모 |
|---|---|---|---|---|---|
| 메시지 ← 메세지 | 95.6% (14:0) | 99.9% (12:0) | 97.4% (21:0) | 70% / 65% | UI 문자열 3종도 규범형 |
| 애플리케이션 ← 어플리케이션 | 90.4% (14:0) | 100% (9:0) | 85.9% (19:2) | 76% / 78% | 블로그 어플리케이션의 61%가 한 곳 |
| 콘텐츠 ← 컨텐츠 | 89.2% (11:1) | 99.6% (10:0) | 89.8% (17:1) | 75% / 80% | 블로그 컨텐츠의 78%가 한 곳 |
| 아키텍처 ← 아키텍쳐 | 96.9% (7:0) | 100% (5:0) | 95.0% (19:0) | 82% / 74% | |
| 스레드 ← 쓰레드 | 98.0% (9:0) | 100% (3:0) | 77.7% (18:1) | 80% / 70% | 블로그 쓰레드의 88%가 한 곳 |
| 메서드 ← 메소드 | 92.2% (10:2) | 99.4% (7:0) | 78.4% (11:3) | 71% / 46% | 현지화 중 PyTorch·Pro Git만 메소드 |
| 라이선스 ← 라이센스 | 86.4% (8:1) | 100% (3:0) | 69.6% (3:1) | 68% / 70% | 블로그 라이센스의 67%가 한 곳 |
| 액세스 ← 엑세스 | 98.9% (10:0) | 100% (8:0) | 94.7% (2:0) | 72% / 75% | |
| 스케줄 ← 스케쥴 | 97.5% (5:1) | 90.5% (3:0) | 96.2% (16:0) | 84% / 50% | velog는 10회뿐 |
| 비즈니스 ← 비지니스 | 92.5% (3:0) | 100% (7:0) | 99.0% (21:0) | 86% / 91% | |
| 세팅 ← 셋팅 | 96.6% (3:0) | 100% (4회) | 97.8% (11:0) | 84% / 76% | 벤더·UI는 주로 '설정' |
| 매뉴얼 ← 메뉴얼 | 94.3% (3:0) | 0회 | 90.9% (33회) | 47% / 95% | README는 17회뿐 |
| 캐시·대시보드·해시·포맷·렌더링·트랜잭션·버전·헤더·데이터·컴포넌트·프레임워크 | 97.4~100% | 100% | 96.7~100% | 89~100% / 91~100% | 비규범형이 사실상 없음 |

이 23개에서 업계형은 한두 블로그의 습관으로만 남아 있다. 블로그의 쓰레드 146회 가운데 128회는 [데브시스터즈](https://tech.devsisters.com) 한 곳에서 나왔고, 컨텐츠는 데브시스터즈가 78%, 어플리케이션은 [하이퍼커넥트](https://hyperconnect.github.io)가 61%, 라이센스는 [DEVOCEAN](https://devocean.sk.com/blog/index.do?boardType=techBlog)이 67%를 차지한다. 블로그 수로 세면 규범형이 스레드 18:1, 콘텐츠 17:1, 애플리케이션 19:2, 라이선스 3:1로 앞선다. 편집이 차이를 만든다는 흔적도 있다. 교보문고 IT 도서 제목에서 애플리케이션·아키텍처·비즈니스·버전·데이터는 2010~2019년 출간본에서 이미 **94~99%**가 규범형이었지만 ([교보문고 '애플리케이션' 검색](https://search.kyobobook.co.kr/search?keyword=%EC%95%A0%ED%94%8C%EB%A6%AC%EC%BC%80%EC%9D%B4%EC%85%98&target=kyobo&gbCode=TOT&cat2=%EA%B5%AD%EB%82%B4%EB%8F%84%EC%84%9C%40KORBOOK%40%40%EC%BB%B4%ED%93%A8%ED%84%B0%2FIT%4033&len=100)), 2023년 이전에 만든 저장소의 README에서는 콘텐츠 48%, 메서드 62%, 애플리케이션 67%, 메시지 69%에 그쳤다 ([GitHub REST 검색](https://docs.github.com/en/rest/search/search#search-repositories)). 편집된 글이 먼저 규범형으로 모였고, 편집 안 된 글은 그보다 늦다. 그래서 2019~2022년 velog의 메서드(46%)나 README의 매뉴얼(17회 중 8회)처럼 작은 층에서는 업계형이 앞선 곳도 남아 있다.

메서드는 국립국어원 자료가 충돌하는데도 벤더 문서 99.4%, 현지화 92.2%가 메서드를 쓴다. 비규범형을 고른 곳은 TTA 정보통신용어사전을 근거로 메소드를 용어집에 올린 PyTorch 한국어 튜토리얼과 '초판 기준' 방침을 지키는 Pro Git 정도다 ([PyTorch 번역 가이드](https://github.com/PyTorchKR/tutorials-kr/blob/84b7db6e020c098cf38a0dfaf036007c24057bb1/TRANSLATION_GUIDE.md#L94), [Pro Git 번역 노트](https://github.com/progit/progit2-ko/blob/f50647da032bf210ef91802290d60d05da1a9416/TRANSLATION_NOTES.asc)). 애플리케이션은 준말 '앱'과 함께 봐야 한다. 카카오 개발자 문서(앱 1,093 대 애플리케이션 0), Apple 개발자 도움말(2,019 대 10), Android 문자열(1,479 대 69)은 준말을 쓰는데, 둘 다 2012년 심의 결과라 어느 쪽도 틀리지 않다. 세팅은 철자보다 단어 선택이 크다. Android·JetBrains·Windows Terminal 문자열은 settings를 '설정'으로 옮긴다(1,128회, 2,642회, 88회 대 세팅 0~1회).

### 갈림과 관용은 편집 여부와 용어집의 선택을 따라간다

| 규범형 ← 업계형 | 국립국어원 근거 | 현지화 15개 | 벤더 문서·UI | 기업 블로그 22곳 | README / velog 2019–22 / velog 2026 | 판정 |
|---|---|---|---|---|---|---|
| 디렉터리 ← 디렉토리 | 용례 '디렉토리(X)' | 70.5% (9:4) | 96.6% (6:0), JetBrains 1,647:38 | 49.3% (7:3) | 14% / 36% / 57% | 갈림 |
| 릴리스 ← 릴리즈 | 용례 '릴리즈(X)' | 71.1% (6:4) | 89.6% (6:1), 토스 0:20 | 44.3% (6:10) | 32% / 10% / 76% | 갈림 |
| 셸 ← 쉘 | 용례 '쉘(X)' | 91.6% (4:3) | 96.4% (2:0), UI 3종 100% | 22.6% (2:3) | 28% / 0% / 83% | 갈림 |
| 리디렉션 ← 리다이렉션 | 우리말샘 표제어 | 72.5% (5:1) | 96.6% (3:0) | 1:2회 | 5:3회 / 0:4회 / 0:7회 | 갈림(편집 안 된 글은 표본 작음) |
| 리포지터리 ← 리포지토리·레포지토리 | 우리말샘 지시뿐 | 24.2% (1:3) | 0% (0:6) | 38.3% (2:3) | 0.4% / 0% / 0% | 관용 굳음 |
| 보디 ← 바디 | 용례 '바디(X)' | 0% (0:2) | 0% (0:2) | 0:5회 | 0:2회 / 0:7회 / 0:3회 | 관용 굳음 |
| 칼럼 ← 컬럼 | 우리말샘 '컬럼 ⇒ 칼럼' | 43.2% (1:1) | 토스 10:1, MS 0:2, MS 용어집 '열' | 9.0% (2:16) | 22% / 10% / 6% | 관용 굳음 |
| 타깃 ← 타겟 | 용례 '타겟(X)' | 37.0% (2:4) | 4.6% (0:2), JetBrains 822:2 | 22.6% (2:7) | 14% / 9% / 47% | 관용 굳음 |
| 리디렉트 ← 리다이렉트 | 공식 표기 없음 | 7.2% (1:2) | 0% (0:2) | 0:8회 | 0% / 0% / 9% | 미정어, 업계형 우세 |
| 리팩터링 ← 리팩토링 | 공식 표기 없음(유추 안내) | 56.5% (3:6) | 100% (2:0) | 21.9% (2:10) | 10% / 3% / 11% | 미정어, 업계형 우세 |

갈리는 네 단어는 편집된 문서와 편집 안 된 글 사이에 경계가 있다. 디렉터리는 Microsoft·GitHub·AWS·Google 표본에서 **91~100%**이고 JetBrains 한국어 언어 팩도 1,647 대 38이지만, README에서는 **14%**에 그치고 블로그 합산은 74 대 76이다. 블로그 수로는 디렉터리 7곳 대 디렉토리 3곳이어서, 합산 반반은 디렉토리를 많이 쓰는 인프랩(21회)과 컬리(11회)의 몫이다. 공식 문서 안의 예외는 제품 이름이다. macOS 앱 이름이 '디렉토리 유틸리티'라서 Apple 도움말 한 쪽에 디렉토리가 51번 나오고 디렉터리는 0번이다 ([디렉토리 유틸리티 사용 설명서](https://support.apple.com/ko-kr/guide/directory-utility/welcome/mac)). 현지화에서는 MDN(디렉토리 145 대 69), Pro Git(383 대 1), PyTorch(22 대 6), LibreOffice(91 대 66)가 디렉토리를 유지한다. 릴리스는 Microsoft Learn 77 대 0, GitHub Docs 36 대 0, JetBrains 53 대 1이지만, 토스페이먼츠 문서는 릴리즈만 20번 쓰고 그중 12번은 "API 버전 업데이트 사항은 릴리즈 노트에서 확인할 수 있습니다"라는 같은 문장이다 ([토스페이먼츠 해외 결제 연동](https://docs.tosspayments.com/guides/v2/payment-window/integration-international)). 현지화에서는 React(릴리즈 160 대 33), Rust 책(62 대 0), Pro Git(14 대 0)이 릴리즈를, Kubernetes(릴리스 458 대 13)·Python·Vue·VS Code가 릴리스를 쓰고, 블로그 수로는 릴리즈가 10곳 대 6곳이다. 셸은 Android·JetBrains·Windows Terminal 문자열이 모두 셸이고 현지화도 91.6%지만, 블로그는 쉘 48 대 셸 14(인프랩의 '앱쉘' 14회를 빼도 34 대 14)이고 2019~2022년 velog는 쉘 10 대 0이다. IT 도서 제목도 「유닉스 쉘 바이블」(2005)과 「처음 배우는 셸 스크립트」(2021)로 갈린다 ([교보문고 '셸' 검색](https://search.kyobobook.co.kr/search?keyword=%EC%85%B8&target=kyobo&gbCode=TOT&cat2=%EA%B5%AD%EB%82%B4%EB%8F%84%EC%84%9C%40KORBOOK%40%40%EC%BB%B4%ED%93%A8%ED%84%B0%2FIT%4033&len=100)). 명사 리디렉션은 우리말샘 표제어이고 벤더 문서 96.6%가 따르지만, 표에 든 블로그·README·velog 층을 합친 22회 가운데 리디렉션은 6회뿐이다 ([우리말샘 리디렉션](https://opendict.korean.go.kr/dictionary/view?sense_no=1105914&viewType=confirm)).

관용이 굳은 네 단어는 편집된 문서에서도 규범형이 소수다. 리포지터리는 벤더 표본 **1,104회 중 0회**다. Microsoft 용어집이 repository를 '리포지토리'로 정해 두었고 ([Microsoft Terminology](https://learn.microsoft.com/en-us/globalization/reference/microsoft-terminology)), 대부분 기계 번역인 Microsoft Learn(49회)과 GitHub Docs(939회), VS Code 언어 팩(257회), AWS, NAVER Cloud가 같은 형태를 쓴다. GitHub 한국어 용어집도 표제어가 리포지토리다 ([GitHub 용어집](https://docs.github.com/ko/get-started/learning-about-github/github-glossary)). 리포지터리를 쓰는 곳은 용어집에 명시한 Kubernetes 한국어 문서(95/102)와 블로그 중 NHN Cloud(34회)뿐이고, 편집 안 된 README에서는 레포지토리가 162회로 리포지토리(63회)보다 많다. 반면 Google·토스페이먼츠·삼성 문서, JetBrains UI("Git 저장소 생성…", 저장소 617 대 리포지토리 1), Pro Git(800회), 네이버 D2(41/41)는 '저장소'로 비켜 간다. 바디는 현지화 95회, 벤더 표본 110회에서 보디가 0회다(벤더 쪽 1회는 '캄보디아'). NAVER Cloud API 가이드는 50쪽 가운데 39쪽에 '요청 바디'·'응답 바디' 머리말이 있고, Python 문서 번역 용어집은 body를 '바디'로 정했다 ([NCP API 가이드](https://api.ncloud-docs.com/docs/security-privateca-updateocspurl.md), [Python 번역 가이드](https://github.com/python/python-docs-ko/blob/242bdce63d20a3042fa438fea9677f289d7a6d0c/.pdk/guide.md)). Microsoft 용어집은 body를 '본문'으로, javascript.info가 쓰는 tech-translation-ko 용어집은 함수 body를 '본문'으로 옮겨 규범 논쟁을 피한다 ([tech-translation-ko 용어집](https://github.com/Violet-Bora-Lee/tech-translation-ko/blob/573efbd3dddd7109fec668aa0917112a4f0b3ca8/docs/analysis/glossary.tsv)). 컬럼은 블로그 332회 가운데 **302회**이고 블로그 18곳 중 16곳의 다수형이며, [카카오페이](https://tech.kakaopay.com)는 45회 모두 컬럼이다. 칼럼을 쓰는 곳은 토스페이먼츠 문서(10 대 1)와 MDN(61%) 정도이고, Microsoft 용어집은 '열'을 쓴다. 타겟은 Google 개발자 문서 87회 모두와 카카오 개발자 문서 275회 중 261회인데, 카카오의 261회 중 217회는 광고 API 다섯 쪽에 몰려 있다 ([카카오모먼트 타겟 관리](https://developers.kakao.com/docs/ko/kakaomoment/target-reaction-mgmt)). 반대로 Python 번역(49/49)과 JetBrains UI(822 대 2)는 타깃을, Microsoft 용어집과 Android("공유 대상:")는 '대상'을 쓴다.

공식 표기가 없는 두 단어는 업계형이 거의 전부다. 리다이렉트는 카카오(202회)와 토스페이먼츠(147회) 문서, Kubernetes 용어집이 쓰고, 현지화에서 리디렉트는 111회 중 8회(Python 6회)뿐이다 ([Kubernetes 한글화 용어집](https://github.com/kubernetes/website/blob/3e3fcc9b5e530cb8e6fa5573e53de3c8af3c9df5/content/ko/docs/contribute/localization_ko.md#L254)). 카카오 개발자 문서 스타일 가이드는 "외래어 표기법에 맞춰" 쓰라고 하면서 초출 표기 예시로 '파라미터(Parameter)'와 '리다이렉트(Redirect)'를 든다 ([카카오 문서 스타일 가이드](https://developers.kakao.com/docs/ko/documentation-guideline/document-style-open)). 표기법을 따르라는 원칙만으로는 표기가 정해지지 않은 단어의 형태가 나오지 않는다는 뜻이다. 리팩토링은 블로그 146회 중 114회, README 125회 중 112회이고 현지화 9곳 가운데 6곳(React 20 대 1, PyTorch, javascript.info 등)도 리팩토링이다. 그러나 Microsoft 용어집과 벤더 표본(18/18), VS Code(32 대 1), Rust 책(23/23), 2020년에 나온 도서 「리팩터링」은 국립국어원이 유추로 안내한 리팩터링을 쓴다 ([교보문고 '리팩터링' 검색](https://search.kyobobook.co.kr/search?keyword=%EB%A6%AC%ED%8C%A9%ED%84%B0%EB%A7%81&target=kyobo&gbCode=TOT&cat2=%EA%B5%AD%EB%82%B4%EB%8F%84%EC%84%9C%40KORBOOK%40%40%EC%BB%B4%ED%93%A8%ED%84%B0%2FIT%4033&len=100)).

이 분류는 업계형을 공식 정책으로 받아들인 회사의 기준과도 맞아떨어진다. 토스 「테크니컬 라이팅 가이드」는 "구글 트렌드 기준으로 외래어 표기법보다 5배 이상 많이 사용되는 표기가 있으면 그 표기를 사용"한다 ([technical-writing.dev](https://technical-writing.dev/sentence/consistency.html)). 구글 트렌드 대신 이 조사의 코퍼스에 같은 문턱을 대어 보면, 5배를 넘는 것은 **컬럼**(블로그 10배, GitHub 코드 검색 13배), **리다이렉트**(코드 검색 61배), **리포지토리 계열**(코드 검색 23배), **바디**(편집 문서에서 보디 0회)뿐이다 ([GitHub 코드 검색](https://docs.github.com/en/rest/search/search#search-code)). 리팩토링(2.5~3.6배), 타겟(2.1~3.4배), 쉘(블로그 3.4배), 디렉토리(1.0~1.7배), 릴리즈(0.5~1.3배)는 넘지 못한다. 토스 블로그에서도 5회 이상 나온 단어 가운데 철자 비규범형은 릴리즈(19/21)와 컬럼(10/10)뿐이고, 가이드 예시어인 프론트엔드는 36 대 0이다 ([toss.tech](https://toss.tech)). 업계형을 허용하는 쪽과 규범을 지키는 쪽이 문제 단어는 거의 같게 고르고, 그 자리에 무엇을 넣느냐에서만 다르다는 뜻이다.

### 에러·파라미터·띄어쓰기는 철자가 아니라 회사의 선택이다

| 지정 후보 / 대안 | 국립국어원 근거 | 현지화 15개 | 벤더 문서 12개 표본 | 기업 블로그 22곳 | README / velog 2019–22 / velog 2026 |
|---|---|---|---|---|---|
| 오류 / 에러 | 둘 다 표준국어대사전 표제어, 다듬은 말 '에러 → 실수·잘못·오류' | 50.1% (11:4), UI 문자열 4종 100% | 49.9% (10:2, 카카오·토스는 에러) | 40.8% (7:14) | 58% / 38% / 61% |
| 매개변수 / 파라미터 | 둘 다 표준국어대사전 표제어, 다듬은 말 '파라미터 → 매개 변수' | 87.4% (10:3) | 35.1% (3:6) | 13.8% (2:14) | 43% / 42% / 20% |
| 사용자 / 유저 | 다듬은 말 '유저 → 사용자'(2013 고시) | 96.9% (15:0) | 99.9% (12:0) | 72.9% (18:4) | 79% / 79% / 91% |
| 기본값 / 디폴트 | 둘 다 우리말샘·용례에 있음 | 98.5% (15:0) | 99.4% (10:0) | 97.6% (11:0) | 70% / 70% / 96% |
| 배포 / 디플로이 | 디플로이는 세 자료에 없음 | 99% 이상(디플로이먼트 제외) | 100% (9:0) | 99.9% (22:0) | 100% / 99% / 100% |

| 붙여 쓴 형태의 비율 | 국립국어원 근거 | 현지화 15개 | 벤더 문서 12개 표본 | 기업 블로그 22곳 | README / velog 2019–22 / velog 2026 | GitHub 코드 검색 |
|---|---|---|---|---|---|---|
| 기본값 (← 기본 값) | 우리말샘 '기본-값' 한 단어 | 89.5% | 91.9% | 85.1% | 100% / 76% / 98% | 96% |
| 매개변수 (← 매개 변수) | 띄움 원칙, 붙임 허용 | 61.9% | 38.2% | 97.1% | 80% / 85% / 100% | 92% |
| 반환값 (← 반환 값) | 사전 미등재 | 17.2% | 0.6% | 71.0% (31회) | 82% / 100% / 89% | 66% |
| 오픈소스 (← 오픈 소스) | 띄움 원칙, 붙임 허용 | 47.2% | 61.0% | 69.2% | 89% / 54% / 92% | 73% |

오류와 에러, 매개변수와 파라미터는 둘 다 표준국어대사전 표제어라 규범 위반이 아니고, 선택은 회사 단위로 뚜렷하게 갈린다. UI 문자열은 VS Code·Firefox·Android·Chromium 모두 **오류 100%**이고 Microsoft·GitHub·AWS·Google 문서도 오류지만, 카카오(오류 10.8%)와 토스페이먼츠(25.4%) 문서는 에러가 다수다 ([카카오 로그인 이해하기](https://developers.kakao.com/docs/ko/kakaologin/common), [토스페이먼츠 에러 코드](https://docs.tosspayments.com/reference/error-codes)). 블로그에서도 NHN Cloud(오류 100%), 네이버 D2(82%), 카카오(73%)와 컬리(12%), 카카오페이(19%)가 갈린다. 현지화에서는 Python(에러 95%)·Rust 책(99%)·javascript.info(97%)가 에러를 쓴다. 매개변수는 Microsoft·GitHub(매개 변수)와 Google(매개변수), React·MDN·Rust 등 현지화 87%가 쓰지만, AWS와 카카오·토스페이먼츠·NAVER Cloud 문서, 블로그 22곳 중 14곳은 파라미터를 쓰고 블로그 합산으로는 파라미터가 매개변수의 6.2배다. 사용자/유저는 블로그 수로 18곳 대 4곳이고 유저가 다수인 곳은 하이퍼커넥트·데브시스터즈·컬리·무신사뿐이며, 기본값/디폴트와 배포/디플로이는 선택이 사실상 끝났다.

띄어쓰기는 벤더 용어집이 정한다. Microsoft 용어집은 '매개 변수·반환 값·오픈 소스'를 띄우고 GitHub Docs도 같으며, Google은 '매개변수·오픈소스'를 붙이되 '반환 값'은 띄운다. Microsoft 한국어 스타일 가이드는 합성어를 "Generally, there should be no space"라고 하면서도 용어집은 '매개 변수'를 띄우니, 한 회사 안에서도 일관되지 않다 ([Microsoft 한국어 스타일 가이드](https://download.microsoft.com/download/5/b/6/5b62389f-4e3b-4c77-bc18-94efba2fa7bb/kor-kor-StyleGuide.pdf)). 현지화에서 반환값을 붙이는 곳은 React(84%)와 Vue(82%)뿐이고, MDN은 "반환 값, 기본 값"을 규칙으로 정했다. 그런데 MDN 문서는 반환 값 규칙을 88% 지키면서 기본 값 규칙은 32%만 지킨다 ([MDN 용어 안내서](https://github.com/mdn/translated-content/blob/d039df688593089a43fb7cdca456567549bca360/docs/ko/guides/glossary-guide.md)). 편집 안 된 글은 네 쌍 모두 붙이는 쪽이 다수다.

이런 선택에는 근거가 남지 않는 경우가 많다. 비규범형이나 외래어를 고른 용어집 가운데 근거를 적은 것은 PyTorch의 메소드(TTA 링크)뿐이고, Kubernetes의 파라미터·리다이렉트, Python의 에러·바디, tech-translation-ko의 에러·리포지토리는 근거 없이 팀 결정으로만 기록되어 있다. 반대로 규범형을 고른 쪽은 국립국어원을 든다. TypeScript-KR은 "국립국어원 발음표기에 따라 '메소드'가 아닌 '메서드'로 통일"했고, Kubernetes는 API 오브젝트를 "국립국어원 외래어 표기법에 따라" 적는다 ([TypeScript-KR 기여 안내](https://github.com/typescript-kr/typescript-kr.github.io/blob/3fad5f8dab80e88a9190aae8c3256ce0b9bc7869/CONTRIBUTING.md), [Kubernetes 한글화 용어집](https://github.com/kubernetes/website/blob/3e3fcc9b5e530cb8e6fa5573e53de3c8af3c9df5/content/ko/docs/contribute/localization_ko.md#L254)). 일관성과 규범 준수도 다른 축이다. 카카오페이 블로그는 컬럼 45/45, 릴리즈 7/7, 리팩토링 8/8로 비규범형을 한결같이 쓰면서 애플리케이션 100/100, 메서드 86/86은 규범형으로 쓴다. 반대로 MDN 한국어 문서는 5회 이상 나온 묶음 41개 가운데 37개에서 형태를 섞고, 메서드와 메소드가 한 파일에 함께 나오는 문서가 66개다.

## 2026년 글은 사람의 관행과 LLM의 습관을 가려 주지 못한다

편집 안 된 개발자 글에 LLM이 쓰거나 다듬은 글이 섞였다는 신호가 뚜렷하다. em dash(—)가 한 번 이상 나온 velog 글의 비율은 2019~2025년 스냅숏에서 **0~1.9%**였다가 2026년 4월 스냅숏에서 **19.6%**(22/112), 최근 글 1,500편에서 걸러 낸 883편에서 19.1%, 지난 1년 인기 글에서 17.5%로 뛰었다. README도 2023년 이전에 만든 저장소 0.8%에서 이후 8.2%로 늘었다 ([velog GraphQL](https://v3.velog.io/graphql)). em dash는 사람도 쓰고 자동 치환으로도 생기는 대리 지표라서 글 하나하나가 LLM 출력인지는 판정하지 않았다.

변화의 방향은 한쪽이 아니다. 아래 표처럼 2026년 velog 글은 디렉터리·셸·메서드·릴리스에서 규범형이 크게 늘었지만, 매개변수와 띄어 쓴 오픈 소스는 오히려 줄었고 리포지터리·칼럼·리팩터링은 거의 움직이지 않았다. README도 2023년 전후로 콘텐츠 48%→90%, 메서드 62%→96%가 오르는 동안 매개변수는 59%→23%로 떨어졌다 ([GitHub REST 검색](https://docs.github.com/en/rest/search/search#search-repositories)). 2023년 이후 velog 글을 em dash 유무로 나누면, em dash가 있는 글이 디렉터리·셸·메서드·콘텐츠에서는 규범형을 더 쓰고 매개변수와 칼럼에서는 덜 쓴다.

| 규범형(대안) | velog 2019–22 | velog 2026 | 2023년 이후 velog: em dash 있는 글 / 없는 글 |
|---|---|---|---|
| 디렉터리 | 36% | 57% | 65% / 27% |
| 셸 | 0% (10회) | 83% | 96% / 66% |
| 메서드 | 46% | 81% | 100% / 77% |
| 콘텐츠 | 80% | 87% | 100% / 84% |
| 릴리스 | 10% | 76% | 측정 안 함 |
| 매개변수(파라미터 대비) | 42% | 20% | 14% / 44% |
| 칼럼 | 10% | 6% | 2% / 10% |
| 오픈 소스(띄움) | 46% | 8% | 7% / 7% |
| 리팩터링 | 3% | 11% | 24% / 13% |
| 리포지터리 | 0% | 0% | 측정 안 함 |

이 결과는 LLM이 규범을 따르기보다 학습 자료에서 우세한 형태를 재현한다는 가설과 맞는다. 기계 번역 벤더 문서와 현지화를 규범형이 장악한 단어(디렉터리·셸·메서드·콘텐츠)에서는 규범형 쪽으로, 편집된 문서에서도 업계형이 흔한 컬럼과 국내 개발 글에서 다수인 파라미터에서는 업계형 쪽으로 기운다. 이 해석은 em dash라는 대리 지표에 기댄 가설이다. 그러나 편집된 출처도 이미 기계의 출력이라는 점은 측정으로 확인된다. Microsoft Learn 표본 122쪽 중 **115쪽**이 메타데이터에 기계 번역(MT)으로 표시되어 있고(사람 번역은 4쪽), AWS 무작위 가이드 112쪽 중 93쪽에 기계 번역 안내가 붙어 있으며, GitHub Docs 133쪽 모두에 "이 콘텐츠 중 일부는 기계 또는 AI로 번역되었을 수 있습니다" 배너가 있다 ([Microsoft Learn](https://learn.microsoft.com/ko-kr/), [AWS](https://docs.aws.amazon.com/ko_kr/), [GitHub Docs 예](https://docs.github.com/ko/pull-requests/get-started/about-forks)). 그래서 벤더 문서의 철자는 작성자가 아니라 용어집이 정하고, Microsoft 용어집의 repository→리포지토리가 Microsoft Learn·GitHub Docs·VS Code에 함께 나타난다. 2026년에는 현지화와 사내 편집도 모델을 쓴다. javascript.info 한국어판은 번역에 tech-translation-ko 에이전트 스킬을 쓰고 "용어집 위반은 스킬의 린터가 자동으로 검사"한다고 밝히며 ([javascript.info README](https://github.com/javascript-tutorial/ko.javascript.info/blob/2489814d15d09791bf6edfe00774ce0171e3bd1e/README.md)), 토스는 테크니컬 라이팅 가이드로 문서 PR에 AI 리뷰 봇을 붙였다 ([토스 '5. Technical Writer, 사라질 결심'](https://toss.tech/article/technical-writing-5)).

이 사정이 판단에 주는 영향은 셋이다. 첫째, 분류의 뼈대는 흔들리지 않는다. 관용이 굳은 6개는 2023년 이전 README와 2019~2022년 velog에서도 규범형이 많아야 3분의 1이었고, 2026년에도 타깃(47%)을 빼면 11% 이하다. 규범 23개는 2010~2019년 IT 도서 제목처럼 LLM 이전의 편집된 출처에서 이미 우세했다. 둘째, 갈리는 4개가 규범으로 수렴하고 있다는 해석은 쓸 수 없다. 릴리스 10%→76% 같은 상승분이 사람의 변화인지 모델 출력의 유입인지 이 자료로는 나눌 수 없으므로, 2026년 수치를 근거로 이 단어들의 린터 강도를 낮추거나 높여서는 안 된다. 셋째, 순환의 위험이 있다. SimpleKorean의 출력은 내년의 '업계 실사용'이 된다. 2026년 빈도를 그대로 규칙의 근거로 삼으면 모델의 습관을 규칙으로 굳혀 다시 모델에 먹이게 된다. 근거의 순서는 국립국어원 판정, 근거를 기록한 사람의 용어집 결정, 2023년 이전 사람 글과 편집된 코퍼스, 2026년 편집 안 된 글 순이어야 한다.

같은 자료는 원칙보다 목록이 출력을 묶는다는 점도 보여 준다. React 한국어 문서는 textlint로 강제하는 용어집 단어를 **99.8~100%** 지키지만, 같은 저장소에서 린트 대상이 아닌 단어는 릴리즈 160 대 릴리스 33, 리팩토링 20 대 리팩터링 1, 에러 92 대 오류 348로 섞였다 ([React textlint 용어집](https://github.com/reactjs/ko.react.dev/blob/89f79e9e971e9ad424ea5ebabdf8d5fa66c87375/textlint/data/rules/translateGlossary.js)). 스킬 린터로 용어집을 검사하는 javascript.info도 해당 단어에서 97~100% 일관된다. 카카오 가이드처럼 '표기법을 따르라'는 원칙만 주면 미정어와 선택어는 쓰는 사람, 또는 모델의 습관이 채운다.

## SimpleKorean은 원칙 한 줄에 여섯 무리 목록과 두 검사를 붙여야 한다

초안의 원칙은 23개 단어에서 실사용과 충돌하지 않는다. 예시로 든 디렉터리·메시지·애플리케이션은 용례·표준국어대사전·우리말샘이 모두 받치는 가장 단단한 단어이기도 하다. 다만 디렉터리는 '업계도 그렇게 쓴다'는 근거로는 가장 약하다(README 14%). 그러니 원칙은 그대로 두고, 원칙이 답을 내지 못하는 자리에 목록과 예외를 붙이면 된다. SimpleEnglish가 STE 사전에 맡기는 자리를 ([AminBlg/SimpleEnglish](https://github.com/AminBlg/SimpleEnglish)) SimpleKorean의 표기 규칙에서는 이 목록이 맡는다. 규칙 문구는 다음처럼 쓰기를 권한다.

> 외래어는 외래어 표기법과 국립국어원 용례를 따른다(디렉터리, 메시지, 애플리케이션). 단어 목록에 있는 단어는 목록의 형태를 쓴다. 규범 표기가 실제로 거의 쓰이지 않는 단어는 우리말 대응어를 쓴다(저장소, 본문, 열, 대상). 공식 표기가 없는 단어는 목록이 정한 형태를 쓴다(리디렉션, 리팩터링). 전문 용어 합성어는 붙여 쓴다(기본값, 매개변수). 제품 이름, 화면 문구 인용, API 객체 이름, 코드는 원래 표기를 그대로 둔다. 한 문서에서 한 개념은 한 형태로만 쓴다.

### 표기는 두 모드가 같게 쓰고 검사 강도만 다르게 둔다

글을 쓰는 형태는 두 모드가 같아야 한다. 모드마다 쓰는 형태가 다르면 한 저장소의 문서가 모드에 따라 갈라지고, 일관성 검사가 기준을 잃는다. 모드가 다르게 하는 일은 기존 문서와 사람이 쓴 글을 얼마나 세게 검사하느냐다.

| 무리 | 단어 | 글을 쓸 때 | 기본 모드 린터 | 엄격 모드 린터 |
|---|---|---|---|---|
| ① 규범=관용 (23) | 메시지·애플리케이션·콘텐츠·아키텍처·스레드·메서드·라이선스·액세스·스케줄·비즈니스·세팅·매뉴얼·캐시·대시보드·해시·포맷·렌더링·트랜잭션·버전·헤더·데이터·컴포넌트·프레임워크 | 규범형 | 변이형 오류(1:1 자동 수정) | 오류 |
| ② 출처별로 갈림 (4) | 디렉터리·릴리스·셸·리디렉션 | 규범형 | 디렉토리·릴리즈·쉘·리다이렉션 경고 | 오류 |
| ③ 관용이 굳음 (4) | repository·body·column·target | 저장소·본문·열·대상(이름이 굳은 개념은 타깃) | 리포지토리·레포지토리·레포·바디·컬럼·타겟 경고와 대응어 제안 | 위 변이형 오류, 리포지터리·보디·칼럼은 지정형 아님 경고 |
| ④ 공식 표기 없음 (2) | redirect·refactoring | 리디렉션(하다)·리팩터링 | 문서 안 혼용만 경고 | 리다이렉트·리팩토링 경고 |
| ⑤ 고유어·한자어 대 외래어 | error·parameter·user·default·deploy | 오류·매개변수·사용자·기본값·배포 | 문서 안 혼용만 경고 | 에러·파라미터·유저·디폴트·디플로이 경고 |
| ⑥ 띄어쓰기 | 기본값·매개변수·반환값·오픈소스 | 붙임 | '기본 값' 경고, 나머지는 문서 안 혼용만 경고 | '기본 값' 오류, 나머지 띄운 형태 경고 |
| 모든 무리 | 문서 안 일관성 | 한 개념 한 형태 | 경고 | 오류 |

강도는 근거의 종류와 실사용의 일치 여부로 정했다. 국립국어원 자료가 규범 표기를 정했고 실사용도 규범형인 ①에서는 다른 철자를 두 모드 모두 오류로 두고 자동 수정한다. 1:1 치환이라 뜻이 바뀌지 않고, 고쳐도 독자가 어색해하지 않는다. 규범 표기는 정해졌지만 업계가 갈리거나 관용이 굳은 ②③은 기본 모드에서 경고로 알리고 엄격 모드에서 오류로 막는다. 기본 모드에서 이것까지 오류로 두면, README 속 디렉터리 계열 출현의 **86%**를 차지하는 디렉토리처럼 사람이 써 온 문서를 대량으로 지적하게 된다. 규범 표기가 없거나(④) 규범이 두 형태를 모두 허용하는 자리(⑤⑥)는 어느 쪽도 틀렸다고 할 수 없으므로, 기본 모드는 문서 안 혼용만 지적하고 엄격 모드도 지정형이 아닌 형태를 경고로만 둔다. 예외는 우리말샘이 한 단어로 올린 기본값의 띄어쓰기 하나다. 린터 메시지도 근거를 따라야 한다. 엄격 모드의 리다이렉트 경고는 '규범 위반'이 아니라 'SimpleKorean 엄격 모드의 지정형은 리디렉션'이라고 말해야 한다. 엄격 모드를 CI 관문으로 쓰는 프로젝트는 경고까지 실패로 처리하도록 설정할 수 있다.

④⑤⑥의 지정형은 근거가 가장 넓게 겹치는 형태로 골랐다. redirect는 우리말샘 표제어이자 Microsoft 용어집의 대응어인 리디렉션(동사는 '리디렉션하다'), refactoring은 국립국어원 유추 안내와 Microsoft 용어집, 벤더 문서가 함께 쓰는 리팩터링이다. 고유어·한자어 쪽은 UI 문자열과 글로벌 벤더가 모두 쓰는 오류, 표준국어대사전이 뜻풀이를 싣고 다듬은 말이 권하는 매개변수, 다듬은 말 고시의 사용자, 벤더 문서·현지화·블로그에서 97~100%인 기본값과 배포다 ([다듬은 말 파라미터](https://korean.go.kr/front/imprv/refineView.do?mn_id=158&imprv_refine_seq=11857&pageIndex=1), [다듬은 말 유저](https://korean.go.kr/front/imprv/refineView.do?mn_id=158&imprv_refine_seq=20480&pageIndex=1), [다듬은 말 에러](https://korean.go.kr/front/imprv/refineView.do?mn_id=158&imprv_refine_seq=7602&pageIndex=1)). 띄어쓰기는 단어마다 고르지 말고 '전문 용어 합성어는 붙여 쓴다' 한 규칙으로 묶는다. 기본값은 사전이 한 단어로 정했고, 매개변수와 오픈소스는 맞춤법과 표기법이 붙여 쓰기를 허용하며, 반환값은 같은 '-값' 꼴이라 함께 붙인다. KS A 0001:2023 부속서 H도 전문용어를 가능한 한 붙여 쓰라고 하고 ([KS A 0001 기계가독 원문](https://standard.go.kr/KSCI/api/std/viewMachine.do?reformNo=40&tmprKsNo=KSA0001&formType=STD)), 편집 안 된 글에서도 붙여 쓰기가 다수다. 반환값은 현지화와 벤더 문서에서는 띄우는 쪽이 다수이므로, Microsoft·GitHub 문서를 옮기는 프로젝트처럼 띄우는 쪽을 원하면 설정 하나로 바꿀 수 있게 둔다.

### 관용이 굳은 단어는 우리말 대응어로 비켜 간다

③의 네 단어에서 세 선택지를 비교하면 대응어가 남는다. 규범형만 강제하면 벤더 표본 1,104회 중 0회인 리포지터리, 어느 코퍼스에도 없는 보디처럼 독자가 공식 문서에서 본 적 없는 형태를 쓰게 된다. 업계형을 따르면 오표기를 규칙으로 승인하게 되고, '업계'가 하나가 아니라는 문제도 생긴다. 리포지토리는 Microsoft 계열이, 레포지토리와 레포는 개발자 커뮤니티가 쓰고, 어느 쪽을 고를지는 따르는 회사에 달려 있다. 대응어는 규범에 맞으면서 주요 벤더의 선례도 갖는다. 저장소는 우리말샘 표제어이고 Google·토스페이먼츠·JetBrains·Pro Git·네이버 D2가 쓰며, 블로그에서 코드 저장소 뜻으로 쓴 말 가운데 가장 많다(**41%**, 레포 37%, 리포지터리류 22%). 본문·열·대상은 Microsoft 용어집이 body·column·target에 붙인 말이고, 대상은 국립국어원 다듬은 말의 전산기 용어(1997)와 Android도 쓴다 ([다듬은 말 타깃](https://korean.go.kr/front/imprv/refineView.do?mn_id=158&pageIndex=1&imprv_refine_seq=11552)).

저장소에는 비용이 있다. 블로그의 '저장소' 461회 가운데 252회는 Redis 저장소·상태 저장소 같은 데이터 저장 공간을 가리켰다. 그래서 처음 나올 때 '저장소(repository)'나 'Git 저장소'로 한정하고, 데이터 저장 공간은 '데이터 저장소'로 구별해 쓰게 해야 한다. 타깃은 규범형이고 JetBrains가 822번 쓰므로, 빌드 타깃처럼 이름이 굳은 개념에는 남긴다. 토스처럼 업계형을 정책으로 정했거나 카카오 개발자 문서처럼 업계형이 굳은 팀은 ③④의 지정형을 프로젝트 설정에서 리포지토리·컬럼·리다이렉트 등으로 바꿀 수 있어야 한다. 그때도 일관성 검사는 그대로 돈다.

목록이 손대지 않는 자리도 정해야 한다. 코드 블록·인라인 코드·URL·파일 경로, 제품과 앱 이름(디렉토리 유틸리티), 화면 문구를 그대로 인용한 부분, Kubernetes의 디플로이먼트 같은 API 객체 이름, 하이퍼파라미터·모노레포처럼 굳은 합성어는 검사에서 뺀다. 국립국어원 용례가 국내 고유명사 '쉘 (사)'를 예외로 둔 것과 같은 이치다. 부분 문자열 검사는 거짓 일치를 낸다. 이번 측정에서 거른 것만 해도 캐시백, 캄보디아(보디), 브리티시컬럼비아(컬럼), 이해시키다(해시), 레포트·텔레포트(레포), 쉘프(shelf), 컨버전(버전)이 있었다. PyTorch 문서의 파라미터 91회 중 25회는 하이퍼파라미터였고, 블로그의 레포 175회 중 105회는 모노레포 같은 합성어였다. 린터는 이 목록을 예외로 싣고 형태소 단위로 맞춰야 한다.

### 일관성 검사는 규범 검사와 따로 돈다

일관성 검사는 규범 검사와 별개로 돌린다. 카카오페이처럼 비규범형으로 한결같은 블로그와 MDN처럼 규범형이 다수인데도 문서 안에서 섞는 번역이 모두 있으므로, 두 검사를 하나로 합치면 어느 한쪽 문제를 놓친다. 한 문서 안에서 같은 개념에 둘 이상의 형태가 나오면 소수 형태를 지적한다. 철자 변이형(디렉터리/디렉토리), 선택어(오류/에러), 띄어쓰기(반환값/반환 값), 대응어 쌍(저장소/리포지터리)이 모두 대상이다. 기준 형태는 기본 모드에서는 문서에 먼저 나온 형태, 엄격 모드에서는 지정형이다. 관리되는 프로젝트는 이미 이 수준에 있다. 현지화 코퍼스에서 한 파일 안에 두 형태가 섞인 문서는 대부분 0~10%이고, 용어집을 CI 린트나 스킬 린터로 강제하는 React와 javascript.info는 해당 단어에서 97~100% 일관된다. 앱과 애플리케이션은 본말과 준말로 둘 다 규범형이고 벤더마다 제품 성격에 따라 고르므로, 프로젝트가 정하지 않는 한 일관성 쌍으로 묶지 않는다. 같은 말을 두 뜻으로 쓰는 반대 문제, 곧 repository와 storage를 모두 '저장소'로 쓰는 경우는 문자열로 잡을 수 없다. 블로그 조사에서는 이 뜻을 모델 판정으로 갈랐다. 판정 모델이 앞쪽 선택지로 기우는 경향이 알려져 있어 순서를 바꿔 두 번 물었고 ([Jev 1.13 특성 문서](https://docs.typesafe.ai/model-jaggedness/jev-1.13)), 두 판정은 743곳 중 729곳(98.1%)에서 같았다. 엄격 모드에는 이런 뜻 판정 경고를 선택 기능으로 둘 수 있다.

### 목록 항목은 근거와 측정 시점을 함께 싣는다

목록은 ko.react.dev 용어집처럼 '잡아낼 형태 → 쓸 형태 + 결정 기록' 구조를 쓰되 ([React textlint 용어집](https://github.com/reactjs/ko.react.dev/blob/89f79e9e971e9ad424ea5ebabdf8d5fa66c87375/textlint/data/rules/translateGlossary.js)), 무리, 모드별 강도, 허용형, 예외, 국립국어원 근거의 종류와 링크, 출처별 실사용과 측정 날짜, 2023년 이전 사람 기준선을 필드로 둔다. 예를 들면 다음과 같다.

```yaml
- concept: repository
  group: 3                     # 관용이 굳은 단어
  write: 저장소
  first_mention: 저장소(repository)
  accept: [저장소, 리포지터리]   # 규범 위반으로 보지 않는 형태(엄격 모드는 지정형 외 경고)
  flag:
    forms: [리포지토리, 레포지토리, 레포지터리, 레포]
    default: warning
    strict: error
    suggest: 저장소
  skip: [모노레포, 멀티레포]     # 굳은 합성어
  basis:
    kind: 우리말샘 규범 표기 지시(용례·표준국어대사전에는 없음)
    url: https://opendict.korean.go.kr/dictionary/view?sense_no=724814&viewType=confirm
  practice:
    measured: 2026-10-07
    vendor_docs: 리포지터리 0/1104
    blogs_code_repo_sense: 저장소 41%, 레포 37%, 리포지터리류 22%
    human_pre2023: README 리포지터리 1/86
  decision: <결정 PR 링크>
```

항목에는 판정과 링크만 담고 사전 뜻풀이는 옮기지 않는다. 우리말샘은 CC BY-SA 2.0 KR이고 외래어 표기 용례 오픈 API는 공공누리 제2유형(비상업)이라 내용을 MIT 저장소에 실을 수 없지만, 외래어 표기법 같은 고시는 저작권 보호 대상이 아니다 ([국어사전 통합 누리집 저작권 정책](https://kdict.korean.go.kr/info/copyright), [공공데이터포털 외래어 표기 용례 API](https://www.data.go.kr/data/15112892/openapi.do), [저작권법](https://www.law.go.kr/법령/저작권법)). 프로젝트 재정의는 무리별로 범위를 둔다. ②~⑥은 프로젝트가 지정형을 바꿀 수 있게 하고(Kubernetes처럼 리포지터리, 토스처럼 릴리즈·컬럼, 카카오처럼 파라미터), ①의 23개를 바꿀 때는 PyTorch의 메소드처럼 이유를 기록하게 한다. 목록은 33개 밖으로도 넓혀야 한다. 토스 가이드의 예시어인 프런트엔드/프론트엔드는 블로그 22곳 합산에서 프론트엔드가 79%지만, 우아한형제들은 프런트엔드 49 대 16으로 반대다 ([우아한형제들 기술 블로그](https://techblog.woowahan.com)). 측정은 해마다 다시 하되 2023년 이전 기준선과 2026년 이후 글을 나눠 싣고, 국립국어원이 method·redirect·refactoring의 표기를 정하면 해당 항목의 무리를 옮긴다.

## 결론

규범과 업계의 거리는 철학이 아니라 열 개 남짓한 단어의 목록 문제다. 33개 가운데 23개는 이미 출처 유형을 가리지 않고 규범대로 쓰이고, 나머지도 '편집했는가'와 '어느 용어집에서 왔는가'라는 두 경계를 따라 예측 가능하게 갈린다. 글로벌 벤더의 한국어는 Microsoft 용어집 같은 몇 개의 결정이 기계 번역을 타고 퍼진 결과이고, 국내 회사의 문서는 개발 현장의 말투를 옮긴다. 그래서 '업계 표기를 따른다'는 정책은 어느 업계인지 정하지 않으면 정의조차 되지 않는다. repository 하나에 리포지토리, 레포지토리, 레포, 저장소가 모두 업계 표기다. 규범은 하나뿐인 공통 기준이고, 규범형이 실제로 쓰이지 않는 몇 자리는 규범에 맞으면서 주요 벤더도 쓰는 우리말 대응어가 메운다.

더 큰 함의는 영향의 방향에 있다. 2026년의 '실사용'에는 이미 용어집과 모델 기본값이 깊이 섞여 있고, SimpleKorean의 단어 목록도 관찰자가 아니라 그런 용어 결정의 하나가 되어 다음 해의 실사용을 만든다. 그러므로 목록은 최근 빈도를 따라가기보다 근거의 무게와 측정 시점을 드러내야 한다. 또 엄격 모드 전후 출력의 표기 분포를 공개해, 스킬이 스스로 만든 변화를 사람의 관행과 구별해 잴 수 있어야 한다. 그렇게 해야 몇 년 뒤의 조사자가 이 보고서보다 깨끗한 기준선을 가질 수 있다.
