from __future__ import annotations

from typing import Any, Callable

try:
    from .ESpeed import get_response
    from .schema_assistant import assist_schema_plan
    from .schema_planner import plan_schema
    from .table_repair import repair_markdown_table
    from .table_validator import validate_markdown_table
except ImportError:
    from ESpeed import get_response
    from schema_assistant import assist_schema_plan
    from schema_planner import plan_schema
    from table_repair import repair_markdown_table
    from table_validator import validate_markdown_table


Generator = Callable[..., list[dict[str, str]]]
Repairer = Callable[..., str]
MessageReplacer = Callable[[str, str], list[dict[str, str]]]
SchemaAssister = Callable[..., dict[str, Any]]


def generate_table_with_quality_loop(
    message: str,
    model: str | None = None,
    session_id: str = "default",
    template_id: str | None = None,
    max_repair_attempts: int = 1,
    use_llm_assist: bool = True,
    generator: Generator = get_response,
    repairer: Repairer = repair_markdown_table,
    message_replacer: MessageReplacer | None = None,
    schema_assister: SchemaAssister = assist_schema_plan,
) -> dict[str, Any]:
    schema_plan = plan_schema(message, template_id=template_id)
    if use_llm_assist:
        schema_plan = schema_assister(message, schema_plan, model=model)
    messages = generator(
        message,
        model=model,
        session_id=session_id,
        schema_plan=schema_plan,
    )
    markdown = get_last_assistant_content(messages)
    validation_result = validate_markdown_table(markdown, schema_plan)
    repair_attempts = 0

    while not validation_result["passed"] and repair_attempts < max_repair_attempts:
        repair_attempts += 1
        markdown = repairer(markdown, schema_plan, validation_result, model=model)
        validation_result = validate_markdown_table(markdown, schema_plan)
        if message_replacer:
            messages = message_replacer(session_id, markdown)
        else:
            messages = replace_last_assistant_content(messages, markdown)

    status = "passed" if validation_result["passed"] else "repair_failed"
    return {
        "status": status,
        "messages": messages,
        "schema_plan": schema_plan,
        "validation_result": validation_result,
        "repair_attempts": repair_attempts,
    }


def get_last_assistant_content(messages: list[dict[str, str]]) -> str:
    for message in reversed(messages):
        if message.get("role") == "assistant":
            return message.get("content") or ""
    return ""


def replace_last_assistant_content(
    messages: list[dict[str, str]],
    content: str,
) -> list[dict[str, str]]:
    copied = [dict(message) for message in messages]
    for message in reversed(copied):
        if message.get("role") == "assistant":
            message["content"] = content
            return copied
    copied.append({"role": "assistant", "content": content})
    return copied
