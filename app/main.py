from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routes import blog, home, projects

app = FastAPI(title="xdadwal.in")
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(home.router)
app.include_router(projects.router)
app.include_router(blog.router)
