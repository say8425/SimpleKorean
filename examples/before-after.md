# 전후 예시

'전'은 스킬 없이 만든 원본 출력입니다. '후'는 같은 과제를 스킬을 켜고 만든 원본 출력입니다. 두 글 모두 고치지 않고 옮겼습니다. 과제와 질문은 측정 전에 정했습니다(`evals/make_examples.py`의 PICKS). `python3 evals/check_numbers.py`가 이 파일의 글을 원본 파일과 글자 하나까지 대조합니다.

## README 소개(설명문)

전: 스킬 없음, `evals/results/2026-10-17/docs/baseline__readme-intro__r1.json`

<!-- source: evals/results/2026-10-17/docs/baseline__readme-intro__r1.json -->
<!-- simple-korean: off -->
> sqlpipe는 Postgres 테이블을 Parquet 파일로 변환해 S3에 동기화하는 CLI 도구입니다. 별도의 ETL 파이프라인이나 복잡한 설정 없이 명령어 한 줄로 테이블 데이터를 데이터 레이크에 옮길 수 있습니다.
>
> 변경된 행만 증분 방식으로 동기화하고, 컬럼 타입을 Parquet 스키마에 맞게 자동으로 매핑합니다. 대용량 테이블도 스트리밍으로 처리해 메모리 부담이 적습니다. 분석용 데이터 적재를 간단하고 안정적으로 만들어 줍니다.
<!-- simple-korean: on -->

후: 기본 모드, `evals/results/2026-10-17/docs/plain__readme-intro__r1.json`

<!-- source: evals/results/2026-10-17/docs/plain__readme-intro__r1.json -->
<!-- simple-korean: off -->
> sqlpipe는 Postgres 테이블을 Parquet 파일로 변환해 S3에 동기화하는 CLI 도구입니다. 테이블 하나를 지정하면 sqlpipe가 행을 읽어 Parquet 파일로 쓰고 S3 버킷에 올립니다.
>
> sqlpipe는 단일 실행 파일로 동작합니다. 터미널이나 스케줄러에서 명령 하나로 실행할 수 있습니다. 실행하는 호스트는 Postgres와 S3에 모두 연결할 수 있어야 합니다.
<!-- simple-korean: on -->

## 문제 해결(절차문)

전: 스킬 없음, `evals/results/2026-10-17/docs/baseline__troubleshooting__r1.json`

<!-- source: evals/results/2026-10-17/docs/baseline__troubleshooting__r1.json -->
<!-- simple-korean: off -->
> ## 문제 해결
>
> ### Postgres 연결 타임아웃
> `connection timed out` 오류가 나면 먼저 호스트와 포트(기본 5432)에 네트워크로 접근되는지 확인하세요. `nc -zv <호스트> 5432`로 점검할 수 있습니다. 방화벽이나 보안 그룹, VPN 연결 상태도 살펴보세요. 네트워크에 문제가 없는데도 지연된다면 `--connect-timeout 30`처럼 제한 시간을 늘려 보세요. 접속 문자열의 `sslmode` 설정이 서버와 맞는지도 확인해야 합니다.
>
> ### S3 권한 오류
> `AccessDenied` 또는 `403`이 나오면 현재 자격 증명이 올바른지 `aws sts get-caller-identity`로 확인하세요. 그다음 IAM 정책에 대상 버킷의 `s3:GetObject`, `s3:PutObject`, `s3:ListBucket` 권한이 있는지 보세요. 버킷 이름과 리전이 맞는지, 버킷 정책이 접근을 막고 있지 않은지도 확인하세요.
<!-- simple-korean: on -->

후: 기본 모드, `evals/results/2026-10-17/docs/plain__troubleshooting__r1.json`

<!-- source: evals/results/2026-10-17/docs/plain__troubleshooting__r1.json -->
<!-- simple-korean: off -->
> ## 문제 해결
>
> ### Postgres 연결 타임아웃
>
> sqlpipe는 Postgres 포트에 연결하지 못하면 `dial tcp: i/o timeout` 오류를 내고 멈춥니다.
>
> 1. sqlpipe를 실행하는 호스트가 Postgres 포트(기본값 5432)에 연결할 수 있는지 확인하세요. 보통 방화벽이나 보안 그룹이 연결을 막습니다.
> 2. 데이터베이스가 관리형(RDS, Cloud SQL)이면, 인스턴스가 sqlpipe의 IP에서 오는 연결을 허용하는지 확인하세요.
>
> ### S3 권한 오류
>
> sqlpipe가 S3에 쓸 때 `AccessDenied` 오류가 나면 자격 증명에 권한이 없는 것입니다.
>
> 1. sqlpipe를 실행하는 호스트에서 어떤 자격 증명을 쓰는지 확인하세요.
> 2. 그 자격 증명의 IAM 정책이 대상 버킷의 `s3:PutObject`를 허용하는지 확인하세요.
> 3. 버킷 정책이 해당 자격 증명을 거부하면 버킷 정책을 고치세요.
<!-- simple-korean: on -->

