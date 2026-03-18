"""
ReAct agent loop — domain-agnostic.

Based on the ReAct pattern (Reason + Act):
1. Send customer message + conversation history to Claude
2. Claude responds with Thought → Action (tool call) or Thought → FINISH
3. If Action: parse it, call the tool, feed the Observation back
4. Repeat until FINISH or max iterations

This file can run standalone in the terminal for testing (Phase 1)
or be imported by app.py for the Streamlit frontend (Phase 2+).

The agent loop itself is domain-agnostic — it accepts tools, prompts,
and failure injection as parameters. Defaults to Oakwood (backward compat).
"""

import re
import os
import inspect
import anthropic
from dotenv import load_dotenv

# Default imports for backward compatibility (standalone terminal mode)
from tools import TOOLS as _DEFAULT_TOOLS
from tools import inject_failure as _default_inject_failure
from prompts import build_system_prompt as _default_build_system_prompt

load_dotenv()

MAX_ITERATIONS = 10
MODEL = "claude-haiku-4-5-20251001"


def format_tool_descriptions(tools_registry: dict | None = None) -> str:
    """Format the tool registry into a string for the system prompt."""
    tools = tools_registry or _DEFAULT_TOOLS
    lines = []
    for name, info in tools.items():
        params = ", ".join(f'{k}: {v}' for k, v in info["parameters"].items())
        lines.append(f"- {name}({params}): {info['description']}")
    return "\n".join(lines)


def parse_action(text: str) -> tuple[str, dict] | None:
    """
    Parse an Action line like: Action: tool_name(param1="value1", param2="value2")
    Returns (tool_name, {param1: value1, ...}) or None if no action found.

    Handles multi-line quoted values (e.g. email bodies with newlines).
    """
    # Match tool name after Action:, then capture everything up to the last )
    match = re.search(r'Action:\s*(\w+)\((.+)\)', text, re.DOTALL)
    if not match:
        return None

    tool_name = match.group(1)
    params_str = match.group(2)

    # Parse key="value" pairs — allow newlines and escaped quotes inside values
    params = {}
    for param_match in re.finditer(r'(\w+)\s*=\s*"((?:[^"\\]|\\.)*)"', params_str, re.DOTALL):
        params[param_match.group(1)] = param_match.group(2)

    # Also handle numeric values: amount=18.99
    for param_match in re.finditer(r'(\w+)\s*=\s*([0-9]+\.?[0-9]*)\b', params_str):
        key = param_match.group(1)
        if key not in params:  # Don't overwrite string matches
            params[key] = float(param_match.group(2))

    return tool_name, params


