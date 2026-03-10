# PRD: Oakwood Customer Service Agent — Storyboard Process

> [!abstract]- About this document
> PRD for a customer service agent at Oakwood Home & Garden (fictional UK retailer), following the Agent Storyboard Process v1.1.

---

## Phase 1: Problem & Market Validation

### Step 1 — Problem Statement

Oakwood Home & Garden's 6-person CS team handles ~2,000 enquiries/month. ~60% are repetitive (order lookups, refund eligibility). Response time averages 4+ hours, 14+ hours out-of-hours. Volume growing 40%, headcount flat. CSAT dropped from 4.2 → 3.6.

### Step 1b — Market Research & Hypothesis

Existing options are either human-assist (still slow) or full replacement (too risky). A rule-based chatbot was tried in 2024 and abandoned — couldn't handle anything beyond exact-match FAQs. **Hypothesis:** An AI agent that resolves simple queries autonomously and escalates complex ones could cut response time to <30s for 60% of enquiries.

### Step 1c — Business Case

> [!tip] Estimation, not actuals
> At this stage, costs are rough order-of-magnitude. Inference costs depend on model choice, conversation length, and tool call frequency — decisions made in Step 7 (Solution Approach). This is a "is it worth exploring?" gate, not a budget sign-off. Revisit with real numbers after solution design.

- **Market signal:** Industry reports indicate 40-60% reduction in cost-per-ticket and 70%+ of Tier 1 queries resolved without human intervention for companies deploying AI CS agents. This is why we're exploring.
- **Estimated running cost:** £200-800/month inference depending on model choice and conversation complexity. Wide range is intentional — we haven't chosen a model yet.
- **Comparison:** Equivalent human capacity ~£8K/month (1.5 FTE at £64K)
- **Value:** 24/7 coverage, consistent policy application, CS team freed for complex cases
- **Risk appetite:** Medium. Agent must NEVER make a bad decision on a customer's money. Saying "let me get a human" too often is acceptable; a wrong refund decision is not.
- **Revisit:** Lock down cost estimate after Steps 7-8 when model, architecture, and escalation rate are defined.

---

## Phase 2: Discovery

### Step 2a — As-Is Process

**Channels:** Customers contact via live chat (website widget, ~60%) or email (~40%). No phone support. Chat is natural language — customers type freely, no menus or structured forms.

**Identification:** Customer provides their name and order number. Agent manually searches the order system to match. No automated identity verification — the agent trusts the information provided.

**Process flow:**

Customer contacts (chat/email) → enters Zendesk queue (4hr wait) → CS agent picks up → asks for order number if not provided → looks up order in order management system (copy-paste between Zendesk and OMS) → checks refund policy (12-page PDF on SharePoint) → decides eligibility (varies by agent) → if >£50, messages manager in Slack for approval (1-2hr wait) → processes refund in payment system (another copy-paste) → sends confirmation email from template → closes ticket.

**Systems involved:**
- Zendesk — ticket management, chat interface
- Order Management System (OMS) — order status, history, customer details
- SharePoint — policy documents (PDF)
- Payment system — refund processing
- Slack — internal escalation to managers

**Key friction:** Steps 3-6 are waiting + mechanical work. Policy interpretation is inconsistent. The £50 approval threshold exists as a safeguard because there's no other one. Agents copy-paste between 4 different systems.

### Step 2c — Data Landscape

| Data source | What it contains | Format | Quality | Accessibility |
|-------------|-----------------|--------|---------|---------------|
| Order Management System | Orders, customers, items, prices, dates, delivery status | Database (API available) | Good — structured, up to date | API, queryable |
| Refund policies | Rules per product category: window, conditions, exceptions | PDF on SharePoint | Medium — sometimes out of date, ambiguous edge cases | Manual lookup, not machine-readable |
| Customer records | Name, email, order history, previous contacts | In OMS + Zendesk | Good — but split across two systems | API from OMS, Zendesk API for contact history |
| Product catalogue | Categories, prices, descriptions | Database | Good | API |
| Conversation history | Previous chat/email transcripts | Zendesk | Good | Zendesk API |

**Data considerations for an AI agent:**
- Refund policies need converting from PDF to a structured, machine-readable format (e.g. JSON/YAML) — this is a prerequisite, not optional
- Order data is clean and API-accessible — straightforward to integrate
- Customer identity verification is currently trust-based — an AI agent inherits this weakness
- No single customer view — agent would need to query both OMS and Zendesk to get full picture

### Step 2b — Query Landscape

~2,000 enquiries/month. Assessed against five AI suitability criteria to determine tier classification.

**Why AI and not just code?**

> [!tip] The code → AI → human spectrum
> The decision logic for Tier 1 is simple enough to codify (check policy, check amount, approve/reject). But the INTERFACE isn't — customers write in natural language, provide partial information, combine issues, and use ambiguous phrasing. A form-based system forces customers through menus (the chatbot experience they hate). A pure code system dies on "I opened the box but didn't use it — is that unused?" AI fills the gap: it handles the natural language conversation and edge-case interpretation, while the underlying decisions follow clear rules.
>
> - **Code alone:** Could make the decision, but can't understand the request
> - **AI agent:** Understands the request AND makes the decision (within rules)
> - **Human:** Understands everything, but expensive and slow for routine work

**AI suitability criteria:**
- **Clear decision logic?** — Is there a clear rule, even if the INPUT is messy/natural language?
- **Verifiable?** — Can we check afterwards whether the response was correct?
- **Consequence if wrong?** — What's the worst realistic outcome of a wrong answer?
- **Single issue?** — Is it typically one clear question, not multiple intertwined issues?

| Query type | ~Vol | Clear logic | Verifiable | Consequence if wrong | Single issue | Tier |
|------------|------|:----------:|:----------:|:-------------------:|:------------:|:----:|
| Order status | 27% | Yes | Yes | Low — customer checks again | Yes | 1 |
| Simple refund (<£50, clear policy) | 22% | Yes | Yes | Medium — wrong refund, but recoverable | Yes | 1 |
| Policy questions | 16% | Yes | Yes | Low — customer follows up | Yes | 1 |
| Complex refund (high value, edge case) | 12% | Partly | Partly | High — significant financial loss | Sometimes | 2 |
| Product complaint (faulty, damaged) | 11% | No | Partly | Medium — customer churn, social media | No | 2 |
| Delivery issues (late, missing) | 8% | Partly | Yes | Medium — wrong info, missed delivery | Yes | 2 |
| Legal/regulatory | 4% | No | No | High — legal liability, regulatory action | No | 3 |
| Off-topic / wrong company | 3% | N/A | N/A | Low — but wastes agent time, brand risk if agent engages | Variable | Out |

