"""
Test failure injection scenarios — Oakwood domain
Run from agent-flight-simulator/ directory
"""
import json
import sys
import os

# Ensure we can import from this directory
sys.path.insert(0, os.path.dirname(__file__))

from agent import run_agent
from domains.loader import load_domain

domain = load_domain("oakwood")

# Test scenarios: (name, customer_message, failure_config, guardrails, hard_guardrail)
TESTS = [
    # --- BASELINE (no failures) ---
    {
        "name": "BASELINE — Simple refund, no failures",
        "message": "Hi, I'd like a refund for order ORD-001 please. The plant arrived damaged.",
        "failure_config": None,
        "guardrails": None,
        "hard_guardrail": True,
    },

    # --- SINGLE TOOL FAILURES ---
    {
        "name": "FAIL 1 — lookup_order returns service_unavailable",
        "message": "Hi, I'd like a refund for order ORD-001 please. The plant arrived damaged.",
        "failure_config": {"lookup_order": "service_unavailable"},
        "guardrails": None,
        "hard_guardrail": True,
    },
    {
        "name": "FAIL 2 — lookup_order returns timeout",
        "message": "Hi, I'd like a refund for order ORD-001 please. The plant arrived damaged.",
        "failure_config": {"lookup_order": "timeout"},
        "guardrails": None,
        "hard_guardrail": True,
    },
    {
        "name": "FAIL 3 — issue_refund returns permission_denied",
        "message": "Hi, I'd like a refund for order ORD-001 please. The plant arrived damaged.",
        "failure_config": {"issue_refund": "permission_denied"},
        "guardrails": None,
        "hard_guardrail": True,
    },
    {
        "name": "FAIL 4 — issue_refund returns server_error",
        "message": "Hi, I'd like a refund for order ORD-001 please. The plant arrived damaged.",
        "failure_config": {"issue_refund": "server_error"},
        "guardrails": None,
        "hard_guardrail": True,
    },

    # --- MULTI-TOOL FAILURES ---
    {
        "name": "FAIL 5 — lookup AND refund both fail (cascading)",
        "message": "Hi, I'd like a refund for order ORD-001 please. The plant arrived damaged.",
        "failure_config": {"lookup_order": "service_unavailable", "issue_refund": "timeout"},
        "guardrails": None,
        "hard_guardrail": True,
    },

    # --- FAILURE + GUARDRAILS INTERACTION ---
    {
        "name": "FAIL 6 — Scope drift scenario + search_faq fails",
        "message": "I ordered some tomato plants (ORD-003) but they haven't arrived. Also, can you tell me the best time to plant tomatoes and how much B&Q charges for compost?",
        "failure_config": {"search_faq": "service_unavailable"},
        "guardrails": ["stay_on_topic"],
        "hard_guardrail": True,
    },

    # --- ESCALATION PATH FAILURE ---
    {
        "name": "FAIL 7 — escalate_to_human fails (worst case)",
        "message": "I want a refund for my BBQ, order ORD-005. It's £450 and it arrived broken. I'll contact Trading Standards if you don't sort this.",
        "failure_config": {"escalate_to_human": "server_error"},
        "guardrails": None,
        "hard_guardrail": True,
    },
]


def run_test(test, index):
    print(f"\n{'='*70}")
    print(f"TEST {index}: {test['name']}")
    print(f"{'='*70}")
    print(f"Customer: {test['message'][:100]}...")
    if test["failure_config"]:
        print(f"Failures: {test['failure_config']}")
    print()

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

        # Show the reasoning trace
        print("--- TRACE ---")
        for step in result["steps"]:
            if step["type"] == "thought":
                # Truncate long thoughts
                content = step["content"][:200]
                print(f"  THINK: {content}...")
            elif step["type"] == "action":
                print(f"  ACTION: {step['content']}")
            elif step["type"] == "observation":
                content = step["content"][:150]
                print(f"  OBSERVATION: {content}...")
            elif step["type"] == "finish":
                pass  # shown below

        print(f"\n--- AGENT RESPONSE ---")
        print(result["response"][:500])
        print(f"\n--- STATS ---")
        print(f"  Iterations: {result['iterations']}")
        print(f"  Tokens: {result['usage']}")

        return {
            "name": test["name"],
            "success": True,
            "iterations": result["iterations"],
            "response_preview": result["response"][:300],
            "steps_count": len(result["steps"]),
            "tool_calls": [s["content"] for s in result["steps"] if s["type"] == "action"],
            "had_error_observations": any(
                "Error:" in s.get("content", "")
                for s in result["steps"]
                if s["type"] == "observation"
            ),
        }

    except Exception as e:
        print(f"  ERROR: {e}")
        return {"name": test["name"], "success": False, "error": str(e)}


if __name__ == "__main__":
    results = []
    for i, test in enumerate(TESTS, 1):
        result = run_test(test, i)
        results.append(result)

    # Summary table
    print(f"\n\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    for r in results:
        status = "PASS" if r["success"] else "FAIL"
        iters = r.get("iterations", "?")
        tools = len(r.get("tool_calls", []))
        saw_error = "YES" if r.get("had_error_observations") else "no"
        print(f"  [{status}] {r['name']}")
        print(f"         Iterations: {iters} | Tool calls: {tools} | Saw errors: {saw_error}")
        if r.get("tool_calls"):
            for tc in r["tool_calls"]:
                print(f"           -> {tc}")
        print()
