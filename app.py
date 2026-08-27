import json
from pathlib import Path

import streamlit as st

# ---------------------------------------------------------------------------
# Fix: when an f-string built for unsafe_allow_html markdown contains a
# conditionally-empty placeholder (e.g. a badge that's "" for some cases),
# that line becomes blank. CommonMark treats a blank line as the end of a
# raw-HTML block, so everything after it gets parsed as plain indented text
# instead of HTML — showing up as literal code on screen. Stripping blank
# lines before handing the string to Streamlit's markdown renderer avoids
# this for every call site in this file.
_original_markdown = st.markdown

def _markdown_no_blank_lines(body, *args, **kwargs):
    if kwargs.get("unsafe_allow_html") and isinstance(body, str):
        body = "\n".join(line for line in body.split("\n") if line.strip() != "")
    return _original_markdown(body, *args, **kwargs)

st.markdown = _markdown_no_blank_lines

st.set_page_config(
    page_title="Discharge Worklist — NexusCare AI",
    page_icon="✚",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# Data loading — exact same demo_export.json used by the live Lovable app
# ---------------------------------------------------------------------------
DATA_PATH = Path(__file__).parent / "demo_export.json"

@st.cache_data
def load_cases():
    with open(DATA_PATH, "r") as f:
        return json.load(f)

cases = load_cases()
cases = sorted(cases, key=lambda c: c["risk_score"], reverse=True)

# ---------------------------------------------------------------------------
# Color tokens — matched to the live app's CSS custom properties
# ---------------------------------------------------------------------------
COLORS = {
    "background": "#eef4f2",
    "foreground": "#1d3336",
    "card": "#ffffff",
    "primary": "#2c7688",
    "primary_foreground": "#fbfdfc",
    "secondary": "#dde8e7",
    "secondary_foreground": "#2e4448",
    "muted": "#e6ece9",
    "muted_foreground": "#5c6f70",
    "accent": "#d7e7e5",
    "accent_foreground": "#293e42",
    "border": "#cddad8",
    "header": "#1d3336",
    "header_foreground": "#eef3f2",
    "risk_high": "#c1432c",
    "risk_high_foreground": "#fdf7f6",
    "risk_high_soft": "#f8e2dd",
    "risk_medium": "#c0862f",
    "risk_medium_foreground": "#4a3418",
    "risk_medium_soft": "#f6ecd8",
    "risk_low": "#2d7c5e",
    "risk_low_foreground": "#fbfdfc",
    "risk_low_soft": "#e2f0e7",
    "success": "#2b7a5b",
    "success_soft": "#e2f0e7",
    "destructive": "#c1432c",
}


def risk_level(record):
    tier = record["risk_tier"].lower()
    if tier.startswith("high"):
        return "high"
    if tier.startswith("medium"):
        return "medium"
    return "low"


LEVEL_COLOR = {
    "high": COLORS["risk_high"],
    "medium": COLORS["risk_medium"],
    "low": COLORS["risk_low"],
}
LEVEL_SOFT = {
    "high": COLORS["risk_high_soft"],
    "medium": COLORS["risk_medium_soft"],
    "low": COLORS["risk_low_soft"],
}
LEVEL_FG = {
    "high": COLORS["risk_high_foreground"],
    "medium": COLORS["risk_medium_foreground"],
    "low": COLORS["risk_low_foreground"],
}

STEP_ICONS = ["⚖", "🔍", "✎", "🛡", "📅"]
CADENCE = {
    "high": "High-risk protocol · within 7 days",
    "medium": "Medium-risk protocol · within 14 days",
    "low": "Low-risk protocol · routine window",
}

# ---------------------------------------------------------------------------
# Global CSS
# ---------------------------------------------------------------------------
st.markdown(
    f"""
    <style>
    .stApp {{
        background: {COLORS['background']};
    }}
    #MainMenu, footer, header {{visibility: hidden;}}
    .block-container {{
        padding-top: 1rem;
        padding-bottom: 2rem;
        max-width: 100%;
    }}
    * {{
        font-family: -apple-system, "Segoe UI", Roboto, sans-serif;
    }}

    .nc-header {{
        display: flex; align-items: center; gap: 12px;
        background: {COLORS['header']}; color: {COLORS['header_foreground']};
        padding: 14px 20px; border-radius: 10px; margin-bottom: 18px;
    }}
    .nc-header .logo {{
        display: flex; align-items: center; justify-content: center;
        width: 34px; height: 34px; border-radius: 8px; background: {COLORS['primary']};
        color: white; font-weight: 700; font-size: 18px; flex-shrink: 0;
    }}
    .nc-header .title {{ font-size: 16px; font-weight: 700; line-height: 1.2; }}
    .nc-header .subtitle {{ font-size: 11px; opacity: 0.7; line-height: 1.2; }}
    .nc-header .badge {{
        margin-left: auto; border: 1px solid rgba(255,255,255,0.25);
        padding: 5px 10px; border-radius: 999px; font-size: 11px; font-weight: 500;
    }}
    .nc-header .avatar {{
        width: 32px; height: 32px; border-radius: 999px; background: {COLORS['accent']};
        color: {COLORS['accent_foreground']}; display: flex; align-items: center;
        justify-content: center; font-size: 12px; font-weight: 700;
    }}

    .nc-card {{
        background: {COLORS['card']}; border: 1px solid {COLORS['border']};
        border-radius: 12px; padding: 18px 20px; margin-bottom: 18px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }}

    .nc-badge {{
        display: inline-flex; align-items: center; gap: 6px;
        border-radius: 999px; padding: 3px 10px; font-size: 11px;
        font-weight: 700; letter-spacing: 0.02em; text-transform: uppercase;
    }}
    .nc-dot {{ width: 6px; height: 6px; border-radius: 999px; background: currentColor; }}

    .nc-worklist-item {{
        border-radius: 10px; padding: 12px; margin-bottom: 8px;
        border: 1px solid transparent; background: {COLORS['card']};
    }}
    .nc-worklist-item.selected {{
        border-color: {COLORS['primary']}66; background: {COLORS['accent']};
    }}
    .nc-worklist-name {{ font-size: 14px; font-weight: 700; color: {COLORS['foreground']}; }}
    .nc-worklist-age {{ font-size: 11px; color: {COLORS['muted_foreground']}; float: right; }}
    .nc-worklist-id {{ font-size: 11px; color: {COLORS['muted_foreground']}; font-family: monospace; }}

    .nc-bar-track {{ height: 6px; border-radius: 999px; background: {COLORS['muted']}; overflow: hidden; }}
    .nc-bar-fill {{ height: 100%; border-radius: 999px; }}

    .nc-section-title {{
        font-size: 13px; font-weight: 700; color: {COLORS['foreground']};
        display: flex; align-items: center; gap: 8px; margin-bottom: 10px;
    }}
    .nc-count-pill {{
        margin-left: auto; background: {COLORS['secondary']}; color: {COLORS['secondary_foreground']};
        border-radius: 999px; padding: 2px 8px; font-size: 11px; font-weight: 700;
    }}

    .nc-fact {{
        border-radius: 8px; padding: 8px 12px; margin-bottom: 8px;
        background: {COLORS['muted']}66; border: 1px solid {COLORS['border']};
    }}
    .nc-fact.redflag {{
        background: {COLORS['risk_high_soft']}99; border: 1px solid {COLORS['risk_high']}66;
        border-left: 4px solid {COLORS['risk_high']};
    }}
    .nc-fact-label {{
        font-size: 10.5px; font-weight: 700; letter-spacing: 0.03em; text-transform: uppercase;
        color: {COLORS['muted_foreground']};
    }}
    .nc-fact.redflag .nc-fact-label {{ color: {COLORS['risk_high']}; }}
    .nc-fact-value {{ font-size: 13px; color: {COLORS['foreground']}ee; margin-top: 2px; }}
    .nc-fact.redflag .nc-fact-value {{ color: {COLORS['risk_high']}; font-weight: 600; }}

    .nc-check {{
        border-radius: 8px; padding: 8px 12px; font-size: 12px;
        background: {COLORS['muted']}66; border: 1px solid {COLORS['border']}; margin-bottom: 8px;
    }}
    .nc-check.fail {{
        background: {COLORS['risk_medium_soft']}99; border: 1px solid {COLORS['risk_medium']}66;
    }}
    .nc-check-name {{ font-weight: 700; color: {COLORS['foreground']}; }}
    .nc-check-detail {{ color: {COLORS['muted_foreground']}; margin-top: 2px; }}

    .nc-trace-node {{ text-align: center; }}
    .nc-trace-circle {{
        width: 40px; height: 40px; border-radius: 999px; display: flex;
        align-items: center; justify-content: center; margin: 0 auto;
        background: {COLORS['success']}; color: white; font-size: 16px; border: 2px solid {COLORS['success']};
    }}
    .nc-trace-name {{ font-size: 11px; font-weight: 700; margin-top: 6px; color: {COLORS['foreground']}; }}
    .nc-trace-chip {{
        display: inline-block; margin-top: 4px; background: {COLORS['success_soft']};
        color: {COLORS['success']}; border-radius: 999px; padding: 1px 8px; font-size: 9.5px; font-weight: 700;
    }}
    .nc-trace-decision {{ font-size: 10.5px; color: {COLORS['muted_foreground']}; margin-top: 4px; line-height: 1.3; }}
    .nc-trace-latency {{ font-size: 9.5px; color: {COLORS['muted_foreground']}99; margin-top: 4px; font-family: monospace; }}

    .nc-citation {{
        background: {COLORS['card']}; border: 1px solid {COLORS['border']};
        border-radius: 8px; padding: 4px 4px; margin-bottom: 8px;
    }}
    .nc-citation-source {{ font-size: 10.5px; font-weight: 700; color: {COLORS['primary']}; margin-top: 4px; }}
    .nc-citation-excerpt {{
        font-size: 11px; color: {COLORS['muted_foreground']}; font-style: italic;
        border-left: 2px solid {COLORS['primary']}66; padding-left: 10px; margin-top: 6px; line-height: 1.4;
    }}

    .nc-schedule-box {{
        border: 1px solid {COLORS['primary']}40; background: {COLORS['accent']}66;
        border-radius: 10px; padding: 12px 14px;
    }}
    .nc-cadence-pill {{
        display: inline-block; background: {COLORS['secondary']}; color: {COLORS['secondary_foreground']};
        border-radius: 999px; padding: 2px 8px; font-size: 10px; font-weight: 700;
        text-transform: uppercase; margin-bottom: 6px;
    }}

    .nc-footer-note {{ font-size: 10.5px; color: {COLORS['muted_foreground']}; line-height: 1.4; }}

    div[data-testid="stButton"] > button {{
        border-radius: 8px;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


def badge_html(level, label, solid=False):
    if solid:
        bg = LEVEL_COLOR[level]
        fg = LEVEL_FG[level]
    else:
        bg = LEVEL_SOFT[level]
        fg = LEVEL_COLOR[level]
    return (
        f'<span class="nc-badge" style="background:{bg};color:{fg};">'
        f'<span class="nc-dot"></span>{label}</span>'
    )


# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
if "selected_id" not in st.session_state:
    st.session_state.selected_id = cases[0]["case_id"]
if "drafts" not in st.session_state:
    st.session_state.drafts = {}
if "actions" not in st.session_state:
    st.session_state.actions = {}

selected = next((c for c in cases if c["case_id"] == st.session_state.selected_id), cases[0])

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown(
    f"""
    <div class="nc-header">
        <div class="logo">✚</div>
        <div>
            <div class="title">NexusCare AI</div>
            <div class="subtitle">Humana Care Management Console · Post-Discharge Coordination</div>
        </div>
        <div class="badge">Demo dataset · no live backend</div>
        <div class="avatar">SP</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Three-panel layout
# ---------------------------------------------------------------------------
col_worklist, col_main, col_sources = st.columns([1.1, 2.4, 1.3], gap="medium")

# ---- LEFT: Discharge Worklist -----------------------------------------
with col_worklist:
    review_count = sum(1 for c in cases if c["requires_human_review"])
    st.markdown(
        f"""
        <div class="nc-section-title">📋 Discharge Worklist
            <span class="nc-count-pill">{len(cases)}</span>
        </div>
        <div style="font-size:11px;color:{COLORS['muted_foreground']};margin-top:-6px;margin-bottom:10px;">
            Sorted by 30-day readmission risk
        </div>
        """,
        unsafe_allow_html=True,
    )
    if review_count > 0:
        st.markdown(
            f"""<div style="background:{COLORS['risk_medium_soft']};color:{COLORS['risk_medium_foreground']};
            border-radius:8px;padding:6px 10px;font-size:11px;font-weight:600;margin-bottom:10px;">
            ⚠ {review_count} case{'s' if review_count != 1 else ''} flagged for human review</div>""",
            unsafe_allow_html=True,
        )

    for record in cases:
        level = risk_level(record)
        is_selected = record["case_id"] == selected["case_id"]
        action = st.session_state.actions.get(record["case_id"])
        pct = round(record["risk_score"] * 100)

        status_line = ""
        if record["requires_human_review"]:
            status_line += (
                f'<span style="color:{COLORS["risk_medium_foreground"]};font-size:10px;font-weight:600;">'
                f'⚠ Human review</span> '
            )
        if action == "approved":
            status_line += (
                f'<span style="background:{COLORS["success_soft"]};color:{COLORS["success"]};'
                f'border-radius:999px;padding:1px 8px;font-size:10px;font-weight:700;">✓ Sent</span>'
            )
        elif action == "escalated":
            status_line += (
                f'<span style="background:{COLORS["risk_high_soft"]};color:{COLORS["risk_high"]};'
                f'border-radius:999px;padding:1px 8px;font-size:10px;font-weight:700;">🛡 Escalated</span>'
            )

        card_class = "nc-worklist-item selected" if is_selected else "nc-worklist-item"
        st.markdown(
            f"""
            <div class="{card_class}">
                <div><span class="nc-worklist-name">{record['name']}</span>
                <span class="nc-worklist-age">{record['age']} y/o</span></div>
                <div class="nc-worklist-id">{record['case_id']}</div>
                <div style="margin-top:8px;">{badge_html(level, record['risk_tier'])}</div>
                <div style="display:flex;align-items:center;gap:8px;margin-top:8px;">
                    <div class="nc-bar-track" style="flex:1;">
                        <div class="nc-bar-fill" style="width:{pct}%;background:{LEVEL_COLOR[level]};"></div>
                    </div>
                    <span style="font-size:11px;font-weight:700;color:{COLORS['muted_foreground']};">
                        {record['risk_score']:.2f}</span>
                </div>
                <div style="margin-top:6px;">{status_line}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Select", key=f"select_{record['case_id']}", use_container_width=True):
            st.session_state.selected_id = record["case_id"]
            st.rerun()

    st.markdown(
        f"""<div class="nc-footer-note" style="margin-top:12px;border-top:1px solid {COLORS['border']};padding-top:10px;">
        Demo dataset · <code>demo_export.json</code><br>Real pipeline exports · no live backend calls</div>""",
        unsafe_allow_html=True,
    )

# ---- MIDDLE: Agent Trace + Coordinator Brief ---------------------------
with col_main:
    level = risk_level(selected)
    score_pct = round(selected["risk_score"] * 100)
    red_flag_count = sum(1 for f in selected["extracted_facts"] if f.get("red_flag"))

    # Agent Reasoning Trace
    st.markdown('<div class="nc-card">', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div style="display:flex;justify-content:space-between;align-items:center;">
            <div>
                <div style="font-size:14px;font-weight:700;color:{COLORS['foreground']};">Agent Reasoning Trace</div>
                <div style="font-size:11px;color:{COLORS['muted_foreground']};">
                    Five-node pipeline · timings from the recorded export</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    trace = selected["agent_trace"]
    trace_cols = st.columns(len(trace))
    for i, (tcol, step) in enumerate(zip(trace_cols, trace)):
        icon = STEP_ICONS[i % len(STEP_ICONS)]
        is_skipped = step.get("status") == "skipped"
        if is_skipped:
            circle_style = f"background:{COLORS['muted']};color:{COLORS['muted_foreground']};border:2px solid {COLORS['border']};"
            circle_glyph = "⏭"
            chip_style = f"background:{COLORS['muted']};color:{COLORS['muted_foreground']};"
            chip_label = "Skipped"
        else:
            circle_style = "background:" + COLORS["success"] + ";color:white;border:2px solid " + COLORS["success"] + ";"
            circle_glyph = "✓"
            chip_style = f"background:{COLORS['success_soft']};color:{COLORS['success']};"
            chip_label = "✓ Done"
        with tcol:
            st.markdown(
                f"""
                <div class="nc-trace-node">
                    <div class="nc-trace-circle" style="{circle_style}">{circle_glyph}</div>
                    <div class="nc-trace-name">{step['node']}</div>
                    <div class="nc-trace-chip" style="{chip_style}">{chip_label}</div>
                    <div class="nc-trace-decision">{step['decision']}</div>
                    <div class="nc-trace-latency">{step['latency_ms']/1000:.2f}s</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    st.markdown(
        f"""<div style="margin-top:14px;background:{COLORS['success_soft']};color:{COLORS['success']};
        text-align:center;border-radius:8px;padding:8px;font-size:12px;font-weight:600;">
        Pipeline complete — brief, outreach draft, and proposed schedule ready for coordinator review.</div>""",
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # Coordinator Brief header
    review_chip = ""
    if selected["requires_human_review"]:
        review_chip = (
            f'<span class="nc-badge" style="background:{COLORS["risk_medium_soft"]};'
            f'color:{COLORS["risk_medium_foreground"]};margin-left:8px;">🛡 Human review required</span>'
        )
    st.markdown(
        f"""
        <div class="nc-card">
            <div style="display:flex;align-items:center;flex-wrap:wrap;gap:10px;">
                <div style="font-size:18px;font-weight:700;color:{COLORS['foreground']};">
                    Coordinator Brief — {selected['name']}</div>
                {badge_html(level, selected['risk_tier'], solid=True)}
                {review_chip}
                <div style="margin-left:auto;display:flex;align-items:center;gap:10px;">
                    <span style="font-size:10.5px;font-weight:600;color:{COLORS['muted_foreground']};
                    text-transform:uppercase;">30-day risk</span>
                    <div class="nc-bar-track" style="width:110px;">
                        <div class="nc-bar-fill" style="width:{score_pct}%;background:{LEVEL_COLOR[level]};"></div>
                    </div>
                    <span style="font-size:14px;font-weight:800;color:{COLORS['foreground']};">
                        {selected['risk_score']:.2f}</span>
                </div>
            </div>
            <div style="margin-top:12px;font-size:13.5px;line-height:1.6;color:{COLORS['foreground']}dd;">
                {selected['brief_text']}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Contributing Risk Factors + Extracted Clinical Facts
    fc1, fc2 = st.columns(2)
    with fc1:
        st.markdown('<div class="nc-card" style="height:100%;">', unsafe_allow_html=True)
        st.markdown(
            f"""<div class="nc-section-title">🧪 Contributing Risk Factors
            <span class="nc-count-pill">{len(selected['top_factors'])}</span></div>""",
            unsafe_allow_html=True,
        )
        for factor in selected["top_factors"]:
            st.markdown(
                f"""<div style="display:flex;gap:8px;font-size:13px;margin-bottom:8px;
                color:{COLORS['foreground']}dd;line-height:1.4;">
                <span style="color:{COLORS['primary']};">●</span><span>{factor}</span></div>""",
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

    with fc2:
        st.markdown('<div class="nc-card" style="height:100%;">', unsafe_allow_html=True)
        flag_chip = ""
        if red_flag_count > 0:
            flag_chip = (
                f'<span class="nc-count-pill" style="background:{COLORS["risk_high_soft"]};'
                f'color:{COLORS["risk_high"]};">⚠ {red_flag_count} red flag{"s" if red_flag_count != 1 else ""}</span>'
            )
        st.markdown(
            f"""<div class="nc-section-title">📑 Extracted Clinical Facts {flag_chip}</div>""",
            unsafe_allow_html=True,
        )
        for fact in selected["extracted_facts"]:
            is_flag = fact.get("red_flag", False)
            cls = "nc-fact redflag" if is_flag else "nc-fact"
            flag_icon = "⚠ " if is_flag else ""
            st.markdown(
                f"""<div class="{cls}">
                <div class="nc-fact-label">{flag_icon}{fact['label']}</div>
                <div class="nc-fact-value">{fact['value']}</div></div>""",
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

    # Drafted Outreach Message
    st.markdown('<div class="nc-card">', unsafe_allow_html=True)
    st.markdown(
        f"""<div class="nc-section-title">💬 Drafted Outreach Message
        <span class="nc-badge" style="background:{COLORS['accent']};color:{COLORS['accent_foreground']};">
        🤖 AI draft · editable</span></div>""",
        unsafe_allow_html=True,
    )
    draft_key = f"draft_{selected['case_id']}"
    if draft_key not in st.session_state.drafts:
        st.session_state.drafts[draft_key] = selected["outreach_message"]
    message = st.text_area(
        "Drafted outreach message",
        value=st.session_state.drafts[draft_key],
        height=160,
        key=f"textarea_{selected['case_id']}",
        label_visibility="collapsed",
    )
    st.session_state.drafts[draft_key] = message
    st.markdown(
        f"""<div class="nc-footer-note">{len(message)} chars ·
        Edits stay local to this demo console — nothing is sent until you approve.</div>""",
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # Automated Validation & Critic
    st.markdown('<div class="nc-card">', unsafe_allow_html=True)
    vr = selected["validation_result"]
    status_label = "All checks passed" if vr["status"] == "passed" else "Passed with warnings"
    status_bg = COLORS["success_soft"] if vr["status"] == "passed" else COLORS["risk_medium_soft"]
    status_fg = COLORS["success"] if vr["status"] == "passed" else COLORS["risk_medium_foreground"]
    st.markdown(
        f"""<div class="nc-section-title">✅ Automated Validation & Critic
        <span class="nc-count-pill" style="background:{status_bg};color:{status_fg};">{status_label}</span>
        </div>""",
        unsafe_allow_html=True,
    )
    vc1, vc2 = st.columns(2)
    for i, check in enumerate(vr["checks"]):
        target = vc1 if i % 2 == 0 else vc2
        cls = "nc-check" if check["passed"] else "nc-check fail"
        icon = "✓" if check["passed"] else "⚠"
        with target:
            st.markdown(
                f"""<div class="{cls}"><div class="nc-check-name">{icon} {check['name']}</div>
                <div class="nc-check-detail">{check['detail']}</div></div>""",
                unsafe_allow_html=True,
            )
    cr = selected["critic_result"]
    st.markdown(
        f"""<div style="background:{COLORS['muted']}66;border:1px solid {COLORS['border']};
        border-radius:8px;padding:10px 12px;margin-top:6px;">
        <span style="font-weight:700;font-size:12px;color:{COLORS['foreground']};">
        Critic verdict: {cr['verdict']}</span>
        <span style="margin-left:8px;font-family:monospace;font-size:11px;color:{COLORS['muted_foreground']};">
        score {cr['score']:.2f}</span>
        <div style="margin-top:4px;font-size:11.5px;color:{COLORS['muted_foreground']};line-height:1.4;">
        {cr['notes']}</div></div>""",
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

# ---- RIGHT: Sources & Actions ------------------------------------------
with col_sources:
    st.markdown('<div class="nc-card">', unsafe_allow_html=True)
    st.markdown(
        f"""<div class="nc-section-title">🔗 Sources & Citations
        <span class="nc-count-pill">{len(selected['retrieved_citations'])}</span></div>
        <div style="font-size:11px;color:{COLORS['muted_foreground']};margin-top:-6px;margin-bottom:10px;">
        Every brief claim is grounded in a playbook excerpt or the discharge summary.</div>""",
        unsafe_allow_html=True,
    )
    for i, citation in enumerate(selected["retrieved_citations"]):
        is_discharge = "discharge summary" in citation["source"].lower()
        icon = "📄" if is_discharge else "📖"
        with st.expander(f"{i+1}. {citation['claim']}", expanded=False):
            st.markdown(
                f"""<div class="nc-citation-source">{icon} {citation['source']}</div>
                <div class="nc-citation-excerpt">"{citation['excerpt']}"</div>""",
                unsafe_allow_html=True,
            )
    st.markdown("</div>", unsafe_allow_html=True)

    # Proposed Follow-Up
    scheduling = next((n for n in selected["agent_trace"] if n["node"] == "Scheduling"), None)
    if scheduling:
        st.markdown('<div class="nc-card">', unsafe_allow_html=True)
        st.markdown(
            f"""<div class="nc-section-title">📅 Proposed Follow-Up</div>
            <div class="nc-cadence-pill">{CADENCE[level]}</div>
            <div style="font-size:13px;line-height:1.5;color:{COLORS['foreground']}dd;margin-top:6px;">
            {scheduling['decision']}</div>""",
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    # Coordinator Actions
    st.markdown('<div class="nc-card">', unsafe_allow_html=True)
    st.markdown(
        f"""<div class="nc-section-title" style="margin-bottom:6px;">Coordinator Actions</div>""",
        unsafe_allow_html=True,
    )
    current_action = st.session_state.actions.get(selected["case_id"])
    if current_action == "approved":
        st.markdown(
            f"""<div style="background:{COLORS['success_soft']};color:{COLORS['success']};
            border-radius:8px;padding:8px 10px;font-size:12px;font-weight:700;margin-bottom:8px;">
            ✓ Approved & queued for delivery</div>""",
            unsafe_allow_html=True,
        )
    elif current_action == "escalated":
        st.markdown(
            f"""<div style="background:{COLORS['risk_high_soft']};color:{COLORS['risk_high']};
            border-radius:8px;padding:8px 10px;font-size:12px;font-weight:700;margin-bottom:8px;">
            🛡 Escalated to supervisor</div>""",
            unsafe_allow_html=True,
        )

    if st.button("📤 Approve & Send", key="approve_btn", use_container_width=True,
                 disabled=(current_action == "approved")):
        st.session_state.actions[selected["case_id"]] = "approved"
        st.toast(f"Outreach approved & sent — {selected['name']} · {selected['case_id']}")
        st.rerun()

    if st.button("✎ Edit Message", key="edit_btn", use_container_width=True):
        st.info("Scroll to the Drafted Outreach Message box in the center panel to edit.")

    with st.expander("🛡 Escalate to Supervisor"):
        st.write(
            f"Case **{selected['case_id']}** ({selected['name']}, {selected['age']}) will be "
            "routed to the on-call supervisor with the full agent trace, validation results, "
            "and critic notes attached. This pauses the outreach SLA clock for this case."
        )
        if st.button("Confirm escalation", key="escalate_confirm_btn"):
            st.session_state.actions[selected["case_id"]] = "escalated"
            st.toast(f"Case escalated to supervisor — {selected['name']} · {selected['case_id']}")
            st.rerun()

    st.markdown(
        f"""<div class="nc-footer-note" style="margin-top:10px;">
        Actions are simulated in this demo — no messages are transmitted and no backend is called.
        </div>""",
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)