## 오류 메시지

전: 스킬 없음, `evals/results/2026-10-17/docs/baseline__error-message__r1.json`

<!-- source: evals/results/2026-10-17/docs/baseline__error-message__r1.json -->
<!-- simple-korean: off -->
> S3 업로드 실패: 접근이 거부되었습니다(AccessDenied).
> 현재 IAM 자격 증명에 대상 버킷에 대한 s3:PutObject 권한이 없습니다.
> 해당 IAM 사용자 또는 역할의 정책에 s3:PutObject를 허용하는 권한을 추가한 뒤 다시 시도하세요.
<!-- simple-korean: on -->

후: 기본 모드, `evals/results/2026-10-17/docs/plain__error-message__r1.json`

<!-- source: evals/results/2026-10-17/docs/plain__error-message__r1.json -->
<!-- simple-korean: off -->
> ```
> 오류: S3 업로드가 AccessDenied로 실패했습니다.
> IAM 자격 증명에 `s3:PutObject` 권한이 없습니다.
> IAM 정책에 대상 버킷의 `s3:PutObject` 권한을 추가하세요.
> ```
<!-- simple-korean: on -->

## 릴리스 노트(엄격 모드)

전: 스킬 없음, `evals/results/2026-10-17/docs/baseline__release-notes__r1.json`

<!-- source: evals/results/2026-10-17/docs/baseline__release-notes__r1.json -->
<!-- simple-korean: off -->
> **sqlpipe v2.0 릴리스 노트**
>
> **⚠️ 호환성 깨짐**
> - `/v2/users` 응답의 `name` 필드가 `first_name`과 `last_name`으로 분리되었습니다. 기존에 `name`을 사용하던 클라이언트는 업그레이드 전에 반드시 수정해야 합니다.
>
> **새 기능**
> - `--incremental` 플래그가 추가되어, 변경된 데이터만 선택적으로 처리할 수 있습니다.
>
> **성능 개선**
> - Parquet 쓰기 속도가 약 40% 향상되었습니다.
>
> 업그레이드 전에 `name` 필드 의존 코드를 꼭 확인해 주세요.
<!-- simple-korean: on -->

후: 엄격 모드, `evals/results/2026-10-17/docs/strict__release-notes__r1.json`

<!-- source: evals/results/2026-10-17/docs/strict__release-notes__r1.json -->
<!-- simple-korean: off -->
> # sqlpipe v2.0 릴리스 노트
>
> ## 호환성이 깨지는 변경
>
> `/v2/users`의 `name` 필드를 `first_name`과 `last_name`으로 나눴습니다. 이 필드를 읽는 클라이언트는 새 필드를 읽도록 고쳐야 합니다.
>
> ## 새 기능
>
> `--incremental` 플래그를 추가했습니다. 
>
> ## 성능
>
> Parquet 쓰기가 40% 빨라졌습니다.
<!-- simple-korean: on -->

## 답변: OOMKilled 질문

전: 스킬 없음, `evals/results/2026-10-17/reply/baseline__oom__r1.txt`

