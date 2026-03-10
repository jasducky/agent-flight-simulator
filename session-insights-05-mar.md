---
type: session
date: 2026-03-05
status: paused
related_to: "[[Agent PM Framework]]"
goal: "Work through customer service agent PRD step by step — methodology worked example"
next_focus: "Phase 3 Solution Design — Step 7 (which backbone steps need AI vs code vs human, and why), Step 7b (solution assumptions), Step 8 (product type classification). This is where the interesting agentic decisions happen."
---

# Session Insights: PRD Walkthrough — 5 Mar 2026

## What We Did

Worked through Phase 1 and Phase 2 of the Storyboard Process for the Oakwood customer service agent PRD. This is the worked example that demonstrates the Agent PM Framework methodology.

Split the PRD into two documents:
- `PRD-customer-service-agent.md` — the worked example (PM specifying a real CS agent)
- `PRD.md` — the meta-layer (flight simulator as a PM learning tool)

## Key Insights for the Framework

### 1. Two-layer PRD for worked examples

When building a teaching tool, you need two PRDs. The inner one (customer service agent) is written as if it's real — this is what PMs learn from. The outer one (flight simulator) is the meta-layer about what to make visible for learning. Don't mix them.

### 2. Business case is estimation, not actuals

At Step 1c, inference costs depend on decisions not yet made (model choice, conversation complexity, escalation rate). The business case at this stage is grounded in **market signals** ("industry reports say 40-60% cost reduction") not specific calculations. Revisit with real numbers after solution design (Step 7).

### 3. The code → AI → human spectrum

A critical question most PRDs don't address: **why AI and not just code?** If Tier 1 queries follow clear rules, a coded workflow could make the decisions. The answer is the INTERFACE — customers write in natural language, provide partial information, use ambiguous phrasing. AI fills the gap between code (can decide but can't understand) and humans (can do everything but are expensive and slow).

### 4. Query landscape before scope decision

The methodology was missing a step. Before deciding scope (Tier 1 only), you need to map the query landscape — what types of enquiries come in, at what volume, with what complexity. Added as Step 2b. Without it, the scope decision is an assertion, not an evidence-based choice.

### 5. AI suitability criteria

Four criteria that determine whether a query type is a good candidate for AI:
- **Clear decision logic?** (not "rule-based" — that implies code could do it)
- **Verifiable?**
- **Consequence if wrong?**
- **Single issue?**

These are reusable — any PM could apply them to their own domain.

### 6. Emotional tone is a modifier, not a query type

"Angry customer" is not a query type — it's a modifier that can apply to ANY query type. A calm refund request and a furious refund request are the same underlying query with different emotional context. This matters because the agent needs to detect tone shifts mid-conversation and escalate, not just route by topic.

### 7. Happy path vs complexity modifiers

The query landscape table is the happy path — what the conversation starts as. Complexity modifiers (emotional escalation, legal language, high value, repeat contact, manager request, off-topic, deliberate misuse) are how reality deviates. The agent must detect when a conversation has left the happy path. A human does this instinctively; an agent needs explicit triggers.

### 8. Failure modes are discovered, not designed

Step 4b (Failure Mode Analysis) is a new addition to the methodology. Guardrails and evals (Step 11) are SOLUTIONS — you can't design solutions without first identifying what they need to solve. Failure mode discovery belongs in Phase 2 (Discovery), before solution design.

### 9. Three buckets of failure

Failures split into three buckets with different implications:
- **Known failures** — things that go wrong today with humans (inconsistency, slow response, wrong policy). The agent should FIX some of these.
- **AI failure categories** — things that didn't happen before or happen differently with AI. Need new thinking.
- **Amplified failures** — existing problems that get WORSE at scale. One wrong prompt = 1,000 identical mistakes.

### 10. Five AI failure categories (consolidated)

