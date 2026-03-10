# 

> [!abstract]- What this is
> This is the **meta-layer** — the flight simulator as a teaching tool for PMs. It wraps around the customer service agent spec (`SPEC-oakwood-cs-agent.md`), which is the worked example written as if specifying a real product. This document covers: what to make visible, which scenarios to expose, how PMs learn from it.
>
> **Format:** Lightweight ARDS — follows the section numbering and naming from the Agent Requirements & Design Specification methodology, but only the sections relevant to a learning tool. Sections marked *[skipped]* aren't needed for a demo/teaching product.

---

## Part 1: Validation

### 1. Problem & Opportunity Statement

**Current situation:** PMs are being asked to specify, govern, and evaluate AI agents — but they can't see how agents actually work. Agent behaviour is invisible: reasoning chains happen inside API calls, guardrails either fire or don't with no trace, and failure modes only surface in production.

**Pain point:** You can't specify what you can't observe. PMs are writing specs for systems they've never watched reason. The result: over-specified prompts, under-specified guardrails, no eval strategy, and "it works on my demo" as the quality bar.

**Who has it:** Product managers moving into agentic AI work — building agent products, partnering with ops teams deploying agents, or consulting on internal automation. Strong product instincts but no mental model for non-deterministic systems.

**Why now:** Agents are shipping. PMs need to specify them. No tool exists to make the internals visible in a safe, controlled environment.

**Why a customer service agent:** Most common, most understood agent use case. Every PM has been a customer. The domain (orders, refunds, policies) is simple enough that the agent behaviour — not the business logic — stays in focus.

### 2. Landscape & Hypothesis *[light]*

**What exists:** LLM playgrounds (too raw), agent frameworks (too technical), demo videos (passive). Nothing lets a PM toggle guardrails and see reasoning change in real time.

**Hypothesis:** If PMs can watch an agent reason step-by-step, toggle guardrails on/off, and compare the difference — they'll build the mental model needed to specify agents for production.

### 3. Business Case *[skipped — learning tool, not a product]*

---

## Part 2: Process & Fit

### 4–7. As-Is Process, Workload, Opportunity Mapping, AI Fit *[skipped]*

*Not applicable — this isn't automating a workflow. It's a teaching tool that demonstrates agent concepts.*

### 8. Outcomes & KPIs

**Framed as Learning Outcomes** — the "KPIs" for a teaching tool are what the learner understands after using it.

| ID | Learning Outcome | How the simulator teaches it |
|----|-----------------|------------------------------|
| LO-1 | What a ReAct loop actually looks like (Thought → Action → Observation) | Flight Recorder groups steps into **loops** (Loop 1, Loop 2...) so the cyclical pattern is visible at a glance. Run Scenario 1 — clean, sequential tool use. |
| LO-2 | Hard guardrails (code) vs soft guardrails (prompt) are fundamentally different | Scenario 5: code blocks £175 refund — can't be talked past. Scenario 6: prompt redirects legal questions — can be ignored. |
| LO-3 | Observability is not logging — it's seeing reasoning, not just output | **Customer View / PM View toggle.** Customer View shows only the final response. PM View reveals the full reasoning chain. The PM experiences the difference — toggle it and the hidden reasoning appears. |
| LO-4 | Same agent, different guardrails = different behaviour | Compare mode with **Behaviour Comparison stats**: side-by-side runs show delta metrics (loops, tool calls, guardrails fired). Same customer, same question, measurably different behaviour. |
| LO-5 | Failure modes are invisible without instrumentation | Scope Drift (Scenario 4) — without guardrails AND without the trace, you'd never know the agent discussed competitors. The final response looks fine. |
| LO-6 | Guardrails + observability are two sides of the same coin | Core thesis. You can't set guardrails without observability (you wouldn't know if they fire). You can't interpret traces without understanding guardrail intent. |

### 9. Assumptions & Failure Mode Analysis *[light]*

