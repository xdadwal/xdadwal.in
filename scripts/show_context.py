"""Print what the assistant's model is given: each source in context.md and its size.

Usage (from the repo root): python -m scripts.show_context [--full]
"""

import sys

from app.services.assistant_content import build_system_prompt, context_sections


def main() -> int:
    if "--full" in sys.argv[1:]:
        print(build_system_prompt())
        return 0
    total = 0
    for title, text in context_sections():
        # Roughly four characters per token for English text.
        tokens = len(text) // 4
        total += tokens
        print(f"{tokens:>7,} tokens  {title}")
    print(f"{total:>7,} tokens  total (estimate)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
