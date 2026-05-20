from pathlib import Path

import frontmatter
import markdown

from app.models.blog import BlogPost

POSTS_DIR = Path(__file__).parent.parent / "content" / "posts"


def get_all_posts() -> list[BlogPost]:
    posts = []
    for path in POSTS_DIR.glob("*.md"):
        post = frontmatter.load(path)
        if not post.get("published", False):
            continue
        posts.append(
            BlogPost(
                title=post["title"],
                date=post["date"],
                description=post["description"],
                tags=post.get("tags", []),
                reading_time=post.get("reading_time", 5),
                slug=path.stem,
                published=True,
            )
        )
    return sorted(posts, key=lambda p: p.date, reverse=True)


def get_post(slug: str) -> BlogPost | None:
    path = POSTS_DIR / f"{slug}.md"
    if not path.exists():
        return None
    post = frontmatter.load(path)
    if not post.get("published", True):
        return None
    content = markdown.markdown(post.content, extensions=["extra"])
    return BlogPost(
        title=post["title"],
        date=post["date"],
        description=post["description"],
        tags=post.get("tags", []),
        reading_time=post.get("reading_time", 5),
        slug=slug,
        published=True,
        content=content,
    )
