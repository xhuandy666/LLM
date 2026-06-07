import unittest

from api.schema_planner import build_generation_context, plan_schema


class SchemaPlannerTest(unittest.TestCase):
    def test_plans_ecommerce_schema_from_template_and_user_constraints(self):
        plan = plan_schema(
            "生成 50 条电商订单测试数据，金额 10-500 元，支付状态包括已支付、未支付、退款。",
            template_id="ecommerce_order",
        )
        fields = {field["name"]: field for field in plan["schema"]}

        self.assertEqual(plan["scenario"], "ecommerce_order")
        self.assertEqual(plan["scenario_label"], "电商订单测试数据")
        self.assertEqual(plan["row_count"], 50)
        self.assertEqual(fields["amount"]["constraints"]["min"], 10)
        self.assertEqual(fields["amount"]["constraints"]["max"], 500)
        self.assertEqual(
            fields["payment_status"]["constraints"]["enum"],
            ["已支付", "未支付", "退款"],
        )

    def test_infers_crm_template_from_natural_language(self):
        plan = plan_schema("生成 30 条 CRM 销售线索，用于销售看板 Demo。")
        fields = {field["name"]: field for field in plan["schema"]}

        self.assertEqual(plan["scenario"], "crm_leads")
        self.assertEqual(plan["source"], "inferred_template")
        self.assertEqual(plan["row_count"], 30)
        self.assertIn("customer_name", fields)
        self.assertIn("follow_status", fields)

    def test_custom_schema_uses_explicit_field_list(self):
        plan = plan_schema("生成 12 条活动报名表，字段包括姓名、手机号、报名渠道、是否到场。")

        self.assertEqual(plan["scenario"], "custom")
        self.assertEqual(plan["row_count"], 12)
        self.assertEqual(
            [field["label"] for field in plan["schema"]],
            ["姓名", "手机号", "报名渠道", "是否到场"],
        )

    def test_generation_context_includes_schema_and_constraints(self):
        plan = plan_schema(
            "生成 5 条电商订单测试数据，金额 100 到 200 元。",
            template_id="ecommerce_order",
        )

        context = build_generation_context("生成 5 条电商订单测试数据，金额 100 到 200 元。", plan)

        self.assertIn("目标行数: 5", context)
        self.assertIn("amount", context)
        self.assertIn("100", context)
        self.assertIn("200", context)
        self.assertIn("Markdown 表格", context)


if __name__ == "__main__":
    unittest.main()
