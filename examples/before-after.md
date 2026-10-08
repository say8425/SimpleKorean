# 전후 예시

'전'은 스킬 없이 만든 원본 출력이고, '후'는 같은 과제를 스킬을 켜고 만든 원본 출력입니다. 두 글 모두 고치지 않고 옮겼습니다. 과제와 질문은 측정 전에 정했습니다(`evals/make_examples.py`의 PICKS). `python3 evals/check_numbers.py`가 이 파일의 글을 원본 파일과 글자 하나까지 대조합니다.

## README 소개(설명문)

전: 스킬 없음, `evals/results/2026-10-08/docs/baseline__readme-intro__r1.json`

<!-- source: evals/results/2026-10-08/docs/baseline__readme-intro__r1.json -->
<!-- simple-korean: off -->
> sqlpipe는 Postgres 테이블을 Parquet 파일로 변환해 S3에 동기화하는 CLI 도구입니다. 명령 한 줄로 테이블을 읽어 컬럼 타입에 맞는 Parquet 스키마를 만들고, 지정한 버킷과 경로에 업로드합니다. 별도의 ETL 인프라 없이 분석용 데이터 레이크를 손쉽게 구성할 수 있습니다.
>
> 변경된 데이터만 증분 동기화하고, 대용량 테이블도 스트리밍으로 처리해 메모리 사용량을 낮게 유지합니다. 설정은 YAML 파일이나 환경 변수로 관리할 수 있어 cron이나 CI 파이프라인에도 쉽게 붙일 수 있습니다.
<!-- simple-korean: on -->

후: 기본 모드, `evals/results/2026-10-08/docs/plain__readme-intro__r1.json`

<!-- source: evals/results/2026-10-08/docs/plain__readme-intro__r1.json -->
<!-- simple-korean: off -->
> sqlpipe는 Postgres 테이블을 Parquet 파일로 변환해 S3에 동기화하는 CLI 도구입니다. 테이블을 하나씩 읽어 Parquet 파일로 쓰고, 지정한 S3 버킷에 올립니다.
>
> sqlpipe를 실행하는 호스트는 Postgres와 S3에 모두 연결할 수 있어야 합니다. 동기화할 테이블과 대상 버킷은 설정에서 지정하세요.
<!-- simple-korean: on -->

## 문제 해결(절차문)

전: 스킬 없음, `evals/results/2026-10-08/docs/baseline__troubleshooting__r1.json`

<!-- source: evals/results/2026-10-08/docs/baseline__troubleshooting__r1.json -->
<!-- simple-korean: off -->
> ## 문제 해결
>
> **Postgres 연결 타임아웃**
> `connection timed out` 오류가 나면 먼저 호스트와 포트(기본 5432)에 네트워크로 접근할 수 있는지 확인하세요. 방화벽, 보안 그룹, VPN 설정이 흔한 원인입니다. 서버가 느리게 응답하는 환경이라면 `--connect-timeout 30`처럼 제한 시간을 늘려 보세요. 클라우드 DB를 쓴다면 접속하는 IP가 허용 목록에 있는지도 확인하세요. 연결 문자열의 `sslmode` 값이 서버 설정과 맞는지도 점검하세요.
>
> **S3 권한 오류**
> `AccessDenied`나 `403`이 나오면 사용 중인 자격 증명이 맞는지 `aws sts get-caller-identity`로 확인하세요. 해당 IAM 역할에 대상 버킷의 `s3:GetObject`, `s3:PutObject`, `s3:ListBucket` 권한이 있어야 합니다. 버킷 정책이나 리전 설정이 다르지 않은지도 살펴보세요. 임시 자격 증명을 쓴다면 만료 여부도 확인하세요.
<!-- simple-korean: on -->

후: 기본 모드, `evals/results/2026-10-08/docs/plain__troubleshooting__r1.json`

<!-- source: evals/results/2026-10-08/docs/plain__troubleshooting__r1.json -->
<!-- simple-korean: off -->
> ## 문제 해결
>
> ### Postgres 연결 타임아웃
>
> sqlpipe가 `dial tcp: i/o timeout` 오류를 내고 멈추면, sqlpipe를 실행하는 호스트에서 Postgres 포트(기본값 5432)에 연결할 수 있는지 확인하세요. 보통 방화벽이나 보안 그룹이 연결을 막습니다. 데이터베이스가 관리형(RDS, Cloud SQL)이면, 인스턴스가 sqlpipe의 IP에서 오는 연결을 허용하는지 확인하세요.
>
> ### S3 권한 오류
>
> sqlpipe가 `AccessDenied` 오류를 내면, sqlpipe를 실행하는 호스트의 자격 증명이 대상 버킷에 쓸 수 있는지 확인하세요. IAM 정책에 `s3:PutObject` 권한이 있어야 합니다. 버킷 정책이 해당 역할을 막으면, 정책에서 그 역할을 허용하세요. 자격 증명은 환경 변수 `AWS_PROFILE`로 지정한 프로필에서 읽습니다.
<!-- simple-korean: on -->

