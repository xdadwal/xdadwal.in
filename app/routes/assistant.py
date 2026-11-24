from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import StreamingResponse
from logpose import SessionBusyError
from starlette.background import BackgroundTask

from app.config import Settings, get_settings
from app.models.assistant import ChatRequest, FeedbackRequest, HistoryMessage
from app.services.assistant import (
    AssistantRuntime,
    is_session_id,
    load_history,
    new_session_id,
    open_turn,
    reply_events,
    visitor_hash,
)
from app.services.assistant_content import page_note
from app.services.rate_limit import RateLimiter

router = APIRouter(prefix="/api/chat")

_COOKIE = "chat_sid"


def _runtime(request: Request) -> AssistantRuntime:
    runtime = request.app.state.assistant
    if runtime is None:
        raise HTTPException(status_code=503, detail="Assistant is not enabled")
    return runtime


Runtime = Annotated[AssistantRuntime, Depends(_runtime)]
AppSettings = Annotated[Settings, Depends(get_settings)]


def _session_id(request: Request) -> str | None:
    """The visitor's session ID from their own cookie; a malformed value counts as absent."""
    value = request.cookies.get(_COOKIE)
    return value if is_session_id(value) else None


def _enforce_limit(limiter: RateLimiter, request: Request) -> None:
    client_ip = request.client.host if request.client else "unknown"
    retry_after = limiter.check(client_ip)
    if retry_after is not None:
        raise HTTPException(
            status_code=429,
            detail="Too many requests",
            headers={"Retry-After": str(retry_after)},
        )


def _set_session_cookie(response: Response, session_id: str, settings: Settings) -> None:
    response.set_cookie(
        _COOKIE,
        session_id,
        max_age=settings.assistant_retention_days * 86400,
        path=router.prefix,
        httponly=True,
        samesite="lax",
        secure=not settings.debug,
    )


@router.post("")
async def chat(
    request: Request, body: ChatRequest, runtime: Runtime, settings: AppSettings
) -> StreamingResponse:
    _enforce_limit(runtime.limiter, request)
    # Worked out before the session is leased: it reads content files, and an error after the
    # lease is taken would leave the visitor's session locked until the lease lapses.
    note = page_note(runtime.pages, body.page)

    existing = _session_id(request)
    session_id = existing or new_session_id()
    try:
        turn = await open_turn(runtime.agent, session_id)
    except SessionBusyError:
        raise HTTPException(status_code=409, detail="Another reply is still in progress") from None

    response = StreamingResponse(
        reply_events(runtime.agent, turn, body.message, body.page, note),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        # Covers a body that stops being iterated (the client left before or during streaming).
        background=BackgroundTask(turn.aclose),
    )
    if existing is None:
        _set_session_cookie(response, session_id, settings)
    return response


@router.get("/history")
async def history(request: Request, runtime: Runtime) -> list[HistoryMessage]:
    session_id = _session_id(request)
    if session_id is None:
        return []
    return await load_history(runtime.agent, session_id)


@router.post("/reset", status_code=204)
async def reset(response: Response, runtime: Runtime, settings: AppSettings) -> None:
    # The old session is left to expire, so it stays in the review log until then.
    _set_session_cookie(response, new_session_id(), settings)


@router.post("/feedback", status_code=204)
async def feedback(request: Request, body: FeedbackRequest, runtime: Runtime) -> None:
    """Record a thumbs up or down on one answer; rating it again replaces the earlier rating."""
    _enforce_limit(runtime.feedback_limiter, request)
    session_id = _session_id(request)
    if session_id is None:
        raise HTTPException(status_code=403, detail="No chat session")
    await runtime.feedback.record(visitor_hash(session_id), body.id, body.rating)
