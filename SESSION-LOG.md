---
type: session
date: 2026-03-05
status: in_progress
related_to: "[[Agent PM Framework]]"
goal: Build Agent Flight Simulator — worked example for framework
---

# Agent Flight Simulator — Session Log

## 5 Mar 2026 — Initial Build + Course Correction

### What happened

Claude built all 7 files for Phases 1-3 based on the approved plan:
- `tools.py` — 5 tools, 10 mock orders, 8 refund policies, hard guardrail (£50 limit)
- `prompts.py` — system prompt + 3 soft guardrail blocks
- `agent.py` — ReAct loop with regex parsing, terminal mode
- `scenarios.py` — 6 pre-built customer scenarios
- `app.py` — Streamlit frontend with Flight Recorder trace panel
- `requirements.txt` — anthropic, streamlit, python-dotenv
- `README.md` — setup instructions

**Dependencies installed.** All modules import and pass basic tests (parsing, tool calls, guardrail blocking).

### Course correction

Julia flagged that this skipped the PRD process — the whole point of the framework is that PMs shape the product before code gets written. Two specific issues:

1. **Mock data is hardcoded in Python** — Julia prefers a spreadsheet (CSV/Google Sheet) because it better simulates a real database and is easier to edit without touching code
2. **No PRD was written** — the plan went straight from design to build, bypassing the specification step that the framework teaches

### What exists now (prototype status)

The code works as a rough prototype but should be treated as a **spike**, not the final build. The PRD process should drive what actually ships.

**Files to keep as reference:** All 7 files in `agent-flight-simulator/`
**Key decisions still needed:** See PRD process below.

### Next step

Write a simple PRD for the Agent Flight Simulator. This serves dual purpose:
1. Shapes the actual product (what gets built)
2. Demonstrates the framework's PRD process as a worked example

### Design decisions to capture in PRD

- [ ] Mock data format — CSV spreadsheet, not hardcoded Python dicts
- [ ] Company name and product catalogue — confirm Oakwood Home & Garden
- [ ] Scenario design — which scenarios, what each tests
- [ ] Guardrail taxonomy — which guardrails, hard vs soft distinction
- [ ] UI layout — Streamlit panels, what's visible where
- [ ] ReAct format — confirm Thought/Action/Observation/FINISH pattern
