#!/usr/bin/env python3
"""
Token Visualizer - Analyze and optimize your prompts for LLM efficiency
Supports multiple tokenizers and provides compression suggestions
"""

import argparse
import importlib.util
import os
import re
import sys
from collections import Counter
from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional

__version__ = "0.2.0"

MODEL_OPTIONS = ["gpt-4", "gpt-4o", "gpt-3.5-turbo", "claude-3-sonnet", "llama-2-7b"]


def _use_bundled_encodings() -> None:
    """Point tiktoken at the encodings shipped inside the prebuilt executable.

    tiktoken normally downloads them on first use; the release binaries carry
    them so they work offline. A user-set TIKTOKEN_CACHE_DIR always wins.
    """
    base = getattr(sys, "_MEIPASS", None)
    if base and "TIKTOKEN_CACHE_DIR" not in os.environ:
        cache = os.path.join(base, "tiktoken_cache")
        if os.path.isdir(cache):
            os.environ["TIKTOKEN_CACHE_DIR"] = cache


_use_bundled_encodings()

try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False
    print("⚠️  tiktoken not installed. Install with: pip install tiktoken")

# transformers is optional and slow to import, so it is only loaded when a
# non-GPT tokenizer is actually requested.
TRANSFORMERS_AVAILABLE = importlib.util.find_spec("transformers") is not None

# ANSI color codes for terminal formatting
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
    
    @classmethod
    def disable(cls):
        """Disable colors for non-terminal output"""
        for attr in dir(cls):
            if not attr.startswith('_') and attr != 'disable':
                setattr(cls, attr, '')

@dataclass
class TokenStats:
    text: str
    tokens: List[str]
    token_count: int
    char_count: int
    efficiency: float  # chars per token
    line_stats: List[Tuple[str, int]]  # (line, token_count)

