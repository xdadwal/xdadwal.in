# Who the site is about, for search engines (structured data) and AI agents (llms.txt). Keep it to
# what the pages show; employer and skills can join once the home page mentions them.
PROFILE: dict = {
    "name": "Akshay Dadwal",
    "handle": "xdadwal",
    "job_title": "Software Engineer",
    "summary": "Backend engineer, homelab tinkerer and builder.",
    "profiles": {
        "GitHub": "https://github.com/xdadwal",
        "LinkedIn": "https://linkedin.com/in/xdadwal",
    },
}

PROJECTS: list[dict] = [
    {
        "title": "logpose",
        "description": (
            "A provider-neutral agent loop for Python: typed tools, streaming events, "
            "sessions and input guardrails. It runs the assistant on this site."
        ),
        "tags": ["Python", "LLM agents", "asyncio"],
        "url": "https://github.com/xdadwal/logpose",
    },
    {
        "title": "ohara",
        "description": (
            "My home server setup: docker-compose services behind nginx and Certbot, "
            "hosting this site, a media stack and a private dashboard."
        ),
        "tags": ["docker-compose", "nginx", "Linux", "self-hosted"],
        "url": "https://github.com/xdadwal/ohara",
    },
    {
        "title": "the-django-boilerplate",
        "description": (
            "A ready-to-code Django and DRF starter with docker-compose, pre-commit hooks, "
            "base models and serializers, and environment-based settings."
        ),
        "tags": ["Django", "DRF", "Docker"],
        "url": "https://github.com/xdadwal/the-django-boilerplate",
    },
    {
        "title": "dex-cli",
        "description": "A CLI tool to download manga from various platforms.",
        "tags": ["Python", "CLI", "multithreading"],
        "url": "https://github.com/xdadwal/dex-cli",
    },
]
