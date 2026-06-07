from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any


DEFAULT_PROVIDER = "qwen"
DEFAULT_MODEL = "qwen-plus-2025-09-11"
DEFAULT_MAX_TOKENS = 4096

OPENAI_COMPATIBLE_PROVIDERS = {
    "openai",
    "deepseek",
    "qwen",
    "kimi",
    "openrouter",
    "custom_openai_compatible",
}

DEFAULT_BASE_URLS = {
    "openai": "https://api.openai.com/v1",
    "deepseek": "https://api.deepseek.com/v1",
    "qwen": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "kimi": "https://api.moonshot.cn/v1",
    "openrouter": "https://openrouter.ai/api/v1",
    "custom_openai_compatible": "",
}

DEFAULT_MODELS = {
    "openai": "gpt-4.1-mini",
    "deepseek": "deepseek-chat",
    "qwen": DEFAULT_MODEL,
    "kimi": "moonshot-v1-8k",
    "openrouter": "openai/gpt-4.1-mini",
    "custom_openai_compatible": "custom-model",
}

API_KEY_ENV = {
    "openai": "OPENAI_API_KEY",
    "deepseek": "DEEPSEEK_API_KEY",
    "qwen": "DASHSCOPE_API_KEY",
    "kimi": "MOONSHOT_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
    "custom_openai_compatible": "CUSTOM_LLM_API_KEY",
}

BASE_URL_ENV = {
    "openai": "OPENAI_BASE_URL",
    "deepseek": "DEEPSEEK_BASE_URL",
    "qwen": "DASHSCOPE_BASE_URL",
    "kimi": "MOONSHOT_BASE_URL",
    "openrouter": "OPENROUTER_BASE_URL",
    "custom_openai_compatible": "CUSTOM_LLM_BASE_URL",
}


class LLMUnavailable(RuntimeError):
    """Raised when the configured model cannot be called."""


def normalize_provider(provider: str | None) -> str:
    normalized = (provider or DEFAULT_PROVIDER).strip().lower().replace("-", "_")
    aliases = {
        "dashscope": "qwen",
        "custom": "custom_openai_compatible",
        "moonshot": "kimi",
        "gpt": "openai",
    }
    normalized = aliases.get(normalized, normalized)
    if normalized not in OPENAI_COMPATIBLE_PROVIDERS:
        supported = ", ".join(sorted(OPENAI_COMPATIBLE_PROVIDERS))
        raise ValueError(f"Unsupported LLM provider '{provider}'. Supported: {supported}")
    return normalized


@dataclass(frozen=True)
class LLMConfig:
    provider: str = DEFAULT_PROVIDER
    model: str = DEFAULT_MODEL
    api_key: str | None = None
    base_url: str = DEFAULT_BASE_URLS[DEFAULT_PROVIDER]
    temperature: float = 0.2
    max_tokens: int = DEFAULT_MAX_TOKENS
    timeout: float = 60.0

    @classmethod
    def from_env(
        cls,
        provider: str | None = None,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        timeout: float | None = None,
    ) -> "LLMConfig":
        normalized = normalize_provider(provider or os.getenv("LLM_PROVIDER"))
        api_key_env = API_KEY_ENV.get(normalized)
        base_url_env = BASE_URL_ENV.get(normalized)
        return cls(
            provider=normalized,
            model=model or os.getenv("MODEL") or DEFAULT_MODELS[normalized],
            api_key=os.getenv(api_key_env) if api_key_env else None,
            base_url=(
                (os.getenv(base_url_env) if base_url_env else None)
                or DEFAULT_BASE_URLS[normalized]
            ),
            temperature=temperature if temperature is not None else 0.2,
            max_tokens=max_tokens if max_tokens is not None else DEFAULT_MAX_TOKENS,
            timeout=timeout if timeout is not None else 60.0,
        )

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key and self.base_url)


class LLMClient:
    """Small OpenAI-compatible chat client used by the Flask app."""

    def __init__(self, config: LLMConfig | None = None) -> None:
        self.config = config or LLMConfig.from_env()

    def chat(self, messages: list[dict[str, str]]) -> str:
        if not self.config.is_configured:
            env_name = API_KEY_ENV.get(self.config.provider, "LLM_API_KEY")
            raise LLMUnavailable(
                f"{self.config.provider} is not configured. Please set {env_name}."
            )

        payload: dict[str, Any] = {
            "model": self.config.model,
            "messages": messages,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
        }
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
        }
        url = f"{self.config.base_url.rstrip('/')}/chat/completions"
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        request = urllib.request.Request(url, data=body, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=self.config.timeout) as response:
                data = json.loads(response.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"]
        except (
            urllib.error.URLError,
            TimeoutError,
            json.JSONDecodeError,
            KeyError,
            IndexError,
            TypeError,
        ) as exc:
            raise LLMUnavailable(f"LLM request failed for {self.config.provider}: {exc}") from exc


def table_generation_instruction(content: str) -> str:
    return f"{content}\n注意：输出的内容请不要加任何多余的文字描述。"
