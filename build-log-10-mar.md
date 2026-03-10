# Build Log — 10 March 2026

## What we built today

Polished the Agent Flight Simulator from working spike to demo-ready. Three layers of work: bug fixes, UI enhancements, and a critical discovery about how the agent loop works.

---

## The Fake Observations Bug (the interesting bit)

When we first tested the app with a real API key, something unexpected happened. The agent was supposed to go through a loop:

1. **Think** about what to do
2. **Call a tool** (e.g. look up an order)
3. **Get the result back** from the tool
4. **Think again** based on what it learned
5. Repeat until done

But instead, Claude (the model) was doing the entire loop **in a single response**. It would say:

> "Thought: I need to look up the order..."
> "Action: lookup_order(order_id='ORD-001')"
> "Observation: Order found, customer is Sarah Mitchell, item is trowel set..."

That "Observation" line was **made up by the model**. It never actually called the tool — it just *imagined* what the tool would return. Then it kept going, imagining more tool results, until it reached a final answer.

**Why this matters for PMs:** This is exactly the kind of silent failure that's invisible without observability. The final answer looked fine — polite, correct-ish. But the agent never actually checked the database. In a real system, this means the agent could confidently tell a customer their refund is processed... when it never actually processed it.

**The fix:** We added `stop_sequences=["Observation:"]` to the API call. This tells Claude: "Stop generating text when you reach the word 'Observation:'" — because that's the point where the *real* tool should run. It's like putting a wall in the middle of the conversation: the model can think and choose a tool, but then it MUST stop and let the code actually run the tool.

After the fix: 5 real loops, 4 real tool calls, actual data from the mock database.

---

## The Scenario 5 Problem

Even after fixing the loop, Scenario 5 (High-Value Refund) wasn't working as designed. The scenario was supposed to show a **hard guardrail** blocking a £175 refund that exceeds the £50 auto-limit.

But the agent was too clever. The original scenario said the customer bought the fire pit "five weeks ago" — which is outside the 30-day refund window. So the agent looked at the policy, decided the customer wasn't eligible, and **never even tried to issue the refund**. The guardrail never fired because the agent never reached it.

**The fix:** Rewrote the scenario so the customer is clearly within the return window (just received it, still in packaging, changed their mind). Now the *only* reason to block is the £175 amount exceeding the £50 limit. The agent looks up the order, checks the policy, tries the refund, gets BLOCKED, and escalates. The trace tells the whole story.

**The PM lesson:** When designing guardrails, you need scenarios that actually trigger them. If your test scenario has two reasons to fail, you can't be sure which one the agent will hit first. Design your test cases so only the thing you're testing is the variable.

---

## Teaching Note: Stop Sequences Explained

### What's happening in plain English

Think of a conversation with someone who talks too much. They answer your question, but then keep going — answering questions you haven't asked yet, making up what you *would* have said, then responding to that too.

That's what Claude was doing. The ReAct format looks like:

```
Thought: I need to look up this order...
Action: lookup_order(order_id="ORD-001")
Observation: Order found, customer is Sarah...
Thought: Now I'll check the policy...
```

Claude knows this pattern from its training. So it didn't stop after the Action line — it kept going and **wrote its own Observation**, imagining what the tool would return. Then it thought again, imagined another tool result, and so on. All in one breath. All hallucinated.

### What `stop_sequences` does

It's a parameter sent with the API call — a list of words that act as a **stop sign** for the model.

`stop_sequences=["Observation:"]` tells Claude: "Generate text as normal. But the moment you're about to write the word 'Observation:', **stop immediately**. Hand control back to the code."

So now Claude generates:

```
Thought: I need to look up this order...
Action: lookup_order(order_id="ORD-001")
[STOPS HERE]
```

Then our Python code:
1. Reads what Claude wrote
2. Sees the Action line
3. Actually calls the real `lookup_order` function with real data
4. Gets the real result back
5. Sends it to Claude as the next message

Now Claude reasons about **real information**, not something it made up.

### The PM framing: who controls the loop?

This is a design decision about where **code controls the agent** vs where the **model controls itself**.

| Without stop sequences | With stop sequences |
|---|---|
| Model runs the entire process unsupervised | Model proposes an action, then **code takes over** to execute it |
| Like giving someone a checklist and saying "do all of this, don't check in with me" | Like saying "tell me what you want to do, I'll do it, then tell you what happened" |
| Fast (one API call) but unreliable (hallucinated data) | Slower (multiple API calls) but grounded in real data |

