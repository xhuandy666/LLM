from __future__ import annotations

import re
from typing import Any


ValidationResult = dict[str, Any]


def validate_markdown_table(markdown: str, schema_plan: dict[str, Any]) -> ValidationResult:
    parsed_table = parse_markdown_table(markdown)
    issues: list[dict[str, Any]] = []
    expected_row_count = int(schema_plan.get("row_count") or 0)
    schema = schema_plan.get("schema") or []

    if not parsed_table:
        issues.append(
            build_issue(
                "parse_error",
                "未识别到 Markdown 表格，请确认模型输出的是标准 Markdown 表格。",
            )
        )
        return build_result(schema_plan, [], [], issues, expected_row_count)

    headers = parsed_table["headers"]
    rows = parsed_table["rows"]
    header_index = {normalize_header(header): index for index, header in enumerate(headers)}

    if expected_row_count and len(rows) != expected_row_count:
        issues.append(
            build_issue(
                "row_count",
                f"目标行数为 {expected_row_count}，实际识别到 {len(rows)} 行数据。",
            )
        )

    for field in schema:
        field_index = find_field_index(field, header_index)
        label = field.get("label")
        if field.get("required") and field_index is None:
            issues.append(
                build_issue(
                    "missing_column",
                    f"缺少必填字段「{label}」。",
                    field=field.get("name"),
                    field_label=label,
                )
            )

    for row_number, row in enumerate(rows, start=1):
        for field in schema:
            label = field.get("label")
            field_index = find_field_index(field, header_index)
            if field_index is None:
                continue
            value = get_cell(row, field_index)
            if field.get("required") and not value.strip():
                issues.append(
                    build_issue(
                        "missing_value",
                        f"第 {row_number} 行字段「{label}」为空。",
                        row=row_number,
                        field=field.get("name"),
                        field_label=label,
                    )
                )
                continue
            validate_field_value(issues, row_number, field, value)

    return build_result(schema_plan, headers, rows, issues, expected_row_count)


def parse_markdown_table(markdown: str) -> dict[str, Any] | None:
    lines = [line.strip() for line in markdown.splitlines() if line.strip()]
    table_lines = [line for line in lines if line.startswith("|") and line.endswith("|")]
    if len(table_lines) < 2:
        return None

    headers = split_table_row(table_lines[0])
    separator = split_table_row(table_lines[1])
    if not headers or not is_separator_row(separator):
        return None

    rows = [split_table_row(line) for line in table_lines[2:]]
    rows = [row for row in rows if row]
    return {"headers": headers, "rows": rows}


def split_table_row(row: str) -> list[str]:
    return [cell.strip() for cell in row.strip().strip("|").split("|")]


def is_separator_row(cells: list[str]) -> bool:
    if not cells:
        return False
    return all(re.fullmatch(r":?-{3,}:?", cell.strip()) for cell in cells)


def normalize_header(header: str | None) -> str:
    return (header or "").strip().lower()


def find_field_index(field: dict[str, Any], header_index: dict[str, int]) -> int | None:
    candidates = [
        field.get("label"),
        field.get("name"),
    ]
    for candidate in candidates:
        normalized = normalize_header(candidate)
        if normalized in header_index:
            return header_index[normalized]
    return None


def validate_field_value(
    issues: list[dict[str, Any]],
    row_number: int,
    field: dict[str, Any],
    raw_value: str,
) -> None:
    field_type = field.get("type")
    constraints = field.get("constraints") or {}
    label = field.get("label")
    value = raw_value.strip()

    if field_type in {"enum", "boolean"}:
        allowed_values = constraints.get("enum") or boolean_allowed_values(constraints)
        if allowed_values and value not in allowed_values:
            issues.append(
                build_issue(
                    "enum_value",
                    f"第 {row_number} 行字段「{label}」的值「{value}」不在允许范围: {', '.join(allowed_values)}。",
                    row=row_number,
                    field=field.get("name"),
                    field_label=label,
                    value=value,
                )
            )

    if field_type in {"number", "integer"}:
        number = parse_number(value)
        if number is None:
            issues.append(
                build_issue(
                    "number_format",
                    f"第 {row_number} 行字段「{label}」的值「{value}」不是有效数字。",
                    row=row_number,
                    field=field.get("name"),
                    field_label=label,
                    value=value,
                )
            )
            return
        if field_type == "integer" and not float(number).is_integer():
            issues.append(
                build_issue(
                    "integer_format",
                    f"第 {row_number} 行字段「{label}」的值「{value}」不是整数。",
                    row=row_number,
                    field=field.get("name"),
                    field_label=label,
                    value=value,
                )
            )
        validate_number_range(issues, row_number, field, number, value, constraints)


