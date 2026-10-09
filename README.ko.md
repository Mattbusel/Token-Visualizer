# Token Visualizer

[English](README.md) | [简体中文](README.zh-CN.md) | [日本語](README.ja.md) | 한국어

**ChatGPT 같은 AI 모델이 프롬프트를 어떻게 토큰으로 쪼개는지, 어느 줄이 토큰을 가장 많이 먹는지, 어떤 장황한 표현을 줄여야 하는지 보여 줍니다. 절약량은 추측이 아니라 실측입니다.**

프롬프트를 쓰고 토큰 단위로 비용을 내는 모든 분을 위한 도구입니다: 개발자, 프롬프트 엔지니어, 그리고 문장 하나가 왜 그만큼 "비싼지" 궁금한 누구나. OpenAI의 실제 토크나이저(GPT-4, GPT-4o, GPT-3.5)를 오프라인으로 쓰는 터미널용 무료 LLM 토큰 계산기입니다.

<p align="center"><a href="https://gitlab.com/mattbusel/Token-Visualizer/-/releases/permalink/latest/downloads/token-visualizer-windows-x86_64.exe"><b>Windows용 다운로드 (.exe)</b></a> &nbsp;&middot;&nbsp; <a href="#install">Linux와 macOS</a> &nbsp;&middot;&nbsp; <a href="https://token-visualizer-app.vercel.app/">프로젝트 사이트</a> &nbsp;&middot;&nbsp; <a href="docs/REFERENCE.md">문서</a></p>

설치 없이 브라우저에서 써 보기: https://gpt-token-counter.vercel.app

<p align="center"><img src="assets/demo.gif" alt="실제 터미널 세션: token-visualizer가 5줄짜리 고객 지원 프롬프트를 GPT-4o 토크나이저로 분석해 각 토큰을 색깔 칩으로 보여 주고, 제안대로 줄였을 때 70토큰에서 61토큰이 되는 것을 실측한다." width="900"></p>

<a id="install"></a>
## 설치

**Linux**(x86_64, Ubuntu 20.04+ / Debian 11+). 의존성 없이 한 줄로 `~/.local/bin`에 설치합니다:

```sh
mkdir -p ~/.local/bin && curl -fsSL https://gitlab.com/mattbusel/Token-Visualizer/-/releases/permalink/latest/downloads/token-visualizer-linux-x86_64.tar.gz | tar xz --strip-components=1 -C ~/.local/bin --wildcards '*/token-visualizer'
```

