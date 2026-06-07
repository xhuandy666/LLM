import unittest

from api.schema_planner import plan_schema
from api.table_validator import validate_markdown_table


class TableValidatorTest(unittest.TestCase):
    def test_valid_table_passes_schema_checks(self):
        plan = plan_schema(
            "生成 2 条电商订单测试数据，金额 10-500 元，支付状态包括已支付、未支付、退款。",
            template_id="ecommerce_order",
        )
        markdown = """
| 订单号 | 用户ID | 商品类别 | 商品名称 | 金额 | 支付状态 | 下单时间 | 收货城市 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ORD202606070001 | U102938 | 数码 | 无线耳机 | 99.90 | 已支付 | 2026-06-07 10:30:00 | 杭州 |
| ORD202606070002 | U102939 | 家居 | 台灯 | 188 | 退款 | 2026-06-07 11:10:00 | 上海 |
"""

        result = validate_markdown_table(markdown, plan)

        self.assertTrue(result["passed"])
        self.assertEqual(result["summary"]["row_count"]["actual"], 2)
        self.assertEqual(result["summary"]["issue_count"], 0)
        self.assertIn("校验通过", result["report"])

    def test_field_name_headers_are_accepted_for_llm_outputs(self):
        plan = plan_schema(
            "生成 2 条电商订单测试数据，金额 10-500 元，支付状态包括已支付、未支付、退款。",
            template_id="ecommerce_order",
        )
        markdown = """
| order_id | user_id | product_category | product_name | amount | payment_status | order_time | shipping_city |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ORD202606070001 | U102938 | 数码 | 无线耳机 | 99.90 | 已支付 | 2026-06-07 10:30:00 | 杭州 |
| ORD202606070002 | U102939 | 家居 | 台灯 | 188 | 退款 | 2026-06-07 11:10:00 | 上海 |
"""

        result = validate_markdown_table(markdown, plan)

        self.assertTrue(result["passed"])
        self.assertEqual(result["summary"]["issue_count"], 0)

    def test_invalid_table_reports_row_enum_and_range_issues(self):
        plan = plan_schema(
            "生成 2 条电商订单测试数据，金额 10-500 元，支付状态包括已支付、未支付、退款。",
            template_id="ecommerce_order",
        )
        markdown = """
| 订单号 | 用户ID | 商品类别 | 商品名称 | 金额 | 支付状态 | 下单时间 | 收货城市 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ORD202606070001 | U102938 | 数码 | 无线耳机 | 999.90 | 已完成 | 2026-06-07 10:30:00 | 杭州 |
"""

        result = validate_markdown_table(markdown, plan)
        messages = [issue["message"] for issue in result["issues"]]

        self.assertFalse(result["passed"])
        self.assertEqual(result["summary"]["row_count"]["expected"], 2)
        self.assertEqual(result["summary"]["row_count"]["actual"], 1)
        self.assertGreaterEqual(result["summary"]["issue_count"], 3)
        self.assertTrue(any("目标行数" in message for message in messages))
        self.assertTrue(any("金额" in message and "500" in message for message in messages))
        self.assertTrue(any("支付状态" in message and "已完成" in message for message in messages))
        self.assertIn("校验未通过", result["report"])

    def test_missing_required_column_is_reported(self):
        plan = plan_schema("生成 1 条 CRM 销售线索。", template_id="crm_leads")
        markdown = """
| 客户名称 | 行业 | 联系人 |
| --- | --- | --- |
| 星河科技有限公司 | 互联网 | 李经理 |
"""

        result = validate_markdown_table(markdown, plan)
        messages = [issue["message"] for issue in result["issues"]]

        self.assertFalse(result["passed"])
        self.assertTrue(any("缺少必填字段" in message and "手机号" in message for message in messages))
        self.assertTrue(any("缺少必填字段" in message and "线索等级" in message for message in messages))

    def test_non_table_content_reports_parse_error(self):
        plan = plan_schema("生成 1 条学生信息。", template_id="student_profile")

        result = validate_markdown_table("这里不是 Markdown 表格。", plan)

        self.assertFalse(result["passed"])
        self.assertEqual(result["summary"]["issue_count"], 1)
        self.assertIn("未识别到 Markdown 表格", result["issues"][0]["message"])


if __name__ == "__main__":
    unittest.main()
