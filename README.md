# Token Visualizer

English | [简体中文](README.zh-CN.md) | [日本語](README.ja.md) | [한국어](README.ko.md)

**Shows how a model like ChatGPT cuts your prompt into tokens. Shows which lines cost the most and which wordy phrases to cut. Savings are measured, not guessed.**

A free LLM token counter for the terminal. Uses OpenAI's real tokenizers (GPT-4, GPT-4o, GPT-3.5), offline.

<p align="center"><a href="https://gitlab.com/mattbusel/Token-Visualizer/-/releases/permalink/latest/downloads/token-visualizer-windows-x86_64.exe"><b>Download for Windows (.exe)</b></a> &nbsp;&middot;&nbsp; <a href="#install">Linux and macOS</a> &nbsp;&middot;&nbsp; <a href="https://token-visualizer-app.vercel.app/">Project site</a> &nbsp;&middot;&nbsp; <a href="docs/REFERENCE.md">Docs</a></p>

No install: try it in the browser at https://gpt-token-counter.vercel.app

<p align="center"><img src="assets/demo.gif" alt="A real terminal session: token-visualizer analyzes a 5-line support prompt with the GPT-4o tokenizer, shows each token as a colored chip, and measures 70 to 61 tokens after the suggested cuts." width="900"></p>

## No install? Use the browser version