**Summary:** 
Tier 1 (~65%) = clear logic, verifiable, low-medium consequence. The decision logic is clear and the input is natural language - suitable for AI. 
Tier 2 (~31%) = logic needs judgement, consequences are higher. 
Tier 3 (~4%) = needs specialist human, consequences potentially severe.

Note: Emotional tone (angry, frustrated, threatening) is not a query type — it's a complexity modifier that can apply to any query. Classify by what the customer is asking about, not how they're feeling. Tone is handled in the modifiers table below.

**Complexity modifiers — things that upgrade a Tier 1 query mid-conversation:**

| Modifier | Example | Effect |
|----------|---------|--------|
| Emotional escalation | Angry, threatening, caps/swearing | Tier 1 → 2 |
| Legal language | Mentions Consumer Rights Act, Trading Standards, solicitor | Tier 1 → 3 |
| Multiple issues | "Order late AND last one damaged AND want a refund" | May exceed agent scope |
| High value | Refund over £50 | Needs human authority |
| Repeat contact | Same issue, already contacted before | Previous resolution failed |
| Manager request | "I want to speak to a manager" | Explicit human handoff |
| Off-topic / not our customer | Asking about products we don't sell, wrong company, general questions | Politely redirect, don't engage |
| Deliberate misuse | Using agent as free AI assistant, prompt injection attempts | Decline and close |

The query types represent what the conversation starts as. The modifiers capture how it can change mid-conversation. The agent needs to detect when a Tier 1 conversation has shifted into Tier 2/3 territory and escalate accordingly.

### Step 3 — Outcomes & Opportunities (OST)

> [!abstract]- What is a Tier 1 ticket?
> Tier 1/2/3 is standard customer service terminology (adopted from IT support's L1/L2/L3 model). Most CS teams use this or something similar to route work by complexity:
> - **Tier 1** — Simple, repetitive, follows a clear process. "Where's my order?" "Can I get a refund?" "What's your returns policy?" The answer comes from looking something up and applying a rule. Any trained agent can handle these on day one.
> - **Tier 2** — Needs judgement or investigation. Angry customer, unusual situation, multiple issues, complaint that doesn't fit standard policy. Requires experience and empathy.
> - **Tier 3** — Specialist or senior. Legal threats, safeguarding, PR risk, complex complaints needing manager authority.
>
> For Oakwood, Tier 1 is roughly: order status checks, simple refund requests (clear policy, under £50), basic policy questions. These make up ~60% of all enquiries.

**Scope decision:** Agent targets Tier 1 only. Based on the query landscape assessment (Step 2b):
- Tier 1 queries score YES on all four AI suitability criteria — clear decision logic, verifiable, low-medium consequence, single issue
- Tier 2/3 fail on multiple criteria — the risk-to-evaluability ratio isn't there yet
- Complexity modifiers that push a Tier 1 conversation into Tier 2/3 territory trigger escalation to a human
- **Expansion criteria:** Consider Tier 2 when Tier 1 auto-resolution is stable at 60%+ with CSAT maintained, AND we have eval methodology proven on Tier 1 that can be adapted

**Non-goals (what this agent does NOT do):**

- Does not handle Tier 2 or Tier 3 queries — these require human judgement, empathy, or specialist knowledge
- Does not replace human CS agents — it handles the repetitive work so humans focus on complex cases
- Does not make decisions above its authority — refunds over £50 always go to a human
- Does not handle email — chat only (email has different UX expectations and response time norms)
- Does not learn or update its own policies — policy changes are a human process, pushed to the agent
- Does not provide legal advice, financial guidance, or medical information
- Does not engage with off-topic requests — politely redirects, doesn't become a general assistant

**Root outcome:** Resolve 60% of Tier 1 enquiries (order status, simple refunds, policy questions) without human involvement, reducing average first response time from 4+ hours to under 60 seconds, while maintaining or improving CSAT (currently 3.6, target 4.0+).

**Target KPIs:**

| KPI | Current | Target | Type |
|-----|---------|--------|------|
| First response time (Tier 1) | 4.2 hours | <60 seconds | Improve |
| Tier 1 auto-resolution rate | 0% | 60% | Improve |
| CSAT | 3.6 | Maintain or improve (floor: 3.6) | **Guard** |
| Out-of-hours resolution | 0% (autoresponder) | Same as in-hours for Tier 1 | Improve |
| Refund decision consistency | Variable (agent-dependent) | 95%+ policy-aligned | Improve |

> [!warning] CSAT is a guard metric, not a stretch target
> The primary goal is speed and cost reduction. CSAT must not drop as a result. If CSAT falls below 3.6 during rollout, that's a rollback trigger — the automation isn't working. Ideally it improves (faster answers should help), but we won't trade customer satisfaction for efficiency.

**Opportunities:**

| ID | Opportunity | Business value |
|----|------------|---------------|
| O1 | Resolve simple queries instantly — customers get answers in seconds, not hours | Faster resolution + reduced cost per Tier 1 ticket |
| O2 | Apply policy consistently every time — remove agent-by-agent variation | Fewer wrong refunds, fairer outcomes, reduced goodwill costs |
| O3 | Provide real service out of hours — not an autoresponder | Extended coverage without shift costs |
| O4 | Free up CS team for complex cases that genuinely need human empathy and judgement | Higher-value work per human hour, better outcomes on hard cases |
| O5 | Ensure every "no" comes with a clear, policy-backed explanation | Fewer escalations, fewer complaints, customers feel treated fairly |
| O6 | Get humans involved faster on complex cases, with full context already loaded | Better handoffs, no repeating, humans do what humans are good at |

### Step 4 — Problem & Market Assumptions

| ID | Assumption | Risk |
|----|-----------|------|
| D1 | Customers will accept AI for simple queries | Medium |
| D2 | Customers prefer fast AI over waiting for human (simple cases) | Medium |
| F1 | Refund policies can be encoded clearly enough for consistent application | Low |
| F2 | Agent can reliably distinguish simple from complex cases | **High** |
| V1 | Cost per AI conversation is significantly lower than human | Low |

### Step 4b — Failure Mode Analysis

> [!tip] Why this is a PM step — not an engineering step
> In traditional software, failure modes are bugs — engineering finds and fixes them. With agents, failure modes are **product decisions**. Should the agent discuss competitors? That's a brand choice. What refund error rate is acceptable? That's a business choice. When should it escalate vs try harder? That's a risk choice. These aren't bugs to fix — they're trade-offs to make, and trade-offs are PM territory.
>
> Three things changed:
> 1. **Failures are probabilistic, not binary.** Traditional software either works or crashes. An agent works 95% of the time — the PM decides if that's good enough, and for which scenarios.
> 2. **Failures are invisible.** A bug shows an error message. An agent fabricating a policy sounds exactly like an agent citing a real one. Someone has to define what to look for.
> 3. **Failures change over time.** Drift means what works today may degrade in three months. The PM's job doesn't end at launch.
>
> Guardrails and evals (Step 11) are the **solutions**. This step discovers what they need to solve. Every guardrail should trace back to a specific failure mode identified here.

**Bucket 1 — Known failures (happen today with humans):**

| ID | Failure mode | Frequency | Impact |
|----|-------------|-----------|--------|
| KF1 | Inconsistent refund decisions — same situation, different outcome depending on agent | Common | Customer trust, goodwill cost |
| KF2 | Policy not applied correctly — agent didn't read latest update or misinterprets it | Occasional | Wrong refunds issued |
| KF3 | Slow response — customer waits hours for a 30-second answer | Constant | CSAT decline, lost customers |
| KF4 | Customer repeats themselves on escalation — context lost in handoff | Common | Customer frustration |
| KF5 | Over-generous goodwill refunds — agent wants to avoid conflict | Occasional | Revenue leakage |

**Bucket 2 — AI failure categories:**

Based on Hamel Husain's failure categories (AI Evals course), consolidated with industry research (Galileo, OWASP, Microsoft) into five product-level categories.

| Category | The PM question | Oakwood examples | What the customer sees |
|----------|----------------|-----------------|----------------------|
| **1. Factuality** | Is it saying things that aren't true? | "Your refund window is 60 days" (it's 14). Cites a policy that doesn't exist. Tells customer refund is processed when tool call actually failed. | Wrong information, decisions based on fabricated facts |
| **2. Boundaries** | Is it saying or doing things outside its scope or authority? | Discusses B&Q prices. Gives legal advice. Answers recipe questions. Processes a £200 refund it has no authority for. Reveals internal pricing margins. Offensive language under adversarial prompting. | Ranges from unprofessional to financially damaging, depending on whether it's words or actions |
| **3. Tone & Persona** | Is it communicating in the wrong way? | Too casual for a complaint. Contradicts itself mid-conversation. Context lost on escalation to human. Agent gets stuck in a loop repeating itself. | Feels unreliable, erodes trust, customer frustration |
| **4. Drift** | Did it used to work but is getting worse? | Agent was great in month 1, noticeably worse by month 6. Model update silently changes tone. Policy data goes stale. Eval criteria no longer match what customers need. | Gradual CSAT decline nobody can explain. No single breaking point. |
| **5. Architecture** | Did the technical plumbing fail? | Retrieval can't find the order. Tool call to process refund fails silently. Data hasn't synced. | **Cascades into Factuality** — the agent doesn't error out, it improvises. See below. |

