"""Light / dark theme tokens and CSS for the Streamlit UI."""

from __future__ import annotations

import streamlit as st

THEME_KEY = "ui_theme"

THEMES = {
    "light": {
        "app_bg": "#F4F7FA",
        "surface": "#FFFFFF",
        "surface_alt": "#F8FAFC",
        "sidebar_from": "#FFFFFF",
        "sidebar_to": "#F0F6FC",
        "border": "#D5E3F0",
        "text": "#0F172A",
        "text_muted": "#64748B",
        "heading": "#0B3D6B",
        "primary": "#1565C0",
        "primary_soft": "#E8F2FC",
        "primary_text": "#0D47A1",
        "accent": "#0891B2",
        "kaslu_green": "#059669",
        "shadow": "0 8px 24px rgba(15, 23, 42, 0.06)",
        "toolbar_shadow": "0 2px 8px rgba(15, 23, 42, 0.04)",
        "chart_bg": "#FFFFFF",
        "btn_bg": "#FFFFFF",
        "btn_text": "#0F172A",
        "btn_border": "#CBD5E1",
        "btn_hover": "#F1F5F9",
        "btn_disabled_bg": "#E2E8F0",
        "btn_disabled_text": "#64748B",
        "btn_primary_text": "#FFFFFF",
        "input_bg": "#FFFFFF",
        "input_text": "#0F172A",
        "segment_bg": "#E2E8F0",
        "segment_active_bg": "#FFFFFF",
        "segment_active_text": "#0F172A",
        "segment_inactive_text": "#475569",
    },
    "dark": {
        "app_bg": "#0A0F18",
        "surface": "#121B2B",
        "surface_alt": "#0E1624",
        "sidebar_from": "#0A0F18",
        "sidebar_to": "#101827",
        "border": "#243044",
        "text": "#E2E8F0",
        "text_muted": "#94A3B8",
        "heading": "#7DD3FC",
        "primary": "#3B9EFF",
        "primary_soft": "#0C2340",
        "primary_text": "#BAE6FD",
        "accent": "#22D3EE",
        "kaslu_green": "#34D399",
        "shadow": "0 10px 28px rgba(0, 0, 0, 0.35)",
        "toolbar_shadow": "0 4px 14px rgba(0, 0, 0, 0.25)",
        "chart_bg": "#151F32",
        "btn_bg": "#1E293B",
        "btn_text": "#F8FAFC",
        "btn_border": "#64748B",
        "btn_hover": "#334155",
        "btn_disabled_bg": "#111827",
        "btn_disabled_text": "#64748B",
        "btn_primary_text": "#FFFFFF",
        "input_bg": "#0F172A",
        "input_text": "#F1F5F9",
        "segment_bg": "#1E293B",
        "segment_active_bg": "#334155",
        "segment_active_text": "#F8FAFC",
        "segment_inactive_text": "#CBD5E1",
    },
}


def init_theme(default: str = "light") -> None:
    if THEME_KEY not in st.session_state:
        st.session_state[THEME_KEY] = default


def get_theme() -> str:
    init_theme()
    theme = st.session_state.get(THEME_KEY, "light")
    return theme if theme in THEMES else "light"


def set_theme(theme: str) -> None:
    if theme in THEMES:
        st.session_state[THEME_KEY] = theme


def toggle_theme() -> None:
    set_theme("dark" if get_theme() == "light" else "light")


def apply_matplotlib_theme() -> None:
    try:
        import matplotlib.pyplot as plt

        if get_theme() == "dark":
            plt.style.use("dark_background")
        else:
            plt.style.use("default")
    except Exception:
        pass


def _extra_theme_css(theme_name: str) -> str:
    if theme_name != "dark":
        return """
    .stApp {
        color-scheme: light;
    }
    """
    return """
    .stApp {
        color-scheme: dark;
        --background-color: #0A0F18 !important;
        --secondary-background-color: #121B2B !important;
        --text-color: #E2E8F0 !important;
        --primary-color: #3B82F6 !important;
    }

    html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"], section.main {
        background-color: transparent !important;
        color: #E2E8F0 !important;
    }

    [data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"] {
        background: transparent !important;
    }

    [data-testid="stSidebar"], [data-testid="stSidebar"] > div:first-child {
        background:
            radial-gradient(circle at 1px 1px, rgba(59, 130, 246, 0.18) 1.5px, transparent 0),
            linear-gradient(180deg, #0A0F18 0%, #101827 100%) !important;
        background-size: 20px 20px, auto !important;
    }

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] small {
        color: #E2E8F0 !important;
    }

    [data-testid="stWidgetLabel"] p,
    [data-testid="stWidgetLabel"] label,
    label[data-testid="stWidgetLabel"],
    [data-testid="stWidgetLabel"] span {
        color: #E2E8F0 !important;
    }

    [data-testid="stVerticalBlockBorderWrapper"],
    [data-testid="stVerticalBlockBorderWrapper"] > div,
    div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stVerticalBlock"] {
        background-color: #151F32 !important;
        border-color: #475569 !important;
    }

    [data-testid="stVerticalBlockBorderWrapper"] p,
    [data-testid="stVerticalBlockBorderWrapper"] span,
    [data-testid="stVerticalBlockBorderWrapper"] label,
    [data-testid="stVerticalBlockBorderWrapper"] h1,
    [data-testid="stVerticalBlockBorderWrapper"] h2,
    [data-testid="stVerticalBlockBorderWrapper"] h3 {
        color: #E2E8F0 !important;
    }

    .stButton > button[kind="secondary"],
    .stButton > button[data-testid="baseButton-secondary"],
    button[data-testid="baseButton-secondary"],
    [data-testid="baseButton-secondary"] {
        background-color: #1E293B !important;
        color: #F8FAFC !important;
        border: 1px solid #64748B !important;
    }

    .stButton > button[kind="secondary"] p,
    .stButton > button[kind="secondary"] span,
    button[data-testid="baseButton-secondary"] p,
    button[data-testid="baseButton-secondary"] span {
        color: #F8FAFC !important;
    }

    div[data-baseweb="base-input"],
    div[data-baseweb="input"],
    div[data-baseweb="select"] > div,
    div[data-baseweb="select"] span,
    div[data-baseweb="select"] div[value] {
        background-color: #0F172A !important;
        color: #F1F5F9 !important;
        border-color: #475569 !important;
    }

    div[data-baseweb="select"] input {
        color: #F1F5F9 !important;
        -webkit-text-fill-color: #F1F5F9 !important;
    }

    .stTextInput input, .stNumberInput input, textarea, input[type="password"] {
        background-color: #0F172A !important;
        color: #F1F5F9 !important;
        -webkit-text-fill-color: #F1F5F9 !important;
        border-color: #475569 !important;
    }

    .stNumberInput button,
    .stTextInput button {
        background-color: #1E293B !important;
        color: #F8FAFC !important;
        border-color: #64748B !important;
    }

    div[data-baseweb="popover"],
    div[data-baseweb="popover"] > div,
    ul[data-baseweb="menu"] {
        background-color: #151F32 !important;
        border-color: #475569 !important;
    }

    div[data-baseweb="popover"] li,
    ul[data-baseweb="menu"] li {
        background-color: #151F32 !important;
        color: #E2E8F0 !important;
    }

    div[data-baseweb="popover"] li:hover,
    ul[data-baseweb="menu"] li:hover {
        background-color: #334155 !important;
    }

    [data-testid="stAlert"],
    [data-testid="stAlert"] > div,
    div[data-testid="stNotification"],
    div[data-testid="stNotification"] > div {
        background-color: #111827 !important;
        color: #E2E8F0 !important;
        border: 1px solid #475569 !important;
    }

    [data-testid="stAlert"] p,
    [data-testid="stAlert"] span,
    div[data-testid="stNotification"] p,
    div[data-testid="stNotification"] span {
        color: #E2E8F0 !important;
    }

    [data-testid="stInfo"] {
        background-color: #172554 !important;
        color: #DBEAFE !important;
        border: 1px solid #1D4ED8 !important;
    }

    [data-testid="stWarning"] {
        background-color: #422006 !important;
        color: #FDE68A !important;
        border: 1px solid #B45309 !important;
    }

    [data-testid="stSuccess"] {
        background-color: #052E16 !important;
        color: #BBF7D0 !important;
        border: 1px solid #15803D !important;
    }

    [data-testid="stError"] {
        background-color: #450A0A !important;
        color: #FECACA !important;
        border: 1px solid #B91C1C !important;
    }

    [data-testid="stInfo"] p, [data-testid="stWarning"] p,
    [data-testid="stSuccess"] p, [data-testid="stError"] p {
        color: inherit !important;
    }

    [data-testid="stDataFrame"] [data-testid="stTable"],
    [data-testid="stTable"],
    [data-testid="stDataFrame"] div[data-testid="glideDataEditor"] {
        background-color: #151F32 !important;
    }

    [data-testid="stDataFrame"] table thead tr th,
    [data-testid="stTable"] thead tr th {
        background-color: #1E293B !important;
        color: #E2E8F0 !important;
    }

    [data-testid="stDataFrame"] table tbody tr td,
    [data-testid="stTable"] tbody tr td {
        background-color: #151F32 !important;
        color: #E2E8F0 !important;
    }

    .stRadio div[role="radiogroup"] > label[data-baseweb="radio"] {
        background-color: #1E293B !important;
        border: 1px solid #64748B !important;
        color: #F8FAFC !important;
    }

    .stRadio div[role="radiogroup"] > label[data-baseweb="radio"] p,
    .stRadio div[role="radiogroup"] > label[data-baseweb="radio"] span {
        color: #F8FAFC !important;
    }

    .stRadio div[role="radiogroup"] > label[data-baseweb="radio"]:has(input:checked) {
        background-color: #1E3A5F !important;
        border-color: #3B82F6 !important;
    }

    .stRadio div[role="radiogroup"] > label[data-baseweb="radio"]:has(input:checked) p,
    .stRadio div[role="radiogroup"] > label[data-baseweb="radio"]:has(input:checked) span {
        color: #BFDBFE !important;
    }

    div[data-testid="stExpander"] details summary,
    div[data-testid="stExpander"] details summary span,
    div[data-testid="stExpander"] .streamlit-expanderContent,
    div[data-testid="stExpander"] .streamlit-expanderContent p {
        color: #E2E8F0 !important;
    }

    .stJson, pre, code, .stCodeBlock, [data-testid="stCodeBlock"] {
        background-color: #0F172A !important;
        color: #E2E8F0 !important;
        border: 1px solid #475569 !important;
    }

    .stProgress > div > div > div {
        background-color: #3B82F6 !important;
    }

    .stProgress > div > div {
        background-color: #334155 !important;
    }

    .stTabs [data-baseweb="tab-list"] button {
        background-color: #1E293B !important;
        color: #E2E8F0 !important;
    }

    .stTabs [aria-selected="true"] {
        background-color: #1E3A5F !important;
        color: #BFDBFE !important;
    }

    [data-testid="stMetric"] {
        background-color: #151F32 !important;
        border-color: #475569 !important;
    }

    [data-testid="stMetricLabel"] {
        color: #94A3B8 !important;
    }

    [data-testid="stMetricValue"] {
        color: #F8FAFC !important;
    }
    """