<!-- source: evals/results/2026-10-17/reply/baseline__oom__r1.txt -->
<!-- simple-korean: off -->
> # OOMKilled 재시작: 원인과 조치
>
> ## 무슨 일이 일어나는가
>
> 컨테이너의 메모리 사용량이 `resources.limits.memory`를 넘으면 리눅스 커널의 cgroup OOM killer가 프로세스를 강제 종료합니다(종료 코드 137, 사유 `OOMKilled`). kubelet은 `restartPolicy`에 따라 컨테이너를 다시 시작하고, 같은 일이 반복되면 `CrashLoopBackOff`가 됩니다. 재시작 간격은 10초에서 최대 5분까지 지수적으로 늘어납니다.
>
> 노드 전체의 메모리가 부족해서 파드가 쫓겨나는 경우(Evicted)와는 다릅니다. OOMKilled는 대개 **컨테이너 자신의 limit 초과**입니다.
>
> ## 먼저 확인할 것
>
> ```bash
> kubectl describe pod <pod> | grep -A5 "Last State"   # Reason: OOMKilled, Exit Code: 137
> kubectl top pod <pod> --containers                    # 현재 사용량
> kubectl get pod <pod> -o jsonpath='{.spec.containers[*].resources}'
> ```
>
> Prometheus를 쓰고 있다면 `container_memory_working_set_bytes`를 limit과 겹쳐 보세요. 죽기 직전까지 우상향하는지, 특정 시점에 급증하는지를 보면 원인을 가를 수 있습니다.
>
> ## 흔한 원인
>
> | 원인 | 징후 |
> |---|---|
> | limit이 너무 낮음 | 사용량이 시작 후 안정적으로 limit 근처에서 유지됨 |
> | 메모리 누수 | 시간이 갈수록 계속 증가해서 주기적으로 죽음 |
> | 트래픽/배치 급증 | 특정 요청이나 작업 때 스파이크 |
> | 런타임 설정 불일치 | JVM 힙, Node.js `--max-old-space-size` 등이 limit보다 크게 잡혀 있음 |
> | 페이지 캐시/tmpfs | `emptyDir`(medium: Memory)나 파일 캐시가 컨테이너 메모리로 계산됨 |
>
> ## 무엇을 바꿔야 하나
>
> 1. **limit 올리기**: 실제 피크 사용량에 20~30% 여유를 둡니다. `requests`도 평균 사용량에 맞춰 같이 조정하세요.
>    ```yaml
>    resources:
>      requests: { memory: "512Mi" }
>      limits:   { memory: "1Gi" }
>    ```
> 2. **런타임 메모리를 limit에 맞추기**
>    - JVM: `-XX:MaxRAMPercentage=70` (힙 외에 메타스페이스, 스레드 스택 등도 필요합니다)
>    - Node.js: `--max-old-space-size`를 limit의 약 75% 이하로
>    - Go: `GOMEMLIMIT`를 limit의 약 90%로
> 3. **누수라면 limit을 올려도 시간만 벌 뿐입니다.** 힙 덤프나 프로파일링(pprof, heap dump 등)으로 원인을 찾아야 합니다.
> 4. **스파이크 대응**: 요청 동시성 제한, 배치 크기 축소, 스트리밍 처리로 바꾸는 방법이 있습니다. HPA로 파드 수를 늘리는 방법도 있습니다.
> 5. **사이드카도 확인하세요.** 죽는 컨테이너가 앱이 아니라 사이드카(istio-proxy, 로그 에이전트 등)일 수 있습니다.
>
> ## 진단 순서 권장
>
> 1. `describe`로 어떤 컨테이너가 죽는지와 종료 코드를 확인합니다.
> 2. 사용량 그래프로 "계속 증가"인지 "limit이 낮은 것"인지 구분합니다.
> 3. 후자면 limit과 런타임 설정을 조정하고, 전자면 프로파일링을 합니다.
>
> `kubectl describe` 출력, 사용 언어/런타임, 현재 resources 설정을 알려주시면 구체적인 값까지 같이 잡아드릴 수 있습니다.
<!-- simple-korean: on -->

후: SimpleKorean, `evals/results/2026-10-17/reply/plain__oom__r1.txt`

