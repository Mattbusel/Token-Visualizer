# Token Visualizer

[English](README.md) | [简体中文](README.zh-CN.md) | 日本語 | [한국어](README.ko.md)

**ChatGPT のような AI モデルがプロンプトをどうトークンに分割するのか、どの行がいちばんトークンを食っているのか、どの冗長な言い回しを削ればいいのかがわかります。節約できる量は推測ではなく実測です。**

プロンプトを書いてトークン単位で料金を払っているすべての人に：開発者、プロンプトエンジニア、そして 1 文の「値段」がなぜそうなるのか気になる人。OpenAI の本物のトークナイザー（GPT-4、GPT-4o、GPT-3.5）をオフラインで使う、ターミナル用の無料 LLM トークンカウンターです。

<p align="center"><a href="https://gitlab.com/mattbusel/Token-Visualizer/-/releases/permalink/latest/downloads/token-visualizer-windows-x86_64.exe"><b>Windows 版をダウンロード (.exe)</b></a> &nbsp;&middot;&nbsp; <a href="#install">Linux と macOS</a> &nbsp;&middot;&nbsp; <a href="https://token-visualizer-app.vercel.app/">プロジェクトサイト</a> &nbsp;&middot;&nbsp; <a href="docs/REFERENCE.md">ドキュメント</a></p>

インストール不要：ブラウザで試すなら https://gpt-token-counter.vercel.app

<p align="center"><img src="assets/demo.gif" alt="実際のターミナルセッション：token-visualizer が 5 行のサポート用プロンプトを GPT-4o のトークナイザーで分析し、各トークンを色付きのチップで表示して、提案どおりに削ると 70 トークンから 61 トークンになることを実測する。" width="900"></p>

<a id="install"></a>
## インストール

**Linux**（x86_64、Ubuntu 20.04+ / Debian 11+）。依存関係なしの 1 行で、`~/.local/bin` にインストールします。

```sh
mkdir -p ~/.local/bin && curl -fsSL https://gitlab.com/mattbusel/Token-Visualizer/-/releases/permalink/latest/downloads/token-visualizer-linux-x86_64.tar.gz | tar xz --strip-components=1 -C ~/.local/bin --wildcards '*/token-visualizer'
```

| その他の環境 | |
|---|---|
| **Windows** | [token-visualizer-windows-x86_64.exe をダウンロード](https://gitlab.com/mattbusel/Token-Visualizer/-/releases/permalink/latest/downloads/token-visualizer-windows-x86_64.exe)して実行するだけ。（署名なしのため SmartScreen が確認してくることがあります。*詳細情報* を押してから *実行* を押してください。） |
| **macOS、またはソースから** | `pipx install git+https://gitlab.com/mattbusel/Token-Visualizer.git`（Python 3.8+） |

ダウンロードできるのはトークナイザーのデータを内蔵した単一ファイルなので、オフラインで動きます。全リリースと SHA-256 チェックサム：[Releases](https://gitlab.com/mattbusel/Token-Visualizer/-/releases)。

**GitLab CI で使う**：[`prompt-diet`](https://gitlab.com/explore/catalog/mattbusel/llm-ci) CI/CD コンポーネントを使えば、パイプラインのたびに、すべてのプロンプトファイルの冗長な言い回しを、実測したトークン節約量とともにレポートできます。

## 仕組み

<img src="assets/how-it-works.svg" width="100%" alt="examples/support-prompt.txt を GPT-4o のトークナイザーで実際に処理したときのアニメーション図。ステップ 1：2 行目が In、order、to、help のような番号付きの 16 トークンに分割される。ステップ 2：各行のトークン数は 12、16、17、18、7 で、合計 70 トークン、357 文字、推定 $0.0021。ステップ 3：'In order to' が 'To' に、'Due to the fact that' が 'Because' に、'In the event that' が 'If' になり、トークン化し直すとプロンプトは 70 トークンから 61 トークンへと 13% 短くなる。">

1. **分割**：モデル自身のトークナイザー（`tiktoken`）が各行をトークンに分割します。トークンとは、モデルが読み込み、課金の単位にもなる番号付きのかけらです。
2. **カウント**：各行にトークン数が付き、緑、黄、赤で色分けされます。プロンプト全体には合計と大まかなコストが出ます。
3. **実測**：冗長な言い回しを短いものに置き換え、余分な空白を詰め、新しいテキストを同じトークナイザーに通して、実際の差をレポートします。

## 例

すべて `token-visualizer` 0.3.1 による今日の実際の出力です。

**1. 5 行のサポート用プロンプト**（[`examples/support-prompt.txt`](examples/support-prompt.txt)）、レポートの末尾：

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

**2. 冗長な 1 文をパイプで渡す**：

```console
$ echo "In order to help you, due to the fact that you asked." | token-visualizer
  Total tokens: 14
  ...
  Applying the phrase and whitespace fixes: 14 → 8 tokens (-6, 43%)
```

**3. 正確なトークン境界**：ターミナルでは各トークンが色付きのチップになります（上の GIF）。色をオフにすると、インデックス付きのグリッドになります。

```console
$ echo "In order to help you, due to the fact that you asked." | token-visualizer --no-color
TOKEN BREAKDOWN:
  [0:In] [1: order] [2: to] [3: help] [4: you] [5:,] [6: due] [7: to] [8: the]
  [9: fact] [10: that] [11: you] [12: asked] [13:.\n]
```

ほとんどのトークンは単語の前のスペースを含んでいます。だから ` order` と `order` は別のトークンです。

## CI で使う

プロンプトがトークン予算を超えたらジョブを失敗させたり、スクリプト用に JSON を出したりできます。終了コード：0 は正常、1 は入力なしまたはファイルが読めない、2 は不正なオプション、3 は予算超過。

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

`--top N` と `--threshold N` は、行をトークン数の多い順に並べ、上位 N 行、または N トークンを超える行だけを残します。JSON には、冗長な言い回しごとに実測した節約トークン数も載ります。

**tokenviz の後継**：[tokenviz](https://gitlab.com/mattbusel/tokenviz) でできたこと（`--budget`、`--json`、`--top`、`--threshold`）はすべてこちらに移ったので、こちらを使ってください。tokenviz も引き続き動きます。

## 3 ステップで使う

1. **入手する**：上の Linux 用ワンライナーか Windows 用 .exe、または `pipx` を使います。
2. **自分のプロンプトで実行する**：`token-visualizer prompt.txt -m gpt-4o`（または .exe をダブルクリックして貼り付け、Ctrl+Z を押して Enter）。
3. **指摘された部分を削り**、もう一度実行して新しいトークン数を確認します。

`token-visualizer --help` で、すべてのオプションを使用例付きで確認できます。

## ドキュメント

| ドキュメント | 内容 |
| --- | --- |
| [リファレンス](docs/REFERENCE.md) | すべてのオプション、チェックする内容、インストールの詳細、Hugging Face のトークナイザー、Python からの使い方、制限事項 |
| [Token-Visualizer と tokenviz のどちら？](docs/REFERENCE.md#token-visualizer-or-tokenviz) | tokenviz を置き換えた理由と、対応するコマンド |
| [変更履歴](CHANGELOG.md) | 各リリースでの変更点 |

Anthropic は Claude のトークナイザーを公開していないため、`-m claude-3-sonnet` は空白区切りの分割にフォールバックし、ヘッダーにもその旨が表示されます。Llama などのオープンなモデルでは、Hugging Face のモデル ID を渡してください（ソースからのインストールと `transformers` が必要）。[詳細](docs/REFERENCE.md#limitations)。

## ライセンス

MIT。[LICENSE](LICENSE) を参照してください。
