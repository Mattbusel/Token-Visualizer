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