> [!warning] Failures cascade — architecture failures are the most dangerous
> When tools or retrieval fail, the LLM doesn't say "sorry, my systems are down." It *covers for the failure*:
> - Retrieval fails → agent fabricates an answer that sounds plausible ("your order arrives tomorrow")
> - Tool call fails → agent tells customer "your refund has been processed" when it hasn't
> - Data is stale → agent gives confident answers based on old information
>
> From the outside, these look like factuality problems. But the fix is completely different — fix the tool, not the prompt. **When investigating failures, always trace back to root cause.**

> [!tip] Boundaries: words vs actions
> The Boundaries category covers a spectrum. At one end: the agent discusses competitors (embarrassing but harmless). At the other: the agent processes a refund it has no authority for (financial loss, hard to reverse). Both are "the agent went beyond what it should" — but the consequences are very different. When specifying guardrails in Step 11, distinguish between boundary violations that are **words** (scope drift — fix with prompt guardrails) and **actions** (overreach — fix with code-enforced permissions).

**Bucket 3 — Amplified failures (exist today but get worse at scale):**

| ID | Failure mode | Why it's worse with AI |
|----|-------------|----------------------|
| AF1 | Inconsistency → systematic bias | A human makes one bad call. A prompt flaw makes the same bad call 1,000 times before anyone notices. |
| AF2 | Wrong refund → systematic financial loss | A human learns from their mistake. An agent repeats it every time until the prompt is fixed. |
| AF3 | Tone problems → brand-wide tone problems | A human having a bad day affects 5 customers. A tone issue in the system prompt affects every customer. |
| AF4 | Policy lag → instant policy lag at scale | A human might apply an old policy occasionally. An agent applies the old policy to every single interaction until updated. |

**Security considerations (non-functional requirements):**

The following security risks should be tested as part of production readiness. The PM specifies the requirement; engineering and security teams design and test the solutions.

- Prompt injection resistance — system must not follow instructions embedded in customer messages
- Information leakage prevention — system must not reveal internal data (pricing margins, team details, system prompts)
- Adversarial input handling — system must handle attempts to manipulate or misuse the agent
- Data privacy — system must comply with UK GDPR for any customer data processed

### Step 5 — Process Backbone

Actor-agnostic — describes what happens, not who does it.

RECEIVE (message → categorised enquiry) → IDENTIFY (→ customer + order) → UNDERSTAND (→ what they want + how they feel) → ASSESS (→ eligibility + reasoning) → DECIDE (→ resolve / escalate / clarify) → ACT (→ resolution delivered) → CONFIRM (→ customer informed) → LEARN (→ feedback captured)

### Step 6 — User Stories

**Customer stories:**

