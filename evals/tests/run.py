#!/usr/bin/env python3
"""evals/tests의 test_* 함수를 모두 돌린다. pytest 없이 표준 라이브러리로 돈다.

    python3 evals/tests/run.py                         # 전부
    python3 evals/tests/run.py evals/tests/test_ko_text.py   # 파일 하나
"""
import importlib.util
import sys
import traceback
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))


def run(paths):
    """파일마다 test_로 시작하는 함수를 돌리고 실패 수를 돌려준다."""
    failures = 0
    for path in paths:
        spec = importlib.util.spec_from_file_location(path.stem, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        for name in sorted(n for n in dir(module) if n.startswith("test_")):
            try:
                getattr(module, name)()
                print(f"ok   {path.stem}.{name}")
            except Exception:  # noqa: BLE001  모든 실패를 모아 보고한다
                failures += 1
                print(f"FAIL {path.stem}.{name}")
                traceback.print_exc()
    return failures


if __name__ == "__main__":
    selected = [Path(a).resolve() for a in sys.argv[1:]] or sorted(HERE.glob("test_*.py"))
    sys.exit(1 if run(selected) else 0)