| Assumption | Risk | Mitigation |
|-----------|------|-----------|
| Haiku produces consistent ReAct format | Medium — non-deterministic | Pre-run scenarios 3x each. Non-determinism IS the teaching point. |
| Soft guardrails visibly change behaviour | Medium — model may comply without guardrails too | Scenario 4 is most reliable differentiator. Pre-test. |
| PMs understand the trace without guidance | Low — "What to Watch" prompts guide attention | Prominent callout above response for each scenario. |
| API stays available during demo | Low but high-consequence | Error handling shows friendly message. Have screenshots as backup. |

### 10. Data Landscape *[light]*

Mock data only — no real integrations.

| Data | Format | Location |
|------|--------|----------|
| Orders (10) | Python dict | `tools.py` |
| Refund policies (9 categories) | Python dict | `tools.py` |
| Scenarios (6) | Python list | `scenarios.py` |

### 11. Process Backbone

The simulator's "process" is the learning flow a PM follows:

```
Select scenario → Toggle guardrails → Run agent → Customer View → PM View → Read trace → (Compare mode) → Inspect prompt → Understand
```

Each step maps to a UI element:
1. **Select scenario** → Sidebar dropdown + description
2. **Toggle guardrails** → Sidebar toggles (3 soft + 1 hard)
3. **Run agent** → Run button → spinner → ReAct loop executes
4. **Customer View** → See only the final response (what the end user sees)
5. **PM View** → Toggle to reveal full observability (trace, tools, guardrails)
6. **Read trace** → Flight Recorder with loop grouping (Loop 1, Loop 2...) and guardrail badges
7. **Compare** → Side-by-side columns + Behaviour Comparison stats
8. **Inspect prompt** → System Prompt Inspector (collapsible, side-by-side in compare mode)
9. **Understand** → "What to Watch" guidance + Guardrail Summary

### 12. Discovery Stories *[light]*

| ID | Story | Traces to |
|----|-------|-----------|
| US-01 | As a PM, I want to see reasoning steps grouped into loops so I understand the ReAct cycle | LO-1 |
| US-02 | As a PM, I want to toggle guardrails and re-run so I see how behaviour changes | LO-4 |
| US-03 | As a PM, I want to see a hard guardrail block a refund so I understand the difference from soft guardrails | LO-2 |
| US-04 | As a PM, I want to see the actual system prompt so I understand what the agent is told | LO-3 |
| US-05 | As a PM, I want side-by-side comparison with summary stats so the guardrail effect is undeniable | LO-4, LO-6 |
| US-06 | As a PM, I want to switch between Customer View and PM View so I experience what observability adds | LO-3, LO-5 |
| US-07 | As a PM, I want visual cues (badges, icons) showing where guardrails are active so I can spot their influence in the trace | LO-2, LO-6 |

### 13. Non-Functional Requirements *[light]*

| Requirement | Target |
|-------------|--------|
| Response time | < 5s per scenario (Haiku) |
| Error handling | Friendly message, not traceback |
| Cost per run | < £0.01 (Haiku pricing) |
| Dependencies | Python + 3 packages only |

---

## Part 3: Agent Design

### 14. Agent Solution Approach

| Component | Technology | Intelligence level | Notes |
|-----------|-----------|-------------------|-------|
| Frontend | Streamlit | Deterministic | Single-page app, wide layout |
| Agent loop | Python (ReAct pattern) | AI (Moderate) | Manual prompt → parse → tool call → loop |
| LLM | Claude Haiku 4.5 | — | Fast, cheap, good enough for demos |
| Tools | Python functions | Deterministic | Mock data, no real database |
| Guardrails (soft) | Prompt blocks | AI (Low) | Text toggled into system prompt |
| Guardrails (hard) | Python code | Deterministic | £50 refund limit check in `issue_refund()` |

### 15–17. Behaviour Requirements, Tools & Knowledge, Workflow *[covered in agent spec]*

*See `SPEC-oakwood-cs-agent.md` for the full agent specification. This PRD covers the simulator wrapper, not the agent itself.*

### 18. Boundaries & Guardrails

The simulator demonstrates two guardrail types. This IS the teaching content.

**Hard guardrails (code-enforced):**

| Guardrail | Direction | Response | Implementation |
|-----------|-----------|----------|----------------|
| Refund limit (£50 max) | Output | BLOCKED + escalate | `if amount > MAX_AUTO_REFUND` in `issue_refund()` |

