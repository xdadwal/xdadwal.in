"""The site's assistant: one shared logpose agent, per-visitor sessions, and SSE replies."""

import asyncio
import hashlib
import json
import logging
import re
import secrets
import sqlite3
from collections.abc import AsyncIterator
from contextlib import AsyncExitStack, aclosing
from dataclasses import dataclass, field
from datetime import timedelta

import httpx
from logpose import (
    Agent,
    GuardrailInput,
    GuardrailVerdict,
    InputGuardrail,
    LogposeError,
    Message,
    RunEnd,
    SessionHandle,
    TextBlock,
    TextDelta,
    openai_decision_guard,
    pattern_guard,
)

from app.config import Settings
from app.models.assistant import HistoryMessage, PagesContent
from app.services.assistant_content import build_system_prompt, load_guardrails, load_pages
from app.services.feedback import FeedbackStore
from app.services.rate_limit import RateLimiter

logger = logging.getLogger(__name__)

_SESSION_ID_RE = re.compile(r"[A-Za-z0-9_-]{43}")
_CLEANUP_INTERVAL_SECONDS = 24 * 60 * 60

# Transport-level failures only; everything the assistant "says" comes from the .md content files.
_CUT_SHORT = "That answer was cut short. Try asking something more specific."
_FAILED = "Something went wrong on my side. Please try again."


@dataclass
class AssistantRuntime:
    agent: Agent
    limiter: RateLimiter
    http_client: httpx.AsyncClient
    pages: PagesContent | None
    feedback: FeedbackStore
    # Ratings get their own allowance so that rating answers never uses up a visitor's messages.
    feedback_limiter: RateLimiter


def build_runtime(settings: Settings) -> AssistantRuntime:
    """Build the shared agent from settings and the content files.

    logpose reads the endpoint, credentials, database path and tracing switches from its own
    LOGPOSE_* environment variables, so none of them are passed here.
    """
    guardrails = load_guardrails()
    http_client = httpx.AsyncClient()

    guards = [_length_guard(guardrails.max_chars, guardrails.replies.too_long)]
    if guardrails.block_patterns:
        guards.append(
            pattern_guard(
                max_chars=None,
                block_patterns=guardrails.block_patterns,
                reply=guardrails.replies.blocked_pattern,
            )
        )
    guards.append(
        openai_decision_guard(
            guardrails.domain,
            replies={
                "off_topic": guardrails.replies.off_topic,
                "unsafe": guardrails.replies.unsafe,
            },
            on_topic_min=guardrails.on_topic_min,
            unsafe_max=guardrails.unsafe_max,
            # A guard outage must not take the chat down; instructions and rate limits still apply.
            on_error="allow",
            client=http_client,
        )
    )

    extra = {}
    if settings.assistant_reasoning_effort is not None:
        extra["reasoning_effort"] = settings.assistant_reasoning_effort

    agent = Agent(
        "openai-compat",
        model=settings.assistant_model,
        system=build_system_prompt(),
        max_tokens=settings.assistant_max_output_tokens,
        max_iterations=1,
        run_timeout=settings.assistant_run_timeout_seconds,
        provider_turn_timeout=settings.assistant_turn_timeout_seconds,
        extra=extra,
        session_ttl=timedelta(days=settings.assistant_retention_days),
        context_window=settings.assistant_context_window,
        context_budget=settings.assistant_context_budget,
        input_guardrails=guards,
        guardrail_mode="parallel",
    )
    return AssistantRuntime(
        agent=agent,
        limiter=_limiter(settings),
        http_client=http_client,
        pages=load_pages(),
        feedback=FeedbackStore(settings.assistant_feedback_db_path),
        feedback_limiter=_limiter(settings),
    )


def _length_guard(max_chars: int, reply: str) -> InputGuardrail:
    """Cap the length of what the visitor typed. The page note in front of it does not count,
    so the same question is never too long on one page and fine on another."""

    def length_guard(inp: GuardrailInput) -> GuardrailVerdict:
        if len(_shown_text(inp.message)) > max_chars:
            return GuardrailVerdict.block("too_long", reply, reason=f"over {max_chars} chars")
        return GuardrailVerdict.allow()

    length_guard.name = "length_guard"  # type: ignore[attr-defined]
    return length_guard


def _limiter(settings: Settings) -> RateLimiter:
    return RateLimiter(
        per_ip=settings.assistant_rate_limit_per_ip,
        window_seconds=settings.assistant_rate_limit_window_seconds,
        per_day=settings.assistant_rate_limit_per_day,
    )


async def close_runtime(runtime: AssistantRuntime) -> None:
    await runtime.agent.aclose()
    await runtime.http_client.aclose()


