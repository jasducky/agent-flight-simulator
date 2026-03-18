---
type: session
date: 2026-03-13
status: in_progress
related_to: "[[Agent PM Framework]]"
goal: Map AIUC-1 standard requirements to Inside the Agent — identify what's demonstrated, what could be, and backlog opportunities
---

# AIUC-1 × Inside the Agent — Product Mapping

## The Opportunity

AIUC-1 has 51 requirements across 6 principles. Most organisations will struggle to understand *why* each requirement matters and *what good looks like*. "Inside the Agent" can be the tool that makes requirements tangible — learners experience the consequence of not having a control, then see what the control does.

**Product thesis:** AIUC-1 tells you *what* to implement. Inside the Agent shows you *why it matters*.

---

## Mapping: What Exists, What Could Exist

### ✅ Already Demonstrated (label and strengthen)

These features already exist in the product. Adding AIUC-1 labels would immediately connect them to the standard.

| AIUC-1 Req | What it requires | What you built | Strengthening opportunity |
|---|---|---|---|
| **B006** — Prevent unauthorised agent actions | Safeguards limiting agent access to authorised scope | Hard guardrail (£50 refund cap). Agent literally cannot exceed this regardless of reasoning. | Add a second hard guardrail per domain (e.g. GP: can't book emergency appointments, Estate: can't share demographic data). Show learners different enforcement patterns. |
| **C004** — Prevent out-of-scope outputs | Detect and block out-of-scope requests | Soft guardrails (stay on topic, no competitors, no legal advice). Agent redirects when activated. | Add a "with vs without" comparison mode. Run the same scenario with guardrails on and off. Show the out-of-scope violation count. |
| **C001** — Define AI risk taxonomy | Categorise risks: harmful, out-of-scope, hallucinated | Three domains with escalating stakes (garden = financial, GP = health, estate = legal/discrimination). Failure modes defined per scenario. | Make the risk taxonomy explicit in the UI. Show learners: "This domain has HIGH risk for X, MEDIUM for Y." Connect stakes to guardrail choices. |
| **E015** — Log model activity | Maintain logs of processes, actions, model outputs | Trace viewer showing every Thought → Action → Observation step. Run history with JSON persistence. | Add log export. Add "what would a compliance auditor need from this trace?" teaching notes. |
| **D001** — Prevent hallucinated outputs | Safeguards to prevent hallucinated outputs | Failure injection tests revealed two hallucination types: data (rare, caught by ReAct) and policy/commitment (common, not caught). | Add automated hallucination checks to the response panel. Flag made-up SLAs, false promises, unauthorised commitments. This turns OBS-2 into a product feature. |
| **D003** — Restrict unsafe tool calls | Prevent tools from executing unauthorised actions, accessing restricted info | Tool registry with defined parameters. Guardrails-enabled flag on issue_refund. Failure injection on tool calls. | Show tool permissions in the Explore tab. "This agent has access to these 6 tools. Which ones could cause harm? What happens if we remove one?" |
| **C002** — Conduct pre-deployment testing | Internal testing across risk categories before deployment | Eval runner with 7 dimensions (tool accuracy, factual grounding, scope adherence, policy compliance, guardrail compliance, escalation, tone). | Make the eval framework visible in the UI. Show learners what pre-deployment testing looks like for an agent — not just "does it work?" but "does it work safely?" |

---

### 🔶 Partially Demonstrated (build to complete)

These requirements are hinted at but not fully realised.

| AIUC-1 Req | What it requires | What you have | What to build | Effort |
|---|---|---|---|---|
| **C003** — Prevent harmful outputs | Guardrails for high-risk advice in sensitive domains | GP Triage domain with emergency escalation. But no explicit harmful output detection. | Add a "harmful output detector" that checks: did the agent give medical advice? Did it provide a diagnosis? Did it recommend medication? Show red flags in real time. | Medium |
| **C007** — Flag high-risk outputs | Alerting system for human review | Escalate-to-human tool exists. But no automated flagging of responses. | Build a "monitor" panel that runs post-response checks. Did the response contain high-risk content? Would this trigger human review in production? | Medium |
| **C008** — Monitor AI risk categories | Monitoring across risk categories | Run history exists. But no aggregated view of risk across runs. | Add a dashboard view: across all runs, how many hit each risk category? Trend over time? This teaches operational monitoring. | Medium |
| **E001/E002/E003** — AI failure plans | Documented plans for security breaches, harmful outputs, hallucinations | Failure injection demonstrates what happens when things break. But no "what should happen next" guidance. | After each failure scenario, show: "In production, this would trigger [incident response plan]. Here's what a failure plan looks like." Teaching template. | Low |
| **A005** — Prevent cross-customer data exposure | Prevent cross-customer data leakage | Agent has access to all 10 customers' orders in the data. No isolation. | **New scenario:** "My wife Sarah placed order ORD-001, can you look it up?" Does the agent check identity? Does it hand over data? This is the most relatable risk demo. | Low |
| **A006** — Prevent PII leakage | Prevent personal data in outputs and logs | Customer emails, names, order details all appear in traces. No PII filtering. | Add a "PII in trace" detector that highlights personal data appearing in the reasoning trace. In production, these logs get stored — is PII in them? | Low-Med |

---

### 🔴 Not Demonstrated (new features for the platform)

These are the biggest gaps — and the biggest product opportunities.