## 오류 메시지

전: 스킬 없음, `evals/results/2026-10-08/docs/baseline__error-message__r1.json`

<!-- source: evals/results/2026-10-08/docs/baseline__error-message__r1.json -->
<!-- simple-korean: off -->
> S3 업로드 실패: 접근이 거부되었습니다(AccessDenied). 현재 IAM 자격 증명에 s3:PutObject 권한이 없습니다.
> 대상 버킷과 경로에 대한 s3:PutObject 권한을 IAM 정책에 추가한 뒤 다시 시도하세요.
> 사용 중인 자격 증명(프로필 또는 역할)이 의도한 것인지도 함께 확인하세요.
<!-- simple-korean: on -->

후: 기본 모드, `evals/results/2026-10-08/docs/plain__error-message__r1.json`

<!-- source: evals/results/2026-10-08/docs/plain__error-message__r1.json -->
<!-- simple-korean: off -->
> S3 업로드가 `AccessDenied` 오류로 실패했습니다. 사용 중인 IAM 자격 증명에 `s3:PutObject` 권한이 없습니다.
> IAM 정책에 `s3:PutObject`를 추가한 뒤 다시 실행하세요.
> 정책이 이미 있으면 버킷 정책이 업로드를 막는지 확인하세요.
<!-- simple-korean: on -->

## 릴리스 노트(엄격 모드)

전: 스킬 없음, `evals/results/2026-10-08/docs/baseline__release-notes__r1.json`

<!-- source: evals/results/2026-10-08/docs/baseline__release-notes__r1.json -->
<!-- simple-korean: off -->
> # sqlpipe v2.0 릴리스 노트
>
> **⚠️ 호환성 깨짐**
> - `/v2/users` 응답의 `name` 필드가 `first_name`과 `last_name`으로 분리되었습니다. `name`을 사용하는 클라이언트는 업그레이드 전에 새 필드를 사용하도록 수정해 주세요.
>
> **새 기능**
> - `--incremental` 플래그가 추가되었습니다. 변경된 데이터만 처리해 반복 실행 시간을 줄일 수 있습니다.
>
> **성능 개선**
> - Parquet 쓰기 속도가 약 40% 향상되었습니다.
<!-- simple-korean: on -->

후: 엄격 모드, `evals/results/2026-10-08/docs/strict__release-notes__r1.json`

<!-- source: evals/results/2026-10-08/docs/strict__release-notes__r1.json -->
<!-- simple-korean: off -->
> 한국어 통제 언어 국가 표준은 없으며, 이 기준은 KS A 0001과 공개 연구를 바탕으로 한 비공식 기준입니다.
>
> sqlpipe v2.0을 릴리스했습니다.
>
> 이번 버전에는 호환성을 깨는 변경(breaking change)이 있습니다. `/v2/users`의 `name` 필드가 `first_name`과 `last_name`으로 나뉘었습니다. `name` 필드를 읽는 코드가 있으면 업그레이드 전에 두 필드를 읽도록 고치세요.
>
> 새 기능도 있습니다. `--incremental` 플래그가 새로 생겼습니다. Parquet 쓰기가 40% 빨라졌습니다.
<!-- simple-korean: on -->

## 답변: OOMKilled 질문

전: 스킬 없음, `evals/results/2026-10-08/reply/baseline__oom__r1.txt`

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

후: SimpleKorean, `evals/results/2026-10-08/reply/plain__oom__r1.txt`

