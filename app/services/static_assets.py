"""Versioned URLs for static files, so browsers can cache them for a long time."""

import hashlib
from functools import lru_cache
from pathlib import Path

STATIC_DIR = Path(__file__).parent.parent.parent / "static"


def static_url(path: str) -> str:
    """URL of a file under static/, with a version that changes whenever its content does.

    A missing file gets no version: the page still renders, and the browser's request for the file
    gets the same 404 it would without versioning (e.g. before the CSS is built).
    """
    file = STATIC_DIR / path
    try:
        stat = file.stat()
    except FileNotFoundError:
        return f"/static/{path}"
    return f"/static/{path}?v={_version(file, stat.st_mtime_ns, stat.st_size)}"


@lru_cache(maxsize=64)
def _version(file: Path, mtime_ns: int, size: int) -> str:
    # The modification time and size are in the cache key, so a rebuilt file is hashed again.
    return hashlib.sha256(file.read_bytes()).hexdigest()[:12]
