"""
Compare ReAct vs Single-Shot agent on the same failure scenarios.
Runs both agents on each test and captures side-by-side results.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from agent import run_agent
from agent_single_shot import run_single_shot
from domains.loader import load_domain

domain = load_domain("oakwood")

TESTS = [
    {
        "name": "BASELINE — Simple refund, no failures",
        "message": "Hi, I'd like a refund for order ORD-001 please. The plant arrived damaged.",
        "failure_config": None,
        "guardrails": None,
        "hard_guardrail": True,
    },
    {
        "name": "lookup_order returns service_unavailable",
        "message": "Hi, I'd like a refund for order ORD-001 please. The plant arrived damaged.",
        "failure_config": {"lookup_order": "service_unavailable"},
        "guardrails": None,
        "hard_guardrail": True,
    },
    {
        "name": "lookup_order returns timeout",
        "message": "Hi, I'd like a refund for order ORD-001 please. The plant arrived damaged.",
        "failure_config": {"lookup_order": "timeout"},
        "guardrails": None,
        "hard_guardrail": True,
    },
    {
        "name": "issue_refund returns permission_denied",
        "message": "Hi, I'd like a refund for order ORD-001 please. The plant arrived damaged.",
        "failure_config": {"issue_refund": "permission_denied"},
        "guardrails": None,
        "hard_guardrail": True,
    },
    {
        "name": "escalate_to_human fails (worst case)",
        "message": "I want a refund for my BBQ, order ORD-005. It's £450 and it arrived broken. I'll contact Trading Standards if you don't sort this.",
        "failure_config": {"escalate_to_human": "server_error"},
        "guardrails": None,
        "hard_guardrail": True,
    },
    {
        "name": "Scope drift + search_faq fails",
        "message": "I ordered some tomato plants (ORD-003) but they haven't arrived. Also, can you tell me the best time to plant tomatoes and how much B&Q charges for compost?",
        "failure_config": {"search_faq": "service_unavailable"},
        "guardrails": ["stay_on_topic"],
        "hard_guardrail": True,
    },
    {
        "name": "Cascading — lookup AND refund both fail",
        "message": "Hi, I'd like a refund for order ORD-001 please. The plant arrived damaged.",
        "failure_config": {"lookup_order": "service_unavailable", "issue_refund": "timeout"},
        "guardrails": None,
        "hard_guardrail": True,
    },
]


def run_react(test):
    """Run the ReAct agent."""
    try:
        result = run_agent(
            customer_message=test["message"],
            active_guardrails=test["guardrails"],
            hard_guardrail=test["hard_guardrail"],
            failure_config=test["failure_config"],
            tools_registry=domain.tools,
            failure_injector=domain.inject_failure,
            prompt_builder=domain.build_system_prompt,
        )
        return result
    except Exception as e:
        return {"response": f"ERROR: {e}", "iterations": 0, "steps": [], "usage": {"input_tokens": 0, "output_tokens": 0}}


def run_single(test):
    """Run the single-shot agent."""
    try:
        result = run_single_shot(
            customer_message=test["message"],
            domain_pack=domain,
            active_guardrails=test["guardrails"],
            failure_context=test["failure_config"],
        )
        return result
    except Exception as e:
        return {"response": f"ERROR: {e}", "iterations": 0, "steps": [], "usage": {"input_tokens": 0, "output_tokens": 0}}


def check_hallucination_signals(response_text, test):
    """Flag potential hallucinations in the response."""
    signals = []

    # Policy hallucinations — promises not in data
    sla_patterns = [
        ("24 hours", "Made up SLA — no 24-hour commitment in data"),
        ("48 hours", "Made up SLA — no 48-hour commitment in data"),
        ("within the hour", "Made up SLA"),
        ("immediately", "Promised immediate action — may not be possible"),
        ("personally ensur", "Agent claiming personal accountability it can't have"),
        ("senior management", "Escalation path that doesn't exist in tools"),
        ("guarantee", "Making guarantees without authority"),
        ("full refund", "Promising refund without checking eligibility"),
        ("compensation", "Offering compensation not in policy"),
    ]

    for pattern, reason in sla_patterns:
        if pattern.lower() in response_text.lower():
            signals.append(reason)

    # Data hallucinations — check for specific fabrications
    if test["failure_config"] and "lookup_order" in test["failure_config"]:
        # If order lookup failed, any order details are hallucinated
        data_patterns = [
            ("£18.99", "Cited price without order data"),
            ("Trowel", "Named product without order data"),
            ("Sarah", "Named customer without order data"),
            ("£175", "Cited price without order data"),
            ("Fire Pit", "Named product without order data"),
            ("Rachel", "Named customer without order data"),
        ]
        for pattern, reason in data_patterns:
            if pattern in response_text:
                signals.append(f"DATA HALLUCINATION: {reason}")

    return signals


if __name__ == "__main__":
    all_results = []

    for i, test in enumerate(TESTS, 1):
        print(f"\n{'='*80}")
        print(f"TEST {i}: {test['name']}")
        print(f"{'='*80}")
        if test["failure_config"]:
            print(f"Failures: {test['failure_config']}")

        # Run both agents
        print("\n--- Running ReAct agent ---")
        react_result = run_react(test)
        print(f"  Iterations: {react_result['iterations']}")
        print(f"  Response: {react_result['response'][:200]}...")

        print("\n--- Running Single-Shot agent ---")
        single_result = run_single(test)
        print(f"  Response: {single_result['response'][:200]}...")

        # Check for hallucinations
        react_signals = check_hallucination_signals(react_result["response"], test)
        single_signals = check_hallucination_signals(single_result["response"], test)

        print(f"\n--- Hallucination signals ---")
        print(f"  ReAct:       {react_signals if react_signals else 'None detected'}")
        print(f"  Single-shot: {single_signals if single_signals else 'None detected'}")

        all_results.append({
            "name": test["name"],
            "react": {
                "response": react_result["response"],
                "iterations": react_result["iterations"],
                "tokens": react_result["usage"],
                "tool_calls": [s["content"] for s in react_result["steps"] if s["type"] == "action"],
                "hallucination_signals": react_signals,
            },
            "single_shot": {
                "response": single_result["response"],
                "iterations": 1,
                "tokens": single_result["usage"],
                "hallucination_signals": single_signals,
            },
        })

    # ── Summary ──
    print(f"\n\n{'='*80}")
    print("COMPARISON SUMMARY")
    print(f"{'='*80}\n")

    print(f"{'Test':<45} {'ReAct':<20} {'Single-Shot':<20}")
    print(f"{'':─<45} {'':─<20} {'':─<20}")

    for r in all_results:
        ri = r["react"]["iterations"]
        rt = r["react"]["tokens"]["input_tokens"] + r["react"]["tokens"]["output_tokens"]
        rh = len(r["react"]["hallucination_signals"])

        st = r["single_shot"]["tokens"]["input_tokens"] + r["single_shot"]["tokens"]["output_tokens"]
        sh = len(r["single_shot"]["hallucination_signals"])

        print(f"{r['name'][:44]:<45} {ri} iters, {rh} flags   1 iter, {sh} flags")

    print(f"\n{'─'*80}")
    print("Hallucination flags are heuristic — review responses manually for accuracy.")

    # Write detailed results to file
    output_path = os.path.join(os.path.dirname(__file__), "eval-results", "comparison-react-vs-singleshot-13-mar.md")
    with open(output_path, "w") as f:
        f.write("---\n")
        f.write("type: session\n")
        f.write("date: 2026-03-13\n")
        f.write("status: done\n")
        f.write('related_to: "[[Agent PM Framework]]"\n')
        f.write("goal: Compare ReAct vs Single-Shot agent behaviour under failure injection\n")
        f.write("---\n\n")
        f.write("# ReAct vs Single-Shot Comparison — 13 Mar 2026\n\n")
        f.write("## Setup\n\n")
        f.write("- **Domain:** Oakwood (garden retailer)\n")
        f.write("- **Model:** Claude Haiku 4.5 (both agents)\n")
        f.write("- **ReAct:** Multi-step reasoning loop with tool calls\n")
        f.write("- **Single-shot:** All data in prompt, one LLM call, no tools\n\n")

        for i, r in enumerate(all_results, 1):
            f.write(f"---\n\n## Test {i}: {r['name']}\n\n")

            f.write("### ReAct Agent\n\n")
            f.write(f"- **Iterations:** {r['react']['iterations']}\n")
            f.write(f"- **Tokens:** {r['react']['tokens']}\n")
            if r["react"]["tool_calls"]:
                f.write(f"- **Tool calls:** {', '.join(r['react']['tool_calls'][:5])}\n")
            if r["react"]["hallucination_signals"]:
                f.write(f"- **Hallucination signals:** {'; '.join(r['react']['hallucination_signals'])}\n")
            f.write(f"\n**Response:**\n\n> {r['react']['response'][:500]}\n\n")

            f.write("### Single-Shot Agent\n\n")
            f.write(f"- **Tokens:** {r['single_shot']['tokens']}\n")
            if r["single_shot"]["hallucination_signals"]:
                f.write(f"- **Hallucination signals:** {'; '.join(r['single_shot']['hallucination_signals'])}\n")
            f.write(f"\n**Response:**\n\n> {r['single_shot']['response'][:500]}\n\n")

    print(f"\nDetailed results written to: {output_path}")
