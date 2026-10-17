import subprocess
import sys
import tempfile
import time
import unicodedata
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import ko_lint  # noqa: E402

LINT = HERE.parent / "ko_lint.py"


def run_cli(*args, cwd=None):
    return subprocess.run([sys.executable, str(LINT), *args], capture_output=True, text=True, cwd=cwd)


def test_self_test_passes():
    ko_lint.self_test()


def test_detail_matches_counts():
    report = ko_lint.lint(ko_lint.SLOP_FIXTURE, "procedural", config={})
    detail = ko_lint.lint_detail(ko_lint.SLOP_FIXTURE, "procedural", config={})
    assert len(detail) == report["violations_total"]
    assert Counter(h["category"] for h in detail) == Counter(report["violations"])


def test_nfd_input_matches_nfc():
    nfd = unicodedata.normalize("NFD", ko_lint.SLOP_FIXTURE)
    assert ko_lint.lint_detail(nfd, config={}) == ko_lint.lint_detail(ko_lint.SLOP_FIXTURE, config={})


def test_crlf_matches_lf():
    crlf = ko_lint.SLOP_FIXTURE.replace("\n", "\r\n")
    assert ko_lint.lint_detail(crlf, config={}) == ko_lint.lint_detail(ko_lint.SLOP_FIXTURE, config={})


def test_large_document_is_fast():
    big = (ko_lint.SLOP_FIXTURE + "\n" + ko_lint.CLEAN_FIXTURE + "\n") * 400
    start = time.time()
    ko_lint.lint(big, config={})
    assert time.time() - start < 5.0, time.time() - start


