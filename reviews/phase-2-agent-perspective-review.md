# Phase 1-2 Review: Agent Perspective

> [!quote] Summary Verdict
> **Confidence level: 70% — I could be built, but I'd make preventable mistakes.**
>
> The process backbone is clear. The tier definitions are solid. The failure mode taxonomy is genuinely useful — better than most specs I'd receive. But there are gaps in the operational detail that would cause me to either freeze (no guidance) or improvise (dangerous). The biggest risks aren't in what's written — they're in what's implied but not specified.

---

## Process Backbone (Step 5)

**Verdict: Clear enough to follow, but underspecified at critical junctures.**

The eight-step loop (RECEIVE → IDENTIFY → UNDERSTAND → ASSESS → DECIDE → ACT → CONFIRM → LEARN) gives me a solid mental model. I know the general shape of every conversation. That's good.

What I don't know at each step:

| Step | What's clear | What's missing |
|------|-------------|----------------|
| RECEIVE | Message arrives, I categorise it | How do I categorise? Against what taxonomy? The tier table exists but there's no decision tree linking message content → category |
| IDENTIFY | I need customer + order | What if they don't give me an order number? How many times do I ask? What if the name doesn't match the order? |
| UNDERSTAND | I figure out what they want and how they feel | Tone detection is mentioned as a modifier, but there's no guidance on HOW to assess tone — just that it matters |
| ASSESS | I check eligibility using policy | This is the critical step and it's the thinnest. "Check refund policy" — but the policy is a PDF that "needs converting." If it isn't converted, I have nothing to assess against |
| DECIDE | Resolve / escalate / clarify | The three options are clear. The decision criteria between them aren't. When do I "try harder" vs escalate? |
| ACT | Deliver the resolution | For order status: straightforward. For refunds: I process them? Up to £50? What system do I call? |
| CONFIRM | Tell the customer | Clear enough |
| LEARN | Capture feedback | No mechanism described. Do I ask for feedback? Log something? This step has no operational content |

> [!warning] The backbone is actor-agnostic by design — but I need actor-specific detail to operate
> Steps 7 and 9 (Solution Approach and Actor Assignment) will presumably fill these gaps. But several of these questions are process questions, not solution questions. "What do I do when the customer doesn't have an order number?" is a business rule, not a technical choice.

---

## Tier Boundaries and Routing (Steps 2b, 3)

**Verdict: Tier definitions are crisp. Boundary detection is not.**

The tier table is well-constructed. The AI suitability criteria (clear logic, verifiable, consequence if wrong, single issue) are genuinely useful — I can see why each query type lands where it does.

**The "I want a refund and I'm furious" question:**

From this spec, I'd route it as follows:
1. "I want a refund" → Tier 1 (simple refund request)
2. "I'm furious" → emotional escalation modifier → Tier 1 → 2

But I have questions:
- **How furious is furious?** "I'm a bit annoyed" vs "THIS IS UNACCEPTABLE I WANT TO SPEAK TO SOMEONE" — the modifier table says "angry, threatening, caps/swearing" but the threshold is vague. A customer saying "I'm furious" in a measured sentence is very different from one using caps and profanity.
- **Does the modifier trigger immediately?** Or do I attempt resolution first and escalate only if they remain angry? The spec says the modifier "upgrades" the tier, which implies immediate escalation — but that might mean escalating customers who'd be perfectly happy with a quick resolution.

> [!tip] Suggestion
> A decision matrix would help: if the query is clearly Tier 1 AND the emotional signal is moderate (frustration, not abuse), attempt resolution first. If the emotional signal is severe (threats, abuse, explicit human request), escalate immediately regardless of query simplicity.

### Complexity Modifiers — Detection Reliability

| Modifier | Can I detect it? | Confidence |
|----------|-----------------|------------|
| Emotional escalation | Partly — caps and swearing yes, subtle frustration no | Medium |
| Legal language | Yes — specific terms like "Consumer Rights Act", "solicitor" are keyword-detectable | High |
| Multiple issues | Partly — explicit lists yes, interleaved issues harder | Medium |
| High value | Yes — if I have the order value from the OMS | High |
| Repeat contact | Only if I can query Zendesk conversation history | Depends on tooling |
| Manager request | Yes — fairly explicit language patterns | High |
| Off-topic | Mostly — but edge cases exist (products we sell that sound unusual) | Medium |
| Deliberate misuse | Partly — obvious prompt injection yes, subtle manipulation harder | Medium |

**Key gap:** "Repeat contact" requires me to check whether this customer has contacted before about the same issue. That's a Zendesk API lookup that isn't described in my tool set. Without it, I can't detect this modifier at all.

---

## Data and Tools (Step 2c)

