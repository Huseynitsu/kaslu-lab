"""AI recommendations for operation logs — detailed per-section analysis."""

from __future__ import annotations

import json
import os
from typing import Literal

import httpx
import streamlit as st

from core.i18n import bilingual
from core.operation_log import OperationLogResult
from core.operation_log_sections import SectionAdvice, build_section_analyses

ProviderId = Literal["rule_based", "gpt", "claude", "deepseek", "perplexity"]

PROVIDER_CONFIG = {
    "gpt": {
        "env_key": "OPENAI_API_KEY",
        "session_key": "api_key_openai",
        "model_env": "OPENAI_MODEL",
        "default_model": "gpt-4o-mini",
        "url": "https://api.openai.com/v1/chat/completions",
        "style": "openai",
    },
    "claude": {
        "env_key": "ANTHROPIC_API_KEY",
        "session_key": "api_key_claude",
        "model_env": "ANTHROPIC_MODEL",
        "default_model": "claude-3-5-haiku-latest",
        "url": "https://api.anthropic.com/v1/messages",
        "style": "claude",
    },
    "deepseek": {
        "env_key": "DEEPSEEK_API_KEY",
        "session_key": "api_key_deepseek",
        "model_env": "DEEPSEEK_MODEL",
        "default_model": "deepseek-chat",
        "url": "https://api.deepseek.com/v1/chat/completions",
        "style": "openai",
    },
    "perplexity": {
        "env_key": "PERPLEXITY_API_KEY",
        "session_key": "api_key_perplexity",
        "model_env": "PERPLEXITY_MODEL",
        "default_model": "sonar",
        "url": "https://api.perplexity.ai/chat/completions",
        "style": "openai",
    },
}


def get_api_key(provider: ProviderId) -> str | None:
    if provider == "rule_based":
        return None
    cfg = PROVIDER_CONFIG[provider]
    session_val = st.session_state.get(cfg["session_key"], "").strip()
    if session_val:
        return session_val
    env_val = os.environ.get(cfg["env_key"], "").strip()
    return env_val or None


def provider_available(provider: ProviderId) -> bool:
    if provider == "rule_based":
        return True
    return bool(get_api_key(provider))


def provider_key_hint(provider: ProviderId) -> str:
    cfg = PROVIDER_CONFIG[provider]
    return cfg["env_key"]


def _sections_to_prompt(sections: list[SectionAdvice], result: OperationLogResult) -> str:
    lang = "English with Chinese terms in parentheses where helpful"
    blocks = [
        f"Respond in {lang}.",
        f"Source file: {result.source_name}, records: {result.summary.row_count}",
        "For EACH section below, write: (1) a detailed 3-5 sentence analysis of the trend, "
        "(2) 2-4 bullet recommendations. Use only the statistics given.",
        "",
    ]
    for sec in sections:
        blocks.append(f"## {sec.title}")
        blocks.append(f"Summary: {sec.summary}")
        for h in sec.highlights:
            blocks.append(f"- {h.label}: {h.value} ({h.caption})")
        blocks.append(f"Initial notes: {'; '.join(sec.recommendations)}")
        blocks.append("")
    return "\n".join(blocks)


def _L(en: str, zh: str) -> str:
    return bilingual(en, zh)


