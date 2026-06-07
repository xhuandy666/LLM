"""Manual smoke entrypoint for checking LLM configuration without exposing secrets."""

from __future__ import annotations

try:
    from .llm_client import LLMConfig
except ImportError:
    from llm_client import LLMConfig


def main() -> None:
    config = LLMConfig.from_env()
    print(f"provider={config.provider}")
    print(f"model={config.model}")
    print(f"base_url={config.base_url}")
    print(f"configured={config.is_configured}")


if __name__ == "__main__":
    main()