Started with Hamel Husain's 5 categories from the AI Evals course. Extended with Drift (Galileo) and Overreach (OWASP). Then consolidated overlaps into five product-level categories:

| Category | The PM question |
|----------|----------------|
| **Factuality** | Is it saying things that aren't true? |
| **Boundaries** | Is it saying or doing things outside its scope or authority? |
| **Tone & Persona** | Is it communicating in the wrong way? |
| **Drift** | Did it used to work but is getting worse? |
| **Architecture** | Did the technical plumbing fail? |

**Why five, not seven:** Safety/Alignment, Instruction Following, and Overreach all collapsed into "Boundaries" — they're all "the agent went beyond what it should." The sub-types (harmful content vs scope drift vs unauthorised actions) matter for severity, but they're the same root problem.

**Why Boundaries needs a words-vs-actions distinction:** Scope drift (discusses competitors) is embarrassing. Overreach (processes unauthorised refund) costs money. Same category, very different guardrail design — prompt guardrails for words, code-enforced permissions for actions.

### 11. Failures cascade — architecture is the dangerous one

When tools or retrieval fail, the LLM doesn't error out — it COVERS for the failure. A failed tool call becomes "your refund has been processed" (it hasn't). A missed retrieval becomes a fabricated order status. From the outside it looks like a factuality problem, but the fix is completely different (fix the tool, not the prompt). **Always trace back to root cause.**

### 12. Security as non-functional requirements

PMs don't write pen test plans. Security concerns (prompt injection, data poisoning, information leakage) are captured as requirements ("the system must resist prompt injection") — engineering and security teams design and test the solutions. It's a line item, not a section.

### 13. CSAT is a guard metric, not a stretch target

Two types of KPI for agentic products:
- **Improvement metrics** — the reason you're building this (speed, cost, consistency)
- **Guard metrics** — things that must not get worse (CSAT, accuracy, trust)

CSAT dropping below its current level is a rollback trigger. You can't trade customer satisfaction for efficiency.

### 14. Opportunities are business opportunities, not user wishes