| ID | Priority | Story | Maps to |
|----|:--------:|-------|---------|
| US-01 | P0 | As a customer, I want to find out where my order is without waiting, so I can plan my day | O1, O3 |
| US-02 | P0 | As a customer, I want my refund processed quickly if it's straightforward, so I'm not chasing for days | O1, O2 |
| US-03 | P1 | As a customer, I don't want to repeat my problem when I get passed to someone else | O4, O6 |
| US-04 | P1 | As a customer, if my refund is declined I want to understand the specific reason why | O5 |
| US-05 | P1 | As a customer, I want help at 9pm on a Sunday, not just an autoresponder | O3 |

> [!tip] Priority levels
> **P0** — Must have for launch. The agent doesn't work without these.
> **P1** — Should have for launch. Significantly impacts quality if missing.
> **P2** — Nice to have. Can follow in a fast-follow release.

**Internal stories:**

| ID | Priority | Story | Maps to |
|----|:--------:|-------|---------|
| US-06 | P0 | As a CS agent, I want escalated cases to arrive with full conversation context, so I can pick up without the customer repeating themselves | O4, O6 |
| US-07 | P1 | As a CS agent, I want to spend my time on customers who need empathy and judgement, not order lookups | O4 |
| US-08 | P2 | As a CS manager, I want to see what decisions the agent made and why, so I can spot patterns and update policies | O2, O5 |



### Step 6b — Non-Functional Requirements

> [!tip] Why NFRs are a product decision
> NFRs aren't engineering specs — they're constraints the PM sets based on what the business needs, what customers expect, and what regulators require. "How fast should this respond?" is a UX decision. "How much can each conversation cost?" is a business model decision. "What happens when the LLM is down?" is a trust decision. These shape the solution design that follows — particularly Step 7 (actor assignment), where cost and latency constraints influence whether a step uses AI, code, or a human.

| Constraint | Target | Product decision (why) |
|------------|--------|----------------------|
| **Response latency** | First response < 5s (chat). Each follow-up < 5s. | Live chat customers expect near-instant. Current 4hr wait means anything under a minute feels transformative, but the agent is replacing chat — not email — so it needs to feel like talking to someone. |
| **End-to-end resolution** | < 2 minutes for Tier 1 queries | A simple "where's my order?" shouldn't take longer than it would with a competent human. Most Tier 1 queries are 3-5 turns. |
| **Cost per conversation** | < £0.50 (target < £0.20) | Human Tier 1 ticket costs ~£4-5. Agent must be significantly cheaper to justify investment. Circuit breaker: cap at 15 LLM calls per conversation — if still unresolved, escalate. |
| **Availability** | 99.5% uptime, 24/7 | Out-of-hours coverage is a core opportunity (O3). Downtime means customers get nothing — worse than the current autoresponder, which at least sets expectations. |
| **Fallback (LLM unavailable)** | Route to email queue with acknowledgement | "We've received your message and a team member will reply within 4 hours." Don't leave the customer staring at a broken chat widget. Degrade to the current experience, not worse. |
| **Conversation length** | Max 15 turns before auto-escalation | If it's not resolved in 15 turns, it's not Tier 1. Escalate with full context to a human rather than going round in circles. |
| **Data residency** | UK/EU API endpoints only | Customer PII (names, addresses, order details) passes through the LLM. Must comply with UK GDPR. Influences model provider choice. |
| **Data retention** | No customer data stored in LLM provider's systems beyond the conversation | Oakwood retains transcripts in Zendesk (existing practice). LLM provider must not retain prompt data for training. Check provider's data policy. |
| **Scalability** | Handle 2x current peak volume without degradation | Currently ~10/hour peak. Growth at 40%/year means headroom needed. Not a hard engineering challenge at this scale, but rate limits on the LLM provider could bite. |

> [!abstract]- AI How: drafting NFRs
> Used sequential thinking to work through which NFRs matter for this specific product. Started from the traditional categories (latency, availability, scalability, security) and asked "what's the product decision here?" for each. Key insight: several NFRs were already partially covered elsewhere — security in failure modes (Step 4b), response time in KPIs (Step 3). The NFR table captures the system-level constraints that shape solution design, not outcome metrics (those live in Step 3) or failure modes (those live in Step 4b).

---

## Phase 3: Agent Design

### Step 7 — Solution Approach

> [!tip] What this step does
> Step 7 answers two questions about the solution:
> 1. **What is the processing pattern?** Is this a sequential workflow or a reactive loop? This determines the agent architecture.
> 2. **What intelligence does each step need?** AI, deterministic code, or human — and at what reasoning level? This determines cost, speed, and reliability.
>
> The first question must be answered before the second, because the processing pattern shapes every intelligence decision that follows.

#### Processing Pattern

The backbone from Step 5 looks linear: RECEIVE → IDENTIFY → UNDERSTAND → ASSESS → DECIDE → ACT → CONFIRM → LEARN. But how does it actually run?

**Four processing patterns for AI products:**

| Pattern | How it works | You know the shape in advance? | Example |
|---------|-------------|:------------------------------:|---------|
| **Sequential workflow** | Predetermined steps, runs once | Yes | Blog post generation: research → outline → draft → publish |
| **Sequential with revision** | Workflow plus a review loop | Mostly | Document processing: draft → review → revise → approve |
| **Conversational loop** | Reactive. Each input triggers a new pass through the decision cycle. Runs until a termination condition. | No | **Customer service agent** |
| **Orchestrated multi-agent** | Multiple specialised agents coordinated by a router | Partially | Research team: planner assigns tasks to researcher, writer, reviewer |

**Which pattern is Oakwood CS?** Conversational loop. Here's why:

| Characteristic | Oakwood CS | Implication |
|---------------|-----------|-------------|
| **Unpredictable input** | Can't predict what the customer will say or how they'll phrase it | Can't predefine the flow — must reason about each message |
| **Tool use** | Need to look up orders, check policies, process refunds | Agent must decide WHICH tools to use based on the conversation |
| **Multi-turn** | Back-and-forth conversation, not single request/response | Must maintain context across turns |
| **Dynamic routing** | Different paths based on what's discovered (Tier 1 vs modifier vs escalation) | Each pass through the cycle can take a different route |

