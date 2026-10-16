import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import check_pr_title as pt  # noqa: E402


def test_good_titles_pass():
    for title in ("fix: 설정 파일의 지정형을 20자로 제한한다",
                  "ci: release-please로 릴리스 PR을 만든다",
                  "docs: README를 영어, 일본어, 중국어, 스페인어로 옮긴다",
                  "feat: `ko_lint`가 BOM 뒤의 frontmatter를 건너뛴다."):
        assert pt.problems(title) == [], title


def test_format_errors_name_the_rule():
    for title in ("", "설정 파일을 고친다", "fix(hooks): 훅을 고친다", "feat!: 규칙을 바꾼다",
                  "fix：전각 콜론을 쓴다", "fix:  공백이 둘이다", "Fix: 대문자 유형을 쓴다", "style: 서식을 고친다"):
        found = pt.problems(title)
        assert len(found) == 1 and "'<유형>: <내용>'" in found[0], title


def test_content_must_be_haera():
    assert any("해라체" in p for p in pt.problems("fix: 설정 파일의 지정형을 20자로 제한합니다"))
    assert any("해라체" in p for p in pt.problems("docs: README 번역 추가"))


def test_content_must_pass_the_linter():
    assert any(p.startswith("린터 ") and "메세지" in p for p in pt.problems("fix: 메세지 처리를 고친다"))


def test_changelog_sections_cover_the_title_types():
    config = json.loads((pt.ROOT / "release-please-config.json").read_text(encoding="utf-8"))
    sections = {s["type"]: s for s in config["changelog-sections"]}
    assert set(sections) == set(pt.TYPES)
    assert {t for t, s in sections.items() if not s.get("hidden")} == {"feat", "fix", "perf"}


def test_main_reads_the_title_from_the_environment():
    old = os.environ.get("PR_TITLE")
    try:
        os.environ["PR_TITLE"] = "fix: 설정 파일의 지정형을 20자로 제한한다"
        assert pt.main() == 0
        os.environ["PR_TITLE"] = "fix: 고쳤습니다"
        assert pt.main() == 1
        del os.environ["PR_TITLE"]
        assert pt.main() == 1
    finally:
        if old is None:
            os.environ.pop("PR_TITLE", None)
        else:
            os.environ["PR_TITLE"] = old
