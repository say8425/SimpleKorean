#!/usr/bin/env python3
"""src/simple_korean/ko_lint.py를 옛 경로에서 쓴다. 이 경로로 import하면 패키지의 모듈을 그대로 받는다."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from simple_korean import ko_lint as _module  # noqa: E402

if __name__ == "__main__":
    sys.exit(_module.main())
sys.modules[__name__] = _module
