"""Login page UI — animated lab-themed design (reload-safe)."""

from __future__ import annotations

import html
import importlib

import streamlit as st
import streamlit.components.v1 as components

import core.i18n as i18n
import core.ui.theme as theme_mod
from core.ui.brand import logo_data_uri

importlib.reload(i18n)
importlib.reload(theme_mod)
from core.i18n import t  # noqa: E402

LOGIN_PANEL_H = 480
LOGIN_SCOPE = '[data-testid="stMain"]:has(#kaslu-login)'


def _theme_icon_data_uri(*, sun: bool) -> str:
    """Inline SVG for sun/moon toggle."""
    import urllib.parse

    if sun:
        stroke = "%23FBBF24"
        svg = (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"'
            f' stroke="{stroke}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
            '<circle cx="12" cy="12" r="4"/>'
            '<path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2'
            'M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"/>'
            "</svg>"
        )
    else:
        stroke = "%23CBD5E1"
        svg = (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"'
            f' stroke="{stroke}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
            '<path d="M21 14.5A7.5 7.5 0 0 1 9.5 3 5.5 5.5 0 1 0 21 14.5z"/>'
            "</svg>"
        )
    return "data:image/svg+xml," + urllib.parse.quote(svg)


def _tokens() -> dict[str, str]:
    importlib.reload(theme_mod)
    tok = dict(theme_mod.THEMES[theme_mod.get_theme()])
    tok.setdefault("kaslu_green", "#059669")
    tok.setdefault("primary_soft", "#E8F2FC")
    tok.setdefault("primary_text", tok.get("primary", "#1565C0"))
    return tok


def _label(key: str, *, en: str, zh: str) -> str:
    text = t(key)
    if not text or text == key or text.startswith("home."):
        if zh and zh.strip() != en.strip():
            return f"{en} ({zh})"
        return en
    return text


