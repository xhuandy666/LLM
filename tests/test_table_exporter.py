import json
import unittest

from api.schema_planner import plan_schema
from api.table_exporter import export_table


class TableExporterTest(unittest.TestCase):
    def setUp(self):
        self.plan = plan_schema("生成 1 条招聘候选人信息表。", template_id="recruiting_candidates")
        self.markdown = """
| 姓名 | 应聘岗位 | 经验年限 | 技能标签 | 面试状态 | 期望薪资 | 城市 |
| --- | --- | --- | --- | --- | --- | --- |
| 王同学 | AI Agent 实习生 | 1.5 | Python/Flask/LLM | 一面中 | 12000 | 上海 |
"""

    def test_exports_table_as_json_rows(self):
        exported = export_table(self.markdown, self.plan, "json")

        self.assertEqual(exported["content_type"], "application/json")
        payload = json.loads(exported["content"])
        self.assertEqual(payload["rows"][0]["姓名"], "王同学")
        self.assertEqual(payload["schema"]["scenario"], "recruiting_candidates")

    def test_exports_schema_configuration(self):
        exported = export_table(self.markdown, self.plan, "schema")

        payload = json.loads(exported["content"])
        self.assertEqual(exported["filename"], "datasheet-schema.json")
        self.assertEqual(payload["scenario_label"], "招聘候选人信息表")

    def test_exports_excel_compatible_html(self):
        exported = export_table(self.markdown, self.plan, "excel")

        self.assertEqual(exported["filename"], "datasheet.xls")
        self.assertIn("application/vnd.ms-excel", exported["content_type"])
        self.assertIn("<table", exported["content"])
        self.assertIn("王同学", exported["content"])


if __name__ == "__main__":
    unittest.main()
