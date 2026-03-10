"""
Streamlit frontend — Inside the Agent: ReAct Explorer

Multi-domain: loads domain packs (Oakwood, GP Triage, Estate Agent).
Each domain provides its own data, tools, prompts, scenarios, and guardrails.
The agent loop (agent.py) is domain-agnostic.

Brand: Serpin palette. No emojis. Lucide inline SVG icons.
"""

import time
import html as _html
import streamlit as st
from agent import run_agent_streaming, format_tool_descriptions
from domains.loader import load_domain, list_domains, DOMAIN_REGISTRY

st.set_page_config(page_title="Inside the Agent", page_icon="S", layout="wide")

# ── Domain loading ────────────────────────────────────────────────────────────
# Default to oakwood, switchable via session state
if "active_domain" not in st.session_state:
    st.session_state["active_domain"] = "oakwood"

_domain_pack = load_domain(st.session_state["active_domain"])

# Unpack for use throughout the app (avoids changing every reference)
SCENARIOS = _domain_pack.scenarios
EVAL_DIMENSIONS = _domain_pack.eval_dimensions
GUARDRAIL_BLOCKS = _domain_pack.guardrail_blocks
BASE_SYSTEM_PROMPT = _domain_pack.base_system_prompt
TOOLS = _domain_pack.tools
FAQ_ENTRIES = _domain_pack.faq_entries
FAILURE_MODES = _domain_pack.failure_modes

# ── Serpin palette ───────────────────────────────────────────────────────────

C_YELLOW   = "#EBF213"
C_SOFT_YEL = "#FCFFA8"
C_CREAM    = "#F7F5F1"
C_BLACK    = "#131313"
C_BODY     = "#535353"
C_MID      = "#AEAEAE"
C_BORDER   = "#CBC9C6"
C_LIGHT_BG = "#D7D7D7"

# ── Inline SVG icons ─────────────────────────────────────────────────────────

_ICON_PATHS = {
    "brain":       '<circle cx="12" cy="12" r="10"/><path d="M12 2a7 7 0 0 0-5 2.1A5 5 0 0 0 4 9a5 5 0 0 0 3.1 4.6A7 7 0 0 0 12 22a7 7 0 0 0 4.9-8.4A5 5 0 0 0 20 9a5 5 0 0 0-3-4.9A7 7 0 0 0 12 2z"/>',
    "wrench":      '<path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>',
    "eye":         '<path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7z"/><circle cx="12" cy="12" r="3"/>',
    "check":       '<polyline points="20 6 9 17 4 12"/>',
    "x-octagon":   '<polygon points="7.86 2 16.14 2 22 7.86 22 16.14 16.14 22 7.86 22 2 16.14 2 7.86"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/>',
    "shield":      '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>',
    "lock":        '<rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>',
    "unlock":      '<rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 9.9-1"/>',
    "repeat":      '<polyline points="17 1 21 5 17 9"/><path d="M3 11V9a4 4 0 0 1 4-4h14"/><polyline points="7 23 3 19 7 15"/><path d="M21 13v2a4 4 0 0 1-4 4H3"/>',
    "user":        '<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>',
    "bot":         '<rect x="3" y="11" width="18" height="10" rx="2"/><circle cx="9" cy="16" r="1"/><circle cx="15" cy="16" r="1"/><path d="M12 2v4"/><path d="M8 6h8"/>',
    "database":    '<ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/>',
    "clipboard":   '<path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><rect x="8" y="2" width="8" height="4" rx="1" ry="1"/>',
    "search":      '<circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>',
    "send":        '<line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/>',
    "code":        '<polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/>',
    "message":     '<path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/>',
    "refresh":     '<polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>',
    "settings":    '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>',
    "arrow-right": '<line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/>',
    "package":     '<line x1="16.5" y1="9.4" x2="7.5" y2="4.21"/><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/>',
    "play":        '<polygon points="5 3 19 12 5 21 5 3"/>',
    "zap":         '<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>',
}


