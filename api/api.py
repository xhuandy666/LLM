from __future__ import annotations

from flask import Flask, jsonify, request
from flask_cors import CORS

try:
    from .ESpeed import clear_message, get_response
    from .Optimize import get_reply
    from .business_templates import list_templates
    from .env_loader import load_local_env
    from .llm_client import LLMUnavailable
    from .schema_planner import plan_schema
    from .table_validator import validate_markdown_table
except ImportError:
    from ESpeed import clear_message, get_response
    from Optimize import get_reply
    from business_templates import list_templates
    from env_loader import load_local_env
    from llm_client import LLMUnavailable
    from schema_planner import plan_schema
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
    if not message and not template_id:
        return jsonify({"error": "message or template_id is required"}), 400
    return jsonify(plan_schema(message, template_id=template_id))


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


@app.route("/api/data", methods=["POST"])
def post_data():
    data = request.get_json(silent=True) or {}
    message = data.get("message", "").strip()
    model = data.get("model")
    session_id = data.get("session_id") or "default"
    template_id = data.get("template_id") or None
    if not message:
        return jsonify({"error": "message is required"}), 400
    try:
        schema_plan = plan_schema(message, template_id=template_id)
        return jsonify(
            get_response(
                message,
                model=model,
                session_id=session_id,
                schema_plan=schema_plan,
            )
        )
    except LLMUnavailable as exc:
        return jsonify({"error": str(exc)}), 503


@app.route("/api/clear", methods=["GET"])
def clear_history():
    session_id = request.args.get("session_id") or "default"
    clear_message(session_id)
    return jsonify({"message": "History cleared", "session_id": session_id})


if __name__ == "__main__":
    app.run()
