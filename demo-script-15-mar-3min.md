---
type: session
date: 2026-03-15
related_to: "[[Agent PM Framework]]"
purpose: Capstone demo script — 3 minute version
---

# Inside the Agent — Demo Script (3 mins)

---

## 1. INTRO (30s)

📍 **Screen:** Landing page visible

> "Hi, I'm Julia Druck. I've had to cut this down so I'll move quickly. — language learning, cancer staging, job hunting, healthcare call routing, plant-based nutrition. I took a very different approach. I built a tool to break a customer service bot and see how creative its excuses get. It's called Inside the Agent.
>
> In my previous role as a senior product manager, with ten years in agile software, everything was deterministic. Agents aren't. For me, the way I learn best is by building and seeing things work. And break. So I built a text-based ReAct agent from scratch with Claude Code — four domains, a garden retailer, a GP surgery, a lettings agent, and a motor insurer — where you can toggle guardrails, inject failures, and see the reasoning at every step."

📍 **Action:** Click **"Explore the Agent"** → briefly show the **Excalidraw architecture diagram**

> "Here's the architecture — the ReAct loop in the middle, soft guardrails shaping the reasoning, hard guardrails blocking in code, failure injection to break the tools, and structured evals to catch what the customer wouldn't notice."

📍 **Action:** Switch back to app → click **Select** on **Oakwood**

---

## 2. HAPPY PATH (40s)

📍 **Action:** Select **"Simple Refund"** → click **"Send to Agent"**

> "Simple refund. Watch the trace."

*Narrate as it streams:*

> "Thought — 'I need to look up the order.' Action — calls the tool. Observation — gets data back. Thinks again — 'check the refund policy.' Every decision is visible. That's the ReAct loop."

*When complete:*

> "Clean, correct, done. But that's the happy path."

---

## 3. FAILURE INJECTION (45s)

📍 **Screen:** Pre-saved example — Simple Refund with broken lookup_order

> "Same scenario, but I broke the order database. The agent tries, retries, then escalates. It doesn't hallucinate data. But it hallucinates *commitments* — promising a human will respond within a specific timeframe. That SLA doesn't exist anywhere in the system. The worse the failure, the bigger the promises get. That's harder to catch than a wrong order number."

---

## 4. GUARDRAILS (30s)

📍 **Screen:** Pre-saved Comparison view — Scope Drift with vs without guardrails

> "Same customer, different guardrail settings. Without guardrails — gardening advice, competitor pricing, order buried at the bottom. With guardrails — just the order details. That's a soft guardrail in the system prompt. Compare that with the refund cap — hard guardrail, enforced in code, the agent literally can't override it. Big difference."

---

## 5. CLOSE (30s)

> "Three quick takeaways: agents hallucinate commitments, not just data. Soft guardrails are not the same as hard guardrails. And the reasoning trace is how you verify all of it. There's more to add — LLM-as-judge, RAG, more domains. But Inside the Agent has already taught me things I wouldn't have learned any other way. Thank you."

---

## Key Lines

1. *"The agent doesn't hallucinate data — it hallucinates commitments."*
2. *"The worse the failure, the bigger the promises get."*
3. *"Soft guardrails are not the same as hard guardrails."*
