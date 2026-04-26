"""Small helpers for safely rendering dynamic text in raw HTML blocks."""
from html import escape
from typing import Any


def escape_html(value: Any, max_length: int | None = None) -> str:
    """Return a string escaped for insertion into an unsafe_allow_html block."""
    text = "" if value is None else str(value)
    if max_length is not None:
        text = text[:max_length]
    return escape(text, quote=True)