<!-- source: evals/results/2026-10-17/reply/plain__oom__r1.txt -->
<!-- simple-korean: off -->
> 파드가 메모리 제한(limit)을 넘어서 커널에 강제 종료되고, kubelet이 컨테이너를 다시 시작하는 상태입니다. 제한을 올리거나 애플리케이션의 메모리 사용량을 줄이면 해결됩니다.
>
> ## 무슨 일이 일어나는지
>
> 1. 컨테이너가 `resources.limits.memory` 값보다 많은 메모리를 씁니다.
> 2. 리눅스 cgroup(프로세스 그룹의 자원 사용을 제한하는 커널 기능)이 한도 초과를 감지합니다.
> 3. 커널의 OOM killer(메모리 부족 시 프로세스를 죽이는 기능)가 프로세스에 SIGKILL을 보냅니다. 종료 코드는 137입니다.
> 4. kubelet이 `restartPolicy`에 따라 컨테이너를 다시 시작합니다. 반복되면 `CrashLoopBackOff`로 표시됩니다.
>
> 노드 전체의 메모리가 부족해서 파드가 쫓겨나는 경우는 `Evicted`로 표시되므로 다른 문제입니다.
>
> ## 원인 확인
>
> 먼저 종료 사유를 확인하세요.
>
> ```
> kubectl describe pod <파드 이름>
> ```
>
> `Last State: Terminated`의 `Reason: OOMKilled`와 `Exit Code: 137`을 찾으세요. 그다음 실제 사용량을 보세요. 이 명령은 metrics-server가 설치되어 있어야 동작합니다.
>
> ```
> kubectl top pod <파드 이름> --containers
> ```
>
> 재시작 직전 로그는 `kubectl logs <파드 이름> --previous`로 확인하세요.
>
> ## 바꿀 것
>
> 1. 사용량이 제한에 가까워지다 넘으면 제한을 올리세요. 요청(request)도 함께 올려야 스케줄러가 메모리가 충분한 노드에 배치합니다.
>
> ```yaml
> resources:
>   requests:
>     memory: "512Mi"
>   limits:
>     memory: "1Gi"
> ```
>
> 2. 사용량이 시간이 지날수록 계속 늘면 메모리 누수(leak)입니다. 제한을 올려도 재시작 주기만 늘어나므로 코드를 고쳐야 합니다.
>
> 3. 런타임이 컨테이너 제한을 모르면 힙(heap, 동적 할당 영역) 크기를 제한보다 작게 지정하세요.
>    - JVM은 `-XX:MaxRAMPercentage=75.0`을 씁니다.
>    - Node.js는 `--max-old-space-size`를 씁니다.
>
> 4. `emptyDir`에 `medium: Memory`를 쓰면 그 파일이 메모리로 계산됩니다. 쓰는 중이면 크기를 확인하세요.
>
> 5. 시작 시점이나 트래픽 급증 때만 죽으면 일시적인 최대 사용량(peak)이 원인입니다. 이때는 제한을 최대치에 맞추고, 수평 확장(HPA)으로 부하를 나누세요.
>
> 사용 중인 언어와 `kubectl describe` 출력, `kubectl top` 결과를 알려 주시면 원인을 더 좁힐 수 있습니다.
<!-- simple-korean: on -->

## 답변: 캐시 무효화 질문

전: 스킬 없음, `evals/results/2026-10-17/reply/baseline__cache__r1.txt`

<!-- source: evals/results/2026-10-17/reply/baseline__cache__r1.txt -->
<!-- simple-korean: off -->
> ## 왜 그런가
>
> 가격이 바뀌어도 Redis에 캐시된 값이 그대로 남아 있기 때문입니다. 보통 아래 중 하나입니다. 코드를 보지 않아서 어느 쪽인지는 단정할 수 없습니다.
>
> - **TTL만 믿는 경우**: 캐시 키에 `SET key value EX 600`처럼 10분 TTL만 걸어 두었습니다. DB를 갱신해도 Redis 키는 만료될 때까지 남습니다. 증상이 "최대 10분"이라면 이 경우일 가능성이 가장 큽니다.
> - **쓰기 시 무효화를 하지 않는 경우**: 가격 변경 로직이 DB만 갱신하고 `DEL`을 호출하지 않습니다. 다른 서비스나 배치, 어드민이 DB를 직접 수정하는 경우도 같습니다.
> - **무효화 순서나 경쟁 상태**: "DB 갱신 → 캐시 삭제" 사이에 다른 요청이 옛 값을 읽어 캐시에 다시 채울 수 있습니다. 그러면 이후 TTL이 끝날 때까지 옛 값이 남습니다.
> - **다른 계층의 캐시**: CDN, API 게이트웨이, 애플리케이션 로컬 캐시(Caffeine 등), 브라우저 캐시가 Redis와 별개로 옛 값을 들고 있을 수 있습니다.
> - **읽기 전용 복제본 지연**: 캐시를 지운 직후 복제본에서 옛 값을 읽어 다시 캐시에 넣을 수도 있습니다.
>
> ## 어떻게 고치나
>
> 1. **가격 변경 성공 후 해당 키를 삭제합니다 (cache-aside).**
>    - 순서는 DB를 먼저 커밋하고 그 뒤에 `DEL`입니다. 반대로 하면 옛 값이 다시 채워집니다.
>    - 트랜잭션 안에서 지우지 말고 커밋 이후(after-commit 훅)에 지우세요. 그래야 커밋 전에 옛 값이 다시 캐싱되는 일이 없습니다.
> 2. **TTL은 안전망으로 남기되 짧게 줄입니다.** 예를 들어 30~60초 정도로 하면 삭제가 실패해도 오래가지 않습니다.
> 3. **삭제가 유실될 때를 대비합니다.**
>    - 지연 이중 삭제: 수백 ms 뒤에 한 번 더 `DEL`을 호출합니다.
>    - 더 확실하게 하려면 outbox 패턴이나 CDC(Debezium 등)로 DB 변경 이벤트를 받아 무효화합니다. 이 방식은 어드민이나 배치가 DB를 직접 고쳐도 동작합니다.
> 4. **버전 키를 사용합니다.** 캐시 키를 `price:{productId}:v{version}`처럼 만들고 가격 변경 때 버전을 올리면 옛 키는 자연히 안 읽힙니다. 삭제 경쟁 문제도 피할 수 있습니다.
> 5. **다른 캐시 계층도 확인합니다.** CDN 퍼지, `Cache-Control` 헤더, 로컬 캐시 무효화(Redis Pub/Sub 등)를 점검하세요.
> 6. **결제나 주문 시점의 가격은 캐시를 거치지 않고 DB에서 직접 읽습니다.** 캐시가 낡아도 잘못된 금액으로 결제되는 일은 막을 수 있습니다.
>
> 가격 변경 코드와 캐시 조회 코드를 알려 주시면 어느 원인인지 확인해서 구체적인 수정안을 드리겠습니다.
<!-- simple-korean: on -->

