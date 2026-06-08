import unittest

from api.schema_planner import plan_schema
from api.schema_assistant import sanitize_llm_schema_plan


class SchemaAssistantTest(unittest.TestCase):
    def test_sanitizes_llm_schema_before_merging_with_base_plan(self):
        base_plan = plan_schema("生成 三 条门店巡检记录，字段包括门店、状态。")
        suggestion = {
            "scenario_label": "门店巡检记录",
            "row_count": "3",
            "schema": [
                {
                    "name": "store_name",
                    "label": "门店",
                    "type": "text",
                    "required": True,
                    "constraints": {"examples": ["上海店", "杭州店"]},
                },
                {
                    "name": "store_name",
                    "label": "门店",
                    "type": "string",
                    "required": True,
                    "constraints": {},
                },
                {
                    "name": "status",
                    "label": "状态",
                    "type": "enum",
                    "required": True,
                    "constraints": {"enum": ["正常", "异常", "待复查"]},
                },
                {
                    "name": "risk_score",
                    "label": "风险分",
                    "type": "float",
                    "required": False,
                    "constraints": {"min": "0", "max": "100"},
                },
            ],
        }

        assisted = sanitize_llm_schema_plan(suggestion, base_plan)

        self.assertEqual(assisted["source"], "llm_assisted")
        self.assertEqual(assisted["row_count"], 3)
        self.assertEqual(assisted["scenario_label"], "门店巡检记录")
        self.assertEqual(
            [field["name"] for field in assisted["schema"]],
            ["store_name", "status", "risk_score"],
        )
        fields = {field["name"]: field for field in assisted["schema"]}
        self.assertEqual(fields["store_name"]["type"], "string")
        self.assertEqual(fields["risk_score"]["type"], "number")
        self.assertEqual(fields["risk_score"]["constraints"]["min"], 0)
        self.assertEqual(fields["risk_score"]["constraints"]["max"], 100)
        self.assertIn("LLM 辅助规划", "\n".join(assisted["notes"]))


if __name__ == "__main__":
    unittest.main()
