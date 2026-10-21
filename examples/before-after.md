# 전후 예시

'전'은 스킬 없이 만든 원본 출력입니다. '후'는 같은 과제를 스킬을 켜고 만든 원본 출력입니다. 두 글 모두 고치지 않고 옮겼습니다. 다듬기 과제에는 두 조건에 준 초안도 싣습니다. 과제와 질문은 측정 전에 정했습니다(`evals/make_examples.py`의 PICKS). `python3 evals/check_numbers.py`가 이 파일의 글을 원본 파일과 글자 하나까지 대조합니다.

## 초안 다듬기(절차문)

초안: `evals/results/2026-10-21/inputs/scenarios.json`의 `polish` 과제

<!-- draft: evals/results/2026-10-21/inputs/scenarios.json#polish -->
<!-- simple-korean: off -->
> ## 문제 해결
>
> **Postgres 연결 타임아웃** — sqlpipe가 `connection timed out` 오류를 내면 대부분 방화벽·보안 그룹이 5432 포트를 막고 있는 것입니다. `nc -zv <호스트> 5432`로 연결되는지 확인해 보시기 바랍니다.
>
> **S3 권한 오류** — `AccessDenied`가 나면 IAM 정책·버킷 정책에 읽기·쓰기 권한(`s3:GetObject`, `s3:PutObject`)이 있는지 확인하세요. 먼저 `aws sts get-caller-identity`로 지금 쓰는 자격 증명을 확인하는 것이 좋습니다.
<!-- simple-korean: on -->

전: 스킬 없음, `evals/results/2026-10-21/docs/baseline__polish__r1.json`

<!-- source: evals/results/2026-10-21/docs/baseline__polish__r1.json -->
<!-- simple-korean: off -->
> ## 문제 해결
>
> **Postgres 연결 타임아웃** — sqlpipe에서 `connection timed out` 오류가 나면 대개 방화벽이나 보안 그룹이 5432 포트를 막고 있는 경우입니다. `nc -zv <호스트> 5432`로 연결 가능 여부를 먼저 확인하세요.
>
> **S3 권한 오류** — `AccessDenied`가 나면 IAM 정책과 버킷 정책에 읽기·쓰기 권한(`s3:GetObject`, `s3:PutObject`)이 있는지 확인하세요. 그 전에 `aws sts get-caller-identity`로 현재 사용 중인 자격 증명이 맞는지 먼저 확인하는 것이 좋습니다.
<!-- simple-korean: on -->

후: 기본 모드, `evals/results/2026-10-21/docs/plain__polish__r1.json`

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

## README 소개(설명문)

전: 스킬 없음, `evals/results/2026-10-21/docs/baseline__readme-intro__r1.json`

<!-- source: evals/results/2026-10-21/docs/baseline__readme-intro__r1.json -->
<!-- simple-korean: off -->
> sqlpipe는 Postgres 테이블을 Parquet 파일로 변환해 S3에 동기화하는 CLI 도구입니다. 복잡한 ETL 파이프라인이나 별도 인프라 없이, 명령어 한 줄로 운영 데이터베이스의 데이터를 분석용 데이터 레이크에 옮길 수 있습니다.
>
> 동기화할 테이블과 대상 S3 경로만 지정하면 스키마를 자동으로 Parquet 타입에 매핑하고, 대용량 테이블도 나누어 안정적으로 전송합니다. 주기적인 실행도 간단해서 cron이나 CI 작업에 바로 연결해 쓸 수 있습니다.
<!-- simple-korean: on -->

후: 기본 모드, `evals/results/2026-10-21/docs/plain__readme-intro__r1.json`

<!-- source: evals/results/2026-10-21/docs/plain__readme-intro__r1.json -->
<!-- simple-korean: off -->
> sqlpipe는 Postgres 테이블을 Parquet 파일로 변환해 S3에 동기화하는 CLI 도구입니다. 테이블 하나를 지정하면 sqlpipe가 행을 읽어 Parquet 파일로 쓰고 S3 버킷에 올립니다.
>
> sqlpipe를 실행하는 호스트는 Postgres 포트와 S3에 모두 연결할 수 있어야 합니다. 연결하지 못하면 sqlpipe는 오류를 내고 멈춥니다.
<!-- simple-korean: on -->

## 문제 해결(절차문)