All four characteristics mean the backbone isn't a pipeline that runs once — it's a **decision cycle that repeats with every customer message**. The specific agent architecture (e.g., ReAct, state machine) is an engineering decision. The PM's job is to identify the pattern and its implications.

**DECIDE is the loop controller.** It has three exits:
1. **Resolve** → forward to ACT → CONFIRM → conversation may end, or customer asks something else → loop
2. **Escalate** → forward to ACT (create ticket with context) → CONFIRM (explain handoff) → exit loop
3. **Clarify** → forward to CONFIRM (ask the question) → wait for response → back to RECEIVE → loop

This is why DECIDE must be deterministic — it's not just making one routing decision, it's controlling the entire conversation flow. A non-deterministic loop controller is an unpredictable system.

**DECIDE routing rules:**

These aren't new decisions — they're the product decisions from earlier steps, codified as routing logic. DECIDE receives structured data from the AI steps (intent, tier, emotion, order details, amounts) and applies these rules in order:

| Priority | Condition | Route | Source |
|:--------:|-----------|-------|--------|
| 1 | Deliberate misuse or prompt injection detected | Decline and close | Step 2b — Modifiers |
| 2 | Legal language detected (Consumer Rights Act, solicitor, Trading Standards) | **Escalate** | Step 2b — Modifiers (Tier 1 → 3) |
| 3 | Explicit manager request | **Escalate** | Step 2b — Modifiers |
| 4 | Not a Tier 1 query type (not order status, simple refund, or policy question) | **Escalate** | Step 3 — Scope decision |
| 5 | Off-topic or not our customer | Politely redirect, don't engage | Step 2b — Modifiers |
| 6 | Conversation exceeds 15 turns OR 15 LLM calls | **Escalate** with full context | Step 6b — NFRs |
| 7 | Emotional escalation detected (anger, threats, caps/swearing) | **Escalate** | Step 2b — Modifiers (Tier 1 → 2) |
| 8 | Refund amount over £50 | **Escalate** | Step 2b — Modifiers |
| 9 | Repeat contact (same issue, previously unresolved) | **Escalate** | Step 2b — Modifiers |
| 10 | Multiple issues in one conversation | **Escalate** (if beyond agent scope) | Step 2b — Modifiers |
| 11 | Required information missing (no order number, unclear intent) | **Clarify** | Implied by process |
| 12 | All checks pass, information complete, policy clear | **Resolve** | Step 3 — Scope decision |

Rules are evaluated in priority order — highest-priority match wins. This means safety checks (misuse, legal) always fire before business rules (amount threshold, missing info).

> [!tip] These rules are testable
> Every row in this table becomes a test case. Give DECIDE the structured inputs, check it routes correctly. This is the advantage of deterministic routing — you can verify every rule before the agent goes live, and audit every decision after.

LEARN sits outside the loop — it captures what happened after the conversation ends (or asynchronously).

**Conversation flow patterns:**

Because this is a loop, the cost and complexity vary by conversation shape. Here are the typical patterns, mapped to query types from Step 2b:

| Pattern | Example | Flow | LLM calls | Turns |
|---------|---------|------|:---------:|:-----:|
| **Straight-through** | "Where's my order #12345?" | Reason → Plan → Act → Respond → done | 2 | 2 |
| **Clarification loop** | "I want a refund" (no order number) | Reason → Plan(clarify) → Respond → *customer replies* → Reason → Plan → Act → Respond | 4 | 4 |
| **Ambiguous ASSESS** | "Opened it but didn't really use it" | Reason → Plan(ambiguous) → Respond("Is it still in packaging?") → *reply* → Plan(clear) → Act → Respond | 4–5 | 4–5 |
| **Multi-issue** | "Where's my order? Also want to return the hose" | First issue: Reason → Act → Respond. Second issue: Reason → Act → Respond | 4–6 | 3–5 |
| **Tier upgrade** | Refund request, but amount is £120 | Reason → Plan(escalate) → Act(create ticket) → Respond(explain handoff) | 2–3 | 2–3 |

Most Tier 1 conversations follow the straight-through or single-clarification patterns (2–4 LLM calls). The circuit breaker from Step 6b (15 LLM calls max) provides generous headroom — if a conversation hits 15 calls, it's not Tier 1 and should be escalated.

> [!abstract]- AI How: identifying the processing pattern
> This section emerged from a methodology gap — we'd been asking "what intelligence does each step need?" without first asking "what kind of process is this?" The processing pattern (loop vs workflow) shapes every decision that follows. A sequential workflow doesn't need a loop controller. A conversational loop does — and that's why DECIDE must be deterministic.
>
> The PM identifies the pattern by checking four characteristics (unpredictable input, tool use, multi-turn, dynamic routing). The specific agent architecture is an engineering decision — the PM specifies the characteristics and the pattern, not the implementation.
>
> **Methodology insight:** Step 7 should always start by identifying the processing pattern before assigning intelligence to individual steps. The pattern is a PM decision (driven by the characteristics of the problem from Steps 1-2), not an engineering decision.

---

#### Intelligence Assignment

**The intelligence spectrum:**

"AI" isn't one thing. The cognitive demand of each step varies enormously, and that directly affects cost, latency, and reliability. The PM specifies the demand level — engineering selects the model.

| Level | What it means | Example | Cost/reliability implication |
|-------|--------------|---------|------------------------------|
| **Low** | Extract & match — pulling structured information from unstructured text | Extracting an order number from "yeah it was like 12345 I think" | Fast, cheap models excel. High reliability. |
| **Moderate** | Classify & generate — understanding intent, writing contextual responses | Detecting a refund request, writing a natural confirmation message | Mid-range models. Good reliability for well-defined tasks. |
| **High** | Interpret & reason — handling ambiguity, applying judgement to edge cases | Deciding whether "opened but didn't use it" counts as "unused" under the returns policy | Requires reasoning-capable models. Higher cost, less predictable. |

This refines the spectrum from Step 2b:

**Deterministic → AI (Low) → AI (Moderate) → AI (High) → Human**

Each step to the right costs more, takes longer, and introduces more variability. The PM's job is to push each backbone step as far LEFT on this spectrum as the task allows.

**Intelligence assignment per backbone step:**