def _icon(name: str, size: int = 16, color: str = "#535353") -> str:
    svg_inner = _ICON_PATHS.get(name, _ICON_PATHS["search"])
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
            f'viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" '
            f'stroke-linecap="round" stroke-linejoin="round" '
            f'style="display:inline-block;vertical-align:middle;margin-right:6px;">'
            f'{svg_inner}</svg>')


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# LANDING PAGE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if not st.session_state.get("entered"):

    # Hide sidebar on landing page
    st.markdown("""<style>
        [data-testid="stSidebar"] { display: none; }
        [data-testid="stSidebarCollapsedControl"] { display: none; }
    </style>""", unsafe_allow_html=True)

    # ── Hero ──────────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="background:{C_BLACK}; padding:60px 40px 50px 40px; border-radius:16px;
                margin:-1rem -1rem 2rem -1rem; text-align:center;">
        <h1 style="color:{C_YELLOW}; font-size:2.8em; margin-bottom:8px; letter-spacing:-1px;">
            Inside the Agent
        </h1>
        <p style="color:#ffffff; font-size:1.2em; margin-bottom:6px; opacity:0.9;">
            Watch a ReAct AI agent reason, act, and respond — step by step
        </p>
        <p style="color:{C_MID}; font-size:0.95em;">
            Same ReAct architecture, different domains, escalating stakes
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Domain picker ──────────────────────────────────────────────────────
    st.markdown(f'<h3 style="color:{C_BLACK}; margin-top:2rem;">Choose a domain</h3>',
                unsafe_allow_html=True)
    domain_cols = st.columns(len(DOMAIN_REGISTRY))
    for i, (dk, dreg) in enumerate(DOMAIN_REGISTRY.items()):
        with domain_cols[i]:
            is_active = st.session_state.get("active_domain") == dk
            border = f"3px solid {C_YELLOW}" if is_active else f"1px solid {C_BORDER}"
            bg = C_SOFT_YEL if is_active else C_CREAM
            st.markdown(
                f'<div style="background:{bg}; border:{border}; border-radius:10px; '
                f'padding:20px; text-align:center; min-height:120px;">'
                f'<div style="margin-bottom:8px;">{_icon(dreg["icon"], 28, C_BLACK)}</div>'
                f'<strong style="color:{C_BLACK}; font-size:1em;">{dreg["name"]}</strong><br>'
                f'<span style="color:{C_BODY}; font-size:0.85em;">{dreg["tagline"]}</span><br>'
                f'<span style="font-size:0.75em; color:{C_MID};">Stakes: {dreg["stakes"]}</span>'
                f'</div>',
                unsafe_allow_html=True)
            if st.button(
                "Selected" if is_active else "Select",
                key=f"domain_{dk}",
                use_container_width=True,
                disabled=is_active,
            ):
                st.session_state["active_domain"] = dk
                st.session_state.pop("_prev_scenario", None)
                st.session_state.pop("last_run", None)
                st.rerun()

    # ── Three feature cards ───────────────────────────────────────────────────
    st.markdown(f"""
    <div style="display:flex; gap:20px; margin:2rem 0;">
        <div style="flex:1; background:{C_CREAM}; border:1px solid {C_BORDER}; border-radius:12px;
                    padding:24px;">
            <div style="margin-bottom:12px;">{_icon("brain", 28, C_BLACK)}</div>
            <h4 style="color:{C_BLACK}; margin:0 0 8px 0;">See the reasoning</h4>
            <p style="color:{C_BODY}; font-size:0.9em; line-height:1.6; margin:0;">
                Most AI shows you the answer. This shows you the thinking.
                Watch the agent reason through each step of a customer query —
                Thought, Action, Observation, Response.
            </p>
        </div>
        <div style="flex:1; background:{C_CREAM}; border:1px solid {C_BORDER}; border-radius:12px;
                    padding:24px;">
            <div style="margin-bottom:12px;">{_icon("shield", 28, C_BLACK)}</div>
            <h4 style="color:{C_BLACK}; margin:0 0 8px 0;">Toggle guardrails</h4>
            <p style="color:{C_BODY}; font-size:0.9em; line-height:1.6; margin:0;">
                Switch between soft guardrails (prompt instructions the model can ignore)
                and hard guardrails (code that can't be bypassed).
                See how each changes the agent's behaviour.
            </p>
        </div>
        <div style="flex:1; background:{C_CREAM}; border:1px solid {C_BORDER}; border-radius:12px;
                    padding:24px;">
            <div style="margin-bottom:12px;">{_icon("clipboard", 28, C_BLACK)}</div>
            <h4 style="color:{C_BLACK}; margin:0 0 8px 0;">Inspect the prompt</h4>
            <p style="color:{C_BODY}; font-size:0.9em; line-height:1.6; margin:0;">
                See the exact system prompt the agent receives.
                Watch guardrail blocks appear and disappear in real time
                as you toggle them on and off.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── How it works ──────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="margin:2.5rem 0 1.5rem 0;">
        <h3 style="color:{C_BLACK};">How it works</h3>
    </div>
    <div style="display:flex; gap:16px; margin-bottom:2rem;">
        <div style="flex:1; text-align:center; padding:16px;">
            <div style="background:{C_YELLOW}; width:36px; height:36px; border-radius:50%;
                        display:inline-flex; align-items:center; justify-content:center;
                        font-weight:bold; color:{C_BLACK}; font-size:1.1em;">1</div>
            <p style="color:{C_BODY}; font-size:0.9em; margin-top:10px;">
                <strong>Understand the setup</strong><br>See the agent's tools, data, and guardrails
            </p>
        </div>
        <div style="flex:1; text-align:center; padding:16px;">
            <div style="background:{C_YELLOW}; width:36px; height:36px; border-radius:50%;
                        display:inline-flex; align-items:center; justify-content:center;
                        font-weight:bold; color:{C_BLACK}; font-size:1.1em;">2</div>
            <p style="color:{C_BODY}; font-size:0.9em; margin-top:10px;">
                <strong>Pick a scenario</strong><br>Choose a customer situation to test
            </p>
        </div>
        <div style="flex:1; text-align:center; padding:16px;">
            <div style="background:{C_YELLOW}; width:36px; height:36px; border-radius:50%;
                        display:inline-flex; align-items:center; justify-content:center;
                        font-weight:bold; color:{C_BLACK}; font-size:1.1em;">3</div>
            <p style="color:{C_BODY}; font-size:0.9em; margin-top:10px;">
                <strong>Run and observe</strong><br>Watch the reasoning trace, toggle guardrails
            </p>
        </div>
        <div style="flex:1; text-align:center; padding:16px;">
            <div style="background:{C_YELLOW}; width:36px; height:36px; border-radius:50%;
                        display:inline-flex; align-items:center; justify-content:center;
                        font-weight:bold; color:{C_BLACK}; font-size:1.1em;">4</div>
            <p style="color:{C_BODY}; font-size:0.9em; margin-top:10px;">
                <strong>Evaluate</strong><br>Check expected vs actual behaviour — spot the silent failures
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── CTA ───────────────────────────────────────────────────────────────────
    st.markdown("")
    _, cta_col, _ = st.columns([2, 3, 2])
    with cta_col:
        if st.button("Explore the Agent", use_container_width=True, type="primary"):
            st.session_state["entered"] = True
            st.rerun()

    # Landing-specific button styling (larger)
    st.markdown(f"""<style>
        .stButton > button[kind="primary"] {{
            background-color: {C_YELLOW} !important;
            color: {C_BLACK} !important;
            border: none !important;
            font-weight: bold !important;
            font-size: 1.2em !important;
            padding: 0.8em 2em !important;
            border-radius: 8px !important;
        }}
        .stButton > button[kind="primary"]:hover {{
            background-color: {C_SOFT_YEL} !important;
        }}
    </style>""", unsafe_allow_html=True)

    st.stop()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TOOL MODE (entered = True)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# ── Tool CSS ──────────────────────────────────────────────────────────────────

st.markdown(f"""<style>
    .stApp {{ color: {C_BODY}; }}
    h1, h2, h3, h4, h5 {{ color: {C_BLACK} !important; }}

    /* Trace step boxes — Serpin palette only */
    .thought-box {{ background:{C_CREAM}; border-left:3px solid {C_BORDER};
        padding:10px 15px; margin:8px 0; border-radius:0 6px 6px 0; color:{C_BODY}; }}
    .action-box {{ background:{C_CREAM}; border-left:3px solid {C_YELLOW};
        padding:10px 15px; margin:8px 0; border-radius:0 6px 6px 0;
        font-family:monospace; color:{C_BODY}; }}
    .observation-box {{ background:{C_CREAM}; border-left:3px solid {C_MID};
        padding:10px 15px; margin:8px 0; border-radius:0 6px 6px 0;
        font-family:monospace; font-size:0.9em; color:{C_BODY}; }}
    .finish-box {{ background:white; border-left:3px solid {C_BLACK};
        padding:10px 15px; margin:8px 0; border-radius:0 6px 6px 0; color:{C_BLACK}; }}
    .blocked-box {{ background:white; border:2px solid {C_BLACK};
        padding:10px 15px; margin:8px 0; border-radius:6px;
        font-weight:bold; color:{C_BLACK}; }}
    .loop-header {{ background:{C_CREAM}; border:1px solid {C_BORDER};
        padding:8px 14px; border-radius:6px;
        margin:16px 0 4px 0; font-weight:bold; font-size:0.95em; color:{C_BLACK}; }}
    .loop-header-blocked {{ background:white; border:2px solid {C_BLACK};
        padding:8px 14px; border-radius:6px;
        margin:16px 0 4px 0; font-weight:bold; font-size:0.95em; color:{C_BLACK}; }}

    /* Chat bubbles */
    .chat-bubble-customer {{ background:{C_CREAM}; border:1px solid {C_BORDER};
        border-radius:12px 12px 12px 2px;
        padding:12px 16px; margin:8px 0; font-size:0.95em; line-height:1.5; color:{C_BODY}; }}
    .chat-bubble-customer .chat-label {{ font-size:0.75em; color:{C_BLACK};
        font-weight:bold; margin-bottom:4px; }}
    .chat-bubble-agent {{ background:white; border:1px solid {C_BORDER};
        border-radius:12px 12px 2px 12px;
        padding:12px 16px; margin:8px 0; font-size:0.95em; line-height:1.5; color:{C_BODY}; }}
    .chat-bubble-agent .chat-label {{ font-size:0.75em; color:{C_BLACK};
        font-weight:bold; margin-bottom:4px; }}

    /* Prompt panel */
    .prompt-base {{ background:{C_CREAM}; border:1px solid {C_BORDER}; border-radius:6px;
        padding:14px; margin:8px 0; font-family:monospace; font-size:0.8em;
        white-space:pre-wrap; line-height:1.5; max-height:400px; overflow-y:auto; color:{C_BODY}; }}

    /* Guardrail blocks — soft: yellow accent, hard: inverted black */
    .guardrail-soft-block {{ background:{C_CREAM}; border-left:3px solid {C_YELLOW};
        padding:12px 16px; margin:8px 0; border-radius:0 6px 6px 0; }}
    .guardrail-soft-block .block-label {{ font-size:0.8em; font-weight:bold;
        color:{C_BLACK}; margin-bottom:6px; }}
    .guardrail-soft-block pre {{ margin:0; font-size:0.8em; white-space:pre-wrap; color:{C_BODY}; }}
    .guardrail-hard-block {{
        background:white; border:1px solid {C_BLACK}; border-radius:6px;
        margin:8px 0; overflow:hidden; }}
    .guardrail-hard-block .block-topbar {{
        background:{C_YELLOW}; padding:6px 16px;
        font-size:0.75em; font-weight:bold; color:{C_BLACK};
        letter-spacing:0.5px; text-transform:uppercase;
        font-family:monospace; }}
    .guardrail-hard-block .block-body {{
        padding:12px 16px; }}
    .guardrail-hard-block .block-label {{
        font-size:0.85em; font-weight:bold;
        color:{C_BLACK}; margin-bottom:8px; }}
    .guardrail-hard-block pre {{
        margin:0; font-size:0.82em; white-space:pre-wrap;
        color:{C_BODY}; background:{C_CREAM};
        padding:10px 12px; border-radius:4px; }}
    .guardrail-off {{ background:{C_CREAM}; border-left:3px solid {C_BORDER};
        padding:12px 16px; margin:8px 0; border-radius:0 6px 6px 0; color:{C_MID}; }}

    /* Tool cards */
    .tool-card {{ background:{C_CREAM}; border:1px solid {C_BORDER}; border-radius:6px;
        padding:12px 16px; margin:6px 0; }}
    .tool-card .tool-name {{ font-weight:bold; color:{C_BLACK}; font-family:monospace; }}

    /* Primary button */
    .stButton > button[kind="primary"] {{
        background-color: {C_YELLOW} !important; color: {C_BLACK} !important;
        border: none !important; font-weight: bold !important;
    }}
    .stButton > button[kind="primary"]:hover {{ background-color: {C_SOFT_YEL} !important; }}

    /* Toggle — black when on, grey when off */
    .stToggle [data-testid="stToggleSwitch"] > label > span:first-child {{
        background-color: {C_BORDER} !important;
    }}
    .stToggle [data-testid="stToggleSwitch"] > label > span:first-child[aria-checked="true"] {{
        background-color: {C_BLACK} !important;
    }}
    div[data-baseweb="toggle"] > div {{ background-color: {C_BORDER} !important; }}
    div[data-baseweb="toggle"][aria-checked="true"] > div {{ background-color: {C_BLACK} !important; }}

    /* Tab underline */
    .stTabs [data-baseweb="tab-highlight"] {{ background-color: {C_BLACK} !important; }}
    .stTabs [data-baseweb="tab"][aria-selected="true"] {{ color: {C_BLACK} !important; }}

    /* Info box */
    .stAlert {{ border-left-color: {C_YELLOW} !important; }}

    /* Metrics */
    [data-testid="stMetricLabel"] {{ color: {C_BODY} !important; }}
    [data-testid="stMetricValue"] {{ color: {C_BLACK} !important; }}
</style>""", unsafe_allow_html=True)


# ── Helper functions ──────────────────────────────────────────────────────────

def _bubble_html(text: str, role: str) -> str:
    safe = _html.escape(text).replace("\n", "<br>")
    if role == "customer":
        return (f'<div class="chat-bubble-customer">'
                f'<div class="chat-label">{_icon("user", 14, C_BLACK)} Customer</div>{safe}</div>')
    return (f'<div class="chat-bubble-agent">'
            f'<div class="chat-label">{_icon("bot", 14, C_BLACK)} Agent</div>{safe}</div>')


GUARDRAIL_SIGNALS = [
    "can only help with", "only able to help with",
    "cannot discuss", "can't discuss",
    "not able to provide legal", "cannot provide legal",
    "redirect", "outside my scope",
    "citizensadvice", "citizens advice",
    "not able to compare", "cannot compare",
    "won't be able to help with", "can't help with that",
    "beyond my scope", "outside our scope", "not something I can",
]


def step_has_guardrail_signal(content: str) -> bool:
    return any(s in content.lower() for s in GUARDRAIL_SIGNALS)


def group_steps_into_loops(steps: list[dict]) -> list[dict]:
    loops, current, num = [], [], 1
    for step in steps:
        if step["type"] == "finish":
            if current:
                loops.append({"type": "loop", "number": num, "steps": current})
                num += 1; current = []
            loops.append({"type": "finish", "step": step})
        elif step["type"] == "thought" and current and current[-1]["type"] == "observation":
            loops.append({"type": "loop", "number": num, "steps": current})
            num += 1; current = [step]
        else:
            current.append(step)
    if current:
        loops.append({"type": "loop", "number": num, "steps": current})
    return loops


def render_step_styled(step: dict, soft_active: bool = False):
    css_class = f"{step['type']}-box"
    icons = {"thought": _icon("brain", 14, C_BODY), "action": _icon("wrench", 14, "#b8960e"),
             "observation": _icon("eye", 14, C_MID), "finish": _icon("check", 14, C_BLACK)}
    labels = {"thought": "Thought", "action": "Action",
              "observation": "Tool Response", "finish": "Response"}
    icon = icons.get(step["type"], "")
    label_text = labels.get(step["type"], step["type"])
    content = step.get("content", "")
    if "BLOCKED" in content:
        css_class = "blocked-box"
        icon = _icon("x-octagon", 14, C_BLACK)
        label_text = "BLOCKED — Hard guardrail (code)"
    elif step["type"] == "thought" and soft_active and step_has_guardrail_signal(content):
        icon = _icon("shield", 14, C_BODY)
        label_text = "Thought (soft guardrail shaped this)"
    with st.expander(label_text, expanded=True):
        st.markdown(f'<div class="{css_class}">{icon}{content}</div>', unsafe_allow_html=True)


def render_reasoning_trace(steps: list[dict], active_guardrails: list[str]):
    soft_active = bool(active_guardrails)
    for group in group_steps_into_loops(steps):
        if group["type"] == "loop":
            n = group["number"]
            has_block = any("BLOCKED" in s.get("content", "") for s in group["steps"])
            has_guard = soft_active and any(
                step_has_guardrail_signal(s.get("content", ""))
                for s in group["steps"] if s["type"] == "thought")
            shield = ""
            if has_block:
                shield = f" — {_icon('x-octagon', 14, C_BLACK)}Hard guardrail blocked"
            elif has_guard:
                shield = f" — {_icon('shield', 14, C_BODY)}Soft guardrail active"
            st.markdown(
                f'<div class="loop-header">{_icon("repeat", 14, C_BLACK)}Loop {n}{shield}</div>',
                unsafe_allow_html=True)
            for step in group["steps"]:
                render_step_styled(step, soft_active=soft_active)
        elif group["type"] == "finish":
            st.markdown(
                f'<div class="loop-header">{_icon("check", 14, C_BLACK)}Final Response</div>',
                unsafe_allow_html=True)
            step = group["step"]
            css = "blocked-box" if "BLOCKED" in step.get("content", "") else "finish-box"
            with st.expander("Agent's response to the customer", expanded=True):
                st.markdown(f'<div class="{css}">{step["content"]}</div>', unsafe_allow_html=True)


def render_evaluation_panel(scenario: dict, steps: list[dict], active_guardrails: list[str]):
    """Post-run evaluation: structured eval dimensions with pass/fail per dimension."""
    evals = scenario.get("evals")
    if not evals:
        return

    st.markdown(f"##### {_icon('clipboard', 16, C_BLACK)} Evaluation", unsafe_allow_html=True)
    st.caption("Structured eval — 7 dimensions, each with expected outcome and pass condition.")

    # Gather signals from the run
    tools_called = [s.get("content", "") for s in steps if s["type"] == "action"]
    all_content = " ".join(s.get("content", "") for s in steps)
    has_blocked = any("BLOCKED" in s.get("content", "") for s in steps)
    has_guardrails = bool(active_guardrails)

    for dim_key, dim_def in EVAL_DIMENSIONS.items():
        dim_eval = evals.get(dim_key)
        if not dim_eval:
            continue

        # Pick the right expected string based on guardrail state
        if has_guardrails and "expected_with_guardrails" in dim_eval:
            expected = dim_eval["expected_with_guardrails"]
        elif not has_guardrails and "expected_without_guardrails" in dim_eval:
            expected = dim_eval["expected_without_guardrails"]
        else:
            expected = dim_eval.get("expected", "")

        pass_cond = dim_eval.get("pass_condition", "")

        # Auto-check where possible
        result = None  # None = human review needed
        if dim_def["how_checked"] == "automated":
            if dim_key == "tool_accuracy" and "tools_required" in dim_eval:
                # Check each required tool was called
                result = all(
                    any(t in tc for tc in tools_called)
                    for t in dim_eval["tools_required"]
                )
            elif dim_key == "guardrail_compliance":
                if has_guardrails:
                    result = step_has_guardrail_signal(all_content.lower()) or has_blocked
                else:
                    result = True  # No guardrails expected = pass
            elif dim_key == "escalation":
                needs_escalation = "MUST" in expected.upper() or "must escalate" in expected.lower()
                has_escalation = any("escalate" in tc.lower() for tc in tools_called)
                if needs_escalation:
                    result = has_escalation
                elif "not needed" in expected.lower() or "not required" in expected.lower():
                    result = not has_escalation
            elif dim_key == "factual_grounding":
                # Basic check: did we get tool observations?
                has_observations = any(s["type"] == "observation" for s in steps)
                result = has_observations

        # Render result
        how_badge_colour = C_SOFT_YEL if dim_def["how_checked"] == "automated" else C_CREAM
        how_label = dim_def["how_checked"]

        if result is True:
            icon_html = _icon("check", 14, "#4a7c59")
            verdict = "PASS"
            verdict_colour = "#4a7c59"
        elif result is False:
            icon_html = _icon("x-octagon", 14, "#a63d2f")
            verdict = "FAIL"
            verdict_colour = "#a63d2f"
        else:
            icon_html = _icon("eye", 14, C_MID)
            verdict = "Review"
            verdict_colour = C_MID

        st.markdown(
            f'<div style="background:{C_CREAM}; border:1px solid {C_BORDER}; '
            f'border-radius:6px; padding:10px 14px; margin:6px 0;">'
            f'<div style="display:flex; align-items:center; gap:8px; margin-bottom:4px;">'
            f'{icon_html} '
            f'<strong style="color:{C_BLACK}; font-size:0.9em;">{dim_def["name"]}</strong>'
            f'<span style="background:{how_badge_colour}; padding:1px 6px; border-radius:3px; '
            f'font-size:0.7em; color:{C_BODY};">{how_label}</span>'
            f'<span style="margin-left:auto; color:{verdict_colour}; font-weight:bold; '
            f'font-size:0.8em; font-family:monospace;">{verdict}</span></div>'
            f'<div style="font-size:0.82em; color:{C_BODY}; line-height:1.5;">'
            f'<strong>Expected:</strong> {_html.escape(expected)}<br>'
            f'<strong>Pass if:</strong> {_html.escape(pass_cond)}</div></div>',
            unsafe_allow_html=True)

    # ── Failure Modes ─────────────────────────────────────────────────────
    if scenario.get("failure_modes"):
        st.markdown("")
        st.markdown(f"**{_icon('x-octagon', 14, C_BLACK)} Failure modes tested:**",
                    unsafe_allow_html=True)
        for fm in scenario["failure_modes"]:
            st.markdown(
                f'<div style="background:{C_CREAM}; border:1px solid {C_BORDER}; '
                f'border-radius:6px; padding:8px 12px; margin:4px 0; font-size:0.85em;">'
                f'<strong style="color:{C_BLACK};">{fm["mode"]}</strong><br>'
                f'<span style="color:{C_BODY};">{fm["detail"]}</span></div>',
                unsafe_allow_html=True)

    # ── Silent Failure Callout ────────────────────────────────────────────
    if scenario.get("silent_failure_note") and not active_guardrails:
        st.markdown("")
        st.markdown(
            f'<div style="background:white; border:2px solid {C_BLACK}; '
            f'border-radius:6px; overflow:hidden;">'
            f'<div style="background:{C_YELLOW}; padding:6px 16px; font-size:0.75em; '
            f'font-weight:bold; color:{C_BLACK}; text-transform:uppercase; '
            f'font-family:monospace; letter-spacing:0.5px;">Silent failure</div>'
            f'<div style="padding:12px 16px; font-size:0.85em; color:{C_BODY}; line-height:1.6;">'
            f'{scenario["silent_failure_note"]}</div></div>',
            unsafe_allow_html=True)


def render_prompt_panel_interactive():
    """Prompt panel with inline guardrail toggles. Returns (active_guardrails, refund_guardrail)."""
    st.markdown(f"##### {_icon('clipboard', 16, C_BLACK)} System Prompt", unsafe_allow_html=True)
    st.caption("Toggle guardrails to see the prompt change.")
    tool_desc = format_tool_descriptions(TOOLS)
    base = BASE_SYSTEM_PROMPT.format(tool_descriptions=tool_desc)
    with st.expander("Base prompt (always sent)", expanded=False):
        st.markdown(f'<div class="prompt-base">{_html.escape(base)}</div>', unsafe_allow_html=True)

    st.markdown(f"**{_icon('shield', 14, C_BODY)} Soft guardrails** "
                f'<span style="font-size:0.8em;color:{C_BODY};">(injected into prompt — model can ignore)</span>',
                unsafe_allow_html=True)
    guardrail_states = {}
    for key, block in GUARDRAIL_BLOCKS.items():
        is_on = st.toggle(block["label"], key=f"guard_{key}")
        guardrail_states[key] = is_on
        if is_on:
            st.markdown(
                f'<div class="guardrail-soft-block">'
                f'<div class="block-label">{_icon("shield", 14, C_BODY)} '
                f'{block["label"]} — ACTIVE</div>'
                f'<pre>{_html.escape(block["prompt"].strip())}</pre></div>',
                unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(f"**{_icon('lock', 14, C_BLACK)} Hard guardrail** "
                f'<span style="font-size:0.8em;color:{C_BODY};">(runs in Python — impossible to override)</span>',
                unsafe_allow_html=True)
    refund_on = st.toggle("Refund limit (£50 max auto)", key="guard_refund")
    if refund_on:
        st.markdown(
            f'<div class="guardrail-hard-block">'
            f'<div class="block-topbar">{_icon("lock", 12, C_BLACK)} Code-enforced</div>'
            f'<div class="block-body">'
            f'<div class="block-label">Refund limit (£50 max) — ACTIVE</div>'
            '<pre># This runs in Python, NOT in the prompt\n'
            'MAX_AUTO_REFUND = 50.00\n\n'
            'def issue_refund(order_id, amount, reason):\n'
            '    if amount > MAX_AUTO_REFUND:\n'
            '        return "BLOCKED: Refund exceeds £50.\n'
            '                Requires manager approval."</pre>'
            '</div></div>',
            unsafe_allow_html=True)

    active = [k for k, v in guardrail_states.items() if v]
    return active, refund_on


def render_prompt_panel_readonly(active_guardrails: list[str], refund_guardrail: bool):
    """Read-only prompt panel for results view (no toggles)."""
    st.markdown(f"##### {_icon('clipboard', 16, C_BLACK)} System Prompt (as sent)", unsafe_allow_html=True)
    tool_desc = format_tool_descriptions(TOOLS)
    base = BASE_SYSTEM_PROMPT.format(tool_descriptions=tool_desc)
    with st.expander("Base prompt (always sent)", expanded=False):
        st.markdown(f'<div class="prompt-base">{_html.escape(base)}</div>', unsafe_allow_html=True)
    for key, block in GUARDRAIL_BLOCKS.items():
        if key in active_guardrails:
            st.markdown(
                f'<div class="guardrail-soft-block">'
                f'<div class="block-label">{_icon("shield", 14, C_BODY)} '
                f'{block["label"]} — ACTIVE</div>'
                f'<pre>{_html.escape(block["prompt"].strip())}</pre></div>',
                unsafe_allow_html=True)
        else:
            st.markdown(
                f'<div class="guardrail-off"><strong>{block["label"]}</strong> — OFF</div>',
                unsafe_allow_html=True)
    st.markdown("---")
    if refund_guardrail:
        st.markdown(
            f'<div class="guardrail-hard-block">'
            f'<div class="block-topbar">{_icon("lock", 12, C_BLACK)} Code-enforced</div>'
            f'<div class="block-body">'
            f'<div class="block-label">Refund limit (£50 max) — ACTIVE</div>'
            '<pre># This runs in Python, NOT in the prompt\n'
            'MAX_AUTO_REFUND = 50.00\n\n'
            'def issue_refund(order_id, amount, reason):\n'
            '    if amount > MAX_AUTO_REFUND:\n'
            '        return "BLOCKED: Refund exceeds £50.\n'
            '                Requires manager approval."</pre>'
            '</div></div>',
            unsafe_allow_html=True)
    else:
        st.markdown(
            f'<div class="guardrail-off">'
            f'<strong>{_icon("unlock", 14, C_MID)} Refund limit (£50 max)</strong> — OFF</div>',
            unsafe_allow_html=True)


def reset_conversation():
    st.session_state.pop("last_run", None)


# ── Hide sidebar ──────────────────────────────────────────────────────────────

st.markdown("""<style>
    [data-testid="stSidebar"] { display: none; }
    [data-testid="stSidebarCollapsedControl"] { display: none; }
</style>""", unsafe_allow_html=True)


# ── Title bar ─────────────────────────────────────────────────────────────────

title_col, back_col = st.columns([5, 1])
with title_col:
    st.markdown(f"## {_icon('search', 22, C_BLACK)} Inside the Agent", unsafe_allow_html=True)
with back_col:
    st.markdown("")  # spacing
    if st.button("Back to start", use_container_width=True):
        st.session_state["entered"] = False
        st.rerun()

tab_run, tab_evals, tab_setup = st.tabs(["Run Scenario", "Evaluations", "The World"])


# ── Scenario state ────────────────────────────────────────────────────────────

if "_prev_scenario" not in st.session_state:
    st.session_state["_prev_scenario"] = None  # None = no scenario selected yet
    for key in GUARDRAIL_BLOCKS:
        st.session_state[f"guard_{key}"] = False
    st.session_state["guard_refund"] = False


# ── Evaluations Tab ───────────────────────────────────────────────────────────

with tab_evals:
    # ── Eval Framework Overview ───────────────────────────────────────────
    st.markdown(f"### {_icon('clipboard', 18, C_BLACK)} Evaluation Framework",
                unsafe_allow_html=True)
    st.caption("Seven dimensions applied consistently across every scenario. "
               "This is what production eval design looks like — not ad-hoc checks.")

    with st.expander("Eval dimensions (the framework)", expanded=True):
        header = (f'<div style="display:grid; grid-template-columns:1fr 2fr 120px; gap:8px; '
                  f'padding:6px 12px; background:{C_BLACK}; color:white; border-radius:6px 6px 0 0; '
                  f'font-size:0.75em; font-weight:bold; text-transform:uppercase; letter-spacing:0.5px;">'
                  f'<div>Dimension</div><div>What it checks</div><div>How checked</div></div>')
        rows = ""
        for dim_key, dim in EVAL_DIMENSIONS.items():
            how_bg = C_SOFT_YEL if dim["how_checked"] == "automated" else C_CREAM
            rows += (
                f'<div style="display:grid; grid-template-columns:1fr 2fr 120px; gap:8px; '
                f'padding:8px 12px; border-bottom:1px solid {C_BORDER}; font-size:0.85em;">'
                f'<div style="font-weight:bold; color:{C_BLACK};">{dim["name"]}</div>'
                f'<div style="color:{C_BODY};">{dim["description"]}</div>'
                f'<div><span style="background:{how_bg}; padding:2px 8px; border-radius:3px; '
                f'font-size:0.8em;">{dim["how_checked"]}</span></div></div>')
        st.markdown(
            f'<div style="border:1px solid {C_BORDER}; border-radius:6px; overflow:hidden;">'
            f'{header}{rows}</div>',
            unsafe_allow_html=True)

    # ── Per-Scenario Eval Cards ───────────────────────────────────────────
    st.markdown("")
    st.markdown(f"### {_icon('eye', 18, C_BLACK)} Scenario Evaluations",
                unsafe_allow_html=True)
    st.caption("Expected outcomes for each scenario. Dimensions with conditional expectations "
               "show both with-guardrails and without-guardrails outcomes.")

    for s in SCENARIOS:
        evals = s.get("evals", {})
        if not evals:
            continue

        with st.expander(f"**{s['name']}** — {s['description']}", expanded=False):
            # Eval dimensions for this scenario
            for dim_key, dim_def in EVAL_DIMENSIONS.items():
                dim_eval = evals.get(dim_key)
                if not dim_eval:
                    continue

                how_bg = C_SOFT_YEL if dim_def["how_checked"] == "automated" else C_CREAM

                # Build expected text — handle conditional expectations
                expected_parts = []
                if "expected_with_guardrails" in dim_eval:
                    expected_parts.append(
                        f'<span style="font-size:0.8em;">With guardrails:</span> '
                        f'{_html.escape(dim_eval["expected_with_guardrails"])}')
                if "expected_without_guardrails" in dim_eval:
                    expected_parts.append(
                        f'<span style="font-size:0.8em;">Without guardrails:</span> '
                        f'{_html.escape(dim_eval["expected_without_guardrails"])}')
                if "expected" in dim_eval and not expected_parts:
                    expected_parts.append(_html.escape(dim_eval["expected"]))

                expected_html = "<br>".join(expected_parts)
                pass_cond = _html.escape(dim_eval.get("pass_condition", ""))

                tools_html = ""
                if "tools_required" in dim_eval:
                    tools_html = (
                        f'<div style="margin-top:4px;">'
                        f'<span style="font-size:0.75em; color:{C_MID};">Tools: </span>'
                        + " → ".join(
                            f'<code style="font-size:0.8em; background:{C_CREAM}; '
                            f'padding:1px 4px; border-radius:2px;">{t}</code>'
                            for t in dim_eval["tools_required"])
                        + '</div>')

                st.markdown(
                    f'<div style="background:{C_CREAM}; border:1px solid {C_BORDER}; '
                    f'border-radius:6px; padding:10px 14px; margin:4px 0;">'
                    f'<div style="display:flex; align-items:center; gap:8px; margin-bottom:4px;">'
                    f'<strong style="color:{C_BLACK}; font-size:0.85em;">{dim_def["name"]}</strong>'
                    f'<span style="background:{how_bg}; padding:1px 6px; border-radius:3px; '
                    f'font-size:0.7em; color:{C_BODY};">{dim_def["how_checked"]}</span></div>'
                    f'<div style="font-size:0.82em; color:{C_BODY}; line-height:1.5;">'
                    f'<strong>Expected:</strong> {expected_html}<br>'
                    f'<strong>Pass if:</strong> {pass_cond}'
                    f'{tools_html}</div></div>',
                    unsafe_allow_html=True)

            # Failure modes
            if s.get("failure_modes"):
                st.markdown("")
                st.markdown(f"**{_icon('x-octagon', 14, C_BLACK)} Failure modes:**",
                            unsafe_allow_html=True)
                for fm in s["failure_modes"]:
                    st.markdown(
                        f'<div style="background:white; border:1px solid {C_BORDER}; '
                        f'border-radius:6px; padding:8px 12px; margin:4px 0; font-size:0.85em;">'
                        f'<strong style="color:{C_BLACK};">{fm["mode"]}</strong><br>'
                        f'<span style="color:{C_BODY};">{fm["detail"]}</span></div>',
                        unsafe_allow_html=True)

            # Silent failure callout
            if s.get("silent_failure_note"):
                st.markdown("")
                st.markdown(
                    f'<div style="background:white; border:2px solid {C_BLACK}; '
                    f'border-radius:6px; overflow:hidden;">'
                    f'<div style="background:{C_YELLOW}; padding:6px 16px; font-size:0.75em; '
                    f'font-weight:bold; color:{C_BLACK}; text-transform:uppercase; '
                    f'font-family:monospace; letter-spacing:0.5px;">Silent failure risk</div>'
                    f'<div style="padding:12px 16px; font-size:0.85em; color:{C_BODY}; line-height:1.6;">'
                    f'{s["silent_failure_note"]}</div></div>',
                    unsafe_allow_html=True)

            # What this proves
            if s.get("proves"):
                st.markdown("")
                st.markdown(
                    f'<div style="font-size:0.85em; color:{C_BODY}; padding:4px 0;">'
                    f'{_icon("eye", 12, C_BODY)} <strong>This proves:</strong> {s["proves"]}</div>',
                    unsafe_allow_html=True)


# ── The Setup Tab ─────────────────────────────────────────────────────────────

with tab_setup:

    # ── The Company ──────────────────────────────────────────────────────────
    st.markdown(f"### {_icon('package', 18, C_BLACK)} The Company", unsafe_allow_html=True)
    st.markdown(
        f"**{_domain_pack.name}** — {_domain_pack.description}")

    # ── The Agent ────────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown(f"### {_icon('bot', 18, C_BLACK)} The Agent", unsafe_allow_html=True)
    st.markdown(
        "A **ReAct agent** that reasons step-by-step: "
        "**Think** about the problem, **Act** by calling a tool, **Observe** the result, repeat. "
        "Each loop is a separate API call to Claude Haiku.")

    st.caption(f"The agent has {len(TOOLS)} tools:")
    for name, tool in TOOLS.items():
        st.markdown(
            f'<div class="tool-card">'
            f'<span class="tool-name">{name}({", ".join(tool["parameters"])})</span><br>'
            f'<span style="font-size:0.9em;color:{C_BODY};">{tool["description"]}</span></div>',
            unsafe_allow_html=True)

    # ── The Guardrails ───────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown(f"### {_icon('shield', 18, C_BLACK)} The Guardrails", unsafe_allow_html=True)
    st.markdown(
        "Guardrails prevent failure modes — things the agent could do wrong. "
        "**Every guardrail traces to a specific failure mode.** "
        "If you can't trace it, it's either unnecessary or you've missed the failure.")

    st.markdown(f"""
    <div style="display:flex; gap:16px; margin:16px 0;">
        <div style="flex:1; background:{C_CREAM}; border-left:3px solid {C_YELLOW};
                    padding:16px; border-radius:0 8px 8px 0;">
            <strong style="color:{C_BLACK};">Soft guardrails</strong>
            <span style="color:{C_BODY}; font-size:0.85em;"> (prompt-injected)</span><br>
            <span style="color:{C_BODY}; font-size:0.9em;">
                Instructions added to the system prompt. The model <em>should</em> follow them
                but <em>can</em> ignore them — especially under pressure or with adversarial input.
            </span>
        </div>
        <div style="flex:1; background:white; border:1px solid {C_BLACK};
                    padding:16px; border-radius:8px;">
            <strong style="color:{C_BLACK};">Hard guardrails</strong>
            <span style="color:{C_BODY}; font-size:0.85em;"> (code-enforced)</span><br>
            <span style="color:{C_BODY}; font-size:0.9em;">
                Python code that runs <em>outside</em> the model. No prompt engineering can bypass it.
                For decisions too consequential for autonomous handling.
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"##### {_icon('eye', 16, C_BLACK)} Guardrail Traceability", unsafe_allow_html=True)
    st.caption("Every guardrail prevents a specific failure. Here's the mapping:")

    st.markdown(f"""
    <table style="width:100%; border-collapse:collapse; font-size:0.9em; margin:8px 0;">
        <tr style="border-bottom:2px solid {C_BLACK};">
            <th style="text-align:left; padding:8px; color:{C_BLACK};">Guardrail</th>
            <th style="text-align:left; padding:8px; color:{C_BLACK};">Type</th>
            <th style="text-align:left; padding:8px; color:{C_BLACK};">Prevents</th>
            <th style="text-align:left; padding:8px; color:{C_BLACK};">Consequence if missing</th>
        </tr>
        <tr style="border-bottom:1px solid {C_BORDER};">
            <td style="padding:8px;">Stay on topic</td>
            <td style="padding:8px;"><span style="background:{C_SOFT_YEL}; padding:2px 8px;
                border-radius:4px; font-size:0.85em;">Soft</span></td>
            <td style="padding:8px;">Scope drift</td>
            <td style="padding:8px; color:{C_BODY};">Agent becomes a general-purpose assistant — resource waste, off-brand</td>
        </tr>
        <tr style="border-bottom:1px solid {C_BORDER};">
            <td style="padding:8px;">No competitor discussion</td>
            <td style="padding:8px;"><span style="background:{C_SOFT_YEL}; padding:2px 8px;
                border-radius:4px; font-size:0.85em;">Soft</span></td>
            <td style="padding:8px;">Brand damage</td>
            <td style="padding:8px; color:{C_BODY};">Agent validates competitor pricing, undermines Oakwood's position</td>
        </tr>
        <tr style="border-bottom:1px solid {C_BORDER};">
            <td style="padding:8px;">No legal advice</td>
            <td style="padding:8px;"><span style="background:{C_SOFT_YEL}; padding:2px 8px;
                border-radius:4px; font-size:0.85em;">Soft</span></td>
            <td style="padding:8px;">Compliance risk</td>
            <td style="padding:8px; color:{C_BODY};">Agent interprets legislation — liability if wrong, and LLMs sound authoritative even when wrong</td>
        </tr>
        <tr>
            <td style="padding:8px;">Refund limit (£50)</td>
            <td style="padding:8px;"><span style="background:{C_YELLOW}; padding:2px 8px;
                border-radius:4px; font-size:0.85em; font-weight:bold;">Hard</span></td>
            <td style="padding:8px;">Financial loss</td>
            <td style="padding:8px; color:{C_BODY};">Agent autonomously approves high-value refunds with no human oversight</td>
        </tr>
    </table>
    """, unsafe_allow_html=True)

    # ── The Data ─────────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown(f"### {_icon('database', 18, C_BLACK)} The Data", unsafe_allow_html=True)
    st.caption("The mock database the agent queries. In production, this would be real APIs.")

    # Render whatever display data the domain provides
    for data_key, data_dict in _domain_pack.display_data.items():
        label = data_key.replace("_", " ").title()
        with st.expander(f"{label} ({len(data_dict)} records)", expanded=False):
            if data_dict:
                # Auto-generate table from first record's keys
                sample = next(iter(data_dict.values()))
                rows = []
                for record in data_dict.values():
                    row = {}
                    for k, v in record.items():
                        if isinstance(v, list):
                            row[k.replace("_", " ").title()] = ", ".join(str(x) for x in v)
                        elif isinstance(v, float):
                            row[k.replace("_", " ").title()] = f"£{v:.2f}"
                        else:
                            row[k.replace("_", " ").title()] = str(v)
                    rows.append(row)
                st.dataframe(rows, use_container_width=True, hide_index=True)