def inject_login_page_css() -> None:
    tok = _tokens()
    importlib.reload(theme_mod)
    p = tok["primary"]
    a = tok["accent"]
    g = tok["kaslu_green"]
    s = tok["surface"]
    sf = tok["surface_alt"]
    b = tok["border"]
    h = tok["heading"]
    tm = tok["text_muted"]
    tx = tok["text"]
    ib = tok.get("input_bg", s)
    ph = tok.get("text_muted", "#64748B")
    scope = LOGIN_SCOPE
    st.markdown(
        f"""
        <style>
        @keyframes kasluFadeUp {{
            from {{ opacity: 0; transform: translateY(12px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        @keyframes kasluOrb {{
            0%, 100% {{ transform: translate(0,0) scale(1); }}
            50% {{ transform: translate(14px,-18px) scale(1.05); }}
        }}
        @keyframes kasluShimmer {{
            0% {{ background-position: -200% center; }}
            100% {{ background-position: 200% center; }}
        }}
        @media (prefers-reduced-motion: reduce) {{
            *, *::before, *::after {{ animation: none !important; transition: none !important; }}
        }}

        /* ---- viewport: no page scroll ---- */
        .stApp:has(#kaslu-login),
        [data-testid="stAppViewContainer"]:has(#kaslu-login),
        {scope} {{
            overflow: hidden !important;
            max-height: 100dvh !important;
            height: 100dvh !important;
        }}
        .stApp:has(#kaslu-login) footer,
        .stApp:has(#kaslu-login) [data-testid="stToolbar"],
        .stApp:has(#kaslu-login) [data-testid="stStatusWidget"] {{
            display: none !important;
        }}
        {scope} [data-testid="stHeader"] {{
            background: transparent !important;
            height: 2.25rem !important;
            min-height: 2.25rem !important;
        }}
        {scope} [data-testid="stMainBlockContainer"] {{
            max-width: min(1040px, 94vw) !important;
            padding: 0.75rem 1.25rem !important;
            margin: 0 auto !important;
            min-height: calc(100dvh - 2.25rem) !important;
            display: flex !important;
            flex-direction: column !important;
            justify-content: center !important;
            overflow: hidden !important;
        }}

        /* ---- background ---- */
        .login-ambience {{
            position: fixed; inset: 0; pointer-events: none; z-index: 0; overflow: hidden;
            background: linear-gradient(145deg, color-mix(in srgb, {p} 6%, {sf}), {s} 40%, color-mix(in srgb, {a} 8%, {sf}));
        }}
        .login-mesh {{
            position: absolute; inset: 0;
            background:
                radial-gradient(ellipse 80% 50% at 15% 20%, color-mix(in srgb, {p} 14%, transparent), transparent 55%),
                radial-gradient(ellipse 70% 45% at 85% 75%, color-mix(in srgb, {a} 12%, transparent), transparent 50%),
                radial-gradient(ellipse 50% 40% at 50% 100%, color-mix(in srgb, {g} 10%, transparent), transparent 45%);
        }}
        .login-grid {{
            position: absolute; inset: 0; opacity: 0.55;
            background-image:
                linear-gradient(color-mix(in srgb, {p} 7%, transparent) 1px, transparent 1px),
                linear-gradient(90deg, color-mix(in srgb, {p} 7%, transparent) 1px, transparent 1px);
            background-size: 36px 36px;
            mask-image: radial-gradient(ellipse 85% 75% at 50% 45%, black 20%, transparent 75%);
        }}
        .login-orb {{
            position: absolute; border-radius: 50%; filter: blur(56px); opacity: 0.42;
            animation: kasluOrb 28s ease-in-out infinite;
        }}
        .login-orb-1 {{ width: 340px; height: 340px; top: -4%; left: -2%; background: {p}66; }}
        .login-orb-2 {{ width: 280px; height: 280px; top: 48%; right: -4%; background: {a}55; }}
        .login-orb-3 {{ width: 220px; height: 220px; bottom: -2%; left: 32%; background: {g}44; }}
        .login-orb-4 {{ width: 180px; height: 180px; top: 18%; right: 28%; background: {p}33; }}

        /* ---- symmetric columns ---- */
        {scope} [data-testid="stHorizontalBlock"] {{
            align-items: stretch !important;
            gap: 1.15rem !important;
            animation: kasluFadeUp 0.55s ease both;
        }}
        {scope} [data-testid="stColumn"] {{
            min-height: {LOGIN_PANEL_H}px !important;
            max-height: {LOGIN_PANEL_H}px !important;
            display: flex !important;
            flex-direction: column !important;
        }}
        {scope} [data-testid="stColumn"]:first-child > [data-testid="stVerticalBlock"] {{
            flex: 0 0 auto !important;
            height: {LOGIN_PANEL_H}px !important;
        }}
        #kaslu-form-shell {{ display: none !important; }}
        {scope} [data-testid="stColumn"]:last-child > [data-testid="stVerticalBlock"] {{
            position: relative !important;
            flex: 0 0 {LOGIN_PANEL_H}px !important;
            height: {LOGIN_PANEL_H}px !important;
            max-height: {LOGIN_PANEL_H}px !important;
            min-height: {LOGIN_PANEL_H}px !important;
            background: color-mix(in srgb, {s} 92%, transparent) !important;
            backdrop-filter: blur(16px) !important;
            -webkit-backdrop-filter: blur(16px) !important;
            border: 1px solid color-mix(in srgb, {a} 35%, {b}) !important;
            border-radius: 22px !important;
            box-shadow: 0 16px 44px rgba(21,101,192,0.12) !important;
            padding: 1rem 1.15rem 0.85rem !important;
            box-sizing: border-box !important;
            gap: 0.4rem !important;
            overflow: hidden !important;
        }}

        /* ---- left brand iframe ---- */
        {scope} [data-testid="stIFrame"] {{
            border: none !important;
            border-radius: 22px !important;
            box-shadow: 0 16px 48px rgba(21,101,192,0.14) !important;
            height: {LOGIN_PANEL_H}px !important;
            min-height: {LOGIN_PANEL_H}px !important;
            max-height: {LOGIN_PANEL_H}px !important;
            width: 100% !important;
        }}
        {scope} [data-testid="stColumn"]:first-child [data-testid="stElementContainer"] {{
            height: {LOGIN_PANEL_H}px !important;
        }}

        /* ---- right form card (Streamlit border container key) ---- */
        /* ---- theme toggle ---- */
        {scope} .st-key-login_theme {{
            position: absolute !important;
            top: 0.85rem !important;
            right: 0.95rem !important;
            z-index: 8 !important;
            width: 2.45rem !important;
            height: 2.45rem !important;
            margin: 0 !important;
        }}
        {scope} .st-key-login_theme [data-testid="stTooltipIcon"] {{
            display: none !important;
        }}
        {scope} .st-key-login_theme [data-testid="stButton"] {{
            margin: 0 !important;
            width: 2.45rem !important;
            height: 2.45rem !important;
        }}
        {scope} .st-key-login_theme [data-testid="stBaseButton-secondary"] {{
            width: 2.45rem !important;
            min-width: 2.45rem !important;
            height: 2.45rem !important;
            min-height: 2.45rem !important;
            padding: 0 !important;
            margin: 0 !important;
            border-radius: 999px !important;
            font-size: 1.05rem !important;
            line-height: 1 !important;
            background-color: color-mix(in srgb, {sf} 88%, {a} 12%) !important;
            border: 1px solid color-mix(in srgb, {a} 38%, {b}) !important;
            box-shadow: {tok["toolbar_shadow"]} !important;
        }}
        {scope} .st-key-login_theme [data-testid="stBaseButton-secondary"]:hover {{
            border-color: {a} !important;
            transform: scale(1.05);
        }}

        /* ---- login / register tabs ---- */
        {scope} .st-key-login_mode {{
            width: 100% !important;
            padding-right: 2.75rem !important;
        }}
        {scope} .st-key-login_mode [data-testid="stElementContainer"] {{
            width: 100% !important;
        }}
        {scope} .st-key-login_mode [data-testid="stWidgetLabel"] {{
            display: none !important;
        }}
        {scope} .st-key-login_mode div[role="radiogroup"] {{
            display: flex !important;
            width: 100% !important;
            gap: 0.35rem !important;
            background: {sf} !important;
            border: 1px solid {b} !important;
            border-radius: 12px !important;
            padding: 0.32rem !important;
            margin: 0 !important;
        }}
        {scope} .st-key-login_mode div[role="radiogroup"] > label {{
            flex: 1 1 50% !important;
            justify-content: center !important;
            border: none !important;
            border-radius: 9px !important;
            background: transparent !important;
            font-weight: 600 !important;
            font-size: 0.9rem !important;
            color: {tm} !important;
            margin: 0 !important;
            padding: 0.5rem 0.65rem !important;
            white-space: nowrap !important;
        }}
        {scope} .st-key-login_mode div[role="radiogroup"] > label p,
        {scope} .st-key-login_mode div[role="radiogroup"] > label span {{
            color: inherit !important;
        }}
        {scope} .st-key-login_mode div[role="radiogroup"] > label:has(input:checked) {{
            background: {s} !important;
            color: {tok["primary_text"]} !important;
            box-shadow: 0 2px 8px rgba(21,101,192,0.1) !important;
        }}
        {scope} .st-key-login_mode div[role="radiogroup"] > label > div:first-child {{
            display: none !important;
        }}

        /* ---- inputs ---- */
        {scope} .stTextInput,
        {scope} .stTextInput > div {{
            margin-bottom: 0 !important;
        }}
        {scope} .stTextInput label,
        {scope} .stTextInput label p {{
            color: {tm} !important;
            font-size: 0.76rem !important;
            margin-bottom: 0.12rem !important;
        }}
        {scope} .stTextInput input,
        {scope} input[type="password"] {{
            border-radius: 11px !important;
            background-color: {ib} !important;
            color: {tx} !important;
            border: 1px solid {b} !important;
            min-height: 2.35rem !important;
            font-size: 0.88rem !important;
        }}
        {scope} .stTextInput input:placeholder-shown,
        {scope} input[type="password"]:placeholder-shown {{
            color: {ph} !important;
            opacity: 0.55 !important;
        }}
        {scope} .stTextInput input::placeholder,
        {scope} input[type="password"]::placeholder {{
            color: {ph} !important;
            opacity: 0.55 !important;
        }}
        {scope} .stTextInput input:focus,
        {scope} input[type="password"]:focus {{
            color: {tx} !important;
            opacity: 1 !important;
            border-color: {a} !important;
            box-shadow: 0 0 0 3px color-mix(in srgb, {a} 20%, transparent) !important;
        }}

        /* ---- submit button ---- */
        {scope} .st-key-auth_submit [data-testid="stBaseButton-primary"] {{
            background: linear-gradient(135deg, {p}, {a}, {g}) !important;
            background-size: 200% 200% !important;
            border: none !important;
            border-radius: 12px !important;
            margin-top: 0.25rem !important;
            min-height: 2.45rem !important;
            box-shadow: 0 6px 18px rgba(21,101,192,0.25) !important;
        }}

        /* ---- form header / footer ---- */
        .login-dynamic-header {{ margin: 0.15rem 0 0.45rem; }}
        .login-form-eyebrow {{
            font-size: 0.68rem; font-weight: 700; letter-spacing: 0.14em;
            text-transform: uppercase; color: {a}; margin: 0 0 0.15rem;
        }}
        .login-form-title {{
            font-size: 1.45rem; font-weight: 700; color: {h};
            margin: 0 0 0.2rem; border: none; padding: 0;
        }}
        .login-form-caption {{
            font-size: 0.85rem; color: {tm}; margin: 0 0 0.35rem; line-height: 1.45;
        }}
        .login-secure-note {{
            display: flex; align-items: center; gap: 0.4rem;
            font-size: 0.72rem; color: {tm};
            margin-top: 0.45rem; padding-top: 0.5rem;
            border-top: 1px solid color-mix(in srgb, {b} 70%, transparent);
        }}

        @media (max-width: 860px) {{
            .stApp:has(#kaslu-login),
            [data-testid="stAppViewContainer"]:has(#kaslu-login),
            {scope} {{
                overflow: auto !important;
                height: auto !important;
                max-height: none !important;
            }}
            {scope} [data-testid="stMainBlockContainer"] {{
                min-height: auto !important;
                max-height: none !important;
                padding: 1rem !important;
            }}
            {scope} [data-testid="stHorizontalBlock"] {{
                flex-direction: column !important;
            }}
            {scope} [data-testid="stColumn"]:last-child > [data-testid="stVerticalBlock"] {{
                height: auto !important;
                min-height: auto !important;
                max-height: none !important;
                overflow: visible !important;
            }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_login_ambience() -> None:
    st.markdown(
        """
        <div class="login-ambience" aria-hidden="true">
            <div class="login-mesh"></div>
            <div class="login-grid"></div>
            <span class="login-orb login-orb-1"></span>
            <span class="login-orb login-orb-2"></span>
            <span class="login-orb login-orb-3"></span>
            <span class="login-orb login-orb-4"></span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_login_theme_toggle(*, key: str = "login_theme") -> None:
    importlib.reload(theme_mod)
    light = theme_mod.get_theme() == "light"
    icon = "🌙" if light else "☀️"
    help_text = "Switch to dark mode" if light else "Switch to light mode"
    if st.button(icon, key=key, help=help_text):
        theme_mod.toggle_theme()
        st.rerun()


def render_login_brand_panel() -> None:
    tok = _tokens()
    title = html.escape(_label("home.title", en="KASLU LAB", zh="卡琉实验室"))
    tag = html.escape(_label("home.brand_tag", en="Caspian Bridge · Lab Platform", zh="里海—长江 · 实验平台"))
    ready = html.escape(_label("home.lab_ready", en="Lab systems ready", zh="实验系统就绪"))
    features = [
        html.escape(_label("home.feature_1", en="Precision-driven laboratory research", zh="精准驱动的实验室研究")),
        html.escape(_label("home.feature_2", en="Secure, private workspace for your team", zh="安全私密的团队工作空间")),
        html.escape(_label("home.feature_3", en="Built for modern science & collaboration", zh="为现代科研与协作而设计")),
    ]
    logo_src = logo_data_uri()
    feat_html = "".join(
        f'<li class="f" style="animation-delay:{0.15+i*0.11}s">'
        f'<span class="n">{i+1:02d}</span><span class="t">{text}</span></li>'
        for i, text in enumerate(features)
    )
    panel = f"""
    <!DOCTYPE html><html><head><meta charset="utf-8"><style>
      *{{box-sizing:border-box;margin:0;padding:0}}
      body{{font-family:'Plus Jakarta Sans',system-ui,sans-serif;background:transparent;overflow:hidden}}
      .panel{{
        position:relative;min-height:{LOGIN_PANEL_H}px;height:{LOGIN_PANEL_H}px;border-radius:22px;
        border:1px solid color-mix(in srgb,{tok["accent"]} 30%,{tok["border"]});
        background:linear-gradient(148deg,{tok["surface"]} 0%,{tok["primary_soft"]} 48%,color-mix(in srgb,{tok["accent"]} 12%,{tok["surface"]}) 100%);
        background-size:220% 220%;animation:grad 20s ease infinite;
        box-shadow:0 18px 50px rgba(21,101,192,0.14);overflow:hidden;
      }}
      @keyframes grad{{0%,100%{{background-position:0% 50%}}50%{{background-position:100% 50%}}}}
      .panel::before{{
        content:"";position:absolute;inset:0;
        background-image:radial-gradient(circle at 1px 1px,rgba(21,101,192,0.09) 1px,transparent 0);
        background-size:20px 20px;opacity:.55
      }}
      .glow{{
        position:absolute;width:250px;height:250px;right:-70px;top:-70px;border-radius:50%;
        background:radial-gradient(circle,rgba(8,145,178,0.22),transparent 68%);
        animation:float 20s ease-in-out infinite
      }}
      @keyframes float{{0%,100%{{transform:translate(0,0)}}50%{{transform:translate(-10px,14px)}}}}
      .in{{position:relative;z-index:1;padding:1.35rem 1.4rem;animation:up .65s ease both}}
      @keyframes up{{from{{opacity:0;transform:translateY(14px)}}to{{opacity:1;transform:translateY(0)}}}}
      .ring{{position:relative;width:82px;height:82px;margin-bottom:.85rem}}
      .ring::before{{
        content:"";position:absolute;inset:-5px;border-radius:22px;
        background:conic-gradient(from 0deg,{tok["primary"]},{tok["accent"]},{tok["kaslu_green"]},{tok["primary"]});
        opacity:.55;animation:spin 14s linear infinite
      }}
      @keyframes spin{{to{{transform:rotate(360deg)}}}}
      .ring img{{
        position:relative;z-index:1;width:70px;height:70px;margin:6px;border-radius:16px;
        animation:lg 4.5s ease-in-out infinite
      }}
      @keyframes lg{{
        0%,100%{{filter:drop-shadow(0 4px 14px rgba(21,101,192,0.28))}}
        50%{{filter:drop-shadow(0 8px 22px rgba(8,145,178,0.35))}}
      }}
      h1{{font-size:1.38rem;font-weight:800;letter-spacing:.06em;color:{tok["heading"]};margin-bottom:.18rem}}
      .tag{{font-size:.64rem;font-weight:600;letter-spacing:.12em;text-transform:uppercase;color:{tok["text_muted"]};margin-bottom:.5rem;line-height:1.4}}
      .status{{
        display:inline-flex;align-items:center;gap:.42rem;font-size:.71rem;font-weight:600;
        color:{tok["kaslu_green"]};background:color-mix(in srgb,{tok["kaslu_green"]} 12%,{tok["surface"]});
        border:1px solid color-mix(in srgb,{tok["kaslu_green"]} 28%,{tok["border"]});
        border-radius:999px;padding:.22rem .5rem;margin-bottom:.65rem
      }}
      .dot{{width:7px;height:7px;border-radius:50%;background:{tok["kaslu_green"]};animation:pulse 2.4s ease-in-out infinite}}
      @keyframes pulse{{0%,100%{{opacity:1;transform:scale(1)}}50%{{opacity:.45;transform:scale(.85)}}}}
      ul{{list-style:none;display:flex;flex-direction:column;gap:.32rem}}
      .f{{
        display:flex;align-items:center;gap:.55rem;padding:.46rem .58rem;border-radius:12px;
        background:color-mix(in srgb,{tok["surface"]} 82%,transparent);
        border:1px solid color-mix(in srgb,{tok["border"]} 80%,transparent);
        animation:up .52s ease both;transition:transform .22s ease,border-color .22s ease,box-shadow .22s ease
      }}
      .f:hover{{transform:translateX(4px);border-color:{tok["accent"]};box-shadow:0 4px 16px rgba(21,101,192,0.1)}}
      .n{{
        display:flex;align-items:center;justify-content:center;
        width:1.85rem;height:1.85rem;font-size:.62rem;font-weight:800;
        color:{tok["primary_text"]};background:{tok["primary_soft"]};
        border-radius:999px;flex-shrink:0;line-height:1
      }}
      .t{{font-size:.8rem;font-weight:500;line-height:1.35;color:{tok["text"]};flex:1}}
      @media(prefers-reduced-motion:reduce){{*,*::before,*::after{{animation:none!important;transition:none!important}}}}
    </style></head><body>
      <div class="panel"><div class="glow"></div><div class="in">
        <div class="ring"><img src="{logo_src}" alt="{title}"></div>
        <h1>{title}</h1><p class="tag">{tag}</p>
        <div class="status"><span class="dot"></span><span>{ready}</span></div>
        <ul>{feat_html}</ul>
      </div></div>
    </body></html>
    """
    components.html(panel, height=LOGIN_PANEL_H, scrolling=False)


def render_login_form_header(*, mode: str) -> None:
    is_register = mode == "register"
    if is_register:
        eyebrow = _label("home.register_eyebrow", en="New workspace", zh="新工作台")
        title = _label("home.register", en="Register", zh="注册")
        subtitle = _label(
            "home.register_sub",
            en="Create your workspace — one account for all lab tools.",
            zh="创建工作台 — 一个账户管理全部实验工具。",
        )
    else:
        eyebrow = _label("home.login_eyebrow", en="Lab workspace", zh="实验室工作台")
        title = _label("home.login", en="Login", zh="登录")
        subtitle = _label(
            "home.login_sub",
            en="Welcome back — sign in to continue your research.",
            zh="欢迎回来 — 登录以继续您的研究。",
        )
    st.markdown(
        f"""
        <div class="login-dynamic-header">
            <p class="login-form-eyebrow">{html.escape(eyebrow)}</p>
            <h2 class="login-form-title">{html.escape(title)}</h2>
            <p class="login-form-caption">{html.escape(subtitle)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_login_secure_note() -> None:
    note = _label(
        "home.secure_note",
        en="Your data stays in your lab workspace.",
        zh="数据保存在您的实验室工作台中。",
    )
    st.markdown(
        f'<p class="login-secure-note"><span aria-hidden="true">🔒</span> {html.escape(note)}</p>',
        unsafe_allow_html=True,
    )
