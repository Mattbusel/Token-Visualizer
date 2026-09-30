"""Tests for token_visualizer. The first run downloads tiktoken's GPT-4 encoding."""
import token_visualizer as tv


def test_tiktoken_counts():
    stats = tv.TokenVisualizer("gpt-4").tokenize("hello world\nsecond line")
    assert stats.token_count == 5
    assert [n for _, n in stats.line_stats] == [2, 2]
    assert stats.char_count == len("hello world\nsecond line")


def test_special_token_text_is_counted():
    assert tv.TokenVisualizer("gpt-4").tokenize("<|endoftext|>").token_count > 0


def test_cli_file_mode(tmp_path, capsys):
    path = tmp_path / "p.txt"
    path.write_text("In order to help you, due to the fact that you asked.\n", encoding="utf-8")
    assert tv.main([str(path), "--model", "gpt-4", "--no-color"]) == 0
    out = capsys.readouterr().out
    assert "TOKEN ANALYSIS - GPT-4" in out
    assert "in order to" in out
    assert "→ 'to'" in out


def test_cli_missing_file(capsys):
    assert tv.main(["definitely-missing.txt"]) == 1
    assert "File not found" in capsys.readouterr().out


def test_version(capsys):
    try:
        tv.main(["--version"])
    except SystemExit as exc:
        assert exc.code == 0
    assert tv.__version__ in capsys.readouterr().out


def test_measured_savings_are_real(tmp_path, capsys):
    text = "In order to help you, due to the fact that you asked.\n"
    viz = tv.TokenVisualizer("gpt-4")
    compressed = viz.compress(text)
    assert compressed == "To help you, because you asked.\n"
    before, after = viz.tokenize(text).token_count, viz.tokenize(compressed).token_count
    path = tmp_path / "p.txt"
    path.write_text(text, encoding="utf-8")
    assert tv.main([str(path), "--no-color"]) == 0
    out = capsys.readouterr().out
    assert f"{before} → {after} tokens" in out


def test_force_color_shows_token_chips(tmp_path, capsys, monkeypatch):
    monkeypatch.setenv("FORCE_COLOR", "1")
    monkeypatch.delenv("NO_COLOR", raising=False)
    path = tmp_path / "p.txt"
    path.write_text("hello world", encoding="utf-8")
    assert tv.main([str(path)]) == 0
    out = capsys.readouterr().out
    assert "TOKEN BOUNDARIES" in out
    assert "\033[48;5;24mhello\033[0m" in out


def test_file_in_a_terminal_does_not_ask_for_a_tokenizer(tmp_path, capsys, monkeypatch):
    class TTY:
        def isatty(self):
            return True

        def readline(self):
            raise AssertionError("asked for input")

    monkeypatch.setattr(tv.sys, "stdin", TTY())
    monkeypatch.setattr("builtins.input", lambda *a: (_ for _ in ()).throw(AssertionError("asked")))
    path = tmp_path / "p.txt"
    path.write_text("hello world", encoding="utf-8")
    assert tv.main([str(path), "--no-color"]) == 0
    assert "TOKEN ANALYSIS - GPT-4" in capsys.readouterr().out


# CI flags (absorbed from tokenviz): --budget, --json, --top, --threshold.
import json

import pytest

SAMPLE = ("In order to help you, due to the fact that you asked.\n"
          "short line\n"
          "\n"
          "In the event that it fails, retry.\n")


@pytest.fixture
def sample(tmp_path):
    path = tmp_path / "p.txt"
    path.write_text(SAMPLE, encoding="utf-8")
    return str(path)


def _total():
    return tv.TokenVisualizer("gpt-4").tokenize(SAMPLE).token_count


def test_budget_over_exits_3(sample, capsys):
    total = _total()
    assert tv.main([sample, "--no-color", "--budget", str(total - 1)]) == 3
    assert f"Over budget: {total} tokens > {total - 1} (exit code 3)" in capsys.readouterr().out


def test_budget_within_exits_0(sample, capsys):
    total = _total()
    assert tv.main([sample, "--no-color", "--budget", str(total)]) == 0
    assert f"Within budget: {total} of {total} tokens" in capsys.readouterr().out


