"""Bilingual UI strings — English with Chinese in parentheses."""

from __future__ import annotations

import streamlit as st

LANG_KEY = "ui_lang"

MESSAGES: dict[str, dict[str, str]] = {
    # Layout / chrome
    "brand.title": {"en": "KASLU LAB", "zh": "卡琉实验室"},
    "brand.sub": {
        "en": "Kaslu Lab Platform",
        "zh": "卡琉实验平台",
    },
    "seo.description": {
        "en": "KASLU LAB — Caspian Bridge lab platform for reactor operation logs, sample analysis, performance monitoring, and research tools.",
        "zh": "卡琉实验室 — 里海—长江实验平台：反应器运行日志、样品分析、性能监控与研究工具。",
    },
    "seo.keywords": {
        "en": "KASLU LAB, lab platform, reactor operation log, nitrogen removal, wastewater, experiment analysis",
        "zh": "卡琉实验室, 实验平台, 反应器运行日志, 脱氮, 废水, 实验分析",
    },
    "nav.workflow": {"en": "Workflow", "zh": "工作流程"},
    "nav.lab_tools": {"en": "Lab tools", "zh": "实验工具"},
    "nav.research": {"en": "Research", "zh": "研究模块"},
    "nav.admin": {"en": "Administration", "zh": "管理"},
    "nav.dashboard": {"en": "Dashboard", "zh": "仪表板"},
    "nav.operation_log": {"en": "Reactor Operation Log", "zh": "反应器运行日志"},
    "nav.sample": {"en": "Sample Analysis", "zh": "样品分析"},
    "nav.simulation": {"en": "Performance Analysis", "zh": "性能分析"},
    "nav.history": {"en": "History", "zh": "历史记录"},
    "nav.advisor": {"en": "AI Advisor", "zh": "AI 顾问"},
    "nav.pn": {"en": "PN Monitor", "zh": "PN 监控"},
    "nav.stoich": {"en": "Stoichiometry", "zh": "化学计量"},
    "nav.diagnostics": {"en": "Daily Diagnostics", "zh": "每日诊断"},
    "nav.analytics": {"en": "Experiment Analysis", "zh": "实验分析"},
    "nav.sensitivity": {"en": "Sensitivity", "zh": "敏感性分析"},
    "nav.exp_details": {"en": "Experiment Details", "zh": "实验详情"},
    "nav.prediction": {"en": "Hybrid / ML Prediction", "zh": "混合 / ML 预测"},
    "nav.optimization": {"en": "Optimization", "zh": "优化"},
    "nav.monte_carlo": {"en": "Monte Carlo", "zh": "蒙特卡洛"},
    "nav.comparison": {"en": "Comparison", "zh": "对比"},
    "nav.pdf_report": {"en": "PDF Report", "zh": "PDF 报告"},
    "nav.admin_panel": {"en": "Admin Panel", "zh": "管理面板"},
    "ui.back": {"en": "← Back", "zh": "← 返回"},
    "ui.back_short": {"en": "Back", "zh": "返回"},
    "ui.home": {"en": "Home", "zh": "首页"},
    "ui.home_short": {"en": "Home", "zh": "首页"},
    "ui.logout": {"en": "Logout", "zh": "退出登录"},
    "ui.logout_short": {"en": "Sign out", "zh": "退出"},
    "ui.dismiss": {"en": "Dismiss", "zh": "关闭"},
    "ui.theme": {"en": "Theme", "zh": "主题"},
    "ui.theme_light": {"en": "Light", "zh": "浅色"},
    "ui.theme_dark": {"en": "Dark", "zh": "深色"},
    "ui.theme_light_short": {"en": "Light", "zh": "浅"},
    "ui.theme_dark_short": {"en": "Dark", "zh": "深"},
    "ui.signed_in": {"en": "Signed in as", "zh": "当前用户"},
    "ui.account": {"en": "Account", "zh": "账户"},
    # Home
    "home.title": {"en": "KASLU LAB", "zh": "卡琉实验室"},
    "home.caption": {
        "en": "Sign in to your lab workspace — journal, analysis, monitoring, and research tools.",
        "zh": "登录实验室工作台 — 日志导入、分析、监控与研究工具。",
    },
    "home.brand_tag": {
        "en": "Caspian Bridge · Lab Platform",
        "zh": "里海—长江 · 实验平台",
    },
    "home.login_eyebrow": {"en": "Lab workspace", "zh": "实验室工作台"},
    "home.register_eyebrow": {"en": "New workspace", "zh": "新工作台"},
    "home.login_sub": {
        "en": "Welcome back — pick up where your last experiment left off.",
        "zh": "欢迎回来 — 从上次实验继续。",
    },
    "home.register_sub": {
        "en": "Create your workspace — one account for logs, charts, and research.",
        "zh": "创建工作台 — 一个账户管理日志、图表与研究。",
    },
    "home.feature_1": {
        "en": "Precision-driven laboratory research",
        "zh": "精准驱动的实验室研究",
    },
    "home.feature_2": {
        "en": "Secure, private workspace for your team",
        "zh": "安全私密的团队工作空间",
    },
    "home.feature_3": {
        "en": "Built for modern science & collaboration",
        "zh": "为现代科研与协作而设计",
    },
    "home.secure_note": {
        "en": "Your data stays in your lab workspace.",
        "zh": "数据保存在您的实验室工作台中。",
    },
    "home.lab_ready": {"en": "Lab systems ready", "zh": "实验系统就绪"},
    "home.mode": {"en": "Mode", "zh": "模式"},
    "home.login": {"en": "Login", "zh": "登录"},
    "home.register": {"en": "Register", "zh": "注册"},
    "home.username": {"en": "Username", "zh": "用户名"},
    "home.password": {"en": "Password", "zh": "密码"},
    "home.sign_in": {"en": "Sign in", "zh": "登录"},
    "home.create_account": {"en": "Create account", "zh": "创建账户"},
    "home.account_created": {"en": "Account created — you can log in now.", "zh": "账户已创建 — 现在可以登录。"},
    "home.username_exists": {"en": "Username already exists.", "zh": "用户名已存在。"},
    "home.invalid_login": {"en": "Invalid username or password.", "zh": "用户名或密码无效。"},
    # Dashboard
    "dash.title": {"en": "KASLU LAB Dashboard", "zh": "卡琉实验室 仪表板"},
    "dash.caption": {
        "en": "Caspian Bridge Lab Platform — journal, analysis, monitoring, research",
        "zh": "里海—长江实验平台 — 日志、分析、监控与研究",
    },
    "dash.welcome": {
        "en": "Welcome back — track samples, compare reactor performance, and review saved experiments.",
        "zh": "欢迎回来 — 跟踪样品、比较反应器性能并查看已保存的实验。",
    },
    "dash.workflow": {"en": "Recommended workflow", "zh": "推荐工作流程"},
    "dash.open": {"en": "Open →", "zh": "打开 →"},
    "dash.recent_sims": {"en": "Recent simulations", "zh": "最近模拟"},
    "dash.recent_readings": {"en": "Recent lab readings", "zh": "最近实验读数"},
    "dash.no_sims": {"en": "No simulations yet.", "zh": "尚无模拟记录。"},
    "dash.no_readings": {"en": "No lab readings yet.", "zh": "尚无实验读数。"},
    # Operation log
    "oplog.title": {"en": "Reactor Operation Log", "zh": "反应器运行日志"},
    "oplog.intro": {
        "en": "Upload the **lab Excel journal**. The system **auto-detects columns** (missing columns are OK). Charts use **duration time (days)** on X and **concentration (mg-N/L)** on Y.",
        "zh": "上传 **实验室 Excel 日志**。系统会 **自动识别列**（缺少部分列也可以）。图表 X 轴为 **运行时间（天）**，Y 轴为 **浓度 (mg-N/L)**。",
    },
    "oplog.load_data": {"en": "Load data", "zh": "加载数据"},
    "oplog.upload": {"en": "Excel file (.xlsx)", "zh": "Excel 文件 (.xlsx)"},
    "oplog.load_sample": {"en": "Load sample from Desktop", "zh": "从桌面加载样本"},
    "oplog.sample_missing": {"en": "Sample file not found on Desktop.", "zh": "桌面上未找到样本文件。"},
    "oplog.inhibition_shared_ph": {
        "en": "pH and temperature for FA and FNA (not in Excel yet)",
        "zh": "FA 与 FNA 共用的 pH、温度（Excel 中尚无）",
    },
    "oplog.fa_optional": {"en": "About FA (free ammonia)", "zh": "关于 FA（游离氨）"},
    "oplog.fa_hint": {
        "en": "FA (NH₃-N) is calculated from influent NH₄-N, pH, and temperature (Anthonisen).",
        "zh": "FA（NH₃-N）由进水 NH₄-N、pH 与温度估算（Anthonisen）。",
    },
    "oplog.fna_optional": {"en": "About FNA (free nitrous acid)", "zh": "关于 FNA（游离亚硝酸）"},
    "oplog.fna_hint": {
        "en": "FNA (HNO₂-N) is calculated from NO₂ effluent (as N), pH, and temperature (Anthonisen).",
        "zh": "FNA（HNO₂-N）由 NO₂ 出水（以 N 计）、pH 与温度估算（Anthonisen）。",
    },
    "oplog.fa_formula": {
        "en": "FA (mg/L NH₃-N) = NH₄ influent / (1 + 10^(pKa − pH))",
        "zh": "FA (mg/L NH₃-N) = NH₄ 进水 / (1 + 10^(pKa − pH))",
    },
    "oplog.fna_formula": {
        "en": "FNA (mg/L HNO₂-N) = NO₂ effluent / (1 + 10^(pH − pKa))",
        "zh": "FNA (mg/L HNO₂-N) = NO₂ 出水 / (1 + 10^(pH − pKa))",
    },
    "oplog.fa_missing_nh4": {
        "en": "Add influent NH₄ column to chart FA.",
        "zh": "请添加 NH₄ 进水列以绘制 FA。",
    },
    "oplog.fna_missing_no2": {
        "en": "Add NO₂ effluent column to chart FNA.",
        "zh": "请添加 NO₂ 出水列以绘制 FNA。",
    },
    "oplog.empty": {
        "en": "Upload your `.xlsx` file or click **Load sample from Desktop** in the sidebar.",
        "zh": "上传 `.xlsx` 文件，或在侧边栏点击 **从桌面加载样本**。",
    },
    "oplog.empty_heading": {"en": "No data loaded yet", "zh": "尚未加载数据"},
    "oplog.steps.upload": {"en": "Upload Excel", "zh": "上传 Excel"},
    "oplog.steps.preview": {"en": "Preview summary", "zh": "预览摘要"},
    "oplog.steps.charts": {"en": "Explore charts", "zh": "查看图表"},
    "oplog.parsing": {"en": "Parsing workbook…", "zh": "正在解析工作簿…"},
    "oplog.file_ready": {
        "en": "Ready: **{name}** ({count} rows)",
        "zh": "已就绪：**{name}**（{count} 行）",
    },
    "oplog.data_quality": {"en": "Data quality", "zh": "数据质量"},
    "oplog.dq.detected": {"en": "Detected columns", "zh": "已识别列"},
    "oplog.dq.missing": {"en": "Missing (optional)", "zh": "缺失（可选）"},
    "oplog.dq.warnings": {"en": "Parse warnings", "zh": "解析警告"},
    "oplog.dq.alerts": {"en": "Alerts", "zh": "提醒"},
    "oplog.help.date_range": {
        "en": "First date in the journal after parsing.",
        "zh": "解析后日志中的首个日期。",
    },
    "oplog.help.to": {
        "en": "Last date in the journal after parsing.",
        "zh": "解析后日志中的最后日期。",
    },
    "oplog.help.duration": {
        "en": "Min–max operation duration in days (X-axis for charts).",
        "zh": "运行天数的最小–最大范围（图表 X 轴）。",
    },
    "oplog.help.mean_r1": {
        "en": "Mean NH₄ removal efficiency for Reactor 1 over all rows.",
        "zh": "反应器 1 全部行的平均 NH₄ 去除率。",
    },
    "oplog.help.mean_r2": {
        "en": "Mean NH₄ removal for Reactor 2. Delta arrow shows change vs R1 mean.",
        "zh": "反应器 2 平均 NH₄ 去除率；箭头表示相对 R1 均值的差值。",
    },
    "oplog.loaded": {"en": "Loaded **{name}** — {count} records", "zh": "已加载 **{name}** — {count} 条记录"},
    "oplog.schema_detected": {"en": "Auto-detected columns", "zh": "自动识别的列"},
    "oplog.schema_missing": {"en": "Not found (optional)", "zh": "未找到（可选）"},
    "oplog.date_range": {"en": "Date range", "zh": "日期范围"},
    "oplog.to": {"en": "To", "zh": "至"},
    "oplog.duration": {"en": "Duration (days)", "zh": "运行时间（天）"},
    "oplog.mean_r1": {"en": "Mean NH₄ removal R1", "zh": "平均 NH₄ 去除率 R1"},
    "oplog.mean_r2": {"en": "Mean NH₄ removal R2", "zh": "平均 NH₄ 去除率 R2"},
    "oplog.formula_ok": {
        "en": "Removal rate check: (Influent − Effluent) / Influent matches Excel (max error {err:.4f}%).",
        "zh": "去除率检查：(进水 − 出水) / 进水 与 Excel 一致（最大误差 {err:.4f}%）。",
    },
    "oplog.alert.formula_mismatch": {
        "en": "NH₄ removal rate differs from formula by up to {err:.2f}% — check Excel.",
        "zh": "NH₄ 去除率与公式相差最多 {err:.2f}% — 请检查 Excel。",
    },
    "oplog.alert.r1_mean_low": {
        "en": "Reactor (1) mean NH₄ removal is low ({pct:.1f}%).",
        "zh": "反应器 (1) 平均 NH₄ 去除率偏低（{pct:.1f}%）。",
    },
    "oplog.alert.r1_latest_low": {
        "en": "Latest Reactor (1) NH₄ removal is below 80% — check recent operation.",
        "zh": "反应器 (1) 最新 NH₄ 去除率低于 80% — 请检查近期运行。",
    },
    "oplog.alert.tn_nh4_diff": {
        "en": "TN influent differs from NH₄ influent — total nitrogen includes other N forms.",
        "zh": "TN 进水与 NH₄ 进水不一致 — 总氮包含其他氮形态。",
    },
    "oplog.tab.nh4": {"en": "NH₄ vs duration", "zh": "NH₄ vs 运行时间"},
    "oplog.tab.removal": {"en": "Removal rate", "zh": "去除率"},
    "oplog.tab.tn": {"en": "TN", "zh": "总氮 TN"},
    "oplog.tab.ops": {"en": "ANR & loading", "zh": "ANR 与负荷"},
    "oplog.tab.compare": {"en": "Reactor 1 vs 2", "zh": "反应器 1 vs 2"},
    "oplog.tab.fa": {"en": "FA (free ammonia)", "zh": "FA（游离氨）"},
    "oplog.tab.fna": {"en": "FNA (free nitrous acid)", "zh": "FNA（游离亚硝酸）"},
    "oplog.tab.data": {"en": "Raw table", "zh": "原始数据"},
    "oplog.compare.r1": {"en": "Latest R1 effluent", "zh": "R1 最新出水"},
    "oplog.compare.r2": {"en": "Latest R2 effluent", "zh": "R2 最新出水"},
    "oplog.compare.diff": {"en": "R2 − R1", "zh": "R2 − R1"},
    "oplog.download_csv": {"en": "Download CSV", "zh": "下载 CSV"},
    "oplog.ai.title": {"en": "AI recommendations", "zh": "AI 建议"},
    "oplog.ai.provider": {"en": "Select AI provider", "zh": "选择 AI 提供商"},
    "oplog.ai.get": {"en": "Get recommendations", "zh": "获取建议"},
    "oplog.ai.no_key": {
        "en": "Enter API key in sidebar → **API keys**, or create `.env` from `.env.example`.",
        "zh": "请在侧边栏 → **API 密钥** 中输入，或从 `.env.example` 创建 `.env` 文件。",
    },
    "oplog.ai.api_keys": {"en": "API keys (optional)", "zh": "API 密钥（可选）"},
    "oplog.ai.api_hint": {
        "en": "Keys stay in this session only. Or set in project `.env` file.",
        "zh": "密钥仅保存在当前会话。也可在项目 `.env` 文件中设置。",
    },
    "oplog.ai.analysis": {"en": "Analysis", "zh": "分析"},
    "oplog.ai.actions": {"en": "Recommendations", "zh": "建议措施"},
    "oplog.ai.fallback": {
        "en": "Showing built-in detailed analysis (external AI unavailable).",
        "zh": "显示内置详细分析（外部 AI 不可用）。",
    },
    "oplog.ai.rule_based": {"en": "Built-in analysis (free)", "zh": "内置分析（免费）"},
    "oplog.ai.providers.gpt": {"en": "OpenAI GPT (paid API)", "zh": "OpenAI GPT（付费 API）"},
    "oplog.ai.providers.claude": {"en": "Anthropic Claude (paid API)", "zh": "Anthropic Claude（付费 API）"},
    "oplog.ai.providers.deepseek": {"en": "DeepSeek (paid API)", "zh": "DeepSeek（付费 API）"},
    "oplog.ai.providers.perplexity": {"en": "Perplexity (paid API)", "zh": "Perplexity（付费 API）"},
}


def bilingual(en: str, zh: str | None = None) -> str:
    """English label with Chinese translation in parentheses."""
    if not zh or zh.strip() == en.strip():
        return en
    return f"{en} ({zh})"


def init_lang(default: str = "en") -> None:
    if LANG_KEY not in st.session_state:
        st.session_state[LANG_KEY] = default


def get_lang() -> str:
    """Kept for compatibility — UI is always bilingual English-first."""
    return "en"


def t(key: str, **kwargs) -> str:
    entry = MESSAGES.get(key, {})
    en = entry.get("en") or key
    zh = entry.get("zh")
    text = bilingual(en, zh)
    return text.format(**kwargs) if kwargs else text


def t_en(key: str, **kwargs) -> str:
    """English-only string for compact toolbar controls (tooltips stay bilingual via t())."""
    entry = MESSAGES.get(key, {})
    en = entry.get("en") or key
    return en.format(**kwargs) if kwargs else en
