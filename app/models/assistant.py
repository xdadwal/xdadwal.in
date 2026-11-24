from typing import Annotated, Literal

from pydantic import BaseModel, Field, HttpUrl, StringConstraints, field_validator

NonEmptyStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class GuardrailReplies(BaseModel):
    too_long: NonEmptyStr
    blocked_pattern: NonEmptyStr
    off_topic: NonEmptyStr
    unsafe: NonEmptyStr


class GuardrailContent(BaseModel):
    """`guardrails.md`: frontmatter fields plus the body as `domain`."""

    max_chars: int = Field(ge=1)
    on_topic_min: float = Field(ge=0, le=1)
    unsafe_max: float = Field(ge=0, le=1)
    block_patterns: list[str] = []
    replies: GuardrailReplies
    domain: NonEmptyStr


class PanelContent(BaseModel):
    """`panel.md`: the copy visitors see in the floating ask bar and the chat panel."""

    greeting: NonEmptyStr
    placeholder: NonEmptyStr
    starters: list[str] = []
    credit: NonEmptyStr | None = None
    credit_url: HttpUrl | None = None
    # The "email Akshay" button under a reply that gives his address. `{question}` in the body
    # is replaced with the visitor's question.
    contact_label: NonEmptyStr | None = None
    contact_copied: NonEmptyStr | None = None
    contact_subject: str = ""
    contact_body: str = ""

    @field_validator("starters")
    @classmethod
    def _drop_blank_starters(cls, value: list[str]) -> list[str]:
        return [item.strip() for item in value if item.strip()]


class ContextContent(BaseModel):
    """`context.md`: the ordered sources that make up the model's system prompt."""

    sources: list[NonEmptyStr] = Field(min_length=1)


class ChatRequest(BaseModel):
    # 8000 is a transport cap; the content-defined limit in guardrails.md is enforced by the guard.
    message: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=8000)]
    page: str | None = Field(default=None, max_length=200)


class FeedbackRequest(BaseModel):
    id: Annotated[str, StringConstraints(pattern=r"^run_[0-9a-f]{32}$")]
    rating: Literal["up", "down"]


class HistoryMessage(BaseModel):
    role: Literal["user", "assistant"]
    text: str