def test_dense_term_document_is_fast():
    line = "캐시백 캐시를 레포트 레포에 디플로이먼트 디렉토리와 메세지를 남깁니다.\n"
    big = line * (360 * 1024 // len(line.encode("utf-8")))
    start = time.time()
    report = ko_lint.lint(big, config={})
    elapsed = time.time() - start
    assert report["violations"].get("spelling", 0) > 10_000, report["violations"]
    assert elapsed < 2.0, elapsed


def test_frontmatter_is_not_linted():
    text = "---\nname: x\ndescription: 강력한 도구 — 정말\n---\n로그를 읽으세요.\n"
    assert ko_lint.lint(text, config={})["violations_total"] == 0


def test_frontmatter_after_a_bom_is_not_linted():
    text = "﻿---\nname: x\ndescription: 강력한 도구 — 정말\n---\n로그를 읽으세요.\n"
    assert ko_lint.lint(text, config={})["violations_total"] == 0


def test_html_entities_are_not_semicolons():
    text = "표 칸에 A&nbsp;B와 &#124; 기호를 씁니다.\n"
    assert ko_lint.lint(text, config={})["violations_total"] == 0
    assert ko_lint.lint("첫째; 둘째입니다.\n", config={})["violations"] == {"semicolon": 1}


def test_bad_text_type_fails_fast():
    try:
        ko_lint.lint("본문입니다.", "reply")
    except ValueError as err:
        assert "text_type" in str(err)
    else:
        raise AssertionError("ValueError가 나야 합니다")


def test_cli_gate_fails_on_errors_only():
    with tempfile.TemporaryDirectory() as d:
        warn = Path(d, "warn.md")
        warn.write_text("서버에 대해 설명합니다.\n", encoding="utf-8")
        err = Path(d, "err.md")
        err.write_text("메세지를 보냅니다.\n", encoding="utf-8")
        assert run_cli("--gate", str(warn)).returncode == 0
        assert run_cli("--gate=warning", str(warn)).returncode == 1
        r = run_cli("--gate", str(warn), str(err))
        assert r.returncode == 1 and "메세지" in r.stdout, r.stdout


def test_cli_accepts_flags_written_with_an_equals_sign():
    with tempfile.TemporaryDirectory() as d:
        warn = Path(d, "warn.md")
        warn.write_text("서버에 대해 설명합니다.\n", encoding="utf-8")
        err = Path(d, "err.md")
        err.write_text("메세지를 보냅니다.\n", encoding="utf-8")
        config = Path(d, "team.json")
        config.write_text('{"terms": {"message": {"write": "메세지", "reason": "팀 표기"}}}', encoding="utf-8")
        r = run_cli("--type=procedural", str(warn))
        assert r.returncode == 0 and '"type": "procedural"' in r.stdout, (r.returncode, r.stderr)
        assert run_cli("--gate=error", str(warn)).returncode == 0
        assert run_cli("--gate=error", str(err)).returncode == 1
        r = run_cli(f"--config={config}", "--gate", str(err))
        assert r.returncode == 0 and '"violations_total": 0' in r.stdout, (r.returncode, r.stdout, r.stderr)


def test_cli_rejects_an_unknown_flag():
    with tempfile.TemporaryDirectory() as d:
        doc = Path(d, "a.md")
        doc.write_text("로그를 읽으세요.\n", encoding="utf-8")
        for flag in ("--strcit", "--gate=everything", "--type"):
            r = run_cli(flag, str(doc))
            assert r.returncode != 0 and "사용법" in r.stderr and "No such file" not in r.stderr, (flag, r.stderr)


def test_cli_names_a_file_that_is_not_utf8():
    with tempfile.TemporaryDirectory() as d:
        doc = Path(d, "legacy.md")
        doc.write_bytes("로그를 읽으세요.\n".encode("cp949"))
        r = run_cli(str(doc))
        assert r.returncode != 0 and "legacy.md" in r.stderr and "UTF-8" in r.stderr, r.stderr
        assert "설정 파일" not in r.stderr and "Traceback" not in r.stderr, r.stderr


def test_cli_uses_project_config():
    with tempfile.TemporaryDirectory() as d:
        Path(d, ".simple-korean.json").write_text('{"terms": {"release": "릴리즈"}}', encoding="utf-8")
        doc = Path(d, "a.md")
        doc.write_text("릴리즈 노트를 봅니다.\n", encoding="utf-8")
        assert '"violations_total": 0' in run_cli(str(doc)).stdout


def test_cli_rejects_broken_config():
    with tempfile.TemporaryDirectory() as d:
        Path(d, ".simple-korean.json").write_text("{broken", encoding="utf-8")
        doc = Path(d, "a.md")
        doc.write_text("로그를 읽으세요.\n", encoding="utf-8")
        r = run_cli(str(doc))
        assert r.returncode != 0 and ".simple-korean.json" in r.stderr, (r.returncode, r.stderr)


def test_reader_check_reply_counts():
    report = ko_lint.reader_check(ko_lint.REPLY_FIXTURE)
    r = report["counts"]
    assert (r["sentences"], r["em_dash"], r["bold_spans"], r["headers"], r["bullets"]) == (5, 1, 1, 1, 2)
    # 헤더와 목록 항목은 세기만 한다. 답변 규칙이 막는 서식은 em-dash와 굵은 글씨다
    assert report["visible_total"] == 2, report


def test_reader_check_counts_tables_and_lead_structure():
    r = ko_lint.reader_check("답은 둘입니다.\n\n| 이름 | 값 |\n|---|:-:|\n| a | 1 |\n")
    assert (r["counts"]["tables"], r["counts"]["lead_structure"], r["visible_total"]) == (1, 0, 1), r
    lead = ko_lint.reader_check("## 요약\n\n디스크가 가득 찼습니다.\n")
    assert (lead["counts"]["lead_structure"], lead["counts"]["headers"], lead["visible_total"]) == (1, 1, 1), lead
    # 네 칸 이상 들여 쓴 줄은 코드다
    assert ko_lint.reader_check("    - 코드 안의 줄\n답입니다.\n")["counts"]["lead_structure"] == 0
    assert ko_lint.reader_check("\n  1. 로그를 지우세요.\n2. 다시 배포하세요.\n")["counts"]["lead_structure"] == 1
    # 답을 쓴 첫 문장 뒤의 헤더와 목록은 결함이 아니다
    shaped = ko_lint.reader_check("디스크가 가득 찼습니다.\n\n## 원인\n\n로그가 쌓였습니다. 정리하지 않았습니다.\n\n- 하나\n- 둘\n- 셋\n")
    assert (shaped["counts"]["lead_structure"], shaped["counts"]["bullets"], shaped["visible_total"]) == (0, 3, 0), shaped
    fenced = ko_lint.reader_check("```\n| a |\n|---|\n```\n표가 아닙니다. 코드 블록입니다.\n")["counts"]
    assert (fenced["tables"], fenced["lead_structure"]) == (0, 0), fenced


def test_cli_reply_gate_allows_structure_but_not_tables():
    with tempfile.TemporaryDirectory() as d:
        shaped = Path(d, "shaped.txt")
        shaped.write_text("디스크가 가득 찼습니다.\n\n## 원인\n\n로그가 쌓였습니다.\n\n1. 지우세요.\n2. 늘리세요.\n3. 배포하세요.\n",
                          encoding="utf-8")
        table = Path(d, "table.txt")
        table.write_text("답입니다.\n\n| a | b |\n|---|---|\n| 1 | 2 |\n", encoding="utf-8")
        assert run_cli("--type", "reply", "--gate", str(shaped)).returncode == 0
        r = run_cli("--type", "reply", "--gate", str(table))
        assert r.returncode != 0 and '"tables": 1' in r.stdout, (r.returncode, r.stdout)


def test_reply_fillers():
    assert ko_lint.reply_fillers("좋은 질문입니다! 답은 이렇습니다.") == (True, False)
    assert ko_lint.reply_fillers("네, 멱등성에 대해 설명드리겠습니다. 답입니다.") == (True, False)
    assert ko_lint.reply_fillers("답입니다. 도움이 되셨기를 바랍니다.") == (False, True)
    assert ko_lint.reply_fillers("원인은 디스크입니다. 원하시면 스크립트를 고쳐 드리겠습니다.") == (False, True)
    assert ko_lint.reply_fillers("그래프를 알려주시면 원인을 더 좁혀 드리겠습니다.") == (False, True)
    # "드리다" 없이 제안하는 맺음말도 센다
    assert ko_lint.reply_fillers("클라이언트를 알려 주시면 해당 코드에 맞춰 수정안을 쓰겠습니다.") == (False, True)
    assert ko_lint.reply_fillers("설정 파일을 보여 주시면 다시 정리할게요.") == (False, True)
    assert ko_lint.reply_fillers("로그를 보내 주시면 원인을 더 좁혀 드릴 수 있습니다.") == (False, True)
    assert ko_lint.reply_fillers("설정을 올려 주시면 맞는지 보겠습니다.") == (False, True)
    assert ko_lint.reply_fillers("요청을 보내 주시면 서버가 응답합니다.") == (False, False)
    # 동사와 상관없이 "주시면 … 겠습니다"와, 두 문장에 나눈 "알려 주세요. … 겠습니다"도 센다
    assert ko_lint.reply_fillers("다음 정보를 주시면 대괄호를 채워 다시 쓰겠습니다.") == (False, True)
    assert ko_lint.reply_fillers("원인을 찾았다면 결과를 알려 주세요. 그에 맞춰 다음 단계를 안내하겠습니다.") == (False, True)
    assert ko_lint.reply_fillers("배포가 끝나면 결과를 알려 주세요.") == (False, False)
    assert ko_lint.reply_fillers("필요하면 다시 실행하세요. 로그는 남습니다.") == (False, False)
    assert ko_lint.reply_fillers("빌드가 실패한 이유는 디스크입니다.") == (False, False)


def test_reply_checks_take_linear_time_on_long_blank_runs():
    start = time.time()
    assert ko_lint.reply_fillers(" " * 10_000 + "답입니다.") == (False, False)
    assert ko_lint.reply_fillers(" " * 10_000 + "좋은 질문입니다.") == (True, False)
    assert ko_lint.reply_fillers("가" * 30_000 + "주시면 답입니다.") == (False, False)
    ko_lint.reader_check("답입니다.\n" + " " * 30_000 + "x")
    elapsed = time.time() - start
    assert elapsed < 0.5, elapsed


def test_reply_checks_take_linear_time_on_many_blank_lines():
    start = time.time()
    counts = ko_lint.reader_check("답입니다." + "\n" * 20_000 + "끝입니다.")["counts"]
    elapsed = time.time() - start
    assert counts["bullets"] == 0, counts
    assert elapsed < 0.5, elapsed


def test_reply_checks_are_unchanged():
    assert ko_lint.reply_fillers("  \n  좋은 질문입니다! 답입니다.") == (True, False)
    assert ko_lint.reply_fillers("— 물론입니다.") == (True, False)
    counts = ko_lint.reader_check("답입니다.\n|---|:-:|\n  \n| a | b |\n")["counts"]
    assert (counts["sentences"], counts["bullets"], counts["headers"]) == (1, 0, 0), counts
    report = ko_lint.reader_check("답입니다.\n\n\n# 헤더\n\n- 하나\n  - 둘\n1. 셋\n-\n- 넷\n| a | b |\n")
    counts = report["counts"]
    assert (counts["sentences"], counts["headers"], counts["bullets"], report["eojeol"]) == (1, 1, 5, 10), report


def test_cli_rejects_type_invalid_config_without_traceback():
    with tempfile.TemporaryDirectory() as d:
        Path(d, ".simple-korean.json").write_text('{"terms": {"release": 5}}', encoding="utf-8")
        doc = Path(d, "a.md")
        doc.write_text("로그를 읽으세요.\n", encoding="utf-8")
        r = run_cli(str(doc))
        assert r.returncode != 0 and ".simple-korean.json" in r.stderr and "Traceback" not in r.stderr, r.stderr


def test_haera_document_with_anida_is_not_a_register_mix():
    text = "이 보고서는 해라체로 쓴다. 변화의 방향은 한쪽이 아니다. 결과는 표에 있다.\n"
    assert ko_lint.lint(text, config={})["violations"].get("register_mix", 0) == 0
    mixed = "이 보고서는 해라체로 쓴다. 결과는 표에 있습니다. 변화는 크다.\n"
    assert ko_lint.lint(mixed, config={})["violations"].get("register_mix", 0) == 1