async def cleanup_loop(runtime: AssistantRuntime, retention: timedelta) -> None:
    """Delete expired chats, old traces and old ratings once a day. Runs until cancelled."""
    while True:
        try:
            sessions = await runtime.agent.purge_expired_sessions()
            spans = await runtime.agent.purge_traces(older_than=retention)
            ratings = await runtime.feedback.purge(older_than=retention)
            logger.info(
                "assistant cleanup: %d expired sessions, %d old spans, %d old ratings",
                sessions,
                spans,
                ratings,
            )
        except (LogposeError, sqlite3.Error):
            # logpose wraps only open failures; later writes raise sqlite3 errors (a locked db).
            logger.exception("assistant cleanup failed; will retry at the next interval")
        await asyncio.sleep(_CLEANUP_INTERVAL_SECONDS)


def new_session_id() -> str:
    return secrets.token_urlsafe(32)


def is_session_id(value: str | None) -> bool:
    return value is not None and _SESSION_ID_RE.fullmatch(value) is not None


def visitor_hash(session_id: str) -> str:
    """Stands in for the session ID wherever the ID itself should not travel or be stored."""
    return hashlib.sha256(session_id.encode()).hexdigest()


def _new_run_id() -> str:
    return f"run_{secrets.token_hex(16)}"


@dataclass
class ChatTurn:
    """One visitor message being answered: the leased session and the run streaming its reply.

    Closing the turn saves and releases the session. A turn that did not finish (provider
    failure, stop button, closed tab) is rolled back first, on every exit path: logpose appends
    the question as the run starts, which would otherwise leave it stored with no answer, and
    stored twice after a retry.
    """

    stack: AsyncExitStack
    handle: SessionHandle
    stream: AsyncIterator[object] | None = field(default=None, repr=False)
    finished: bool = False

    async def _rollback(self) -> None:
        if self.finished:
            return
        if self.stream is not None:
            # End the run before editing its history; a no-op if it has already been closed.
            await self.stream.aclose()
        del self.handle.conversation.messages[self.handle.loaded_count :]

    async def aclose(self) -> None:
        await self.stack.aclose()


async def open_turn(agent: Agent, session_id: str) -> ChatTurn:
    """Lease the visitor's session. Raises SessionBusyError if a reply is already in progress.

    The caller owns the returned turn and must close it once the reply has been sent.
    """
    stack = AsyncExitStack()
    handle = await stack.enter_async_context(agent.session(session_id))
    turn = ChatTurn(stack=stack, handle=handle)
    # Exit callbacks run last-in first-out, so the rollback runs before the session saves.
    stack.push_async_callback(turn._rollback)
    return turn


def _sse(event: str, data: dict[str, object]) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


async def reply_events(
    agent: Agent, turn: ChatTurn, message: str, page: str | None, note: str | None
) -> AsyncIterator[str]:
    """Stream one reply as SSE frames, then save and release the session.

    `note` (see `page_note`) goes in front of the question as a block of its own, so the model
    reads it with the message while the visitor's history shows only what they typed.
    """
    # A hash, so OpenAI can attribute abuse to one visitor without receiving the session ID.
    extra = {"safety_identifier": visitor_hash(turn.handle.id)}
    metadata = {"page": page} if page else None
    # Our own ID for the run, sent to the browser so a rating can be matched to this answer.
    run_id = _new_run_id()
    prompt: str | Message = message
    if note:
        prompt = Message(
            role="user", content=[TextBlock(text=f"{note}\n\n"), TextBlock(text=message)]
        )
    try:
        turn.stream = agent.stream(
            prompt, session=turn.handle, extra=extra, metadata=metadata, run_id=run_id
        )
        # aclosing ends the run before the session is saved, also when the client disconnects.
        async with aclosing(turn.stream) as events:
            async for event in events:
                if isinstance(event, TextDelta):
                    yield _sse("delta", {"text": event.text})
                elif isinstance(event, RunEnd):
                    turn.finished = True
                    if event.result.stop_reason == "max_tokens":
                        yield _sse("error", {"message": _CUT_SHORT, "retry": False})
                    else:
                        blocked = event.result.guardrail is not None
                        yield _sse("done", {"blocked": blocked, "id": run_id})
    except LogposeError:
        # Provider, auth and timeout failures: details go to the log, never to the visitor.
        logger.exception("assistant reply failed")
        yield _sse("error", {"message": _FAILED, "retry": True})
    finally:
        await turn.aclose()


async def load_history(agent: Agent, session_id: str) -> list[HistoryMessage]:
    messages = await agent.load_session(session_id)
    history = [
        HistoryMessage(role=message.role, text=_shown_text(message))
        for message in messages
        if message.role in ("user", "assistant")
    ]
    return [item for item in history if item.text]


def _shown_text(message: Message) -> str:
    """What the visitor saw: their own words without the page note, or the whole answer."""
    if message.role == "user":
        blocks = [block.text for block in message.content if isinstance(block, TextBlock)]
        return blocks[-1] if blocks else ""
    return message.text
