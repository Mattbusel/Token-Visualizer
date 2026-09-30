# Token Visualizer reference

[README](../README.md) · [Reference](REFERENCE.md) · [Project site](https://token-visualizer-app.vercel.app/)

## All options

```text
usage: token-visualizer [-h] [-m MODEL] [-t N] [--threshold N] [-b N] [--json]
                        [--no-color] [--version]
                        [file]

positional arguments:
  file                  text file to analyze (default: read stdin)

options:
  -h, --help            show this help message and exit
  -m MODEL, --model MODEL
                        tokenizer to use: gpt-4, gpt-4o, gpt-3.5-turbo,
                        claude-3-sonnet, llama-2-7b, any tiktoken model name,
                        or a Hugging Face model ID. Default gpt-4; only pasted
                        text gets a menu.
  -t N, --top N         rank lines heaviest first and show only the top N
  --threshold N         rank lines heaviest first and show only those over N
                        tokens
  -b N, --budget N      exit with code 3 if the whole input is over N tokens
                        (for CI and scripts)
  --json                print machine-readable JSON instead of the report
  --no-color            disable ANSI colors
  --version             show program's version number and exit
```

Exit codes: 0 ok, 1 no input or unreadable file, 2 bad option, 3 over `--budget`. With `--json`, stdout carries only the JSON (model, encoding, total_tokens, lines, budget, over_budget, and the suggestions with measured savings); messages go to stderr.

Colors turn off when output is not a terminal, with `--no-color`, or when `NO_COLOR` is set; `FORCE_COLOR=1` keeps them on in a pipe. The tokenizer menu only appears for pasted text; a file argument or a pipe uses `gpt-4` unless `-m` says otherwise, so scripts never hang.

## What it checks

- **Token counts** with `tiktoken` for GPT model names (unknown GPT names fall back to `cl100k_base`), or a Hugging Face `AutoTokenizer` for any other model ID when `transformers` is installed. The header says which tokenizer was really used.
- **Line breakdown**: each line's tokens and characters per token. Lines over 50 tokens are listed again as expensive.
- **Token boundaries**: in a terminal, each token on its own colored background with `↵` for newlines; without colors, an indexed grid like `[0:You] [1: are]`.
- **Suggestions**: repeated words, five wordy phrases (`in order to`, `due to the fact that`, `at this point in time`, `for the purpose of`, `in the event that`), low characters per token, lines over 40 tokens, and extra whitespace.
- **Cost**: a rough figure at a fixed $0.03 per 1K input tokens (an old GPT-4 list price), clearly labeled as such.

The measured savings are not a guess: the tool applies its own phrase swaps and whitespace fixes to your text and tokenizes the result again with the same tokenizer.

## Install details

| Platform | Command |
| --- | --- |
| Windows (download) | [token-visualizer-windows-x86_64.exe](https://gitlab.com/mattbusel/Token-Visualizer/-/releases/permalink/latest/downloads/token-visualizer-windows-x86_64.exe) |
| macOS / Linux (Homebrew) | `brew install mattbusel/tap/token-visualizer` |
| Windows (Scoop) | `scoop bucket add mattbusel https://gitlab.com/mattbusel/scoop-bucket; scoop install mattbusel/token-visualizer` |
| macOS / Linux (script) | `curl -fsSL https://gitlab.com/mattbusel/Token-Visualizer/-/raw/main/install.sh \| sh` |
| Windows (PowerShell script) | `irm https://gitlab.com/mattbusel/Token-Visualizer/-/raw/main/install.ps1 \| iex` |
| Any OS with Python 3.8+ | `pipx install git+https://gitlab.com/mattbusel/Token-Visualizer` |
| Manual download | [Latest release](https://gitlab.com/mattbusel/Token-Visualizer/-/releases): Windows .exe and zip, macOS (Apple Silicon or Intel) and Linux tarballs |

The downloads are single files with the GPT tokenizers built in, so they work offline. The two scripts check the SHA-256 against the release's `SHA256SUMS.txt` before installing: `install.sh` puts `token-visualizer` in `~/.local/bin`, `install.ps1` puts `token-visualizer.exe` in `%LOCALAPPDATA%\Programs\token-visualizer` and adds it to your user PATH. Hugging Face tokenizers are not in the downloads; for those use pipx or source with `transformers` (below).

**Unsigned binary warnings.** Windows SmartScreen may say "unknown publisher": click **More info**, then **Run anyway**. On macOS, if a manually downloaded binary is blocked, right-click it and choose **Open** the first time, or run `xattr -d com.apple.quarantine token-visualizer`. Homebrew, Scoop and the install scripts do not trigger this.

## From source, Hugging Face tokenizers, and use from Python

Python 3.8+. `tiktoken` is required for real GPT counts; `transformers` is optional.

```bash
git clone https://gitlab.com/mattbusel/Token-Visualizer
cd Token-Visualizer
pip install -e ".[hf,dev]"      # or: pip install tiktoken
pytest
python token_visualizer.py examples/support-prompt.txt -m bert-base-uncased    # a Hugging Face model ID
```

The old `python "Token Visualizer.py"` command still works.

```python
import token_visualizer as tv

viz = tv.TokenVisualizer("gpt-4o")
stats = viz.tokenize("Your prompt here")
print(stats.token_count, stats.efficiency)
print(viz.compress("In order to help you, due to the fact that you asked."))
# To help you, because you asked.
viz.visualize_tokens("Your prompt here")
viz.suggest_compression("Your prompt here")
```

## Token-Visualizer or tokenviz?

Token-Visualizer now does everything its sibling [tokenviz](https://gitlab.com/mattbusel/tokenviz) did, so use this one. tokenviz keeps working for existing scripts and CI jobs.

| tokenviz | Token-Visualizer |
| --- | --- |
| `tokenviz -f prompt.txt --top 5` | `token-visualizer prompt.txt --top 5` |
| `tokenviz -f prompt.txt --threshold 20` | `token-visualizer prompt.txt --threshold 20` |
| `tokenviz -f prompt.txt --budget 2000` | `token-visualizer prompt.txt --budget 2000` (same exit code 3) |
| `tokenviz -f prompt.txt --json` | `token-visualizer prompt.txt --json` |
| `tokenviz "some text"` | `echo "some text" \| token-visualizer` |

## Limitations

- Anthropic does not publish a Claude tokenizer, and `claude-3-sonnet` and `llama-2-7b` in the menu are not Hugging Face model IDs, so those two fall back to whitespace splitting (the header says so). For real counts outside OpenAI models, pass a valid Hugging Face model ID with `-m`.
- With no tokenizer library at all, everything uses whitespace splitting, which undercounts real tokens.
- The cost figure uses a fixed historical price and is only a rough guide.
