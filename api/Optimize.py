from __future__ import annotations

try:
    from .llm_client import LLMClient, LLMConfig
except ImportError:
    from llm_client import LLMClient, LLMConfig


PROMPT_OPTIMIZER_SYSTEM = (
    "你是一名表格数据生成提示词优化顾问。你的任务是把用户的原始需求改写成更清晰、"
    "更具体、更适合生成结构化表格数据的提示词。只输出优化后的提示词，不要输出解释。"
)


def _build_optimizer_prompt(content: str) -> str:
    return (
        "请优化下面的表格数据生成需求，使大模型可以更准确、高效地输出表格数据。\n"
        "优化时请关注：字段完整性、行数、字段类型、取值范围、枚举值、展示清晰度。\n\n"
        "参考案例：\n"
        "优化前：小明班级共有10个人，其中男性5人，女性5人，身高范围在165-180。\n"
        "优化后：请生成一张小明班级学生信息表，共10行，字段包括姓名、性别、身高。"
        "其中男性5人、女性5人，身高在165-180厘米之间随机生成，要求数据清晰且不要重复。\n\n"
        f"用户需求：{content}"
    )


def get_reply(content: str, model: str | None = None) -> str:
    config = LLMConfig.from_env(model=model)
    client = LLMClient(config)
    return client.chat(
        [
            {"role": "system", "content": PROMPT_OPTIMIZER_SYSTEM},
            {"role": "user", "content": _build_optimizer_prompt(content)},
        ]
    )
