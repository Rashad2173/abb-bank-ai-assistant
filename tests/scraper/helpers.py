"""Small builders for test inputs."""

from __future__ import annotations

import json


def flight_push(payload: str) -> str:
    """Wrap a Flight payload the way Next.js embeds it into the HTML."""
    return f"<script>self.__next_f.push([1,{json.dumps(payload)}])</script>"


def flight_text_row(row_id: str, text: str) -> str:
    """A Flight text row; its length prefix counts UTF-8 bytes."""
    return f"{row_id}:T{len(text.encode('utf-8')):x},{text}"


def page_html(body: str, *, lang: str = "az", title: str = "ABB") -> str:
    """A minimal page with the site's header/footer layout around ``body``."""
    return (
        f'<!DOCTYPE html><html lang="{lang}"><head><title>{title}</title></head><body>'
        '<div><header id="header"><nav aria-label="Main">Fərdi Biznes</nav></header>'
        f"{body}"
        '<footer id="footer"><p>Tel: 937</p></footer></div>'
        "</body></html>"
    )
