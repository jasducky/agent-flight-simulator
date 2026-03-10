"""
Domain loader — provides a consistent interface for loading domain packs.

Each domain folder contains:
- data.py:      Mock data, tool functions, TOOLS registry, FAQ_ENTRIES
- prompts.py:   BASE_SYSTEM_PROMPT, GUARDRAIL_BLOCKS, build_system_prompt()
- scenarios.py: SCENARIOS list, EVAL_DIMENSIONS dict

The loader imports all of these and returns them as a single DomainPack object.
"""

from dataclasses import dataclass, field
from importlib import import_module
from typing import Any


@dataclass
class DomainPack:
    """Everything needed to run a domain in the flight simulator."""
    # Identity
    name: str
    tagline: str
    description: str
    stakes: str
    colour: str

    # Data
    tools: dict
    faq_entries: dict
    failure_modes: dict

    # Functions
    inject_failure: Any  # callable
    build_system_prompt: Any  # callable

    # Prompt
    base_system_prompt: str
    guardrail_blocks: dict

    # Scenarios
    scenarios: list
    eval_dimensions: dict

    # Domain-specific display data (optional, for "The World" tab)
    display_data: dict = field(default_factory=dict)


# ── Registry of available domains ─────────────────────────────────────────────

DOMAIN_REGISTRY = {
    "oakwood": {
        "module": "domains.oakwood",
        "name": "Oakwood Home & Garden",
        "tagline": "UK garden retailer — customer service",
        "icon": "package",
        "stakes": "Low (financial)",
    },
    "gp_triage": {
        "module": "domains.gp_triage",
        "name": "Greenfield Surgery",
        "tagline": "NHS GP surgery — patient triage",
        "icon": "heart",
        "stakes": "High (health)",
    },
    "estate_agent": {
        "module": "domains.estate_agent",
        "name": "Hartwell & Lane",
        "tagline": "UK lettings agency — property enquiries",
        "icon": "home",
        "stakes": "Medium (legal)",
    },
}


def load_domain(domain_key: str) -> DomainPack:
    """
    Load a domain pack by key.

    Args:
        domain_key: One of the keys in DOMAIN_REGISTRY (e.g. "oakwood").

    Returns:
        DomainPack with all data, tools, prompts, and scenarios loaded.
    """
    if domain_key not in DOMAIN_REGISTRY:
        raise ValueError(f"Unknown domain: {domain_key}. Available: {list(DOMAIN_REGISTRY.keys())}")

    reg = DOMAIN_REGISTRY[domain_key]
    base_module = reg["module"]

    # Import the three domain files
    data_mod = import_module(f"{base_module}.data")
    prompts_mod = import_module(f"{base_module}.prompts")
    scenarios_mod = import_module(f"{base_module}.scenarios")

    # Get domain metadata
    meta = getattr(data_mod, "DOMAIN_META", {})

    # Build display data from whatever the domain exposes
    display_data = {}
    for attr in ["ORDERS", "PATIENTS", "PROPERTIES",
                 "REFUND_POLICIES", "CLINICAL_GUIDELINES", "TENANT_CRITERIA"]:
        if hasattr(data_mod, attr):
            display_data[attr] = getattr(data_mod, attr)

    return DomainPack(
        name=meta.get("name", reg["name"]),
        tagline=meta.get("tagline", reg["tagline"]),
        description=meta.get("description", ""),
        stakes=meta.get("stakes", reg["stakes"]),
        colour=meta.get("colour", "#535353"),
        tools=data_mod.TOOLS,
        faq_entries=data_mod.FAQ_ENTRIES,
        failure_modes=data_mod.FAILURE_MODES,
        inject_failure=data_mod.inject_failure,
        build_system_prompt=prompts_mod.build_system_prompt,
        base_system_prompt=prompts_mod.BASE_SYSTEM_PROMPT,
        guardrail_blocks=prompts_mod.GUARDRAIL_BLOCKS,
        scenarios=scenarios_mod.SCENARIOS,
        eval_dimensions=scenarios_mod.EVAL_DIMENSIONS,
        display_data=display_data,
    )


def list_domains() -> dict:
    """Return the domain registry for UI display."""
    return DOMAIN_REGISTRY