def test_json_report(sample, capsys):
    assert tv.main([sample, "--json"]) == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    viz = tv.TokenVisualizer("gpt-4")
    assert data["model"] == "gpt-4"
    assert data["encoding"] == "cl100k_base"
    assert data["total_tokens"] == _total()
    assert data["lines_total"] == 3
    assert data["budget"] is None and data["over_budget"] is False
    assert [entry["line"] for entry in data["lines"]] == [1, 4, 2]  # heaviest first, blank skipped
    tokens = [entry["tokens"] for entry in data["lines"]]
    assert tokens == sorted(tokens, reverse=True)
    phrases = {p["phrase"]: p for p in data["suggestions"]["phrases"]}
    assert set(phrases) == {"in order to", "due to the fact that", "in the event that"}
    swapped = SAMPLE.replace("due to the fact that", "because")
    assert phrases["due to the fact that"]["tokens_saved"] == _total() - viz.tokenize(swapped).token_count
    savings = data["suggestions"]["savings"]
    assert savings["tokens_after"] == viz.tokenize(viz.compress(SAMPLE)).token_count
    assert savings["tokens_saved"] == savings["tokens_before"] - savings["tokens_after"] > 0
    assert "\033[" not in captured.out


def test_json_over_budget_exits_3(sample, capsys):
    assert tv.main([sample, "--json", "--budget", "5"]) == 3
    data = json.loads(capsys.readouterr().out)
    assert data["budget"] == 5 and data["over_budget"] is True


def test_json_errors_go_to_stderr(capsys):
    assert tv.main(["definitely-missing.txt", "--json"]) == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "File not found" in captured.err


def test_top_ranks_heaviest_lines(sample, capsys):
    assert tv.main([sample, "--no-color", "--top", "1"]) == 0
    out = capsys.readouterr().out
    assert "HEAVIEST LINES  top 1; 1 of 3 lines" in out
    assert "LINE BREAKDOWN" not in out
    assert "Line  1:" in out and "Line  4:" not in out and "Line  2:" not in out


def test_threshold_filters_lines(sample, capsys):
    counts = {i: n for i, (_, n) in enumerate(tv.TokenVisualizer("gpt-4").tokenize(SAMPLE).line_stats, 1)}
    assert tv.main([sample, "--json", "--threshold", str(counts[2])]) == 0
    lines = [entry["line"] for entry in json.loads(capsys.readouterr().out)["lines"]]
    assert lines == [1, 4]
    assert tv.main([sample, "--no-color", "--threshold", "1000"]) == 0
    assert "No lines match." in capsys.readouterr().out


def test_top_and_threshold_together(sample, capsys):
    assert tv.main([sample, "--json", "--top", "1", "--threshold", "0"]) == 0
    assert [e["line"] for e in json.loads(capsys.readouterr().out)["lines"]] == [1]


@pytest.mark.parametrize("flag,value", [("--budget", "0"), ("--top", "0"),
                                        ("--threshold", "-1"), ("--budget", "lots")])
def test_bad_option_exits_2(sample, flag, value):
    with pytest.raises(SystemExit) as exc:
        tv.main([sample, flag, value])
    assert exc.value.code == 2


def test_unreadable_file_exits_1(tmp_path, capsys):
    path = tmp_path / "bad.txt"
    path.write_bytes(b"\xff\xfe\xff not utf-8")
    assert tv.main([str(path)]) == 1
    assert "Could not read" in capsys.readouterr().out


def test_empty_input_exits_1(monkeypatch, capsys):
    import io
    monkeypatch.setattr(tv.sys, "stdin", io.StringIO("   \n"))
    assert tv.main(["--json"]) == 1


def test_default_output_has_no_ci_sections(sample, capsys):
    assert tv.main([sample, "--no-color"]) == 0
    out = capsys.readouterr().out
    assert "LINE BREAKDOWN" in out
    assert "HEAVIEST LINES" not in out and "budget" not in out.lower()
