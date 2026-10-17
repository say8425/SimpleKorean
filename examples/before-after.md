# 전후 예시

'전'은 스킬 없이 만든 원본 출력입니다. '후'는 같은 과제를 스킬을 켜고 만든 원본 출력입니다. 두 글 모두 고치지 않고 옮겼습니다. 과제와 질문은 측정 전에 정했습니다(`evals/make_examples.py`의 PICKS). `python3 evals/check_numbers.py`가 이 파일의 글을 원본 파일과 글자 하나까지 대조합니다.

## README 소개(설명문)

전: 스킬 없음, `evals/results/2026-10-17/docs/baseline__readme-intro__r1.json`

<!-- source: evals/results/2026-10-17/docs/baseline__readme-intro__r1.json -->
<!-- simple-korean: off -->
> sqlpipe는 Postgres 테이블을 Parquet 파일로 변환해 S3에 동기화하는 CLI 도구입니다. 명령 한 줄로 원하는 테이블을 지정하면, 데이터를 읽어 컬럼 기반 Parquet 형식으로 저장하고 S3 버킷에 업로드합니다. 별도의 ETL 인프라 없이도 분석용 데이터 레이크를 간단히 구축할 수 있습니다.
>
> 변경된 데이터만 반영하는 증분 동기화를 지원하므로 큰 테이블도 빠르고 저렴하게 최신 상태로 유지할 수 있습니다. cron이나 CI 파이프라인에 쉽게 붙일 수 있도록 설계되어, 정기적인 백업과 분석 데이터 적재에 알맞습니다.
<!-- simple-korean: on -->

후: 기본 모드, `evals/results/2026-10-17/docs/plain__readme-intro__r1.json`

<!-- source: evals/results/2026-10-17/docs/plain__readme-intro__r1.json -->
<!-- simple-korean: off -->
> sqlpipe는 Postgres 테이블을 Parquet 파일로 변환해 S3에 동기화하는 CLI 도구입니다. 지정한 테이블의 행을 읽어 Parquet 파일로 쓰고, 그 파일을 S3 버킷에 올립니다.
>
> sqlpipe는 한 번 실행할 때마다 변경된 데이터만 동기화합니다. 사용자는 연결 정보와 대상 테이블만 설정에 적으면 됩니다. 실행하는 호스트는 Postgres와 S3에 모두 연결할 수 있어야 합니다.
<!-- simple-korean: on -->

## 문제 해결(절차문)

전: 스킬 없음, `evals/results/2026-10-17/docs/baseline__troubleshooting__r1.json`

<!-- source: evals/results/2026-10-17/docs/baseline__troubleshooting__r1.json -->
<!-- simple-korean: off -->
> ## 문제 해결
>
> ### Postgres 연결 타임아웃
>
> `connection timed out` 오류가 나면 먼저 호스트와 포트(기본 5432)에 네트워크로 접근할 수 있는지 확인하세요. VPN, 방화벽, 보안 그룹의 인바운드 규칙이 흔한 원인입니다. 접근에 문제가 없다면 연결 대기 시간을 늘려 보세요.
>
> ```
> sqlpipe run --timeout 30s ...
> ```
>
> 접속 문자열의 호스트, 포트, `sslmode` 값도 다시 확인하세요. 서버가 SSL을 요구하는데 `sslmode=disable`로 되어 있으면 연결이 멈춘 것처럼 보일 수 있습니다.
>
> ### S3 권한 오류
>
> `AccessDenied` 또는 `403`이 나오면 자격 증명이 올바른지 먼저 확인하세요. `aws sts get-caller-identity`로 현재 사용 중인 계정을 볼 수 있습니다. 그다음 IAM 정책에 대상 버킷의 `s3:GetObject`, `s3:PutObject`, `s3:ListBucket` 권한이 있는지 확인하세요. 버킷 정책과 리전 설정도 함께 점검해야 합니다.
<!-- simple-korean: on -->

후: 기본 모드, `evals/results/2026-10-17/docs/plain__troubleshooting__r1.json`

