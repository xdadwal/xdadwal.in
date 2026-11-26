from fastapi import APIRouter, Request

from app.data import PROJECTS
from app.templates import templates

router = APIRouter()


@router.api_route("/projects", methods=["GET", "HEAD"])
async def projects(request: Request):
    return templates.TemplateResponse(
        request,
        "projects/index.html",
        {"active_page": "projects", "projects": PROJECTS},
    )
