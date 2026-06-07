from __future__ import annotations

import json
import re
from copy import deepcopy
from typing import Any

try:
    from .business_templates import get_template
except ImportError:
    from business_templates import get_template


SchemaPlan = dict[str, Any]

DEFAULT_ROW_COUNT = 10

SCENARIO_KEYWORDS = {
    "ecommerce_order": ("订单", "电商", "支付", "商品", "收货"),
    "student_profile": ("学生", "班级", "学号", "成绩", "住宿"),
    "crm_leads": ("crm", "销售", "线索", "客户", "跟进"),
    "recruiting_candidates": ("招聘", "候选人", "面试", "应聘", "岗位"),
}


def plan_schema(user_request: str, template_id: str | None = None) -> SchemaPlan:
    request_text = (user_request or "").strip()
    selected_template_id = template_id or infer_template_id(request_text)
    template = get_template(selected_template_id)

    if template:
        source = "template" if template_id else "inferred_template"
        schema = deepcopy(template["fields"])
        scenario = template["id"]
        scenario_label = template["name"]
    else:
        source = "custom"
        schema = build_custom_schema(request_text)
        scenario = "custom"
        scenario_label = infer_custom_label(request_text)

    row_count = parse_row_count(request_text)
    notes: list[str] = []
    if not request_text:
        notes.append("未输入自然语言需求，使用模板默认字段和默认行数。")
    if source == "custom":
        notes.append("未匹配到内置模板，已根据显式字段列表生成自定义 schema。")

    apply_request_constraints(schema, request_text)

    return {
        "scenario": scenario,
        "scenario_label": scenario_label,
        "row_count": row_count,
        "schema": schema,
        "source": source,
        "notes": notes,
    }


def infer_template_id(user_request: str) -> str | None:
    text = user_request.lower()
    for template_id, keywords in SCENARIO_KEYWORDS.items():
        if any(keyword.lower() in text for keyword in keywords):
            return template_id
    return None


def parse_row_count(user_request: str) -> int:
    patterns = [
        r"(?:生成|创建|构造|造|需要|输出|做)\s*(\d{1,5})\s*(?:条|行|个|份|组)",
        r"(\d{1,5})\s*(?:条|行)\s*(?:数据|记录|表格)?",
    ]
    for pattern in patterns:
        match = re.search(pattern, user_request)
        if match:
            return max(1, int(match.group(1)))
    return DEFAULT_ROW_COUNT


def build_custom_schema(user_request: str) -> list[dict[str, Any]]:
    labels = extract_field_labels(user_request)
    if not labels:
        labels = ["名称", "类型", "状态", "创建时间"]
    return [
        {
            "name": normalize_field_name(label, index),
            "label": label,
            "type": infer_field_type(label),
            "required": True,
            "constraints": default_constraints_for_label(label),
            "example": "",
        }
        for index, label in enumerate(labels, start=1)
    ]


def extract_field_labels(user_request: str) -> list[str]:
    match = re.search(r"(?:字段包括|包含字段|列包括|包含列)([^。；;\n]+)", user_request)
    if not match:
        return []
    raw_labels = match.group(1)
    labels = [
        label.strip(" ，,、：:。")
        for label in re.split(r"[、,，/]+", raw_labels)
        if label.strip(" ，,、：:。")
    ]
    return labels


def normalize_field_name(label: str, index: int) -> str:
    ascii_name = re.sub(r"[^a-zA-Z0-9_]+", "_", label).strip("_").lower()
    return ascii_name or f"field_{index}"


def infer_field_type(label: str) -> str:
    if any(keyword in label for keyword in ("是否", "通过", "到场")):
        return "boolean"
    if any(keyword in label for keyword in ("金额", "薪资", "价格", "成绩", "年龄", "数量")):
        return "number"
    if any(keyword in label for keyword in ("时间", "日期")):
        return "date"
    if any(keyword in label for keyword in ("状态", "渠道", "等级", "性别", "类型")):
        return "enum"
    if "手机号" in label or "电话" in label:
        return "phone"
    return "string"


