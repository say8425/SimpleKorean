## sqlpipe v2.0

sqlpipe v2.0은 호환성을 깨는 변경을 포함합니다.

호환성 깨짐:
- `/v2/users`의 `name` 필드가 `first_name`과 `last_name`으로 나뉘었습니다.
- `name` 필드를 읽는 클라이언트는 두 필드를 읽도록 고쳐야 합니다.

새 기능:
- `--incremental` 플래그가 새로 생겼습니다.

개선:
- Parquet 쓰기가 40% 빨라졌습니다.
