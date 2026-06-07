from __future__ import annotations

try:
    from .conversation_store import ConversationStore
    from .llm_client import LLMClient, LLMConfig, table_generation_instruction
    from .schema_planner import SchemaPlan, build_generation_context
except ImportError:
    from conversation_store import ConversationStore
    from llm_client import LLMClient, LLMConfig, table_generation_instruction
    from schema_planner import SchemaPlan, build_generation_context


conversation_store = ConversationStore()


def get_response(
    content: str,
    model: str | None = None,
    session_id: str = "default",
    schema_plan: SchemaPlan | None = None,
):
    config = LLMConfig.from_env(model=model)
    client = LLMClient(config)
    llm_content = build_generation_context(content, schema_plan)
    user_content = table_generation_instruction(llm_content)
    messages = conversation_store.get_history(session_id)
    messages.append({"role": "user", "content": user_content})
    assistant_content = client.chat(messages)
    return conversation_store.add_exchange(session_id, content, assistant_content)


def clear_message(session_id: str | None = None):
    conversation_store.clear(session_id)