This maps directly to **HITL levels** in the ARDS:
- Without stop sequences = **AUTONOMOUS** — agent does everything, including making up results
- With stop sequences = **GATED** — agent proposes, code executes, agent continues with real data

### Why this matters for the thesis

This is a perfect real example of the "two sides of the same coin" argument:
- **Without observability** (the Flight Recorder), we'd never have known the agent was faking its tool calls. The final answer looked fine.
- **Without the guardrail** (stop sequences forcing real tool execution), the agent was confidently operating on hallucinated data.
- You only caught it because you could **see inside the loop**.

### Broader implication: "tool use" doesn't mean "tool use"

Just because an agent has tools available doesn't mean it actually uses them. An agent can *appear* to use tools while hallucinating the entire interaction. Without observability, you'd never know. This is one of the silent failure modes from the Quality Defence Layers model — the output looks correct, structured, and confident, but it's grounded in nothing.

---

## Teaching Note: Scenario Design for Guardrail Testing

When Scenario 5 originally said the customer bought the fire pit "five weeks ago" (outside the 30-day refund window), the agent found a perfectly valid reason to decline the refund *before* it ever reached the £50 guardrail. The hard guardrail never fired — not because it was broken, but because the agent was too clever.

**The lesson:** When designing test scenarios for guardrails, isolate the variable. If your scenario has two reasons to fail, you can't control which one the agent hits first. Design your test so the *only* thing that should stop the process is the guardrail you're testing.

This is an eval design principle: **one test, one variable, one expected behaviour.** It applies to agent evals the same way it applies to A/B tests or user research — if you change two things at once, you don't know which one caused the result.

---

## UI Enhancements

### 1. Loop Grouping
The Flight Recorder now groups steps into **"Loop 1", "Loop 2"** etc. instead of a flat list. This makes the ReAct pattern visible — you can see at a glance that the agent went around the loop 3 times before answering.

Each loop header also shows if a guardrail was involved:
- 🛡️ = a soft guardrail influenced the agent's thinking
- 🚫 = a hard guardrail blocked an action

### 2. Customer View / PM View Toggle
After running a scenario, you can switch between:
- **Customer View** — just the final response (what the end user would see)
- **PM View** — full trace, tools, guardrails, prompt inspector

The demo move: run a scenario in Customer View ("looks fine, right?"), then toggle to PM View and see everything the agent was doing behind the scenes.

### 3. Behaviour Comparison Stats
In compare mode (guardrails OFF vs ON), there's now a stats panel showing the delta: how many loops, tool calls, tokens, and guardrails fired — side by side.

### 4. Guardrail Visual Cues
- Green/grey pill badges at the top of the Flight Recorder showing which guardrails are armed
- 🛡️ icons on loop headers where soft guardrails shaped reasoning
- 🚫 icons where hard guardrails blocked actions
- "Thought (guardrail-influenced)" labels on specific thoughts that show redirect language

---

## Teaching Note: Streamlit Session State (the disappearing results bug)

### What happened

After running a scenario, clicking the Customer View / PM View toggle made the entire result disappear — back to the welcome screen.

### Why it happened

Streamlit works differently from a normal web app. Every time you interact with ANY widget (a button, a toggle, a radio button), Streamlit **reruns the entire Python script from top to bottom**. It's not like clicking a tab on a normal website — it's literally re-executing all the code.

The Run button (`st.button`) returns `True` only on the click that triggered it. On the next rerun (caused by clicking the radio button), `run_clicked` is `False` again. So the code goes straight to the `else` branch and shows the welcome screen. The agent result is gone — it was just a local variable that only existed during that one run of the script.

### How we fixed it

We used `st.session_state` — Streamlit's built-in way to persist data across reruns. Think of it as a shared notebook that survives page refreshes:

1. When the Run button is clicked, we run the agent and **save the result** to `st.session_state["last_run"]`
2. The display logic checks `if "last_run" in st.session_state` instead of `if run_clicked`
3. Now when you toggle Customer/PM View, the page reruns, but the result is still there in session state

### The PM takeaway

This is a common pattern in any interactive tool: **separate the action (running the agent) from the display (showing the results)**. The action happens once. The display can be re-rendered many times from the saved data. This is the same principle behind caching API responses, storing conversation history, or keeping agent state between turns.

---

## Bug Fixes

