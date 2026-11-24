import os
from functools import lru_cache

from dotenv import load_dotenv
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings

# Model access is configured through logpose's own environment variables, which logpose reads
# itself; this app never handles their values. The assistant is on only when all of these are set.
LOGPOSE_REQUIRED_ENV = ("LOGPOSE_BASE_URL", "LOGPOSE_API_KEY", "LOGPOSE_GUARD_API_KEY")


def load_env() -> None:
    """Put `.env` into the process environment so logpose can read its `LOGPOSE_*` settings.

    Variables already set in the environment win over the file.
    """
    load_dotenv(".env")


def missing_logpose_env() -> list[str]:
    """Names of the required logpose variables that are unset or blank."""
    return [name for name in LOGPOSE_REQUIRED_ENV if not os.environ.get(name, "").strip()]


class Settings(BaseSettings):
    app_name: str = "xdadwal.in"
    debug: bool = False

    # Assistant behaviour. Credentials, endpoint, database path and tracing are logpose's
    # (LOGPOSE_* variables); logpose has no variable for the settings below.
    assistant_model: str = "gpt-6-luna"
    assistant_reasoning_effort: str | None = "low"
    assistant_max_output_tokens: int = 2000
    # The model's context window, and how much of it one request may use before older turns are
    # summarized. Change the window whenever the model changes.
    assistant_context_window: int = 1_050_000
    assistant_context_budget: int = 16_000
    # Wall-clock limits for a whole reply and for one model call within it.
    assistant_run_timeout_seconds: float = 60
    assistant_turn_timeout_seconds: float = 45
    assistant_retention_days: int = 30
    # SQLite file holding visitors' thumbs up/down on answers.
    assistant_feedback_db_path: str = "feedback.db"
    # Chat messages allowed per visitor per window, and per day across all visitors. 0 = no limit.
    assistant_rate_limit_per_ip: int = Field(default=20, ge=0)
    assistant_rate_limit_window_seconds: int = Field(default=600, ge=1)
    assistant_rate_limit_per_day: int = Field(default=1000, ge=0)

    @field_validator("assistant_reasoning_effort", mode="before")
    @classmethod
    def _blank_is_unset(cls, value: object) -> object:
        """Treat `KEY=` in the environment as "not set"."""
        if isinstance(value, str) and not value.strip():
            return None
        return value

    @property
    def assistant_enabled(self) -> bool:
        return not missing_logpose_env()


@lru_cache
def get_settings() -> Settings:
    load_env()
    return Settings()
