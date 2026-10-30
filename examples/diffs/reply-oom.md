클러스터나 매니페스트를 아직 보지 못했습니다. 그래서 아래는 일반적인 원인과 진단 순서입니다. 실제 수치를 알려주시면 구체적으로 짚어드리겠습니다.

## 무슨 일이 일어나는 건가

OOMKilled는 컨테이너가 `resources.limits.memory`를 넘겨서 커널의 cgroup OOM killer가 프로세스를 SIGKILL(종료 코드 137)로 죽였다는 뜻입니다. 그러면 kubelet이 `restartPolicy`에 따라 컨테이너를 다시 띄우고, 이 과정이 반복되면 `CrashLoopBackOff`가 됩니다. 노드 전체의 메모리가 부족한 경우가 아니라 **컨테이너 단위의 limit 초과**가 보통입니다. 다만 노드 메모리 압박으로 인한 eviction은 `Evicted`로 표시되어 OOMKilled와 구분됩니다.

API와 워커가 동시에 죽는다면 다음 원인 중 하나일 가능성이 큽니다.

1. **limit이 너무 낮음.** 기본값이나 복사해 온 값(예: 256Mi)이 실제 사용량보다 작습니다.
2. **최근 배포 이후 메모리 사용량 증가.** 두 파드가 같은 코드나 라이브러리를 공유하면 같이 터집니다.
3. **메모리 누수.** 시간이 지날수록 메모리가 계속 늘어납니다.
4. **런타임이 limit을 인식하지 못함.**
   - JVM: 힙 설정(`-Xmx`)이 limit보다 크거나 off-heap 몫이 없는 경우
   - Node: `--max-old-space-size`
   - Python/Go: 캐시나 GOMEMLIMIT 미설정
5. **워커의 큰 작업.** 큰 페이로드를 통째로 메모리에 올리거나, concurrency가 너무 높거나, prefetch가 큰 경우입니다.
6. **API의 트래픽 급증.** 동시 요청마다 메모리가 늘어납니다.

## 확인 방법

```bash
kubectl describe pod <pod> | grep -A5 "Last State"   # Reason: OOMKilled, Exit Code 137 확인
kubectl top pod --containers -n <ns>                 # 현재 사용량 (metrics-server 필요)
kubectl get pod <pod> -o jsonpath='{.spec.containers[*].resources}'
kubectl get events -n <ns> --sort-by=.lastTimestamp | tail -30
```

Prometheus나 Grafana가 있다면 `container_memory_working_set_bytes`를 limit과 겹쳐서 보세요. 그래프가 우상향이면 누수이고, 계단식이나 스파이크면 특정 요청이나 작업이 원인입니다. 재시작 직전에 limit에 닿는지도 확인하세요.

## 바꿔야 할 것

- **limit과 request를 실측값 기준으로 조정합니다.** 피크 사용량에 20~30% 여유를 둔 값을 limit으로 잡습니다. 메모리는 압축할 수 없는 자원이라 **request와 limit을 같게** 두는 편이 안전합니다.
  ```yaml
  resources:
    requests: { memory: "768Mi" }
    limits:   { memory: "768Mi" }
  ```
- **런타임 설정을 limit에 맞춥니다.**
  - JVM: `-XX:MaxRAMPercentage=70`
  - Node: `--max-old-space-size`를 limit의 약 75%로
  - Go: `GOMEMLIMIT`을 limit의 약 90%로
- **워커는 concurrency, 배치 크기, prefetch를 줄이거나 스트리밍 처리로 바꿉니다.**
- **API는 HPA로 수평 확장하고, 요청 크기와 동시성을 제한합니다.**
- **누수라면 limit을 올려도 재시작 주기만 늘어납니다.** 이 경우 프로파일링(heap dump, pprof 등)으로 원인을 찾아야 합니다.

limit을 올리기 전에 위 `describe` 결과와 메모리 그래프 모양, 그리고 최근 배포가 있었는지부터 확인하세요. 아래 정보를 주시면 어느 원인인지 좁혀드리겠습니다.

- 사용 언어와 런타임
- 현재 requests/limits 값
- `kubectl describe pod`의 `Last State` 출력

매니페스트나 Helm values 파일이 이 환경에 있으면 경로를 알려주세요. 직접 읽고 수정안을 제안하겠습니다.
