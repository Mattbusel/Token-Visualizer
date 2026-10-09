# Token Visualizer

[English](README.md) | 简体中文 | [日本語](README.ja.md) | [한국어](README.ko.md)

**看清 ChatGPT 这类 AI 模型如何把你的提示词切成 token、哪几行最费 token、哪些啰嗦的短语该删，并且省下的 token 是实测出来的，不是估的。**

适合所有写提示词、按 token 付费的人：开发者、提示词工程师，以及好奇一句话为什么"花"那么多钱的人。一个免费的终端 LLM token 计数器，离线使用 OpenAI 真正的分词器（GPT-4、GPT-4o、GPT-3.5）。

<p align="center"><a href="https://gitlab.com/mattbusel/Token-Visualizer/-/releases/permalink/latest/downloads/token-visualizer-windows-x86_64.exe"><b>下载 Windows 版 (.exe)</b></a> &nbsp;&middot;&nbsp; <a href="#install">Linux 和 macOS</a> &nbsp;&middot;&nbsp; <a href="https://token-visualizer-app.vercel.app/">项目网站</a> &nbsp;&middot;&nbsp; <a href="docs/REFERENCE.md">文档</a></p>

无需安装：在浏览器里试用 https://gpt-token-counter.vercel.app

<p align="center"><img src="assets/demo.gif" alt="真实的终端录屏：token-visualizer 用 GPT-4o 分词器分析一段 5 行的客服提示词，把每个 token 显示成一个彩色小块，并实测出按建议删减后从 70 个 token 降到 61 个。" width="900"></p>

<a id="install"></a>
## 安装

**Linux**（x86_64，Ubuntu 20.04+ / Debian 11+）。一行命令，无需任何依赖，安装到 `~/.local/bin`：

```sh
mkdir -p ~/.local/bin && curl -fsSL https://gitlab.com/mattbusel/Token-Visualizer/-/releases/permalink/latest/downloads/token-visualizer-linux-x86_64.tar.gz | tar xz --strip-components=1 -C ~/.local/bin --wildcards '*/token-visualizer'
```

| 其他系统 | |
|---|---|
| **Windows** | [下载 token-visualizer-windows-x86_64.exe](https://gitlab.com/mattbusel/Token-Visualizer/-/releases/permalink/latest/downloads/token-visualizer-windows-x86_64.exe) 后直接运行。（程序未签名，SmartScreen 可能会弹出提示：先点 *更多信息*，再点 *仍要运行*。） |
| **macOS，或从源码安装** | `pipx install git+https://gitlab.com/mattbusel/Token-Visualizer.git`（Python 3.8+） |

下载的都是单个文件，内置了分词器数据，所以可以离线使用。所有版本及其 SHA-256 校验和：[Releases](https://gitlab.com/mattbusel/Token-Visualizer/-/releases)。

**在 GitLab CI 中**：用 [`prompt-diet`](https://gitlab.com/explore/catalog/mattbusel/llm-ci) CI/CD 组件，在每次流水线中报告每个提示词文件里的啰嗦短语，并附上实测节省的 token 数。

## 工作原理

<img src="assets/how-it-works.svg" width="100%" alt="动画示意图，来自用 GPT-4o 分词器对 examples/support-prompt.txt 的一次真实运行。第 1 步：第 2 行被切成 16 个带编号的 token，比如 In、order、to、help。第 2 步：各行的 token 数为 12、16、17、18 和 7，共 70 个 token，357 个字符，估算费用 $0.0021。第 3 步：'In order to' 变成 'To'，'Due to the fact that' 变成 'Because'，'In the event that' 变成 'If'，重新分词后提示词从 70 个 token 降到 61 个，缩短 13%。">

1. **切分**：模型自己的分词器（`tiktoken`）把每一行切成 token，也就是模型读取并据此计费的一个个带编号的片段。
2. **计数**：每一行都会得到一个 token 数，并标成绿色、黄色或红色；整个提示词会得到总数和大致费用。
3. **实测**：把啰嗦的短语换成简短的说法，压缩多余的空白，再用同一个分词器重新处理新文本，报告真实的差值。

## 示例

以下全部是 `token-visualizer` 0.3.1 今天的真实输出。

**1. 一段 5 行的客服提示词**（[`examples/support-prompt.txt`](examples/support-prompt.txt)），报告的结尾部分：

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

**2. 通过管道传入一句啰嗦的话**：

```console
$ echo "In order to help you, due to the fact that you asked." | token-visualizer
  Total tokens: 14
  ...
  Applying the phrase and whitespace fixes: 14 → 8 tokens (-6, 43%)
```

**3. 精确的 token 边界**：在终端里每个 token 是一个彩色小块（见上面的 GIF）；关闭颜色后会得到一个带索引的网格：

```console
$ echo "In order to help you, due to the fact that you asked." | token-visualizer --no-color
TOKEN BREAKDOWN:
  [0:In] [1: order] [2: to] [3: help] [4: you] [5:,] [6: due] [7: to] [8: the]
  [9: fact] [10: that] [11: you] [12: asked] [13:.\n]
```

大多数 token 都带着单词前面的空格，所以 ` order` 和 `order` 是两个不同的 token。

## 在 CI 中使用

当提示词超出 token 预算时让任务失败，或者输出 JSON 供脚本使用。退出码：0 正常，1 没有输入或文件无法读取，2 参数错误，3 超出预算。

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

`--top N` 和 `--threshold N` 会把各行按 token 数从多到少排序，分别保留前 N 行，或保留超过 N 个 token 的行。JSON 里还会列出每个啰嗦短语以及实测能省下的 token 数。

**取代 tokenviz**：[tokenviz](https://gitlab.com/mattbusel/tokenviz) 的所有功能（`--budget`、`--json`、`--top`、`--threshold`）现在都在这里了，请改用这个工具。tokenviz 仍然可以继续使用。

## 3 步上手

1. **获取**：用上面的 Linux 一行命令或 Windows .exe，或者用 `pipx`。
2. **对你的提示词运行**：`token-visualizer prompt.txt -m gpt-4o`（也可以双击 .exe 后粘贴，再按 Ctrl+Z 和 Enter）。
3. **删掉它标出的内容**，再运行一次看看新的 token 数。

`token-visualizer --help` 会列出所有选项并附带示例。

## 文档

| 文档 | 内容 |
| --- | --- |
| [参考手册](docs/REFERENCE.md) | 所有选项、它检查什么、安装细节、Hugging Face 分词器、在 Python 中调用、局限性 |
| [Token-Visualizer 还是 tokenviz？](docs/REFERENCE.md#token-visualizer-or-tokenviz) | 为什么用它取代 tokenviz，以及对应的命令 |
| [更新日志](CHANGELOG.md) | 每个版本的改动 |

Anthropic 没有公开 Claude 的分词器，所以 `-m claude-3-sonnet` 会退回到按空白切分，并在报告开头注明这一点。对于 Llama 和其他开源模型，传入一个 Hugging Face 模型 ID 即可（需从源码安装，并装有 `transformers`）。[详情](docs/REFERENCE.md#limitations)。

## 许可证

MIT，见 [LICENSE](LICENSE)。