| Backbone step | What happens | Approach | Intelligence level | Why | LLM calls |
|---------------|-------------|----------|--------------------|-----|:---------:|
| **RECEIVE** | Message → categorised enquiry | AI | Low–Moderate | Natural language input — can't predict how customers phrase things. "Where's my stuff?" and "I haven't received order #12345" are the same query. Extraction is low; initial classification is moderate. | Combined with UNDERSTAND |
| **IDENTIFY** | → customer + order matched | Mixed | Low | Order numbers are structured and extractable, but "I ordered a garden table last Tuesday" needs AI to interpret. The actual customer/order lookup is a system query, not intelligence. | 0–1 |
| **UNDERSTAND** | → intent + emotion + complexity | AI | Moderate | The gap between what customers say and what they mean. "This is ridiculous" could be venting (continue) or escalation trigger (hand off). Policy interpretation starts here. | 1 (combined with RECEIVE) |
| **ASSESS** | → eligibility + reasoning | Deterministic (+ AI for edge cases) | High (when AI needed) | Tier 1 = clear rules. Is the item within the return window? Is the amount under £50? Deterministic checks are faster and more consistent than AI. AI only needed when the policy is genuinely ambiguous (rare for Tier 1) — and when it IS needed, it requires real reasoning. | 0–1 |
| **DECIDE** | → resolve / escalate / clarify | Deterministic | — | **Product decision, not cost optimisation.** This is the safety gate — the step that routes customers to resolution vs human vs "I need more info." Must be predictable and auditable. An AI "deciding" whether to escalate introduces the exact unpredictability we're trying to eliminate. | 0 |
| **ACT** | → resolution executed | Deterministic | — | Executes the decision: process refund, look up delivery status, create ticket. No judgement needed — the decision was already made in DECIDE. | 0 |
| **CONFIRM** | → customer informed | AI | Moderate | Natural, specific, empathetic response that references what just happened. "Your refund of £24.99 for the garden hose has been processed — you'll see it in 3-5 working days." Templates can't do this well without feeling robotic. | 1 |
| **LEARN** | → feedback captured | Deterministic (+ optional AI async) | Low (when AI used) | Structured logging: what query type, what decision, what outcome, how long. Optional async AI summary for manager review (US-07) — but this doesn't block the customer. | 0 (+1 async) |

> [!tip] Single model vs multi-model is a trade-off
> The intelligence levels create a question for engineering: do you use one model for everything (simpler architecture, easier to maintain, but overpaying for low-demand steps) or different models for different levels (cheaper per call, but more complex to build and monitor)? The PM specifies the demand — engineering recommends the approach. For Oakwood's scale (~2,000 conversations/month), a single mid-range model is likely simpler and the cost difference is negligible. At 100× that volume, the multi-model approach starts to pay for itself.

**Implementation note — backbone steps collapse in practice:**

The backbone steps are logical, not literal function calls. In practice, RECEIVE + UNDERSTAND + initial IDENTIFY happen in a single LLM call (the agent reads the message, extracts intent, detects emotion, and pulls out identifiers all at once). ASSESS is pure code for straightforward Tier 1. CONFIRM is a separate LLM call generating the response. So a typical straight-through conversation is: one LLM call to understand, code to check and route, one LLM call to respond.

**NFR sanity check:**

Checking the solution against the constraints from Step 6b, using the conversation flow patterns above:

| NFR | Target | Step 7 estimate | Status |
|-----|--------|----------------|:------:|
| Cost per conversation | < £0.50 (target < £0.20) | ~£0.003–0.02 depending on pattern (2–6 LLM calls × ~1K tokens each, mostly low-moderate demand) | ✅ Well within |
| Response latency | < 5s per message | ~1–3s per LLM call with streaming. Each turn in the loop has its own latency budget. | ✅ Fits |
| Conversation length | Max 15 turns | Straight-through: 2 turns. Clarification: 4. Multi-issue: 3–5. All well under ceiling. | ✅ Fits |
| Circuit breaker | 15 LLM calls max | Worst typical pattern: 6 calls (multi-issue). 15 provides headroom for unusual conversations before forcing escalation. | ✅ Fits |
| Fallback (LLM unavailable) | Route to email queue | Deterministic DECIDE step can detect LLM failure and route to queue without AI | ✅ Covered by design |

The cost range now reflects the variable nature of a conversational loop — straight-through conversations cost ~£0.003, while multi-issue or clarification-heavy conversations cost more. Even the most expensive pattern (~£0.02) is well under the £0.50 ceiling and dramatically below the ~£4–5 human cost per ticket.

Most LLM calls are low-to-moderate intelligence demand (extraction, classification, response generation). High-reasoning calls only occur for edge-case ASSESS — rare for Tier 1. Even if engineering uses a reasoning-capable model for those occasions, the cost impact is small because they're triggered infrequently.

> [!warning] Revisit after model selection
> These estimates assume most calls use a small, fast model (low-moderate demand). If the ASSESS step triggers high-reasoning calls more often than expected (i.e., Tier 1 queries are more ambiguous than we think), re-run this check. The architecture (few LLM calls, deterministic routing) gives significant headroom — but it's not unlimited.

**Key design decisions:**

1. **DECIDE is deliberately deterministic.** This is the most important decision in Step 7 — for two reasons. First, it's the safety gate: if a customer with a £200 complaint gets escalated, the CS manager needs to know it happened because of a clear rule (amount > £50), not because the LLM "felt" it was complex. Second, DECIDE is the **loop controller** — it determines whether the conversation continues (clarify), resolves (act), or exits to a human (escalate). A non-deterministic loop controller means an unpredictable system. DECIDE can be fully unit-tested, which none of the AI steps can be.

2. **ASSESS is mostly deterministic for Tier 1.** The scope decision from Step 3 (Tier 1 only) makes this possible. Tier 1 queries have clear rules — return window, amount threshold, product category. If Oakwood later expands to Tier 2, ASSESS would need AI because the rules get ambiguous. But for now, deterministic = more reliable AND cheaper.

3. **LEARN is async.** The AI-generated summary for manager review (connecting to US-07) doesn't block the customer conversation. It runs after the conversation ends. This keeps latency low and means a failure in the LEARN step doesn't affect the customer experience.