전: 스킬 없음, `evals/results/2026-10-21/docs/baseline__troubleshooting__r1.json`

<!-- source: evals/results/2026-10-21/docs/baseline__troubleshooting__r1.json -->
<!-- simple-korean: off -->
> ## 문제 해결
>
> ### Postgres 연결 타임아웃
> `connection timed out` 오류가 나면 먼저 호스트와 포트(기본 5432)에 네트워크로 접근되는지 확인하세요. `nc -vz <호스트> 5432`로 점검할 수 있습니다. 방화벽이나 보안 그룹이 현재 IP를 허용하는지, VPN이 필요한 환경인지도 살펴보세요. 연결은 되는데 응답이 느리다면 `--connect-timeout 30`처럼 제한 시간을 늘려 보세요. 접속 URL에 `sslmode`가 서버 설정과 맞게 지정되어 있는지도 확인하세요.
>
> ### S3 권한 오류
> `AccessDenied` 또는 `403`이 나오면 현재 자격 증명을 `aws sts get-caller-identity`로 확인하세요. 의도한 계정과 역할이 아니라면 `AWS_PROFILE` 설정을 바로잡으세요. 해당 역할에는 대상 버킷에 대한 `s3:GetObject`, `s3:PutObject`, `s3:ListBucket` 권한이 필요합니다. `ListBucket`은 버킷 ARN에, 나머지는 `버킷/*`에 부여해야 합니다. 버킷 정책과 KMS 암호화 키 권한도 함께 점검하세요.
<!-- simple-korean: on -->

후: 기본 모드, `evals/results/2026-10-21/docs/plain__troubleshooting__r1.json`

<!-- source: evals/results/2026-10-21/docs/plain__troubleshooting__r1.json -->
<!-- simple-korean: off -->
> ## 문제 해결
>
> ### Postgres 연결 타임아웃
>
> sqlpipe는 Postgres 포트(기본값 5432)에 연결하지 못하면 `dial tcp: i/o timeout` 오류를 내고 멈춥니다. 보통 방화벽이나 보안 그룹이 연결을 막습니다.
>
> 1. sqlpipe를 실행하는 호스트가 Postgres 포트에 연결할 수 있는지 확인하세요.
> 2. 데이터베이스가 관리형(RDS, Cloud SQL)이면, 인스턴스가 sqlpipe의 IP에서 오는 연결을 허용하는지 확인하세요.
>
> ### S3 권한 오류
>
> sqlpipe는 S3 버킷에 쓸 권한이 없으면 `AccessDenied` 오류를 내고 멈춥니다. 자격 증명(credentials)이 없거나, 자격 증명에 연결된 정책이 버킷 접근을 허용하지 않을 때 이 오류가 납니다.
>
> 1. sqlpipe를 실행하는 호스트에 AWS 자격 증명이 설정되어 있는지 확인하세요.
> 2. 자격 증명에 연결된 IAM 정책이 대상 버킷의 `s3:PutObject` 권한을 허용하는지 확인하세요.
> 3. 버킷 정책이 해당 자격 증명을 거부하지 않는지 확인하세요.
<!-- simple-korean: on -->

## 오류 메시지

전: 스킬 없음, `evals/results/2026-10-21/docs/baseline__error-message__r1.json`

<!-- source: evals/results/2026-10-21/docs/baseline__error-message__r1.json -->
<!-- simple-korean: off -->
> S3 업로드 실패: s3://<bucket>/<key> 에 객체를 쓸 수 없습니다 (AccessDenied).
> 현재 IAM 자격 증명에 s3:PutObject 권한이 없습니다.
> 해당 버킷/경로에 대한 s3:PutObject 권한을 IAM 정책에 추가한 뒤 다시 시도하세요.
<!-- simple-korean: on -->

후: 기본 모드, `evals/results/2026-10-21/docs/plain__error-message__r1.json`

<!-- source: evals/results/2026-10-21/docs/plain__error-message__r1.json -->
<!-- simple-korean: off -->
> ```
> 오류: S3 업로드가 AccessDenied로 실패했습니다. 현재 IAM 자격 증명에 `s3:PutObject` 권한이 없습니다.
> IAM 정책에 대상 버킷과 키 접두사에 대한 `s3:PutObject` 권한을 추가하세요.
> 권한을 추가한 뒤 sqlpipe를 다시 실행하세요.
> ```
<!-- simple-korean: on -->

