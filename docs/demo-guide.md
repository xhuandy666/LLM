# DataSheet Agent Demo Guide

本文档用于准备 GitHub README、项目答辩、校招面试和录屏演示。推荐使用“电商订单测试数据”作为主 Demo，因为它能同时展示业务模板、金额范围、枚举约束、Schema 规划、质量校验和 CSV 导出。

## Demo 目标

通过一个完整流程说明 DataSheet Agent 不是简单调用 LLM 生成表格，而是围绕业务模拟数据构造形成了轻量 Agent 闭环:

1. 用户用自然语言描述业务数据需求。
2. 系统选择或识别业务场景模板。
3. Schema Planner 规划字段、类型、必填项和约束。
4. LLM 按 schema 生成 Markdown 表格。
5. Table Validator 检查行数、字段、枚举值和数值范围。
6. 用户复制表格或导出 CSV。

## 推荐演示输入

```text
生成 5 条电商订单测试数据，金额 10-500 元，支付状态包括已支付、未支付、退款。
```

推荐选择模板: `电商订单测试数据`

这个输入适合展示:

- 行数约束: 5 条数据。
- 数值范围: 金额 10-500 元。
- 枚举约束: 支付状态只能是已支付、未支付、退款。
- 业务字段: 订单号、用户 ID、商品类别、金额、支付状态、下单时间、收货城市。

## 前端演示步骤

1. 启动后端:

```bash
source .venv/bin/activate
python api/api.py
```

2. 启动前端:

```bash
cd frontend
npm run serve
```

3. 打开前端:

```text
http://127.0.0.1:8080/
```

4. 在模板下拉框选择 `电商订单测试数据`。

5. 输入推荐演示需求，点击 `规划 Schema`。

6. 观察 Schema 面板:

- 场景显示为电商订单测试数据。
- 目标行数显示为 5。
- `amount` 字段约束应包含 10-500。
- `payment_status` 字段枚举应包含已支付、未支付、退款。

7. 点击 `生成表格`。

8. 表格生成后点击 `质量检查`。

9. 观察质量检查结果:

- 如果模型输出满足约束，应显示 `校验通过`。
- 如果模型输出行数不对、字段缺失、金额越界或枚举值错误，应显示问题列表。

10. 点击 `导出csv`，验证可导出最近一次生成的 Markdown 表格。

## API 演示

### 获取业务模板

```bash
curl http://127.0.0.1:5000/api/templates
```

### 规划 Schema

```bash
curl -X POST http://127.0.0.1:5000/api/schema/plan \
  -H "Content-Type: application/json" \
  -d '{"message":"生成 5 条电商订单测试数据，金额 10-500 元，支付状态包括已支付、未支付、退款。","template_id":"ecommerce_order"}'
```

### 校验一张合格表格

```bash
curl -X POST http://127.0.0.1:5000/api/validate \
  -H "Content-Type: application/json" \
  -d '{
    "markdown":"| 订单号 | 用户ID | 商品类别 | 商品名称 | 金额 | 支付状态 | 下单时间 | 收货城市 |\n| --- | --- | --- | --- | --- | --- | --- | --- |\n| ORD202606070001 | U102938 | 数码 | 无线耳机 | 99.90 | 已支付 | 2026-06-07 10:30:00 | 杭州 |",
    "schema_plan":{
      "scenario":"ecommerce_order",
      "scenario_label":"电商订单测试数据",
      "row_count":1,
      "schema":[
        {"name":"order_id","label":"订单号","type":"string","required":true,"constraints":{}},
        {"name":"user_id","label":"用户ID","type":"string","required":true,"constraints":{}},
        {"name":"product_category","label":"商品类别","type":"enum","required":true,"constraints":{"enum":["数码","家居","服饰","食品","美妆"]}},
        {"name":"product_name","label":"商品名称","type":"string","required":true,"constraints":{}},
        {"name":"amount","label":"金额","type":"number","required":true,"constraints":{"min":10,"max":500}},
        {"name":"payment_status","label":"支付状态","type":"enum","required":true,"constraints":{"enum":["已支付","未支付","退款"]}},
        {"name":"order_time","label":"下单时间","type":"datetime","required":true,"constraints":{}},
        {"name":"shipping_city","label":"收货城市","type":"string","required":true,"constraints":{}}
      ]
    }
  }'
```

## README 截图建议

截图不需要太多，建议 3 张即可:

1. `docs/assets/demo-schema-plan.png`
   - 展示输入需求、模板选择和 Schema 面板。

2. `docs/assets/demo-generated-table.png`
   - 展示模型生成的 Markdown 表格。

3. `docs/assets/demo-validation-report.png`
   - 展示质量检查结果和问题列表。

截图说明建议写法:

- Schema Planner 将自然语言需求转换为字段、类型和约束。
- Table Validator 对生成表格进行确定性检查，发现行数、枚举值和数值范围问题。
- 用户可以复制表格或导出 CSV，用于测试、教学、产品 Demo 和数据看板原型。

当前项目已根据真实 API Demo 生成 3 张展示图:

- [assets/demo-schema-plan.png](assets/demo-schema-plan.png)
- [assets/demo-generated-table.png](assets/demo-generated-table.png)
- [assets/demo-validation-report.png](assets/demo-validation-report.png)

真实运行记录见 [demo-run.md](demo-run.md)。

## 录屏讲解顺序

建议控制在 90 秒内:

1. 10 秒: 项目定位，说明是业务模拟数据生成 Agent。
2. 20 秒: 输入电商订单需求，展示模板选择。
3. 20 秒: 点击 Schema 规划，说明字段和约束来自模板与自然语言。
4. 20 秒: 点击生成表格，说明 LLM 只负责生成，结构由 schema 约束。
5. 20 秒: 点击质量检查，说明 Validator 是工程闭环，避免完全依赖模型输出。

## Demo 注意事项

- 如果没有配置 `DASHSCOPE_API_KEY`，不要演示真实生成，可以只演示 Schema 规划和质量校验 API。
- 如果模型输出不是标准 Markdown 表格，质量检查会提示解析失败，这是符合预期的错误处理。
- 如果模型生成的数据不满足约束，不要回避，可以借此说明 Validator 的意义。
- 项目短期不接入真实企业数据，避免隐私和权限风险；它的实际价值是生成模拟业务数据。
