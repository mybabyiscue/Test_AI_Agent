from __future__ import annotations

from pathlib import Path
import re
from typing import Any

from .config import roles_root


ROLE_FILES: dict[str, str] = {
    "requirement_agent": "requirement_agent.md",
    "testcase_agent": "testcase_agent.md",
    "api_mapper_agent": "api_mapper_agent.md",
    "automation_agent": "automation_agent.md",
}

SECTION_FIELD_MAP: dict[str, str] = {
    "使命": "mission",
    "职责": "responsibilities",
    "不负责什么": "out_of_scope",
    "可读取输入": "input_contract",
    "必须输出": "output_contract",
    "质量门禁": "quality_gates",
    "阻塞条件": "blocking_conditions",
    "禁止事项": "forbidden_actions",
    "交接规则": "handoff_rules",
}


class RoleLoader:
    def __init__(self, root: Path) -> None:
        self._root = root

    @classmethod
    def default(cls) -> "RoleLoader":
        return cls(roles_root())

    def role_path(self, agent_name: str) -> Path:
        return self._root / ROLE_FILES[agent_name]

    def load_markdown(self, agent_name: str) -> str:
        return self.role_path(agent_name).read_text(encoding="utf-8").strip() + "\n"

    def load(self, agent_name: str) -> dict[str, Any]:
        path = self.role_path(agent_name)
        markdown = self.load_markdown(agent_name)
        sections = self._parse_sections(markdown)
        basic = sections.get("基本要求", [])
        profile = {
            "agent_name": agent_name,
            "title": self._parse_title(markdown),
            "language": self._parse_basic_value(basic, "工作语言", default="中文"),
            "strict_mode": self._parse_basic_value(basic, "严格模式", default="开启") == "开启",
            "mission": self._collapse_single_text(sections.get("使命", [])),
            "responsibilities": sections.get("职责", []),
            "out_of_scope": sections.get("不负责什么", []),
            "input_contract": sections.get("可读取输入", []),
            "output_contract": sections.get("必须输出", []),
            "quality_gates": sections.get("质量门禁", []),
            "blocking_conditions": sections.get("阻塞条件", []),
            "forbidden_actions": sections.get("禁止事项", []),
            "handoff_rules": sections.get("交接规则", []),
            "role_markdown_path": str(path),
            "role_markdown": markdown,
        }
        return profile

    def _parse_title(self, markdown: str) -> str:
        first_line = markdown.splitlines()[0].strip()
        if first_line.startswith("# "):
            return first_line[2:].strip()
        raise ValueError("Role markdown missing level-1 title.")

    def _parse_basic_value(self, items: list[str], key: str, *, default: str) -> str:
        prefix = f"{key}："
        for item in items:
            if item.startswith(prefix):
                return item.removeprefix(prefix).strip()
        return default

    def _collapse_single_text(self, items: list[str]) -> str:
        return "\n".join(item.strip() for item in items if item.strip()).strip()

    def _parse_sections(self, markdown: str) -> dict[str, list[str]]:
        sections: dict[str, list[str]] = {}
        current_section: str | None = None
        paragraph_buffer: list[str] = []
        for raw_line in markdown.splitlines()[1:]:
            line = raw_line.rstrip()
            heading = re.match(r"^##\s+(.+?)\s*$", line)
            if heading:
                self._flush_paragraph(sections, current_section, paragraph_buffer)
                current_section = heading.group(1).strip()
                sections.setdefault(current_section, [])
                continue
            if current_section is None:
                continue
            stripped = line.strip()
            if not stripped:
                self._flush_paragraph(sections, current_section, paragraph_buffer)
                continue
            if stripped.startswith("- "):
                self._flush_paragraph(sections, current_section, paragraph_buffer)
                sections[current_section].append(stripped[2:].strip())
                continue
            paragraph_buffer.append(stripped)
        self._flush_paragraph(sections, current_section, paragraph_buffer)
        return sections

    def _flush_paragraph(
        self,
        sections: dict[str, list[str]],
        current_section: str | None,
        paragraph_buffer: list[str],
    ) -> None:
        if current_section and paragraph_buffer:
            sections[current_section].append(" ".join(paragraph_buffer).strip())
            paragraph_buffer.clear()