def parse_finish(text: str) -> str | None:
    """Extract the final response after FINISH:"""
    match = re.search(r'FINISH:\s*(.+)', text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None


def call_tool(
    tool_name: str,
    params: dict,
    guardrails_enabled: bool = True,
    failure_config: dict | None = None,
    tools_registry: dict | None = None,
    failure_injector=None,
) -> str:
    """Call a tool function by name with the given parameters."""
    tools = tools_registry or _DEFAULT_TOOLS
    _inject = failure_injector or _default_inject_failure

    # Check failure injection first
    if failure_config:
        failure_msg = _inject(tool_name, failure_config)
        if failure_msg:
            return failure_msg

    tool = tools.get(tool_name)
    if not tool:
        return f"Error: Unknown tool '{tool_name}'. Available tools: {', '.join(tools.keys())}"

    func = tool["function"]

    # Inject guardrails_enabled for any tool that accepts it
    # (e.g. Oakwood's issue_refund, GP's book_appointment)
    sig = inspect.signature(func)
    if "guardrails_enabled" in sig.parameters:
        params["guardrails_enabled"] = guardrails_enabled

    try:
        return func(**params)
    except TypeError as e:
        return f"Error calling {tool_name}: {e}"


def run_agent(
    customer_message: str,
    active_guardrails: list[str] | None = None,
    hard_guardrail: bool = True,
    failure_config: dict | None = None,
    tools_registry: dict | None = None,
    prompt_builder=None,
    failure_injector=None,
) -> dict:
    """
    Run the ReAct agent loop.

    Args:
        customer_message: The customer's message.
        active_guardrails: List of soft guardrail keys to activate in the prompt.
        hard_guardrail: Whether the domain's hard guardrail is active (e.g. £50 refund cap, emergency escalation).
        failure_config: Dict mapping tool names to failure modes for chaos testing.
        tools_registry: Domain-specific tools dict (defaults to Oakwood).
        prompt_builder: Domain-specific build_system_prompt function.
        failure_injector: Domain-specific inject_failure function.

    Returns:
        dict with keys:
            - response: The agent's final response to the customer
            - steps: List of {type, content} dicts showing the reasoning trace
            - usage: Token usage stats {input_tokens, output_tokens}
            - iterations: Number of loop iterations
    """
    _build_prompt = prompt_builder or _default_build_system_prompt
    client = anthropic.Anthropic()
    tool_descriptions = format_tool_descriptions(tools_registry)
    system_prompt = _build_prompt(tool_descriptions, active_guardrails)

    steps = []
    messages = [{"role": "user", "content": customer_message}]
    total_input_tokens = 0
    total_output_tokens = 0

    for i in range(MAX_ITERATIONS):
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            system=system_prompt,
            messages=messages,
            stop_sequences=["Observation:"],
        )

        total_input_tokens += response.usage.input_tokens
        total_output_tokens += response.usage.output_tokens

        assistant_text = response.content[0].text

        # Check for Action FIRST — if both Action and FINISH, execute the tool
        action = parse_action(assistant_text)

        if action:
            thought_match = re.search(r'Thought:\s*(.+?)(?=Action:)', assistant_text, re.DOTALL)
            if thought_match:
                steps.append({"type": "thought", "content": thought_match.group(1).strip()})
        elif parse_finish(assistant_text):
            final_response = parse_finish(assistant_text)
            thought_match = re.search(r'Thought:\s*(.+?)(?=FINISH:)', assistant_text, re.DOTALL)
            if thought_match:
                steps.append({"type": "thought", "content": thought_match.group(1).strip()})
            steps.append({"type": "finish", "content": final_response})
            return {
                "response": final_response,
                "steps": steps,
                "usage": {"input_tokens": total_input_tokens, "output_tokens": total_output_tokens},
                "iterations": i + 1,
            }
        else:
            thought_match = re.search(r'Thought:\s*(.+?)$', assistant_text, re.DOTALL)
            if thought_match:
                steps.append({"type": "thought", "content": thought_match.group(1).strip()})

        if action:
            tool_name, params = action
            steps.append({"type": "action", "content": f"{tool_name}({params})"})

            observation = call_tool(tool_name, params, guardrails_enabled=hard_guardrail, failure_config=failure_config, tools_registry=tools_registry, failure_injector=failure_injector)
            steps.append({"type": "observation", "content": observation})

            # Add assistant response and observation to conversation
            messages.append({"role": "assistant", "content": assistant_text})
            messages.append({"role": "user", "content": f"Observation: {observation}"})
        else:
            # No action and no finish — treat the whole response as the answer
            steps.append({"type": "finish", "content": assistant_text})
            return {
                "response": assistant_text,
                "steps": steps,
                "usage": {
                    "input_tokens": total_input_tokens,
                    "output_tokens": total_output_tokens,
                },
                "iterations": i + 1,
            }

    # Max iterations reached
    return {
        "response": "I apologise, but I'm having difficulty resolving this. Let me escalate to a human agent.",
        "steps": steps,
        "usage": {
            "input_tokens": total_input_tokens,
            "output_tokens": total_output_tokens,
        },
        "iterations": MAX_ITERATIONS,
    }


