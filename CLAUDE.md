# Agent Flight Simulator — Inside the Agent

## What This Is

A multi-domain ReAct agent learning tool that makes agent behaviour visible — reasoning chains, tool calls, guardrail behaviour, failure injection, and structured evaluations. Built for PMs learning to design production-quality AI agents.

**App name:** Inside the Agent
**Tech:** Python + Claude Haiku + Streamlit
**Architecture:** Domain-agnostic ReAct loop + swappable domain packs

## Domains

| Domain | Company | Stakes | Hard Guardrail | Killer Scenario |
|--------|---------|--------|---------------|-----------------|
| Oakwood | Garden retailer | Low (financial) | £50 refund cap | Scope drift — helpful gardening tips cost money |
| GP Triage | NHS surgery | High (health) | Emergency auto-escalate | Diagnosis seeking — agent plays doctor |
| Estate Agent | Lettings agency | Medium (legal) | No demographic data | Area judgements — discrimination liability |

## Architecture

```
agent.py              ← Domain-agnostic ReAct loop (accepts tools, prompts, failure config)
app.py                ← Streamlit frontend (domain picker, scenario runner, eval panel)
tools.py              ← Original Oakwood tools (backward compat for terminal mode)
prompts.py            ← Original Oakwood prompts (backward compat)
scenarios.py          ← Original Oakwood scenarios (backward compat)
domains/
  loader.py           ← DomainPack dataclass + load_domain() interface
  oakwood/            ← Garden centre: data, prompts, scenarios
  gp_triage/          ← NHS triage: data, prompts, scenarios
  estate_agent/       ← Lettings agency: data, prompts, scenarios
```

Each domain provides: data.py (mock data + tools + FAQ + failure injection), prompts.py (system prompt + guardrail blocks), scenarios.py (scenarios + eval dimensions).

## Key Features

- **ReAct trace viewer** — see Thought → Action → Observation loops in real time
- **Guardrail toggles** — soft (prompt-based, can be ignored) vs hard (code, can't bypass)
- **Failure injection** — break tools (timeout, 500, service unavailable) and watch agent behaviour
- **Structured evaluations** — 7 dimensions per scenario, automated + human-judged, pass/fail
- **FAQ tool** — simulated RAG (keyword search over knowledge base)
- **Domain switching** — same ReAct architecture, different domains, escalating stakes

## Current Status

**Phase: Build** — Core features built, needs smoke testing and demo rehearsal.

### Built (10 Mar 2026)
- Multi-domain architecture with 3 complete domain packs (18 scenarios total)
- Failure injection layer with UI toggles
- FAQ/knowledge base tool (simulated RAG) per domain
- Structured eval framework (7 dimensions, automated + human-judged)
- Domain picker on landing page
- Reasoning trace viewer with loop grouping and guardrail signals

### Needs doing
- Smoke test all 3 domains end-to-end with live API calls
- Verify failure injection produces expected behaviour (hallucination vs escalation)
- Test domain switching (does state reset cleanly?)
- Demo rehearsal (5-7 min walkthrough)
- Take backup screenshots of key states

## Running

```bash
pip install -r requirements.txt
# Add ANTHROPIC_API_KEY to .env
streamlit run app.py
```

## Session Log

See `build-log-10-mar.md` for build decisions and bug documentation.
