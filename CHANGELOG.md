# Changelog

## [0.3.1] - 2026-09-28

- Releases also carry versionless files, including the bare `token-visualizer-windows-x86_64.exe`, so `releases/latest/download/...` links always point at the newest build. The versioned archives the install scripts and winget use are unchanged.
- README shortened to one screen: a direct Windows download, an animated how-it-works diagram from a real run, three real examples and three steps. Options, install details, Python use, the tokenviz comparison and limitations moved to `docs/REFERENCE.md`.
- A project site at https://mattbusel.github.io/Token-Visualizer/ (in `docs/`).

## [0.3.0] - 2026-09-25

- Token boundaries are shown as colored chips, one background color per token, instead of an indexed grid (the grid is still used when colors are off).
- The flat "10% savings" guess is gone. The tool now applies its own phrase swaps and whitespace fixes, tokenizes the result again and reports the measured difference (`70 → 61 tokens`).
- A file argument no longer stops to ask for a tokenizer; only pasted text gets the menu, which now also accepts a typed model name.
- The report header names the tokenizer really used (for example `tiktoken o200k_base`, or a whitespace-split fallback).
- `FORCE_COLOR` keeps colors on in a pipe; warnings go to stderr and say how to fix the problem; `--help` has examples; emoji removed from the output.
- Install with Homebrew, Scoop, or the new one-line `install.sh` / `install.ps1` scripts (they verify SHA-256).
- An example prompt in `examples/`, and a README that says which of Token-Visualizer and tokenviz to use for what.

## [0.2.0] - 2026-09-25

- Prebuilt single-file executables (`token-visualizer`) for Windows, macOS (Apple Silicon and Intel) and Linux on every GitHub Release. The GPT tokenizers are built in, so they work offline. Double-click it on Windows to paste a prompt; the window waits for Enter before closing.
- Command line flags: `--model/-m` (skips the tokenizer menu), `--no-color`, `--version`, `--help`. Piped input no longer stops to ask for a tokenizer.
- The code moved to `token_visualizer.py` so it can be imported normally and installed with `pipx install git+https://github.com/Mattbusel/Token-Visualizer`. `python "Token Visualizer.py"` still works.
- `gpt-4o` added to the tokenizer menu.
- Text containing special tokens such as `<|endoftext|>` is counted instead of crashing.
- `transformers` is only imported when a Hugging Face tokenizer is picked, which removes a slow import and a warning on every run.
- Emoji and colors work in Windows consoles and pipes.
- A real test suite, and CI that fails when it fails (it used to swallow every error).

## 0.1.0

- The original single-file script.