def default_constraints_for_label(label: str) -> dict[str, Any]:
    field_type = infer_field_type(label)
    if field_type == "boolean":
        return {"enum": ["是", "否"]}
    if field_type == "phone":
        return {"pattern": "中国大陆11位手机号"}
    if field_type == "number":
        return {}
    if field_type == "date":
        return {"format": "YYYY-MM-DD"}
    if field_type == "enum":
        return {"enum": []}
    return {}


def infer_custom_label(user_request: str) -> str:
    match = re.search(r"(?:生成|创建|构造|造|需要|输出|做)\s*\d{0,5}\s*(?:条|行|个|份|组)?\s*([^，。；;\n]+)", user_request)
    if match:
        label = match.group(1).strip()
        if label:
            return label
    return "自定义业务表格"


def apply_request_constraints(schema: list[dict[str, Any]], user_request: str) -> None:
    apply_number_ranges(schema, user_request)
    apply_enum_overrides(schema, user_request)


def apply_number_ranges(schema: list[dict[str, Any]], user_request: str) -> None:
    range_pattern = re.compile(
        r"(金额|预计金额|价格|费用|薪资|期望薪资|成绩|年龄)[^0-9]{0,12}"
        r"(\d+(?:\.\d+)?)\s*(?:-|~|到|至)\s*(\d+(?:\.\d+)?)"
    )
    for match in range_pattern.finditer(user_request):
        label_keyword = match.group(1)
        min_value = parse_number(match.group(2))
        max_value = parse_number(match.group(3))
        for field in schema:
            if field["type"] not in {"number", "integer"}:
                continue
            if label_keyword in field["label"] or label_keyword in field["name"]:
                constraints = field.setdefault("constraints", {})
                constraints["min"] = min_value
                constraints["max"] = max_value


def apply_enum_overrides(schema: list[dict[str, Any]], user_request: str) -> None:
    for field in schema:
        if field["type"] not in {"enum", "boolean"}:
            continue
        enum_values = parse_enum_values(user_request, field["label"])
        if enum_values:
            field.setdefault("constraints", {})["enum"] = enum_values


def parse_enum_values(user_request: str, label: str) -> list[str]:
    pattern = re.compile(
        rf"{re.escape(label)}[^，。；;\n]*?(?:包括|包含|为|有)\s*([^。；;\n]+)"
    )
    match = pattern.search(user_request)
    if not match:
        return []
    raw_values = re.sub(r"(?:等|之一)$", "", match.group(1).strip())
    values = [
        value.strip(" ，,、/：:")
        for value in re.split(r"[、,，/]+", raw_values)
        if value.strip(" ，,、/：:")
    ]
    return values


def parse_number(raw_value: str) -> int | float:
    value = float(raw_value)
    if value.is_integer():
        return int(value)
    return value


def build_generation_context(user_request: str, schema_plan: SchemaPlan | None) -> str:
    if not schema_plan:
        return user_request

    compact_schema = [
        {
            "name": field["name"],
            "label": field["label"],
            "type": field["type"],
            "required": field.get("required", False),
            "constraints": field.get("constraints", {}),
        }
        for field in schema_plan["schema"]
    ]
    schema_json = json.dumps(compact_schema, ensure_ascii=False, indent=2)
    return (
        f"用户需求: {user_request}\n"
        f"业务场景: {schema_plan['scenario_label']} ({schema_plan['scenario']})\n"
        f"目标行数: {schema_plan['row_count']}\n"
        "请严格按照以下 schema 生成 Markdown 表格，字段顺序、字段含义、枚举值、数值范围要与 schema 保持一致。\n"
        "表头优先使用 schema 中的中文 label，不要使用英文 name 作为表头。\n"
        f"Schema:\n{schema_json}\n"
        "输出要求:\n"
        f"1. 只输出 1 个 Markdown 表格。\n"
        f"2. 表格数据行数必须为 {schema_plan['row_count']} 行，不包含表头。\n"
        "3. 不要输出解释、标题或额外说明。"
    )
