"""What the site tells search engines and AI agents about itself."""

import json

from app.config import get_settings
from app.data import PROFILE


def structured_data() -> str:
    """JSON-LD for the home page: the site, and the person it is about.

    `sameAs` ties his GitHub and LinkedIn to this site as one person; `WebSite.name` is the site
    name search results show. Returned ready to place inside a <script> element.
    """
    home = f"{get_settings().site_url.rstrip('/')}/"
    data = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "WebSite",
                "name": PROFILE["name"],
                "alternateName": ["xdadwal.in", PROFILE["handle"]],
                "url": home,
            },
            {
                "@type": "ProfilePage",
                "url": home,
                "mainEntity": {
                    "@type": "Person",
                    "name": PROFILE["name"],
                    "alternateName": PROFILE["handle"],
                    "url": home,
                    "jobTitle": PROFILE["job_title"],
                    "description": PROFILE["summary"],
                    "sameAs": list(PROFILE["profiles"].values()),
                },
            },
        ],
    }
    # "<" escaped so no value can close the <script> element early.
    return json.dumps(data, ensure_ascii=False).replace("<", "\\u003c")
