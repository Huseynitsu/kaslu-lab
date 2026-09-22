"""KASLU LAB brand assets, logo helpers, and SEO head injection."""

from __future__ import annotations

import base64
from functools import lru_cache
from pathlib import Path

import streamlit as st

from core.i18n import t

_ASSETS = Path(__file__).resolve().parents[2] / "app" / "assets"
_LOGO_CANDIDATES = (
    _ASSETS / "kaslu-lab-logo.png",
    _ASSETS / "kaslu-lab-logo.svg",
)


@lru_cache(maxsize=1)
def logo_path() -> Path:
    for path in _LOGO_CANDIDATES:
        if path.is_file():
            return path
    return _LOGO_CANDIDATES[-1]


def logo_mime(path: Path | None = None) -> str:
    resolved = path or logo_path()
    if resolved.suffix.lower() == ".png":
        return "image/png"
    return "image/svg+xml"


@lru_cache(maxsize=1)
def logo_data_uri() -> str:
    path = logo_path()
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{logo_mime(path)};base64,{encoded}"


def render_logo_html(*, size: str = "72px", css_class: str = "brand-logo", alt: str | None = None) -> str:
    alt_text = alt or t("brand.title")
    return (
        f'<img class="{css_class}" src="{logo_data_uri()}" '
        f'alt="{alt_text}" width="{size.replace("px", "")}" height="{size.replace("px", "")}" '
        f'style="width:{size};height:{size};" loading="eager" decoding="async" />'
    )


def inject_seo(*, page_title: str | None = None) -> None:
    """Page title is set via st.set_page_config; avoid injecting head tags into the body."""
    _ = page_title or t("brand.title")