## 릴리스 노트(엄격 모드)

전: 스킬 없음, `evals/results/2026-10-21/docs/baseline__release-notes__r1.json`

<!-- source: evals/results/2026-10-21/docs/baseline__release-notes__r1.json -->
<!-- simple-korean: off -->
> **sqlpipe v2.0 릴리스 노트**
>
> **⚠️ 호환성 깨짐**
> `/v2/users` 응답의 `name` 필드가 `first_name`과 `last_name`으로 분리되었습니다. `name`을 사용하는 클라이언트는 업그레이드 전에 코드를 수정해야 합니다.
>
> **새 기능**
> - `--incremental` 플래그 추가: 변경된 데이터만 처리할 수 있습니다.
>
> **성능 개선**
> - Parquet 쓰기 속도가 40% 빨라졌습니다.
>
> v2.0으로 업그레이드하기 전에 위 호환성 변경 사항을 꼭 확인해 주세요.
<!-- simple-korean: on -->

후: 엄격 모드, `evals/results/2026-10-21/docs/strict__release-notes__r1.json`

<!-- source: evals/results/2026-10-21/docs/strict__release-notes__r1.json -->
<!-- simple-korean: off -->
> 엄격 모드: 한국어 통제 언어 국가 표준은 없습니다. 이 기준은 KS A 0001과 공개 연구를 바탕으로 한 비공식 기준입니다.
>
> # sqlpipe v2.0 릴리스 노트
>
> ## 호환성이 깨지는 변경
>
> `/v2/users`의 `name` 필드를 `first_name`과 `last_name`으로 나눴습니다. `name` 필드를 읽는 클라이언트는 새 필드를 읽도록 고쳐야 합니다.
>
> ## 새 기능
>
> `--incremental` 플래그를 추가했습니다. 이 플래그는 마지막 실행 이후 바뀐 행만 처리합니다.
>
> ## 성능
>
> Parquet 쓰기가 40% 빨라졌습니다.
<!-- simple-korean: on -->

## 답변: OOMKilled 질문

전: 스킬 없음, `evals/results/2026-10-21/reply/baseline__oom__r1.txt`

