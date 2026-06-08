from __future__ import annotations

import csv
import io
import json
from html import escape
from typing import Any

try:
    from .table_validator import parse_markdown_table
except ImportError:
    from table_validator import parse_markdown_table


def export_table(markdown: str, schema_plan: dict[str, Any], export_format: str) -> dict[str, str]:
    parsed = parse_markdown_table(markdown)
    if not parsed:
        raise ValueError("markdown table is required")
    normalized_format = (export_format or "json").strip().lower()
    headers = parsed["headers"]
    rows = parsed["rows"]
    if normalized_format == "json":
        return export_json(headers, rows, schema_plan)
    if normalized_format == "schema":
        return export_schema(schema_plan)
    if normalized_format == "csv":
        return export_csv(headers, rows)
    if normalized_format in {"excel", "xls"}:
        return export_excel_html(headers, rows)
    raise ValueError(f"unsupported export format: {export_format}")


def export_json(headers: list[str], rows: list[list[str]], schema_plan: dict[str, Any]) -> dict[str, str]:
    payload = {
        "schema": schema_plan,
        "rows": rows_to_objects(headers, rows),
    }
    return {
        "filename": "datasheet.json",
        "content_type": "application/json",
        "content": json.dumps(payload, ensure_ascii=False, indent=2),
    }


def export_schema(schema_plan: dict[str, Any]) -> dict[str, str]:
    return {
        "filename": "datasheet-schema.json",
        "content_type": "application/json",
        "content": json.dumps(schema_plan, ensure_ascii=False, indent=2),
    }


def export_csv(headers: list[str], rows: list[list[str]]) -> dict[str, str]:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    writer.writerows(rows)
    return {
        "filename": "datasheet.csv",
        "content_type": "text/csv;charset=utf-8",
        "content": output.getvalue(),
    }


def export_excel_html(headers: list[str], rows: list[list[str]]) -> dict[str, str]:
    header_html = "".join(f"<th>{escape(header)}</th>" for header in headers)
    row_html = []
    for row in rows:
        cells = "".join(f"<td>{escape(cell)}</td>" for cell in row)
        row_html.append(f"<tr>{cells}</tr>")
    html = (
        '<html><head><meta charset="utf-8"></head><body>'
        f"<table><thead><tr>{header_html}</tr></thead>"
        f"<tbody>{''.join(row_html)}</tbody></table>"
        "</body></html>"
    )
    return {
        "filename": "datasheet.xls",
        "content_type": "application/vnd.ms-excel;charset=utf-8",
        "content": html,
    }


def rows_to_objects(headers: list[str], rows: list[list[str]]) -> list[dict[str, str]]:
    objects = []
    for row in rows:
        item = {}
        for index, header in enumerate(headers):
            item[header] = row[index] if index < len(row) else ""
        objects.append(item)
    return objects