def _theme_css(theme_name: str) -> str:
    t = THEMES[theme_name]
    extra = _extra_theme_css(theme_name)
    return f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,400;0,500;0,600;0,700;0,800;1,400&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@24,400,0,0&display=block');

    html, body, .stApp, [data-testid="stAppViewContainer"],
    [data-testid="stSidebar"], section.main,
    p, label, input, textarea, select, option,
    h1, h2, h3, h4, h5, h6,
    [data-testid="stMarkdownContainer"],
    .stButton > button,
    .stTextInput input, .stNumberInput input,
    div[data-baseweb="select"] {{
        font-family: 'Plus Jakarta Sans', system-ui, -apple-system, 'Segoe UI', sans-serif !important;
    }}

    /* Streamlit Material Symbols — must not inherit UI font (ligatures become plain text). */
    [data-testid="stIconMaterial"],
    [data-testid="stIconMaterial"] span,
    [data-testid="collapsedControl"] span,
    [data-testid="stSidebarCollapseButton"] span,
    div[data-testid="stExpander"] details summary [data-testid="stIconMaterial"] {{
        font-family: 'Material Symbols Rounded', 'Material Icons' !important;
        font-weight: normal !important;
        font-style: normal !important;
        font-size: 1.25rem !important;
        line-height: 1 !important;
        letter-spacing: normal !important;
        text-transform: none !important;
        white-space: nowrap !important;
        word-wrap: normal !important;
        direction: ltr !important;
        font-feature-settings: 'liga' !important;
        -webkit-font-smoothing: antialiased;
        font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24 !important;
    }}

    {extra}
    :root {{
        --app-bg: {t["app_bg"]};
        --surface: {t["surface"]};
        --surface-alt: {t["surface_alt"]};
        --border: {t["border"]};
        --text: {t["text"]};
        --text-muted: {t["text_muted"]};
        --heading: {t["heading"]};
        --primary: {t["primary"]};
        --primary-soft: {t["primary_soft"]};
        --primary-text: {t["primary_text"]};
        --accent: {t["accent"]};
        --shadow: {t["shadow"]};
        --toolbar-shadow: {t["toolbar_shadow"]};
        --btn-bg: {t["btn_bg"]};
        --btn-text: {t["btn_text"]};
        --btn-border: {t["btn_border"]};
        --btn-hover: {t["btn_hover"]};
        --btn-disabled-bg: {t["btn_disabled_bg"]};
        --btn-disabled-text: {t["btn_disabled_text"]};
        --btn-primary-text: {t["btn_primary_text"]};
        --input-bg: {t["input_bg"]};
        --input-text: {t["input_text"]};
        --segment-bg: {t["segment_bg"]};
        --segment-active-bg: {t["segment_active_bg"]};
        --segment-active-text: {t["segment_active_text"]};
        --segment-inactive-text: {t["segment_inactive_text"]};
        --kaslu-green: {t["kaslu_green"]};
        /* Base fill is --app-bg; mesh + dots are painted in .stApp::before (scaled by --pattern-opacity). */
        --pattern-opacity: 0.38;
        --pattern-dot-strength: 18%;
    }}

    @media (prefers-reduced-motion: reduce) {{
        *, *::before, *::after {{
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
        }}
    }}

    .stApp {{
        background: var(--app-bg) !important;
        color: var(--text);
        position: relative;
        isolation: isolate;
    }}

    @keyframes meshDrift {{
        0%, 100% {{ background-position: 0 0, 0% 0%, 100% 0%, 80% 100%, 0 0; }}
        50% {{ background-position: 11px 11px, 4% 6%, 96% 4%, 75% 95%, 0 0; }}
    }}

    @keyframes orbFloat {{
        0% {{ transform: translate3d(0, 0, 0) scale(1); }}
        100% {{ transform: translate3d(0, -8px, 0) scale(1.02); }}
    }}

    @keyframes fadeSlideUp {{
        from {{ opacity: 0; transform: translateY(14px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}

    @keyframes accentShimmer {{
        0% {{ background-position: -120% center; }}
        100% {{ background-position: 220% center; }}
    }}

    @keyframes statusPulse {{
        0%, 100% {{ opacity: 1; transform: scale(1); }}
        50% {{ opacity: 0.55; transform: scale(0.88); }}
    }}

    .stApp::before {{
        content: "";
        position: fixed;
        inset: 0;
        z-index: 0;
        pointer-events: none;
        opacity: var(--pattern-opacity);
        background:
            radial-gradient(
                circle at 1px 1px,
                color-mix(in srgb, var(--primary) var(--pattern-dot-strength), transparent) 1.25px,
                transparent 0
            ),
            linear-gradient(
                135deg,
                color-mix(in srgb, var(--primary) 3%, var(--app-bg)) 0%,
                transparent 48%,
                color-mix(in srgb, var(--accent) 2.5%, var(--app-bg)) 100%
            ),
            radial-gradient(ellipse 65% 45% at 8% 12%, rgba(21, 101, 192, 0.06), transparent 55%),
            radial-gradient(ellipse 55% 40% at 92% 8%, rgba(8, 145, 178, 0.05), transparent 50%),
            radial-gradient(ellipse 45% 35% at 85% 95%, rgba(5, 150, 105, 0.04), transparent 45%);
        background-size: 20px 20px, auto, auto, auto, auto;
        animation: meshDrift 22s ease-in-out infinite;
    }}

    .stApp::after {{
        content: "";
        position: fixed;
        inset: 0;
        z-index: 0;
        pointer-events: none;
        opacity: calc(var(--pattern-opacity) * 0.75);
        background:
            radial-gradient(circle at 18% 78%, rgba(8, 145, 178, 0.06), transparent 38%),
            radial-gradient(circle at 82% 18%, rgba(21, 101, 192, 0.06), transparent 36%);
        animation: orbFloat 14s ease-in-out infinite alternate;
    }}

    [data-testid="stAppViewContainer"],
    [data-testid="stMain"],
    section.main {{
        position: relative;
        z-index: 1;
        background: transparent !important;
    }}

    section.main .block-container,
    [data-testid="stMain"] .block-container {{
        margin-bottom: 0 !important;
    }}

    .main .block-container {{
        padding-top: 1.25rem;
        max-width: min(1180px, 100%);
        padding-left: clamp(0.75rem, 2vw, 1.5rem);
        padding-right: clamp(0.75rem, 2vw, 1.5rem);
        padding-bottom: 1.5rem;
        color: var(--text);
        background: color-mix(in srgb, var(--surface) 78%, transparent);
        border: 1px solid color-mix(in srgb, var(--border) 85%, transparent);
        border-radius: 18px;
        box-shadow: 0 8px 32px rgba(15, 23, 42, 0.04);
        backdrop-filter: blur(6px);
    }}

    [data-testid="stSidebarNav"] {{ display: none !important; }}

    [data-testid="stAppViewContainer"] {{
        background: transparent !important;
    }}

    [data-testid="stSidebar"],
    [data-testid="stSidebar"] > div:first-child {{
        background:
            radial-gradient(
                circle at 1px 1px,
                color-mix(in srgb, var(--primary) var(--pattern-dot-strength), transparent) 1.25px,
                transparent 0
            ),
            radial-gradient(ellipse 50% 40% at 0% 0%, rgba(21, 101, 192, 0.10), transparent 55%),
            linear-gradient(180deg, color-mix(in srgb, var(--surface) 92%, transparent) 0%, {t["sidebar_to"]} 100%) !important;
        background-size: 20px 20px, auto, auto !important;
        border-right: 1px solid var(--border);
        color: var(--text);
    }}

    h1, h2, h3, h4, h5, h6 {{
        color: var(--heading) !important;
        letter-spacing: -0.02em;
    }}

    section.main h1 {{
        font-size: clamp(1.45rem, 3vw, 1.85rem) !important;
        font-weight: 700 !important;
        padding-bottom: 0.55rem;
        margin-bottom: 0.15rem !important;
        border-bottom: 2px solid transparent;
        border-image: linear-gradient(90deg, var(--primary), var(--accent), transparent) 1;
    }}

    section.main h2, section.main h3 {{
        font-weight: 600 !important;
    }}

    section.main .stCaption {{
        color: var(--text-muted) !important;
        font-size: 0.92rem;
        line-height: 1.55;
        margin-bottom: 0.75rem;
    }}

    .stMarkdown, .stMarkdown p, .stCaption {{
        color: var(--text);
    }}

    .stMarkdown .user-chip, .app-top-bar .user-chip {{
        color: var(--text-muted) !important;
    }}

    .stMarkdown .user-chip strong {{
        color: var(--text) !important;
    }}

    /* ---- Buttons (fix white bg + light text in dark mode) ---- */
    .stButton > button,
    [data-testid="stSidebar"] .stButton > button,
    .stFormSubmitButton > button {{
        background-color: var(--btn-bg) !important;
        color: var(--btn-text) !important;
        border: 1px solid var(--btn-border) !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        transition: background-color 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease;
    }}

    .stButton > button:hover,
    [data-testid="stSidebar"] .stButton > button:hover,
    .stFormSubmitButton > button:hover {{
        background-color: var(--btn-hover) !important;
        color: var(--btn-text) !important;
        border-color: var(--primary) !important;
        box-shadow: 0 4px 16px rgba(21, 101, 192, 0.18);
        transform: translateY(-2px);
    }}

    .stButton > button:active,
    [data-testid="stSidebar"] .stButton > button:active {{
        transform: translateY(0) scale(0.98);
        box-shadow: 0 1px 6px rgba(21, 101, 192, 0.12);
    }}

    .stButton > button p,
    .stButton > button span,
    .stButton > button div,
    [data-testid="stSidebar"] .stButton > button p,
    [data-testid="stSidebar"] .stButton > button span,
    .stFormSubmitButton > button p,
    .stFormSubmitButton > button span {{
        color: var(--btn-text) !important;
    }}

    .stButton > button[kind="primary"],
    .stButton > button[data-testid="baseButton-primary"],
    .stFormSubmitButton > button[kind="primaryFormSubmit"],
    .stFormSubmitButton > button[data-testid="baseButton-primary"] {{
        background: linear-gradient(135deg, var(--primary), var(--accent), var(--kaslu-green)) !important;
        color: var(--btn-primary-text) !important;
        border: 1px solid transparent !important;
    }}

    .stButton > button[kind="primary"]:hover,
    .stButton > button[data-testid="baseButton-primary"]:hover,
    .stFormSubmitButton > button[kind="primaryFormSubmit"]:hover {{
        filter: brightness(1.06);
        box-shadow: 0 4px 16px rgba(38, 198, 218, 0.28);
        color: var(--btn-primary-text) !important;
    }}

    .stButton > button[kind="primary"] p,
    .stButton > button[kind="primary"] span,
    .stButton > button[kind="primary"] div,
    .stButton > button[data-testid="baseButton-primary"] p,
    .stButton > button[data-testid="baseButton-primary"] span,
    .stFormSubmitButton > button[kind="primaryFormSubmit"] p,
    .stFormSubmitButton > button[kind="primaryFormSubmit"] span {{
        color: var(--btn-primary-text) !important;
    }}

    .stButton > button:disabled,
    [data-testid="stSidebar"] .stButton > button:disabled {{
        background-color: var(--btn-disabled-bg) !important;
        color: var(--btn-disabled-text) !important;
        border-color: var(--border) !important;
        opacity: 0.85;
    }}

    .stButton > button:disabled p,
    .stButton > button:disabled span {{
        color: var(--btn-disabled-text) !important;
    }}

    /* ---- Segmented control (theme toggle) ---- */
    div[data-testid="stSegmentedControl"] {{
        background: var(--segment-bg) !important;
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
        padding: 2px !important;
    }}

    div[data-testid="stSegmentedControl"] button {{
        background: transparent !important;
        color: var(--segment-inactive-text) !important;
        border: none !important;
        font-weight: 600 !important;
    }}

    div[data-testid="stSegmentedControl"] button[aria-checked="true"],
    div[data-testid="stSegmentedControl"] button[aria-selected="true"] {{
        background: var(--segment-active-bg) !important;
        color: var(--segment-active-text) !important;
        box-shadow: var(--toolbar-shadow);
    }}

    div[data-testid="stSegmentedControl"] button p,
    div[data-testid="stSegmentedControl"] button span {{
        color: inherit !important;
    }}

    /* ---- Inputs ---- */
    .stTextInput label,
    .stNumberInput label,
    .stSelectbox label,
    .stTextArea label,
    .stSlider label,
    .stRadio > label,
    .stCheckbox label {{
        color: var(--text) !important;
    }}

    .stTextInput input,
    .stNumberInput input,
    textarea,
    input[type="password"] {{
        background-color: var(--input-bg) !important;
        color: var(--input-text) !important;
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
    }}

    .stTextInput input::placeholder,
    .stNumberInput input::placeholder {{
        color: var(--text-muted) !important;
        opacity: 1;
    }}

    div[data-baseweb="select"] > div,
    div[data-baseweb="popover"] > div {{
        background-color: var(--input-bg) !important;
        color: var(--input-text) !important;
        border-color: var(--border) !important;
    }}

    div[data-baseweb="popover"] li {{
        background-color: var(--surface) !important;
        color: var(--text) !important;
    }}

    div[data-baseweb="popover"] li:hover {{
        background-color: var(--btn-hover) !important;
    }}

    /* ---- Radio (login Mode selector) ---- */
    .stRadio > div {{
        gap: 0.5rem;
    }}

    .stRadio label {{
        background-color: var(--btn-bg) !important;
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
        padding: 0.35rem 0.75rem !important;
        color: var(--btn-text) !important;
    }}

    .stRadio label:hover {{
        background-color: var(--btn-hover) !important;
    }}

    .stRadio label[data-baseweb="radio"] > div:first-child {{
        background-color: var(--surface-alt) !important;
        border-color: var(--border) !important;
    }}

    .stRadio div[role="radiogroup"] label p,
    .stRadio div[role="radiogroup"] label span,
    .stRadio div[role="radiogroup"] label div[data-testid="stMarkdownContainer"] p {{
        color: var(--btn-text) !important;
    }}

    /* ---- Checkbox / slider ---- */
    .stCheckbox span {{
        color: var(--text) !important;
    }}

    .stSlider [data-baseweb="slider"] div {{
        color: var(--text) !important;
    }}

    /* ---- Sidebar width ---- */
    section[data-testid="stSidebar"],
    section[data-testid="stSidebar"] > div {{
        min-width: 19rem !important;
        width: 19rem !important;
    }}

    section[data-testid="stSidebar"] .stRadio label {{
        font-size: 0.82rem !important;
        padding: 0.3rem 0.55rem !important;
    }}

    /* ---- Cards & chrome ---- */
    .app-brand {{
        background: color-mix(in srgb, var(--surface) 90%, transparent);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 0.85rem 0.9rem;
        margin-bottom: 0.75rem;
        box-shadow: var(--toolbar-shadow);
        transition: border-color 0.2s ease, box-shadow 0.2s ease;
        backdrop-filter: blur(4px);
    }}

    .app-brand:hover {{
        border-color: rgba(38, 198, 218, 0.45);
        box-shadow: 0 4px 18px rgba(21, 101, 192, 0.10);
    }}

    .app-brand .brand-logo-row {{
        display: flex;
        align-items: center;
        gap: 0.65rem;
        margin-bottom: 0.45rem;
    }}

    .brand-logo-emblem {{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
        padding: 0.15rem;
        border-radius: 14px;
        background: linear-gradient(
            145deg,
            color-mix(in srgb, var(--primary) 12%, var(--surface)),
            color-mix(in srgb, var(--accent) 10%, var(--surface))
        );
        box-shadow:
            0 4px 14px rgba(21, 101, 192, 0.18),
            inset 0 1px 0 color-mix(in srgb, white 40%, transparent);
        transition: transform 0.25s ease, box-shadow 0.25s ease;
    }}

    .app-brand:hover .brand-logo-emblem {{
        transform: scale(1.06);
        box-shadow:
            0 6px 20px rgba(21, 101, 192, 0.24),
            inset 0 1px 0 color-mix(in srgb, white 45%, transparent);
    }}

    .brand-logo {{
        display: block;
        border-radius: 12px;
        flex-shrink: 0;
        filter: drop-shadow(0 3px 8px rgba(13, 71, 161, 0.35));
        transform: scale(1.04);
    }}

    .app-brand .brand-title {{
        font-size: 1rem;
        font-weight: 700;
        color: var(--heading) !important;
        margin: 0 0 0.15rem;
        line-height: 1.3;
        text-align: left !important;
    }}

    .app-brand .brand-sub {{
        font-size: 0.78rem;
        color: var(--text-muted);
        margin: 0.15rem 0 0 0;
        text-align: left !important;
    }}

    .app-brand .brand-accent {{
        height: 3px;
        border-radius: 999px;
        margin-top: 0.65rem;
        background: linear-gradient(90deg, var(--primary), var(--accent), var(--kaslu-green));
    }}

    .kaslu-topbar-marker {{
        display: none !important;
    }}

    [class*="st-key-app_top_bar"] {{
        margin-bottom: 1rem;
        animation: fadeSlideUp 0.45s ease-out;
    }}

    [class*="st-key-app_top_bar"] [data-testid="stVerticalBlockBorderWrapper"] {{
        background: linear-gradient(
            118deg,
            color-mix(in srgb, var(--surface) 96%, var(--primary)) 0%,
            color-mix(in srgb, var(--surface) 92%, var(--accent)) 55%,
            color-mix(in srgb, var(--surface) 94%, transparent) 100%
        );
        border: 1px solid color-mix(in srgb, var(--primary) 22%, var(--border)) !important;
        border-radius: 16px !important;
        padding: 0.55rem 1rem !important;
        box-shadow:
            0 4px 20px rgba(15, 23, 42, 0.06),
            inset 0 1px 0 color-mix(in srgb, white 35%, transparent);
        transition: border-color 0.25s ease, box-shadow 0.25s ease, transform 0.25s ease;
    }}

    [class*="st-key-app_top_bar"]:hover [data-testid="stVerticalBlockBorderWrapper"] {{
        border-color: color-mix(in srgb, var(--accent) 35%, var(--border)) !important;
        box-shadow: 0 6px 24px rgba(21, 101, 192, 0.12);
    }}

    [class*="st-key-app_top_bar"] [data-testid="stVerticalBlockBorderWrapper"] > div {{
        align-items: center !important;
    }}

    [class*="st-key-app_top_bar"] [data-testid="stHorizontalBlock"] {{
        align-items: center !important;
        flex-wrap: nowrap !important;
        gap: 0.5rem !important;
        row-gap: 0 !important;
    }}

    [class*="st-key-app_top_bar"] [data-testid="stHorizontalBlock"] > div[data-testid="column"] {{
        flex: 1 1 auto !important;
        min-width: 0 !important;
        max-width: none !important;
        align-self: center !important;
    }}

    [class*="st-key-app_top_bar"] [data-testid="column"]:has([class*="st-key-top_home"]) {{
        flex: 0 0 auto !important;
        min-width: 0 !important;
        max-width: none !important;
        width: auto !important;
    }}

    [class*="st-key-app_top_bar"] [data-testid="column"]:has([class*="st-key-top_home"]) [data-testid="stHorizontalBlock"] {{
        flex-wrap: nowrap !important;
        gap: 0.35rem !important;
        align-items: center !important;
        width: auto !important;
    }}

    [class*="st-key-app_top_bar"] [data-testid="column"]:has(.topbar-page-title) {{
        flex: 1 1 auto !important;
        min-width: 0 !important;
    }}

    [class*="st-key-app_top_bar"] [data-testid="column"] {{
        display: flex !important;
        align-items: center !important;
        justify-content: flex-start !important;
    }}

    [class*="st-key-app_top_bar"] [data-testid="column"]:last-child {{
        justify-content: flex-end !important;
    }}

    [class*="st-key-app_top_bar"] [data-testid="element-container"],
    [class*="st-key-app_top_bar"] [data-testid="stElementContainer"] {{
        margin-bottom: 0 !important;
        margin-top: 0 !important;
        display: flex !important;
        align-items: center !important;
        width: 100%;
    }}

    [class*="st-key-app_top_bar"] [data-testid="column"] [data-testid="stVerticalBlock"] {{
        justify-content: center !important;
        gap: 0 !important;
    }}

    [class*="st-key-app_top_bar"] [data-testid="column"] [data-testid="stHorizontalBlock"] {{
        flex-wrap: nowrap !important;
        width: 100%;
    }}

    [class*="st-key-app_top_bar"] [data-testid="column"]:last-child [data-testid="stHorizontalBlock"] > div[data-testid="column"] {{
        flex: 1 1 0 !important;
        min-width: 0 !important;
        overflow: visible !important;
    }}

    [class*="st-key-app_top_bar"] [data-testid="column"]:last-child [data-testid="stHorizontalBlock"] > div[data-testid="column"]:has([class*="st-key-top_theme_segment"]) {{
        flex: 0 1 auto !important;
        min-width: 7.25rem !important;
        overflow: visible !important;
    }}

    [class*="st-key-app_top_bar"] [data-testid="column"]:last-child [data-testid="stHorizontalBlock"] > div[data-testid="column"]:has([class*="st-key-top_logout"]) {{
        flex: 1 1 auto !important;
        min-width: 5.5rem !important;
    }}

    [class*="st-key-app_top_bar"] .stButton > button {{
        min-height: 2.35rem !important;
        max-height: 2.35rem !important;
        padding: 0.35rem 0.65rem !important;
        font-size: 0.82rem !important;
        transition: transform 0.18s ease, box-shadow 0.18s ease, background-color 0.18s ease, border-color 0.18s ease !important;
    }}

    [class*="st-key-app_top_bar"] [class*="st-key-top_home"] .stButton > button,
    [class*="st-key-app_top_bar"] [class*="st-key-top_back"] .stButton > button {{
        padding: 0 !important;
    }}

    [class*="st-key-app_top_bar"] .stButton > button:hover:not(:disabled) {{
        transform: translateY(-1px);
    }}

    [class*="st-key-app_top_bar"] .stButton > button[kind="secondary"]:disabled {{
        opacity: 1 !important;
        background: var(--primary-soft) !important;
        border-color: color-mix(in srgb, var(--primary) 35%, var(--border)) !important;
        color: var(--primary-text) !important;
        cursor: default !important;
    }}

    [class*="st-key-app_top_bar"] [data-testid="stMarkdownContainer"] {{
        display: flex !important;
        align-items: center !important;
        margin: 0 !important;
        padding: 0 !important;
        width: 100%;
    }}

    /* Top bar icon-only nav (Home / Back) */
    [class*="st-key-top_home"] [data-testid="element-container"],
    [class*="st-key-top_back"] [data-testid="element-container"],
    [class*="st-key-top_home"] [data-testid="stElementContainer"],
    [class*="st-key-top_back"] [data-testid="stElementContainer"] {{
        width: 2.35rem !important;
        min-width: 2.35rem !important;
        max-width: 2.35rem !important;
        flex: 0 0 2.35rem !important;
    }}

    [class*="st-key-top_home"] .stButton,
    [class*="st-key-top_back"] .stButton {{
        width: 2.35rem !important;
        min-width: 2.35rem !important;
        max-width: 2.35rem !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
    }}

    [class*="st-key-top_home"] .stButton > button,
    [class*="st-key-top_back"] .stButton > button {{
        width: 2.35rem !important;
        min-width: 2.35rem !important;
        max-width: 2.35rem !important;
        height: 2.35rem !important;
        min-height: 2.35rem !important;
        max-height: 2.35rem !important;
        padding: 0 !important;
        margin: 0 !important;
        position: relative !important;
        line-height: 0 !important;
        border-radius: 10px !important;
        border: 1px solid var(--btn-border) !important;
        background: var(--btn-bg) !important;
        display: grid !important;
        place-items: center !important;
        box-sizing: border-box !important;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.06) !important;
        transition: transform 0.18s ease, box-shadow 0.18s ease, background-color 0.18s ease, border-color 0.18s ease !important;
    }}

    [class*="st-key-top_home"] .stButton > button > div,
    [class*="st-key-top_back"] .stButton > button > div {{
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        width: 100% !important;
        height: 100% !important;
        margin: 0 !important;
        padding: 0 !important;
        gap: 0 !important;
        min-width: 0 !important;
        position: relative !important;
    }}

    [class*="st-key-top_home"] .stButton > button p,
    [class*="st-key-top_back"] .stButton > button p {{
        display: none !important;
    }}

    [class*="st-key-top_home"] .stButton > button [data-testid="stIconMaterial"],
    [class*="st-key-top_back"] .stButton > button [data-testid="stIconMaterial"],
    [class*="st-key-top_home"] .stButton > button [data-testid="stIconMaterial"] span,
    [class*="st-key-top_back"] .stButton > button [data-testid="stIconMaterial"] span {{
        margin: 0 !important;
        padding: 0 !important;
        width: 1.15rem !important;
        height: 1.15rem !important;
        font-size: 1.15rem !important;
        line-height: 1 !important;
        position: absolute !important;
        left: 50% !important;
        top: 50% !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        transform: translate(-50%, -50%) !important;
        transition: transform 0.18s ease !important;
    }}

    [class*="st-key-top_home"] .stButton > button:hover,
    [class*="st-key-top_back"] .stButton > button:hover {{
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(21, 101, 192, 0.14) !important;
        border-color: color-mix(in srgb, var(--primary) 40%, var(--border)) !important;
        background: var(--btn-hover) !important;
    }}

    [class*="st-key-top_home"] .stButton > button:hover [data-testid="stIconMaterial"],
    [class*="st-key-top_back"] .stButton > button:hover [data-testid="stIconMaterial"],
    [class*="st-key-top_home"] .stButton > button:hover [data-testid="stIconMaterial"] span,
    [class*="st-key-top_back"] .stButton > button:hover [data-testid="stIconMaterial"] span {{
        transform: translate(-50%, calc(-50% - 1px)) !important;
    }}

    [class*="st-key-top_home"] .stButton > button:active,
    [class*="st-key-top_back"] .stButton > button:active {{
        transform: translateY(0) scale(0.97) !important;
    }}

    .topbar-page-title {{
        display: inline-flex;
        align-items: center;
        justify-content: flex-start;
        gap: 0.45rem;
        font-size: clamp(0.95rem, 2.2vw, 1.08rem);
        font-weight: 700;
        color: var(--heading) !important;
        margin: 0 !important;
        padding: 0.15rem 0;
        letter-spacing: -0.02em;
        line-height: 1.2 !important;
        min-height: 2.25rem;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 100%;
    }}

    .topbar-account {{
        display: inline-flex;
        align-items: center;
        gap: 0.55rem;
        max-width: 100%;
        min-height: 2.35rem;
        padding: 0.35rem 0.65rem 0.35rem 0.35rem;
        background: color-mix(in srgb, var(--surface-alt) 78%, var(--primary));
        border: 1px solid color-mix(in srgb, var(--border) 88%, var(--primary));
        border-radius: 12px;
        box-sizing: border-box;
    }}

    .topbar-account-avatar {{
        flex-shrink: 0;
        width: 1.75rem;
        height: 1.75rem;
        border-radius: 9px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 0.78rem;
        font-weight: 800;
        color: var(--btn-primary-text) !important;
        background: linear-gradient(145deg, var(--primary), var(--accent));
        box-shadow: 0 2px 8px rgba(21, 101, 192, 0.22);
    }}

    .topbar-account-text {{
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        justify-content: center;
        min-width: 0;
        line-height: 1.15;
    }}

    .topbar-account-label {{
        font-size: 0.62rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        line-height: 1.2;
        color: var(--text-muted) !important;
    }}

    .topbar-account-name {{
        font-size: 0.82rem;
        font-weight: 700;
        color: var(--text) !important;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 11rem;
    }}

    @media (max-width: 768px) {{
        .topbar-account-label {{
            display: none;
        }}

        .topbar-account {{
            padding: 0.35rem 0.55rem 0.35rem 0.35rem;
        }}

        .topbar-account-name {{
            max-width: 6.5rem;
        }}

        [class*="st-key-top_theme_segment"] button {{
            padding: 0.28rem 0.35rem !important;
            font-size: 0.68rem !important;
        }}
    }}

    [class*="st-key-app_top_bar"] [data-testid="column"]:last-child [data-testid="stHorizontalBlock"] > div[data-testid="column"]:first-child {{
        flex: 1 1 auto !important;
        min-width: 0 !important;
        overflow: visible !important;
    }}

    [class*="st-key-top_theme_segment"] [data-testid="element-container"],
    [class*="st-key-top_theme_segment"] [data-testid="stElementContainer"] {{
        margin: 0 !important;
        width: auto !important;
        min-width: 7rem !important;
        overflow: visible !important;
    }}

    [class*="st-key-top_theme_segment"] [data-testid="stButtonGroup"],
    [class*="st-key-top_theme_segment"] [role="group"] {{
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        align-items: stretch !important;
        min-height: 2.35rem !important;
        width: auto !important;
        min-width: 7rem !important;
        overflow: visible !important;
    }}

    [class*="st-key-top_theme_segment"] button {{
        min-height: 2.35rem !important;
        font-size: 0.72rem !important;
        font-weight: 600 !important;
        padding: 0.28rem 0.55rem !important;
        border-radius: 8px !important;
        flex: 1 1 0 !important;
        white-space: nowrap !important;
    }}

    [class*="st-key-top_theme_segment"] button[aria-pressed="true"],
    [class*="st-key-top_theme_segment"] button[aria-checked="true"] {{
        background: color-mix(in srgb, var(--primary) 14%, var(--btn-bg)) !important;
        color: var(--primary-text) !important;
        border-color: color-mix(in srgb, var(--primary) 38%, var(--border)) !important;
        box-shadow: inset 0 1px 0 color-mix(in srgb, white 25%, transparent) !important;
    }}

    [class*="st-key-top_logout"] .stButton > button {{
        font-size: 0.68rem !important;
        font-weight: 600 !important;
        padding: 0.32rem 0.45rem !important;
        white-space: nowrap !important;
        overflow: visible !important;
        text-overflow: clip !important;
        min-width: 0 !important;
        min-height: 2.35rem !important;
        max-height: 2.35rem !important;
        width: 100% !important;
        border-color: color-mix(in srgb, var(--kaslu-green) 45%, var(--border)) !important;
        background: color-mix(in srgb, var(--kaslu-green) 8%, var(--btn-bg)) !important;
    }}

    [class*="st-key-top_logout"] .stButton > button p,
    [class*="st-key-top_logout"] .stButton > button span {{
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
    }}

    [class*="st-key-top_logout"] .stButton > button:hover {{
        border-color: var(--kaslu-green) !important;
        background: color-mix(in srgb, var(--kaslu-green) 16%, var(--btn-bg)) !important;
    }}

    .sidebar-nav-divider {{
        height: 1px;
        margin: 0.28rem 0.35rem;
        background: linear-gradient(
            90deg,
            transparent 0%,
            color-mix(in srgb, var(--border) 95%, var(--primary)) 18%,
            color-mix(in srgb, var(--border) 95%, var(--primary)) 82%,
            transparent 100%
        );
        opacity: 0.9;
    }}

    .nav-current {{
        background: linear-gradient(90deg, var(--primary-soft), color-mix(in srgb, var(--accent) 14%, var(--surface)));
        color: var(--primary-text) !important;
        border-radius: 10px;
        padding: 0.42rem 0.6rem;
        font-size: 0.8rem;
        font-weight: 600;
        margin: 0.06rem 0 !important;
        text-align: left !important;
        border: 1px solid color-mix(in srgb, var(--primary) 30%, var(--border));
        border-left: 3px solid var(--primary);
        box-shadow: inset 0 1px 0 color-mix(in srgb, white 25%, transparent);
        white-space: nowrap !important;
        overflow: hidden;
        text-overflow: ellipsis;
        line-height: 1.35 !important;
        min-height: 2.15rem;
        box-sizing: border-box;
        display: flex;
        align-items: center;
        transition: background-color 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
    }}

    [data-testid="stSidebar"] div[data-testid="stExpander"] [data-testid="element-container"],
    [data-testid="stSidebar"] div[data-testid="stExpander"] [data-testid="stElementContainer"],
    [data-testid="stSidebar"] div[data-testid="stExpander"] [data-testid="stMarkdownContainer"],
    [data-testid="stSidebar"] div[data-testid="stExpander"] [data-testid="stMarkdownContainer"] p {{
        margin-bottom: 0 !important;
        margin-top: 0 !important;
    }}

    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {{
        gap: 0.35rem !important;
    }}

    [data-testid="stSidebar"] div[data-testid="stExpander"] .streamlit-expanderContent [data-testid="stVerticalBlock"] {{
        gap: 0.25rem !important;
    }}

    [data-testid="stSidebar"] div[data-testid="stExpander"] .streamlit-expanderContent [data-testid="stVerticalBlock"] > div {{
        gap: 0 !important;
    }}

    [data-testid="stSidebar"] div[data-testid="stExpander"] .sidebar-nav-divider {{
        margin: 0.2rem 0.35rem !important;
    }}

    [data-testid="stSidebar"] div[data-testid="stExpander"] {{
        background: color-mix(in srgb, var(--surface) 88%, transparent);
        border: 1px solid var(--border);
        border-radius: 10px;
        margin-bottom: 0.3rem;
        box-shadow: none;
        transition: border-color 0.2s ease, background-color 0.2s ease;
    }}

    [data-testid="stSidebar"] div[data-testid="stExpander"]:hover {{
        border-color: color-mix(in srgb, var(--primary) 30%, var(--border));
        background: var(--surface);
    }}

    [data-testid="stSidebar"] div[data-testid="stExpander"] details summary {{
        font-size: 0.8rem;
        font-weight: 600;
        color: var(--text) !important;
        padding: 0.35rem 0.5rem !important;
        text-align: left !important;
        justify-content: flex-start !important;
    }}

    [data-testid="stSidebar"] div[data-testid="stExpander"] details summary > span {{
        justify-content: flex-start !important;
        text-align: left !important;
        width: 100%;
    }}

    [data-testid="stSidebar"] div[data-testid="stExpander"] .streamlit-expanderContent {{
        color: var(--text);
        padding: 0.25rem 0.35rem 0.45rem !important;
        background: color-mix(in srgb, var(--surface-alt) 55%, transparent);
        border-radius: 0 0 8px 8px;
        border-top: 1px solid color-mix(in srgb, var(--border) 70%, transparent);
    }}

    [data-testid="stSidebar"] div[data-testid="stExpander"] .stButton {{
        width: 100%;
    }}

    [data-testid="stSidebar"] div[data-testid="stExpander"] .stButton > button {{
        font-size: 0.8rem !important;
        padding: 0.42rem 0.6rem !important;
        min-height: 2.15rem !important;
        width: 100% !important;
        background: color-mix(in srgb, var(--surface) 92%, var(--primary)) !important;
        border: 1px solid color-mix(in srgb, var(--border) 85%, var(--primary)) !important;
        border-radius: 9px !important;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04) !important;
        margin: 0 !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: flex-start !important;
        text-align: left !important;
        transition: background-color 0.18s ease, border-color 0.18s ease, transform 0.18s ease, box-shadow 0.18s ease !important;
    }}

    [data-testid="stSidebar"] div[data-testid="stExpander"] .stButton > button > div {{
        justify-content: flex-start !important;
        width: 100% !important;
        margin: 0 !important;
        gap: 0.35rem !important;
    }}

    [data-testid="stSidebar"] div[data-testid="stExpander"] .stButton > button p,
    [data-testid="stSidebar"] div[data-testid="stExpander"] .stButton > button span,
    [data-testid="stSidebar"] div[data-testid="stExpander"] .stButton > button div,
    [data-testid="stSidebar"] div[data-testid="stExpander"] .stButton > button [data-testid="stMarkdownContainer"] {{
        text-align: left !important;
        justify-content: flex-start !important;
        width: 100% !important;
        margin: 0 !important;
    }}

    [data-testid="stSidebar"] div[data-testid="stExpander"] .stButton > button:hover {{
        background: var(--primary-soft) !important;
        border-color: color-mix(in srgb, var(--primary) 35%, var(--border)) !important;
        transform: translateX(3px);
        box-shadow: 0 2px 8px rgba(21, 101, 192, 0.10) !important;
    }}

    [data-testid="stSidebar"] .stButton > button {{
        font-size: 0.8rem !important;
        padding: 0.35rem 0.55rem !important;
        min-height: unset !important;
    }}

    [class*="st-key-sidebar_logout"] .stButton > button {{
        background: var(--btn-bg) !important;
        border: 1px solid var(--border) !important;
        margin-top: 0.25rem;
    }}

    [class*="st-key-sidebar_logout"] .stButton > button:hover {{
        border-color: var(--kaslu-green) !important;
        background: color-mix(in srgb, var(--kaslu-green) 10%, var(--btn-bg)) !important;
    }}

    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background: var(--surface) !important;
        border-color: var(--border) !important;
        border-radius: 14px !important;
        box-shadow: var(--toolbar-shadow);
        overflow: visible !important;
        padding: 0.85rem 1rem !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }}

    div[data-testid="stVerticalBlockBorderWrapper"]:hover {{
        border-color: color-mix(in srgb, var(--primary) 28%, var(--border)) !important;
        box-shadow: 0 4px 16px rgba(21, 101, 192, 0.07);
    }}

    div[data-testid="stVerticalBlockBorderWrapper"] > div {{
        gap: 0.35rem !important;
    }}

    div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stMetric"] {{
        padding: 0.45rem 0.55rem !important;
        margin: 0 !important;
        min-height: unset !important;
    }}

    div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stMetricValue"] {{
        font-size: 1.15rem !important;
    }}

    div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stCaptionContainer"] {{
        margin-top: -0.15rem !important;
        padding-bottom: 0.15rem !important;
    }}

    [class*="st-key-oplog_page_intro"] [data-testid="stMarkdownContainer"] p {{
        color: var(--text-muted) !important;
        font-size: 0.88rem !important;
        line-height: 1.55 !important;
        margin-bottom: 0.75rem !important;
    }}

    .oplog-empty-state {{
        border: 1px dashed color-mix(in srgb, var(--primary) 35%, var(--border));
        border-radius: 14px;
        padding: 1.1rem 1.15rem;
        margin: 0.5rem 0 0.75rem;
        background: color-mix(in srgb, var(--surface-alt) 85%, var(--primary));
    }}

    .oplog-empty-title {{
        font-size: 1.05rem;
        font-weight: 700;
        color: var(--heading) !important;
        margin: 0 0 0.65rem;
    }}

    .oplog-empty-steps {{
        list-style: none;
        margin: 0 0 0.5rem;
        padding: 0;
        display: flex;
        flex-wrap: wrap;
        gap: 0.45rem;
    }}

    .oplog-empty-step {{
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.35rem 0.55rem;
        border-radius: 999px;
        border: 1px solid var(--border);
        background: var(--surface);
        font-size: 0.78rem;
        font-weight: 600;
        color: var(--text) !important;
    }}

    .oplog-empty-step-num {{
        width: 1.35rem;
        height: 1.35rem;
        border-radius: 999px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 0.72rem;
        font-weight: 800;
        color: var(--btn-primary-text) !important;
        background: linear-gradient(145deg, var(--primary), var(--accent));
    }}

    [class*="st-key-oplog_loaded_banner"] [data-testid="stVerticalBlock"] {{
        gap: 0.25rem !important;
    }}

    [class*="st-key-oplog_loaded_banner"] [data-testid="stMarkdownContainer"] p {{
        margin: 0 !important;
        padding: 0.35rem 0.55rem !important;
        border-radius: 10px !important;
        background: color-mix(in srgb, var(--kaslu-green) 12%, var(--surface)) !important;
        border: 1px solid color-mix(in srgb, var(--kaslu-green) 35%, var(--border)) !important;
        font-size: 0.82rem !important;
        line-height: 1.4 !important;
    }}

    [class*="st-key-oplog_loaded_banner"] .stButton > button {{
        min-height: 2rem !important;
        font-size: 0.72rem !important;
        padding: 0.25rem 0.45rem !important;
    }}

    [class*="st-key-oplog_summary_metrics"] div[data-testid="stVerticalBlockBorderWrapper"] {{
        height: 6.5rem !important;
        min-height: 6.5rem !important;
        max-height: 6.5rem !important;
        box-sizing: border-box !important;
        display: flex !important;
        flex-direction: column !important;
    }}

    [class*="st-key-oplog_summary_metrics"] div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stMetric"] {{
        flex: 1 1 auto !important;
        height: 100% !important;
        min-height: 0 !important;
        max-height: 100% !important;
        padding: 0.45rem 0.55rem !important;
    }}

    [class*="st-key-oplog_summary_metrics"] [data-testid="stHorizontalBlock"] {{
        flex-wrap: nowrap !important;
        gap: 0.5rem !important;
        align-items: stretch !important;
    }}

    [class*="st-key-oplog_summary_metrics"] [data-testid="stHorizontalBlock"] > div[data-testid="column"] {{
        flex: 1 1 0 !important;
        min-width: 0 !important;
        max-width: none !important;
        display: flex !important;
        align-items: stretch !important;
    }}

    [class*="st-key-oplog_summary_metrics"] [data-testid="column"] [data-testid="stMetric"],
    [class*="st-key-oplog_summary_metrics"] [data-testid="column"] [data-testid="stMetric"] {{
        flex: 1 1 auto !important;
        align-self: stretch !important;
    }}

    [class*="st-key-oplog_summary_metrics"] [data-testid="stMetric"],
    .oplog-summary-metrics [data-testid="stMetric"] {{
        width: 100% !important;
        height: 6.5rem !important;
        min-height: 6.5rem !important;
        max-height: 6.5rem !important;
        box-sizing: border-box !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: flex-start !important;
        padding: 0.5rem 0.65rem !important;
        overflow: hidden !important;
    }}

    [class*="st-key-oplog_summary_metrics"] [data-testid="stMetricLabel"],
    [class*="st-key-oplog_summary_metrics"] [data-testid="stMetricLabel"] p,
    [class*="st-key-oplog_summary_metrics"] [data-testid="stMetricLabel"] span,
    [class*="st-key-oplog_summary_metrics"] label[data-testid="stMetricLabel"] {{
        min-height: 2.6rem !important;
        max-height: 2.6rem !important;
        display: -webkit-box !important;
        -webkit-line-clamp: 2 !important;
        -webkit-box-orient: vertical !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        white-space: normal !important;
        font-size: 0.72rem !important;
        line-height: 1.35 !important;
        word-wrap: break-word !important;
        overflow-wrap: anywhere !important;
    }}

    [class*="st-key-oplog_summary_metrics"] [data-testid="stMetricValue"],
    [class*="st-key-oplog_summary_metrics"] [data-testid="stMetricValue"] > div {{
        font-size: clamp(0.78rem, 1.6vw, 0.92rem) !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        white-space: nowrap !important;
        flex: 0 0 auto !important;
        margin-top: auto !important;
        color: var(--text) !important;
    }}

    [class*="st-key-oplog_summary_metrics"] [data-testid="stMetricDelta"] {{
        height: 1.35rem !important;
        min-height: 1.35rem !important;
        max-height: 1.35rem !important;
        margin: 0 !important;
        padding: 0 !important;
        display: flex !important;
        align-items: center !important;
        font-size: 0.72rem !important;
        flex-shrink: 0 !important;
    }}

    [class*="st-key-oplog_summary_metrics"] [data-testid="stMetricDelta"] svg {{
        width: 0.85rem !important;
        height: 0.85rem !important;
        flex-shrink: 0 !important;
    }}

    [class*="st-key-oplog_summary_metrics"] [data-testid="stMetric"]:not(:has([data-testid="stMetricDelta"]))::after {{
        content: "" !important;
        display: block !important;
        height: 1.35rem !important;
        min-height: 1.35rem !important;
        flex-shrink: 0 !important;
    }}

    [class*="st-key-oplog_summary_metrics"] [data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(3) [data-testid="stMetricValue"],
    [class*="st-key-oplog_summary_metrics"] [data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(3) [data-testid="stMetricValue"] > div {{
        color: var(--primary-text) !important;
    }}

    [class*="st-key-oplog_summary_metrics"] [data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(4) [data-testid="stMetricValue"],
    [class*="st-key-oplog_summary_metrics"] [data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(4) [data-testid="stMetricValue"] > div,
    [class*="st-key-oplog_summary_metrics"] [data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(5) [data-testid="stMetricValue"],
    [class*="st-key-oplog_summary_metrics"] [data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(5) [data-testid="stMetricValue"] > div {{
        color: color-mix(in srgb, var(--kaslu-green) 78%, var(--text)) !important;
        font-weight: 700 !important;
    }}

    @media (max-width: 900px) {{
        [class*="st-key-oplog_summary_metrics"] [data-testid="stHorizontalBlock"] {{
            flex-wrap: wrap !important;
        }}

        [class*="st-key-oplog_summary_metrics"] [data-testid="stHorizontalBlock"] > div[data-testid="column"] {{
            flex: 1 1 calc(33.333% - 0.4rem) !important;
            min-width: min(100%, 160px) !important;
        }}
    }}

    @media (max-width: 768px) {{
        [class*="st-key-oplog_summary_metrics"] [data-testid="stHorizontalBlock"] > div[data-testid="column"] {{
            flex: 1 1 calc(50% - 0.35rem) !important;
            min-width: min(100%, 140px) !important;
        }}

        [class*="st-key-oplog_summary_metrics"] [data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(5) {{
            flex: 1 1 100% !important;
            max-width: 100% !important;
        }}
    }}

    @media (max-width: 480px) {{
        [class*="st-key-oplog_summary_metrics"] [data-testid="stHorizontalBlock"] > div[data-testid="column"] {{
            flex: 1 1 100% !important;
            max-width: 100% !important;
        }}
    }}

    [data-testid="stMetricLabel"],
    [data-testid="stMetricLabel"] p,
    [data-testid="stMetricLabel"] span,
    label[data-testid="stMetricLabel"] {{
        white-space: normal !important;
        overflow: visible !important;
        text-overflow: unset !important;
        -webkit-line-clamp: unset !important;
        display: block !important;
        height: auto !important;
        max-height: none !important;
        word-wrap: break-word !important;
        overflow-wrap: anywhere !important;
        line-height: 1.45 !important;
    }}

    /* Oplog summary metrics: clamp labels after global stMetricLabel reset */
    [class*="st-key-oplog_summary_metrics"] [data-testid="stMetricLabel"],
    [class*="st-key-oplog_summary_metrics"] [data-testid="stMetricLabel"] p,
    [class*="st-key-oplog_summary_metrics"] [data-testid="stMetricLabel"] span,
    [class*="st-key-oplog_summary_metrics"] label[data-testid="stMetricLabel"] {{
        min-height: 2.6rem !important;
        max-height: 2.6rem !important;
        height: 2.6rem !important;
        display: -webkit-box !important;
        -webkit-line-clamp: 2 !important;
        -webkit-box-orient: vertical !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        white-space: normal !important;
        font-size: 0.72rem !important;
        line-height: 1.35 !important;
        word-wrap: break-word !important;
        overflow-wrap: anywhere !important;
    }}

    .stCaption,
    .stCaption p,
    .stCaption span,
    [data-testid="stCaptionContainer"],
    [data-testid="stCaptionContainer"] p {{
        white-space: normal !important;
        overflow: visible !important;
        text-overflow: unset !important;
        word-wrap: break-word !important;
        overflow-wrap: anywhere !important;
        line-height: 1.5 !important;
    }}

    section.main div[data-testid="stHorizontalBlock"] {{
        flex-wrap: wrap !important;
        gap: 0.5rem;
        row-gap: 0.75rem;
    }}

    section.main div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {{
        flex: 1 1 180px !important;
        min-width: min(100%, 160px) !important;
        max-width: 100% !important;
    }}

    [class*="st-key-oplog_summary_metrics"] [data-testid="stHorizontalBlock"] {{
        flex-wrap: nowrap !important;
        gap: 0.5rem !important;
        align-items: stretch !important;
    }}

    [class*="st-key-oplog_summary_metrics"] [data-testid="stHorizontalBlock"] > div[data-testid="column"] {{
        flex: 1 1 0 !important;
        min-width: 0 !important;
        max-width: none !important;
        display: flex !important;
        align-items: stretch !important;
    }}

    @media (max-width: 900px) {{
        [class*="st-key-oplog_summary_metrics"] [data-testid="stHorizontalBlock"] {{
            flex-wrap: wrap !important;
        }}

        [class*="st-key-oplog_summary_metrics"] [data-testid="stHorizontalBlock"] > div[data-testid="column"] {{
            flex: 1 1 calc(33.333% - 0.4rem) !important;
            min-width: min(100%, 160px) !important;
        }}
    }}

    @media (max-width: 768px) {{
        [class*="st-key-oplog_summary_metrics"] [data-testid="stHorizontalBlock"] > div[data-testid="column"] {{
            flex: 1 1 calc(50% - 0.35rem) !important;
            min-width: min(100%, 140px) !important;
        }}

        [class*="st-key-oplog_summary_metrics"] [data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(5) {{
            flex: 1 1 100% !important;
            max-width: 100% !important;
        }}
    }}

    @media (max-width: 480px) {{
        [class*="st-key-oplog_summary_metrics"] [data-testid="stHorizontalBlock"] > div[data-testid="column"] {{
            flex: 1 1 100% !important;
            max-width: 100% !important;
        }}
    }}

    div[data-testid="stTabs"] [data-baseweb="tab-list"] {{
        flex-wrap: wrap !important;
        row-gap: 0.35rem;
        gap: 0.25rem;
        background: var(--surface-alt);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 0.25rem;
    }}

    div[data-testid="stTabs"] button[data-baseweb="tab"] {{
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 0.82rem !important;
        color: var(--text-muted) !important;
        transition: background-color 0.2s ease, color 0.2s ease;
    }}

    div[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] {{
        background: var(--surface) !important;
        color: var(--primary-text) !important;
        box-shadow: var(--toolbar-shadow);
    }}

    div[data-testid="stTabs"] [data-baseweb="tab-panel"] {{
        padding-top: 0.85rem;
    }}

    [class*="st-key-oplog_chart_tabs"] [data-testid="stTabs"] [data-baseweb="tab-list"] {{
        flex-wrap: nowrap !important;
        overflow-x: auto !important;
        -webkit-overflow-scrolling: touch;
        scrollbar-gutter: stable;
        gap: 0.4rem !important;
        padding: 0.35rem !important;
    }}

    [class*="st-key-oplog_chart_tabs"] [data-testid="stTabs"] button[data-baseweb="tab"] {{
        flex-shrink: 0 !important;
        white-space: nowrap !important;
        border: 1px solid var(--border) !important;
        background: var(--surface) !important;
        padding: 0.4rem 0.65rem !important;
        cursor: pointer !important;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.05) !important;
    }}

    [class*="st-key-oplog_chart_tabs"] [data-testid="stTabs"] button[data-baseweb="tab"]:hover:not([aria-selected="true"]) {{
        background: var(--btn-hover) !important;
        border-color: color-mix(in srgb, var(--primary) 35%, var(--border)) !important;
        color: var(--text) !important;
    }}

    [class*="st-key-oplog_chart_tabs"] [data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] {{
        background: var(--surface) !important;
        color: var(--primary-text) !important;
        border-color: color-mix(in srgb, var(--primary) 45%, var(--border)) !important;
        box-shadow:
            0 2px 8px rgba(21, 101, 192, 0.12),
            inset 0 0 0 1px color-mix(in srgb, var(--primary) 18%, transparent) !important;
    }}

    [data-testid="stFileUploader"] section {{
        border: 2px dashed var(--border) !important;
        border-radius: 12px !important;
        background: var(--surface-alt) !important;
        transition: border-color 0.2s ease, background-color 0.2s ease;
    }}

    [data-testid="stFileUploader"] section:hover {{
        border-color: var(--accent) !important;
        background: var(--primary-soft) !important;
    }}

    [data-testid="stFileUploader"] label,
    [data-testid="stFileUploader"] span,
    [data-testid="stFileUploader"] small {{
        color: var(--text) !important;
    }}


    [data-testid="stMetric"] {{
        background: var(--surface);
        border: 1px solid var(--border);
        border-left: 3px solid var(--primary);
        border-radius: 12px;
        padding: 0.65rem 0.75rem;
        box-shadow: var(--toolbar-shadow);
        transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }}

    [data-testid="stMetric"]:hover {{
        border-left-color: var(--accent);
        box-shadow: 0 4px 14px rgba(21, 101, 192, 0.08);
    }}

    [data-testid="stMetricLabel"] {{
        color: var(--text-muted) !important;
    }}

    [data-testid="stMetricValue"] {{
        color: var(--text) !important;
    }}

    div[data-testid="stDataFrame"],
    div[data-testid="stTable"],
    [data-testid="stDataEditor"] {{
        border: 1px solid var(--border);
        border-radius: 12px;
        overflow: hidden;
    }}

    [data-testid="stAlert"] {{
        border-radius: 12px;
        background-color: var(--surface-alt) !important;
        color: var(--text) !important;
    }}

    [data-testid="stAlert"] p,
    [data-testid="stAlert"] span,
    [data-testid="stAlert"] div[data-testid="stMarkdownContainer"] p {{
        color: var(--text) !important;
    }}

    div[data-testid="stInfo"],
    div[data-testid="stWarning"],
    div[data-testid="stSuccess"],
    div[data-testid="stError"] {{
        background-color: var(--surface-alt) !important;
        color: var(--text) !important;
        border: 1px solid var(--border) !important;
        border-left-width: 3px !important;
        border-radius: 12px !important;
    }}

    div[data-testid="stInfo"] {{ border-left-color: var(--primary) !important; }}
    div[data-testid="stWarning"] {{ border-left-color: #D97706 !important; }}
    div[data-testid="stSuccess"] {{ border-left-color: var(--kaslu-green) !important; }}
    div[data-testid="stError"] {{ border-left-color: #DC2626 !important; }}

    div[data-testid="stInfo"] p,
    div[data-testid="stWarning"] p,
    div[data-testid="stSuccess"] p,
    div[data-testid="stError"] p {{
        color: var(--text) !important;
    }}

    hr {{
        border: none !important;
        height: 1px !important;
        background: linear-gradient(90deg, transparent, var(--border), transparent) !important;
        margin: 1.25rem 0 !important;
    }}

    .stTextInput input:focus,
    .stNumberInput input:focus,
    textarea:focus,
    input[type="password"]:focus {{
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 2px color-mix(in srgb, var(--accent) 20%, transparent) !important;
        outline: none !important;
    }}

    .theme-pill {{
        display: inline-block;
        padding: 0.2rem 0.55rem;
        border-radius: 999px;
        font-size: 0.72rem;
        font-weight: 600;
        background: var(--primary-soft);
        color: var(--primary-text) !important;
        border: 1px solid var(--border);
    }}

    .theme-toggle-label {{
        font-size: 0.78rem;
        font-weight: 600;
        color: var(--text-muted) !important;
        margin-bottom: 0.35rem;
    }}

    /* ---- Page transition overlay ---- */
    @keyframes kasluKPulse {{
        0%, 100% {{ transform: scale(1); opacity: 1; }}
        50% {{ transform: scale(1.08); opacity: 0.92; }}
    }}

    @keyframes kasluKRingSpin {{
        from {{ transform: rotate(0deg); }}
        to {{ transform: rotate(360deg); }}
    }}

    .kaslu-page-transition {{
        position: fixed;
        inset: 0;
        z-index: 999999;
        display: flex;
        align-items: center;
        justify-content: center;
        pointer-events: none;
        opacity: 0;
        background: color-mix(in srgb, var(--surface) 82%, var(--primary));
        backdrop-filter: blur(6px);
        transition: opacity 0.35s ease;
    }}

    .kaslu-page-transition--active {{
        opacity: 1;
    }}

    .kaslu-page-transition--done {{
        opacity: 0;
    }}

    .kaslu-page-transition-inner {{
        position: relative;
        width: 4.5rem;
        height: 4.5rem;
        display: flex;
        align-items: center;
        justify-content: center;
    }}

    .kaslu-page-transition-ring {{
        position: absolute;
        inset: 0;
        border-radius: 50%;
        border: 2px solid transparent;
        border-top-color: var(--accent);
        border-right-color: var(--primary);
        animation: kasluKRingSpin 0.85s linear infinite;
    }}

    .kaslu-page-transition-logo {{
        width: 2.75rem;
        height: 2.75rem;
        animation: kasluKPulse 0.85s ease-in-out infinite;
        filter: drop-shadow(0 4px 12px rgba(13, 71, 161, 0.35));
    }}

    /* ---- Login page animations ---- */
    @keyframes loginFadeUp {{
        from {{ opacity: 0; transform: translateY(14px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}

    @keyframes loginSlideIn {{
        from {{ opacity: 0; transform: translateX(18px); }}
        to {{ opacity: 1; transform: translateX(0); }}
    }}

    @keyframes loginOrbFloat {{
        0%, 100% {{ transform: translate(0, 0) scale(1); }}
        33% {{ transform: translate(12px, -18px) scale(1.04); }}
        66% {{ transform: translate(-8px, 10px) scale(0.96); }}
    }}

    @keyframes loginGradientShift {{
        0%, 100% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
    }}

    @keyframes loginLogoGlow {{
        0%, 100% {{ filter: drop-shadow(0 4px 14px rgba(21, 101, 192, 0.22)); }}
        50% {{ filter: drop-shadow(0 6px 22px rgba(38, 198, 218, 0.28)); }}
    }}

    @keyframes loginRingSpin {{
        from {{ transform: rotate(0deg); }}
        to {{ transform: rotate(360deg); }}
    }}

    @keyframes loginPulse {{
        0%, 100% {{ opacity: 1; transform: scale(1); }}
        50% {{ opacity: 0.55; transform: scale(0.85); }}
    }}

    @keyframes loginShimmer {{
        0% {{ background-position: -200% center; }}
        100% {{ background-position: 200% center; }}
    }}

    /* ---- Login layout ---- */
    #kaslu-login {{
        display: none;
    }}

    /* ---- Page headers & sections ---- */
    .lab-page-header {{
        margin-bottom: 1.35rem;
    }}

    .lab-page-title {{
        font-size: clamp(1.5rem, 3vw, 1.9rem) !important;
        font-weight: 700 !important;
        color: var(--heading) !important;
        margin: 0 0 0.35rem !important;
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        gap: 0.5rem;
        border: none !important;
        padding: 0 !important;
    }}

    .lab-badge {{
        display: inline-block;
        font-size: 0.68rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        padding: 0.2rem 0.55rem;
        border-radius: 999px;
        background: var(--primary-soft);
        color: var(--primary-text);
        border: 1px solid var(--border);
        vertical-align: middle;
    }}

    .lab-page-caption {{
        font-size: 0.92rem;
        line-height: 1.55;
        color: var(--text-muted);
        margin: 0;
        max-width: 62ch;
    }}

    .lab-page-header-accent {{
        width: 72px;
        height: 3px;
        border-radius: 999px;
        margin-top: 0.75rem;
        background: linear-gradient(90deg, var(--primary), var(--accent), var(--kaslu-green), var(--primary));
        background-size: 200% auto;
        animation: accentShimmer 4s linear infinite;
    }}

    .lab-page-header {{
        animation: fadeSlideUp 0.45s ease-out both;
    }}

    .lab-section {{
        margin: 1.25rem 0 0.85rem;
    }}

    .lab-section-title {{
        font-size: 1.05rem !important;
        font-weight: 600 !important;
        color: var(--heading) !important;
        margin: 0 !important;
        border: none !important;
        padding: 0 !important;
    }}

    .lab-section-sub {{
        font-size: 0.82rem;
        color: var(--text-muted);
        margin: 0.25rem 0 0;
    }}

    /* ---- Workflow strip ---- */
    [class*="st-key-wf_step_"] {{
        animation: fadeSlideUp 0.5s ease-out both;
    }}

    [class*="st-key-wf_step_1"] {{ animation-delay: 0.04s; }}
    [class*="st-key-wf_step_2"] {{ animation-delay: 0.08s; }}
    [class*="st-key-wf_step_3"] {{ animation-delay: 0.12s; }}
    [class*="st-key-wf_step_4"] {{ animation-delay: 0.16s; }}

    [class*="st-key-wf_step_"] [data-testid="stVerticalBlockBorderWrapper"] {{
        border-left: 3px solid var(--primary) !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease;
        margin-bottom: 0.25rem;
    }}

    [class*="st-key-wf_step_"]:hover [data-testid="stVerticalBlockBorderWrapper"] {{
        border-left-color: var(--accent) !important;
        box-shadow: 0 6px 18px rgba(21, 101, 192, 0.12);
        transform: translateY(-2px);
    }}

    [class*="st-key-wf_step_"] [data-testid="stMarkdownContainer"] p {{
        font-size: 0.95rem !important;
        font-weight: 700 !important;
        color: var(--primary-text) !important;
        margin-bottom: 0.15rem !important;
    }}

    [class*="st-key-wf_step_"] [data-testid="stCaptionContainer"] p {{
        font-size: 0.78rem !important;
        font-weight: 600 !important;
        line-height: 1.35 !important;
        color: var(--text) !important;
    }}

    .lab-workflow-num {{
        display: flex;
        align-items: center;
        justify-content: center;
        width: 1.65rem;
        height: 1.65rem;
        border-radius: 8px;
        font-size: 0.78rem;
        font-weight: 700;
        color: var(--primary-text);
        background: var(--primary-soft);
        flex-shrink: 0;
    }}

    .lab-workflow-label {{
        font-size: 0.78rem;
        font-weight: 600;
        line-height: 1.35;
        color: var(--text);
    }}

    /* ---- Module cards (dashboard) ---- */
    [class*="st-key-go_"] {{
        animation: fadeSlideUp 0.55s ease-out both;
    }}

    [class*="st-key-go_oplog"] {{ animation-delay: 0.06s; }}
    [class*="st-key-go_analysis"] {{ animation-delay: 0.10s; }}
    [class*="st-key-go_sim"] {{ animation-delay: 0.14s; }}
    [class*="st-key-go_pn"] {{ animation-delay: 0.18s; }}
    [class*="st-key-go_stoich"] {{ animation-delay: 0.22s; }}
    [class*="st-key-go_hist"] {{ animation-delay: 0.26s; }}

    [class*="st-key-go_"] [data-testid="stVerticalBlockBorderWrapper"] {{
        border-left: 3px solid var(--primary) !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease;
    }}

    [class*="st-key-go_"]:hover [data-testid="stVerticalBlockBorderWrapper"] {{
        border-left-color: var(--accent) !important;
        box-shadow: 0 8px 22px rgba(21, 101, 192, 0.14);
        transform: translateY(-3px);
    }}

    [class*="st-key-go_"] .stButton > button:hover {{
        transform: translateY(-2px) scale(1.02);
        box-shadow: 0 6px 20px rgba(8, 145, 178, 0.25) !important;
    }}

    .lab-card-title {{
        font-size: 0.95rem;
        font-weight: 700;
        color: var(--heading) !important;
        margin: 0 0 0.15rem;
    }}

    .lab-module-grid {{
        margin-bottom: 0.5rem;
    }}

    /* ---- Advice / insight cards ---- */
    .lab-advice-card [data-testid="stVerticalBlockBorderWrapper"] {{
        border-left: 3px solid var(--kaslu-green) !important;
    }}

    .lab-sidebar-label {{
        font-size: 0.68rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: var(--text-muted);
        margin: 0.5rem 0 0.35rem;
        text-align: left !important;
    }}

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {{
        text-align: left !important;
    }}

    .lab-status-dot {{
        display: inline-block;
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: var(--kaslu-green);
        margin-right: 0.35rem;
        box-shadow: 0 0 0 2px color-mix(in srgb, var(--kaslu-green) 25%, transparent);
        animation: statusPulse 2.4s ease-in-out infinite;
    }}

    /* Hide Vega chart debug / source dumps */
    .vega-embed details,
    .vega-embed .vega-actions {{
        display: none !important;
    }}

    /* ---- Data editor / dataframe grid ---- */
    [data-testid="stDataEditor"],
    [data-testid="stDataFrame"],
    .stDataFrame {{
        --gdg-bg-header: {t["surface_alt"]};
        --gdg-bg-header-has-focus: {t["btn_hover"]};
        --gdg-bg-header-hovered: {t["btn_hover"]};
        --gdg-bg-cell: {t["surface"]};
        --gdg-bg-cell-medium: {t["surface_alt"]};
        --gdg-text-dark: {t["input_text"]};
        --gdg-text-medium: {t["text"]};
        --gdg-text-light: {t["text_muted"]};
        --gdg-border-color: {t["border"]};
        --gdg-accent-color: {t["primary"]};
        --gdg-accent-light: {t["primary_soft"]};
    }}

    /* ---- Vega/streamlit charts (line_chart) ---- */
    [data-testid="stVegaLiteChart"] {{
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 0.25rem;
    }}
    </style>
    """


def inject_theme_css() -> None:
    init_theme()
    st.markdown(
        '<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate" />'
        '<meta http-equiv="Pragma" content="no-cache" />'
        '<meta http-equiv="Expires" content="0" />',
        unsafe_allow_html=True,
    )
    st.markdown(_theme_css(get_theme()), unsafe_allow_html=True)


def _apply_theme_from_segment(selected: str | None) -> None:
    if selected == "Light":
        set_theme("light")
    elif selected == "Dark":
        set_theme("dark")


def render_topbar_theme_segment() -> None:
    """Compact Light/Dark segmented control for the top toolbar."""
    from core.i18n import t

    theme = get_theme()
    current = "Dark" if theme == "dark" else "Light"

    def _format_option(option: str) -> str:
        if option == "Light":
            return t("ui.theme_light_short")
        if option == "Dark":
            return t("ui.theme_dark_short")
        return option

    selected = st.segmented_control(
        t("ui.theme"),
        ["Light", "Dark"],
        default=current,
        key="top_theme_segment",
        label_visibility="collapsed",
        format_func=_format_option,
        width="content",
    )
    if selected and selected != current:
        _apply_theme_from_segment(selected)
        st.rerun()


def render_theme_toggle(*, key_prefix: str = "theme", label: str = "Appearance") -> None:
    theme = get_theme()
    current = "Dark" if theme == "dark" else "Light"

    st.markdown(f'<p class="theme-toggle-label">{label}</p>', unsafe_allow_html=True)
    selected = st.segmented_control(
        label,
        ["Light", "Dark"],
        default=current,
        key=f"{key_prefix}_segment",
        label_visibility="collapsed",
    )
    if selected and selected != current:
        _apply_theme_from_segment(selected)
        st.rerun()


def render_theme_toggle_top(*, key_prefix: str = "top_theme") -> None:
    """Sun/moon toggle buttons for the top toolbar (single row)."""
    theme = get_theme()
    light_col, dark_col = st.columns(2, gap="small")
    with light_col:
        if st.button(
            "☀",
            key=f"{key_prefix}_light",
            help="Light mode",
            type="primary" if theme == "light" else "secondary",
            use_container_width=True,
        ):
            if theme != "light":
                set_theme("light")
                st.rerun()
    with dark_col:
        if st.button(
            "🌙",
            key=f"{key_prefix}_dark",
            help="Dark mode",
            type="primary" if theme == "dark" else "secondary",
            use_container_width=True,
        ):
            if theme != "dark":
                set_theme("dark")
                st.rerun()


def render_theme_toggle_compact(*, key: str = "theme_compact") -> None:
    """Deprecated: use render_theme_toggle_top in app chrome."""
    render_theme_toggle_top(key_prefix=key)
