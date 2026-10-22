"""src/simple_korean/ko_terms.py를 옛 경로에서 쓴다. 이 경로로 import하면 패키지의 모듈을 그대로 받는다."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from simple_korean import ko_terms as _module  # noqa: E402

sys.modules[__name__] = _module