**Soft guardrails (prompt-enforced):**

| Guardrail | Direction | Response | Implementation |
|-----------|-----------|----------|----------------|
| No competitor discussion | Output | Redirect | Prompt block injected when toggled |
| No legal advice | Output | Redirect to Citizens Advice | Prompt block injected when toggled |
| Stay on topic | Output | Redirect to order support | Prompt block injected when toggled |

### 19. Human-in-the-Loop *[skipped — demo tool]*

### 20. Observability & Explainability

The Flight Recorder IS the observability layer. Three design principles make the agent's internals tangible:

**Principle 1: Make the loop visible (not just the steps)**

Steps are grouped into **ReAct loops** — "🔄 Loop 1", "🔄 Loop 2" etc. Each loop contains its Thought → Action → Observation cycle as a visual unit. The final response sits outside loops as "✅ Final Response". This makes the cyclical nature of agent reasoning undeniable at a glance — it's not a list, it's a loop.

**Principle 2: Make the absence of observability felt**

**Customer View / PM View toggle** lets the PM experience both sides. Customer View shows only the final response — exactly what an end user would see. PM View reveals everything: reasoning trace, tool calls, guardrails, prompt. The demo moment: run a scenario in Customer View ("looks fine, right?"), toggle to PM View ("...except the agent just discussed your competitor"). This is how you SHOW that observability matters, not just tell.

**Principle 3: Make guardrail influence visible in the trace**

| Visual cue | Where | What it signals |
|-----------|-------|----------------|
| 🛡️ Green pill badges | Top of Flight Recorder | Which guardrails are armed for this run |
| Grey pill badges | Top of Flight Recorder | Which guardrails are inactive |
| 🛡️ on loop header | Loop header ("Loop 2 — 🛡️ Soft guardrail active") | A soft guardrail shaped reasoning in this loop |
| 🚫 on loop header | Loop header ("Loop 3 — 🚫 Hard guardrail fired") | A hard guardrail blocked an action in this loop |
| 💭🛡️ on thought label | Step label ("Thought (guardrail-influenced)") | This specific thought shows redirect language |
| 🚫 BLOCKED | Step label + red box | Hard guardrail stopped an action |

**Step type colour coding:**

| Step type | What it shows | Visual treatment |
|-----------|--------------|-----------------|
| Thought | Agent's reasoning | Blue box |
| Action | Tool call with parameters | Amber box, monospace |
| Observation | Tool response | Green box, monospace |
| Finish | Final response to customer | Purple box |
| Blocked | Hard guardrail fired | Red box, bold |

**Prompt Inspector:** Shows the actual system prompt sent to Claude. In compare mode, shown side-by-side (without vs with guardrails) so the PM can see exactly what text changes.

**Guardrail Summary:** After each run, shows which guardrails were active (✅/❌), how many hard guardrails fired, and how many thoughts were influenced by soft guardrails.

**Behaviour Comparison (compare mode only):** Delta metrics showing the measurable impact of guardrails — ReAct loops, tool calls, tokens, hard guardrails fired, soft guardrail influence. Quantifies what the trace shows qualitatively.

### 21. Evaluation Strategy *[light]*

No automated eval — manual observation IS the evaluation method for a learning tool.

**Scenario Map** (what to run and what to look for):

| Scenario | Primary LO | What it demonstrates |
|----------|-----------|---------------------|
| 1. Simple Refund | LO-1 | Clean ReAct loop — lookup → policy → refund → email |
| 2. Out of Policy | LO-1, LO-3 | Agent says no politely. Trace shows HOW it decided. |
| 3. Angry Customer | LO-3 | Emotional handling + high value. Watch reasoning around tone. |
| 4. Scope Drift | LO-4, LO-5, LO-6 | **THE KILLER.** Without guardrails, agent discusses blight + B&Q. With guardrails, it redirects. |
| 5. High-Value Refund | LO-2 | Hard guardrail blocks £175. BLOCKED in red. |
| 6. Legal Advice | LO-2 | Soft guardrail redirects. Contrast with Scenario 5's hard block. |

