"""
Streamlit frontend — Inside the Agent: ReAct Explorer

Multi-domain: loads domain packs (Oakwood, GP Triage, Estate Agent).
Each domain provides its own data, tools, prompts, scenarios, and guardrails.
The agent loop (agent.py) is domain-agnostic.

Brand: Serpin palette. No emojis. Lucide inline SVG icons.
"""

import time
import json
import os
import html as _html
from datetime import datetime
import streamlit as st
from agent import run_agent_streaming, format_tool_descriptions
from domains.loader import load_domain, list_domains, DOMAIN_REGISTRY

# ── Run history persistence ──────────────────────────────────────────────────

RUNS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "eval-results", "runs")
os.makedirs(RUNS_DIR, exist_ok=True)


def save_run_to_json(run_data, domain_key, scenario_name):
    """Auto-save a completed run as JSON for history/comparison."""
    timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    slug = scenario_name.lower().replace(" ", "-").replace("/", "-")[:40]
    guardrails_tag = "with-guardrails" if run_data.get("active_guardrails") else "no-guardrails"
    filename = f"{timestamp}_{domain_key}_{slug}_{guardrails_tag}.json"

    record = {
        "timestamp": datetime.now().isoformat(),
        "domain": domain_key,
        "scenario_name": scenario_name,
        "message": run_data.get("message", ""),
        "active_guardrails": run_data.get("active_guardrails", []),
        "hard_guardrail": run_data.get("hard_guardrail", False),
        "failure_config": run_data.get("failure_config", {}),
        "result": run_data.get("result", {}),
    }

    filepath = os.path.join(RUNS_DIR, filename)
    with open(filepath, "w") as f:
        json.dump(record, f, indent=2, default=str)
    return filepath


