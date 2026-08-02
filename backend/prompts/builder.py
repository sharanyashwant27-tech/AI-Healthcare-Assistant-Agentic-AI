"""Compose final prompts: system + dynamic + few-shot + task template."""

from typing import Any, Dict, Optional

from prompts.dynamic import format_dynamic_block
from prompts.few_shot import format_few_shot_block
from prompts.registry import get_prompt_registry
from prompts.system import SYSTEM_PROMPT


def build_prompt(
    name: str,
    variables: Optional[Dict[str, Any]] = None,
    *,
    dynamic_payload: Optional[Dict[str, Any]] = None,
    include_few_shot: bool = False,
    include_system: bool = True,
    version: Optional[str] = None,
) -> str:
    """Render a named task prompt with optional system, dynamic, and few-shot layers."""
    variables = {k: ("" if v is None else v) for k, v in (variables or {}).items()}
    registry = get_prompt_registry()
    task = registry.as_langchain(name, version).format(**variables)

    parts = []
    if include_system:
        parts.append(SYSTEM_PROMPT)
    if dynamic_payload is not None:
        parts.append(format_dynamic_block(dynamic_payload))
    if include_few_shot:
        parts.append(format_few_shot_block())
    parts.append(task)
    return "\n\n".join(parts)


def describe_prompt_engineering() -> Dict[str, Any]:
    from prompts.few_shot import few_shot_catalog
    from prompts.dynamic import DYNAMIC_PROMPT_DIMENSIONS
    from prompts.system import SYSTEM_PROMPT_RULES
    from prompts.templates import PROMPT_TEMPLATES, PROMPT_TUNING_EXAMPLES

    return {
        "system_prompt": SYSTEM_PROMPT,
        "system_rules": SYSTEM_PROMPT_RULES,
        "templates": {
            name: [
                {
                    "version": pv.version,
                    "description": pv.description,
                    "tuning_notes": pv.tuning_notes,
                    "template": pv.template,
                }
                for pv in versions
            ]
            for name, versions in PROMPT_TEMPLATES.items()
        },
        "prompt_tuning": {
            "few_shot_chain": [
                "Symptom",
                "Medical Condition",
                "Doctor Recommendation",
                "Hospital Department",
            ],
            "examples": few_shot_catalog(),
            "history": PROMPT_TUNING_EXAMPLES,
        },
        "dynamic_prompting": {
            "chain": [
                "Patient Type",
                "Age",
                "Disease",
                "Country",
                "Hospital Protocol",
            ],
            "dimensions": DYNAMIC_PROMPT_DIMENSIONS,
        },
    }
