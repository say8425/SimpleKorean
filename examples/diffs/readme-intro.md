sqlpipe는 Postgres 테이블을 Parquet 파일로 변환해 S3에 동기화하는 CLI 도구입니다. 사용자는 동기화할 테이블과 S3 버킷을 지정하고 명령 하나로 실행합니다. sqlpipe는 테이블의 행을 읽어 Parquet 파일로 쓰고 지정한 버킷에 올립니다.

sqlpipe를 실행하는 호스트는 Postgres와 S3에 모두 연결할 수 있어야 합니다. 연결에 실패하면 sqlpipe는 오류 메시지를 출력하고 멈춥니다.