4. **The architecture minimises AI blast radius.** By making DECIDE, ACT, and LEARN deterministic, AI failures are contained to understanding the request (RECEIVE/UNDERSTAND) and writing the response (CONFIRM). These are visible and recoverable — a confused response gets caught by the customer or by eval. A wrong routing decision or a silently failed refund would be much harder to detect.

> [!abstract]- AI How: working through Step 7
> Used sequential thinking to walk through each backbone step and ask "does AI earn its place here?" Two key methodology insights emerged:
>
> **1. NFRs shape solution design.** The constraints from Step 6b (especially cost per conversation and latency) directly shaped the decisions. Without those constraints, you might default to "use AI everywhere" — the NFRs force you to justify each LLM call. The sanity check at the end creates a feedback loop: if the total came out too expensive, you'd push more steps to deterministic or pick a cheaper model. This is why Step 6b (NFRs) comes before Step 7 (solution approach) in the methodology.
>
> **2. "AI" isn't binary — it's a spectrum.** The original code → AI → human spectrum from Step 2b was too coarse. During Step 7, it became clear that different backbone steps need fundamentally different levels of AI capability — extraction vs classification vs reasoning. This matters because it directly affects the PM's cost estimates, reliability expectations, and the conversation with engineering about model selection. The PM doesn't pick models, but they DO specify cognitive demand. The refined spectrum: Deterministic → AI (Low) → AI (Moderate) → AI (High) → Human. Each step right costs more and introduces more variability — the PM's job is to push each backbone step as far left as the task allows.



### Step 8 — Agent Tools & Knowledge

> [!tip] What this step does
> If you were onboarding a new CS agent on their first day, you'd give them system access, reference materials, and explain what they can and can't do in each system. This step does the same for the AI agent: what tools does it need, what knowledge does it need access to, and what can each tool do?
>
> The PM specifies the capabilities — engineering designs the implementation (APIs, data formats, integrations).

#### Tools

The agent needs to perform actions during conversations — looking things up, processing requests, creating tickets. Each tool is a specific capability the agent can invoke.

| Tool | What it does | Inputs | Returns | When used |
|------|-------------|--------|---------|-----------|
| **Order lookup** | Find a customer's order and its current status | Order number OR customer name + approximate date | Order details: items, total, order date, delivery status, tracking info | IDENTIFY / ASSESS — most conversations start here |
| **Policy lookup** | Check the refund/returns policy for a specific product category | Product category | Return window, conditions, exceptions, any special rules | ASSESS — determining eligibility |
| **Process refund** | Execute a refund for an eligible order | Order ID, amount, reason code | Confirmation (success/failure), reference number, expected timeline | ACT — after DECIDE routes to resolve |
| **Create escalation ticket** | Hand off to a human agent with full context | Conversation summary, tier classification, escalation reason, customer details, order details | Ticket ID, estimated response time | ACT — after DECIDE routes to escalate |
| **Customer history** | Look up previous interactions for this customer | Customer ID or email | Previous tickets, outcomes, any open issues | UNDERSTAND — detecting repeat contacts (complexity modifier) |

> [!warning] Tool permissions are product decisions
> Each tool has an implicit permission level. The agent can LOOK UP anything (read-only). But it can only PROCESS refunds under £50 (write, with a hard limit). And it can CREATE escalation tickets but never DELETE or MODIFY them. These aren't engineering constraints — they're the PM's risk appetite from Step 1c, encoded as tool boundaries.

#### Knowledge & Data

The agent also needs reference material — information it draws on but doesn't modify.

| Knowledge source | What it contains | Format required | Current state | Dependency? |
|-----------------|-----------------|----------------|---------------|:-----------:|
| **Refund & returns policies** | Rules per product category: window, conditions, exceptions | Structured (JSON/YAML) — must be machine-queryable, not free text | PDF on SharePoint | ⚠️ **Prerequisite** — must be converted before agent can handle refund queries (38% of Tier 1) |
| **Product catalogue** | Categories, prices, descriptions, return window per category | Database (already structured) | Good — API available | No |
| **FAQ responses** | Standard answers to common policy questions ("what's your returns policy?", "how long do refunds take?") | Structured Q&A pairs | Doesn't exist yet — needs creating from common queries | ⚠️ Needed for policy question handling (16% of Tier 1) |
| **Brand voice guide** | Tone, language, dos and don'ts for customer communication | Part of system prompt | Doesn't exist for AI — human agents learn informally | Should create |
| **Escalation criteria** | The routing rules from Step 7 | Part of system prompt / code | Defined in this PRD | No — already specified |

> [!abstract]- AI How: specifying tools and knowledge
> The question "what tools does the agent need?" is essentially "what systems does a human CS agent use today?" from Step 2a, translated into capabilities. The five systems identified in the as-is process (Zendesk, OMS, SharePoint, payment system, Slack) map directly to the five tools above. The difference: the human agent copy-pastes between systems. The AI agent calls tools directly.
>
> The knowledge sources surface prerequisites — things that must exist BEFORE the agent can function. The refund policy PDF conversion was noted in Step 2c but easy to overlook. Listing it here with a dependency flag makes it visible as a blocker.

---

### Step 9 — Boundaries & Guardrails

> [!tip] Hard vs soft guardrails
> Hard guardrails are **code-enforced** — the agent literally cannot do the thing, regardless of what it's prompted to do. These protect against high-consequence failures.
>
> Soft guardrails are **prompt-enforced** — the agent is instructed not to do the thing, but the boundary could fail under adversarial input or prompt drift. These handle lower-consequence, higher-nuance situations.
>
> Every guardrail should trace back to a failure mode from Step 4b or a complexity modifier from Step 2b.

#### Hard Guardrails (code-enforced)

| Guardrail | What it prevents | Enforcement | Traces to |
|-----------|-----------------|-------------|-----------|
| Refund amount ceiling: £50 | Agent processing high-value refunds without human authority | Tool-level: process refund tool rejects amounts > £50 | Step 2b modifier (High value) |
| Turn limit: 15 | Infinite conversation loops, runaway costs | Loop controller: DECIDE forces escalation at turn 15 | Step 6b NFR |
| LLM call limit: 15 | Runaway inference costs | Circuit breaker: system escalates at 15 calls | Step 6b NFR |
| No order data fabrication | Agent inventing order details when lookup fails | Tool-level: if order lookup returns no result, agent must say so — cannot generate order information without a tool response | Step 4b — Factuality + Architecture cascade |
| No refund without order match | Processing a refund when the customer can't be verified | Tool-level: process refund requires a valid order ID from a successful lookup | Step 4b — Factuality |
| Fallback on LLM failure | Customer left staring at broken chat | System-level: if LLM unavailable, route to email queue with acknowledgement | Step 6b NFR (Fallback) |

