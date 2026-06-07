import unittest

from api.api import app


class StageTwoApiTest(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_templates_endpoint_returns_builtin_templates(self):
        response = self.client.get("/api/templates")

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertIn("templates", payload)
        self.assertIn(
            "ecommerce_order",
            {template["id"] for template in payload["templates"]},
        )

    def test_schema_plan_endpoint_accepts_template_id(self):
        response = self.client.post(
            "/api/schema/plan",
            json={
                "message": "生成 20 条招聘候选人信息表，期望薪资 8000-15000 元。",
                "template_id": "recruiting_candidates",
            },
        )

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["scenario"], "recruiting_candidates")
        self.assertEqual(payload["row_count"], 20)
        self.assertGreaterEqual(len(payload["schema"]), 5)

    def test_schema_plan_requires_message_or_template(self):
        response = self.client.post("/api/schema/plan", json={})

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.get_json())


if __name__ == "__main__":
    unittest.main()
