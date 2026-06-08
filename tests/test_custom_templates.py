import unittest

from api.business_templates import (
    clear_custom_templates,
    get_template,
    list_templates,
    save_custom_template,
)


class CustomTemplatesTest(unittest.TestCase):
    def tearDown(self):
        clear_custom_templates()

    def test_saves_custom_template_for_later_reuse(self):
        saved = save_custom_template(
            {
                "name": "门店巡检表",
                "description": "用于巡店 Demo 的自定义模板。",
                "fields": [
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
                        "constraints": {"enum": ["正常", "异常"]},
                    },
                ],
            }
        )

        self.assertTrue(saved["custom"])
        self.assertEqual(saved["id"], "custom_store_inspection")
        self.assertEqual(get_template("custom_store_inspection")["name"], "门店巡检表")
        self.assertIn(
            "custom_store_inspection",
            {template["id"] for template in list_templates()},
        )

    def test_rejects_custom_template_without_fields(self):
        with self.assertRaises(ValueError):
            save_custom_template({"name": "空模板", "fields": []})


if __name__ == "__main__":
    unittest.main()
