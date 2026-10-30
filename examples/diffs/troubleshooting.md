## 문제 해결

### Postgres 연결 타임아웃
`connection timed out` 오류가 나면 먼저 호스트와 포트(기본 5432)에 네트워크로 접근되는지 확인하세요. `nc -vz <호스트> 5432`로 점검할 수 있습니다. 방화벽이나 보안 그룹이 현재 IP를 허용하는지, VPN이 필요한 환경인지도 살펴보세요. 연결은 되는데 응답이 느리다면 `--connect-timeout 30`처럼 제한 시간을 늘려 보세요. 접속 URL에 `sslmode`가 서버 설정과 맞게 지정되어 있는지도 확인하세요.

### S3 권한 오류
`AccessDenied` 또는 `403`이 나오면 현재 자격 증명을 `aws sts get-caller-identity`로 확인하세요. 의도한 계정과 역할이 아니라면 `AWS_PROFILE` 설정을 바로잡으세요. 해당 역할에는 대상 버킷에 대한 `s3:GetObject`, `s3:PutObject`, `s3:ListBucket` 권한이 필요합니다. `ListBucket`은 버킷 ARN에, 나머지는 `버킷/*`에 부여해야 합니다. 버킷 정책과 KMS 암호화 키 권한도 함께 점검하세요.
