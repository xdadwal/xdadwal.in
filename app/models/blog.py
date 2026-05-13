from datetime import date

from pydantic import BaseModel


class BlogPost(BaseModel):
    title: str
    date: date
    description: str
    tags: list[str]
    reading_time: int
    slug: str
    content: str = ""