- **Dead code removed** — a line that literally said `_render_step(i, step) if False else None`
- **CSS typo** — `text-align: centre` (UK English!) → `text-align: center` (CSS doesn't do UK English)
- **Error handling** — API failures now show a friendly message instead of a Python error dump
- **Float cast** — defensive `amount = float(amount)` in the refund tool, because Claude sometimes sends amounts as text

---

## Files Changed

| File | What changed |
|------|-------------|
| `app.py` | Full rewrite — loop grouping, Customer/PM view, compare stats, guardrail badges |
| `agent.py` | Added `stop_sequences=["Observation:"]` — the critical fix |
| `tools.py` | Added `amount = float(amount)` defensive cast |
| `scenarios.py` | Rewrote Scenario 5 so the guardrail actually fires |
| `ARDS Lite - Agent Flight Simulator.md` | Updated to ARDS structure, reflects all new features |
| `.env` | API key added |

---

## Teaching Note: Why ReAct Exists — Externalised Reasoning

### The missing thought problem

After fixing the stop sequences bug, we hit a subtler problem. When the agent received a simple off-topic question ("Do B&Q sell cheaper trowels?"), the Flight Recorder showed no Thought step at all — just a Final Response. The reasoning trace was empty.

The agent still answered correctly (redirected to Oakwood products). But we couldn't see *why* it made that decision. The trace was useless.

### Why it happened

The model wasn't following the `Thought: ... FINISH:` format for questions that didn't need tool calls. It just responded directly — a plain paragraph with no structured prefix. Our parser looks for `Thought:` and `FINISH:` labels to split the response into steps. No labels = no steps = nothing to display.

**The fix:** Strengthened the system prompt to enforce the ReAct format on *every* response, not just tool-calling ones: "Every response MUST begin with Thought: — no exceptions."

### The deeper insight: LLMs don't "think then respond"

This sparked an important question: doesn't every LLM have to "think"?

**No — not in the way humans do.** LLMs don't have a separate thinking stage. They generate text one token at a time, with each token influenced by everything before it. There's no hidden internal reasoning that happens before the output. The output *is* the reasoning.

When we write `Thought:` in the ReAct format, we're not capturing some hidden process. We're asking the model to **generate reasoning text before generating answer text**. It's all just output — but the order matters.

**Analogy:** Imagine asking a PM "should we build this feature?" Without structure, they say "Yes, here's the spec" — they probably considered trade-offs, but you can't see them. With structure, they first write a decision log: "Customer need is X, cost is Y, risk is Z — therefore yes." Same conclusion, but now the reasoning is visible and auditable.

### What ReAct actually does

A ReAct agent isn't making the model "think more." It imposes a structured format — Thought → Action → Observation — that forces the model to externalise its reasoning at every step.

Without that structure, the model can:
- Skip straight to an answer (no visible reasoning)
- Call a tool and answer in one breath (hallucinating results — the fake observations bug)
- Make a decision without explaining why

ReAct says: you must show your working at every step. Think out loud, then act, then look at what happened, then think again.

### Why this matters for the Flight Recorder

The Flight Recorder isn't magic. It's just reading structured text the agent was forced to produce. No structure = nothing to display. The ReAct format is what makes observability possible.

This connects directly to the thesis: **observability and guardrails are two sides of the same coin.** ReAct gives you observability. Without observability, you'd never know if guardrails fired or if the agent hallucinated its way through.

We saw three failure modes in one session that prove this:
1. **Fake observations** (before stop sequences) — agent hallucinated tool results, invisible without the trace
2. **Missing thoughts** (before format enforcement) — agent's reasoning was invisible, trace was empty
3. **False guardrail attribution** (before detection fix) — trace claimed a guardrail fired when none were active

Each one was only caught because we could see inside the loop. Each one required a different fix. All three would have been invisible to anyone just looking at the final customer response.

---

## Teaching Note: Three-Tier Guardrail Visibility

### The false positive problem

After adding guardrail detection to the Flight Recorder, we tested with a pizza recipe question (all guardrails OFF). The trace incorrectly showed "🛡️ Soft guardrail active" and "Thought (guardrail-influenced)" — even though no guardrails were toggled on.

The agent redirected the customer because it's a customer service agent (that's its base personality). But the keyword-matching detection saw words like "redirect" and "scope" and assumed a guardrail was responsible.

### The fix: three distinct visual states

We needed to differentiate between three things that can look similar but are fundamentally different:

| State | What's happening | Visual in trace | Can be overridden? |
|---|---|---|---|
| **Agent personality** | Base prompt identity — the agent naturally stays in role | `💭 Thought` (plain, no badge) | N/A — it's just who the agent is |
| **Soft guardrail** | Prompt block injected, shaping reasoning | `💭🛡️ Thought (soft guardrail shaped this)` + loop badge | Yes — the model could ignore it |
| **Hard guardrail** | Code blocked the action | `🚫 BLOCKED — Hard guardrail (code)` in red | No — code wall, impossible to bypass |