<!-- source: evals/results/2026-10-21/reply/baseline__oom__r1.txt -->
<!-- simple-korean: off -->
> 클러스터나 매니페스트를 아직 보지 못했습니다. 그래서 아래는 일반적인 원인과 진단 순서입니다. 실제 수치를 알려주시면 구체적으로 짚어드리겠습니다.
>
> ## 무슨 일이 일어나는 건가
>
> OOMKilled는 컨테이너가 `resources.limits.memory`를 넘겨서 커널의 cgroup OOM killer가 프로세스를 SIGKILL(종료 코드 137)로 죽였다는 뜻입니다. 그러면 kubelet이 `restartPolicy`에 따라 컨테이너를 다시 띄우고, 이 과정이 반복되면 `CrashLoopBackOff`가 됩니다. 노드 전체의 메모리가 부족한 경우가 아니라 **컨테이너 단위의 limit 초과**가 보통입니다. 다만 노드 메모리 압박으로 인한 eviction은 `Evicted`로 표시되어 OOMKilled와 구분됩니다.
>
> API와 워커가 동시에 죽는다면 다음 원인 중 하나일 가능성이 큽니다.
>
> 1. **limit이 너무 낮음.** 기본값이나 복사해 온 값(예: 256Mi)이 실제 사용량보다 작습니다.
> 2. **최근 배포 이후 메모리 사용량 증가.** 두 파드가 같은 코드나 라이브러리를 공유하면 같이 터집니다.
> 3. **메모리 누수.** 시간이 지날수록 메모리가 계속 늘어납니다.
> 4. **런타임이 limit을 인식하지 못함.**
>    - JVM: 힙 설정(`-Xmx`)이 limit보다 크거나 off-heap 몫이 없는 경우
>    - Node: `--max-old-space-size`
>    - Python/Go: 캐시나 GOMEMLIMIT 미설정
> 5. **워커의 큰 작업.** 큰 페이로드를 통째로 메모리에 올리거나, concurrency가 너무 높거나, prefetch가 큰 경우입니다.
> 6. **API의 트래픽 급증.** 동시 요청마다 메모리가 늘어납니다.
>
> ## 확인 방법
>
> ```bash
> kubectl describe pod <pod> | grep -A5 "Last State"   # Reason: OOMKilled, Exit Code 137 확인
> kubectl top pod --containers -n <ns>                 # 현재 사용량 (metrics-server 필요)
> kubectl get pod <pod> -o jsonpath='{.spec.containers[*].resources}'
> kubectl get events -n <ns> --sort-by=.lastTimestamp | tail -30
> ```
>
> Prometheus나 Grafana가 있다면 `container_memory_working_set_bytes`를 limit과 겹쳐서 보세요. 그래프가 우상향이면 누수이고, 계단식이나 스파이크면 특정 요청이나 작업이 원인입니다. 재시작 직전에 limit에 닿는지도 확인하세요.
>
> ## 바꿔야 할 것
>
> - **limit과 request를 실측값 기준으로 조정합니다.** 피크 사용량에 20~30% 여유를 둔 값을 limit으로 잡습니다. 메모리는 압축할 수 없는 자원이라 **request와 limit을 같게** 두는 편이 안전합니다.
>   ```yaml
>   resources:
>     requests: { memory: "768Mi" }
>     limits:   { memory: "768Mi" }
>   ```
> - **런타임 설정을 limit에 맞춥니다.**
>   - JVM: `-XX:MaxRAMPercentage=70`
>   - Node: `--max-old-space-size`를 limit의 약 75%로
>   - Go: `GOMEMLIMIT`을 limit의 약 90%로
> - **워커는 concurrency, 배치 크기, prefetch를 줄이거나 스트리밍 처리로 바꿉니다.**
> - **API는 HPA로 수평 확장하고, 요청 크기와 동시성을 제한합니다.**
> - **누수라면 limit을 올려도 재시작 주기만 늘어납니다.** 이 경우 프로파일링(heap dump, pprof 등)으로 원인을 찾아야 합니다.
>
> limit을 올리기 전에 위 `describe` 결과와 메모리 그래프 모양, 그리고 최근 배포가 있었는지부터 확인하세요. 아래 정보를 주시면 어느 원인인지 좁혀드리겠습니다.
>
> - 사용 언어와 런타임
> - 현재 requests/limits 값
> - `kubectl describe pod`의 `Last State` 출력
>
> 매니페스트나 Helm values 파일이 이 환경에 있으면 경로를 알려주세요. 직접 읽고 수정안을 제안하겠습니다.
<!-- simple-korean: on -->

후: SimpleKorean, `evals/results/2026-10-21/reply/plain__oom__r1.txt`

