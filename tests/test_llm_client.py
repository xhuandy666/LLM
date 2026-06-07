import os
import unittest
from unittest.mock import patch

from api.llm_client import (
    DEFAULT_BASE_URLS,
    DEFAULT_MODEL,
    DEFAULT_PROVIDER,
    LLMConfig,
    normalize_provider,
)


class LLMConfigTest(unittest.TestCase):
    def test_default_config_matches_career_copilot_qwen_model(self):
        with patch.dict(os.environ, {}, clear=True):
            config = LLMConfig.from_env()

        self.assertEqual(config.provider, DEFAULT_PROVIDER)
        self.assertEqual(config.provider, "qwen")
        self.assertEqual(config.model, DEFAULT_MODEL)
        self.assertEqual(config.model, "qwen-plus-2025-09-11")
        self.assertEqual(config.base_url, DEFAULT_BASE_URLS["qwen"])

    def test_qwen_reads_dashscope_api_key_from_environment(self):
        with patch.dict(os.environ, {"DASHSCOPE_API_KEY": "test-key"}, clear=True):
            config = LLMConfig.from_env(provider="qwen")

        self.assertEqual(config.api_key, "test-key")
        self.assertTrue(config.is_configured)

    def test_aliases_match_openai_compatible_provider_names(self):
        self.assertEqual(normalize_provider("dashscope"), "qwen")
        self.assertEqual(normalize_provider("custom"), "custom_openai_compatible")


if __name__ == "__main__":
    unittest.main()