**The implementation:** Soft guardrail detection only fires when at least one soft guardrail toggle is actually ON. Hard guardrail detection (looking for "BLOCKED" in tool responses) always fires regardless of toggles — because it's code-level enforcement.

### The PM takeaway

When building agents, you need to know *why* something happened. "The agent didn't discuss competitors" could mean three different things:
1. The agent just stayed in character (no guardrail needed)
2. A prompt instruction redirected it (soft — could fail under pressure)
3. Code prevented it (hard — reliable but inflexible)

The right response depends on which one it is. If you're relying on agent personality for something safety-critical, you have a problem. If you're using a hard guardrail for something that needs nuance, you have a different problem. The trace should tell you which is which.

---

## Teaching Note: How the ReAct Loop Actually Works

### "Is it really an agent if it's just a prompt?"

A common first reaction when looking at a ReAct agent's code: "The prompt tells the model to use Thought/Action/Observation format — isn't that just prompt engineering?"

No. The prompt is one part. The agent is the **loop + tool execution + stop sequences** working together. Here's why.

### What makes it an agent

Every agent needs both a prompt and a code loop. The prompt tells the model who it is and what tools are available — like a job description. The code loop controls what actually happens — like the operational process the employee follows.

| Component | What it does | Without it |
|---|---|---|
| **System prompt** | Tells the model its role, available tools, and the ReAct format | Model doesn't know who it is or how to structure responses |
| **The loop** (`for i in range(MAX_ITERATIONS)`) | Makes multiple API calls — one per reasoning step | Single API call = chatbot, not agent |
| **Stop sequences** (`stop_sequences=["Observation:"]`) | Forces the model to stop after proposing an action | Model hallucinates tool results (the fake observations bug) |
| **Tool execution** (`call_tool()`) | Runs real Python functions against real data | Agent reasons about imaginary data |
| **Feeding results back** | Sends real tool output as the next message to Claude | Model never learns what actually happened |

Remove any one of these and it stops being an agent. The prompt alone gives you a chatbot that pretends to use tools. The loop alone gives you an agent that doesn't know who it is.

### Walking through a real example

Customer sends: "I want a refund for ORD-001."

**Loop 1 — Look up the order:**

The code sends the system prompt + customer message to Claude. Claude responds:

```
Thought: I need to look up this order first.
Action: lookup_order(order_id="ORD-001")
Observ— ← STOPPED HERE by stop_sequences
```

Claude was about to write its own "Observation:" — making up what the order looks like. But `stop_sequences` cuts it off. The code takes over:

1. Parses the response — finds `lookup_order` with `order_id="ORD-001"`
2. Actually runs the Python function `lookup_order("ORD-001")`
3. Gets back real data: "Customer: Sarah Mitchell, Item: Trowel Set, £18.99..."
4. Sends it back to Claude as the next message

**Loop 2 — Check the policy:**

Claude now has the real order data. It responds:

```
Thought: Order found, it's a hand-tool. I need to check the refund policy.
Action: check_refund_policy(category="hand-tools")
Observ— ← STOPPED AGAIN
```

Code runs the real function, gets "Window: 30 days, Condition: unused, in original packaging", sends it back.

**Loop 3 — Issue the refund:**

Claude has the order AND the policy. It responds:

```
Thought: Within 30 days, item unused. I should issue the refund.
Action: issue_refund(order_id="ORD-001", amount=18.99, reason="Changed mind")
Observ— ← STOPPED
```

Code runs `issue_refund` — and THIS is where the hard guardrail lives. £18.99 is under £50, so it passes. Returns "Refund processed successfully."

**Loop 4 — Final response:**

Claude has everything it needs. It responds:

```
Thought: Refund is done. I should confirm with the customer.
FINISH: Hi Sarah, your refund of £18.99 for the Willow Garden Trowel Set
has been processed and will appear on your statement within 5-7 days...
```

Code sees `FINISH` — the loop ends. Four API calls. Four real tool executions. Real data at every step.

### The key insight: each loop is a separate API call

Claude doesn't run all four steps in one breath. It proposes one action, gets stopped, the code does the real work, and Claude only continues once it has real data.

This is what `for i in range(MAX_ITERATIONS)` does — it goes around up to 10 times, one API call per loop, until Claude says `FINISH`. Each loop is a Thought → Action → (code runs tool) → Observation cycle.

### Two ways to build this