<!-- source: evals/results/2026-10-21/reply/plain__oom__r1.txt -->
<!-- simple-korean: off -->
> 파드의 컨테이너가 메모리 한도(limit)를 넘어서 커널이 프로세스를 강제 종료하고 있습니다. kubelet이 컨테이너를 다시 시작하므로 재시작이 반복됩니다. 클러스터와 매니페스트는 제가 보지 못했습니다. 아래는 일반적인 원인과 확인 순서입니다.
>
> ## 무슨 일이 일어나는가
>
> 1. 컨테이너 메모리 사용량이 `resources.limits.memory`에 닿습니다.
> 2. 리눅스 OOM killer(메모리 부족 시 프로세스를 죽이는 커널 기능)가 프로세스에 SIGKILL을 보냅니다.
> 3. 종료 코드는 137이고 사유는 `OOMKilled`입니다.
> 4. kubelet이 컨테이너를 다시 시작합니다. 반복되면 `CrashLoopBackOff`로 바뀝니다.
>
> API와 워커가 모두 죽으면 공통 원인을 먼저 의심해야 합니다. 두 파드에 같은 한도 값이 있거나, 같은 런타임 설정을 쓰거나, 같은 노드에서 돌고 있을 수 있습니다.
>
> ## 먼저 확인할 것
>
> 사유와 종료 코드를 확인하세요. `<pod>`와 `<ns>`는 실제 값으로 바꾸세요.
>
> ```
> kubectl describe pod <pod> -n <ns>
> ```
>
> 출력의 `Last State: Terminated`에서 `Reason: OOMKilled`와 `Exit Code: 137`을 찾으세요.
>
> 현재 사용량과 한도를 비교하세요. 이 명령은 metrics-server가 설치되어 있어야 합니다.
>
> ```
> kubectl top pod -n <ns> --containers
> kubectl get pod <pod> -n <ns> -o jsonpath='{.spec.containers[*].resources}'
> ```
>
> ## 원인별 조치
>
> - 한도가 실제 사용량보다 낮으면 `limits.memory`를 올리세요. 평상시 최대 사용량보다 여유를 두어야 합니다.
> - 사용량이 시간에 따라 계속 오르면 메모리 누수입니다. 한도를 올려도 재시작 주기만 늘어납니다. 힙 프로파일을 떠서 코드를 고쳐야 합니다.
> - JVM이나 Node.js를 쓰면 힙 크기 설정이 컨테이너 한도보다 커서 죽을 수 있습니다. 힙 외 메모리(스레드 스택, 메타스페이스, 네이티브 버퍼)도 한도에 포함됩니다. JVM은 `-XX:MaxRAMPercentage=70` 같은 값으로, Node.js는 `--max-old-space-size`로 힙을 한도보다 작게 맞춰야 합니다.
> - 워커가 큰 작업을 한꺼번에 처리하면 순간 사용량이 치솟습니다. 동시 처리 수나 배치 크기를 줄이세요.
> - `requests.memory`가 너무 낮으면 노드에 파드가 과하게 몰립니다. 노드 전체 메모리가 부족해지면 한도 이내여도 종료될 수 있습니다. `requests`를 실제 평균 사용량에 맞추세요.
>
> ## 변경 예시
>
> ```yaml
> resources:
>   requests:
>     memory: "512Mi"
>   limits:
>     memory: "1Gi"
> ```
>
> 값은 `kubectl top`으로 본 실제 사용량을 기준으로 정해야 합니다.
>
> `kubectl describe` 출력과 `resources` 설정, 사용 중인 런타임(JVM, Node.js 등)을 알려 주시면 구체적인 값을 제안하겠습니다.
<!-- simple-korean: on -->

## 답변: 캐시 무효화 질문

전: 스킬 없음, `evals/results/2026-10-21/reply/baseline__cache__r1.txt`

<!-- source: evals/results/2026-10-21/reply/baseline__cache__r1.txt -->
<!-- simple-korean: off -->
> 이 세션에서는 파일을 읽거나 검색하는 도구를 쓸 수 없어서 코드를 직접 보지 못했습니다. 아래는 증상으로 추정한 내용이고, 실제 코드로 확인한 것이 아닙니다.
>
> ## 왜 그런가
>
> "최대 10분"이고 목록과 상세 모두 영향을 받는다면, 원인은 거의 **cache-aside 패턴에 TTL 600초를 걸어 두고, 가격을 바꿀 때 캐시를 무효화하지 않는 것**입니다.
>
> 1. 읽기 경로는 Redis를 먼저 조회합니다. 값이 있으면 그대로 반환하고, 없으면 DB에서 읽어 `SET key value EX 600`으로 저장합니다.
> 2. 가격 변경은 DB만 갱신하고 Redis 키는 건드리지 않습니다.
> 3. 그래서 키가 TTL로 만료될 때까지 옛 가격이 남습니다. 마지막으로 캐시에 채워진 시점에 따라 0~10분 동안 옛 가격이 보입니다.
>
> 목록과 상세가 모두 영향을 받는 것은 두 가지로 설명할 수 있습니다.
> - 가격이 상품 상세 캐시에도, 목록 캐시(페이지·카테고리·정렬별 키)에도 **각각 따로 복제되어** 있을 수 있습니다.
> - 목록 캐시가 상품 객체 전체를 통째로 저장하고 있을 수 있습니다.
>
> ## 어떻게 고치나
>
> **1. 쓰기 시 무효화 (기본 수정)**
> - DB 커밋 **후에** 해당 상품의 상세 키를 `DEL`합니다. 값을 `SET`으로 덮어쓰는 방식은 경쟁 상태가 생길 수 있어 `DEL`을 권장합니다.
> - 트랜잭션 안에서 지우면 커밋 전에 다른 요청이 옛 값을 다시 캐시에 채울 수 있습니다. `afterCommit` 훅이나 outbox/이벤트로 처리하세요.
>
> **2. 목록 캐시 문제 해결 (보통 이쪽이 더 까다롭습니다)**
> 목록 키는 조합이 많아서 하나씩 지우기 어렵습니다. 선택지는 세 가지입니다.
> - **목록에는 가격을 캐시하지 않기.** 목록은 상품 ID 순서만 캐시하고, 가격이나 상품 상세는 `MGET`으로 상품별 캐시에서 조합합니다. 이러면 상품 키 하나만 무효화해도 목록까지 반영됩니다. 가장 깔끔합니다.
> - **버전 키 사용.** `list:{category}:v{version}` 형태로 두고, 가격이 바뀌면 version을 `INCR`합니다. 옛 키는 TTL로 알아서 사라집니다.
> - **목록 TTL만 짧게(10~30초) 줄이기.** 단순하지만 완전한 해결은 아닙니다.
>
> **3. 보강 장치**
> - TTL을 600초에서 60~120초 정도로 줄여, 무효화가 실패해도 오차 상한을 낮춥니다.
> - 가격 변경이 여러 서비스나 배치에서 일어나면, 모든 경로가 같은 무효화 함수를 거치는지 확인하세요. 관리자 화면에서만 무효화하고 배치나 가격 동기화는 빠뜨린 경우가 흔합니다.
> - CDN이나 HTTP `Cache-Control`, 클라이언트 캐시(SWR 등)가 10분을 만드는 경우도 있습니다. Redis TTL이 정말 600초인지 먼저 확인해 보세요.
>
> ## 확인 방법
> - `redis-cli TTL <상품 키>`로 남은 TTL이 600 근처에서 줄어드는지 봅니다.
> - 가격 변경 코드에서 `del`, `evict`, `invalidate`, `@CacheEvict` 같은 호출이 있는지 확인합니다.
> - 응답 헤더(`Cache-Control`, `Age`)로 CDN이 개입하는지 확인합니다.
>
> 코드 위치(프로젝트 경로나 관련 파일)를 알려 주시면, 실제 캐시 키 구조와 가격 변경 경로를 보고 구체적인 수정안을 드리겠습니다.
<!-- simple-korean: on -->

