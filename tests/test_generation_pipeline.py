import unittest

from api.generation_pipeline import generate_table_with_quality_loop


VALID_MARKDOWN = """
| 姓名 | 应聘岗位 | 经验年限 | 技能标签 | 面试状态 | 期望薪资 | 城市 |
| --- | --- | --- | --- | --- | --- | --- |
| 王同学 | AI Agent 实习生 | 1.5 | Python/Flask/LLM | 一面中 | 12000 | 上海 |
"""

INVALID_MARKDOWN = """
| 姓名 | 应聘岗位 | 经验年限 | 技能标签 | 面试状态 | 期望薪资 | 城市 |
| --- | --- | --- | --- | --- | --- | --- |
| 王同学 | AI Agent 实习生 | 1.5 | Python/Flask/LLM | 未进入流程 | 12000 | 上海 |
"""


class GenerationPipelineTest(unittest.TestCase):
    def test_uses_llm_schema_assist_by_default(self):
        calls = {"assist": 0}
        captured = {}

        def fake_schema_assister(message, base_plan, model=None):
            calls["assist"] += 1
            assisted = dict(base_plan)
            assisted["source"] = "llm_assisted"
            return assisted

        def fake_generator(message, model=None, session_id="default", schema_plan=None):
            captured["schema_source"] = schema_plan["source"]
            return [
                {"role": "user", "content": message},
                {"role": "assistant", "content": VALID_MARKDOWN},
            ]

        result = generate_table_with_quality_loop(
            "生成 1 条招聘候选人信息表。",
            template_id="recruiting_candidates",
            generator=fake_generator,
            schema_assister=fake_schema_assister,
        )

        self.assertEqual(calls["assist"], 1)
        self.assertEqual(captured["schema_source"], "llm_assisted")
        self.assertEqual(result["schema_plan"]["source"], "llm_assisted")
        self.assertTrue(result["validation_result"]["passed"])

    def test_repairs_invalid_generation_before_returning_success(self):
        calls = {"repair": 0}

        def fake_generator(message, model=None, session_id="default", schema_plan=None):
            return [
                {"role": "user", "content": message},
                {"role": "assistant", "content": INVALID_MARKDOWN},
            ]

        def fake_repairer(markdown, schema_plan, validation_result, model=None):
            calls["repair"] += 1
            return VALID_MARKDOWN

        result = generate_table_with_quality_loop(
            "生成 1 条招聘候选人信息表。",
            template_id="recruiting_candidates",
            generator=fake_generator,
            repairer=fake_repairer,
            schema_assister=lambda message, base_plan, model=None: base_plan,
        )

        self.assertTrue(result["validation_result"]["passed"])
        self.assertEqual(result["status"], "passed")
        self.assertEqual(result["repair_attempts"], 1)
        self.assertEqual(calls["repair"], 1)
        self.assertEqual(result["messages"][-1]["content"], VALID_MARKDOWN)

    def test_returns_structured_failure_when_repair_cannot_fix_table(self):
        def fake_generator(message, model=None, session_id="default", schema_plan=None):
            return [
                {"role": "user", "content": message},
                {"role": "assistant", "content": INVALID_MARKDOWN},
            ]

        def fake_repairer(markdown, schema_plan, validation_result, model=None):
            return markdown

        result = generate_table_with_quality_loop(
            "生成 1 条招聘候选人信息表。",
            template_id="recruiting_candidates",
            generator=fake_generator,
            repairer=fake_repairer,
            max_repair_attempts=1,
            schema_assister=lambda message, base_plan, model=None: base_plan,
        )

        self.assertFalse(result["validation_result"]["passed"])
        self.assertEqual(result["status"], "repair_failed")
        self.assertEqual(result["repair_attempts"], 1)
        self.assertGreater(result["validation_result"]["summary"]["issue_count"], 0)


if __name__ == "__main__":
    unittest.main()