Customers prefer humans — they don't want a chatbot. The opportunities are framed from the business perspective: deliver better outcomes at lower cost. Not "automate X" (that's a solution) but "resolve simple queries instantly" (that's an outcome).

## Research Sources Discovered

- **Hamel Husain's 5 failure categories** — in Julia's own course notes at `AgenticAI_PM_Feb26/modules/guardrails-evals-unified-model.md`
- **Microsoft Taxonomy of Failure Modes in Agentic AI** — 27 failure modes, safety + security focus
- **Galileo's 7 Agent Failure Modes** — engineering/debugging focus, includes Drift
- **OWASP Top 10 for LLMs 2025** — security focus, includes Excessive Agency
- **Multi-Agent System Failure Taxonomy (MAST)** — 14 failure modes in 3 categories

## Core Thesis: Why Failure Mode Analysis Is PM Work Now

In traditional software, failure modes are bugs — engineering finds and fixes them. The PM writes acceptance criteria, QA tests against them, clear handoff. With agents, failure modes moved from being **technical concerns** to being **product decisions**:

**What changed:**
1. **Failures are product choices, not bugs.** Should the agent discuss competitors? What error rate on refunds is acceptable? When should it escalate? These are brand, business, and risk decisions — PM territory.
2. **Failures are probabilistic.** Traditional software either works or crashes. An agent works 95% of the time. The PM decides if that's good enough, and for which scenarios it isn't.
3. **Failures are invisible.** A bug shows an error message. An agent fabricating a policy sounds identical to an agent citing a real one. Someone has to define what to look for — that's PM work.
4. **Failures change over time.** Drift means what works at launch may degrade silently. The PM's job doesn't end at ship — it's a continuous loop.
5. **The input space is infinite.** You can't enumerate every possible customer message. The PM has to think in categories of failure, not individual test cases.

**The PM isn't doing engineering's job.** They're doing their own job in a new context — defining what acceptable behaviour looks like. PMs have always done this. It's just that "acceptable behaviour" now includes "what happens when the system is wrong" — because the system WILL be wrong sometimes. That was never true with deterministic software.

**Connection to the quality loop:** Failure mode discovery in Step 4b feeds the entire lifecycle: specify (guardrails address discovered failures) → deploy → observe (monitoring catches failures in production) → discover (new failure modes emerge) → update (refine spec and guardrails) → redeploy. The PM owns this loop.

**Connection to the 70-75% skills delta:** This is part of the genuine 25-30% that's NEW for PMs. Traditional PMs never had to think about probabilistic failure modes, invisible errors, or quality degradation over time.

### 15. Tier terminology is industry standard — explain it, don't assume it

Tier 1/2/3 is standard customer service language, not something we invented. Tier 1 = simple, scripted, high volume. Tier 2 = needs investigation or judgement. Tier 3 = specialist or escalation. Important to explain this in the PRD because PMs from other domains won't know it. The terminology also maps cleanly to AI suitability — Tier 1 is the natural starting point because the queries have clear decision logic and low consequences if wrong.

### 16. As-Is Process needs channels, identification, and systems

Step 2a wasn't just missing the query landscape (Step 2b) — it was also missing **how** customers interact. Channels matter (chat 60%, email 40% — each has different constraints for AI). The identification process matters (order number → system lookup → verify name/postcode). And the systems involved matter (OMS, refund platform, customer records, product catalogue, conversation history). You can't design an agent without knowing what it needs to connect to and how customers reach it.

### 17. Data Landscape is a prerequisite step (Step 2c)

New methodology step. Before you can decide what an agent does, you need to know what data exists, where it lives, what format it's in, and how accessible it is. The Oakwood example surfaced a critical insight: refund policies exist as PDF documents — the agent can't use them without conversion to a searchable format. Product catalogue has 15,000 SKUs with inconsistent descriptions. Conversation history is unstructured text. **Data quality and accessibility determines what the agent can actually do.** This isn't a technical concern — it's a scope constraint that the PM needs to surface early.

## Methodology Changes to Consider

1. **Add Step 2b (Query Landscape)** to the storyboard methodology — not just "as-is process" but "what actually comes in"
2. **Add Step 2c (Data Landscape)** — data sources, quality, format, accessibility as a prerequisite for solution design
3. **Add Step 4b (Failure Mode Analysis)** — three-bucket discovery before solution design
4. **AI suitability criteria** could become a reusable template/checklist
5. **Complexity modifiers** pattern could be generalised beyond customer service
6. **Five failure categories** could become the standard PM risk discovery framework
7. **Guard vs improvement KPIs** pattern could be added to Step 3 guidance
8. **Channels and identification** should be explicit prompts in Step 2a guidance

## What's Next

- **Phase 3: Solution Design** — the next working session
  - **Step 7 — Solution Approach:** Take each backbone step (RECEIVE → IDENTIFY → UNDERSTAND → ASSESS → DECIDE → ACT → CONFIRM → LEARN) and decide: AI, deterministic code, or human? This is where the code → AI → human spectrum insight gets applied concretely.
  - **Step 7b — Solution Assumptions:** What are we betting on at the solution level? (e.g. "LLM can reliably classify tier mid-conversation", "tool calls will be fast enough for chat")
  - **Step 8 — Product Type Classification:** What kind of agentic product is this? (user-facing hybrid, agent-only, agent-assisted workflow, multi-agent)
- **Phase 4: Agent Specification** — after Phase 3
  - Steps 9 (Actor Assignment), 10 (Agent & System Stories), 11 (Guardrails & Evals)
- **Meta-layer PRD** (`PRD.md`) — the flight simulator as PM learning tool. Needs its own pass separately.
- **Methodology updates** — 8 changes identified (see above). Consider incorporating into storyboard methodology v1.1 after the worked example is complete.