후: SimpleKorean, `evals/results/2026-10-21/reply/plain__cache__r1.txt`

<!-- source: evals/results/2026-10-21/reply/plain__cache__r1.txt -->
<!-- simple-korean: off -->
> 원인은 가격을 바꿀 때 Redis 항목을 지우지 않아서, TTL(캐시 항목의 만료 시간)인 600초가 끝나야 값이 갱신되기 때문입니다. 코드를 직접 보지 않았으므로 가장 흔한 구조를 가정했습니다.
>
> ## 원인
>
> - 읽기 경로는 cache-aside(캐시에 없으면 DB에서 읽어 캐시에 채우는 방식)입니다.
> - 쓰기 경로는 DB만 갱신하고 Redis의 옛 값은 그대로 둡니다.
> - 목록과 상세가 각자 키에 가격을 복사해 저장하면 두 화면 모두 최대 10분간 옛 값을 보여 줍니다.
> - CDN이나 브라우저 캐시가 Redis 앞에 있으면 지연이 더 길어질 수 있습니다. 응답의 `Cache-Control` 헤더를 확인하세요.
>
> ## 수정
>
> 1. 가격 변경 트랜잭션이 커밋된 뒤에 상세 키를 삭제하세요. 커밋 전에 지우면 다른 요청이 옛 값을 다시 채웁니다.
> 2. 목록 캐시에는 상품 ID만 저장하세요. 가격은 상세 키에서 `MGET`으로 읽으세요. 키 하나만 지워도 두 화면이 함께 바뀝니다.
> 3. 목록에 가격을 넣어야 하면 키에 버전을 넣으세요. 예를 들어 `product:list:v{n}`으로 두고, 가격이 바뀌면 n을 올리세요. 옛 키는 TTL로 사라집니다.
> 4. TTL을 60초 안팎으로 줄이세요. 삭제가 실패해도 지연이 1분을 넘지 않습니다.
> 5. 삭제 요청을 이벤트 큐로 보내 재시도하세요. 앱이 커밋 직후 죽어도 캐시가 갱신됩니다.
>
> 1번과 2번만 적용해도 대부분의 지연이 사라집니다. 3번부터는 목록 구조와 트래픽에 따라 선택하세요.
<!-- simple-korean: on -->
