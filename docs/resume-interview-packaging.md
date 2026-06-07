# DataSheet Agent 简历与面试包装

本文档用于校招/实习简历、GitHub 项目介绍和面试讲述。所有表达都基于当前源码已实现能力，避免把项目包装成不存在的大型平台。

## 项目标题

推荐标题:

```text
DataSheet Agent: 面向业务场景的智能表格生成与质量校验系统
```

简历较短时可写:

```text
业务表格生成 Agent
```

## 一句话简介

HR 版:

```text
一个用于快速生成电商订单、CRM 线索、招聘候选人等模拟业务数据的 AI 表格生成工具，可用于测试、教学、产品 Demo 和数据看板原型。
```

技术面试官版:

```text
基于 Vue + Flask + OpenAI-compatible LLM API 构建的表格生成 Agent，通过业务模板、Schema Planner 和 Table Validator，将自然语言需求转为可校验、可导出的模拟业务表格。
```

## 简历 Bullet Points

推荐 4 条版本:

```text
- 基于 Vue + Flask 重构本科毕设表格生成项目，将原先“LLM API 直接生成表格”升级为面向业务模拟数据的 DataSheet Agent。
- 设计电商订单、学生信息、CRM 销售线索、招聘候选人 4 类业务模板，支持从自然语言中解析行数、字段类型、枚举值和数值范围等 schema 约束。
- 实现 Schema Planner，将用户需求转换为结构化字段定义，并在生成阶段注入 LLM Prompt，降低字段不一致、行数漂移和约束失效问题。
- 实现 Table Validator，对 Markdown 表格进行确定性质量校验，检查行数、必填字段、枚举值和数值范围，并输出问题列表与校验报告。
- 抽象 OpenAI-compatible LLM 调用层，将 API Key 迁移至环境变量配置，支持 Qwen/DashScope 默认模型并保留多 provider 扩展能力。
```

如果简历篇幅紧张，可压缩成 3 条:

```text
- 将本科毕设中的 LLM 表格生成工具升级为 DataSheet Agent，支持业务模板、schema 规划、表格生成、质量校验和 CSV 导出闭环。
- 设计 Schema Planner 和 Table Validator，解析自然语言中的行数、字段、枚举值、数值范围，并对生成的 Markdown 表格进行确定性校验。
- 基于 Vue + Flask + OpenAI-compatible API 实现前后端交互、模型配置、会话隔离和错误处理，API Key 通过环境变量管理。
```

## 技术关键词

不夸大版:

```text
Vue, Flask, Qwen/DashScope, OpenAI-compatible API, Prompt Engineering, Schema Planning, Data Validation, Markdown Table Parsing, CSV Export, REST API
```

偏 Agent 岗位:

```text
AI Agent Workflow, Tool Use, Schema Planner, Validator, LLM Prompt Constraints, OpenAI-compatible LLM Client, Business Data Simulation
```

偏后端岗位:

```text
Flask, REST API, Configuration Management, Schema Validation, Unit Testing, Error Handling, Session Isolation
```

## 1 分钟项目讲述稿

```text
这个项目最初是我的本科毕设，核心能力是调用大模型 API 根据自然语言生成 Markdown 表格。但我觉得如果只停留在“调 API 生成表格”，在现在的校招里竞争力比较弱，所以我把它升级成了一个面向业务模拟数据的表格生成 Agent。

它的实际场景是测试、教学、产品 Demo 或数据看板原型，经常需要构造电商订单、CRM 线索、招聘候选人这类模拟数据，而真实数据又涉及隐私，手工造数据也比较低效。

现在系统的流程是: 用户输入业务需求后，先通过业务模板和 Schema Planner 规划字段、类型、必填项、枚举值和数值范围，再把 schema 作为约束注入给 LLM 生成表格。生成之后，Table Validator 会对 Markdown 表格做确定性检查，比如行数是否正确、字段是否缺失、枚举值是否合法、金额是否越界，最后给出校验报告并支持 CSV 导出。

所以它不是单纯的 API 套壳，而是形成了“需求理解、schema 规划、LLM 生成、质量校验、导出”的轻量 Agent 闭环。
```

## 面试官可能追问

### 1. 这个项目的意义是什么?

推荐回答:

```text
它解决的是模拟业务数据构造的问题。很多测试、教学、Demo 和数据分析原型都需要结构化表格数据，但真实数据涉及隐私和权限，不能随便使用；手工构造又慢，而且容易遗漏字段和约束。这个项目通过自然语言和业务模板快速生成接近业务语义的模拟数据，并用 schema 和 validator 提高生成结果的可控性。
```

### 2. 为什么说它是 Agent，而不是普通 LLM API 调用?

推荐回答:

```text
普通 LLM API 调用是用户输入 prompt，模型直接返回结果，结果质量主要靠人工判断。这个项目加入了任务流程: 先识别业务场景，再规划 schema，再约束 LLM 生成，最后调用 validator 检查输出是否满足规则。虽然它不是复杂多 Agent 系统，但已经具备“规划、调用、检查”的轻量 Agent 工作流。
```

### 3. Schema Planner 是怎么做的?

推荐回答:

```text
短期版本没有做复杂 NLP，而是采用业务模板 + 规则解析。模板提供默认字段和约束，例如电商订单里的金额、支付状态、下单时间。用户自然语言中的行数、金额范围、枚举值会覆盖模板默认约束。这样实现成本低，但在 Demo 和实际使用中比纯 prompt 更稳定，也便于解释和测试。
```

### 4. Table Validator 检查什么?

推荐回答:

```text
它会解析 Markdown 表格，检查是否能识别表头和数据行，然后根据 schema 检查目标行数、必填字段、必填值、枚举值和数值范围。目前它是确定性规则校验，不依赖 LLM，所以能作为 LLM 输出后的质量兜底。
```

### 5. 项目目前有什么不足?

推荐回答:

```text
目前它还是轻量版本，主要聚焦业务模板、schema 规划和校验闭环。限制包括: Markdown 表格解析只覆盖标准格式；Schema Planner 主要用模板和规则，不是复杂语义解析；质量校验还没有自动修复闭环；前端 UI 也偏毕设风格。后续可以继续做自动修正、Excel/JSON 导出、任务历史和更清晰的 Agent 编排层。
```

### 6. 如果继续优化，你会做什么?

推荐回答:

```text
我会优先做两件事。第一是自动修正: Validator 发现问题后，把问题列表和原始表格重新交给 LLM，让它只修正不合格行。第二是增强导出和复用: 支持导出 schema JSON、Excel 文件，以及保存常用业务模板。这样比盲目加登录或数据库更贴近这个项目的核心价值。
```

## 面试讲述重点

建议重点强调:

- 项目从旧毕设升级而来，有真实上下文。
- 升级目标不是堆技术，而是提升业务意义和工程闭环。
- Agent 感体现在“规划 + 生成 + 校验”，不是强行说成多 Agent。
- Validator 是亮点，因为它让系统不完全依赖 LLM 一次输出。
- 有明确边界，不接真实企业数据，不做复杂平台，不虚构能力。

避免这样说:

- “实现了企业级数据治理平台。”
- “可以完全自动生成高质量数据。”
- “用了复杂多 Agent 协作。”
- “支持所有业务场景。”
- “自动保证 LLM 输出一定正确。”

更稳妥的说法:

- “实现了轻量 Agent 工作流。”
- “通过 schema 和 validator 提高生成可控性。”
- “当前支持 4 类内置业务模板，也支持自定义字段。”
- “适合测试、教学、产品 Demo 和数据分析原型中的模拟数据构造。”

## GitHub README 展示重点

README 首页建议按这个顺序展示:

1. 项目定位: 面向业务场景的表格生成 Agent。
2. 项目意义: 解决模拟业务数据构造问题。
3. 核心能力: 业务模板、Schema Planner、LLM 生成、Table Validator、CSV 导出。
4. 工作流图: 展示规划、生成、校验闭环。
5. Demo 示例: 电商订单测试数据。
6. 技术架构: Vue + Flask + LLM Client + Planner + Validator。
7. 快速开始: 后端、前端、环境变量。
8. 测试命令: 单元测试和前端构建。
9. 后续规划: 自动修正、Excel/JSON 导出、模板复用。

## 最终推荐方向

```text
DataSheet Agent 应定位为“面向测试、教学和产品 Demo 的业务模拟数据生成 Agent”。它不是为了替代 Excel，也不是做复杂数据平台，而是把自然语言需求、业务 schema、LLM 表格生成和确定性质量校验串成一个可演示、可解释、适合本科项目升级的轻量工程闭环。
```