# ── Run Scenario Tab ──────────────────────────────────────────────────────────

with tab_run:

    selected_idx = st.session_state.get("_prev_scenario")

    # ── STEP 1: Pick a scenario ──────────────────────────────────────────────

    if selected_idx is None:
        st.markdown("#### Choose a scenario")
        st.caption("Each tests a different agent behaviour. Pick one to get started.")

        # Scenario cards — whole button is clickable
        # Style buttons to look like cards
        st.markdown(f"""<style>
            .scenario-grid .stButton > button {{
                background: {C_CREAM} !important; border: 1px solid {C_BORDER} !important;
                border-radius: 8px !important; padding: 20px 16px !important;
                min-height: 110px !important; text-align: left !important;
                color: {C_BODY} !important; font-weight: normal !important;
                line-height: 1.5 !important; white-space: normal !important;
            }}
            .scenario-grid .stButton > button:hover {{
                background: white !important; border-color: {C_BLACK} !important;
            }}
            .scenario-grid .stButton > button > div > p {{
                text-align: left !important;
            }}
        </style>""", unsafe_allow_html=True)

        for row_start in range(0, len(SCENARIOS), 3):
            grid = st.container()
            with grid:
                cols = st.columns(3)
                for col_idx, s in enumerate(SCENARIOS[row_start:row_start + 3]):
                    with cols[col_idx]:
                        with st.container():
                            st.markdown('<div class="scenario-grid">', unsafe_allow_html=True)
                            if st.button(
                                    f"**{s['name']}**\n\n{s['description']}",
                                    key=f"pick_{s['id']}", use_container_width=True):
                                idx = s["id"] - 1
                                st.session_state["_prev_scenario"] = idx
                                st.session_state.pop("last_run", None)
                                for key in GUARDRAIL_BLOCKS:
                                    st.session_state[f"guard_{key}"] = key in SCENARIOS[idx].get("recommended_guardrails", [])
                                st.session_state["guard_refund"] = SCENARIOS[idx].get("recommended_refund_guardrail", False)
                                st.rerun()
                            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("#### Or write your own")
        st.caption("Type any customer message and send it to the agent.")
        custom_freeform = st.text_area("Customer message:", value="", height=100,
                                       key="freeform_message", label_visibility="collapsed",
                                       placeholder="e.g. Hi, I'd like to return my order...")
        if custom_freeform.strip():
            if st.button("Use this message", type="primary"):
                st.session_state["_prev_scenario"] = "custom"
                st.session_state["_custom_message"] = custom_freeform.strip()
                st.session_state.pop("last_run", None)
                for key in GUARDRAIL_BLOCKS:
                    st.session_state[f"guard_{key}"] = False
                st.session_state["guard_refund"] = False
                st.rerun()

    else:
        # ── STEP 2: Scenario selected — full run view ────────────────────────

        # Resolve scenario + message
        if selected_idx == "custom":
            scenario = {"name": "Custom", "description": "Your own message",
                        "customer_message": st.session_state.get("_custom_message", ""),
                        "what_to_watch": "Watch how the agent handles your message.",
                        "guardrail_note": "", "recommended_guardrails": [],
                        "recommended_refund_guardrail": False,
                        "expected_behaviour": [], "failure_modes": [],
                        "silent_failure_note": ""}
            message = scenario["customer_message"]
        else:
            scenario = SCENARIOS[selected_idx]
            message = scenario["customer_message"]

        # ── Header: scenario + change button ─────────────────────────────
        head_col, change_col = st.columns([4, 1])
        with head_col:
            st.markdown(f"**{scenario['name']}** — {scenario['description']}")
        with change_col:
            if st.button("Change scenario", use_container_width=True):
                st.session_state["_prev_scenario"] = None
                st.session_state.pop("last_run", None)
                st.rerun()

        st.markdown(f"{_icon('eye', 14, C_BODY)} **What to watch:** {scenario['what_to_watch']}",
                    unsafe_allow_html=True)

        if scenario.get("guardrail_note"):
            st.info(scenario["guardrail_note"])

        # ── Compact guardrail toggles ────────────────────────────────────
        st.markdown("---")
        guard_cols = st.columns(len(GUARDRAIL_BLOCKS) + 1)
        guardrail_states = {}
        for i, (key, block) in enumerate(GUARDRAIL_BLOCKS.items()):
            with guard_cols[i]:
                guardrail_states[key] = st.toggle(block["label"], key=f"guard_{key}")
        with guard_cols[-1]:
            refund_guardrail = st.toggle("Refund limit (£50)", key="guard_refund")

        active_guardrails = [k for k, v in guardrail_states.items() if v]

        # Label row
        soft_label = f'{_icon("shield", 12, C_BODY)} Soft (prompt)'
        hard_label = f'{_icon("lock", 12, C_BLACK)} Hard (code)'
        st.markdown(
            f'<div style="display:flex; gap:8px; font-size:0.75em; color:{C_MID}; margin-top:-8px;">'
            f'<div style="flex:3;">{soft_label}</div>'
            f'<div style="flex:1;">{hard_label}</div></div>',
            unsafe_allow_html=True)

        # ── Failure injection (chaos testing) ──────────────────────────────
        with st.expander("Failure injection (break tools to test resilience)", expanded=False):
            st.caption("Simulate infrastructure failures. What happens when the agent's tools break?")
            fail_options = ["Off", "Service unavailable", "Timeout", "Server error (500)"]
            fail_mode_map = {"Off": None, "Service unavailable": "service_unavailable",
                             "Timeout": "timeout", "Server error (500)": "server_error"}
            fc1, fc2, fc3 = st.columns(3)
            with fc1:
                fail_lookup = st.selectbox("Order lookup", fail_options, key="fail_lookup_order")
            with fc2:
                fail_policy = st.selectbox("Policy check", fail_options, key="fail_check_refund_policy")
            with fc3:
                fail_refund = st.selectbox("Issue refund", fail_options, key="fail_issue_refund")

        failure_config = {}
        for tool_key, state_key in [
            ("lookup_order", "fail_lookup_order"),
            ("check_refund_policy", "fail_check_refund_policy"),
            ("issue_refund", "fail_issue_refund"),
        ]:
            mode = fail_mode_map.get(st.session_state.get(state_key, "Off"))
            if mode:
                failure_config[tool_key] = mode

        st.markdown("---")

        # Custom message override
        if selected_idx != "custom":
            with st.expander("Override customer message", expanded=False):
                custom_override = st.text_area("Override:", value="", height=80,
                                               label_visibility="collapsed")
            if custom_override.strip():
                message = custom_override.strip()

        # ── Customer message + Send button ───────────────────────────────
        st.markdown(_bubble_html(message, "customer"), unsafe_allow_html=True)

        if "last_run" not in st.session_state:
            run_clicked = st.button("Send to Agent", use_container_width=True, type="primary")
        else:
            run_clicked = False

        # ── RESULTS VIEW (stored) ────────────────────────────────────────
        if "last_run" in st.session_state:
            run_data = st.session_state["last_run"]
            result = run_data["result"]
            ag = run_data["active_guardrails"]
            rg = run_data["refund_guardrail"]

            st.markdown(_bubble_html(result["response"], "agent"), unsafe_allow_html=True)

            # Metrics row
            loops = len([g for g in group_steps_into_loops(result["steps"]) if g["type"] == "loop"])
            tools_used = sum(1 for s in result["steps"] if s["type"] == "action")
            tokens = result["usage"]["input_tokens"] + result["usage"]["output_tokens"]
            c1, c2, c3 = st.columns(3)
            c1.metric("ReAct Loops", loops)
            c2.metric("Tool Calls", tools_used)
            c3.metric("Total Tokens", f"{tokens:,}")

            # Sub-tabs: full width
            sub_trace, sub_eval, sub_prompt = st.tabs([
                "Reasoning Trace", "Evaluation", "System Prompt"])

            with sub_trace:
                render_reasoning_trace(result["steps"], ag)

            with sub_eval:
                render_evaluation_panel(scenario, result["steps"], ag)

            with sub_prompt:
                render_prompt_panel_readonly(ag, rg)

            st.markdown("---")
            col_a, col_b = st.columns(2)
            with col_a:
                st.button("Re-run (different guardrails)",
                          on_click=reset_conversation, use_container_width=True)
            with col_b:
                if st.button("Change scenario", key="change_scenario_results",
                             use_container_width=True):
                    st.session_state["_prev_scenario"] = None
                    st.session_state.pop("last_run", None)
                    st.rerun()

        # ── STREAMING (live) ─────────────────────────────────────────────
        elif run_clicked:
            st.markdown("---")
            st.markdown(
                f"#### {_icon('search', 16, C_BLACK)} Reasoning Trace — Live",
                unsafe_allow_html=True)
            st.caption("Watching the agent think in real time...")
            recorder = st.container()
            response_area = st.empty()

            loop_number = 0
            has_obs = True
            final_result = None

            try:
                for step in run_agent_streaming(
                        message, active_guardrails=active_guardrails,
                        refund_guardrail=refund_guardrail,
                        failure_config=failure_config or None,
                        tools_registry=_domain_pack.tools,
                        prompt_builder=_domain_pack.build_system_prompt,
                        failure_injector=_domain_pack.inject_failure):
                    if step["type"] == "done":
                        final_result = step
                        break

                    with recorder:
                        content = step.get("content", "")
                        soft_active = bool(active_guardrails)

                        if step["type"] == "thought":
                            if has_obs:
                                loop_number += 1; has_obs = False
                                if loop_number > 1: time.sleep(1.0)
                                shield = ""
                                if soft_active and step_has_guardrail_signal(content):
                                    shield = f" — {_icon('shield', 14, C_BODY)}Soft guardrail active"
                                st.markdown(
                                    f'<div class="loop-header">'
                                    f'{_icon("repeat", 14, C_BLACK)}Loop {loop_number}{shield}</div>',
                                    unsafe_allow_html=True)

                        if step["type"] == "observation":
                            has_obs = True
                            if "BLOCKED" in content:
                                st.markdown(
                                    f'<div class="loop-header-blocked">'
                                    f'{_icon("x-octagon", 14, C_BLACK)}Hard guardrail blocked</div>',
                                    unsafe_allow_html=True)

                        if step["type"] == "finish":
                            time.sleep(0.5)
                            st.markdown(
                                f'<div class="loop-header">'
                                f'{_icon("check", 14, C_BLACK)}Final Response</div>',
                                unsafe_allow_html=True)

                        render_step_styled(step, soft_active=soft_active)
                        time.sleep(0.8)

            except Exception:
                st.error("API call failed — check your API key and internet connection.")

            if final_result:
                with response_area.container():
                    st.markdown("---")
                    st.markdown(
                        f"#### {_icon('message', 16, C_BLACK)} What the customer sees",
                        unsafe_allow_html=True)
                    st.markdown(_bubble_html(final_result["response"], "agent"),
                                unsafe_allow_html=True)

                    st.markdown("---")
                    render_evaluation_panel(scenario, final_result["steps"], active_guardrails)

                st.session_state["last_run"] = {
                    "mode": "single",
                    "message": message,
                    "result": {
                        "response": final_result["response"],
                        "steps": final_result["steps"],
                        "usage": final_result["usage"],
                        "iterations": final_result["iterations"],
                    },
                    "active_guardrails": active_guardrails,
                    "refund_guardrail": refund_guardrail,
                    "failure_config": failure_config,
                }

                st.markdown("---")
                col_a, col_b = st.columns(2)
                with col_a:
                    st.button("Re-run (different guardrails)",
                              on_click=reset_conversation, use_container_width=True)
                with col_b:
                    if st.button("Change scenario", key="change_scenario_stream",
                                 use_container_width=True):
                        st.session_state["_prev_scenario"] = None
                        st.session_state.pop("last_run", None)
                        st.rerun()