class TokenVisualizer:
    def __init__(self, model_name: str = "gpt-4"):
        self.model_name = model_name
        self.tokenizer = self._load_tokenizer()
        
    def _load_tokenizer(self):
        """Load the appropriate tokenizer"""
        if "gpt" in self.model_name.lower() and TIKTOKEN_AVAILABLE:
            try:
                return tiktoken.encoding_for_model(self.model_name)
            except KeyError:
                return tiktoken.get_encoding("cl100k_base")  # fallback
        elif TRANSFORMERS_AVAILABLE:
            try:
                from transformers import AutoTokenizer
                return AutoTokenizer.from_pretrained(self.model_name)
            except Exception:
                print(f"⚠️  Could not load {self.model_name}, using basic word splitting")
                return None
        else:
            print(f"⚠️  No tokenizer available for {self.model_name}, using basic word splitting "
                  "(pip install transformers for Hugging Face tokenizers)")
            return None
    
    def _encode(self, text: str) -> list:
        """Encode with the loaded tokenizer; special-token text is counted, not rejected."""
        if TIKTOKEN_AVAILABLE and isinstance(self.tokenizer, tiktoken.Encoding):
            return self.tokenizer.encode(text, disallowed_special=())
        return self.tokenizer.encode(text)

    def tokenize(self, text: str) -> TokenStats:
        """Tokenize text and return comprehensive stats"""
        if self.tokenizer is None:
            # Fallback: simple word-based tokenization
            tokens = text.split()
        elif hasattr(self.tokenizer, 'encode'):
            # tiktoken
            token_ids = self._encode(text)
            tokens = [self.tokenizer.decode([tid]) for tid in token_ids]
        else:
            # transformers
            tokens = self.tokenizer.tokenize(text)
        
        lines = text.split('\n')
        line_stats = []
        
        for line in lines:
            if self.tokenizer is None:
                line_tokens = len(line.split())
            elif hasattr(self.tokenizer, 'encode'):
                line_tokens = len(self._encode(line))
            else:
                line_tokens = len(self.tokenizer.tokenize(line))
            line_stats.append((line, line_tokens))
        
        return TokenStats(
            text=text,
            tokens=tokens,
            token_count=len(tokens),
            char_count=len(text),
            efficiency=len(text) / len(tokens) if tokens else 0,
            line_stats=line_stats
        )
    
    def visualize_tokens(self, text: str, show_individual: bool = True) -> None:
        """Display comprehensive token analysis"""
        stats = self.tokenize(text)
        
        print(f"\n{Colors.BOLD}🔍 TOKEN ANALYSIS - {self.model_name.upper()}{Colors.END}")
        print("=" * 60)
        
        # Overall stats
        print(f"{Colors.CYAN}📊 SUMMARY:{Colors.END}")
        print(f"  Total tokens: {Colors.BOLD}{stats.token_count:,}{Colors.END}")
        print(f"  Total characters: {Colors.BOLD}{stats.char_count:,}{Colors.END}")
        print(f"  Efficiency: {Colors.BOLD}{stats.efficiency:.2f}{Colors.END} chars/token")
        
        # Cost estimation (rough)
        gpt4_input_cost = stats.token_count * 0.00003  # $0.03 per 1K tokens
        print(f"  Est. GPT-4 cost: {Colors.GREEN}${gpt4_input_cost:.4f}{Colors.END}")
        
        # Line-by-line analysis
        print(f"\n{Colors.CYAN}📝 LINE BREAKDOWN:{Colors.END}")
        expensive_lines = []
        
        for i, (line, token_count) in enumerate(stats.line_stats, 1):
            if token_count == 0:
                continue
                
            # Color code based on token density
            if token_count > 50:
                color = Colors.RED
                expensive_lines.append((i, line[:50] + "...", token_count))
            elif token_count > 25:
                color = Colors.YELLOW
            else:
                color = Colors.GREEN
            
            efficiency = len(line) / token_count if token_count > 0 else 0
            print(f"  {color}Line {i:2d}: {token_count:3d} tokens{Colors.END} "
                  f"({efficiency:.1f} c/t) {line[:60]}{'...' if len(line) > 60 else ''}")
        
        # Highlight expensive sections
        if expensive_lines:
            print(f"\n{Colors.RED}🚨 EXPENSIVE LINES (>50 tokens):{Colors.END}")
            for line_num, preview, tokens in expensive_lines:
                print(f"  Line {line_num}: {tokens} tokens - {preview}")
        
        # Individual token visualization
        if show_individual and stats.token_count <= 200:  # Only for shorter texts
            print(f"\n{Colors.CYAN}🔤 TOKEN BREAKDOWN:{Colors.END}")
            self._display_token_grid(stats.tokens)
        elif show_individual:
            print(f"\n{Colors.YELLOW}⚠️  Too many tokens ({stats.token_count}) for individual display{Colors.END}")
    
    def _display_token_grid(self, tokens: List[str]) -> None:
        """Display tokens in a readable grid format"""
        line_length = 0
        current_line = []
        
        for i, token in enumerate(tokens):
            # Clean token for display
            clean_token = repr(token)[1:-1]  # Remove quotes, show escapes
            token_display = f"[{i}:{clean_token}]"
            
            if line_length + len(token_display) > 80:
                print("  " + " ".join(current_line))
                current_line = [token_display]
                line_length = len(token_display)
            else:
                current_line.append(token_display)
                line_length += len(token_display) + 1
        
        if current_line:
            print("  " + " ".join(current_line))
    
    def suggest_compression(self, text: str) -> None:
        """Analyze text and suggest compression techniques"""
        stats = self.tokenize(text)
        suggestions = []
        
        print(f"\n{Colors.BOLD}🎯 COMPRESSION SUGGESTIONS{Colors.END}")
        print("=" * 60)
        
        # Check for repetitive phrases
        words = text.lower().split()
        word_freq = Counter(words)
        common_words = [w for w, c in word_freq.most_common(10) if c > 3 and len(w) > 3]
        
        if common_words:
            suggestions.append(f"{Colors.YELLOW}📝 Repetitive words:{Colors.END} {', '.join(common_words[:5])}")
            suggestions.append("   Consider using pronouns or abbreviations")
        
        # Check for verbose patterns
        verbose_patterns = [
            (r'\bin order to\b', 'to'),
            (r'\bdue to the fact that\b', 'because'),
            (r'\bat this point in time\b', 'now'),
            (r'\bfor the purpose of\b', 'to'),
            (r'\bin the event that\b', 'if'),
        ]
        
        found_verbose = []
        for pattern, replacement in verbose_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                found_verbose.append(f"'{pattern}' → '{replacement}'")
        
        if found_verbose:
            suggestions.append(f"{Colors.YELLOW}✂️  Verbose phrases found:{Colors.END}")
            for suggestion in found_verbose:
                suggestions.append(f"   {suggestion}")
        
        # Check efficiency
        if stats.efficiency < 3.0:
            suggestions.append(f"{Colors.RED}⚡ Low efficiency ({stats.efficiency:.1f} c/t):{Colors.END}")
            suggestions.append("   Consider removing filler words, combining sentences")
        
        # Check for long lines
        long_lines = [(i+1, line) for i, (line, tokens) in enumerate(stats.line_stats) if tokens > 40]
        if long_lines:
            suggestions.append(f"{Colors.YELLOW}📏 Long lines detected:{Colors.END}")
            for line_num, line in long_lines[:3]:
                suggestions.append(f"   Line {line_num}: Consider breaking into smaller parts")
        
        # Whitespace optimization
        if text.count('  ') > 5 or text.count('\n\n\n') > 0:
            suggestions.append(f"{Colors.GREEN}🧹 Whitespace optimization:{Colors.END}")
            suggestions.append("   Remove extra spaces and line breaks")
        
        if suggestions:
            for suggestion in suggestions:
                print(suggestion)
        else:
            print(f"{Colors.GREEN}✅ Text appears well-optimized!{Colors.END}")
        
        # Show potential savings
        original_tokens = stats.token_count
        estimated_savings = max(0, int(original_tokens * 0.1))  # Conservative 10%
        
        if estimated_savings > 0:
            savings_cost = estimated_savings * 0.00003
            print(f"\n{Colors.CYAN}💰 POTENTIAL SAVINGS:{Colors.END}")
            print(f"  Estimated reduction: {estimated_savings} tokens (10%)")
            print(f"  Cost savings: ${savings_cost:.4f} per request")