| 다른 시스템 | |
|---|---|
| **Windows** | [token-visualizer-windows-x86_64.exe 다운로드](https://gitlab.com/mattbusel/Token-Visualizer/-/releases/permalink/latest/downloads/token-visualizer-windows-x86_64.exe) 후 실행하세요. (서명되지 않은 파일이라 SmartScreen이 물어볼 수 있습니다: *추가 정보*를 누른 다음 *실행*을 누르세요.) |
| **macOS 또는 소스에서 설치** | `pipx install git+https://gitlab.com/mattbusel/Token-Visualizer.git`(Python 3.8+) |

다운로드 파일은 토크나이저 데이터가 내장된 단일 파일이라 오프라인에서도 동작합니다. SHA-256 체크섬이 포함된 모든 릴리스: [Releases](https://gitlab.com/mattbusel/Token-Visualizer/-/releases).

**GitLab CI에서**: [`prompt-diet`](https://gitlab.com/explore/catalog/mattbusel/llm-ci) CI/CD 컴포넌트로 파이프라인마다 모든 프롬프트 파일의 장황한 표현을 실측한 토큰 절약량과 함께 리포트할 수 있습니다.

## 동작 원리

<img src="assets/how-it-works.svg" width="100%" alt="GPT-4o 토크나이저로 examples/support-prompt.txt를 실제로 처리한 애니메이션 다이어그램. 1단계: 2번째 줄이 In, order, to, help 같은 번호 붙은 토큰 16개로 쪼개진다. 2단계: 줄별 토큰 수는 12, 16, 17, 18, 7로 합계 70토큰, 357자, 예상 비용 $0.0021. 3단계: 'In order to'는 'To'로, 'Due to the fact that'은 'Because'로, 'In the event that'은 'If'로 바뀌고, 다시 토큰화하면 프롬프트가 70토큰에서 61토큰으로 13% 짧아진다.">

1. **쪼개기**: 모델 자체의 토크나이저(`tiktoken`)가 각 줄을 토큰으로 나눕니다. 토큰은 모델이 읽고 요금을 매기는 번호 붙은 조각입니다.
2. **세기**: 줄마다 토큰 수가 매겨지고 초록, 노랑, 빨강으로 표시되며, 프롬프트 전체에는 합계와 대략적인 비용이 나옵니다.
3. **실측하기**: 장황한 표현을 짧은 표현으로 바꾸고 불필요한 공백을 줄인 뒤, 새 텍스트를 같은 토크나이저에 다시 넣어 실제 차이를 리포트합니다.

## 예시

모두 `token-visualizer` 0.3.1로 오늘 뽑은 실제 출력입니다.

**1. 5줄짜리 고객 지원 프롬프트**([`examples/support-prompt.txt`](examples/support-prompt.txt)), 리포트의 끝부분:

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

**2. 장황한 문장 하나를 파이프로 넘기기**:

```console
$ echo "In order to help you, due to the fact that you asked." | token-visualizer
  Total tokens: 14
  ...
  Applying the phrase and whitespace fixes: 14 → 8 tokens (-6, 43%)
```

**3. 정확한 토큰 경계**: 터미널에서는 토큰마다 색깔 칩으로 표시되고(위의 GIF), 색을 끄면 인덱스가 붙은 격자로 나옵니다:

```console
$ echo "In order to help you, due to the fact that you asked." | token-visualizer --no-color
TOKEN BREAKDOWN:
  [0:In] [1: order] [2: to] [3: help] [4: you] [5:,] [6: due] [7: to] [8: the]
  [9: fact] [10: that] [11: you] [12: asked] [13:.\n]
```

대부분의 토큰은 단어 앞의 공백을 함께 담고 있습니다. 그래서 ` order`와 `order`는 서로 다른 토큰입니다.

## CI에서 사용하기

프롬프트가 토큰 예산을 넘으면 작업을 실패시키거나, 스크립트용 JSON을 받을 수 있습니다. 종료 코드: 0 정상, 1 입력 없음 또는 파일을 읽을 수 없음, 2 잘못된 옵션, 3 예산 초과.

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

`--top N`과 `--threshold N`은 줄을 토큰이 많은 순서로 정렬해 상위 N줄, 또는 N토큰을 넘는 줄만 남깁니다. JSON에는 장황한 표현마다 실측한 절약 토큰 수도 들어 있습니다.

**tokenviz를 대체합니다**: [tokenviz](https://gitlab.com/mattbusel/tokenviz)가 하던 모든 기능(`--budget`, `--json`, `--top`, `--threshold`)이 이제 여기에 있으니 이 도구를 쓰세요. tokenviz도 계속 동작합니다.

## 3단계로 사용하기

1. **받기**: 위의 Linux 한 줄 명령이나 Windows .exe, 또는 `pipx`를 쓰세요.
2. **내 프롬프트로 실행하기**: `token-visualizer prompt.txt -m gpt-4o`(또는 .exe를 더블클릭해서 붙여 넣은 뒤 Ctrl+Z와 Enter).
3. 표시된 부분을 **줄이고**, 다시 실행해서 새 토큰 수를 확인하세요.

`token-visualizer --help`로 모든 옵션을 예시와 함께 볼 수 있습니다.

## 문서

| 문서 | 내용 |
| --- | --- |
| [레퍼런스](docs/REFERENCE.md) | 모든 옵션, 무엇을 검사하는지, 설치 상세, Hugging Face 토크나이저, Python에서 사용하기, 한계 |
| [Token-Visualizer와 tokenviz 중 무엇을?](docs/REFERENCE.md#token-visualizer-or-tokenviz) | tokenviz를 대체한 이유와 대응하는 명령 |
| [변경 이력](CHANGELOG.md) | 릴리스별 변경 사항 |

Anthropic은 Claude 토크나이저를 공개하지 않으므로, `-m claude-3-sonnet`은 공백 기준 분할로 대체되며 헤더에 그렇게 표시됩니다. Llama 같은 오픈 모델은 Hugging Face 모델 ID를 넘기세요(소스에서 설치하고 `transformers`가 있어야 함). [자세히](docs/REFERENCE.md#limitations).

## 라이선스

MIT, [LICENSE](LICENSE)를 참고하세요.
