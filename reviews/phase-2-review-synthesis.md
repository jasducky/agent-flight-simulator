# Phase 1-2 Review Synthesis

> [!abstract] Three-agent review of PRD Steps 1–6b
> Run 9 Mar 2026. Three independent agents reviewed the Oakwood CS Agent PRD from different perspectives. This file synthesises the findings into actionable items.

---

## Review Agents

| Agent | Persona | Confidence | Full review |
|-------|---------|:----------:|-------------|
| **Flow Reviewer** | Senior PM reading cold | Strong (minor issues) | `phase-2-flow-review.md` |
| **Agent Perspective** | The AI being built from this spec | 70% buildable | `phase-2-agent-perspective-review.md` |
| **Stress Tester** | Sceptical VP + adversarial customer | 6/10 | `phase-2-stress-test.md` |

---

## What's Strong (consistent across all three)

- Failure mode taxonomy — especially the architecture → factuality cascade warning
- The code → AI → human spectrum justification in Step 2b
- NFRs framed as product decisions with rationale, not engineering specs
- Risk appetite is explicit: "wrong escalation acceptable, wrong refund not"
- Callout boxes add genuine value (not just decoration)
- Tier classification with AI suitability criteria is rigorous

---

## Phase 2 Fixes (should address before going deeper into Phase 3)

### Must-Fix

| # | Issue | Flagged by | Where to fix | Effort |
|---|-------|-----------|-------------|--------|
| 1 | **Identity verification rules undefined** — what does the agent do when order number is wrong/missing? Currently "trust-based" with no AI-specific rules. Also a GDPR risk (customer could access someone else's order). | All three | Step 2a (as-is) + Step 4 (assumptions) + Step 4b (failure modes) | Medium |
| 2 | **65% Tier 1 figure is unvalidated** — is it based on Zendesk data or estimation? A sceptical stakeholder would challenge this immediately. | Stress Tester | Step 2b — add data source or explicitly flag as assumption in Step 4 | Small |
| 3 | **Refund policy as prerequisite** — converting from PDF to structured format is noted but buried. This blocks 38% of Tier 1 value (refunds + policy questions). Should be surfaced as a hard dependency. | Agent, Stress Tester | Step 2c (flag as dependency) + Step 4 (add as assumption) | Small |
| 4 | **No rollback plan** — what happens if the agent goes badly? No mention of phased rollout, kill switch, or revert-to-human process. | Stress Tester | Step 4 (assumptions) or Step 1c (business case) | Medium |

### Should-Fix

| # | Issue | Flagged by | Where to fix | Effort |
|---|-------|-----------|-------------|--------|
| 5 | **Cross-reference errors** — US-06 maps to O7 (doesn't exist), US-04 maps to O6 (should be O5) | Flow Reviewer | Step 6 | Tiny |
| 6 | **Step 2b says "five AI suitability criteria" but only lists four** | Flow Reviewer | Step 2b | Tiny |
| 7 | **Steps 2c and 2b appear out of document order** (2a → 2c → 2b) with no explanation | Flow Reviewer | Reorder or add a note explaining why | Tiny |
| 8 | **CSAT composition blind spot** — AI takes easy wins, humans left with only hard cases. Overall CSAT stays flat but human agent workload quality degrades. Add as guard metric or assumption. | Stress Tester | Step 3 (KPIs) or Step 4 (assumptions) | Small |
| 9 | **Emotional escalation threshold is vague** — does the agent attempt resolution first when customer is angry, or escalate immediately? This is a business rule, not a solution design question. | Agent | Step 2b (complexity modifiers) — clarify the expected behaviour | Small |
| 10 | **Cost comparison is incomplete** — AI cost should include integration, monitoring, eval infrastructure, ongoing PM time. Not just inference. | Stress Tester | Step 1c (business case) — add "total cost of ownership" note | Small |

### Phase 3/4 Work (not Phase 2 gaps — will be addressed in upcoming steps)

| # | Issue | Flagged by | Where it belongs |
|---|-------|-----------|-----------------|
| 11 | Tool specifications — agent knows what data exists but not what it can call | Agent | Step 9 (actor assignment) |
| 12 | Escalation handoff format — how context gets passed to humans | Agent | Step 9 or Step 10 |
| 13 | Topic-change handling — customers don't follow linear flows | Agent | Step 10 (agent stories) |
| 14 | "Try harder vs escalate" criteria at DECIDE step | Agent | Step 9 (actor assignment) |
| 15 | Repeat contact detection — requires Zendesk history lookup | Agent | Step 9 (tool design) |

---

## Adversarial Scenarios Worth Testing (from Stress Tester)

These should feed into Step 11 (Guardrails & Evals) when we get there:

1. **Polite boundary-pusher** — technically within rules but persistently pushing for exceptions
2. **Wrong order number** — provides a valid order number that isn't theirs
3. **Policy arguer** — asks "what's your refund policy?" then disputes each point
4. **Slow escalator** — starts with "where's my order?" and gradually builds to a complaint
5. **Social media threat** — "I'll post about this on Twitter"

---

## Stress Tester's Top 3 Failure Predictions

If this project fails, the most likely reasons:

1. **Fuzzy Tier 1/2 boundary** collapses the auto-resolution rate — too many queries that look Tier 1 turn out to need human judgement
2. **Identity verification gap** causes a data protection incident before the team fixes it
3. **Inability to build/maintain eval infrastructure** leads to undetected drift — the agent degrades and nobody notices until CSAT craters

---

## Methodology Observation

> [!tip] Multi-agent review as a PRD quality gate
> Running three agents with different personas (cold reader, the AI itself, sceptical stakeholder) caught issues that a single review pass would miss. The Agent Perspective review was the most novel — asking "could I be built from this?" surfaced gaps that neither the PM lens nor the business lens would catch (tool specs, identity verification rules, topic-change handling).
>
> **Pattern:** After completing a PRD phase, run 2-3 review agents with distinct personas before moving to the next phase. The cost is ~5 minutes of background compute. The value is catching gaps while they're cheap to fix.
>
> Worth adding to the methodology as an optional quality gate between phases.

---

*Individual reviews in this folder contain full section-by-section analysis.*
