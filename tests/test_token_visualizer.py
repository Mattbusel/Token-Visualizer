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
