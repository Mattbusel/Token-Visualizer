# Token Visualizer

[![CI](https://github.com/Mattbusel/Token-Visualizer/actions/workflows/ci.yml/badge.svg)](https://github.com/Mattbusel/Token-Visualizer/actions/workflows/ci.yml)

A single-file Python script that shows how an LLM tokenizer splits your prompt, which lines cost the most tokens, and which wordy phrases you can cut.

Tokens are what you pay for and what fills the context window, but most prompt editing happens blind. Paste a prompt in or point the script at a file and you get a per-line token count, the exact token boundaries, and a short list of concrete edits.

## What it does

- **Token counts** using `tiktoken` for GPT models (falls back to `cl100k_base` for unknown GPT names) or a Hugging Face `AutoTokenizer` for other model names.
- **Line breakdown**: every line with its token count and characters per token, colored green (< 25 tokens), yellow (25 to 50) or red (> 50). Lines over 50 tokens are listed again as "expensive".
- **Token grid**: each token shown with its index and escapes visible, for texts up to 200 tokens.
- **Compression suggestions**: repeated words, verbose phrases with shorter replacements (`in order to` to `to`, `due to the fact that` to `because`, and a few more), low characters-per-token, long lines, and extra whitespace.
- **Rough cost estimate** at a fixed $0.03 per 1K input tokens (old GPT-4 list price), plus a flat 10% savings estimate.
- Colors switch off automatically when output is not a terminal.

## Quick start

Python 3.7+. Both tokenizer libraries are optional.

```bash
git clone https://github.com/Mattbusel/Token-Visualizer
cd Token-Visualizer
pip install tiktoken            # recommended, for GPT tokenization
pip install transformers        # optional, for Hugging Face tokenizers

# Analyze a file
python "Token Visualizer.py" prompt.txt

# Or paste text interactively, then Ctrl+D (Ctrl+Z then Enter on Windows)
python "Token Visualizer.py"
```

The script then asks which tokenizer to use: `gpt-4`, `gpt-3.5-turbo`, `claude-3-sonnet` or `llama-2-7b`.

### Using it from Python

The file name contains a space, so import it with `importlib`:

```python
import importlib.util
spec = importlib.util.spec_from_file_location("tv", "Token Visualizer.py")
tv = importlib.util.module_from_spec(spec); spec.loader.exec_module(tv)

viz = tv.TokenVisualizer("gpt-4")
stats = viz.tokenize("Your prompt here")
print(stats.token_count, stats.efficiency)
viz.visualize_tokens("Your prompt here")
viz.suggest_compression("Your prompt here")
```

## Example output

```
🔍 TOKEN ANALYSIS - GPT-4
📊 SUMMARY:
  Total tokens: 24
  Total characters: 113
  Efficiency: 4.71 chars/token
📝 LINE BREAKDOWN:
  Line  1:  21 tokens (4.5 c/t) In order to help you, due to the fact that you asked, I will...
  Line  2:   3 tokens (5.7 c/t) Second line here.
🎯 COMPRESSION SUGGESTIONS
✂️  Verbose phrases found:
   '\bin order to\b' → 'to'
   '\bdue to the fact that\b' → 'because'
```

## Limitations

- Anthropic does not publish a Claude tokenizer, and `claude-3-sonnet` and `llama-2-7b` are not Hugging Face model IDs, so those two choices fall back to whitespace splitting. For real counts outside OpenAI models, pass a valid Hugging Face model ID to `TokenVisualizer(...)` in code.
- With neither library installed, everything uses whitespace splitting, which undercounts real tokens.
- The cost figure uses a hardcoded historical price and is only a rough guide.
- There is no test suite; CI installs dependencies and runs pytest if tests exist.

## Related

[tokenviz](https://github.com/Mattbusel/tokenviz) is a sibling project by the same author: a packaged `click` CLI that ranks prompt lines by tiktoken count with `--top` and `--threshold` filters. This repo is the interactive script with tokenizer choice and compression suggestions.