| Approach | How tools work | Visible reasoning? |
|---|---|---|
| **Text-based ReAct** (what we built) | Prompt defines the format, regex parses actions, code calls tools | Yes — Thought text is right there in the output |
| **Native tool use** (Anthropic's tools API) | Tools defined as structured JSON, Claude returns `tool_use` blocks | Hidden — reasoning happens inside the API, harder to inspect |

We chose text-based ReAct deliberately. The whole point of "Inside the Agent" is making reasoning visible. Native tool use would hide the thinking behind structured API calls — the audience would see "tool was called" but not *why* the agent decided to call it.

### The PM framing

When evaluating any AI agent, ask: **where is the loop?** If there's no loop — just a single API call with a clever prompt — it's a chatbot, not an agent. The loop is what gives the agent the ability to reason over multiple steps, use real tools, and adapt based on what it learns.

The prompt matters (it defines the agent's role and capabilities). But the loop is what makes it an agent.

---

## The Eager Model Bug — Action Regex and Priority Fix

### The problem

Running the Scope Drift scenario (guardrails ON), the trace showed only **one loop with a single giant Thought block** — no Action, no Tool Response, no separate steps. The agent appeared to reason about the entire customer query, plan its response, and jump straight to Final Response. The response said things like "[details based on lookup]" — it was **hallucinating the tool result** instead of actually calling the tool.

### Why it happened

Two issues working together:

**1. The Action regex was too strict**

```python
# Old — required Action to be at END of a line
re.search(r'Action:\s*(\w+)\((.+?)\)\s*$', text, re.MULTILINE)
```

With guardrails active, the model would write the Action line then immediately continue planning: "Once I get that information, I can..." — which meant the Action line was no longer at the end of the text. The `$` anchor failed, `parse_action()` returned `None`, and the entire response was treated as a finish.

```python
# Fixed — finds Action anywhere in the text
re.search(r'Action:\s*(\w+)\((.+?)\)', text, re.MULTILINE)
```

**2. FINISH was checked before Action**

The original code flow was:
1. Check for FINISH → if found, return immediately
2. Check for Action → if found, execute tool

But sometimes the model generates BOTH in one response — it writes an Action line, then continues planning, then writes FINISH with a hallucinated response. The old code would find the FINISH first and return, never executing the tool.

Fixed by flipping the priority:
1. Check for Action FIRST → if found, execute the tool (ignore any premature FINISH)
2. Only check for FINISH if no Action was found

### Why this matters for PMs

This is a textbook example of why **observability matters**. Without the reasoning trace, you'd see a customer get a helpful-looking response. You'd never know the agent skipped its tool calls and hallucinated the data. The response might even be correct (if the model's training data happened to match) — but it would be correct *for the wrong reasons*.

In production, this kind of silent failure is dangerous:
- The response **looks right** but isn't grounded in real data
- It works 90% of the time, fails unpredictably on the other 10%
- Without trace visibility, you'd never catch it
- The fix is mechanical (regex + priority), but finding it requires seeing inside the agent

This is the core thesis: **you can't set guardrails without observability, because you wouldn't know what's actually happening**.

### The fix in detail

```python
# agent.py — both run_agent() and run_agent_streaming()

# Before: check FINISH first, then Action
final_response = parse_finish(assistant_text)
if final_response:
    return ...  # ← Might skip a real Action!

action = parse_action(assistant_text)  # ← Never reached

# After: check Action first, only FINISH if no Action
action = parse_action(assistant_text)

if action:
    # Has an action — execute the tool, ignore any premature FINISH
    ...
elif parse_finish(assistant_text):
    # FINISH with no action — genuinely done
    ...
else:
    # Neither — extract thought and continue loop
    ...
```

### Result

Scope Drift now shows the full trace:
- **Loop 1:** Thought (identifies 3 questions, recognises 2 are off-topic) → Action (lookup_order) → Tool Response (real order data)
- **Loop 2:** Thought (plans response — order info + polite redirects for gardening and competitor topics)
- **Final Response:** Answers the order query with real data, redirects gardening advice to the blog, declines competitor comparison

Each step is visible. Each tool call actually executes. The guardrails shape the reasoning in Loop 2, not by blocking but by redirecting. And the trace proves it.

---

## What's next

- Smoke test all 6 scenarios with the regex fix
- Pre-run Scenarios 1, 4, 5 multiple times (non-deterministic model = different results each time)
- Add FAQ/knowledge base tool (simulated RAG)
- Domain pack restructure for multi-scenario support
- Time the full demo walkthrough
- Take backup screenshots
