from fastapi import APIRouter, HTTPException, Request

from app.services.blog import get_all_posts, get_post
from app.templates import templates

router = APIRouter()


@router.api_route("/blog", methods=["GET", "HEAD"])
async def blog_index(request: Request):
    posts = get_all_posts()
    all_tags = sorted({tag for post in posts for tag in post.tags})
    return templates.TemplateResponse(
        request,
        "blog/index.html",
        {"active_page": "blog", "posts": posts, "all_tags": all_tags},
    )


@router.api_route("/blog/{slug}", methods=["GET", "HEAD"])
async def blog_post(request: Request, slug: str):
    post = get_post(slug)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return templates.TemplateResponse(
        request,
        "blog/post.html",
        {"active_page": "blog", "post": post},
    )