def get_detailed_recommendations(
    provider: ProviderId,
    result: OperationLogResult,
    *,
    fa_ph: float = 7.5,
    fa_temp: float = 35.0,
) -> tuple[ProviderId, list[SectionAdvice], str | None]:
    """
    Returns (provider_used, section_advice_list, error_message).
    error_message is set only when external provider failed; rule-based still returned.
    """
    sections = build_section_analyses(result, fa_ph=fa_ph, fa_temp=fa_temp)
    if not sections:
        empty = SectionAdvice(
            section_id="general",
            title=_L("General", "总体"),
            summary=_L("Not enough columns to analyze charts.", "列数据不足，无法分析图表。"),
            recommendations=[_L("Upload a log with NH4 influent/effluent columns.", "请上传含 NH4 进水/出水的日志。")],
        )
        return "rule_based", [empty], None

    if provider == "rule_based":
        return "rule_based", sections, None

    api_key = get_api_key(provider)
    if not api_key:
        # No paid API — silently use built-in detailed analysis (provider choice kept for future use).
        return "rule_based", sections, None

    prompt = (
        "Return ONLY a JSON array. Each item: "
        '{"section_id": "...", "analysis": "3-5 detailed sentences", "recommendations": ["...", "..."]}. '
        "One item per section_id listed below.\n\n"
        + _sections_to_prompt(sections, result)
    )
    try:
        text = _call_provider(provider, api_key, prompt)
        merged = _merge_ai_response(text, sections)
        return provider, merged, None
    except Exception as exc:
        err = _L(f"AI request failed: {exc}", f"AI 请求失败：{exc}")
        return "rule_based", sections, err


def _merge_ai_response(text: str, fallback: list[SectionAdvice]) -> list[SectionAdvice]:
    text = text.strip()
    start = text.find("[")
    end = text.rfind("]")
    if start >= 0 and end > start:
        try:
            payload = json.loads(text[start : end + 1])
            by_id = {item.get("section_id"): item for item in payload if isinstance(item, dict)}
            merged: list[SectionAdvice] = []
            for sec in fallback:
                ai = by_id.get(sec.section_id, {})
                recs = ai.get("recommendations") or sec.recommendations
                if isinstance(recs, str):
                    recs = [recs]
                merged.append(
                    SectionAdvice(
                        section_id=sec.section_id,
                        title=sec.title,
                        summary=str(ai.get("analysis") or sec.summary),
                        highlights=sec.highlights,
                        recommendations=[str(r) for r in recs if str(r).strip()],
                    )
                )
            return merged
        except json.JSONDecodeError:
            pass

    return [
        SectionAdvice(
            section_id=sec.section_id,
            title=sec.title,
            summary=sec.summary,
            highlights=sec.highlights,
            recommendations=sec.recommendations,
        )
        for sec in fallback
    ]


def _call_provider(provider: ProviderId, api_key: str, prompt: str) -> str:
    cfg = PROVIDER_CONFIG[provider]
    if cfg["style"] == "claude":
        return _call_claude(api_key, cfg, prompt)
    model = os.environ.get(cfg["model_env"], cfg["default_model"])
    return _openai_compatible(api_key, model, cfg["url"], prompt)


def _openai_compatible(api_key: str, model: str, url: str, prompt: str) -> str:
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "You are an expert on PN/Anammox lab reactors. Give detailed, structured operational advice.",
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.3,
        "max_tokens": 2000,
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    with httpx.Client(timeout=90.0) as client:
        resp = client.post(url, headers=headers, json=payload)
        if resp.status_code == 401:
            raise ValueError("Invalid API key (401 Unauthorized). Check your key and try again.")
        if resp.status_code == 403:
            raise ValueError("API access forbidden (403). Check billing or permissions.")
        resp.raise_for_status()
        data = resp.json()
    return data["choices"][0]["message"]["content"]


def _call_claude(api_key: str, cfg: dict, prompt: str) -> str:
    model = os.environ.get(cfg["model_env"], cfg["default_model"])
    payload = {
        "model": model,
        "max_tokens": 2000,
        "messages": [{"role": "user", "content": prompt}],
    }
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json",
    }
    with httpx.Client(timeout=90.0) as client:
        resp = client.post(cfg["url"], headers=headers, json=payload)
        if resp.status_code == 401:
            raise ValueError("Invalid Anthropic API key (401).")
        resp.raise_for_status()
        data = resp.json()
    parts = data.get("content", [])
    return "".join(p.get("text", "") for p in parts if p.get("type") == "text")
