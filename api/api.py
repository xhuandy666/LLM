from __future__ import annotations

from flask import Flask, jsonify, request
from flask_cors import CORS

try:
    from .ESpeed import clear_message, replace_last_assistant_message
    from .Optimize import get_reply
    from .business_templates import delete_custom_template, list_templates, save_custom_template
    from .env_loader import load_local_env
    from .generation_pipeline import generate_table_with_quality_loop
    from .llm_client import LLMUnavailable
    from .schema_assistant import assist_schema_plan
    from .schema_planner import plan_schema
    from .table_exporter import export_table
    from .table_validator import validate_markdown_table
except ImportError:
    from ESpeed import clear_message, replace_last_assistant_message
    from Optimize import get_reply
    from business_templates import delete_custom_template, list_templates, save_custom_template
    from env_loader import load_local_env
    from generation_pipeline import generate_table_with_quality_loop
    from llm_client import LLMUnavailable
    from schema_assistant import assist_schema_plan
    from schema_planner import plan_schema
    from table_exporter import export_table
    from table_validator import validate_markdown_table


load_local_env()

app = Flask(__name__)
CORS(app, supports_credentials=True)


@app.route("/")
def hello():
    return "World!"


@app.route("/api/message", methods=["GET"])
def get_data():
    data = request.get_json(silent=True) or {}
    return jsonify(data)


@app.route("/api/optimize", methods=["POST"])
def post_optimize():
    data = request.get_json(silent=True) or {}
    message = data.get("message", "").strip()
    model = data.get("model")
    if not message:
        return jsonify({"error": "message is required"}), 400
    try:
        return jsonify(get_reply(message, model=model))
    except LLMUnavailable as exc:
        return jsonify({"error": str(exc)}), 503


@app.route("/api/templates", methods=["GET"])
def get_templates():
    return jsonify({"templates": list_templates()})


@app.route("/api/schema/plan", methods=["POST"])
def post_schema_plan():
    data = request.get_json(silent=True) or {}
    message = data.get("message", "").strip()
    template_id = data.get("template_id") or None
    model = data.get("model")
    use_llm_assist = bool(data.get("use_llm_assist"))
    if not message and not template_id:
        return jsonify({"error": "message or template_id is required"}), 400
    base_plan = plan_schema(message, template_id=template_id)
    if not use_llm_assist:
        return jsonify(base_plan)
    try:
        return jsonify(assist_schema_plan(message, base_plan, model=model))
    except LLMUnavailable as exc:
        return jsonify({"error": str(exc)}), 503
    except (ValueError, TypeError) as exc:
        return jsonify({"error": f"LLM schema assist failed: {exc}"}), 422


@app.route("/api/validate", methods=["POST"])
def post_validate():
    data = request.get_json(silent=True) or {}
    markdown = data.get("markdown", "")
    schema_plan = data.get("schema_plan")
    if not markdown:
        return jsonify({"error": "markdown is required"}), 400
    if not schema_plan:
        return jsonify({"error": "schema_plan is required"}), 400
    return jsonify(validate_markdown_table(markdown, schema_plan))


@app.route("/api/export", methods=["POST"])
def post_export():
    data = request.get_json(silent=True) or {}
    markdown = data.get("markdown", "")
    schema_plan = data.get("schema_plan")
    export_format = data.get("format") or "json"
    if not markdown:
        return jsonify({"error": "markdown is required"}), 400
    if not schema_plan:
        return jsonify({"error": "schema_plan is required"}), 400
    try:
        return jsonify(export_table(markdown, schema_plan, export_format))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


@app.route("/api/templates/custom", methods=["POST"])
def post_custom_template():
    data = request.get_json(silent=True) or {}
    try:
        template = save_custom_template(data)
        return jsonify({"template": template}), 201
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


@app.route("/api/templates/custom/<template_id>", methods=["DELETE"])
def delete_custom_template_route(template_id: str):
    deleted = delete_custom_template(template_id)
    if not deleted:
        return jsonify({"error": "custom template not found"}), 404
    return jsonify({"deleted": True, "template_id": template_id})


@app.route("/api/data", methods=["POST"])
def post_data():
    data = request.get_json(silent=True) or {}
    message = data.get("message", "").strip()
    model = data.get("model")
    session_id = data.get("session_id") or "default"
    template_id = data.get("template_id") or None
    max_repair_attempts = int(data.get("max_repair_attempts") or 1)
    use_llm_assist = data.get("use_llm_assist", True)
    if not message:
        return jsonify({"error": "message is required"}), 400
    try:
        result = generate_table_with_quality_loop(
            message,
            model=model,
            session_id=session_id,
            template_id=template_id,
            max_repair_attempts=max_repair_attempts,
            use_llm_assist=bool(use_llm_assist),
            message_replacer=replace_last_assistant_message,
        )
        status_code = 200 if result["validation_result"]["passed"] else 422
        return jsonify(result), status_code
    except LLMUnavailable as exc:
        return jsonify({"error": str(exc)}), 503


@app.route("/api/clear", methods=["GET"])
def clear_history():
    session_id = request.args.get("session_id") or "default"
    clear_message(session_id)
    return jsonify({"message": "History cleared", "session_id": session_id})


if __name__ == "__main__":
    app.run()