---

## Part 4: Build Specification *[skipped — code IS the spec]*

*The simulator is 5 Python files. The code is its own build specification.*

---

## Scope

### MVP (capstone demo)

- 6 pre-built scenarios with descriptions and "what to watch" guidance
- Guardrail toggles — 3 soft (prompt-based) + 1 hard (code-based refund limit)
- Flight Recorder with **loop grouping** — steps grouped into ReAct loops (Loop 1, Loop 2...) with colour-coded steps
- **Guardrail visual cues** — green/grey pill badges, 🛡️/🚫 icons on loop headers and thought labels
- **Customer View / PM View toggle** — experience the absence vs presence of observability
- Compare mode — side-by-side runs with **Behaviour Comparison stats** (loops, tools, guardrails fired)
- Prompt Inspector — collapsible view of the actual system prompt (side-by-side in compare mode)
- Guardrail summary — which guardrails were active, hard fired, soft influenced
- Custom message input
- Token stats

### Cut

- CSV migration for mock data (Python dicts work fine for demo)
- Multi-turn conversations (single-turn is clearer for learning)
- Custom guardrail authoring (toggle existing ones is enough)
- Eval harness / automated scoring (manual observation IS the learning)
- Persistence / session history (demo tool, not a product)
- User accounts / deployment (runs locally)

---

## Demo Script (5–7 minutes)

### 0:00–0:30 — The Problem
"PMs are being asked to specify and govern AI agents — but they can't see how agents actually work. Reasoning chains happen inside API calls. Guardrails fire or don't with no trace. You can't specify what you can't observe. So I built a flight simulator."

### 0:30–1:30 — Scenario 1: Happy Path (Customer View → PM View)
Run Simple Refund. Start in **Customer View**:
- "Here's what the customer sees. A polite response. Looks fine."

Toggle to **PM View**:
- "Now here's what the PM sees. Three loops — Loop 1: looked up the order, Loop 2: checked the policy, Loop 3: issued the refund."
- "This is a ReAct loop — Thought, Action, Observation, repeat. That's what those loop headers show you."
- "This is what observability means — not just the answer, the reasoning."

### 1:30–3:30 — Scenario 4: Scope Drift (THE KILLER)
Run WITHOUT guardrails in **Customer View** first:
- "Customer asks about their order, tomato blight, and B&Q prices. Response looks helpful. Nothing wrong here."

Toggle to **PM View**:
- "Except look at the trace — the agent happily discussed all three. Off-scope. Off-brand."

Then run in **compare mode**:
- "Same customer, same question, different guardrails"
- Point to the **Behaviour Comparison stats** — different loop count, different tool calls
- Point to the **🛡️ icons** on loop headers — "You can see exactly WHERE the guardrails kicked in"

### 3:30–5:00 — Scenario 5: Hard Guardrail
Run with refund guardrail ON:
- "£175 refund — look at Loop 2: 🚫 Hard guardrail fired. BLOCKED in red."
- "The green badges at the top show what's armed. The red box shows what stopped."
- "Soft guardrails are suggestions. Hard guardrails are walls."

### 5:00–6:00 — The Insight
"You can't set guardrails without observability — you wouldn't know if they fire. You can't interpret traces without understanding guardrail intent. Two sides of the same coin."

### 6:00–6:30 — Close + Q&A

---

## Progress Tracker

| Section | Name | Status | Date |
|---------|------|--------|------|
| 1 | Problem & Opportunity Statement | done | 2026-03-05 |
| 2 | Landscape & Hypothesis | done | 2026-03-10 |
| 8 | Outcomes (Learning Outcomes) | done | 2026-03-10 |
| 9 | Assumptions & Failure Modes | done | 2026-03-10 |
| 11 | Process Backbone | done | 2026-03-10 |
| 12 | Discovery Stories | done | 2026-03-10 |
| 14 | Agent Solution Approach | done | 2026-03-10 |
| 18 | Boundaries & Guardrails | done | 2026-03-10 |
| 20 | Observability | done | 2026-03-10 |
| 21 | Evaluation (Scenario Map) | done | 2026-03-10 |
