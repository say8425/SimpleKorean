## 문제 해결

### Postgres 연결 타임아웃

sqlpipe가 `connection timed out` 오류를 내면 대부분 방화벽이나 보안 그룹이 5432 포트를 막고 있습니다.

`nc -zv <호스트> 5432`를 실행해 연결되는지 확인하세요.

### S3 권한 오류

sqlpipe가 `AccessDenied` 오류를 내면 IAM 정책과 버킷 정책에 읽기 권한 `s3:GetObject`와 쓰기 권한 `s3:PutObject`가 있는지 확인하세요.

먼저 `aws sts get-caller-identity`를 실행해 지금 쓰는 자격 증명을 확인하세요.
