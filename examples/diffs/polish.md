## 문제 해결

**Postgres 연결 타임아웃** — sqlpipe가 `connection timed out` 오류를 내면 대부분 방화벽·보안 그룹이 5432 포트를 막고 있는 것입니다. `nc -zv <호스트> 5432`로 연결되는지 확인해 보시기 바랍니다.

**S3 권한 오류** — `AccessDenied`가 나면 IAM 정책·버킷 정책에 읽기·쓰기 권한(`s3:GetObject`, `s3:PutObject`)이 있는지 확인하세요. 먼저 `aws sts get-caller-identity`로 지금 쓰는 자격 증명을 확인하는 것이 좋습니다.
