"""python -m simple_korean: 린터 명령. 인자는 evals/ko_lint.py와 같다."""
import sys

from .ko_lint import main

sys.exit(main())