<!-- source: evals/results/2026-10-17/docs/plain__troubleshooting__r1.json -->
<!-- simple-korean: off -->
> ## 문제 해결
>
> ### Postgres 연결 타임아웃
>
> sqlpipe는 Postgres 포트(기본값 5432)에 연결하지 못하면 `dial tcp: i/o timeout` 오류를 내고 멈춥니다.
>
> 1. sqlpipe를 실행하는 호스트가 Postgres 포트에 연결할 수 있는지 확인하세요.
> 2. 방화벽과 보안 그룹 규칙을 확인하세요. 보통 이 규칙이 연결을 막습니다.
> 3. 데이터베이스가 관리형(RDS, Cloud SQL)이면, 인스턴스가 sqlpipe의 IP에서 오는 연결을 허용하는지 확인하세요.
>
> ### S3 권한 오류
>
> S3 요청이 `AccessDenied` 오류로 실패하면 sqlpipe가 사용하는 자격 증명에 권한이 없다는 뜻입니다.
>
> 1. sqlpipe를 실행하는 호스트에서 `aws sts get-caller-identity`를 실행하세요. 이 명령은 현재 자격 증명의 계정과 역할을 보여 줍니다.
> 2. 그 역할의 IAM 정책이 대상 버킷에 `s3:GetObject`와 `s3:PutObject`를 허용하는지 확인하세요.
> 3. 버킷 정책이 해당 역할을 거부하는지 확인하세요.
<!-- simple-korean: on -->

## 오류 메시지

전: 스킬 없음, `evals/results/2026-10-17/docs/baseline__error-message__r1.json`

<!-- source: evals/results/2026-10-17/docs/baseline__error-message__r1.json -->
<!-- simple-korean: off -->
> S3 업로드에 실패했습니다: AccessDenied. 현재 IAM 자격 증명에 `s3:PutObject` 권한이 없습니다.
> 대상 버킷과 키 경로에 대해 `s3:PutObject`를 허용하도록 IAM 정책을 수정한 뒤 다시 시도하세요.
<!-- simple-korean: on -->

후: 기본 모드, `evals/results/2026-10-17/docs/plain__error-message__r1.json`

<!-- source: evals/results/2026-10-17/docs/plain__error-message__r1.json -->
<!-- simple-korean: off -->
> S3 업로드가 실패했습니다. `AccessDenied` 오류가 발생했습니다.
> 현재 IAM 자격 증명에 `s3:PutObject` 권한이 없습니다.
> IAM 정책에 `s3:PutObject`를 추가한 뒤 sqlpipe를 다시 실행하세요.
<!-- simple-korean: on -->

## 릴리스 노트(엄격 모드)

전: 스킬 없음, `evals/results/2026-10-17/docs/baseline__release-notes__r1.json`

<!-- source: evals/results/2026-10-17/docs/baseline__release-notes__r1.json -->
<!-- simple-korean: off -->
> **sqlpipe v2.0 릴리스 노트**
>
> **⚠️ 호환성 깨짐**
> `/v2/users` 응답의 `name` 필드가 `first_name`과 `last_name`으로 분리되었습니다. `name`을 사용하는 클라이언트는 업그레이드 전에 코드를 수정해 주세요.
>
> **새로운 기능**
> - `--incremental` 플래그 추가: 변경된 데이터만 처리할 수 있습니다.
>
> **성능 개선**
> - Parquet 쓰기 속도가 약 40% 빨라졌습니다.
<!-- simple-korean: on -->

후: 엄격 모드, `evals/results/2026-10-17/docs/strict__release-notes__r1.json`

<!-- source: evals/results/2026-10-17/docs/strict__release-notes__r1.json -->
<!-- simple-korean: off -->
> 한국어 통제 언어 국가 표준은 없습니다. 이 기준은 KS A 0001과 공개 연구를 바탕으로 한 비공식 기준입니다.
>
> ## sqlpipe v2.0 릴리스 노트
>
> ### 호환성 깨짐
>
> `/v2/users`의 `name` 필드를 `first_name`과 `last_name`으로 나눴습니다. `name`을 읽는 클라이언트는 두 필드를 읽도록 고쳐야 합니다.
>
> ### 새 기능
>
> `--incremental` 플래그를 추가했습니다. 이 플래그를 쓰면 sqlpipe는 바뀐 행만 전송합니다.
>
> ### 성능
>
> Parquet 쓰기가 40% 빨라졌습니다.
<!-- simple-korean: on -->

## 답변: OOMKilled 질문

전: 스킬 없음, `evals/results/2026-10-17/reply/baseline__oom__r1.txt`

