"""Reads the assistant's `.md` content files and assembles the model's system prompt."""

from pathlib import Path

import frontmatter
import yaml
from pydantic import BaseModel, ValidationError

from app.data import EXPERIENCE, PROJECTS
from app.models.assistant import ContextContent, GuardrailContent, PanelContent
from app.services.blog import get_all_posts

CONTENT_DIR = Path(__file__).parent.parent / "content" / "assistant"

# Config files that are never part of the prompt, even if a glob in context.md matches them.
_CONFIG_FILES = frozenset({"context.md", "guardrails.md", "panel.md"})


class AssistantContentError(RuntimeError):
    """An assistant content file is missing or invalid."""


def _load(name: str) -> frontmatter.Post:
    path = CONTENT_DIR / name
    try:
        return frontmatter.load(path)
    except FileNotFoundError as exc:
        raise AssistantContentError(f"{name}: file not found at {path}") from exc
    except yaml.YAMLError as exc:
        raise AssistantContentError(f"{name}: invalid frontmatter: {exc}") from exc


def _validate[T: BaseModel](model: type[T], name: str, data: dict[str, object]) -> T:
    try:
        return model.model_validate(data)
    except ValidationError as exc:
        fields = "; ".join(
            f"{'.'.join(str(part) for part in error['loc'])}: {error['msg']}"
            for error in exc.errors()
        )
        raise AssistantContentError(f"{name}: {fields}") from exc


def load_guardrails() -> GuardrailContent:
    post = _load("guardrails.md")
    return _validate(GuardrailContent, "guardrails.md", {**post.metadata, "domain": post.content})


def load_panel() -> PanelContent:
    post = _load("panel.md")
    return _validate(PanelContent, "panel.md", dict(post.metadata))


def _experience_section() -> str:
    lines: list[str] = []
    for company in EXPERIENCE:
        lines.append(f"## {company['company']} ({company['period']})")
        for role in company["roles"]:
            lines.append(f"- {role['title']} ({role['period']}): {role['description']}")
            if role.get("tags"):
                lines.append(f"  Technologies: {', '.join(role['tags'])}")
    return "\n".join(lines)


def _projects_section() -> str:
    lines: list[str] = []
    for project in PROJECTS:
        lines.append(f"- {project['title']}: {project['description']}")
        if project.get("tags"):
            lines.append(f"  Technologies: {', '.join(project['tags'])}")
        if project.get("url"):
            lines.append(f"  Link: {project['url']}")
    return "\n".join(lines)


def _blog_section() -> str:
    return "\n".join(
        f"- {post.title} — {post.description} — /blog/{post.slug}" for post in get_all_posts()
    )


_SITE_SOURCES = {
    "experience": ("Experience (from the site)", _experience_section),
    "projects": ("Projects (from the site)", _projects_section),
    "blog": ("Blog posts", _blog_section),
}


def _file_title(path: Path) -> str:
    relative = path.relative_to(CONTENT_DIR)
    stem = relative.stem.replace("-", " ").replace("_", " ")
    if relative.parent == Path("."):
        return stem.capitalize()
    return f"{relative.parent.as_posix().capitalize()}: {stem}"


def _file_sections(source: str, seen: set[Path]) -> list[tuple[str, str]]:
    """Read the files a context.md entry names, skipping any an earlier entry already added."""
    is_glob = any(char in source for char in "*?[")
    paths = sorted(CONTENT_DIR.glob(source)) if is_glob else [CONTENT_DIR / source]
    sections: list[tuple[str, str]] = []
    for path in paths:
        if not path.resolve().is_relative_to(CONTENT_DIR.resolve()):
            raise AssistantContentError(f"context.md: '{source}' points outside {CONTENT_DIR}")
        if path.name in _CONFIG_FILES and path.parent == CONTENT_DIR:
            continue
        if not path.is_file():
            raise AssistantContentError(f"context.md: source '{source}' not found at {path}")
        if path in seen:
            continue
        seen.add(path)
        sections.append((_file_title(path), path.read_text(encoding="utf-8").strip()))
    return sections


def context_sections() -> list[tuple[str, str]]:
    """Return the (title, text) sections listed in `context.md`, in order, skipping empty ones."""
    post = _load("context.md")
    context = _validate(ContextContent, "context.md", dict(post.metadata))
    sections: list[tuple[str, str]] = []
    seen: set[Path] = set()
    for source in context.sources:
        if source.startswith("site:"):
            name = source.removeprefix("site:")
            if name not in _SITE_SOURCES:
                known = ", ".join(f"site:{key}" for key in _SITE_SOURCES)
                raise AssistantContentError(f"context.md: unknown source '{source}' (use {known})")
            title, render = _SITE_SOURCES[name]
            sections.append((title, render()))
        else:
            sections.extend(_file_sections(source, seen))
    return [(title, text) for title, text in sections if text]


def build_system_prompt() -> str:
    sections = context_sections()
    if not sections:
        raise AssistantContentError("context.md: the listed sources are all empty")
    return "\n\n".join(f"# {title}\n\n{text}" for title, text in sections)
