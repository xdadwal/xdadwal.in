"""List visitors' thumbs up/down on the assistant's answers, with each question and answer.

Usage (from the repo root): python -m scripts.show_feedback
"""

import asyncio
import json
import sys
import tempfile
from datetime import datetime
from pathlib import Path

from logpose import export_traces

from app.config import get_settings
from app.services.feedback import FeedbackStore

_NOT_RECORDED = "(not recorded)"


def _attributes(span: dict) -> dict[str, object]:
    return {item["key"]: next(iter(item["value"].values())) for item in span.get("attributes", [])}


def _answer_text(raw: object) -> str | None:
    """The reply text from a span's `gen_ai.output.messages` attribute."""
    try:
        parts = json.loads(str(raw))[0]["parts"]
    except (ValueError, LookupError, TypeError):
        return None
    return "".join(part.get("content", "") for part in parts if part.get("type") == "text")


def _turns(export: Path) -> dict[str, tuple[str, str]]:
    """The question and answer of every run in an OTLP/JSON export, keyed by run ID.

    Both are present only when the site runs with LOGPOSE_TRACE_CONTENT=1.
    """
    turns: dict[str, tuple[str, str]] = {}
    for line in export.read_text(encoding="utf-8").splitlines():
        run_id = None
        question = answer = _NOT_RECORDED
        for resource in json.loads(line).get("resourceSpans", []):
            for scope in resource.get("scopeSpans", []):
                for span in scope.get("spans", []):
                    attributes = _attributes(span)
                    run_id = attributes.get("logpose.run.id", run_id)
                    if span["name"] == "guardrail":
                        question = str(attributes.get("logpose.guardrail.input", question))
                        if attributes.get("logpose.guardrail.allowed") is False:
                            category = attributes.get("logpose.guardrail.category", "guardrail")
                            answer = f"(blocked: {category})"
                    elif "gen_ai.output.messages" in attributes:
                        answer = _answer_text(attributes["gen_ai.output.messages"]) or answer
        if run_id is not None:
            turns[str(run_id)] = (question, answer)
    return turns


def main() -> int:
    # get_settings() also loads .env, where logpose's LOGPOSE_DB_PATH may be set.
    path = Path(get_settings().assistant_feedback_db_path)
    if not path.is_file():
        # Opening the store would create an empty file here and report "no ratings".
        print(f"No ratings file at {path.resolve()}. Is ASSISTANT_FEEDBACK_DB_PATH set?")
        return 1
    ratings = FeedbackStore(str(path)).all()
    if not ratings:
        print("No ratings yet.")
        return 0
    with tempfile.TemporaryDirectory() as folder:
        export = Path(folder) / "traces.jsonl"
        asyncio.run(export_traces(str(export)))
        turns = _turns(export)
    for rating in ratings:
        when = datetime.fromtimestamp(rating.created_at).strftime("%Y-%m-%d %H:%M")
        question, answer = turns.get(rating.run_id, (_NOT_RECORDED, _NOT_RECORDED))
        print(f"{when}  {rating.rating.upper():4}  {rating.run_id}")
        print(f"  Q: {question}")
        print(f"  A: {answer}\n")
    up = sum(1 for rating in ratings if rating.rating == "up")
    print(f"Ratings: {len(ratings)} ({up} up, {len(ratings) - up} down)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
