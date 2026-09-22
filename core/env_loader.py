"""Load .env from project root when present."""

from __future__ import annotations

import os
from pathlib import Path


def load_env() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return

    root = Path(__file__).resolve().parents[1]
    for path in (root / ".env", root / ".env.local"):
        if path.is_file():
            load_dotenv(path, override=False)

    # Optional user-level fallback
    user_env = Path.home() / ".anammox_lab.env"
    if user_env.is_file():
        load_dotenv(user_env, override=False)

    # Streamlit secrets (if deployed on Streamlit Cloud)
    try:
        import streamlit as st

        secrets = getattr(st, "secrets", None)
        if secrets:
            for key in (
                "OPENAI_API_KEY",
                "ANTHROPIC_API_KEY",
                "DEEPSEEK_API_KEY",
                "PERPLEXITY_API_KEY",
            ):
                if key in secrets and not os.environ.get(key):
                    os.environ[key] = str(secrets[key])
    except Exception:
        pass