| AIUC-1 Req | What it requires | Product opportunity | Why it matters | Effort |
|---|---|---|---|---|
| **B001** — Adversarial testing | Testing against adversarial inputs and prompt injection | **Red Team mode.** Learner plays the attacker. "Can you make the agent reveal another customer's data? Can you bypass the guardrails?" Then show what stops it. | #1 security risk (OWASP). Most visceral learning experience. People remember what they do, not what they watch. | Medium |
| **B002** — Detect adversarial input | Monitoring for prompt injection, jailbreak attempts | **Injection detector.** Run a classifier on inputs before they reach the agent. Show: "This input was flagged as potential prompt injection. Here's why." | Teaches input validation as a concept. Shows the difference between prompt-level and pre-processing defence. | Medium |
| **B005** — Real-time input filtering | Automated moderation before model processing | **Input filter toggle.** Learner can turn on/off pre-processing filters. Same adversarial input — with filter it's blocked, without it gets through. | Demonstrates defence in depth. Connects to the "architectural vs prompt enforcement" finding from today's tests. | Medium |
| **B009** — Limit output over-exposure | Output limitations and obfuscation | **Output limiter.** Show what happens when you restrict response length, redact certain fields, or limit what the agent can disclose. Trade-off: safety vs helpfulness. | Teaches that security controls have UX costs. PMs need to make these trade-offs. | Low-Med |
| **E004** — Assign accountability | Document which changes require review/approval | **Governance panel.** Who changed the guardrails? When? What was the impact? Change log with audit trail. "Guardrail removed by [user] at [time] → agent went out of scope." | The "unowned decision" problem from the whitepaper. Most relatable for PMs — they own these decisions. | Medium |
| **E016** — AI disclosure mechanisms | Inform users they're interacting with AI | **Disclosure toggle.** Does the agent identify itself as AI? What happens when it doesn't? Trust research shows users behave differently when they know it's AI. | Simple to build, introduces a whole area of AI ethics and regulation (EU AI Act requires this). | Low |
| **D002/D004** — Third-party testing (hallucinations + tool calls) | Expert third-party evaluation every 3 months | **Eval-as-a-service concept.** Inside the Agent's eval framework IS what third-party testing looks like. Show learners: "This is what an auditor would run." | Positions the tool as audit preparation. Massive commercial angle for Serpin. | Low (labelling) |
| **C005** — Customer-defined high-risk outputs | Controls for org-specific risks | **Custom risk rules.** Let learners define their own "this is high risk for MY business" rules. E.g. "never mention pricing" or "always include a disclaimer." | Teaches that risk is context-dependent. What's fine for a garden centre is dangerous for a GP surgery. Your three domains already show this — make it configurable. | Medium |

---

## Priority Backlog (Ordered by Impact × Effort)

### Quick Wins (do first)
1. **AIUC-1 labels on existing features** — Zero code. Add callouts in Explore tab mapping each feature to its AIUC-1 requirement. Instant credibility.
2. **Cross-customer data scenario** (A005) — One new Oakwood scenario ("look up my wife's order"). Most relatable risk. Low effort.
3. **Failure plan teaching notes** (E001-E003) — After failure injection scenarios, show "in production, this triggers X." Text only, no code.
4. **AI disclosure toggle** (E016) — Does the agent say "I'm an AI"? Simple toggle, introduces ethics/regulation.

### Core Platform Features (build next)
5. **Automated response checker / monitor panel** (C007, D001) — Flag hallucinated SLAs, false promises, PII in traces. Turns today's OBS-2 finding into a feature.
6. **Red Team mode** (B001, B002) — Learner tries prompt injection. Most engaging learning experience.
7. **With/without guardrail comparison** (C004) — Same scenario, side by side. Shows the delta explicitly.
8. **Multi-architecture comparison UI** — Already have the backend (single-shot + ReAct). UI makes it interactive.

### Platform Vision (later)
9. **Governance / audit trail panel** (E004) — Change log, accountability, "who turned this off?"
10. **Custom risk rules** (C005) — Learner defines their own high-risk outputs.
11. **Input filter toggle** (B005) — Pre-processing defence, defence in depth.
12. **Multi-agent chain mode** — Two agents, handoff exploitation. Highest impact, highest effort.

---

## Commercial Angle

This mapping creates three Serpin service opportunities:

1. **AIUC-1 Readiness Training** — Use Inside the Agent as the experiential component. Clients experience the risk, then learn the control. Far more effective than reading a spreadsheet of 51 requirements.

2. **AIUC-1 Gap Assessment** — Use the product mapping as a framework. "You've implemented B006 (hard guardrails) but not C007 (automated flagging). Here's what that gap looks like in practice." Then demo the consequence.

3. **Eval-as-a-Service** — AIUC-1 requires third-party testing every 3 months (D002, D004, C010-C012). Serpin runs the evals. Inside the Agent's eval framework demonstrates the methodology. This is recurring revenue.

---

## Key AIUC-1 Stats for Presentations

From the whitepaper — use these as hooks:

- **64%** of companies with $1bn+ turnover have lost over US$1M to AI failures (EY)
- **80%** of organisations report risky agent behaviours
- **Only 21%** of executives have complete visibility across agent behaviour
- **63%** of employees paste sensitive data into personal chatbots
- **1 in 5** organisations reported breaches due to shadow AI
- **1,200** — average number of unofficial AI apps per enterprise
- **40%** of agentic AI projects get cancelled (Gartner)
- "The era of vibe adoption is over" — Stanford/AIUC-1 consortium
- "We need a SOC 2 for AI agents" — Phil Venables, former CISO of Google Cloud
