# Agent Flight Simulator

A teaching tool that makes AI agent internals visible. Built as the primary worked example for the Agent PM Framework.

**The company:** Oakwood Home & Garden (fictional UK retailer)

## What it does

A ReAct customer service agent that you can observe, test, and break. Run pre-built scenarios, toggle guardrails on and off, and watch the agent's reasoning step by step.

## Setup

```bash
cd ~/Claude/Projects/agent_pm_framework/agent-flight-simulator/

# Install dependencies
pip install -r requirements.txt

# Set up your API key
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

## Running

### Terminal mode (Phase 1)
```bash
python agent.py
```
Type a customer message and watch the agent think, act, and respond.

### Streamlit dashboard (Phase 2+)
```bash
streamlit run app.py
```
Opens a browser with scenario selector, guardrail toggles, and the Flight Recorder trace panel.

## Key concepts demonstrated

- **ReAct pattern:** Thought → Action → Observation → repeat until FINISH
- **Hard guardrails:** Code-level blocks that can't be bypassed (£50 refund limit)
- **Soft guardrails:** Prompt-level instructions that the agent MIGHT ignore under pressure
- **Observability:** Seeing every reasoning step, not just the final output

## Files

| File | Purpose | Lines |
|------|---------|-------|
| `agent.py` | ReAct loop — sends to Claude, parses response, calls tools | ~90 |
| `tools.py` | 5 tool functions + mock order/policy data | ~100 |
| `prompts.py` | System prompt + 3 guardrail blocks | ~60 |
| `scenarios.py` | 6 pre-built customer scenarios | ~40 |
| `app.py` | Streamlit frontend with Flight Recorder | ~150 |
