"""자료 파일의 경로를 찾는다. 설치한 패키지는 패키지 안의 사본을, 레포지토리는 원본을 쓴다."""
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent


def resource(bundled, source):
    """패키지 안에 bundled가 있으면 그 경로를, 없으면 레포지토리 최상위 기준 source 경로를 돌려준다."""
    path = HERE / bundled
    return path if path.is_file() else ROOT / source
