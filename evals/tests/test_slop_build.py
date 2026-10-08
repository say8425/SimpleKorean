import importlib.util
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "evals"))
_spec = importlib.util.spec_from_file_location("build_slop", ROOT / "tools" / "slop-lexicon" / "build_slop.py")
build_slop = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(build_slop)


def test_rule_text_keeps_rule_lines_and_quotes():
    text = ("소개 문장입니다. 원활한 협업을 돕습니다.\n| 원활한 | 지우세요 |\n"
            "- \"획기적인\"을 지우세요\n일반 문장의 '강력한' 인용\n")
    got = build_slop.rule_text(text)
    assert "| 원활한 |" in got and "획기적인" in got and "강력한" in got
    assert "협업을 돕습니다" not in got


def test_count_sources_counts_each_source_once():
    texts = {"a": "| 원활한 | x |\n| 원활하게 | y |", "b": "- 원활한 처리", "c": "본문에만 원활한 말이 있습니다"}
    assert build_slop.count_sources(["원활"], texts) == {"원활": 2}


def test_covered_elsewhere_skips_other_categories():
    assert build_slop.covered_elsewhere("에 대해") is True
    assert build_slop.covered_elsewhere("것 같습니다") is True
    assert build_slop.covered_elsewhere("원활한") is False


def test_build_rows_threshold_exclusions_and_sort():
    texts = {k: "| 원활 | 획기적 | 강력한 | 에 대해 |" for k in "abc"}
    texts["d"] = "| 원활 |"
    rows = build_slop.build_rows([["원활", "(지우세요)"], ["획기적", "새"], ["강력한"], ["에 대해", "x"]],
                                 [["강력한", "시험용 제외"]], texts, threshold=3)
    assert rows == [("원활", 4, "(지우세요)"), ("획기적", 3, "새")], rows


def test_write_tsv_round_trips_through_linter_loader():
    import ko_rules
    with tempfile.TemporaryDirectory() as d:
        out = Path(d, "slop.tsv")
        build_slop.write_tsv([("원활", 4, "(지우세요)")], 10, out)
        assert out.read_text(encoding="utf-8").startswith("# SimpleKorean 슬롭 어휘")
        assert "원활" in ko_rules.load_slop_terms(out)


def test_fetch_uses_pinned_commit_and_separate_dirs():
    calls = []

    class Resp:
        def __init__(self, url):
            self.url = url

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

        def read(self):
            return "| 원활 |".encode("utf-8")

    def opener(url, timeout):
        calls.append(url)
        return Resp(url)

    with tempfile.TemporaryDirectory() as d:
        sources = [{"repo": "o/r", "commit": "abc123", "files": ["a/b.md"]}]
        build_slop.fetch(sources, cache=Path(d), opener=opener)
        assert calls == ["https://raw.githubusercontent.com/o/r/abc123/a/b.md"]
        assert Path(d, "o__r", "a", "b.md").read_text(encoding="utf-8") == "| 원활 |"
        assert build_slop.source_texts(sources, cache=Path(d)) == {"o/r": "| 원활 |"}
