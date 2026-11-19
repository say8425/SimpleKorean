# 전후 예시

'전'은 스킬 없이 만든 원본 출력입니다. '후'는 같은 과제를 스킬을 켜고 만든 원본 출력입니다. 두 글 모두 고치지 않고 옮겼습니다. 다듬기 과제에는 두 조건에 준 초안도 싣습니다. 과제와 질문은 측정 전에 정했습니다(`evals/make_examples.py`의 PICKS). `python3 evals/check_numbers.py`가 이 파일의 글을 원본 파일과 글자 하나까지 대조합니다.

`examples/diffs/`에는 같은 예시의 '후' 글만 과제마다 파일 하나로 나눠 두었습니다. 예시마다 바뀐 곳은 [이 커밋의 diff](https://github.com/say8425/SimpleKorean/commit/ef1c7e3a10a975a66311cd1d88d20000d644b068)에서 볼 수 있습니다. 다듬기 과제의 diff는 초안과 '후' 글의 차이를 보입니다.

## 초안 다듬기(절차문)

초안: `evals/results/2026-11-16/inputs/scenarios.json`의 `polish` 과제

<!-- draft: evals/results/2026-11-16/inputs/scenarios.json#polish -->
<!-- simple-korean: off -->
> ## 문제 해결
>
> **Postgres 연결 타임아웃** — sqlpipe가 `connection timed out` 오류를 내면 대부분 방화벽·보안 그룹이 5432 포트를 막고 있는 것입니다. `nc -zv <호스트> 5432`로 연결되는지 확인해 보시기 바랍니다.
>
> **S3 권한 오류** — `AccessDenied`가 나면 IAM 정책·버킷 정책에 읽기·쓰기 권한(`s3:GetObject`, `s3:PutObject`)이 있는지 확인하세요. 먼저 `aws sts get-caller-identity`로 지금 쓰는 자격 증명을 확인하는 것이 좋습니다.
<!-- simple-korean: on -->

전: 스킬 없음, `evals/results/2026-11-16/docs/baseline__polish__r1.json`

<!-- source: evals/results/2026-11-16/docs/baseline__polish__r1.json -->
<!-- simple-korean: off -->
> ## 문제 해결
>
> **Postgres 연결 타임아웃** — sqlpipe가 `connection timed out` 오류를 내면 대개 방화벽이나 보안 그룹이 5432 포트를 막고 있는 경우입니다. `nc -zv <호스트> 5432`로 해당 포트에 연결되는지 먼저 확인하세요.
>
> **S3 권한 오류** — `AccessDenied`가 나면 IAM 정책과 버킷 정책에 읽기·쓰기 권한(`s3:GetObject`, `s3:PutObject`)이 있는지 확인하세요. 그 전에 `aws sts get-caller-identity`로 현재 사용 중인 자격 증명이 의도한 것인지 확인하는 것이 좋습니다.
<!-- simple-korean: on -->

후: 기본 모드, `evals/results/2026-11-16/docs/plain__polish__r1.json`

<!-- source: evals/results/2026-11-16/docs/plain__polish__r1.json -->
<!-- simple-korean: off -->
> ## 문제 해결
>
> ### Postgres 연결 타임아웃
>
> sqlpipe가 `connection timed out` 오류를 내면 대부분 방화벽이나 보안 그룹이 5432 포트를 막고 있습니다.
>
> `nc -zv <호스트> 5432`를 실행해 연결되는지 확인하세요.
>
> ### S3 권한 오류
>
> sqlpipe가 `AccessDenied` 오류를 내면 IAM 정책과 버킷 정책에 읽기 권한 `s3:GetObject`와 쓰기 권한 `s3:PutObject`가 있는지 확인하세요.
>
> 먼저 `aws sts get-caller-identity`를 실행해 지금 쓰는 자격 증명을 확인하세요.
<!-- simple-korean: on -->

## README 소개(설명문)

전: 스킬 없음, `evals/results/2026-11-16/docs/baseline__readme-intro__r1.json`

<!-- source: evals/results/2026-11-16/docs/baseline__readme-intro__r1.json -->
<!-- simple-korean: off -->
> sqlpipe는 Postgres 테이블을 Parquet 파일로 변환해 S3에 동기화하는 CLI 도구입니다. 복잡한 ETL 파이프라인이나 별도 인프라 없이, 명령어 한 줄로 원하는 테이블을 데이터 레이크에 옮길 수 있습니다. 변경된 데이터만 증분 방식으로 전송하므로 대용량 테이블도 빠르고 효율적으로 처리합니다.
>
> 설정은 간단합니다. 접속 정보와 대상 버킷만 지정하면 스키마를 자동으로 Parquet 타입에 매핑하고, 파티셔닝과 압축까지 알아서 처리합니다. 크론이나 CI 작업에 붙여 정기 동기화를 자동화해 보세요.
<!-- simple-korean: on -->

후: 기본 모드, `evals/results/2026-11-16/docs/plain__readme-intro__r1.json`

<!-- source: evals/results/2026-11-16/docs/plain__readme-intro__r1.json -->
<!-- simple-korean: off -->
> sqlpipe는 Postgres 테이블을 Parquet 파일로 변환해 S3에 동기화하는 CLI 도구입니다. 사용자는 동기화할 테이블과 S3 버킷을 지정하고 명령 하나로 실행합니다. sqlpipe는 테이블의 행을 읽어 Parquet 파일로 쓰고 지정한 버킷에 올립니다.
>
> sqlpipe를 실행하는 호스트는 Postgres와 S3에 모두 연결할 수 있어야 합니다. 연결에 실패하면 sqlpipe는 오류 메시지를 출력하고 멈춥니다.
<!-- simple-korean: on -->

## 문제 해결(절차문)

전: 스킬 없음, `evals/results/2026-11-16/docs/baseline__troubleshooting__r1.json`

<!-- source: evals/results/2026-11-16/docs/baseline__troubleshooting__r1.json -->
<!-- simple-korean: off -->
> ## 문제 해결
>
> **Postgres 연결 타임아웃**
> `connection timed out` 오류가 나면 먼저 호스트와 포트(기본 5432)에 네트워크로 접근할 수 있는지 확인하세요. 방화벽, 보안 그룹, VPN 설정을 점검하세요. 접속은 되는데 응답이 느리면 `--connect-timeout` 값을 늘리세요(예: `--connect-timeout 30`). 클라우드 DB는 SSL이 필수일 수 있으니 연결 문자열에 `sslmode=require`를 추가하세요.
>
> **S3 권한 오류**
> `AccessDenied` 또는 `403`이 나오면 사용 중인 자격 증명이 맞는지 `aws sts get-caller-identity`로 확인하세요. 해당 IAM 정책에 대상 버킷의 `s3:GetObject`, `s3:PutObject`, `s3:ListBucket` 권한이 있는지 보세요. 버킷 정책과 리전 설정이 맞는지도 확인하세요. 임시 자격 증명을 쓴다면 만료 여부도 확인하세요.
<!-- simple-korean: on -->

후: 기본 모드, `evals/results/2026-11-16/docs/plain__troubleshooting__r1.json`

<!-- source: evals/results/2026-11-16/docs/plain__troubleshooting__r1.json -->
<!-- simple-korean: off -->
> ## 문제 해결
>
> ### Postgres 연결 타임아웃
>
> sqlpipe는 Postgres 포트(기본값 5432)에 연결하지 못하면 `dial tcp: i/o timeout` 오류를 내고 멈춥니다.
>
> 1. sqlpipe를 실행하는 호스트에서 Postgres 포트에 연결할 수 있는지 확인하세요.
> 2. 연결할 수 없으면 방화벽과 보안 그룹 규칙을 확인하세요.
> 3. 데이터베이스가 관리형(RDS, Cloud SQL)이면, 인스턴스가 sqlpipe의 IP에서 오는 연결을 허용하는지 확인하세요.
>
> ### S3 권한 오류
>
> S3 요청이 `AccessDenied` 오류로 실패하면, sqlpipe가 쓰는 자격 증명에 권한이 없다는 뜻입니다.
>
> 1. sqlpipe를 실행하는 호스트에서 `aws sts get-caller-identity`를 실행해 자격 증명이 올바른지 확인하세요.
> 2. 해당 자격 증명의 IAM 정책이 대상 버킷에 `s3:GetObject`와 `s3:PutObject`를 허용하는지 확인하세요.
> 3. 버킷 정책이 해당 자격 증명을 거부하면, 거부 규칙을 고치세요.
<!-- simple-korean: on -->

## 오류 메시지

전: 스킬 없음, `evals/results/2026-11-16/docs/baseline__error-message__r1.json`

<!-- source: evals/results/2026-11-16/docs/baseline__error-message__r1.json -->
<!-- simple-korean: off -->
> sqlpipe: S3 업로드에 실패했습니다. 접근이 거부되었습니다(AccessDenied).
> 현재 IAM 자격 증명에 s3:PutObject 권한이 없습니다.
> 대상 버킷과 경로에 대한 s3:PutObject 권한을 IAM 정책에 추가한 뒤 다시 시도하세요.
<!-- simple-korean: on -->

후: 기본 모드, `evals/results/2026-11-16/docs/plain__error-message__r1.json`

<!-- source: evals/results/2026-11-16/docs/plain__error-message__r1.json -->
<!-- simple-korean: off -->
> sqlpipe가 S3에 업로드하지 못했습니다. `AccessDenied` 오류가 발생했습니다.
> IAM 자격 증명에 `s3:PutObject` 권한이 없습니다.
> IAM 정책에 `s3:PutObject` 권한을 추가한 뒤 sqlpipe를 다시 실행하세요.
<!-- simple-korean: on -->

## 릴리스 노트(엄격 모드)

전: 스킬 없음, `evals/results/2026-11-16/docs/baseline__release-notes__r1.json`

<!-- source: evals/results/2026-11-16/docs/baseline__release-notes__r1.json -->
<!-- simple-korean: off -->
> **sqlpipe v2.0 릴리스 노트**
>
> **⚠️ 호환성 깨짐**
> `/v2/users` 응답의 `name` 필드가 `first_name`과 `last_name`으로 분리되었습니다. 기존에 `name`을 읽던 코드는 업그레이드 전에 반드시 수정해 주세요.
>
> **새 기능**
> - `--incremental` 플래그 추가: 변경된 데이터만 처리할 수 있습니다.
>
> **성능 개선**
> - Parquet 쓰기 속도가 약 40% 향상되었습니다.
<!-- simple-korean: on -->

후: 엄격 모드, `evals/results/2026-11-16/docs/strict__release-notes__r1.json`

<!-- source: evals/results/2026-11-16/docs/strict__release-notes__r1.json -->
<!-- simple-korean: off -->
> ## sqlpipe v2.0
>
> sqlpipe v2.0은 호환성을 깨는 변경을 포함합니다.
>
> 호환성 깨짐:
> - `/v2/users`의 `name` 필드가 `first_name`과 `last_name`으로 나뉘었습니다.
> - `name` 필드를 읽는 클라이언트는 두 필드를 읽도록 고쳐야 합니다.
>
> 새 기능:
> - `--incremental` 플래그가 새로 생겼습니다.
>
> 개선:
> - Parquet 쓰기가 40% 빨라졌습니다.
<!-- simple-korean: on -->

## 답변: OOMKilled 질문

전: 스킬 없음, `evals/results/2026-11-16/reply/baseline__oom__r1.txt`

<!-- source: evals/results/2026-11-16/reply/baseline__oom__r1.txt -->
<!-- simple-korean: off -->
> # OOMKilled 재시작: 원인과 조치
>
> 현재 작업 디렉터리의 매니페스트나 메트릭은 확인하지 않았습니다. 아래는 일반적인 원인과 조치입니다.
>
> ## 무슨 일이 일어나는가
>
> OOMKilled는 컨테이너가 `resources.limits.memory`를 넘어서 리눅스 커널의 cgroup OOM killer가 프로세스를 SIGKILL(종료 코드 137)로 죽였다는 뜻입니다. kubelet은 `restartPolicy`에 따라 컨테이너를 다시 띄웁니다. 재시작 후에도 같은 메모리 패턴이 반복되면 CrashLoopBackOff가 됩니다. API와 워커가 둘 다 죽는다면 원인은 보통 다음 중 하나입니다.
>
> 1. **limit이 너무 낮음**: 정상 동작에 필요한 메모리가 limit보다 큽니다. 새 배포나 트래픽 증가 뒤에 흔합니다.
> 2. **메모리 누수**: 시간이 지날수록 메모리가 계속 늘다가 죽습니다.
> 3. **런타임이 컨테이너 limit을 모름**
>    - JVM은 `-Xmx`나 `MaxRAMPercentage`가 limit에 비해 너무 큽니다. 힙 외 메모리(metaspace, 스레드 스택, 다이렉트 버퍼)까지 합치면 limit을 넘습니다.
>    - Node는 `--max-old-space-size`를 설정하지 않았습니다.
>    - Python과 Go는 워커 수나 `GOMEMLIMIT` 설정이 limit과 맞지 않습니다.
> 4. **워커의 일시적 메모리 폭증**: 큰 메시지나 배치를 한꺼번에 메모리에 올리거나, 동시성(concurrency)이 높습니다.
> 5. **API 쪽 요인**: 큰 요청/응답 바디, 대용량 쿼리 결과를 통째로 로드, 커넥션 풀이나 캐시 무제한 증가, 동시 요청 급증이 있습니다.
> 6. **사이드카나 `emptyDir`(medium: Memory)**: 파드 안에서 메모리로 잡히는 다른 항목입니다.
>
> ## 먼저 확인할 것
>
> ```bash
> # 어느 컨테이너가, 언제, 몇 번 죽었는지
> kubectl describe pod <pod> | grep -A8 "Last State"
> kubectl get pod <pod> -o jsonpath='{.status.containerStatuses[*].lastState.terminated}'
>
> # 현재 사용량 vs limit
> kubectl top pod -n <ns> --containers
> kubectl get pod <pod> -o jsonpath='{.spec.containers[*].resources}'
>
> # 죽기 직전 로그
> kubectl logs <pod> --previous
> ```
>
> Prometheus/Grafana를 쓴다면 `container_memory_working_set_bytes`를 limit과 겹쳐서 보세요. 아래 모양으로 원인을 구분할 수 있습니다.
>
> - **톱니 모양**: 천천히 올라가다 죽고 다시 시작합니다. 누수 또는 무제한 캐시입니다.
> - **시작 직후 급상승**: limit이 너무 낮거나 초기 로딩이 과합니다.
> - **특정 시점에 스파이크**: 특정 요청이나 잡이 원인입니다.
>
> ## 무엇을 바꿔야 하나
>
> 1. **limit과 request를 현실에 맞추기**: 관측한 working set의 피크에 20~30% 여유를 두고 limit을 잡으세요. request는 평상시 사용량 근처로 두는 편이 좋습니다.
>    ```yaml
>    resources:
>      requests: { memory: "512Mi" }
>      limits:   { memory: "1Gi" }
>    ```
> 2. **런타임 메모리를 limit의 약 70~75%로 제한하기**
>    - JVM: `-XX:MaxRAMPercentage=70`
>    - Node: `--max-old-space-size=<limit의 약 75%>`
>    - Go: `GOMEMLIMIT`
> 3. **워커**: 동시성, prefetch, 배치 크기를 줄이고 큰 페이로드는 스트리밍으로 처리하세요. 워커와 API는 메모리 특성이 다르니 limit을 따로 잡으세요.
> 4. **API**: 요청 크기 제한, 페이지네이션, 캐시/풀 상한을 두세요. HPA를 쓴다면 메모리나 요청량 기준으로 스케일 아웃을 걸 수 있습니다.
> 5. **누수가 의심되면** limit을 올리는 것은 임시방편입니다. 힙 프로파일링(heap dump, pprof, `tracemalloc` 등)으로 근본 원인을 찾으세요.
>
> 두 파드가 동시에 죽는다면 노드 메모리 압박(노드 레벨 eviction)이나 공통 라이브러리/설정 변경도 의심해 보세요. `kubectl describe node`의 MemoryPressure와 최근 배포 변경 사항을 확인하면 됩니다.
>
> 원인을 더 좁히려면 아래를 알려 주세요.
> - Deployment 매니페스트의 `resources` 부분
> - 사용 언어와 런타임
> - `kubectl describe pod`의 `Last State` 출력
> - 메모리 그래프 모양
>
> 그러면 구체적인 값을 제안하겠습니다.
<!-- simple-korean: on -->

후: SimpleKorean, `evals/results/2026-11-16/reply/plain__oom__r1.txt`

<!-- source: evals/results/2026-11-16/reply/plain__oom__r1.txt -->
<!-- simple-korean: off -->
> 파드의 컨테이너가 메모리 한도(limit)를 넘겨 커널이 프로세스를 강제 종료하고 있고, 그 때문에 재시작이 반복됩니다. 한도를 올리거나 사용량을 줄여야 합니다. 이 클러스터의 설정은 볼 수 없어서 아래는 일반적인 원인과 확인 순서입니다.
>
> ## 무슨 일이 일어나는가
>
> 1. 컨테이너가 `resources.limits.memory`보다 많은 메모리를 씁니다.
> 2. 커널의 OOM killer(메모리 부족 시 프로세스를 죽이는 기능)가 프로세스에 SIGKILL을 보냅니다.
> 3. 종료 코드는 137이고, 파드 상태에는 `OOMKilled`가 찍힙니다.
> 4. kubelet이 컨테이너를 다시 시작합니다. 이 일이 반복되면 `CrashLoopBackOff`가 됩니다.
>
> API와 워커가 함께 죽으면 공통 원인이 있을 가능성이 큽니다. 최근 배포로 한도가 낮아졌거나, 두 서비스가 같은 런타임 설정을 쓰는 경우가 흔합니다.
>
> ## 먼저 확인할 것
>
> ```
> kubectl describe pod <파드> -n <네임스페이스>
> kubectl top pod -n <네임스페이스> --containers
> kubectl get pod <파드> -n <네임스페이스> -o jsonpath='{.spec.containers[*].resources}'
> ```
>
> - `describe`의 `Last State`에서 `Reason: OOMKilled`와 `Exit Code: 137`을 확인합니다.
> - `top`으로 사용량이 한도에 얼마나 가까운지 봅니다. `top`에는 metrics-server가 필요합니다.
> - 한도가 없거나 너무 작은지 `resources` 값을 봅니다.
> - `kubectl describe node`에서 노드 전체가 메모리 압박(MemoryPressure) 상태인지 확인합니다. 이 경우에는 파드가 쫓겨나는 Evicted가 먼저 나타날 수 있습니다.
>
> ## 바꿀 것
>
> 원인에 따라 다릅니다.
>
> - 한도가 실제 필요량보다 낮으면 `limits.memory`를 올립니다. 평소 사용량에 여유 20~30%를 더한 값이 출발점입니다.
> - 스케줄링 기준인 `requests.memory`를 실제 평상시 사용량에 맞춥니다. 안정성이 중요하면 requests와 limits를 같게 둡니다.
> - 런타임이 컨테이너 한도를 모르면 힙(heap, 프로그램이 동적으로 쓰는 메모리 영역) 상한을 직접 지정합니다.
>   - JVM: `-XX:MaxRAMPercentage=70`
>   - Node.js: `--max-old-space-size=<MB>`
>   - Go: 환경 변수 `GOMEMLIMIT`
> - 메모리 누수(leak)가 의심되면 사용량 그래프를 봅니다. 시간이 지날수록 계속 오르면 한도를 올려도 늦어질 뿐이므로 코드를 고쳐야 합니다.
>
> ## 서비스별 점검
>
> - API: 동시 요청 수, 큰 응답 본문, 요청마다 쌓이는 캐시를 확인합니다.
> - 워커: 한 번에 가져오는 작업 수(배치 크기)와 동시 처리 수를 줄입니다. 큰 파일을 통째로 메모리에 올리는 코드도 찾습니다.
>
> 한도를 올린 뒤에도 같은 간격으로 죽으면 누수일 가능성이 높습니다. `describe` 출력과 `top` 결과를 붙여 주시면 원인을 더 좁힐 수 있습니다.
<!-- simple-korean: on -->

## 답변: 캐시 무효화 질문

전: 스킬 없음, `evals/results/2026-11-16/reply/baseline__cache__r1.txt`

<!-- source: evals/results/2026-11-16/reply/baseline__cache__r1.txt -->
<!-- simple-korean: off -->
> 이 세션에서는 파일을 읽거나 검색하는 도구를 쓸 수 없어서 코드를 직접 확인하지 못했습니다. 아래는 증상(최대 10분, 목록과 상세 모두 해당, DB 앞에 Redis)을 근거로 한 추정입니다.
>
> ## 왜 그런가
>
> 가장 가능성이 높은 원인은 **가격을 바꿀 때 캐시를 무효화하지 않고 TTL(600초)이 끝나길 기다리는 것**입니다. 전형적인 cache-aside 구조에서는 이렇게 됩니다.
>
> 1. 읽기 요청이 오면 Redis에서 찾습니다. 없으면 DB에서 읽어 `SET key value EX 600`으로 저장합니다.
> 2. 가격 수정은 DB만 갱신하고 Redis의 해당 키는 그대로 둡니다.
> 3. 키가 만료될 때까지 최대 10분 동안 예전 값이 나갑니다. "최대 10분"이라는 표현은 캐시가 채워진 시점에 따라 0~10분으로 달라지는 TTL 동작과 맞아떨어집니다.
>
> 목록과 상세가 모두 오래된 값을 보여 주는 점도 같은 원인으로 설명됩니다. 둘 다 캐시되어 있는데, 가격 변경 쪽에서 둘 중 어느 것도 지우지 않기 때문입니다. 목록 캐시는 상품 하나가 아니라 **여러 상품의 가격을 한꺼번에 담은 페이지 단위 키**일 가능성이 큽니다(예: `products:list:category=3:page=1`). 그러면 상품 ID만으로는 지울 키를 찾기 어려워서, 목록은 특히 무효화가 빠지기 쉽습니다.
>
> 다른 가능성도 있습니다.
>
> - **무효화 코드는 있는데 실패하는 경우**: 키 이름 불일치, 트랜잭션 커밋 전에 삭제(삭제 직후 다른 요청이 옛 값을 다시 캐시에 채움), 예외를 삼키는 처리가 대표적입니다.
> - **상품 데이터를 읽어 온 서비스 측 로컬 캐시나 CDN/HTTP 캐시**가 따로 있는 경우도 있습니다. 이때는 Redis를 비워도 안 고쳐집니다.
> - **DB 읽기 복제본 지연**이 겹쳤을 수 있습니다. 다만 10분이라는 값은 TTL과 훨씬 잘 맞습니다.
>
> ## 어떻게 고치나
>
> 1. **쓰기 시 무효화**: 가격 변경 트랜잭션이 **커밋된 뒤에** 상세 키를 `DEL`합니다. 커밋 전에 지우면 그 사이에 옛 값이 다시 캐시에 채워집니다.
> 2. **목록 캐시 처리**: 아래 중 하나를 고릅니다.
>    - 목록 키에 버전 번호를 넣습니다(`products:list:v{N}:...`). 가격이 바뀌면 `N`을 `INCR`합니다. 구현이 가장 단순하고 안전합니다.
>    - 목록에는 상품 ID 목록만 캐시하고, 가격은 상품별 캐시에서 조합합니다(`MGET`). 그러면 상세 키만 지우면 목록에도 반영됩니다.
>    - 가격이 목록에서 중요하다면 목록 TTL만 짧게(10~30초) 줄입니다.
> 3. **안전망**: 무효화가 누락돼도 피해가 제한되도록 TTL을 줄입니다(예: 600초에서 60초). 가격은 정합성이 중요한 값이라 이 방법이 특히 유효합니다.
> 4. **재채움 경합 방지**: 인기 상품 키를 지운 직후 요청이 몰리면 DB로 쏠리거나 옛 값이 재저장될 수 있습니다. 필요하면 `SET NX` 락, 또는 가격 변경 시 새 값을 직접 `SET`하는 write-through 방식을 씁니다.
> 5. **캐시 외 계층 확인**: 응답의 `Cache-Control` 헤더, CDN, 프런트엔드(SWR/React Query 등)의 캐시 설정도 점검합니다.
>
> ## 확인 방법
>
> 가격을 바꾼 직후 `redis-cli TTL <상품키>`와 `GET`으로 키가 남아 있는지 보세요. 키가 그대로 있으면 위 원인(무효화 누락)이 확실합니다. 키가 지워져 있는데도 옛 값이 나오면 로컬 캐시, CDN, 복제본 지연 쪽을 의심하세요.
>
> 정확한 수정 위치를 짚으려면 코드를 봐야 합니다. 가격 변경 로직과 캐시 읽기 로직의 파일을 알려 주시거나 내용을 붙여 주시면 실제 코드 기준으로 패치까지 제안하겠습니다.
<!-- simple-korean: on -->

후: SimpleKorean, `evals/results/2026-11-16/reply/plain__cache__r1.txt`

<!-- source: evals/results/2026-11-16/reply/plain__cache__r1.txt -->
<!-- simple-korean: off -->
> 원인은 쓰기 경로가 캐시를 지우지 않기 때문일 가능성이 높습니다. 코드를 보지 않고 쓴 추정이므로, 아래 확인 항목으로 먼저 검증하세요.
>
> ## 왜 10분 동안 예전 가격이 보이나
>
> 읽기 때 DB 결과를 Redis에 저장하고 TTL(만료 시간)을 10분으로 두는 방식(cache-aside)을 쓰면 이런 현상이 생깁니다. 가격을 바꿔도 DB만 갱신되고 Redis 키는 그대로 남습니다. 키가 만료될 때까지 읽기 요청은 예전 값을 받습니다.
>
> 목록 페이지는 더 복잡합니다. 목록 캐시에 가격이 통째로 들어 있으면, 상품 하나의 가격이 여러 목록 키에 흩어져 있습니다. 어느 키를 지워야 하는지 쓰기 쪽에서 알기 어렵습니다.
>
> ## 먼저 확인할 것
>
> - 가격 변경 코드가 Redis 키를 지우거나 갱신하는지 확인하세요.
> - Redis 말고 다른 캐시 계층이 있는지 확인하세요. CDN, `Cache-Control` 헤더, 서버 메모리 캐시가 해당됩니다.
> - DB 읽기 복제본(replica)을 쓰면 복제 지연도 확인하세요.
>
> ## 고치는 방법
>
> 1. 상세 캐시는 DB 커밋 뒤에 키를 삭제하세요. 값을 덮어쓰지 말고 삭제해야 합니다. 동시 요청이 옛 값을 다시 써 넣는 경합을 줄일 수 있습니다.
> 2. 목록 캐시에는 상품 ID 목록만 저장하세요. 가격은 상품별 키에서 `MGET`으로 한 번에 읽으세요. 그러면 가격 변경 때 상품 키 하나만 지우면 됩니다.
> 3. 목록에 가격을 꼭 넣어야 하면 네임스페이스 버전 키를 쓰세요. 예를 들어 `list:v{N}:...` 형태로 쓰고, 가격이 바뀌면 N을 올리세요. 옛 키는 TTL로 사라집니다.
> 4. 삭제 실패에 대비하세요. 앱이 커밋 뒤 삭제 전에 죽으면 예전 가격이 남습니다. 아웃박스(outbox) 테이블이나 CDC(DB 변경 로그 수집)로 삭제 이벤트를 보장하세요.
> 5. TTL은 안전망으로 남기세요. 가격 데이터는 1~2분으로 줄이고 지터(무작위 편차)를 더하면 만료가 한꺼번에 몰리지 않습니다.
>
> 가장 작은 수정은 1번과 2번입니다. 가격 변경 API와 목록 조회 코드의 위치를 알려 주시면 해당 코드를 보고 구체적인 패치를 제안하겠습니다.
<!-- simple-korean: on -->
