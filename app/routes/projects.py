from fastapi import APIRouter, Request

from app.data import PROJECTS
from app.templates import templates

router = APIRouter()


@router.get("/projects")
async def projects(request: Request):
    return templates.TemplateResponse(
        request,
        "projects/index.html",
        {"active_page": "projects", "projects": PROJECTS},
    )
