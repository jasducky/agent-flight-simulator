"""
Multi-persona evaluation runner for Inside the Agent.
Runs selected scenarios across all 3 domains, captures full traces.
Doubles as smoke test + evidence for Hamza/Hamel persona evaluations.
"""

import sys
import os
import json
from datetime import datetime

# Must run from the agent-flight-simulator directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent import run_agent
from domains.loader import load_domain

# ── Scenario selections ──────────────────────────────────────────────────────

RUNS = [
    # Oakwood — baseline happy path
    {
        "domain": "oakwood",
        "scenario_id": 1,
        "label": "Oakwood — Simple Refund (baseline)",
        "guardrails": [],
        "hard_guardrail": True,
    },
    # Oakwood — Scope Drift WITHOUT guardrails (killer demo part 1)
    {
        "domain": "oakwood",
        "scenario_id": 4,
        "label": "Oakwood — Scope Drift (NO guardrails)",
        "guardrails": [],
        "hard_guardrail": False,
    },
    # Oakwood — Scope Drift WITH guardrails (killer demo part 2)
    {
        "domain": "oakwood",
        "scenario_id": 4,
        "label": "Oakwood — Scope Drift (WITH guardrails)",
        "guardrails": ["stay_on_topic", "no_competitors"],
        "hard_guardrail": False,
    },
    # GP — Diagnosis Seeking WITHOUT guardrails (killer demo part 1)
    {
        "domain": "gp_triage",
        "scenario_id": 3,
        "label": "GP — Diagnosis Seeking / Ibuprofen Allergy (NO guardrails)",
        "guardrails": [],
        "hard_guardrail": False,
    },
    # GP — Diagnosis Seeking WITH guardrails (killer demo part 2)
    {
        "domain": "gp_triage",
        "scenario_id": 3,
        "label": "GP — Diagnosis Seeking / Ibuprofen Allergy (WITH guardrails)",
        "guardrails": ["no_diagnosis", "no_medication_advice"],
        "hard_guardrail": False,
    },
    # GP — Chest Pain (emergency escalation)
    {
        "domain": "gp_triage",
        "scenario_id": 2,
        "label": "GP — Chest Pain (emergency escalation)",
        "guardrails": [],
        "hard_guardrail": True,
    },
    # GP — Mental Health (highest stakes)
    {
        "domain": "gp_triage",
        "scenario_id": 4,
        "label": "GP — Mental Health / Self-Harm",
        "guardrails": ["no_mental_health_assessment"],
        "hard_guardrail": True,
    },
    # Estate — Area Judgement WITHOUT guardrails (killer demo part 1)
    {
        "domain": "estate_agent",
        "scenario_id": 2,
        "label": "Estate — Area Judgement Trap (NO guardrails)",
        "guardrails": [],
        "hard_guardrail": False,
    },
    # Estate — Area Judgement WITH guardrails (killer demo part 2)
    {
        "domain": "estate_agent",
        "scenario_id": 2,
        "label": "Estate — Area Judgement Trap (WITH guardrails)",
        "guardrails": ["no_area_judgements"],
        "hard_guardrail": False,
    },
    # Estate — DSS / Housing Benefit (sensitive topic)
    {
        "domain": "estate_agent",
        "scenario_id": 4,
        "label": "Estate — DSS / Housing Benefit",
        "guardrails": [],
        "hard_guardrail": False,
    },
]


def get_scenario(domain_pack, scenario_id):
    """Find a scenario by ID in a domain pack."""
    for s in domain_pack.scenarios:
        if s["id"] == scenario_id:
            return s
    return None


def format_step(step):
    """Format a single trace step for markdown."""
    icons = {
        "thought": "💭 Thought",
        "action": "🔧 Action",
        "observation": "👁 Observation",
        "finish": "✅ Final Response",
    }
    label = icons.get(step["type"], step["type"])
    return f"**{label}:**\n{step['content']}"


def run_single(run_config, domain_packs):
    """Run a single scenario and return formatted results."""
    domain_key = run_config["domain"]
    pack = domain_packs[domain_key]
    scenario = get_scenario(pack, run_config["scenario_id"])

    if not scenario:
        return {"error": f"Scenario {run_config['scenario_id']} not found in {domain_key}"}

    print(f"\n{'='*60}")
    print(f"  {run_config['label']}")
    print(f"  Customer: {scenario['customer_message'][:80]}...")
    print(f"  Guardrails: {run_config['guardrails'] or 'NONE'}")
    print(f"{'='*60}")

    try:
        result = run_agent(
            customer_message=scenario["customer_message"],
            active_guardrails=run_config["guardrails"] or None,
            refund_guardrail=run_config["hard_guardrail"],
            tools_registry=pack.tools,
            prompt_builder=pack.build_system_prompt,
            failure_injector=pack.inject_failure,
        )

        # Print trace live
        for step in result["steps"]:
            icon = {"thought": "💭", "action": "🔧", "observation": "👁", "finish": "✅"}.get(step["type"], "  ")
            content_preview = step["content"][:120].replace("\n", " ")
            print(f"  {icon} {content_preview}")

        print(f"\n  Iterations: {result['iterations']} | Tokens: {result['usage']['input_tokens']}in/{result['usage']['output_tokens']}out")

        return {
            "label": run_config["label"],
            "domain": domain_key,
            "scenario_id": run_config["scenario_id"],
            "scenario_name": scenario["name"],
            "customer_message": scenario["customer_message"],
            "guardrails_active": run_config["guardrails"],
            "hard_guardrail": run_config["hard_guardrail"],
            "what_to_watch": scenario["what_to_watch"],
            "expected_evals": scenario["evals"],
            "silent_failure_note": scenario.get("silent_failure_note", ""),
            "proves": scenario.get("proves", ""),
            "response": result["response"],
            "steps": result["steps"],
            "iterations": result["iterations"],
            "usage": result["usage"],
            "error": None,
        }

    except Exception as e:
        print(f"  ❌ ERROR: {e}")
        return {
            "label": run_config["label"],
            "error": str(e),
        }


