"""Prompt template registry with versioning and tuning support."""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from langchain_core.prompts import ChatPromptTemplate, PromptTemplate

from prompts.system import SYSTEM_PROMPT


@dataclass
class PromptVersion:
    version: str
    template: str
    description: str = ""
    tuning_notes: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


class PromptRegistry:
    """Central registry for versioned medical prompt templates."""

    def __init__(self) -> None:
        self._prompts: Dict[str, Dict[str, PromptVersion]] = {}
        self._active: Dict[str, str] = {}
        self._load_defaults()

    def register(self, name: str, version: PromptVersion, set_active: bool = True) -> None:
        self._prompts.setdefault(name, {})[version.version] = version
        if set_active:
            self._active[name] = version.version

    def get(self, name: str, version: Optional[str] = None) -> PromptVersion:
        versions = self._prompts.get(name)
        if not versions:
            raise KeyError(f"Unknown prompt: {name}")
        ver = version or self._active[name]
        if ver not in versions:
            raise KeyError(f"Unknown version {ver} for prompt {name}")
        return versions[ver]

    def as_langchain(self, name: str, version: Optional[str] = None) -> PromptTemplate:
        pv = self.get(name, version)
        return PromptTemplate.from_template(pv.template)

    def as_chat(self, name: str, version: Optional[str] = None) -> ChatPromptTemplate:
        """Task template as human message with canonical system prompt."""
        pv = self.get(name, version)
        system = SYSTEM_PROMPT if name != "system" else pv.template
        return ChatPromptTemplate.from_messages(
            [
                ("system", system),
                ("human", pv.template if name != "system" else "{input}"),
            ]
        )

    def set_active(self, name: str, version: str) -> None:
        if version not in self._prompts.get(name, {}):
            raise KeyError(f"Unknown version {version} for prompt {name}")
        self._active[name] = version

    def list_versions(self, name: str) -> list[str]:
        return sorted(self._prompts.get(name, {}).keys())

    def list_prompts(self) -> Dict[str, str]:
        return dict(self._active)

    def _load_defaults(self) -> None:
        from prompts.templates import PROMPT_TEMPLATES

        for name, versions in PROMPT_TEMPLATES.items():
            for pv in versions:
                self.register(name, pv, set_active=(pv.version == versions[-1].version))


_registry: Optional[PromptRegistry] = None


def get_prompt_registry() -> PromptRegistry:
    global _registry
    if _registry is None:
        _registry = PromptRegistry()
    return _registry


def get_prompt(name: str, version: Optional[str] = None) -> PromptVersion:
    return get_prompt_registry().get(name, version)


def reset_prompt_registry() -> None:
    global _registry
    _registry = None