def _prepare_console() -> None:
    """Make emoji and colors work in Windows consoles and pipes."""
    for stream in (sys.stdout, sys.stderr):
        encoding = (getattr(stream, "encoding", "") or "").lower().replace("-", "")
        if encoding != "utf8":
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except (AttributeError, ValueError):
                pass
    if os.name == "nt":
        try:  # turn on ANSI escape processing for the classic console
            import ctypes
            kernel32 = ctypes.windll.kernel32
            handle = kernel32.GetStdHandle(-11)
            mode = ctypes.c_uint32()
            if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
                kernel32.SetConsoleMode(handle, mode.value | 0x0004)
        except Exception:
            pass


def _launched_by_double_click() -> bool:
    """True when Windows opened a fresh console just for us (e.g. from Explorer)."""
    if os.name != "nt":
        return False
    try:
        import ctypes
        count = ctypes.windll.kernel32.GetConsoleProcessList((ctypes.c_uint32 * 4)(), 4)
    except Exception:
        return False
    # A PyInstaller one-file build is two processes (bootloader + app).
    return count <= (2 if getattr(sys, "frozen", False) else 1)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="token-visualizer",
        description="Show how an LLM tokenizer splits your prompt, which lines cost the most "
                    "tokens, and which wordy phrases you can cut.",
        epilog="With no file, paste text and finish with Ctrl+D (Ctrl+Z then Enter on Windows), "
               "or pipe it in: cat prompt.txt | token-visualizer -m gpt-4",
    )
    parser.add_argument("file", nargs="?", help="text file to analyze (default: read stdin)")
    parser.add_argument("-m", "--model",
                        help=f"tokenizer to use: {', '.join(MODEL_OPTIONS)}, any tiktoken model "
                             "name, or a Hugging Face model ID. Asked interactively if omitted "
                             "in a terminal, otherwise gpt-4.")
    parser.add_argument("--no-color", action="store_true", help="disable ANSI colors")
    parser.add_argument("--version", action="version", version=f"token-visualizer {__version__}")
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """Interactive token visualizer"""
    _prepare_console()
    args = build_parser().parse_args(argv)
    if args.no_color or not sys.stdout.isatty() or os.environ.get("NO_COLOR"):
        Colors.disable()
    interactive = sys.stdin is not None and sys.stdin.isatty()
    pause = interactive and _launched_by_double_click()

    try:
        if args.file:
            # File mode
            try:
                with open(args.file, 'r', encoding='utf-8') as f:
                    text = f.read()
            except FileNotFoundError:
                print(f"❌ File not found: {args.file}")
                return 1
        elif not interactive:
            text = sys.stdin.read() if sys.stdin is not None else ""
        else:
            # Interactive mode
            eof = "Ctrl+Z then Enter" if os.name == "nt" else "Ctrl+D"
            print(f"{Colors.BOLD}🔍 Token Visualizer{Colors.END}")
            print(f"Enter your text (press {eof} on a new line when done):")
            print("-" * 50)

            lines = []
            try:
                while True:
                    line = input()
                    lines.append(line)
            except EOFError:
                pass
            text = '\n'.join(lines)

        if not text.strip():
            print("❌ No text provided")
            return 1

        # Choose model
        model_name = args.model
        if not model_name and interactive:
            print(f"\n{Colors.CYAN}Select tokenizer:{Colors.END}")
            for i, model in enumerate(MODEL_OPTIONS, 1):
                print(f"  {i}. {model}")
            try:
                choice = input(f"Choice (1-{len(MODEL_OPTIONS)}, default=1): ").strip()
                if not choice:
                    choice = "1"
                model_name = MODEL_OPTIONS[int(choice) - 1]
            except (ValueError, IndexError, EOFError):
                model_name = "gpt-4"
        model_name = model_name or "gpt-4"

        # Analyze
        visualizer = TokenVisualizer(model_name)
        visualizer.visualize_tokens(text)
        visualizer.suggest_compression(text)
        return 0
    finally:
        if pause:
            try:
                input("\nPress Enter to close this window...")
            except EOFError:
                pass


if __name__ == "__main__":
    sys.exit(main())
