import re
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[2] / "skills" / "simple-korean"
SKILL_RELATIVE = re.compile(r"<스킬 디렉터리>/([^\s`]+)")


def test_paths_given_relative_to_the_skill_directory_exist():
    found = [(md.name, rel) for md in sorted(SKILL_DIR.rglob("*.md"))
             for rel in SKILL_RELATIVE.findall(md.read_text(encoding="utf-8"))]
    assert any(name == "strict-mode.md" and rel.endswith("evals/ko_lint.py") for name, rel in found), found
    missing = [(name, rel) for name, rel in found if not (SKILL_DIR / rel).resolve().is_file()]
    assert missing == [], missing