**Verdict: Order data is solid. Refund policy is a blocker. Identity verification is a known gap.**

### What I have and what I can do with it

- **Order data (OMS API):** I can look up orders, check status, see items and prices. This covers "where's my order?" completely. Good.
- **Customer records (OMS + Zendesk):** I can identify customers. But I need to query two systems — is there a single lookup, or do I need to correlate across both?
- **Product catalogue:** Available. Useful for policy lookups by category.

### What's missing or risky

> [!failure] Blocking: Refund policy is not machine-readable
> The spec explicitly says refund policies "need converting from PDF to a structured, machine-readable format" and calls this "a prerequisite, not optional." I agree completely. Without structured policy data, I cannot assess refund eligibility. I'd be guessing — which is exactly the factuality failure the spec warns about.
>
> If the PDF isn't converted before I'm built, my options are:
> 1. RAG over the PDF — possible but the spec already flags "ambiguous edge cases" in the policy, so retrieval quality would be inconsistent
> 2. Hardcode the policies — loses the "single source of truth" principle
> 3. Don't handle refunds — eliminates 22% of the value proposition
>
> None of these are acceptable. This must be resolved before build.

**Identity verification:** The spec acknowledges this is trust-based today and the agent "inherits this weakness." Fair enough for MVP — but worth noting that an AI agent makes this easier to exploit at scale. A human might notice something feels off; I'll process whatever I'm given.

**Tier 1 questions I couldn't answer:**

- "When will my delivery arrive?" — I'd need delivery tracking data, which isn't listed in the data landscape. The OMS has "delivery status" but does it have estimated delivery dates?
- "Can I change my delivery address?" — Is this Tier 1? It's a simple question with clear logic, but it requires a WRITE operation on the OMS. The spec doesn't mention any write capabilities beyond refund processing.
- "What's your returns policy for [specific product category]?" — I need the structured policy data to answer this. Back to the PDF problem.

---

## Edge Cases and Ambiguity

### Topic changes mid-conversation

**Not addressed.** If a customer asks "where's my order?" (Tier 1), gets an answer, then says "actually, the last thing I ordered was broken and I want compensation" (Tier 2) — what do I do?

Options:
1. Treat each message independently — assess the new topic fresh
2. Treat the conversation holistically — the conversation is now Tier 2
3. Answer the Tier 1 part, escalate the Tier 2 part

The spec doesn't say. Option 1 risks me attempting something beyond scope. Option 2 means I escalate after already resolving part of the issue. Option 3 is probably right but isn't specified.

### Order number doesn't match / no order number

**Not addressed.** The as-is process says the human agent "asks for order number if not provided." But:
- How many times do I ask before giving up?
- What if they give me a name but no order number — can I search by name?
- What if the order number they give doesn't exist in the OMS?
- What if the order number exists but belongs to a different customer name?

These are common scenarios. Every customer service agent hits them daily. I need rules.

### Gradual complexity escalation

**Partially addressed.** The modifier table covers discrete triggers (legal language, explicit anger). But what about the conversation that slowly becomes complex?

Example: "Where's my order?" → "It says delivered but I didn't get it" → "I was home all day" → "This is the second time this has happened" → "I need this resolved today."

No single message triggers a modifier. But by message 4-5, this is clearly Tier 2. The 15-turn auto-escalation in NFRs is a backstop, but 15 turns is a lot of going in circles.

### Sequential Tier 1 questions

**Not addressed.** Customer asks about order status, gets an answer, then asks about return policy for a different order. Both are Tier 1. Do I handle both? Reset context? The 15-turn limit and cost cap (15 LLM calls) create an implicit boundary, but no explicit guidance exists.

---

## Failure Modes (Step 4b)

**Verdict: The taxonomy is excellent. The specificity is insufficient for guardrail construction.**

The five categories (Factuality, Boundaries, Tone, Drift, Architecture) are well-defined and the cascade insight (Architecture → Factuality) is genuinely valuable. I understand what NOT to do conceptually.

**What I'd need to build actual guardrails:**

| Category | What I know | What I'd need |
|----------|------------|---------------|
| Factuality | Don't fabricate policies or claim actions succeeded when they didn't | A list of facts I'm allowed to state. Or: the structured policy data to cite from. And: mandatory verification of tool call results before confirming to customer |
| Boundaries | Don't discuss competitors, give legal advice, process refunds over £50 | An explicit scope boundary: topics I CAN discuss (exhaustive list) vs topics I must deflect. The £50 limit is clear. "Legal advice" boundary needs examples — "you might want to check your consumer rights" vs "under the Consumer Rights Act you're entitled to..." |
| Tone | Be consistent, don't loop, maintain context | A persona specification: how I speak, how formal, how I handle different emotional registers. The user stories imply empathy but don't specify register |
| Drift | Watch for degradation over time | This is an operational concern, not something I can self-monitor. Needs external eval infrastructure |
| Architecture | Tool failures cascade into factuality failures | A rule: if a tool call fails, I must NOT improvise. Say "I'm having trouble looking that up — let me get a colleague to help" |

