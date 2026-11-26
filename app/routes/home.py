from fastapi import APIRouter, Request

from app.services.site_meta import structured_data
from app.templates import templates

router = APIRouter()


@router.api_route("/", methods=["GET", "HEAD"])
async def home(request: Request):
    return templates.TemplateResponse(
        request,
        "home.html",
        {"active_page": "home", "structured_data": structured_data()},
    )
