파드의 컨테이너가 메모리 한도(limit)를 넘어서 커널이 프로세스를 강제 종료하고 있습니다. kubelet이 컨테이너를 다시 시작하므로 재시작이 반복됩니다. 클러스터와 매니페스트는 제가 보지 못했습니다. 아래는 일반적인 원인과 확인 순서입니다.

## 무슨 일이 일어나는가

1. 컨테이너 메모리 사용량이 `resources.limits.memory`에 닿습니다.
2. 리눅스 OOM killer(메모리 부족 시 프로세스를 죽이는 커널 기능)가 프로세스에 SIGKILL을 보냅니다.
3. 종료 코드는 137이고 사유는 `OOMKilled`입니다.
4. kubelet이 컨테이너를 다시 시작합니다. 반복되면 `CrashLoopBackOff`로 바뀝니다.

API와 워커가 모두 죽으면 공통 원인을 먼저 의심해야 합니다. 두 파드에 같은 한도 값이 있거나, 같은 런타임 설정을 쓰거나, 같은 노드에서 돌고 있을 수 있습니다.

## 먼저 확인할 것

사유와 종료 코드를 확인하세요. `<pod>`와 `<ns>`는 실제 값으로 바꾸세요.

```
kubectl describe pod <pod> -n <ns>
```

출력의 `Last State: Terminated`에서 `Reason: OOMKilled`와 `Exit Code: 137`을 찾으세요.

현재 사용량과 한도를 비교하세요. 이 명령은 metrics-server가 설치되어 있어야 합니다.

```
kubectl top pod -n <ns> --containers
kubectl get pod <pod> -n <ns> -o jsonpath='{.spec.containers[*].resources}'
```

## 원인별 조치

- 한도가 실제 사용량보다 낮으면 `limits.memory`를 올리세요. 평상시 최대 사용량보다 여유를 두어야 합니다.
- 사용량이 시간에 따라 계속 오르면 메모리 누수입니다. 한도를 올려도 재시작 주기만 늘어납니다. 힙 프로파일을 떠서 코드를 고쳐야 합니다.
- JVM이나 Node.js를 쓰면 힙 크기 설정이 컨테이너 한도보다 커서 죽을 수 있습니다. 힙 외 메모리(스레드 스택, 메타스페이스, 네이티브 버퍼)도 한도에 포함됩니다. JVM은 `-XX:MaxRAMPercentage=70` 같은 값으로, Node.js는 `--max-old-space-size`로 힙을 한도보다 작게 맞춰야 합니다.
- 워커가 큰 작업을 한꺼번에 처리하면 순간 사용량이 치솟습니다. 동시 처리 수나 배치 크기를 줄이세요.
- `requests.memory`가 너무 낮으면 노드에 파드가 과하게 몰립니다. 노드 전체 메모리가 부족해지면 한도 이내여도 종료될 수 있습니다. `requests`를 실제 평균 사용량에 맞추세요.

## 변경 예시

```yaml
resources:
  requests:
    memory: "512Mi"
  limits:
    memory: "1Gi"
```

값은 `kubectl top`으로 본 실제 사용량을 기준으로 정해야 합니다.

`kubectl describe` 출력과 `resources` 설정, 사용 중인 런타임(JVM, Node.js 등)을 알려 주시면 구체적인 값을 제안하겠습니다.