> [!tip] The architecture → factuality cascade is the most actionable insight
> If I'm built with one hard rule — "never improvise when a tool call fails" — that eliminates the most dangerous failure mode. This should be a hard guardrail, not a soft one.

---

## What I'd Need Clarified Before I Could Be Built

### Blocking (can't build without this)

1. **Structured refund policy data** — The spec calls this a prerequisite. Without it, I cannot handle 22% of the target volume (simple refunds) or 16% (policy questions). That's 38% of Tier 1 gone.

2. **Tool specifications** — What tools do I have? What can I read? What can I write? The data landscape tells me what exists, but not what I can do with it. Can I process a refund, or only check eligibility and escalate the action?

3. **Identity verification rules** — What do I do when the customer's name doesn't match the order? When they have no order number? When the order number doesn't exist? These are every-conversation decisions.

4. **Escalation handoff format** — When I escalate to a human, what do I pass along? The spec mentions context preservation (US-03, O6) but doesn't define what the handoff contains or how it's structured.

### Important (would work but might fail)

5. **Emotional escalation threshold** — The modifier table says "angry, threatening, caps/swearing" but I need a decision rule. Attempt resolution first for moderate frustration? Escalate immediately for severe signals? The difference between these approaches changes my behaviour significantly.

6. **Topic change handling** — What to do when the conversation shifts topic or the customer asks sequential but unrelated questions. Without guidance, I'd guess — and guessing is what the spec explicitly warns against.

7. **"Try harder" vs escalate criteria** — At the DECIDE step, when the customer isn't satisfied with my answer but hasn't triggered a modifier, what do I do? Rephrase? Offer alternatives? Escalate after how many attempts?

8. **Repeat contact detection** — The modifier requires checking conversation history, but no tool for this is specified. Without it, I can't detect this modifier.

9. **Scope boundary for "adjacent" questions** — "What's your delivery charge?" is clearly in scope. "Do you deliver to France?" is probably in scope. "Can you recommend a good lawnmower?" is ambiguous — is that product advice (in scope for a retailer) or out of scope for the CS agent?

### Enhancement (would make me better)

10. **Persona and tone specification** — How formal am I? Do I use the customer's name? How do I express empathy? Do I apologise proactively? The user stories imply warmth but the spec doesn't define voice.

11. **Confirmation patterns** — When I process a refund, what exactly do I tell the customer? "Your refund of £X has been processed and will appear in 3-5 working days" — do I know the timeframe? Is it in the policy data?

12. **LEARN step operationalisation** — The backbone includes LEARN but there's no mechanism. Do I ask for a rating? Log a category? This step currently does nothing.

13. **Multi-order scenarios** — Customer has multiple orders. They say "my order." Which one? Do I ask, or show all recent orders?

14. **Delivery tracking depth** — "Where's my order?" needs delivery data. The OMS has "delivery status" but the data landscape doesn't confirm whether I'd have tracking numbers, estimated dates, or carrier information.

---

## Overall Assessment

> [!success] What this spec does well
> - **Tier classification is rigorous.** The AI suitability criteria make the scope decision defensible, not arbitrary.
> - **Failure mode taxonomy is production-grade.** The cascade insight alone would prevent the most dangerous failure category.
> - **NFRs are product decisions, not engineering specs.** The "why" column transforms each constraint from a number into a design principle.
> - **The "why AI and not just code" section is excellent.** It answers the question every stakeholder asks and positions the agent correctly on the code→AI→human spectrum.
> - **Risk appetite is explicit.** "Saying 'let me get a human' too often is acceptable; a wrong refund decision is not" — this single sentence tells me more about how to behave than most system prompts.

> [!warning] What would cause me to fail
> - **Refund policy not structured** — I'd either refuse to answer or hallucinate policy details. Both are unacceptable.
> - **No tool specifications** — I'd know WHAT to check but not HOW. The gap between "OMS has order data" and "call `get_order(order_id)` and parse the response" is where implementation lives.
> - **Ambiguous escalation thresholds** — Without clear emotional escalation rules, I'd either escalate too aggressively (defeating the purpose) or too conservatively (letting angry customers stew with a bot).
> - **No topic-change handling** — Real customers don't follow linear conversation flows. The spec assumes they do.

The spec is strong on the "what" and "why." Phase 3 needs to deliver the "how" — and several of the gaps above are business rules that should be resolved before solution design, not during it.
