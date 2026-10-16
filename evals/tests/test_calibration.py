import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent / "calibration"))
import hits  # noqa: E402
import ko_lint  # noqa: E402
import ko_text  # noqa: E402

COMPLIANT = HERE.parent / "calibration" / "compliant-ko.md"
DOC = "이 문서는 sqlpipe에 대해 설명합니다. 설정 파일이나 환경 변수로 값을 바꿀 수 있습니다.\n"
REPLY = ("좋은 질문입니다. 멱등성은 같은 요청을 여러 번 보내도 결과가 같은 성질이라 재시도를 효율적으로 할 수 있습니다.\n"
         "도움이 되셨기를 바랍니다.\n")


def test_compliant_translations_have_no_errors_or_long_sentences():
    text = COMPLIANT.read_text(encoding="utf-8")
    found = ko_lint.lint_detail(text, "procedural", config={})
    bad = [h for h in found if h["severity"] == "error" or h["category"] == "sentence_over_limit"]
    assert bad == [], bad


def test_compliant_translations_stay_well_under_the_limits():
    text = COMPLIANT.read_text(encoding="utf-8")
    longest = max(ko_text.eojeol_count(u.text) for u in ko_text.units(text))
    assert longest <= 12, longest


def _calibration_dir(d):
    Path(d, "docs").mkdir()
    Path(d, "reply").mkdir()
    record = {"text": DOC, "condition": "baseline", "scenario": "x", "type": "descriptive", "run": 1}
    Path(d, "docs", "baseline__x__r1.json").write_text(json.dumps(record, ensure_ascii=False), encoding="utf-8")
    Path(d, "reply", "baseline__q__r1.txt").write_text(REPLY, encoding="utf-8")
    Path(d, "meta.json").write_text(json.dumps({"date": "2026-10-09", "model": "m", "effort": "low"}), encoding="utf-8")
    return d


def _labeled(rows, fp_category):
    return [{**r, "label": "FP" if r["category"] == fp_category else "TP",
             "note": "원인" if r["category"] == fp_category else ""} for r in rows]


def test_rows_cover_default_strict_and_reply_checks():
    with tempfile.TemporaryDirectory() as d:
        rows = hits.doc_rows(_calibration_dir(d)) + hits.reply_rows(d)
    got = {(r["mode"], r["category"]) for r in rows}
    assert ("기본", "translationese") in got and ("엄격", "strict_connective") in got
    assert {("답변", "opener"), ("답변", "closer"), ("답변", "slop_word")} <= got
    assert all(r["context"] and r["label"] == "" for r in rows)


def test_tsv_round_trip_keeps_tabs_and_quotes():
    row = hits._row("docs/a.json", 3, "기본", "translationese", "warning", '에 "대해"\t', "문맥")
    with tempfile.TemporaryDirectory() as d:
        path = Path(d, "h.tsv")
        path.write_text(hits.to_tsv([row]), encoding="utf-8")
        assert hits.read_tsv(path) == [row]


def test_precision_counts_fp_left_and_tp_lost():
    a = hits._row("f", 1, "기본", "translationese", "warning", "에 대해", "c")
    b = hits._row("f", 2, "기본", "translationese", "warning", "을 통해", "c")
    c = hits._row("f", 3, "기본", "hedge", "error", "것 같", "c")
    labeled = [{**a, "label": "FP"}, {**b, "label": "TP"}, {**c, "label": "TP"}]
    table = hits.precision_table(labeled, [a, c])
    assert table["translationese"]["hits"] == 2 and table["translationese"]["FP"] == 1
    assert table["translationese"]["fp_left"] == 1 and table["translationese"]["tp_lost"] == 1
    assert table["hedge"]["TP"] == 1 and table["hedge"]["tp_lost"] == 0


def test_check_labels_flags_missing_and_unseen_rows():
    a = hits._row("f", 1, "기본", "translationese", "warning", "에 대해", "c")
    b = hits._row("f", 2, "기본", "hedge", "error", "것 같", "c")
    problems = hits.check_labels([a], [a, b])
    assert len(problems) == 2 and "판정이 없습니다" in problems[0] and "hits.tsv에 없는" in problems[1]


def test_decide_limits_only_raises_on_compliant_overflow():
    limits = {"procedural": 15, "descriptive": 20}
    compliant = {"procedural": {"max": 17}, "descriptive": {"max": 11}}
    baseline = {"procedural": {"over": 3}, "descriptive": {"over": 0}}
    decided, reasons = hits.decide_limits(limits, compliant, baseline)
    assert decided == {"procedural": 17, "descriptive": 20}
    assert "올렸습니다" in reasons["procedural"] and "그대로" in reasons["descriptive"]


def test_changelog_lines_follow_the_limits_in_use():
    kept = hits.changelog_lines({}, [], {"procedural": 12, "descriptive": 18}, {"procedural": 12, "descriptive": 18})
    assert kept == ["- 문장 길이 상한은 절차문 12어절, 설명문 18어절 그대로입니다. 규칙을 지킨 예문은 모두 상한 안이었습니다.",
                    "- 기준선 출력에서 거짓 일치를 찾지 못했습니다."]
    raised = hits.changelog_lines({}, [], {"procedural": 17, "descriptive": 20}, {"procedural": 15, "descriptive": 20})
    assert raised[0] == "- 문장 길이 상한을 바꿨습니다: 절차문 15어절에서 17어절로."


def test_record_stops_on_unlabeled_rows_and_renders_when_complete():
    with tempfile.TemporaryDirectory() as d:
        rows = hits.doc_rows(_calibration_dir(d)) + hits.reply_rows(d)
        try:
            hits.record_md(d, rows)
        except SystemExit as err:
            assert "판정이 없습니다" in str(err)
        else:
            raise AssertionError("판정 없는 행을 받아들였습니다")
        text = hits.record_md(d, _labeled(rows, "slop_word"))
    assert "## 범주별 정밀도" in text and "## CHANGELOG에 옮길 줄" in text
    assert "'슬롭 어휘' 범주에서 판정한 1건 가운데 거짓 일치 1건을 찾아 0건을 고쳤습니다. 원인은 원인입니다." in text
    assert "문장 길이 상한은 절차문 15어절, 설명문 20어절 그대로입니다." in text
