from __future__ import annotations

import json
from typing import Any

try:
    from .llm_client import LLMClient, LLMConfig, table_generation_instruction
except ImportError:
    from llm_client import LLMClient, LLMConfig, table_generation_instruction


def repair_markdown_table(
    markdown: str,
    schema_plan: dict[str, Any],
    validation_result: dict[str, Any],
    model: str | None = None,
    client: LLMClient | None = None,
) -> str:
    llm_client = client or LLMClient(LLMConfig.from_env(model=model))
    prompt = build_repair_prompt(markdown, schema_plan, validation_result)
    return llm_client.chat([{"role": "user", "content": table_generation_instruction(prompt)}])


def build_repair_prompt(
    markdown: str,
    schema_plan: dict[str, Any],
    validation_result: dict[str, Any],
) -> str:
    schema_json = json.dumps(schema_plan, ensure_ascii=False, indent=2)
    issues_json = json.dumps(validation_result.get("issues") or [], ensure_ascii=False, indent=2)
    return (
        "请修复下面这张 Markdown 表格，使其严格满足 schema 和校验问题要求。\n"
        "只输出修复后的 1 个 Markdown 表格，不要输出解释、标题或额外文本。\n\n"
        f"Schema:\n{schema_json}\n\n"
        f"校验问题:\n{issues_json}\n\n"
        f"原始表格:\n{markdown}"
    )
