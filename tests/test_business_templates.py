import unittest

from api.business_templates import get_template, list_templates


class BusinessTemplatesTest(unittest.TestCase):
    def test_lists_four_business_templates(self):
        templates = list_templates()
        template_ids = {template["id"] for template in templates}

        self.assertEqual(
            template_ids,
            {
                "ecommerce_order",
                "student_profile",
                "crm_leads",
                "recruiting_candidates",
            },
        )
        for template in templates:
            self.assertIn("name", template)
            self.assertIn("description", template)
            self.assertGreaterEqual(len(template["fields"]), 5)

    def test_ecommerce_template_contains_order_fields_and_constraints(self):
        template = get_template("ecommerce_order")
        fields = {field["name"]: field for field in template["fields"]}

        self.assertIn("order_id", fields)
        self.assertIn("amount", fields)
        self.assertIn("payment_status", fields)
        self.assertEqual(fields["amount"]["type"], "number")
        self.assertEqual(
            fields["payment_status"]["constraints"]["enum"],
            ["已支付", "未支付", "退款"],
        )

    def test_get_template_returns_a_copy(self):
        template = get_template("student_profile")
        template["fields"][0]["label"] = "changed"

        fresh_template = get_template("student_profile")

        self.assertNotEqual(fresh_template["fields"][0]["label"], "changed")


if __name__ == "__main__":
    unittest.main()
