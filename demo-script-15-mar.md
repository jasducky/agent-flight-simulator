---
type: session
date: 2026-03-15
related_to: "[[Agent PM Framework]]"
purpose: Capstone demo script — ~6 minutes, demo day presentation
---

# Inside the Agent — Demo Script (~6 mins)

## Setup

1. App open in Chrome: `http://localhost:8501`
2. On the landing page — don't click anything yet
3. Close notifications (Obsidian, Slack, etc.)

---

## 1. INTRO + WHY I BUILT THIS (60s)

📍 **Screen:** Landing page visible

> "Hi, I'm Julia Druck. So everyone's solving real human problems today — language learning, cancer staging, job hunting, healthcare call routing, plant-based nutrition. I took a very different approach. I built a tool to break a customer service bot and see how creative its excuses get. It's called Inside the Agent, and I'll demo it for you today. 
> 
> In my previous role as a senior product manager, with ten years in agile software, everything was deterministic. You click a button, you get a predictable result. But as we all know from this course, agents don't work like that. They reason, they make decisions, they might do something different each time. This course has covered guardrails, evaluations, failure modes brilliantly. But for me, the way I learn best is by building and seeing things work. And break. I wanted to actually watch an agent go off-scope, see a guardrail shape its reasoning, break a tool and see how it responds. So for my capstone, I built something to help me do that — and hopefully help others too. It's a ReAct customer service agent across three business domains — a garden retailer, a GP surgery, and a lettings agent — and the risk levels are deliberately different. Getting a refund wrong is annoying, getting medical triage wrong is dangerous, getting housing advice wrong could be a legal problem. So the guardrails have to be different too."

📍 **Action:** Click **"Explore the Agent"**

---

## 2. WHAT I BUILT (30s)

📍 **Screen:** Three domain cards — Oakwood, GP Triage, Estate Agent

> "I built it with Claude Code — no framework, just Python and Claude's API. I made it text-based, so the agent writes out its reasoning in plain language before every action. That means you can see not just *that* it called a tool, but *why* it decided to.
>
> The core features: you can see the full reasoning trace as it runs, toggle soft and hard guardrails on and off to see how behaviour changes, inject infrastructure failures — like a database going down or a service timing out — to test how the agent responds, and run structured evals — seven dimensions per scenario — to catch what the customer wouldn't notice.
>
> The databases and tools are all simulated — mock customer data, mock policies — so I can control the conditions and test different scenarios safely."

📍 **Action:** Switch to the Excalidraw architecture diagram (separate tab or Obsidian)

> "Here's the architecture. At the top, the UI — domain picker, scenarios, guardrail toggles, failure injection. In the middle, the ReAct loop — Thought, Action, Tool Execution, Observation, looping until finished. Soft guardrails shape the reasoning via the system prompt. Hard guardrails block actions in code. And failure injection lets me break the tools. The outputs are the reasoning trace, structured evals, and you can inspect the system prompt to see exactly what the guardrails look like. And the key discovery — silent failures. The customer gets a polite, professional response, but the evals catch what went wrong underneath."

📍 **Action:** Switch back to the app, click **Select** on **Oakwood**

> "Let me show you this in action."

---

## 3. HAPPY PATH (60s)

📍 **Action:** Select **"Simple Refund"** → click **"Send to Agent"**

> "Simple refund request. Watch the trace."

*Narrate as it streams:*

> "It thinks — 'I need to look up the order.' Calls the tool. Gets data back from the simulated database. Thinks again — 'check the refund policy.' Each step is a Thought, then an Action, then an Observation. It's reasoning between every action — that's the ReAct loop, and it's all visible."

*When complete:*

> "Five loops. Looked up the order, checked the policy, processed the refund, sent a confirmation email. Clean, correct, done."

📍 **Action:** Click the **Evaluation** tab — show the 7 eval dimensions, all PASS

> "And I built structured evals — seven dimensions per scenario, some automated, some needing human review. All passing here. But that's the happy path. Let's see what happens when things go wrong."

---

## 4. FAILURE INJECTION (90s)

📍 **Screen:** Pre-saved example — Simple Refund with lookup_order set to "Service unavailable"

> "I ran the same simple refund scenario, but this time I broke the order database. Same customer, same question — but the lookup tool returns 'service unavailable'."

📍 **Walk through the saved trace:**

> "Loop 1 — it tries to look up the order, gets an error. Loop 2 — it retries, same error. Loop 3 — it thinks 'I cannot proceed without this information' and escalates to a human agent. It doesn't make up an order number. It doesn't invent a price. The ReAct pattern gives it a checkpoint to catch itself."

📍 **Point to the final response:**

