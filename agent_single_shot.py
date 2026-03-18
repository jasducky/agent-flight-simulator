"""
Single-shot agent — NO reasoning loop.

The simplest possible agent architecture: give the model the customer message,
tool descriptions, and all the mock data in one go. Let it respond in a single pass.
No tool calling, no ReAct loop, no intermediate reasoning.

This is what most teams build first when prototyping an AI feature.
It's the baseline against which ReAct demonstrates its value.
"""

import os
import anthropic
from dotenv import load_dotenv

load_dotenv()

MODEL = "claude-haiku-4-5-20251001"


def run_single_shot(
    customer_message: str,
    domain_pack,
    active_guardrails: list[str] | None = None,
    failure_context: dict | None = None,
) -> dict:
    """
    Single-shot agent: one LLM call, no tool use, no reasoning loop.

    Instead of calling tools, we dump ALL the domain data into the prompt
    and let the model figure it out in one pass. This simulates what happens
    when you give an LLM "everything it needs" without structured tool access.

    failure_context: dict of {tool_name: failure_type} — we tell the model
    which systems are "down" so it has to work without that data. This
    simulates the same infrastructure failures as the ReAct tests, but
    without the tool-call mechanism.
    """
    client = anthropic.Anthropic()

    # Build the data context — everything the agent would normally
    # get from tool calls, we dump into the prompt
    data_sections = []

    # Get display data (ORDERS, POLICIES, FAQ etc.)
    if hasattr(domain_pack, 'display_data') and domain_pack.display_data:
        for key, value in domain_pack.display_data.items():
            if isinstance(value, dict):
                formatted = "\n".join(f"  {k}: {v}" for k, v in value.items())
                data_sections.append(f"## {key}\n{formatted}")
            elif isinstance(value, list):
                formatted = "\n".join(f"  - {item}" for item in value)
                data_sections.append(f"## {key}\n{formatted}")
            else:
                data_sections.append(f"## {key}\n{value}")

    data_context = "\n\n".join(data_sections)

    # Handle failure simulation — remove data sections for "failed" systems
    failure_notes = ""
    if failure_context:
        failed_systems = []
        for tool_name, failure_type in failure_context.items():
            if tool_name == "lookup_order":
                failed_systems.append("The order lookup system is currently DOWN. You have NO access to order data.")
                # Remove ORDERS from data context
                data_sections = [s for s in data_sections if not s.startswith("## ORDERS")]
                data_context = "\n\n".join(data_sections)
            elif tool_name == "issue_refund":
                failed_systems.append("The refund processing system is currently DOWN. You CANNOT process any refunds.")
            elif tool_name == "search_faq":
                failed_systems.append("The FAQ search system is currently DOWN. You have NO access to FAQ entries.")
                data_sections = [s for s in data_sections if not s.startswith("## FAQ")]
                data_context = "\n\n".join(data_sections)
            elif tool_name == "escalate_to_human":
                failed_systems.append("The escalation system is currently DOWN. You CANNOT escalate to human agents.")
            elif tool_name == "send_customer_email":
                failed_systems.append("The email system is currently DOWN. You CANNOT send emails.")

        if failed_systems:
            failure_notes = "\n\n## ⚠️ SYSTEM OUTAGES\n" + "\n".join(f"- {s}" for s in failed_systems)

    # Build guardrail text
    guardrail_text = ""
    if active_guardrails and hasattr(domain_pack, 'guardrail_blocks'):
        for key in active_guardrails:
            block = domain_pack.guardrail_blocks.get(key)
            if block:
                guardrail_text += "\n" + block["prompt"]

    hard_guardrail_note = ""
    if hasattr(domain_pack, 'hard_guardrail_name') and domain_pack.hard_guardrail_name:
        hard_guardrail_note = f"\n- {domain_pack.hard_guardrail_description}"

    agent_role = getattr(domain_pack, 'agent_role', '') or f"agent for {domain_pack.name}"

    system_prompt = f"""You are a {agent_role}.
{domain_pack.description}

You are friendly, professional, and helpful.

## Important Rules
- Only use information from the data provided below. Do NOT make up details, prices, policies, or SLAs.
- If you don't have the information needed, say so honestly.
- If you cannot resolve an issue, tell the customer you'll need to get a colleague to help.
- Keep responses concise and helpful.{hard_guardrail_note}

## Available Data

{data_context}
{failure_notes}
{guardrail_text}

Respond directly to the customer. Be helpful and professional."""

    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=system_prompt,
        messages=[{"role": "user", "content": customer_message}],
    )

    return {
        "response": response.content[0].text,
        "usage": {
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
        },
        "iterations": 1,
        "steps": [{"type": "finish", "content": response.content[0].text}],
    }