<!-- source: evals/results/2026-10-17/reply/baseline__oom__r1.txt -->
<!-- simple-korean: off -->
> ## 무슨 일이 일어나는가
>
> `OOMKilled`는 컨테이너가 **memory limit**을 초과해서 리눅스 커널의 OOM killer가 프로세스를 강제 종료(SIGKILL, exit code 137)했다는 뜻입니다. 쿠버네티스는 `restartPolicy`에 따라 컨테이너를 다시 띄우고, 같은 원인이 반복되면 `CrashLoopBackOff`로 재시작 간격이 점점 늘어납니다.
>
> 메모리 limit을 넘는 흔한 원인은 다음과 같습니다.
>
> 1. **limit이 너무 낮음**: 실제 사용량의 정상 범위보다 낮게 잡힌 경우
> 2. **메모리 누수**: 시간이 지나며 사용량이 계속 증가
> 3. **런타임 설정 불일치**: JVM 힙, Node.js `--max-old-space-size`, Go GC 등이 컨테이너 limit을 고려하지 않음. 힙 외 메모리(메타스페이스, 스레드 스택, 네이티브 버퍼)까지 합쳐서 limit을 넘음
> 4. **트래픽/데이터 급증**: 큰 요청, 대용량 파일 처리, 캐시 증가
> 5. **page cache 포함**: 파일 I/O가 많으면 캐시도 cgroup 메모리로 계산됨
> 6. **사이드카 또는 같은 파드의 다른 컨테이너**가 메모리를 사용 중
>
> ## 먼저 확인할 것
>
> ```bash
> # 종료 원인 확인 (Reason: OOMKilled, Exit Code: 137)
> kubectl describe pod <pod> -n <ns>
> kubectl get pod <pod> -n <ns> -o jsonpath='{.status.containerStatuses[*].lastState}'
>
> # 직전 컨테이너 로그
> kubectl logs <pod> -n <ns> --previous
>
> # 현재 사용량 (metrics-server 필요)
> kubectl top pod <pod> -n <ns> --containers
>
> # 설정된 requests/limits
> kubectl get pod <pod> -n <ns> -o jsonpath='{.spec.containers[*].resources}'
> ```
>
> 또한 Prometheus/Grafana가 있다면 `container_memory_working_set_bytes`를 limit과 함께 그려 보세요. 그래프의 모양으로 원인을 구분할 수 있습니다.
> - **계단식/완만한 우상향**: 누수
> - **시작 직후 급등**: limit이 낮거나 초기 로딩 문제
> - **주기적 스파이크**: 배치 작업이나 특정 요청
>
> 노드 전체가 메모리 부족이면 파드가 `Evicted`될 수 있는데, 이것은 OOMKilled와 다른 현상입니다.
>
> ## 무엇을 바꿔야 하는가
>
> **1. 단기 조치: limit 상향**
>
> ```yaml
> resources:
>   requests:
>     memory: "512Mi"
>   limits:
>     memory: "1Gi"
> ```
>
> 실제 working set의 피크에 20~30% 여유를 두는 것이 일반적입니다. 가능하면 `requests`와 `limits`를 같게 해서 QoS를 Guaranteed로 두면 노드 압박 시 더 안전합니다.
>
> **2. 런타임을 컨테이너에 맞추기**
>
> - JVM: `-XX:MaxRAMPercentage=70` 정도로 지정 (힙을 limit의 100%로 잡지 말 것)
> - Node.js: `--max-old-space-size`를 limit보다 작게 (예: limit 1Gi면 ~768)
> - Go: `GOMEMLIMIT`을 limit의 80~90%로 설정
>
> **3. 근본 원인 해결**
>
> 사용량이 계속 늘어난다면 limit만 올리면 재시작 주기만 늘어날 뿐입니다. 힙 덤프/프로파일링으로 누수를 찾거나, 큰 데이터를 스트리밍 처리하거나, 캐시에 상한을 두세요.
>
> **4. 확장**
>
> 부하 때문이라면 레플리카 수를 늘리거나 HPA로 분산하세요. VPA를 쓰면 적정 requests/limits 추천값을 얻을 수 있습니다.
>
> ## 다음 단계
>
> 원인을 더 좁히려면 아래 정보를 알려주세요.
> - `kubectl describe pod` 출력 중 `Last State`, `Limits` 부분
> - 사용하는 언어/런타임 (Java, Node, Python 등)
> - 재시작까지 걸리는 시간 (시작 직후인지, 몇 시간 뒤인지)
> - `kubectl top` 결과
>
> 이 정보가 있으면 limit 문제인지 누수인지 구체적으로 진단해 드릴 수 있습니다.
<!-- simple-korean: on -->

후: SimpleKorean, `evals/results/2026-10-17/reply/plain__oom__r1.txt`

