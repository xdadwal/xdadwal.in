"""Download the site's fonts from Google Fonts into static/fonts/ and write static/css/fonts.css.

The site serves its own copies, so pages don't wait on fonts.googleapis.com and fonts.gstatic.com.
Run it again after adding an icon to ICON_NAMES (or changing a font), then rebuild the CSS:

    python -m scripts.fetch_fonts
"""

import re
import urllib.request

from app.services.static_assets import STATIC_DIR, static_url

TEXT_FONTS = (
    "https://fonts.googleapis.com/css2?family=Hanken+Grotesk:wght@400;600;700"
    "&family=JetBrains+Mono:wght@400;500&display=swap"
)
# Only the icons the templates use, including ones set from x-text. An icon missing from this list
# shows as its name in plain text. Google Fonts needs them in alphabetical order.
ICON_NAMES = [
    "add",
    "arrow_back",
    "arrow_right_alt",
    "arrow_upward",
    "auto_awesome",
    "check",
    "close",
    "content_copy",
    "expand_more",
    "mail",
    "menu",
    "open_in_new",
    "refresh",
    "stop",
    "thumb_down",
    "thumb_up",
]
ICON_FONT = (
    "https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1"
    f"&icon_names={','.join(sorted(ICON_NAMES))}&display=block"
)
# The site's copy is English; latin-ext covers accented names. Other scripts are left out.
SUBSETS = {"latin", "latin-ext"}

FONTS_DIR = STATIC_DIR / "fonts"
CSS_FILE = STATIC_DIR / "css" / "fonts.css"
# Google Fonts picks the font format by browser; this one gets woff2.
_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/130.0 Safari/537.36"
)
_BLOCK = re.compile(r"(?:/\* (?P<subset>[\w-]+) \*/\s*)?(?P<rule>@font-face \{.*?\})", re.S)
_URL = re.compile(r"url\((https://fonts\.gstatic\.com/[^)]+)\)")


def _get(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()


def _slug(family: str) -> str:
    return family.lower().replace(" ", "-")


def _localize(css: str, keep_all_subsets: bool) -> tuple[list[str], dict[str, str]]:
    """Google's @font-face rules for the kept subsets, and a map of each font URL to a file name."""
    rules, files = [], {}
    for match in _BLOCK.finditer(css):
        subset, rule = match.group("subset"), match.group("rule")
        if not keep_all_subsets and subset not in SUBSETS:
            continue
        family = re.search(r"font-family: '([^']+)'", rule).group(1)
        url = _URL.search(rule).group(1)
        if url not in files:
            name = _slug(family) + (f"-{subset}" if subset else "")
            if name in files.values():  # a static (non-variable) font has one file per weight
                weight = re.search(r"font-weight: ([\d ]+);", rule).group(1).replace(" ", "-")
                name = f"{name}-{weight}"
            files[url] = name
        rules.append(rule)
    return rules, files


def main() -> None:
    text_css = _get(TEXT_FONTS).decode()
    icon_css = _get(ICON_FONT).decode()
    text_rules, text_files = _localize(text_css, keep_all_subsets=False)
    icon_rules, icon_files = _localize(icon_css, keep_all_subsets=True)
    # The icon stylesheet also defines the .material-symbols-outlined class.
    class_start = icon_css.rindex("}", 0, icon_css.index(".material-symbols-outlined")) + 1
    icon_class = icon_css[class_start:]

    FONTS_DIR.mkdir(exist_ok=True)
    for old in FONTS_DIR.glob("*.woff2"):
        old.unlink()
    local = {}
    for url, name in {**text_files, **icon_files}.items():
        (FONTS_DIR / f"{name}.woff2").write_bytes(_get(url))
        local[url] = static_url(f"fonts/{name}.woff2")

    def rewrite(rule: str) -> str:
        return _URL.sub(lambda m: f'url("{local[m.group(1)]}")', rule)

    header = "/* Generated from Google Fonts by `python -m scripts.fetch_fonts`. Don't edit. */\n"
    body = "\n\n".join(rewrite(rule) for rule in text_rules + icon_rules)
    CSS_FILE.write_text(f"{header}\n{body}\n\n{icon_class.strip()}\n")
    print(f"Wrote {len(local)} font files to {FONTS_DIR} and {CSS_FILE}")


if __name__ == "__main__":
    main()