def write_markdown_report(results, output_path):
    """Write all results to a markdown file for persona evaluation."""
    lines = [
        "# Inside the Agent — Evaluation Run",
        f"\n**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"**Runs:** {len(results)}",
        f"**Domains:** Oakwood, GP Triage, Estate Agent",
        "",
    ]

    # Summary table
    lines.append("## Summary\n")
    lines.append("| # | Scenario | Guardrails | Iterations | Tokens | Error |")
    lines.append("|---|----------|-----------|------------|--------|-------|")
    for i, r in enumerate(results, 1):
        if r.get("error") and not r.get("response"):
            lines.append(f"| {i} | {r['label']} | — | — | — | {r['error'][:50]} |")
        else:
            guardrail_str = ", ".join(r.get("guardrails_active", [])) or "NONE"
            lines.append(
                f"| {i} | {r['label']} | {guardrail_str} | "
                f"{r.get('iterations', '?')} | "
                f"{r.get('usage', {}).get('input_tokens', '?')}in/{r.get('usage', {}).get('output_tokens', '?')}out | "
                f"{'—' if not r.get('error') else r['error'][:30]} |"
            )

    # Full traces
    lines.append("\n---\n")
    lines.append("## Full Traces\n")

    for i, r in enumerate(results, 1):
        lines.append(f"### Run {i}: {r['label']}\n")

        if r.get("error") and not r.get("response"):
            lines.append(f"**ERROR:** {r['error']}\n")
            continue

        lines.append(f"**Customer:** {r.get('customer_message', 'N/A')}\n")
        lines.append(f"**Guardrails:** {', '.join(r.get('guardrails_active', [])) or 'NONE'}")
        lines.append(f"**Hard guardrail:** {'ON' if r.get('hard_guardrail') else 'OFF'}\n")
        lines.append(f"**What to watch:** {r.get('what_to_watch', 'N/A')}\n")

        if r.get("silent_failure_note"):
            lines.append(f"> **Silent failure note:** {r['silent_failure_note']}\n")

        lines.append("#### Trace\n")
        for step in r.get("steps", []):
            lines.append(format_step(step))
            lines.append("")

        lines.append(f"**Final response:** {r.get('response', 'N/A')}\n")
        lines.append(f"**Iterations:** {r.get('iterations')} | **Tokens:** {r.get('usage', {}).get('input_tokens', '?')}in / {r.get('usage', {}).get('output_tokens', '?')}out\n")

        # Expected evals
        evals = r.get("expected_evals", {})
        if evals:
            lines.append("#### Expected Eval Outcomes\n")
            lines.append("| Dimension | Expected | Pass condition |")
            lines.append("|-----------|----------|---------------|")
            for dim_key, dim_val in evals.items():
                expected = dim_val.get("expected", dim_val.get("expected_with_guardrails", dim_val.get("expected_without_guardrails", "N/A")))
                pass_cond = dim_val.get("pass_condition", "N/A")
                lines.append(f"| {dim_key} | {expected[:80]} | {pass_cond[:80]} |")
            lines.append("")

        lines.append(f"**Proves:** {r.get('proves', 'N/A')}\n")
        lines.append("---\n")

    with open(output_path, "w") as f:
        f.write("\n".join(lines))

    return output_path


def main():
    print("=" * 60)
    print("  INSIDE THE AGENT — Evaluation Runner")
    print("  10 scenarios across 3 domains")
    print("  Smoke test + persona evaluation evidence")
    print("=" * 60)

    # Load all domain packs
    print("\nLoading domains...")
    domain_packs = {}
    for key in ["oakwood", "gp_triage", "estate_agent"]:
        pack = load_domain(key)
        domain_packs[key] = pack
        print(f"  ✓ {pack.name} ({len(pack.scenarios)} scenarios)")

    # Run all scenarios
    results = []
    for i, run_config in enumerate(RUNS, 1):
        print(f"\n[{i}/{len(RUNS)}]", end="")
        result = run_single(run_config, domain_packs)
        results.append(result)

    # Write report
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "eval-results")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"eval-run-{datetime.now().strftime('%Y-%m-%d-%H%M')}.md")
    write_markdown_report(results, output_path)

    # Summary
    errors = [r for r in results if r.get("error") and not r.get("response")]
    successes = [r for r in results if r.get("response")]
    total_tokens_in = sum(r.get("usage", {}).get("input_tokens", 0) for r in successes)
    total_tokens_out = sum(r.get("usage", {}).get("output_tokens", 0) for r in successes)

    print(f"\n{'='*60}")
    print(f"  DONE: {len(successes)} succeeded, {len(errors)} failed")
    print(f"  Total tokens: {total_tokens_in} in / {total_tokens_out} out")
    print(f"  Report: {output_path}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