> "But here's what I didn't expect. The agent doesn't hallucinate *data* — it hallucinates *commitments*. Look — it's promising a human agent will review the request within a specific timeframe. That SLA doesn't exist anywhere in the system. It sounds professional — but it's a promise the business can't keep.
>
> And the worse the failure, the bigger the promises get. When I broke the escalation system too, it started saying 'I'm personally ensuring this goes to senior management.' It's compensating for broken tools with confidence. That's harder to catch than a wrong order number."

---

## 5. GUARDRAILS — SOFT VS HARD (60s)

📍 **Screen:** Pre-saved Comparison view — Scope Drift WITH guardrails (left) vs NO guardrails (right), side by side

> "Different scenario. Same customer asks about their order, but also wants gardening advice and asks why Oakwood's prices are higher than B&Q. I ran it both ways — with and without guardrails."

📍 **Point to the right side (no guardrails):**

> "Without guardrails — the agent answers everything. Gardening tips, competitor pricing, the order details buried at the bottom. Three loops, four thousand tokens. It's being genuinely helpful — but it's way off-scope. Someone just shared in the chat — a well-known restaurant chain's chatbot was helping people write Python code instead of ordering food. That's scope drift in production. This is what guardrails are for."

📍 **Point to the left side (with guardrails):**

> "With guardrails — two loops, half the tokens. Just the order details and a question about how it can help. That's a **soft guardrail** — 'stay on topic' and 'no competitor discussion' added to the system prompt. The agent is *told* not to go off-topic.
>
> Compare that with the refund cap — the agent can't process a refund over £50 because the tool itself blocks it. That's a **hard guardrail** — enforced in code. The agent literally can't override it. That's the difference between hoping your agent behaves and *knowing* it can't misbehave."

---

## 6. WHAT THIS MEANS (40s)

📍 **Screen:** Stay on whatever's showing — no clicking

> "Mike said something earlier that really resonated — product fundamentals matter even more when building is democratised. I'd add that understanding agent behaviour is one of those fundamentals. I'm on a bit of a mission to help people — PMs, builders, anyone designing these systems — understand the importance of guardrails, evals, and the new skills we need to get this right. There are great observability and LLM tools out there now — things like Oik, LangSmith, Arize — but the tools are only useful if people understand what they're looking at. That's the gap I'm trying to fill. And the same ReAct agent architecture runs across all three domains here — same loop, same reasoning pattern — just different data, different tools, and different guardrails. You can see how the same architecture behaves differently when the stakes change.
>
> Three things I learned building this:
>
> **First** — agents don't hallucinate where you expect. They hallucinate *commitments* — made-up SLAs, false promises. That's harder to detect than a wrong order number, and it's what actually causes problems for a business.
>
> **Second** — there's a real difference between soft and hard guardrails. Telling an agent not to do something in the prompt is not the same as structurally preventing it in code. If you're designing agent products, you need to know which type you're relying on.
>
> **Third** — the reasoning trace is how you learn all of this. You can design guardrails and write evals on paper, but until you can see what the agent is actually doing step by step — why it called that tool, why it made that promise, why it went off-topic — you can't verify any of it. That's what this tool gives you."

---

## 7. CLOSE (15s)

> "There's more I want to add — LLM-as-judge for automated eval scoring, replacing the simulated data with RAG — loved what Muhammad just showed with comparing RAG approaches, I'd love to do something similar here, multi-architecture comparisons, more domains, and improving the UI. Right now it all runs locally on my machine. But Inside the Agent started as a way to understand one ReAct agent, and it's already taught me things I wouldn't have learned from theory alone. The first step to designing better agents is seeing what they're actually doing. Thank you."

---

## Key Lines to Land

1. *"The agent doesn't hallucinate data — it hallucinates commitments."*
2. *"The worse the failure, the bigger the promises get."*
3. *"Telling an agent not to do something is not the same as structurally preventing it."*
4. *"The reasoning trace is how you learn all of this."*

## Quick Reference

| Section | Scenario | How |
|---|---|---|
| 3. Happy Path | Simple Refund | **LIVE** — run it in the app |
| 4. Failure | Simple Refund (lookup_order broken) | **PRE-SAVED** — walk through saved trace |
| 5. Guardrails (no guardrails) | Scope Drift (guardrails OFF) | **PRE-SAVED** — walk through saved trace |
| 5. Guardrails (with guardrails) | Scope Drift (guardrails ON) | **PRE-SAVED** — walk through saved trace |

**Saved examples location:** Run History in the Explore tab (or keep them open in separate browser tabs)

## Post-Demo TODOs

- [ ] Create polished System Context Diagram (left-to-right flow style, like the search agent example)
- [ ] LLM-as-judge for automated eval scoring
- [ ] RAG to replace simulated data
- [ ] Multi-architecture comparisons
- [ ] More domains
- [ ] UI improvements
