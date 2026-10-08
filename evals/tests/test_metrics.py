import importlib.util
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "evals"))
import metrics  # noqa: E402

_spec = importlib.util.spec_from_file_location("extract", ROOT / "tools" / "basic-vocabulary" / "extract.py")
extract = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(extract)

NS = 'xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"'
RNS = 'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"'


def _write_xlsx(path, rows):
    shared = sorted({v for row in rows for v in row})
    index = {v: i for i, v in enumerate(shared)}
    body = "".join(
        f'<row r="{r}">' + "".join(f'<c r="{chr(65 + c)}{r}" t="s"><v>{index[v]}</v></c>' for c, v in enumerate(row)) + "</row>"
        for r, row in enumerate(rows, 1))
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("xl/workbook.xml", f'<workbook {NS} {RNS}><sheets><sheet name="{extract.SHEET}" sheetId="1" r:id="rId1"/></sheets></workbook>')
        z.writestr("xl/_rels/workbook.xml.rels", '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Target="worksheets/sheet1.xml" Type="t"/></Relationships>')
        z.writestr("xl/sharedStrings.xml", f"<sst {NS}>" + "".join(f"<si><t>{s}</t></si>" for s in shared) + "</sst>")
        z.writestr("xl/worksheets/sheet1.xml", f"<worksheet {NS}><sheetData>{body}</sheetData></worksheet>")


def test_extract_keeps_four_columns_and_drops_meaning():
    with tempfile.TemporaryDirectory() as d:
        xlsx = Path(d, "list.xlsx")
        _write_xlsx(xlsx, [["등급", "어휘", "표준동형어번호수정", "품사", "어종", "원어", "의미", "분야"],
                           ["1등급", "학교", "0", "명사", "한자어", "學校", "뜻풀이", "일반어"],
                           ["1등급", "가다", "1", "동사", "고유어", "", "뜻풀이", "일반어"]])
        records = extract.extract(extract.read_rows(xlsx))
        assert records == [("1등급", "학교", "명사", "한자어"), ("1등급", "가다", "동사", "고유어")]
        extract.check_counts(records, expected={"1등급": 2})
        out = Path(d, "grades.tsv")
        extract.write_tsv(records, out)
        text = out.read_text(encoding="utf-8")
        assert text.splitlines()[0] == "등급\t어휘\t품사\t어종" and "뜻풀이" not in text


def test_check_counts_stops_on_mismatch():
    try:
        extract.check_counts([("1등급", "학교", "명사", "한자어")], expected={"1등급": 2})
    except SystemExit as err:
        assert "등급별 개수" in str(err)
    else:
        raise AssertionError("SystemExit가 나야 합니다")


def test_grade1_lemmas_maps_pos_to_kiwi_tags():
    with tempfile.TemporaryDirectory() as d:
        tsv = Path(d, "grades.tsv")
        tsv.write_text("등급\t어휘\t품사\t어종\n1등급\t학교\t명사\t한자어\n1등급\t가다\t동사/보조동사\t고유어\n"
                       "1등급\t다시\t명사/부사\t고유어\n2등급\t설치\t명사\t한자어\n", encoding="utf-8")
        assert metrics.grade1_lemmas(str(tsv)) == frozenset({("학교", "NNG"), ("가다", "VV"), ("다시", "NNG"), ("다시", "MAG")})


def test_easy_word_counts_with_or_without_kiwi():
    got = metrics.easy_word_counts("나는 학교에 갑니다.")
    try:
        import kiwipiepy  # noqa: F401
    except ImportError:
        assert got is None
        return
    hits, total = got
    assert total >= 2 and hits >= 2, got
