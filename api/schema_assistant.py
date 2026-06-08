from __future__ import annotations

import json
import re
from copy import deepcopy
from typing import Any

try:
    from .llm_client import LLMClient, LLMConfig
    from .schema_planner import SchemaPlan
except ImportError:
    from llm_client import LLMClient, LLMConfig
    from schema_planner import SchemaPlan


ALLOWED_FIELD_TYPES = {"string", "number", "integer", "enum", "boolean", "date", "datetime", "phone", "list"}
TYPE_ALIASES = {
    "text": "string",
    "str": "string",
    "float": "number",
    "decimal": "number",
    "double": "number",
    "int": "integer",
    "bool": "boolean",
}


def assist_schema_plan(
    user_request: str,
    base_plan: SchemaPlan,
    model: str | None = None,
    client: LLMClient | None = None,
) -> SchemaPlan:
    llm_client = client or LLMClient(LLMConfig.from_env(model=model))
    prompt = build_schema_assist_prompt(user_request, base_plan)
    content = llm_client.chat([{"role": "user", "content": prompt}])
    suggestion = parse_json_object(content)
    return sanitize_llm_schema_plan(suggestion, base_plan)


def build_schema_assist_prompt(user_request: str, base_plan: SchemaPlan) -> str:
    base_json = json.dumps(base_plan, ensure_ascii=False, indent=2)
    return (
        "你是表格 schema 规划助手。请基于用户需求和已有规则 schema，补充更合适的字段、类型和约束。\n"
        "只输出 JSON，不要输出 Markdown、解释或额外文本。\n"
        "JSON 格式: {\"scenario_label\":\"...\",\"row_count\":10,\"schema\":[{\"name\":\"field_name\",\"label\":\"中文字段\",\"type\":\"string|number|integer|enum|boolean|date|datetime|phone|list\",\"required\":true,\"constraints\":{}}]}\n"
        f"用户需求:\n{user_request}\n"
        f"规则 schema:\n{base_json}"
    )


def parse_json_object(content: str) -> dict[str, Any]:
    text = (content or "").strip()
    fenced = re.search(r"```(?:json)?\s*(\{[\s\S]*?\})\s*```", text)
    if fenced:
        text = fenced.group(1)
    if not text.startswith("{"):
        match = re.search(r"\{[\s\S]*\}", text)
        if match:
            text = match.group(0)
    parsed = json.loads(text)
    if not isinstance(parsed, dict):
        raise ValueError("LLM schema suggestion must be a JSON object")
    return parsed


def sanitize_llm_schema_plan(suggestion: dict[str, Any], base_plan: SchemaPlan) -> SchemaPlan:
    sanitized = deepcopy(base_plan)
    sanitized["source"] = "llm_assisted"
    notes = list(sanitized.get("notes") or [])
    notes.append("已启用 LLM 辅助规划，并对 LLM 输出进行了结构校验、字段去重、类型规范化和约束清洗。")

    scenario_label = str(suggestion.get("scenario_label") or "").strip()
    if scenario_label:
        sanitized["scenario_label"] = scenario_label

    row_count = parse_positive_int(suggestion.get("row_count"))
    if row_count:
        sanitized["row_count"] = row_count

    raw_fields = suggestion.get("schema") or []
    fields = sanitize_fields(raw_fields)
    if fields:
        sanitized["schema"] = fields
    else:
        notes.append("LLM 辅助字段无有效结果，已保留规则 schema 字段。")

    sanitized["notes"] = notes
    return sanitized


def sanitize_fields(raw_fields: Any) -> list[dict[str, Any]]:
    if not isinstance(raw_fields, list):
        return []
    fields: list[dict[str, Any]] = []
    seen_names: set[str] = set()
    seen_labels: set[str] = set()
    for index, raw_field in enumerate(raw_fields, start=1):
        if not isinstance(raw_field, dict):
            continue
        label = str(raw_field.get("label") or raw_field.get("name") or "").strip()
        if not label:
            continue
        name = normalize_field_name(str(raw_field.get("name") or label), index)
        label_key = label.lower()
        if name in seen_names or label_key in seen_labels:
            continue
        seen_names.add(name)
        seen_labels.add(label_key)
        field_type = normalize_field_type(str(raw_field.get("type") or "string"))
        fields.append(
            {
                "name": name,
                "label": label,
                "type": field_type,
                "required": bool(raw_field.get("required", True)),
                "constraints": sanitize_constraints(raw_field.get("constraints"), field_type),
                "example": raw_field.get("example", ""),
            }
        )
    return fields


def normalize_field_name(raw_name: str, index: int) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9_]+", "_", raw_name).strip("_").lower()
    return normalized or f"field_{index}"


def normalize_field_type(raw_type: str) -> str:
    normalized = TYPE_ALIASES.get(raw_type.strip().lower(), raw_type.strip().lower())
    return normalized if normalized in ALLOWED_FIELD_TYPES else "string"


def sanitize_constraints(raw_constraints: Any, field_type: str) -> dict[str, Any]:
    if not isinstance(raw_constraints, dict):
        return {}
    constraints: dict[str, Any] = {}
    enum_values = raw_constraints.get("enum")
    if field_type in {"enum", "boolean"} and isinstance(enum_values, list):
        constraints["enum"] = [str(value).strip() for value in enum_values if str(value).strip()]
    for key in ("min", "max"):
        if key in raw_constraints:
            number = parse_number(raw_constraints[key])
            if number is not None:
                constraints[key] = number
    for key in ("format", "pattern", "unit", "separator"):
        value = str(raw_constraints.get(key) or "").strip()
        if value:
            constraints[key] = value
    examples = raw_constraints.get("examples")
    if isinstance(examples, list):
        values = [str(value).strip() for value in examples if str(value).strip()]
        if values:
            constraints["examples"] = values
    return constraints


def parse_positive_int(value: Any) -> int | None:
    if value is None:
        return None
    match = re.search(r"\d+", str(value))
    if not match:
        return None
    parsed = int(match.group(0))
    return parsed if parsed > 0 else None


def parse_number(value: Any) -> int | float | None:
    match = re.search(r"-?\d+(?:\.\d+)?", str(value))
    if not match:
        return None
    number = float(match.group(0))
    if number.is_integer():
        return int(number)
    return number
