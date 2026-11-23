import json

from fastapi.templating import Jinja2Templates

from app.config import get_settings
from app.services.assistant_content import load_panel

templates = Jinja2Templates(directory="templates")
templates.env.filters["tojson"] = json.dumps

# Chat panel copy from panel.md, or None when the assistant is disabled (templates render nothing).
templates.env.globals["assistant_panel"] = (
    load_panel() if get_settings().assistant_enabled else None
)