<!-- source: evals/results/2026-10-17/reply/plain__oom__r1.txt -->
<!-- simple-korean: off -->
> 컨테이너가 메모리 제한(limit)을 넘어서 커널이 프로세스를 강제로 종료하기 때문에 재시작합니다. 제한을 올리거나 애플리케이션의 메모리 사용을 줄여야 합니다.
>
> ## 원인
>
> 컨테이너가 `resources.limits.memory` 값보다 많은 메모리를 쓰면 커널의 OOM killer(메모리가 부족할 때 프로세스를 죽이는 기능)가 SIGKILL을 보냅니다. 종료 코드는 137입니다. kubelet은 재시작 정책에 따라 컨테이너를 다시 띄웁니다. 같은 일이 반복되면 파드가 CrashLoopBackOff 상태가 됩니다.
>
> 흔한 원인은 네 가지입니다.
>
> - 제한이 실제 사용량보다 낮습니다.
> - 애플리케이션에 메모리 누수가 있습니다.
> - JVM 힙이나 Node.js 힙이 컨테이너 제한을 고려하지 않고 설정되어 있습니다.
> - 트래픽이나 대용량 요청 때문에 메모리가 일시적으로 급증합니다.
>
> ## 확인
>
> 1. `kubectl describe pod <파드 이름>`을 실행하세요.
> 2. `Last State`에서 `Reason: OOMKilled`를 확인하세요.
> 3. `kubectl top pod <파드 이름>`으로 사용량을 확인하세요. 이 명령은 metrics-server가 설치된 클러스터에서만 동작합니다.
> 4. 사용량이 시간이 지날수록 계속 오르면 누수를 의심하세요.
> 5. 시작 직후에 제한을 넘으면 제한이 낮은 것입니다.
>
> ## 수정
>
> 먼저 제한을 실제 사용량보다 여유 있게 올리세요. 요청값(requests)은 평소 사용량에 맞추세요.
>
> ```yaml
> resources:
>   requests:
>     memory: "512Mi"
>   limits:
>     memory: "1Gi"
> ```
>
> JVM을 쓰면 힙 크기를 제한에 맞추세요. `-XX:MaxRAMPercentage=75.0` 옵션이 컨테이너 제한의 75%를 힙 상한으로 정합니다. 나머지 메모리는 스레드 스택과 네이티브 메모리가 씁니다.
>
> 제한을 올려도 사용량이 계속 오르면 누수가 원인입니다. 이때 제한 상향은 임시 조치입니다. 힙 덤프나 프로파일러로 누수 지점을 찾아 고쳐야 합니다.
>
> 사용량 수치나 `describe` 출력을 알려 주시면 원인을 더 좁힐 수 있습니다.
<!-- simple-korean: on -->

## 답변: 캐시 무효화 질문

전: 스킬 없음, `evals/results/2026-10-17/reply/baseline__cache__r1.txt`