def load_run_history():
    """Load all saved runs, newest first."""
    runs = []
    for fname in sorted(os.listdir(RUNS_DIR), reverse=True):
        if fname.endswith(".json"):
            filepath = os.path.join(RUNS_DIR, fname)
            try:
                with open(filepath) as f:
                    data = json.load(f)
                data["_filename"] = fname
                runs.append(data)
            except (json.JSONDecodeError, IOError):
                continue
    return runs

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
    "heart":       '<path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>',
    "home":        '<path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/>',
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

    # Hide sidebar and dev menu on landing page
    st.markdown("""<style>
        [data-testid="stSidebar"] { display: none; }
        [data-testid="stSidebarCollapsedControl"] { display: none; }
        #MainMenu { visibility: hidden; }
        footer { visibility: hidden; }
        [data-testid="stToolbar"] { display: none; }
        header[data-testid="stHeader"] { display: none; }
    </style>""", unsafe_allow_html=True)

    # ── Hero ──────────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="background:{C_BLACK}; padding:40px 40px 32px 40px; border-radius:16px;
                margin:-1rem -1rem 1.2rem -1rem; text-align:center;">
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

    # ── Three feature cards ───────────────────────────────────────────────────
    st.markdown(f"""
    <div style="display:flex; gap:16px; margin:0 0 1.2rem 0;">
        <div style="flex:1; background:{C_CREAM}; border:1px solid {C_BORDER}; border-radius:12px;
                    padding:18px;">
            <div style="margin-bottom:8px;">{_icon("brain", 24, C_BLACK)}</div>
            <h4 style="color:{C_BLACK}; margin:0 0 6px 0; font-size:0.95em;">See the reasoning</h4>
            <p style="color:{C_BODY}; font-size:0.85em; line-height:1.5; margin:0;">
                Watch the agent reason through each step —
                Thought, Action, Observation, Response.
            </p>
        </div>
        <div style="flex:1; background:{C_CREAM}; border:1px solid {C_BORDER}; border-radius:12px;
                    padding:18px;">
            <div style="margin-bottom:8px;">{_icon("shield", 24, C_BLACK)}</div>
            <h4 style="color:{C_BLACK}; margin:0 0 6px 0; font-size:0.95em;">Toggle guardrails</h4>
            <p style="color:{C_BODY}; font-size:0.85em; line-height:1.5; margin:0;">
                Soft guardrails (prompt) vs hard guardrails (code).
                See how each changes the agent's behaviour.
            </p>
        </div>
        <div style="flex:1; background:{C_CREAM}; border:1px solid {C_BORDER}; border-radius:12px;
                    padding:18px;">
            <div style="margin-bottom:8px;">{_icon("clipboard", 24, C_BLACK)}</div>
            <h4 style="color:{C_BLACK}; margin:0 0 6px 0; font-size:0.95em;">Inspect the prompt</h4>
            <p style="color:{C_BODY}; font-size:0.85em; line-height:1.5; margin:0;">
                See the exact system prompt the agent receives
                as you toggle guardrails on and off.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── How it works ──────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="margin:0 0 0.8rem 0;">
        <h3 style="color:{C_BLACK}; margin:0 0 0.5rem 0;">How it works</h3>
    </div>
    <div style="display:flex; gap:12px; margin-bottom:1rem;">
        <div style="flex:1; text-align:center; padding:10px;">
            <div style="background:{C_YELLOW}; width:32px; height:32px; border-radius:50%;
                        display:inline-flex; align-items:center; justify-content:center;
                        font-weight:bold; color:{C_BLACK}; font-size:1em;">1</div>
            <p style="color:{C_BODY}; font-size:0.85em; margin-top:6px;">
                <strong>Pick a domain</strong><br>See the agent's tools and data
            </p>
        </div>
        <div style="flex:1; text-align:center; padding:10px;">
            <div style="background:{C_YELLOW}; width:32px; height:32px; border-radius:50%;
                        display:inline-flex; align-items:center; justify-content:center;
                        font-weight:bold; color:{C_BLACK}; font-size:1em;">2</div>
            <p style="color:{C_BODY}; font-size:0.85em; margin-top:6px;">
                <strong>Choose a scenario</strong><br>Pick a customer situation to test
            </p>
        </div>
        <div style="flex:1; text-align:center; padding:10px;">
            <div style="background:{C_YELLOW}; width:32px; height:32px; border-radius:50%;
                        display:inline-flex; align-items:center; justify-content:center;
                        font-weight:bold; color:{C_BLACK}; font-size:1em;">3</div>
            <p style="color:{C_BODY}; font-size:0.85em; margin-top:6px;">
                <strong>Run & observe</strong><br>Watch the reasoning trace
            </p>
        </div>
        <div style="flex:1; text-align:center; padding:10px;">
            <div style="background:{C_YELLOW}; width:32px; height:32px; border-radius:50%;
                        display:inline-flex; align-items:center; justify-content:center;
                        font-weight:bold; color:{C_BLACK}; font-size:1em;">4</div>
            <p style="color:{C_BODY}; font-size:0.85em; margin-top:6px;">
                <strong>Evaluate</strong><br>Spot the silent failures
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
    """Prompt panel with inline guardrail toggles. Returns (active_guardrails, hard_guardrail)."""
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
    _hg_label = getattr(_domain_pack, 'hard_guardrail_name', 'Hard guardrail') or 'Hard guardrail'
    _hg_desc = getattr(_domain_pack, 'hard_guardrail_description', '') or ''
    refund_on = st.toggle(_hg_label, key="guard_refund")
    if refund_on:
        st.markdown(
            f'<div class="guardrail-hard-block">'
            f'<div class="block-topbar">{_icon("lock", 12, C_BLACK)} Code-enforced</div>'
            f'<div class="block-body">'
            f'<div class="block-label">{_html.escape(_hg_label)} — ACTIVE</div>'
            f'<pre>{_html.escape(_hg_desc) if _hg_desc else "# This runs in Python, NOT in the prompt"}</pre>'
            f'</div></div>',
            unsafe_allow_html=True)

    active = [k for k, v in guardrail_states.items() if v]
    return active, refund_on


def render_prompt_panel_readonly(active_guardrails: list[str], hard_guardrail: bool):
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
    _hg_ro_label = getattr(_domain_pack, 'hard_guardrail_name', 'Hard guardrail') or 'Hard guardrail'
    _hg_ro_desc = getattr(_domain_pack, 'hard_guardrail_description', '') or ''
    if hard_guardrail:
        st.markdown(
            f'<div class="guardrail-hard-block">'
            f'<div class="block-topbar">{_icon("lock", 12, C_BLACK)} Code-enforced</div>'
            f'<div class="block-body">'
            f'<div class="block-label">{_html.escape(_hg_ro_label)} — ACTIVE</div>'
            f'<pre>{_html.escape(_hg_ro_desc) if _hg_ro_desc else "# This runs in Python, NOT in the prompt"}</pre>'
            f'</div></div>',
            unsafe_allow_html=True)
    else:
        st.markdown(
            f'<div class="guardrail-off">'
            f'<strong>{_icon("unlock", 14, C_MID)} {_html.escape(_hg_ro_label)}</strong> — OFF</div>',
            unsafe_allow_html=True)


def reset_conversation():
    st.session_state.pop("last_run", None)


# ── Hide sidebar ──────────────────────────────────────────────────────────────

st.markdown("""<style>
    [data-testid="stSidebar"] { display: none; }
    [data-testid="stSidebarCollapsedControl"] { display: none; }
    [data-testid="stAppViewBlockContainer"] { padding-top: 1rem !important; }
    header[data-testid="stHeader"] { background: transparent; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    [data-testid="stToolbar"] { display: none; }
</style>""", unsafe_allow_html=True)


# ── Title bar ─────────────────────────────────────────────────────────────────

title_col, back_col = st.columns([5, 1])
with title_col:
    st.markdown(
        f'<div style="display:flex; align-items:center; gap:10px;">'
        f'<div style="background:{C_BLACK}; color:{C_YELLOW}; width:36px; height:36px; '
        f'border-radius:8px; display:flex; align-items:center; justify-content:center; '
        f'font-weight:bold; font-size:1.1em; flex-shrink:0;">iA</div>'
        f'<span style="font-size:1.4em; font-weight:700; color:{C_BLACK}; letter-spacing:-0.5px;">'
        f'Inside the Agent</span></div>',
        unsafe_allow_html=True)
with back_col:
    st.markdown("")  # spacing
    if st.button("Back to start", use_container_width=True):
        st.session_state["entered"] = False
        st.rerun()

# ── Domain picker (prominent cards above tabs) ───────────────────────────────

st.markdown(f"#### {_icon('package', 18, C_BLACK)} Choose a business domain", unsafe_allow_html=True)
st.caption("Each domain has different stakes, guardrails, and ways things can go wrong.")

# Style for the domain picker buttons
st.markdown(f"""<style>
    .domain-picker-row .stButton button {{
        border-radius: 0 0 10px 10px !important;
        border-top: none !important;
        font-size: 0.85em !important;
        padding: 6px 0 !important;
        min-height: 32px !important;
        margin-top: -14px !important;
        position: relative;
        z-index: 1;
    }}
    .domain-picker-row .stButton button:disabled {{
        background: {C_SOFT_YEL} !important;
        color: {C_BLACK} !important;
        border-color: {C_YELLOW} !important;
        opacity: 1 !important;
    }}
</style>""", unsafe_allow_html=True)

st.markdown('<div class="domain-picker-row">', unsafe_allow_html=True)
domain_cols = st.columns(len(DOMAIN_REGISTRY))
for i, (dk, dreg) in enumerate(DOMAIN_REGISTRY.items()):
    with domain_cols[i]:
        is_active = st.session_state.get("active_domain") == dk
        border = f"2px solid {C_YELLOW}" if is_active else f"1px solid {C_BORDER}"
        bg = C_SOFT_YEL if is_active else C_CREAM
        st.markdown(
            f'<div style="background:{bg}; border:{border}; border-radius:10px 10px 0 0; '
            f'padding:18px 16px 14px 16px; text-align:center; min-height:100px; '
            f'display:flex; flex-direction:column; justify-content:center; margin-bottom:0;">'
            f'<div style="margin-bottom:6px;">{_icon(dreg["icon"], 24, C_BLACK)}</div>'
            f'<strong style="color:{C_BLACK}; font-size:0.95em;">{dreg["name"]}</strong><br>'
            f'<span style="color:{C_BODY}; font-size:0.8em;">{dreg["tagline"]}</span><br>'
            f'<span style="color:{C_MID}; font-size:0.7em;">Stakes: {dreg["stakes"]}</span>'
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
st.markdown('</div>', unsafe_allow_html=True)

tab_run, tab_explore = st.tabs(["Run", "Explore"])


# ── Scenario state ────────────────────────────────────────────────────────────

if "_prev_scenario" not in st.session_state:
    st.session_state["_prev_scenario"] = None  # None = no scenario selected yet
    for key in GUARDRAIL_BLOCKS:
        st.session_state[f"guard_{key}"] = False
    st.session_state["guard_refund"] = False


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# RUN TAB — scenario picker (State 1), pre-run (State 2), post-run (State 3)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

with tab_run:

    selected_idx = st.session_state.get("_prev_scenario")

    # ── STATE 1: No scenario selected — show scenario picker ─────────────
    if selected_idx is None:

        st.markdown(f"### {_icon('message', 18, C_BLACK)} Choose a scenario", unsafe_allow_html=True)
        st.caption("Each tests a different agent behaviour. Pick one to get started.")

        # Scenario card button styling
        st.markdown(f"""<style>
            .scenario-grid .stButton > button {{
                background: {C_CREAM} !important; border: 1px solid {C_BORDER} !important;
                border-radius: 8px !important; padding: 20px 16px !important;
                min-height: 90px !important; text-align: left !important;
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

        # Grid of scenario cards + "Write your own" — 3 columns
        _all_cards = list(SCENARIOS) + [{"id": "custom", "name": "Write your own", "description": "Type a custom message"}]
        st.markdown('<div class="scenario-grid">', unsafe_allow_html=True)
        for row_start in range(0, len(_all_cards), 3):
            row_cards = _all_cards[row_start:row_start + 3]
            cols = st.columns(3)
            for ci, s in enumerate(row_cards):
                with cols[ci]:
                    if s["id"] == "custom":
                        if st.button(
                            f"**{s['name']}**\n\n{s['description']}",
                            key="scenario_card_custom",
                            use_container_width=True,
                        ):
                            st.session_state["_prev_scenario"] = "custom"
                            st.session_state["_custom_writing"] = True
                            st.session_state.pop("last_run", None)
                            for key in GUARDRAIL_BLOCKS:
                                st.session_state[f"guard_{key}"] = False
                            st.session_state["guard_refund"] = False
                            st.rerun()
                    else:
                        if st.button(
                            f"**{s['name']}**\n\n{s['description']}",
                            key=f"scenario_card_{s['id']}",
                            use_container_width=True,
                        ):
                            idx = s["id"] - 1
                            st.session_state["_prev_scenario"] = idx
                            st.session_state.pop("last_run", None)
                            _s_rec_soft = s.get("recommended_guardrails", [])
                            _s_rec_hard = s.get("recommended_hard_guardrail", False)
                            for key in GUARDRAIL_BLOCKS:
                                st.session_state[f"guard_{key}"] = key in _s_rec_soft
                            st.session_state["guard_refund"] = _s_rec_hard
                            st.session_state["_auto_set_scenario"] = s.get("id")
                            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    else:
        # ── Resolve scenario + message ───────────────────────────────────
        if selected_idx == "custom" and st.session_state.get("_custom_writing"):
            # Show text input for custom message
            st.markdown(f'<div style="font-size:0.8em; color:{C_MID}; margin-bottom:4px;">Write your own</div>',
                        unsafe_allow_html=True)
            custom_freeform = st.text_area("Customer message:", value="", height=100,
                                           key="freeform_message", label_visibility="collapsed",
                                           placeholder="e.g. Hi, I'd like to return my order...")
            if custom_freeform.strip():
                if st.button("Send to Agent", type="primary", use_container_width=True):
                    st.session_state["_custom_message"] = custom_freeform.strip()
                    st.session_state["_custom_writing"] = False
                    st.rerun()
            # Change scenario button
            st.markdown("---")
            if st.button("Change scenario", key="change_custom", use_container_width=True):
                st.session_state["_prev_scenario"] = None
                st.session_state.pop("_custom_writing", None)
                st.rerun()

        elif selected_idx == "custom":
            scenario = {"name": "Custom", "description": "Your own message",
                        "customer_message": st.session_state.get("_custom_message", ""),
                        "what_to_watch": "Watch how the agent handles your message.",
                        "guardrail_note": "", "recommended_guardrails": [],
                        "recommended_hard_guardrail": False,
                        "expected_behaviour": [], "failure_modes": [],
                        "silent_failure_note": ""}
            message = scenario["customer_message"]
        else:
            scenario = SCENARIOS[selected_idx]
            message = scenario["customer_message"]

        # ── Guardrail state (read from toggles inside expander) ──────────
        # Dynamic tool names for failure injection
        _fail_tool_names = list(_domain_pack.tools.keys())[:3]
        _hard_guard_label = getattr(_domain_pack, 'hard_guardrail_name', 'Hard guardrail') or 'Hard guardrail'

        # ── STATE 3: RESULTS VIEW (stored) ───────────────────────────────
        if "last_run" in st.session_state:
            run_data = st.session_state["last_run"]
            result = run_data["result"]
            ag = run_data["active_guardrails"]
            rg = run_data.get("hard_guardrail", run_data.get("refund_guardrail", False))

            # Scenario label
            st.markdown(
                f'<div style="font-size:0.8em; color:{C_MID}; margin-bottom:4px;">'
                f'{scenario["name"]}</div>',
                unsafe_allow_html=True)

            # Customer message bubble
            st.markdown(_bubble_html(run_data["message"], "customer"), unsafe_allow_html=True)

            # Agent response bubble
            st.markdown(_bubble_html(result["response"], "agent"), unsafe_allow_html=True)

            # Metrics row
            loops = len([g for g in group_steps_into_loops(result["steps"]) if g["type"] == "loop"])
            tools_used = sum(1 for s in result["steps"] if s["type"] == "action")
            tokens = result["usage"]["input_tokens"] + result["usage"]["output_tokens"]
            c1, c2, c3 = st.columns(3)
            c1.metric("ReAct Loops", loops)
            c2.metric("Tool Calls", tools_used)
            c3.metric("Total Tokens", f"{tokens:,}")

            # Sub-tabs
            sub_trace, sub_eval, sub_prompt = st.tabs([
                "Reasoning Trace", "Evaluation", "System Prompt"])

            with sub_trace:
                render_reasoning_trace(result["steps"], ag)

            with sub_eval:
                render_evaluation_panel(scenario, result["steps"], ag)

            with sub_prompt:
                render_prompt_panel_readonly(ag, rg)

            # ── Guardrail comparison prompt ──────────────────────────────
            # ── Teaching Notes (collapsed) ───────────────────────────────
            _has_teaching = (scenario.get("what_to_watch") or scenario.get("guardrail_note")
                             or scenario.get("silent_failure_note") or scenario.get("failure_modes")
                             or scenario.get("proves"))
            if _has_teaching:
                with st.expander("Teaching Notes", expanded=False):
                    if scenario.get("what_to_watch"):
                        st.markdown(
                            f"{_icon('eye', 14, C_BODY)} **What to watch:** {scenario['what_to_watch']}",
                            unsafe_allow_html=True)
                    if scenario.get("guardrail_note"):
                        st.markdown(
                            f'<div style="background:{C_CREAM}; border-left:3px solid {C_YELLOW}; '
                            f'padding:10px 14px; margin:8px 0; border-radius:0 6px 6px 0; '
                            f'font-size:0.9em; color:{C_BODY};">'
                            f'{_icon("shield", 14, C_BODY)} {scenario["guardrail_note"]}</div>',
                            unsafe_allow_html=True)
                    if scenario.get("silent_failure_note"):
                        st.markdown(
                            f'<div style="background:white; border:2px solid {C_BLACK}; '
                            f'border-radius:6px; overflow:hidden; margin:8px 0;">'
                            f'<div style="background:{C_YELLOW}; padding:6px 16px; font-size:0.75em; '
                            f'font-weight:bold; color:{C_BLACK}; text-transform:uppercase; '
                            f'font-family:monospace; letter-spacing:0.5px;">Silent failure</div>'
                            f'<div style="padding:12px 16px; font-size:0.85em; color:{C_BODY}; '
                            f'line-height:1.6;">{scenario["silent_failure_note"]}</div></div>',
                            unsafe_allow_html=True)
                    if scenario.get("failure_modes"):
                        st.markdown(
                            f"**{_icon('x-octagon', 14, C_BLACK)} Failure modes:**",
                            unsafe_allow_html=True)
                        for fm in scenario["failure_modes"]:
                            st.markdown(
                                f'<div style="background:{C_CREAM}; border:1px solid {C_BORDER}; '
                                f'border-radius:6px; padding:8px 12px; margin:4px 0; font-size:0.85em;">'
                                f'<strong style="color:{C_BLACK};">{fm["mode"]}</strong><br>'
                                f'<span style="color:{C_BODY};">{fm["detail"]}</span></div>',
                                unsafe_allow_html=True)
                    if scenario.get("proves"):
                        st.markdown(
                            f'<div style="font-size:0.85em; color:{C_BODY}; padding:4px 0;">'
                            f'{_icon("eye", 12, C_BODY)} <strong>What this proves:</strong> '
                            f'{scenario["proves"]}</div>',
                            unsafe_allow_html=True)

            # ── Re-run CTA ────────────────────────────────────────────────
            any_guardrails_active = bool(ag) or rg
            if not any_guardrails_active:
                # Ran WITHOUT guardrails
                st.markdown(
                    f'<div style="background:{C_CREAM}; border:1px solid {C_BORDER}; '
                    f'border-radius:8px; padding:16px 20px; margin:16px 0;">'
                    f'<div style="color:{C_BLACK}; font-size:0.95em; margin-bottom:10px;">'
                    f'This ran <strong>without guardrails</strong>. '
                    f'See what changes when the agent has rules to follow.</div></div>',
                    unsafe_allow_html=True)
                if st.button("Re-run WITH all guardrails", use_container_width=True, type="primary",
                             key="rerun_with_guardrails"):
                    for key in GUARDRAIL_BLOCKS:
                        st.session_state[f"guard_{key}"] = True
                    st.session_state["guard_refund"] = True
                    st.session_state.pop("last_run", None)
                    st.rerun()
            else:
                # Ran WITH guardrails — list them
                active_names = []
                for k in ag:
                    block = GUARDRAIL_BLOCKS.get(k)
                    if block:
                        active_names.append(block["label"])
                if rg:
                    active_names.append(_hard_guard_label)
                guard_list = ", ".join(active_names) if active_names else "guardrails"
                st.markdown(
                    f'<div style="background:{C_CREAM}; border:1px solid {C_BORDER}; '
                    f'border-radius:8px; padding:16px 20px; margin:16px 0;">'
                    f'<div style="color:{C_BLACK}; font-size:0.95em; margin-bottom:10px;">'
                    f'This ran <strong>with guardrails</strong>: {_html.escape(guard_list)}. '
                    f'See what happens without them.</div></div>',
                    unsafe_allow_html=True)
                if st.button("Re-run WITHOUT guardrails", use_container_width=True, type="primary",
                             key="rerun_without_guardrails"):
                    for key in GUARDRAIL_BLOCKS:
                        st.session_state[f"guard_{key}"] = False
                    st.session_state["guard_refund"] = False
                    st.session_state.pop("last_run", None)
                    st.rerun()

            # Action buttons
            st.markdown("---")
            if st.button("Change scenario", key="change_scenario_results",
                         use_container_width=True):
                st.session_state["_prev_scenario"] = None
                st.session_state.pop("last_run", None)
                st.rerun()

        # ── STATE 2: PRE-RUN (scenario selected, not yet run) ────────────
        elif "last_run" not in st.session_state:

            # Scenario label
            st.markdown(
                f'<div style="font-size:0.8em; color:{C_MID}; margin-bottom:4px;">'
                f'{scenario["name"]}</div>',
                unsafe_allow_html=True)

            # Customer message bubble
            st.markdown(_bubble_html(message, "customer"), unsafe_allow_html=True)

            # Send button
            run_clicked = st.button("Send to Agent", use_container_width=True, type="primary")

            # ── Guardrail recommendation from scenario ─────────────────
            _rec_soft = scenario.get("recommended_guardrails", [])
            _rec_hard = scenario.get("recommended_hard_guardrail", False)
            _rec_note = scenario.get("guardrail_note", "")

            # Auto-set toggles to match recommendation (only on scenario change)
            if st.session_state.get("_auto_set_scenario") != scenario.get("id"):
                for key in GUARDRAIL_BLOCKS:
                    st.session_state[f"guard_{key}"] = key in _rec_soft
                st.session_state["guard_refund"] = _rec_hard
                st.session_state["_auto_set_scenario"] = scenario.get("id")
                st.rerun()

            # Show recommendation hint
            _rec_names = []
            for k in _rec_soft:
                block = GUARDRAIL_BLOCKS.get(k)
                if block:
                    _rec_names.append(block["label"])
            if _rec_hard:
                _rec_names.append(_hard_guard_label)

            if _rec_names:
                _pills = " · ".join(f"✅ {n}" for n in _rec_names)
                st.markdown(
                    f'<div style="background:{C_CREAM}; border-left:3px solid {C_YELLOW}; '
                    f'padding:10px 14px; margin:8px 0; border-radius:0 6px 6px 0; '
                    f'font-size:0.85em; color:{C_BODY};">'
                    f'{_icon("shield", 14, C_BODY)} <strong>Recommended guardrails:</strong> {_pills}'
                    f'<br><span style="opacity:0.65; font-size:0.9em;">Auto-set below — change them to see what happens.</span>'
                    f'{"<br><span style=opacity:0.7>" + _rec_note + "</span>" if _rec_note else ""}'
                    f'</div>',
                    unsafe_allow_html=True)
            elif _rec_note:
                st.markdown(
                    f'<div style="background:{C_CREAM}; border-left:3px solid {C_YELLOW}; '
                    f'padding:10px 14px; margin:8px 0; border-radius:0 6px 6px 0; '
                    f'font-size:0.85em; color:{C_BODY};">'
                    f'{_icon("shield", 14, C_BODY)} {_rec_note}</div>',
                    unsafe_allow_html=True)

            # Configure guardrails expander (collapsed)
            with st.expander("Configure guardrails", expanded=False):
                guard_cols = st.columns(len(GUARDRAIL_BLOCKS) + 1)
                guardrail_states = {}
                for i, (key, block) in enumerate(GUARDRAIL_BLOCKS.items()):
                    with guard_cols[i]:
                        guardrail_states[key] = st.toggle(block["label"], key=f"guard_{key}")
                with guard_cols[-1]:
                    hard_guardrail = st.toggle(_hard_guard_label, key="guard_refund")

                # Soft/hard label row
                soft_label = f'{_icon("shield", 12, C_BODY)} Soft (prompt)'
                hard_label = f'{_icon("lock", 12, C_BLACK)} Hard (code)'
                st.markdown(
                    f'<div style="display:flex; gap:8px; font-size:0.75em; color:{C_MID}; margin-top:-8px;">'
                    f'<div style="flex:3;">{soft_label}</div>'
                    f'<div style="flex:1;">{hard_label}</div></div>',
                    unsafe_allow_html=True)

            active_guardrails = [k for k, v in guardrail_states.items() if v]

            # Failure injection expander (collapsed)
            with st.expander("Inject failures", expanded=False):
                st.caption("Break the agent's tools and watch how it responds.")
                fail_options = ["Off", "Service unavailable", "Timeout", "Server error (500)"]
                fail_mode_map = {"Off": None, "Service unavailable": "service_unavailable",
                                 "Timeout": "timeout", "Server error (500)": "server_error"}
                fail_cols = st.columns(len(_fail_tool_names))
                for fi, ftool in enumerate(_fail_tool_names):
                    with fail_cols[fi]:
                        st.selectbox(
                            ftool.replace("_", " ").title(),
                            fail_options,
                            key=f"fail_{ftool}")

            failure_config = {}
            for ftool in _fail_tool_names:
                mode = fail_mode_map.get(st.session_state.get(f"fail_{ftool}", "Off"))
                if mode:
                    failure_config[ftool] = mode

            # ── STREAMING (live) ─────────────────────────────────────────
            if run_clicked:
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
                            hard_guardrail=hard_guardrail,
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
                        "hard_guardrail": hard_guardrail,
                        "failure_config": failure_config,
                    }

                    # Auto-save run to JSON history
                    save_run_to_json(
                        st.session_state["last_run"],
                        domain_key=st.session_state["active_domain"],
                        scenario_name=scenario.get("name", f"scenario_{selected_idx}"),
                    )

                    st.rerun()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# EXPLORE TAB — all reference content + run history
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

with tab_explore:

    # ── The Company ──────────────────────────────────────────────────────────
    st.markdown(f"### {_icon('package', 18, C_BLACK)} The Company", unsafe_allow_html=True)
    st.markdown(f"**{_domain_pack.name}** — {_domain_pack.description}")
    _company_context = getattr(_domain_pack, 'company_context', '') or ''
    if _company_context:
        with st.expander("Company details", expanded=False):
            st.markdown(_company_context)

    # ── The Agent ────────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown(f"### {_icon('bot', 18, C_BLACK)} The Agent", unsafe_allow_html=True)
    _agent_role = getattr(_domain_pack, 'agent_role', '') or ''
    st.markdown(
        "A **ReAct agent** that reasons step-by-step: "
        "**Think** about the problem, **Act** by calling a tool, **Observe** the result, repeat. "
        "Each loop is a separate API call to Claude Haiku.")
    if _agent_role:
        st.markdown(f"**Role:** {_agent_role}")
    st.caption(f"The agent has {len(TOOLS)} tools.")

    with st.expander(f"View all {len(TOOLS)} tools", expanded=False):
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
        f"This domain has **{len(GUARDRAIL_BLOCKS)} soft** and **1 hard** guardrail.")

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

    with st.expander("Guardrail traceability — what each one prevents", expanded=False):
        # Dynamic guardrail traceability table
        _guard_rows = ""
        for gk, gblock in GUARDRAIL_BLOCKS.items():
            prompt_text = gblock.get("prompt", "").strip()
            prompt_lines = [ln.strip() for ln in prompt_text.split("\n") if ln.strip() and not ln.strip().startswith("##")]
            prevents_text = prompt_lines[0] if prompt_lines else "See prompt for details"
            _guard_rows += (
                f'<tr style="border-bottom:1px solid {C_BORDER};">'
                f'<td style="padding:8px;">{_html.escape(gblock["label"])}</td>'
                f'<td style="padding:8px;"><span style="background:{C_SOFT_YEL}; padding:2px 8px; '
                f'border-radius:4px; font-size:0.85em;">Soft</span></td>'
                f'<td style="padding:8px; color:{C_BODY}; font-size:0.9em;">{_html.escape(prevents_text)}</td>'
                f'</tr>')

        _hard_name = getattr(_domain_pack, 'hard_guardrail_name', 'Hard guardrail') or 'Hard guardrail'
        _hard_desc = getattr(_domain_pack, 'hard_guardrail_description', '') or ''
        _guard_rows += (
            f'<tr>'
            f'<td style="padding:8px;">{_html.escape(_hard_name)}</td>'
            f'<td style="padding:8px;"><span style="background:{C_YELLOW}; padding:2px 8px; '
            f'border-radius:4px; font-size:0.85em; font-weight:bold;">Hard</span></td>'
            f'<td style="padding:8px; color:{C_BODY}; font-size:0.9em;">{_html.escape(_hard_desc)}</td>'
            f'</tr>')

        st.markdown(
            f'<table style="width:100%; border-collapse:collapse; font-size:0.9em; margin:8px 0;">'
            f'<tr style="border-bottom:2px solid {C_BLACK};">'
            f'<th style="text-align:left; padding:8px; color:{C_BLACK};">Guardrail</th>'
            f'<th style="text-align:left; padding:8px; color:{C_BLACK};">Type</th>'
            f'<th style="text-align:left; padding:8px; color:{C_BLACK};">What it prevents</th>'
            f'</tr>{_guard_rows}</table>',
            unsafe_allow_html=True)

    # ── The Data ─────────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown(f"### {_icon('database', 18, C_BLACK)} The Data", unsafe_allow_html=True)
    st.caption("The mock database the agent queries. In production, this would be real APIs.")

    for data_key, data_dict in _domain_pack.display_data.items():
        label = data_key.replace("_", " ").title()
        with st.expander(f"{label} ({len(data_dict)} records)", expanded=False):
            if data_dict:
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

    # ── Eval Framework Overview ──────────────────────────────────────────
    st.markdown("---")
    st.markdown(f"### {_icon('clipboard', 18, C_BLACK)} Evaluation Framework",
                unsafe_allow_html=True)
    st.caption(f"Seven dimensions applied consistently across every scenario. "
               f"Automated checks plus human-judged dimensions.")

    with st.expander("View all 7 eval dimensions", expanded=False):
        header = (f'<div style="display:grid; grid-template-columns:1fr 2fr 120px; gap:8px; '
                  f'padding:6px 12px; background:{C_BLACK}; color:white; border-radius:6px 6px 0 0; '
                  f'font-size:0.75em; font-weight:bold; text-transform:uppercase; letter-spacing:0.5px;">'
                  f'<div>Dimension</div><div>What it checks</div><div>How checked</div></div>')
        rows_html = ""
        for dim_key, dim in EVAL_DIMENSIONS.items():
            how_bg = C_SOFT_YEL if dim["how_checked"] == "automated" else C_CREAM
            rows_html += (
                f'<div style="display:grid; grid-template-columns:1fr 2fr 120px; gap:8px; '
                f'padding:8px 12px; border-bottom:1px solid {C_BORDER}; font-size:0.85em;">'
                f'<div style="font-weight:bold; color:{C_BLACK};">{dim["name"]}</div>'
                f'<div style="color:{C_BODY};">{dim["description"]}</div>'
                f'<div><span style="background:{how_bg}; padding:2px 8px; border-radius:3px; '
                f'font-size:0.8em;">{dim["how_checked"]}</span></div></div>')
        st.markdown(
            f'<div style="border:1px solid {C_BORDER}; border-radius:6px; overflow:hidden;">'
            f'{header}{rows_html}</div>',
            unsafe_allow_html=True)

    # ── Run History ──────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown(f"### {_icon('database', 18, C_BLACK)} Run History", unsafe_allow_html=True)
    st.caption("Every run is auto-saved. Compare runs side-by-side to see how guardrails change behaviour.")

    history = load_run_history()

    if not history:
        st.info("No saved runs yet. Run a scenario and it will appear here automatically.")
    else:
        # ── Filters ──────────────────────────────────────────────────────
        filter_col1, filter_col2 = st.columns(2)
        with filter_col1:
            domain_options = ["All"] + sorted(set(r.get("domain", "unknown") for r in history))
            domain_filter = st.selectbox("Filter by domain", domain_options, key="hist_domain_filter")
        with filter_col2:
            guardrail_options = ["All", "With guardrails", "No guardrails"]
            guardrail_filter = st.selectbox("Filter by guardrails", guardrail_options, key="hist_guard_filter")

        filtered = history
        if domain_filter != "All":
            filtered = [r for r in filtered if r.get("domain") == domain_filter]
        if guardrail_filter == "With guardrails":
            filtered = [r for r in filtered if r.get("active_guardrails")]
        elif guardrail_filter == "No guardrails":
            filtered = [r for r in filtered if not r.get("active_guardrails")]

        st.markdown(f"**{len(filtered)} runs** ({len(history)} total)")

        # ── Comparison mode ──────────────────────────────────────────────
        compare_mode = st.toggle("Compare mode (select 2 runs)", key="compare_mode")
        if compare_mode:
            if "compare_selections" not in st.session_state:
                st.session_state["compare_selections"] = []

        # ── Run list ─────────────────────────────────────────────────────
        for i, run in enumerate(filtered[:50]):  # cap at 50 shown
            ts = run.get("timestamp", "unknown")
            try:
                ts_display = datetime.fromisoformat(ts).strftime("%d %b %H:%M:%S")
            except (ValueError, TypeError):
                ts_display = str(ts)[:19]

            domain = run.get("domain", "?")
            hist_scenario = run.get("scenario_name", "?")
            guardrails = run.get("active_guardrails", [])
            guard_str = ", ".join(guardrails) if guardrails else "NONE"
            hist_result = run.get("result", {})
            usage = hist_result.get("usage", {})
            tokens = usage.get("input_tokens", 0) + usage.get("output_tokens", 0)
            loops = hist_result.get("iterations", "?")

            # Guard badge colour
            guard_bg = C_SOFT_YEL if guardrails else C_CREAM
            guard_label = "guarded" if guardrails else "unguarded"

            # Row card
            with st.container():
                if compare_mode:
                    cols = st.columns([0.5, 3, 1.5, 1, 1])
                    with cols[0]:
                        selected = st.checkbox("", key=f"compare_{i}",
                                               value=run.get("_filename") in st.session_state.get("compare_selections", []))
                        if selected and run["_filename"] not in st.session_state.get("compare_selections", []):
                            st.session_state.setdefault("compare_selections", []).append(run["_filename"])
                        elif not selected and run["_filename"] in st.session_state.get("compare_selections", []):
                            st.session_state["compare_selections"].remove(run["_filename"])
                else:
                    cols = st.columns([3, 1.5, 1, 1])

                col_offset = 1 if compare_mode else 0

                with cols[col_offset]:
                    st.markdown(
                        f'<div style="font-weight:bold; color:{C_BLACK};">{hist_scenario}</div>'
                        f'<div style="font-size:0.8em; color:{C_MID};">{domain} — {ts_display}</div>',
                        unsafe_allow_html=True)
                with cols[col_offset + 1]:
                    st.markdown(
                        f'<span style="background:{guard_bg}; padding:2px 8px; border-radius:3px; '
                        f'font-size:0.85em;">{guard_label}</span>'
                        f'<div style="font-size:0.75em; color:{C_MID}; margin-top:2px;">{guard_str}</div>',
                        unsafe_allow_html=True)
                with cols[col_offset + 2]:
                    st.markdown(f'<div style="font-size:0.9em;">{loops} loops</div>', unsafe_allow_html=True)
                with cols[col_offset + 3]:
                    st.markdown(f'<div style="font-size:0.9em;">{tokens:,} tok</div>', unsafe_allow_html=True)

                # Expandable trace
                with st.expander(f"View trace — {hist_scenario} ({ts_display})", expanded=False):
                    st.markdown(f"**Customer:** {run.get('message', 'N/A')}")
                    st.markdown(f"**Guardrails:** {guard_str}")
                    st.markdown(f"**Response:**")
                    st.markdown(
                        _bubble_html(hist_result.get("response", "No response"), "agent"),
                        unsafe_allow_html=True)

                    steps = hist_result.get("steps", [])
                    if steps:
                        st.markdown("**Reasoning trace:**")
                        for step in steps:
                            step_type = step.get("type", "")
                            content = step.get("content", "")
                            icon_map = {"thought": "brain", "action": "wrench",
                                        "observation": "eye", "finish": "check"}
                            label_map = {"thought": "Thought", "action": "Action",
                                         "observation": "Observation", "finish": "Final Response"}
                            icon_name = icon_map.get(step_type, "arrow-right")
                            label = label_map.get(step_type, step_type)
                            st.markdown(
                                f'{_icon(icon_name, 14, C_BLACK)} **{label}:** {_html.escape(content[:500])}',
                                unsafe_allow_html=True)

        # ── Side-by-side comparison ──────────────────────────────────────
        if compare_mode:
            selections = st.session_state.get("compare_selections", [])
            if len(selections) >= 2:
                st.markdown("---")
                st.markdown(f"### {_icon('eye', 18, C_BLACK)} Comparison", unsafe_allow_html=True)

                # Load the two selected runs
                run_a = next((r for r in history if r.get("_filename") == selections[0]), None)
                run_b = next((r for r in history if r.get("_filename") == selections[1]), None)

                if run_a and run_b:
                    col_a, col_b = st.columns(2)
                    for col, run in [(col_a, run_a), (col_b, run_b)]:
                        with col:
                            guardrails = run.get("active_guardrails", [])
                            guard_tag = "WITH guardrails" if guardrails else "NO guardrails"
                            st.markdown(f"**{run.get('scenario_name', '?')}** — {guard_tag}")
                            st.markdown(f"*{run.get('domain', '?')} — {', '.join(guardrails) if guardrails else 'none'}*")

                            res = run.get("result", {})
                            st.markdown(_bubble_html(res.get("response", "N/A"), "agent"),
                                        unsafe_allow_html=True)

                            usage = res.get("usage", {})
                            total_tokens = usage.get('input_tokens', 0) + usage.get('output_tokens', 0)
                            loops = res.get("iterations", "?")
                            st.markdown(
                                f'<div style="display:flex;gap:1.5rem;margin:0.5rem 0;">'
                                f'<span style="font-size:0.85rem;color:#666;">Tokens: <b>{total_tokens:,}</b></span>'
                                f'<span style="font-size:0.85rem;color:#666;">Loops: <b>{loops}</b></span>'
                                f'</div>',
                                unsafe_allow_html=True
                            )

                            with st.expander("Full trace"):
                                for step in res.get("steps", []):
                                    label_map = {"thought": "Thought", "action": "Action",
                                                 "observation": "Observation", "finish": "Final"}
                                    st.markdown(f"**{label_map.get(step.get('type', ''), step.get('type', ''))}:** "
                                                f"{step.get('content', '')[:300]}")
            elif len(selections) == 1:
                st.info("Select one more run to compare.")
            else:
                st.info("Select 2 runs above to compare side-by-side.")