def validate_number_range(
    issues: list[dict[str, Any]],
    row_number: int,
    field: dict[str, Any],
    number: float,
    raw_value: str,
    constraints: dict[str, Any],
) -> None:
    label = field.get("label")
    min_value = constraints.get("min")
    max_value = constraints.get("max")
    if min_value is not None and number < float(min_value):
        issues.append(
            build_issue(
                "number_range",
                f"第 {row_number} 行字段「{label}」的值「{raw_value}」小于最小值 {min_value}。",
                row=row_number,
                field=field.get("name"),
                field_label=label,
                value=raw_value,
            )
        )
    if max_value is not None and number > float(max_value):
        issues.append(
            build_issue(
                "number_range",
                f"第 {row_number} 行字段「{label}」的值「{raw_value}」大于最大值 {max_value}。",
                row=row_number,
                field=field.get("name"),
                field_label=label,
                value=raw_value,
            )
        )


def boolean_allowed_values(constraints: dict[str, Any]) -> list[str]:
    values = []
    if "true_label" in constraints:
        values.append(str(constraints["true_label"]))
    if "false_label" in constraints:
        values.append(str(constraints["false_label"]))
    return values


def parse_number(value: str) -> float | None:
    cleaned = (
        value.replace(",", "")
        .replace("￥", "")
        .replace("¥", "")
        .replace("元", "")
        .strip()
    )
    match = re.search(r"-?\d+(?:\.\d+)?", cleaned)
    if not match:
        return None
    try:
        return float(match.group(0))
    except ValueError:
        return None


def get_cell(row: list[str], index: int) -> str:
    if index >= len(row):
        return ""
    return row[index]


def build_issue(
    issue_type: str,
    message: str,
    row: int | None = None,
    field: str | None = None,
    field_label: str | None = None,
    value: str | None = None,
) -> dict[str, Any]:
    issue = {"type": issue_type, "message": message}
    if row is not None:
        issue["row"] = row
    if field:
        issue["field"] = field
    if field_label:
        issue["field_label"] = field_label
    if value is not None:
        issue["value"] = value
    return issue


def build_result(
    schema_plan: dict[str, Any],
    headers: list[str],
    rows: list[list[str]],
    issues: list[dict[str, Any]],
    expected_row_count: int,
) -> ValidationResult:
    passed = len(issues) == 0
    summary = {
        "scenario": schema_plan.get("scenario"),
        "scenario_label": schema_plan.get("scenario_label"),
        "row_count": {
            "expected": expected_row_count,
            "actual": len(rows),
        },
        "column_count": len(headers),
        "issue_count": len(issues),
    }
    return {
        "passed": passed,
        "summary": summary,
        "issues": issues,
        "report": build_report(summary, issues, passed),
    }


def build_report(summary: dict[str, Any], issues: list[dict[str, Any]], passed: bool) -> str:
    status = "校验通过" if passed else "校验未通过"
    row_count = summary["row_count"]
    lines = [
        f"{status}: {summary.get('scenario_label') or '业务表格'}",
        f"- 目标行数: {row_count['expected']}",
        f"- 实际行数: {row_count['actual']}",
        f"- 字段数量: {summary['column_count']}",
        f"- 问题数量: {summary['issue_count']}",
    ]
    if issues:
        lines.append("- 主要问题:")
        for issue in issues[:5]:
            lines.append(f"  - {issue['message']}")
    else:
        lines.append("- 结论: 生成结果满足当前 schema 的行数、字段和约束要求。")
    return "\n".join(lines)
