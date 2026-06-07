import unittest

from api.api import app
from api.schema_planner import plan_schema


class StageThreeApiTest(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

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


if __name__ == "__main__":
    unittest.main()
