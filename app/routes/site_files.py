"""Files crawlers and agents look for at the site root: robots.txt, sitemap.xml, llms.txt."""

from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import FileResponse

from app.data import PROFILE, PROJECTS
from app.services.blog import get_all_posts
from app.templates import templates

router = APIRouter()

_FAVICON = Path("static/img/favicon.ico")


@router.api_route("/robots.txt", methods=["GET", "HEAD"])
async def robots(request: Request):
    return templates.TemplateResponse(
        request, "site/robots.txt", {}, media_type="text/plain; charset=utf-8"
    )


@router.api_route("/sitemap.xml", methods=["GET", "HEAD"])
async def sitemap(request: Request):
    return templates.TemplateResponse(
        request, "site/sitemap.xml", {"posts": get_all_posts()}, media_type="application/xml"
    )


@router.api_route("/llms.txt", methods=["GET", "HEAD"])
async def llms(request: Request):
    return templates.TemplateResponse(
        request,
        "site/llms.txt",
        {"profile": PROFILE, "projects": PROJECTS, "posts": get_all_posts()},
        media_type="text/plain; charset=utf-8",
    )


# Browsers and search engines ask for /favicon.ico at the root, whatever the page links to.
@router.api_route("/favicon.ico", methods=["GET", "HEAD"])
async def favicon() -> FileResponse:
    return FileResponse(_FAVICON, media_type="image/x-icon")