후: SimpleKorean, `evals/results/2026-10-17/reply/plain__cache__r1.txt`

<!-- source: evals/results/2026-10-17/reply/plain__cache__r1.txt -->
<!-- simple-korean: off -->
> 가격을 바꿔도 Redis에 저장된 예전 값이 TTL(키가 자동으로 삭제되기까지의 시간)이 끝날 때까지 남기 때문입니다. TTL이 10분이면 증상과 맞습니다. 코드를 보지 못했으므로 TTL 값은 확인해야 합니다.
>
> ## 원인
>
> 캐시 어사이드(cache-aside, 읽을 때 캐시를 먼저 보고 없으면 DB에서 채우는 방식) 구조에서는 쓰기가 DB만 바꿉니다. Redis 키는 그대로 남습니다. 읽기 요청은 키가 만료될 때까지 예전 가격을 반환합니다.
>
> ## 고치는 방법
>
> 가장 단순한 방법은 가격을 쓴 뒤 해당 키를 삭제하는 것입니다. 다음 읽기가 DB에서 새 값을 가져와 캐시를 채웁니다.
>
> ```python
> def update_price(product_id, price):
>     with db.transaction():
>         db.update_price(product_id, price)
>     redis.delete(f"price:{product_id}")
> ```
>
> 순서가 중요합니다.
>
> - DB 커밋 뒤에 삭제해야 합니다. 커밋 전에 삭제하면 다른 요청이 예전 값을 다시 캐시에 넣을 수 있습니다.
> - 삭제가 실패할 수 있으므로 TTL은 안전장치로 남겨야 합니다. 10분을 1분 정도로 줄이면 실패의 영향도 줄어듭니다.
> - 서비스가 여러 개이면 가격 변경 이벤트(예: Kafka 메시지)를 받아 각 서비스가 키를 삭제하게 하세요.
>
> ## 다른 선택지
>
> - 쓰기 시점에 DB와 Redis를 함께 갱신하는 방식(write-through)은 삭제 뒤 첫 읽기의 지연을 없앱니다. 하지만 두 저장소의 쓰기 순서가 꼬이면 값이 어긋날 수 있습니다.
> - TTL만 줄이는 방법은 코드 변경이 없습니다. 하지만 DB 부하가 늘고 지연은 줄어들 뿐 없어지지 않습니다.
>
> ## 먼저 확인할 것
>
> Redis 앞이나 뒤에 다른 캐시가 있으면 키를 삭제해도 예전 가격이 보일 수 있습니다. CDN, API 게이트웨이, 애플리케이션 메모리 캐시, 브라우저 `Cache-Control` 헤더를 확인하세요. `redis-cli TTL price:<id>`로 남은 시간을 보면 Redis가 원인인지 바로 알 수 있습니다.
<!-- simple-korean: on -->
