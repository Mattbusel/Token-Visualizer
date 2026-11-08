# Token Visualizer

English | [简体中文](README.zh-CN.md) | [日本語](README.ja.md) | [한국어](README.ko.md)

Free token counter. Shows what to cut from your prompt.

Cut a support prompt from 70 to 61 tokens.

- Counts tokens with OpenAI's real tokenizers
- Shows which lines cost the most
- Measures the savings, not a guess
- Fails CI when a prompt goes over budget

## Install

```sh
pipx install git+https://gitlab.com/mattbusel/Token-Visualizer.git
```

## Use

```console
$ echo "In order to help you, due to the fact that you asked." | token-visualizer
  Total tokens: 14
  ...
  Applying the phrase and whitespace fixes: 14 → 8 tokens (-6, 43%)
```

[Windows .exe](https://gitlab.com/mattbusel/Token-Visualizer/-/releases/permalink/latest/downloads/token-visualizer-windows-x86_64.exe) · [Browser version](https://gpt-token-counter.vercel.app) · [Project site](https://token-visualizer-app.vercel.app/) · [Reference](docs/REFERENCE.md)

More: [docs/DETAILS.md](docs/DETAILS.md)

License: MIT