The free [token counter for GPT, Claude and Gemini](https://tensorust.com/tools/token-counter/?utm_source=github&utm_medium=readme&utm_campaign=token-visualizer) runs in your browser. Nothing to download. To turn token counts into dollars, use the [LLM API cost calculator](https://tensorust.com/tools/llm-api-cost/?utm_source=github&utm_medium=readme&utm_campaign=token-visualizer).

## Install

**Linux** (x86_64, Ubuntu 20.04+ / Debian 11+). One line, no dependencies, installs to `~/.local/bin`:

```sh
mkdir -p ~/.local/bin && curl -fsSL https://gitlab.com/mattbusel/Token-Visualizer/-/releases/permalink/latest/downloads/token-visualizer-linux-x86_64.tar.gz | tar xz --strip-components=1 -C ~/.local/bin --wildcards '*/token-visualizer'
```

| Other systems | |
|---|---|
| **Windows** | [Download token-visualizer-windows-x86_64.exe](https://gitlab.com/mattbusel/Token-Visualizer/-/releases/permalink/latest/downloads/token-visualizer-windows-x86_64.exe) and run it. (Unsigned, so SmartScreen may ask: *More info*, then *Run anyway*.) |
| **macOS, or from source** | `pipx install git+https://gitlab.com/mattbusel/Token-Visualizer.git` (Python 3.8+) |

Each download is one file with the tokenizer data built in. Works offline. All releases, with SHA-256 checksums: [Releases](https://gitlab.com/mattbusel/Token-Visualizer/-/releases).

**In GitLab CI:** the [`prompt-diet`](https://gitlab.com/explore/catalog/mattbusel/llm-ci) component reports the wordy phrases in every prompt file, with the measured token saving, on each pipeline.

## How it works

<img src="assets/how-it-works.svg" width="100%" alt="Animated diagram from a real run on examples/support-prompt.txt with the GPT-4o tokenizer. Step 1: line 2 is cut into 16 numbered tokens, like In, order, to, help. Step 2: line counts 12, 16, 17, 18 and 7, total 70 tokens, 357 characters, estimated $0.0021. Step 3: 'In order to' becomes 'To', 'Due to the fact that' becomes 'Because', 'In the event that' becomes 'If', and re-tokenizing takes the prompt from 70 to 61 tokens, 13 percent shorter.">

1. **Cut.** The model's own tokenizer (`tiktoken`) splits each line into tokens. Tokens are the pieces a model reads and bills for.
2. **Count.** Each line gets a token count, colored green, yellow or red. The prompt gets a total and a rough cost.
3. **Measure.** It swaps wordy phrases for short ones, removes extra whitespace, runs the new text through the same tokenizer, and reports the real difference.

## Examples

All real output from `token-visualizer` 0.3.1.

**1. A 5-line support prompt** ([`examples/support-prompt.txt`](examples/support-prompt.txt)), the end of the report:

```console
$ token-visualizer examples/support-prompt.txt -m gpt-4o
TOKEN ANALYSIS - GPT-4O  tiktoken o200k_base
  Total tokens: 70
  Total characters: 357
  ...
COMPRESSION SUGGESTIONS
  Verbose phrases found:
     'in order to' → 'to'
     'due to the fact that' → 'because'
     'in the event that' → 'if'

MEASURED SAVINGS
  Applying the phrase and whitespace fixes: 70 → 61 tokens (-9, 13%)
  Re-tokenized with the same tokenizer; $0.0003 less per request at $0.03 per 1K.
```

**2. One wordy sentence, piped in:**

```console
$ echo "In order to help you, due to the fact that you asked." | token-visualizer
  Total tokens: 14
  ...
  Applying the phrase and whitespace fixes: 14 → 8 tokens (-6, 43%)
```

**3. Exact token boundaries.** In a terminal each token is a colored chip (the GIF above). With colors off you get a numbered grid:

```console
$ echo "In order to help you, due to the fact that you asked." | token-visualizer --no-color
TOKEN BREAKDOWN:
  [0:In] [1: order] [2: to] [3: help] [4: you] [5:,] [6: due] [7: to] [8: the]
  [9: fact] [10: that] [11: you] [12: asked] [13:.\n]
```

Most tokens include the space before the word. That is why ` order` and `order` are different tokens.

## Use in CI

Fail a job when a prompt goes over a token budget, or get JSON for a script. Exit codes: 0 ok, 1 no input or unreadable file, 2 bad option, 3 over budget.

```console
$ token-visualizer examples/support-prompt.txt -m gpt-4o --budget 60
  ...
Over budget: 70 tokens > 60 (exit code 3)
$ echo $?
3
$ token-visualizer examples/support-prompt.txt -m gpt-4o --json --top 1
{
  "model": "gpt-4o",
  "encoding": "o200k_base",
  "total_tokens": 70,
  ...
  "lines": [
    {
      "line": 4,
      "tokens": 18,
      "text": "In the event that the customer is upset, stay calm and apologize once, not repeatedly."
    }
  ],
  ...
}
```

`--top N` keeps the N heaviest lines. `--threshold N` keeps lines over N tokens. The JSON also lists each wordy phrase with its measured token saving.

**Replaces tokenviz.** Everything [tokenviz](https://gitlab.com/mattbusel/tokenviz) did (`--budget`, `--json`, `--top`, `--threshold`) is here now. Use this one. tokenviz still works.

## Use it in 3 steps

1. **Get it:** use the Linux one-liner or the Windows .exe above, or `pipx`.
2. **Run it on your prompt:** `token-visualizer prompt.txt -m gpt-4o`. Or double-click the .exe, paste, then Ctrl+Z and Enter.
3. **Cut what it flags** and run it again to see the new count.

`token-visualizer --help` lists every option with examples.

## Documentation

| Doc | What is in it |
| --- | --- |
| [Reference](docs/REFERENCE.md) | All options, what it checks, install details, Hugging Face tokenizers, use from Python, limitations |
| [Token-Visualizer or tokenviz?](docs/REFERENCE.md#token-visualizer-or-tokenviz) | Why tokenviz is replaced, and its equivalent commands |
| [Changelog](CHANGELOG.md) | What changed in each release |

Anthropic publishes no Claude tokenizer. So `-m claude-3-sonnet` falls back to splitting on whitespace, and the header says so. For Llama and other open models, pass a Hugging Face model ID (from source, with `transformers`). [Details](docs/REFERENCE.md#limitations).

## License

MIT, see [LICENSE](LICENSE).