<!-- source: evals/results/2026-10-17/reply/baseline__cache__r1.txt -->
<!-- simple-korean: off -->
> 코드를 직접 확인하지는 않았습니다. 증상으로 보면 원인은 거의 확실합니다.
>
> ## 왜 그런가
>
> DB 앞에 Redis를 두는 cache-aside 방식이고, 키의 TTL이 10분일 가능성이 큽니다. 흐름은 이렇습니다.
>
> 1. 읽기 요청이 오면 Redis를 먼저 봅니다. 값이 있으면 그대로 반환하고, 없으면 DB에서 읽어 Redis에 `SET key value EX 600`으로 저장합니다.
> 2. 가격을 바꾸면 DB만 갱신합니다. Redis에는 이전 값이 남아 있습니다.
> 3. 그 키가 TTL로 만료될 때까지 읽기 요청은 이전 가격을 받습니다. 최악의 경우가 TTL 전체인 10분입니다.
>
> 즉 DB와 캐시 사이에 갱신 경로가 없어서 생기는 문제입니다. TTL이 유일한 동기화 수단이 된 상태입니다.
>
> ## 어떻게 고치나
>
> **1. 쓰기 시 캐시 무효화 (가장 기본)**
> - 가격 변경 트랜잭션이 커밋된 뒤에 `DEL price:{productId}`를 실행합니다.
> - 커밋 전에 지우면 안 됩니다. 그 사이 읽기 요청이 이전 값을 다시 캐시에 채웁니다.
> - 값을 덮어쓰는 `SET`보다 `DEL`이 안전합니다. 동시 쓰기가 겹칠 때 오래된 값이 나중에 덮어쓰는 경쟁을 피할 수 있습니다.
>
> **2. DEL 실패에 대비**
> - DB 커밋은 성공했는데 DEL이 실패하면 다시 이전 값이 남습니다. 이를 막는 방법은 세 가지입니다.
>   - 재시도합니다.
>   - outbox 패턴이나 CDC(예: Debezium)로 변경 이벤트를 받아 무효화합니다.
>   - 안전장치로 TTL을 10분에서 30~60초로 줄입니다.
>
> **3. 읽기 경로의 레이스 방지**
> - 읽기가 DB에서 이전 값을 읽은 뒤, 가격 변경과 DEL이 끝난 다음에 그 값을 캐시에 쓰는 경우가 있습니다. 이때는 버전 번호나 `updated_at`을 값에 함께 저장해 더 오래된 값이 덮어쓰지 못하게 합니다.
> - 또는 짧은 TTL과 지연 이중 삭제(delayed double delete)를 씁니다.
>
> **4. 여러 서버를 쓴다면**
> - 서버 프로세스 안에도 로컬 캐시(Caffeine, in-memory 등)가 있으면 Redis를 지워도 이전 가격이 남습니다.
> - 이 경우 Redis pub/sub 등으로 무효화를 전파하거나, 로컬 캐시 TTL을 몇 초로 짧게 둡니다.
>
> ## 권장
>
> 가격은 정합성이 중요한 데이터입니다. **커밋 후 `DEL` + 재시도 가능한 무효화(outbox/CDC) + 짧은 TTL(30~60초)**을 같이 쓰는 구성을 권합니다. 또 결제나 주문 시점에는 캐시 값을 쓰지 말고 DB의 가격으로 다시 검증하세요. 화면에 잠깐 이전 가격이 보이는 것보다 이전 가격으로 결제되는 것이 훨씬 큰 문제입니다.
>
> 원하시면 코드베이스에서 캐시를 읽고 쓰는 위치를 찾아 구체적인 수정안을 만들어 드리겠습니다.
<!-- simple-korean: on -->

후: SimpleKorean, `evals/results/2026-10-17/reply/plain__cache__r1.txt`

<!-- source: evals/results/2026-10-17/reply/plain__cache__r1.txt -->
<!-- simple-korean: off -->
> 가격을 바꿔도 Redis에 예전 가격 키가 남고, 그 키의 TTL(만료 시간)이 10분이기 때문입니다. 코드를 보지 않고 증상으로 추정한 결과입니다.
>
> 대부분 캐시 어사이드(cache-aside) 패턴을 쓰고 있을 것입니다. 이 패턴은 읽을 때 Redis를 먼저 보고, 없을 때만 DB에서 읽어 Redis에 저장합니다. 가격 변경이 DB만 갱신하면 Redis 키는 TTL이 끝날 때까지 예전 값을 돌려줍니다.
>
> 고치는 방법은 다음과 같습니다.
>
> 1. 가격 변경이 DB에 커밋된 뒤 해당 상품의 캐시 키를 `DEL`로 지웁니다. 다음 읽기가 DB에서 새 값을 가져와 캐시를 다시 채웁니다.
> 2. 순서를 지켜야 합니다. 캐시를 먼저 지우고 DB를 나중에 갱신하면, 그 사이의 읽기가 예전 값을 다시 캐시에 저장합니다.
> 3. 가격을 바꾸는 모든 경로(어드민, 배치, 다른 서비스)가 같은 삭제 코드를 거치게 하세요. 한 경로라도 빠지면 같은 문제가 그 경로에서 남습니다.
> 4. TTL은 안전망으로 남기고, 가격처럼 정확해야 하는 값은 1~2분으로 줄일 수 있습니다.
>
> 캐시에 새 값을 직접 쓰는 방식(write-through)도 있습니다. 하지만 동시에 두 번 변경하면 쓰기 순서가 뒤바뀔 수 있어, 삭제 방식이 더 안전합니다. 삭제 방식에도 작은 틈은 있습니다. 삭제 직전에 DB를 읽은 느린 요청이 삭제 직후 예전 값을 저장할 수 있습니다. 이 틈은 4번의 짧은 TTL이 막습니다.
>
> 캐시 코드 위치나 사용하는 클라이언트를 알려 주시면 해당 코드에 맞춰 수정안을 쓰겠습니다.
<!-- simple-korean: on -->