<!-- source: evals/results/2026-10-08/reply/plain__oom__r1.txt -->
<!-- simple-korean: off -->
> 파드가 OOMKilled로 재시작되면 컨테이너가 메모리 한도(`limits.memory`)를 넘겨 커널이 프로세스를 강제 종료한 것입니다. 해결하려면 한도를 올리거나 애플리케이션의 메모리 사용량을 줄여야 합니다.
>
> 컨테이너는 cgroup(프로세스의 자원 사용을 제한하는 리눅스 기능)으로 메모리 한도를 받습니다. 사용량이 한도를 넘으면 커널의 OOM killer가 프로세스에 SIGKILL을 보냅니다. 이때 종료 코드는 137입니다. kubelet은 종료된 컨테이너를 `restartPolicy`에 따라 다시 시작합니다. 같은 일이 반복되면 대기 시간이 늘어나며 CrashLoopBackOff 상태가 됩니다.
>
> 먼저 원인이 한도 초과인지 확인하세요. 아래 명령에서 `<파드>`는 실제 파드 이름으로 바꾸세요.
>
> ```
> kubectl describe pod <파드>
> kubectl top pod <파드> --containers
> ```
>
> describe 출력의 `Last State: Terminated`에 `Reason: OOMKilled`가 보이면 한도 초과입니다. `kubectl top`은 metrics-server가 설치되어 있어야 동작합니다.
>
> 한도가 너무 낮으면 `limits.memory`를 올리세요. 평소 사용량보다 여유를 두고 정하세요. `requests.memory`는 실제 사용량에 가깝게 설정해야 합니다. 그래야 스케줄러가 노드를 정확히 고릅니다.
>
> ```
> resources:
>   requests:
>     memory: "512Mi"
>   limits:
>     memory: "1Gi"
> ```
>
> 한도를 올려도 사용량이 계속 늘면 메모리 누수를 의심해야 합니다. 시간에 따른 사용량 그래프가 우상향하면 누수입니다. 이 경우 한도를 올려도 재시작 간격만 늘어납니다. 애플리케이션의 힙 프로파일을 보고 코드를 고치세요.
>
> 런타임 설정도 확인해야 합니다. 예를 들어 JVM은 컨테이너 한도보다 큰 힙을 잡으면 종료됩니다. `-XX:MaxRAMPercentage=75` 같은 옵션으로 힙을 한도의 일부로 제한하세요. Node.js는 `--max-old-space-size`로 제한할 수 있습니다. 힙 밖에도 스레드 스택, 네이티브 메모리, 파일 캐시가 한도에 포함됩니다. 메모리 기반 `emptyDir`(`medium: Memory`)에 쓴 데이터도 포함됩니다.
>
> 노드 전체의 메모리가 부족해 쫓겨난 경우는 다릅니다. 그때는 상태가 OOMKilled가 아니라 Evicted로 표시됩니다. 이 경우 노드의 자원 압박과 다른 파드의 requests 설정을 점검해야 합니다.
>
> describe 출력이나 사용량 추이를 알려 주시면 한도를 얼마로 잡을지 구체적으로 계산해 드릴 수 있습니다.
<!-- simple-korean: on -->

## 답변: 캐시 무효화 질문

전: 스킬 없음, `evals/results/2026-10-08/reply/baseline__cache__r1.txt`

<!-- source: evals/results/2026-10-08/reply/baseline__cache__r1.txt -->
<!-- simple-korean: off -->
> ## 왜 그런가
>
> 캐시-어사이드(cache-aside) 패턴에 TTL이 10분으로 걸려 있을 가능성이 높습니다.
>
> 1. 읽기 요청이 오면 Redis를 먼저 조회하고, 없으면 DB에서 읽어 Redis에 `SET key value EX 600`으로 저장합니다.
> 2. 가격을 바꾸면 DB만 갱신됩니다. Redis에는 예전 값이 그대로 남아 있습니다.
> 3. 키가 TTL로 만료될 때까지 읽기는 계속 캐시에서 나갑니다. 그래서 최대 10분 동안 예전 가격이 보입니다.
>
> 즉 쓰기 경로가 캐시를 건드리지 않아서 생기는 문제입니다. 캐시와 DB가 따로 갱신되니, TTL이 일관성을 보장하는 유일한 장치가 된 상태입니다.
>
> ## 해결 방법
>
> **1. 쓰기 시 캐시 무효화 (가장 일반적인 방법)**
> - DB 커밋 후 `DEL price:{productId}`를 호출합니다. 다음 읽기에서 새 값을 채웁니다.
> - 순서는 반드시 DB 갱신 후 캐시 삭제입니다. 반대로 하면 그 사이에 다른 요청이 예전 값을 다시 캐시에 넣을 수 있습니다.
> - 트랜잭션 안에서 삭제하면 롤백될 때 불일치가 생깁니다. 커밋 이후(`afterCommit` 훅 등)에 삭제하세요.
>
> **2. 쓰기 시 캐시 갱신 (write-through)**
> - DB 갱신 후 새 값을 바로 `SET`합니다. 첫 읽기 miss는 없어집니다.
> - 동시 쓰기가 겹치면 순서가 뒤바뀔 수 있어서, 보통은 삭제 쪽이 더 안전합니다.
>
> **3. 삭제가 실패할 때를 대비한 안전장치**
> - `DEL`이 실패하면 다시 예전 값이 10분간 남습니다. 재시도하거나, 아웃박스/메시지 큐(Kafka 등)나 CDC(Debezium)로 무효화 이벤트를 발행하는 방법이 있습니다.
> - 가격처럼 민감한 데이터는 TTL을 1~2분 정도로 줄여, 최악의 경우에도 오래 어긋나지 않게 하세요.
> - 레이스 컨디션이 걱정되면 지연 이중 삭제(delayed double delete)를 쓸 수 있습니다. 쓰기 후 삭제하고, 수백 ms 뒤에 한 번 더 삭제합니다.
>
> **4. 그 밖에 확인할 점**
> - 여러 서버가 있다면 앞단의 CDN, API 게이트웨이, 앱 내부 로컬 캐시(Caffeine 등)에도 따로 TTL이 있는지 확인하세요. Redis를 무효화해도 거기서 예전 값이 나갈 수 있습니다.
> - 목록 페이지처럼 가격이 포함된 집계 캐시 키도 같이 무효화해야 합니다.
> - 결제나 주문 시점에는 캐시 값을 쓰지 말고 DB의 가격을 기준으로 검증하세요. 화면 표시용 가격이 잠깐 어긋나도 결제 금액은 틀리지 않게 됩니다.
>
> ## 권장 조합
>
> DB 커밋 후 `DEL`로 무효화하고, 실패에 대비한 재시도나 이벤트 기반 무효화를 두고, TTL은 짧게 유지하세요. 결제 시점에는 DB 가격으로 최종 검증하는 구성입니다.
>
> 실제 코드에서 캐시를 읽고 쓰는 부분을 보여주시면, 어디에 무효화를 넣어야 하는지 구체적으로 짚어드릴 수 있습니다.
<!-- simple-korean: on -->

