"""Export the assistant's stored conversations as OTLP/JSON, one trace per line.

Usage (from the repo root): python -m scripts.export_chats <out.jsonl>
"""

import asyncio
import sys

from logpose import export_traces

from app.config import load_env


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__.strip().splitlines()[-1], file=sys.stderr)
        return 2
    # logpose finds the database through LOGPOSE_DB_PATH, which may live in .env.
    load_env()
    result = asyncio.run(export_traces(sys.argv[1]))
    print(f"Exported {result.traces} conversation turns to {sys.argv[1]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