def run_agent_streaming(
    customer_message: str,
    active_guardrails: list[str] | None = None,
    hard_guardrail: bool = True,
    failure_config: dict | None = None,
    tools_registry: dict | None = None,
    prompt_builder=None,
    failure_injector=None,
):
    """
    Generator version of run_agent — yields each step as it happens.

    Yields:
        dict with keys: type ("thought"|"action"|"observation"|"finish"|"done"), content, and
        for "done": full result dict with response, steps, usage, iterations.
    """
    _build_prompt = prompt_builder or _default_build_system_prompt
    client = anthropic.Anthropic()
    tool_descriptions = format_tool_descriptions(tools_registry)
    system_prompt = _build_prompt(tool_descriptions, active_guardrails)

    steps = []
    messages = [{"role": "user", "content": customer_message}]
    total_input_tokens = 0
    total_output_tokens = 0

    for i in range(MAX_ITERATIONS):
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            system=system_prompt,
            messages=messages,
            stop_sequences=["Observation:"],
        )

        total_input_tokens += response.usage.input_tokens
        total_output_tokens += response.usage.output_tokens

        assistant_text = response.content[0].text

        # Check for Action FIRST — if text has both Action and FINISH,
        # we must execute the tool before finishing (prevent hallucinated results)
        action = parse_action(assistant_text)

        if action:
            # Has an action — extract thought before the Action line
            thought_match = re.search(r'Thought:\s*(.+?)(?=Action:)', assistant_text, re.DOTALL)
            if thought_match:
                step = {"type": "thought", "content": thought_match.group(1).strip()}
                steps.append(step)
                yield step
        elif parse_finish(assistant_text):
            # FINISH with no action — done
            final_response = parse_finish(assistant_text)
            thought_match = re.search(r'Thought:\s*(.+?)(?=FINISH:)', assistant_text, re.DOTALL)
            if thought_match:
                step = {"type": "thought", "content": thought_match.group(1).strip()}
                steps.append(step)
                yield step

            step = {"type": "finish", "content": final_response}
            steps.append(step)
            yield step

            yield {
                "type": "done",
                "response": final_response,
                "steps": steps,
                "usage": {"input_tokens": total_input_tokens, "output_tokens": total_output_tokens},
                "iterations": i + 1,
            }
            return
        else:
            # No action, no FINISH — extract any thought and check again
            thought_match = re.search(r'Thought:\s*(.+?)$', assistant_text, re.DOTALL)
            if thought_match:
                step = {"type": "thought", "content": thought_match.group(1).strip()}
                steps.append(step)
                yield step

        # Execute action if found
        if action:
            tool_name, params = action
            step = {"type": "action", "content": f"{tool_name}({params})"}
            steps.append(step)
            yield step

            observation = call_tool(tool_name, params, guardrails_enabled=hard_guardrail, failure_config=failure_config, tools_registry=tools_registry, failure_injector=failure_injector)
            step = {"type": "observation", "content": observation}
            steps.append(step)
            yield step

            messages.append({"role": "assistant", "content": assistant_text})
            messages.append({"role": "user", "content": f"Observation: {observation}"})
        else:
            step = {"type": "finish", "content": assistant_text}
            steps.append(step)
            yield step

            yield {
                "type": "done",
                "response": assistant_text,
                "steps": steps,
                "usage": {"input_tokens": total_input_tokens, "output_tokens": total_output_tokens},
                "iterations": i + 1,
            }
            return

    # Max iterations reached
    fallback = "I apologise, but I'm having difficulty resolving this. Let me escalate to a human agent."
    yield {
        "type": "done",
        "response": fallback,
        "steps": steps,
        "usage": {"input_tokens": total_input_tokens, "output_tokens": total_output_tokens},
        "iterations": MAX_ITERATIONS,
    }


# ── Terminal mode (Phase 1 testing) ────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("Oakwood Home & Garden — Customer Service Agent")
    print("Type 'quit' to exit")
    print("=" * 60)

    while True:
        print()
        user_input = input("Customer: ").strip()
        if user_input.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break

        print("\nAgent is thinking...\n")
        result = run_agent(user_input)

        # Show the reasoning trace
        print("─── Reasoning Trace ───")
        for step in result["steps"]:
            prefix = {
                "thought": "💭 Thought",
                "action": "🔧 Action",
                "observation": "👁 Observation",
                "finish": "✅ Final Response",
            }.get(step["type"], step["type"])
            print(f"\n{prefix}:")
            print(f"  {step['content']}")

        print("\n─── Stats ───")
        print(f"  Iterations: {result['iterations']}")
        print(f"  Tokens: {result['usage']['input_tokens']} in / {result['usage']['output_tokens']} out")
