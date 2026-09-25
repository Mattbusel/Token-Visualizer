# Changelog

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
