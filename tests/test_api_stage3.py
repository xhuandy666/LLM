import unittest

import api.api as api_module
from api.api import app
from api.business_templates import clear_custom_templates
from api.schema_planner import plan_schema


class StageThreeApiTest(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def tearDown(self):
        clear_custom_templates()

    def test_validate_endpoint_returns_quality_report(self):
        plan = plan_schema("生成 1 条招聘候选人信息表。", template_id="recruiting_candidates")
        markdown = """
| 姓名 | 应聘岗位 | 经验年限 | 技能标签 | 面试状态 | 期望薪资 | 城市 |
| --- | --- | --- | --- | --- | --- | --- |
| 王同学 | AI Agent 实习生 | 1.5 | Python/Flask/LLM | 一面中 | 12000 | 上海 |
"""

        response = self.client.post(
            "/api/validate",
            json={"markdown": markdown, "schema_plan": plan},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertTrue(payload["passed"])
        self.assertIn("report", payload)
        self.assertIn("校验通过", payload["report"])

    def test_validate_endpoint_requires_schema_plan(self):
        response = self.client.post("/api/validate", json={"markdown": "| A |\n|---|\n|1|"})

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.get_json())

    def test_data_endpoint_returns_quality_loop_payload(self):
        original_pipeline = api_module.generate_table_with_quality_loop

        def fake_pipeline(*args, **kwargs):
            return {
                "status": "passed",
                "messages": [{"role": "assistant", "content": "| A |\n|---|\n|1|"}],
                "schema_plan": {"scenario": "demo", "schema": []},
                "validation_result": {"passed": True, "summary": {"issue_count": 0}, "issues": []},
                "repair_attempts": 1,
            }

        api_module.generate_table_with_quality_loop = fake_pipeline
        try:
            response = self.client.post("/api/data", json={"message": "生成 1 条数据"})
        finally:
            api_module.generate_table_with_quality_loop = original_pipeline

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["status"], "passed")
        self.assertEqual(payload["repair_attempts"], 1)
        self.assertTrue(payload["validation_result"]["passed"])

    def test_data_endpoint_returns_422_when_repair_fails(self):
        original_pipeline = api_module.generate_table_with_quality_loop

        def fake_pipeline(*args, **kwargs):
            return {
                "status": "repair_failed",
                "messages": [{"role": "assistant", "content": "| A |\n|---|\n|bad|"}],
                "schema_plan": {"scenario": "demo", "schema": []},
                "validation_result": {"passed": False, "summary": {"issue_count": 1}, "issues": []},
                "repair_attempts": 1,
            }

        api_module.generate_table_with_quality_loop = fake_pipeline
        try:
            response = self.client.post("/api/data", json={"message": "生成 1 条数据"})
        finally:
            api_module.generate_table_with_quality_loop = original_pipeline

        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.get_json()["status"], "repair_failed")

    def test_export_endpoint_returns_requested_format(self):
        plan = plan_schema("生成 1 条招聘候选人信息表。", template_id="recruiting_candidates")
        markdown = """
| 姓名 | 应聘岗位 | 经验年限 | 技能标签 | 面试状态 | 期望薪资 | 城市 |
| --- | --- | --- | --- | --- | --- | --- |
| 王同学 | AI Agent 实习生 | 1.5 | Python/Flask/LLM | 一面中 | 12000 | 上海 |
"""

        response = self.client.post(
            "/api/export",
            json={"markdown": markdown, "schema_plan": plan, "format": "schema"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["filename"], "datasheet-schema.json")

    def test_custom_template_endpoint_saves_reusable_template(self):
        response = self.client.post(
            "/api/templates/custom",
            json={
                "name": "门店巡检表",
                "fields": [
                    {"name": "store_name", "label": "门店", "type": "string", "required": True},
                    {
                        "name": "status",
                        "label": "状态",
                        "type": "enum",
                        "required": True,
                        "constraints": {"enum": ["正常", "异常"]},
                    },
                ],
            },
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()["template"]["id"], "custom_store_inspection")
        templates = self.client.get("/api/templates").get_json()["templates"]
        self.assertIn("custom_store_inspection", {template["id"] for template in templates})

    def test_schema_plan_endpoint_can_use_llm_assist(self):
        original_assist = api_module.assist_schema_plan

        def fake_assist(message, base_plan, model=None):
            assisted = dict(base_plan)
            assisted["source"] = "llm_assisted"
            assisted["notes"] = ["LLM 辅助规划"]
            return assisted

        api_module.assist_schema_plan = fake_assist
        try:
            response = self.client.post(
                "/api/schema/plan",
                json={"message": "生成 3 条门店巡检记录", "use_llm_assist": True},
            )
        finally:
            api_module.assist_schema_plan = original_assist

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["source"], "llm_assisted")


if __name__ == "__main__":
    unittest.main()