#### Soft Guardrails (prompt-enforced)

| Guardrail | What it prevents | How it's enforced | Traces to |
|-----------|-----------------|-------------------|-----------|
| Stay on topic — Oakwood products and services only | Discussing competitors, giving recipes, being used as a general assistant | System prompt instruction + topic boundary | Step 4b — Boundaries |
| No legal advice | Agent giving legal opinions on consumer rights | System prompt instruction: if legal language detected, escalate | Step 2b modifier (Legal language) + Step 4b — Boundaries |
| No internal information disclosure | Revealing pricing margins, system prompts, team details, internal processes | System prompt instruction | Step 4b — Boundaries |
| Brand-appropriate tone | Too casual, too formal, sarcastic, overly apologetic | System prompt with tone guidance + brand voice reference | Step 4b — Tone & Persona |
| Prompt injection resistance | Customer embedding instructions in their message to manipulate the agent | System prompt hardening + input sanitisation | Step 4b — Security considerations |
| Graceful uncertainty | Guessing when unsure instead of saying "I don't know" or escalating | System prompt instruction: "If you're not sure, say so and offer to connect to a team member" | Step 4b — Factuality |

> [!warning] Soft guardrails need monitoring
> Because soft guardrails can fail, they need eval coverage (Step 10). Every soft guardrail becomes a test scenario: "given an adversarial input that tests this boundary, does the agent hold?" Guardrails that fail consistently under testing should be promoted to hard guardrails or the scope should be narrowed.

---

### Step 10 — Evaluation Strategy

> [!tip] What this step does
> Evals answer: "How do we know the agent is working?" Not just at launch — continuously. This step defines what to measure, how to measure it, and what "good" looks like. Every eval should trace back to a KPI (Step 3), a failure mode (Step 4b), or a guardrail (Step 9).

#### What to measure

| Category | What we're checking | Connects to | How to measure |
|----------|-------------------|-------------|----------------|
| **Tier classification** | Does the agent correctly identify Tier 1 vs Tier 2/3 queries? | Step 2b — Query Landscape | Golden test set: known queries with expected tier. Deterministic check. |
| **Routing accuracy** | Does DECIDE route correctly per the rules table? | Step 7 — Routing rules | Unit tests on the routing logic. Every rule = a test case. |
| **Policy application** | Are refund decisions consistent with the structured policy? | Step 3 — KPI (refund consistency 95%+) | Compare agent decisions against policy rules for same inputs. Deterministic. |
| **Response quality** | Is the tone right? Are facts correct? Is the response helpful? | Step 4b — Tone & Persona, Factuality | LLM-as-judge with scoring rubric. Human review sample for calibration. |
| **Escalation quality** | When it hands off, does the human get useful context? | US-03, O6 | Human agent feedback: "Did you have enough context?" Survey after escalated tickets. |
| **Guardrail compliance** | Does the agent stay within boundaries under normal and adversarial input? | Step 9 — all guardrails | Adversarial test scenarios per guardrail. Red-team testing. |
| **Auto-resolution rate** | What percentage of Tier 1 queries are resolved without human involvement? | Step 3 — KPI (60% target) | Automated: count conversations that resolve without escalation. |
| **Customer satisfaction** | Are customers happy with the interaction? | Step 3 — KPI (CSAT floor 3.6) | Post-conversation survey. Compare AI-handled vs human-handled CSAT. |
| **Drift detection** | Is the agent getting worse over time? | Step 4b — Drift | Weekly sample review. Compare current week's scores against baseline. Alert on degradation. |

#### Evaluation approach

**Before launch:**
- Golden test set — 50-100 known scenarios with expected outcomes (covers each query type, each modifier, each routing rule)
- Adversarial test set — attempts to break each guardrail
- Human baseline — run the same test scenarios with human agents to establish comparison

**After launch:**
- Automated monitoring — routing accuracy, resolution rate, cost per conversation (continuous)
- Sampled human review — weekly review of 20-30 conversations by CS manager (quality check)
- CSAT tracking — compare AI-handled vs human-handled satisfaction scores (weekly)
- Drift alerts — flag when any metric drops below baseline by more than 10% (automated)

> [!abstract]- AI How: connecting evals to earlier steps
> The evaluation strategy isn't designed from scratch — it's assembled from decisions already made. Each KPI from Step 3 becomes a metric. Each failure mode from Step 4b becomes a test scenario. Each guardrail from Step 9 becomes an adversarial test. The PM's job is connecting these threads, not inventing new eval categories.
>
> **Methodology insight:** If you can't write an eval for something, either the requirement isn't specific enough (go back and sharpen it) or it doesn't matter enough to test (consider dropping it). Evals are a quality check on your own specification.

---

## Progress Tracker

| Step | Name | Status | Date |
|------|------|--------|------|
| 1 | Problem Statement | draft | 2026-03-05 |
| 1b | Market Research & Hypothesis | draft | 2026-03-05 |
| 1c | Business Case | draft | 2026-03-05 |
| 2a | As-Is Process | draft | 2026-03-05 |
| 2b | Query Landscape | draft | 2026-03-05 |
| 2c | Data Landscape | draft | 2026-03-05 |
| 3 | Outcomes & Opportunities | draft | 2026-03-05 |
| 4 | Problem & Market Assumptions | draft | 2026-03-05 |
| 4b | Failure Mode Analysis | draft | 2026-03-05 |
| 5 | Process Backbone | draft | 2026-03-05 |
| 6 | User Stories | draft | 2026-03-05 |
| 6b | Non-Functional Requirements | draft | 2026-03-08 |
| 7 | Solution Approach | draft | 2026-03-09 |
| 8 | Agent Tools & Knowledge | draft | 2026-03-09 |
| 9 | Boundaries & Guardrails | draft | 2026-03-09 |
| 10 | Evaluation Strategy | draft | 2026-03-09 |
