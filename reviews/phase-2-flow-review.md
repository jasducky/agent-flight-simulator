# Phase 1-2 Flow Review — Cold Read

**Reviewer:** Senior PM (cold read, no prior context)
**Date:** 2026-03-09
**Scope:** Phase 1 (Steps 1–1c) and Phase 2 (Steps 2a–6b) only

---

## Summary Verdict

This is an unusually well-structured PRD. The logic flows cleanly from problem through to user stories and NFRs, and the callout boxes genuinely earn their space — they anticipate exactly the questions a reader would have. The two main issues are a broken cross-reference in user stories (O6 and O7 don't exist), and the step numbering (2a, 2c, 2b) that silently reorders the document without explanation.

---

## Section-by-Section Findings

### Step 1 — Problem Statement

**What works well:**
- Concise and quantified. Every claim has a number (2,000/month, 60%, 4+ hours, 3.6 CSAT). No hand-waving.
- Sets up the "why now" clearly — volume growing 40%, headcount flat.

**Issues:** None. This does exactly what a problem statement should do.

---

### Step 1b — Market Research & Hypothesis

**What works well:**
- The "rule-based chatbot was tried and abandoned" line is excellent — it pre-empts the obvious objection ("why not just a chatbot?") and sets up the AI justification in Step 2b.
- Hypothesis is falsifiable: "<30s for 60% of enquiries" gives a clear bar.

**Issues:** None.

---

### Step 1c — Business Case

**What works well:**
- The tip callout ("Estimation, not actuals") is one of the best in the document. It sets expectations perfectly and tells the reader when to come back with real numbers.
- Risk appetite framing is sharp: "Saying 'let me get a human' too often is acceptable; a wrong refund decision is not." This is the kind of sentence that aligns an entire team.

**Issues:**
- The "Revisit" line references "Steps 7-8" but the reader hasn't seen the step index yet. Minor, but on first read I didn't know what Steps 7-8 were.

---

### Step 2a — As-Is Process

**What works well:**
- The single-paragraph process flow is surprisingly effective. It reads like watching someone do the job — I can feel the copy-pasting and the waiting.
- "Key friction" section correctly identifies the gap (steps 3-6 are waiting + mechanical work) without prescribing a solution.

**Issues:**
- The process flow mentions "steps 3-6" — these are steps within the flow paragraph, not document steps, but there's no numbering in the paragraph itself. A reader could momentarily confuse these with the document's Step 3-6.

---

### Step 2c — Data Landscape

**What works well:**
- The table format is right for this content — scannable, comparative.
- "Data considerations for an AI agent" section bridges nicely from "what data exists" to "what matters for our specific use case."
- Calling out the PDF-to-structured-format conversion as a "prerequisite, not optional" is good PM discipline.

**Issues:**
- **This section appears before Step 2b in the document, but is numbered 2c.** On a cold read, I noticed the jump from 2a to 2c and checked whether I'd missed something. The content itself doesn't depend on Step 2b, so the order works logically — but the numbering creates a moment of confusion. Either renumber to match the actual order (2a → 2b → 2c) or add a brief note explaining why they're presented out of sequence.

---

### Step 2b — Query Landscape

**What works well:**
- The "Why AI and not just code?" callout is outstanding. The code → AI → human spectrum is the clearest articulation I've seen of when AI adds value versus when you're over-engineering. This could be extracted as standalone content.
- AI suitability criteria are well-chosen and consistently applied across the query table.
- Complexity modifiers table is a genuinely useful innovation — it captures the reality that conversations shift mid-stream, which most classification frameworks ignore.
- The note about emotional tone ("classify by what they're asking about, not how they're feeling") is precise and prevents a common mistake.

**Issues:**
- The suitability criteria list has four items but the table header references five columns of criteria (Clear logic, Verifiable, Consequence if wrong, Single issue). These match the four criteria, so it's just the introductory line that says "five AI suitability criteria" when there are four. **This is a factual error that undermines confidence in the framework.**

---

### Step 3 — Outcomes & Opportunities (OST)

**What works well:**
- The Tier 1/2/3 callout box is well-placed — defines terms before using them, without breaking flow.
- Scope decision is well-argued: it traces back to the suitability criteria from Step 2b and sets clear expansion criteria.
- The CSAT guard metric warning is excellent. Distinguishing guard metrics from stretch targets is a concept most PRDs get wrong.
- KPI table is clean and actionable, with current vs target and metric type.

**Issues:**
- The opportunities table has IDs O1–O6, but user stories later reference O7. **O7 does not exist in this table.** US-06 maps to "O7" — this is a broken cross-reference.
- O6 says "Get humans involved faster on complex cases, with full context already loaded." But US-04 maps to O6, and US-04 is about a customer wanting to understand why their refund was declined. These don't match — US-04 is about explanation transparency, O6 is about handoff quality. **This is a misaligned cross-reference.**

---

### Step 4 — Problem & Market Assumptions

**What works well:**
- Short and focused. Each assumption has a clear risk level.
- F2 ("Agent can reliably distinguish simple from complex cases") being flagged as **High** risk is the right call — this is the crux of the entire system.

**Issues:**
- The assumption IDs use a D/F/V prefix scheme that isn't explained anywhere. I can guess (D = Demand, F = Feasibility, V = Viability) but this is never stated. A one-line note or legend would help.

---

### Step 4b — Failure Mode Analysis

**What works well:**
- The tip callout on "why this is a PM step" is the second-best callout in the document (after the code → AI → human spectrum). The three shifts (probabilistic, invisible, change over time) are well-articulated.
- The five failure categories are well-consolidated and the "What the customer sees" column keeps it grounded in outcomes, not abstractions.
- The cascade warning (architecture failures masquerading as factuality problems) is a genuine insight that would prevent real debugging mistakes.
- The "words vs actions" distinction for boundaries is precise and actionable.
- Amplified failures (Bucket 3) is a strong concept — it bridges the "known human failures" to "what happens at AI scale."

**Issues:**
- The section references "Hamel Husain's failure categories (AI Evals course), consolidated with industry research (Galileo, OWASP, Microsoft)" — this is useful context for Julia's internal thinking but may confuse an external reader who doesn't know these sources. If this PRD is also a teaching document, that's fine. If it's meant to stand alone, consider a lighter attribution.
- Security considerations at the end feel slightly orphaned — they're labelled "non-functional requirements" but they're inside the failure mode analysis section, and there's a separate NFR section at Step 6b. The reader might wonder why these aren't in 6b.

---

### Step 5 — Process Backbone

**What works well:**
- "Actor-agnostic" is clearly stated upfront — prevents premature solution thinking.
- The eight steps (RECEIVE → IDENTIFY → UNDERSTAND → ASSESS → DECIDE → ACT → CONFIRM → LEARN) are intuitive and complete.

**Issues:**
- This is a single line of text with arrows. For a step that user stories map to and that Step 7 will assign actors to, it deserves more structure — even a simple numbered list or table with one-line descriptions. Currently, if I want to check whether a user story maps to a backbone step, I have to parse an inline arrow chain. The user stories don't actually reference backbone steps anyway (see Step 6 below), but if they're meant to, this format makes cross-referencing hard.

---

### Step 6 — User Stories

**What works well:**
- Stories are well-written — they follow proper "As a... I want... so that..." format and stay outcome-focused.
- The split between customer and internal stories is clean.

**Issues:**
- **US-06 maps to O7, which doesn't exist.** The opportunities table stops at O6. This is a broken cross-reference.
- **US-04 maps to O6, but O6 is about handoff quality and US-04 is about refund decline explanations.** US-04 ("if my refund is declined I want to understand the specific reason why") aligns more closely with O5 ("every 'no' comes with a clear, policy-backed explanation"). This looks like a mapping error.
- **US-03 maps to O4, but the fit is loose.** O4 is about freeing CS team for complex cases. US-03 is about customers not repeating themselves on escalation. US-03 maps more naturally to O6 (handoff with full context).
- **No user stories map to the backbone steps.** The "Maps to" column references opportunities only. If the backbone (Step 5) is meant to be cross-referenced here, that mapping is missing. If it's not meant to be referenced until Step 7, that's fine — but it's worth stating.

---

### Step 6b — Non-Functional Requirements

**What works well:**
- The "Product decision (why)" column is excellent. Every NFR has a rationale that traces back to a business or customer need. This is rare in PRDs and very valuable.
- The circuit breaker on cost (15 LLM calls per conversation) is a concrete, implementable constraint.
- Fallback behaviour is well-specified — "degrade to the current experience, not worse."
- The conversation length cap (15 turns → escalation) is a smart product decision, well-reasoned.

**Issues:**
- The "AI How" callout at the end describes how the section was drafted. This is useful as a teaching tool but breaks the reader's flow as a PRD section. It might sit better as a footnote or in a separate "process notes" section.
- Some overlap with Step 3 KPIs: first response time appears in both (< 60s in Step 3, < 5s in Step 6b). These aren't contradictory — Step 3's 60s is the outcome target, Step 6b's 5s is the per-message system constraint — but the relationship isn't stated. A reader might wonder which is the real target.
- Security NFRs (data residency, data retention) partially overlap with the security considerations listed in Step 4b. Neither section references the other.

---

## Prioritised Recommendations

### Must-Fix (breaks understanding)

1. **US-06 references O7, which doesn't exist.** Either add O7 to the opportunities table (something like "Free CS team from repetitive work so they can focus on complex cases") or remap US-06 to O4, which says the same thing.

2. **US-04 maps to O6, but should map to O5.** O5 ("every 'no' comes with a clear, policy-backed explanation") matches the user story about understanding refund decline reasons. O6 is about handoff quality.

3. **Step 2b says "five AI suitability criteria" but lists four.** The table has four criteria columns. Either the text should say "four" or a fifth criterion is missing.

4. **Steps 2c and 2b appear out of order in the document.** The reader encounters 2a → 2c → 2b. Either reorder the sections to match the numbering, or renumber them to match the order. The content is independent enough that either works.

### Should-Fix (improves clarity)

5. **US-03 mapping to O4 is a stretch.** US-03 (don't repeat myself on escalation) maps more naturally to O6 (humans get full context on handoff). Consider remapping.

6. **Assumption ID prefixes (D/F/V) are unexplained.** Add a one-line legend: "D = Demand, F = Feasibility, V = Viability" (or whatever the scheme is).

7. **Step 5 backbone needs more structure.** A numbered list or minimal table would make cross-referencing from user stories and future steps much easier than an inline arrow chain.

8. **Security considerations in Step 4b overlap with security NFRs in Step 6b.** Add a brief cross-reference in one or both sections so readers know the full picture lives across two places. Alternatively, consolidate them.

9. **Response time appears in both Step 3 (< 60s) and Step 6b (< 5s).** Add a sentence in Step 6b noting the relationship: "The < 5s per-message target supports the overall < 60s first-response KPI from Step 3."

### Nice-to-Have (polish)

10. **Step 1c references "Steps 7-8" before the reader has seen the step index.** Consider adding "(Solution Approach and Product Type)" in parentheses for context.

11. **Step 2a's process flow mentions "steps 3-6" which could be confused with document step numbers.** Rewording to "the middle portion of the process" or similar would avoid ambiguity.

12. **Hamel Husain attribution in Step 4b** may confuse external readers. Consider "Based on established AI failure taxonomies, consolidated into five product-level categories" if this needs to stand alone.

13. **"AI How" callouts** are valuable as teaching tools but break PRD flow. If this document serves dual purposes (PRD + teaching example), that's fine — but consider flagging this dual purpose in the document header so readers know to expect meta-commentary.

---

## Cross-Reference Audit Summary

| From | References | Status |
|------|-----------|--------|
| US-01 | O1, O3 | Valid |
| US-02 | O1, O2 | Valid |
| US-03 | O4 | Weak mapping — O6 fits better |
| US-04 | O6 | Wrong — should be O5 |
| US-05 | O3 | Valid |
| US-06 | O7 | **Broken — O7 does not exist** |
| US-07 | O5, O2 | Valid |
| Step 3 scope decision | Step 2b suitability criteria | Valid — traces cleanly |
| Step 4b failure modes | Step 3 KPIs | Implicit — no explicit cross-ref |
| Step 4b security | Step 6b security NFRs | No cross-reference — partial overlap |
| Step 6b NFRs | Step 3 KPIs | Partial overlap on response time — not reconciled |
| Step 1c "revisit" | Steps 7-8 | Valid but forward reference is opaque |