후: SimpleKorean, `evals/results/2026-10-08/reply/plain__cache__r1.txt`

<!-- source: evals/results/2026-10-08/reply/plain__cache__r1.txt -->
<!-- simple-korean: off -->
> 사용자가 예전 가격을 보는 이유는 Redis에 저장한 가격이 TTL(키가 자동으로 지워지기까지의 시간) 10분이 끝날 때까지 남기 때문입니다. 코드를 보지 않고 쓴 추정입니다. 가격을 바꾸는 코드가 DB만 갱신하고 Redis 키는 건드리지 않으면 이 증상이 나타납니다.
>
> 먼저 읽기 경로를 확인하세요. 읽기 요청은 Redis를 먼저 조회하고, 값이 없을 때만 DB를 읽어 Redis에 10분 TTL로 저장합니다. 가격이 바뀌어도 Redis에 키가 있으면 요청은 DB까지 가지 않습니다.
>
> 가장 흔한 해결책은 쓰기 시 무효화(invalidation, 낡은 캐시를 지우는 일)입니다. DB 트랜잭션을 커밋한 뒤에 해당 상품의 가격 키를 DEL로 지우세요. 다음 읽기 요청이 DB에서 새 가격을 가져와 캐시를 다시 채웁니다. 커밋 전에 지우면 안 됩니다. 그 사이에 들어온 읽기 요청이 옛 가격을 다시 캐시에 넣기 때문입니다.
>
> 커밋 뒤에 지워도 드문 경쟁 상태(race condition)가 남습니다. 읽기 요청이 옛 값을 DB에서 읽은 직후 가격이 바뀌고 삭제가 끝난 뒤에 그 읽기 요청이 옛 값을 캐시에 쓰면, 옛 값이 TTL이 끝날 때까지 남습니다. 그래서 TTL을 없애지 말고 안전망으로 두어야 합니다. 가격처럼 민감한 값이면 TTL을 1분 안팎으로 줄여도 됩니다.
>
> 삭제 요청이 실패하는 경우도 대비해야 합니다. DB 커밋은 성공했는데 Redis 호출이 실패하면 캐시가 낡은 채로 남습니다. 이를 막으려면 가격 변경 이벤트를 아웃박스(outbox, DB 트랜잭션에 함께 기록하는 발행 대기 테이블)에 저장하고, 별도 작업이 성공할 때까지 재시도하며 키를 지우게 하세요.
>
> 다른 대안은 쓰기 시 캐시 갱신입니다. 가격을 바꾼 직후 새 값을 Redis에 직접 쓰는 방식입니다. 읽기 지연은 줄지만 쓰기 경로가 복잡해지고 경쟁 상태도 같이 생깁니다. 대부분은 삭제 방식이 더 단순하고 안전합니다.
>
> 마지막으로 가격을 바꾸는 경로가 하나뿐인지 확인하세요. 관리자 화면, 배치 작업, 외부 연동이 각각 DB에 직접 쓰면 그중 하나만 무효화를 빠뜨려도 같은 문제가 다시 생깁니다. CDN이나 애플리케이션 내부 메모리 캐시가 Redis 앞에 또 있는지도 확인하세요. 그 캐시에 TTL이 있으면 Redis를 지워도 옛 가격이 계속 보입니다.
<!-- simple-korean: on -->
