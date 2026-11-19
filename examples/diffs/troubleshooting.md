## 문제 해결

### Postgres 연결 타임아웃

sqlpipe는 Postgres 포트(기본값 5432)에 연결하지 못하면 `dial tcp: i/o timeout` 오류를 내고 멈춥니다.

1. sqlpipe를 실행하는 호스트에서 Postgres 포트에 연결할 수 있는지 확인하세요.
2. 연결할 수 없으면 방화벽과 보안 그룹 규칙을 확인하세요.
3. 데이터베이스가 관리형(RDS, Cloud SQL)이면, 인스턴스가 sqlpipe의 IP에서 오는 연결을 허용하는지 확인하세요.

### S3 권한 오류

S3 요청이 `AccessDenied` 오류로 실패하면, sqlpipe가 쓰는 자격 증명에 권한이 없다는 뜻입니다.

1. sqlpipe를 실행하는 호스트에서 `aws sts get-caller-identity`를 실행해 자격 증명이 올바른지 확인하세요.
2. 해당 자격 증명의 IAM 정책이 대상 버킷에 `s3:GetObject`와 `s3:PutObject`를 허용하는지 확인하세요.
3. 버킷 정책이 해당 자격 증명을 거부하면, 거부 규칙을 고치세요.
