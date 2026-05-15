from fastapi import APIRouter, Request

from app.data import EXPERIENCE
from app.templates import templates

router = APIRouter()


@router.get("/")
async def home(request: Request):
    return templates.TemplateResponse(
        request,
        "home.html",
        {"active_page": "home", "experience": EXPERIENCE},
    )
