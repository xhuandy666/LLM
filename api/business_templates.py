from __future__ import annotations

from copy import deepcopy
from typing import Any


BusinessTemplate = dict[str, Any]


_BUSINESS_TEMPLATES: list[BusinessTemplate] = [
    {
        "id": "ecommerce_order",
        "name": "电商订单测试数据",
        "description": "适合订单系统测试、支付状态统计、销售看板和产品 Demo。",
        "fields": [
            {
                "name": "order_id",
                "label": "订单号",
                "type": "string",
                "required": True,
                "constraints": {"pattern": "ORD + 日期 + 4位序号", "unique": True},
                "example": "ORD202606070001",
            },
            {
                "name": "user_id",
                "label": "用户ID",
                "type": "string",
                "required": True,
                "constraints": {"pattern": "U + 6位数字"},
                "example": "U102938",
            },
            {
                "name": "product_category",
                "label": "商品类别",
                "type": "enum",
                "required": True,
                "constraints": {"enum": ["数码", "家居", "服饰", "食品", "美妆"]},
                "example": "数码",
            },
            {
                "name": "product_name",
                "label": "商品名称",
                "type": "string",
                "required": True,
                "constraints": {"max_length": 30},
                "example": "无线耳机",
            },
            {
                "name": "amount",
                "label": "金额",
                "type": "number",
                "required": True,
                "constraints": {"min": 1, "max": 5000, "unit": "CNY", "precision": 2},
                "example": 199.0,
            },
            {
                "name": "payment_status",
                "label": "支付状态",
                "type": "enum",
                "required": True,
                "constraints": {"enum": ["已支付", "未支付", "退款"]},
                "example": "已支付",
            },
            {
                "name": "order_time",
                "label": "下单时间",
                "type": "datetime",
                "required": True,
                "constraints": {"format": "YYYY-MM-DD HH:mm:ss"},
                "example": "2026-06-07 10:30:00",
            },
            {
                "name": "shipping_city",
                "label": "收货城市",
                "type": "string",
                "required": True,
                "constraints": {"examples": ["北京", "上海", "杭州", "深圳", "成都"]},
                "example": "杭州",
            },
        ],
    },
    {
        "id": "student_profile",
        "name": "学生与班级信息表",
        "description": "适合教学案例、数据分析练习和学生管理系统原型。",
        "fields": [
            {
                "name": "student_id",
                "label": "学号",
                "type": "string",
                "required": True,
                "constraints": {"pattern": "S + 8位数字", "unique": True},
                "example": "S20260001",
            },
            {
                "name": "student_name",
                "label": "姓名",
                "type": "string",
                "required": True,
                "constraints": {"max_length": 12},
                "example": "张明",
            },
            {
                "name": "gender",
                "label": "性别",
                "type": "enum",
                "required": True,
                "constraints": {"enum": ["男", "女"]},
                "example": "女",
            },
            {
                "name": "age",
                "label": "年龄",
                "type": "integer",
                "required": True,
                "constraints": {"min": 16, "max": 25},
                "example": 20,
            },
            {
                "name": "class_name",
                "label": "班级",
                "type": "string",
                "required": True,
                "constraints": {"examples": ["计科一班", "计科二班", "软工一班"]},
                "example": "计科一班",
            },
            {
                "name": "height_cm",
                "label": "身高(cm)",
                "type": "number",
                "required": False,
                "constraints": {"min": 145, "max": 200, "unit": "cm", "precision": 1},
                "example": 168.5,
            },
            {
                "name": "score",
                "label": "成绩",
                "type": "number",
                "required": True,
                "constraints": {"min": 0, "max": 100, "precision": 1},
                "example": 86.5,
            },
            {
                "name": "is_boarding",
                "label": "是否住宿",
                "type": "boolean",
                "required": False,
                "constraints": {"true_label": "是", "false_label": "否"},
                "example": "是",
            },
        ],
    },
    {
        "id": "crm_leads",
        "name": "CRM 销售线索表",
        "description": "适合 CRM 原型、销售漏斗看板和客户跟进流程演示。",
        "fields": [
            {
                "name": "customer_name",
                "label": "客户名称",
                "type": "string",
                "required": True,
                "constraints": {"max_length": 30},
                "example": "星河科技有限公司",
            },
            {
                "name": "industry",
                "label": "行业",
                "type": "enum",
                "required": True,
                "constraints": {"enum": ["互联网", "教育", "制造", "金融", "医疗"]},
                "example": "互联网",
            },
            {
                "name": "contact_name",
                "label": "联系人",
                "type": "string",
                "required": True,
                "constraints": {"max_length": 12},
                "example": "李经理",
            },
            {
                "name": "phone",
                "label": "手机号",
                "type": "phone",
                "required": True,
                "constraints": {"pattern": "中国大陆11位手机号"},
                "example": "13800138000",
            },
            {
                "name": "lead_level",
                "label": "线索等级",
                "type": "enum",
                "required": True,
                "constraints": {"enum": ["A", "B", "C"]},
                "example": "A",
            },
            {
                "name": "follow_status",
                "label": "跟进状态",
                "type": "enum",
                "required": True,
                "constraints": {"enum": ["待跟进", "跟进中", "已成交", "已流失"]},
                "example": "跟进中",
            },
            {
                "name": "expected_amount",
                "label": "预计金额",
                "type": "number",
                "required": False,
                "constraints": {"min": 1000, "max": 500000, "unit": "CNY", "precision": 2},
                "example": 80000.0,
            },
            {
                "name": "next_follow_time",
                "label": "下次跟进时间",
                "type": "date",
                "required": False,
                "constraints": {"format": "YYYY-MM-DD"},
                "example": "2026-06-12",
            },
        ],
    },
    {
        "id": "recruiting_candidates",
        "name": "招聘候选人信息表",
        "description": "适合招聘系统 Demo、候选人筛选测试和 HR 数据看板。",
        "fields": [
            {
                "name": "candidate_name",
                "label": "姓名",
                "type": "string",
                "required": True,
                "constraints": {"max_length": 12},
                "example": "王同学",
            },
            {
                "name": "job_role",
                "label": "应聘岗位",
                "type": "string",
                "required": True,
                "constraints": {"examples": ["前端实习生", "后端实习生", "AI Agent 实习生"]},
                "example": "AI Agent 实习生",
            },
            {
                "name": "years_experience",
                "label": "经验年限",
                "type": "number",
                "required": True,
                "constraints": {"min": 0, "max": 10, "unit": "year", "precision": 1},
                "example": 1.5,
            },
            {
                "name": "skill_tags",
                "label": "技能标签",
                "type": "list",
                "required": True,
                "constraints": {"separator": "/", "examples": ["Python", "Vue", "Flask", "LLM"]},
                "example": "Python/Flask/LLM",
            },
            {
                "name": "interview_status",
                "label": "面试状态",
                "type": "enum",
                "required": True,
                "constraints": {"enum": ["待筛选", "一面中", "二面中", "已通过", "已淘汰"]},
                "example": "一面中",
            },
            {
                "name": "expected_salary",
                "label": "期望薪资",
                "type": "number",
                "required": False,
                "constraints": {"min": 3000, "max": 30000, "unit": "CNY", "precision": 0},
                "example": 12000,
            },
            {
                "name": "city",
                "label": "城市",
                "type": "string",
                "required": False,
                "constraints": {"examples": ["北京", "上海", "杭州", "深圳", "广州"]},
                "example": "上海",
            },
        ],
    },
]


def list_templates() -> list[BusinessTemplate]:
    return deepcopy(_BUSINESS_TEMPLATES)


def get_template(template_id: str | None) -> BusinessTemplate | None:
    if not template_id:
        return None
    for template in _BUSINESS_TEMPLATES:
        if template["id"] == template_id:
            return deepcopy(template)
    return None
