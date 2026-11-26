import json

from fastapi.templating import Jinja2Templates

from app.config import get_settings
from app.services.assistant_content import load_panel
from app.services.static_assets import static_url

templates = Jinja2Templates(directory="templates")
templates.env.filters["tojson"] = json.dumps
templates.env.globals["static_url"] = static_url
templates.env.globals["site_url"] = get_settings().site_url.rstrip("/")

# Chat panel copy from panel.md, or None when the assistant is disabled (templates render nothing).
templates.env.globals["assistant_panel"] = (
    load_panel() if get_settings().assistant_enabled else None
)
