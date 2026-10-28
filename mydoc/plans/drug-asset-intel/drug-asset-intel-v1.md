# 全球创新药资产情报平台 — v1

- Status: confirmed
- Supersedes: none
- Date: 2026-10-28
- Session: 69dd30f7-bc86-4fc2-b36d-dea57ab87358
- Trigger: initial — 首版拆解

## 背景

- 题面：`docs/assignment/全球创新药资产情报平台任务说明.pdf`。三部分：候选公司筛选、基线数据文件（Excel）、应用方案与样板；外加 AI 使用说明、已知限制、后续计划。截止 2026-11-04（周三），计划 11-03 晚提交。
- 整体方案、数据模型、架构、风险见 `docs/plan.md`；数据诚信规则见 `CLAUDE.md`。
- 技术栈：Python 3.12（uv）、FastAPI、SQLite、Vite + React + Ant Design、Docker → Render。LLM 用 OpenAI 兼容接口，DeepSeek 主抽取、Qwen 交叉核验。
- 材料中已确认的事实：APGE 已被 AbbVie 收购但仍在指数清单；指数含买方体量药企（ABBV、AMGN、GILD、REGN、VRTX、BIIB）与工具 / 诊断公司；题面第二部分第 8 项空白为笔误。

### 拆分原则

- **代码类**变更走 OpenSpec（proposal + spec delta + tasks），场景即验收标准。
- **研究类**变更不写行为 spec，只在本计划里写任务和数据验收标准（完整度、来源覆盖、核验通过率）。
- 同一数据来源、同一时间点完成、互相没有独立交付价值的工作合并为一个变更，控制在一周内可管理的数量。

## Changes

| Order | ID | Change | 类型 | Ref | Depends on | Status |
|---|---|---|---|---|---|---|
| 1 | A | 项目骨架与数据模型 | 代码 | `project-skeleton` | — | planned |
| 2 | B | 基础材料导入与 Stage 0 排除 | 代码 + 研究 | `baseline-ingest` | A | planned |
| 3 | C | 官方结构化数据拉取（CT.gov + EDGAR） | 代码 | `public-data-ingest` | B | planned |
| 3 | D | LLM 抽取管道 | 代码 | `llm-extraction` | A | planned |
| 4 | E | 评分、买方匹配与候选名单 | 代码 + 研究 | `scoring-shortlist` | B, C | planned |
| 5 | F | 深度填充 3–5 家 | 研究 | — | D, E | planned |
| 5 | G | Web 应用样板 | 代码 | `web-app` | B, C, E | planned |
| 6 | H | Excel 导出与抽样核验 | 代码 + 研究 | `export-verify` | F, G | planned |
| 7 | I | 部署与交付文档 | 交付 | `deploy-docs` | H | planned |
| — | J | 带引用的 RAG 问答（可选） | 代码 | `ask-platform` | D, I | planned |

同一 Order 的变更可并行。

### A — 项目骨架与数据模型

- Goal: 一个能跑起来的空壳，承载后续所有变更。
- Scope: in — uv 项目、FastAPI 骨架、SQLite schema（Buyer、BuyerPreference、Target、Program、ProgramIndication、Trial、TrialResult、Catalyst、FinancialSnapshot、Match、Source、Claim）、Vite + React 前端壳、Dockerfile、`.env.example`；out — 任何真实数据。
- Acceptance: `docker compose up` 后前端能访问并调用到 API 健康检查；建表脚本可重复执行；Claim 表能表达 fact / inference、置信度、原文片段、source_id。

### B — 基础材料导入与 Stage 0 排除

- Goal: 把对方给的两份材料变成库里的数据，并完成第一轮规则排除。
- Scope: in — 导入 MNC Excel 全部 6 张表（保留对方来源ID）；导入 149 家指数清单；ticker → CIK 映射（SEC `company_tickers.json`）；Stage 0 排除规则与逐条核实；out — 评分。
- Acceptance: 10 家买方及其偏好、来源登记与原表逐条一致；149 家每家要么带排除原因与来源，要么进入候选池；排除名单经人工逐个核实。

### C — 官方结构化数据拉取

- Goal: 对候选池自动填充试验与财务字段，证明管道可扩展。
- Scope: in — ClinicalTrials.gov API v2（状态、设计、入组、预计完成）；申办方别名表；SEC EDGAR XBRL（现金、债务、经营现金流、股本）；资金可支撑期计算；股价来源定案并标注；原始响应缓存到 `data/raw/`；out — LLM 抽取。
- Acceptance: 候选池每家都有试验和财务记录，或在缺口清单中写明原因；每个数值带 source_id 与截至日；外国申报主体列为已知限制。

### D — LLM 抽取管道

- Goal: 从非结构化文本抽取字段，且每个值都可验证。
- Scope: in — 可切换服务商的 LLM 客户端（`.env` 配置）；文档切块 + SQLite FTS5 检索；JSON schema 抽取；原文片段校验；DeepSeek / Qwen 双模型交叉核验；不一致进人工复核队列；out — 具体公司的研究结论。
- Acceptance: 对一份样例文档跑通全流程；片段命中率、双模型一致率可统计输出；校验失败的条目不会入库。

### E — 评分、买方匹配与候选名单

- Goal: 从候选池选出 20–30 家，并说明每家匹配哪家买方、为什么。
- Scope: in — 五维加权评分（权重配置化）；买方 × 标的匹配表；入选理由；选出 3–5 家深度对象；筛选方法文档初稿；out — 深度临床数据。
- Acceptance: 名单 20–30 家，每家有分数、匹配买方与理由，全部标为推断并给置信度；调整权重可重新生成排名。

### F — 深度填充 3–5 家

- Goal: 按题面第二部分 1–7 项把少数公司做透。
- Scope: in — 核心管线、MoA、适应症与阶段；关键临床数据及相对标准治疗的优势；12–24 个月催化事件；收购成本估算区间；out — 其余候选公司的同等深度（在交付说明中注明完成情况）。
- Acceptance: 深度对象的题面 1–7 项字段齐全或标 `unknown`；每个字段有来源；全部经过人工复核。

### G — Web 应用样板

- Goal: 覆盖题面第三部分 6 项能力。
- Scope: in — 买方画像页；候选列表（筛选、排序、对比）；公司详情（管线、适应症、阶段）；试验视图（状态、方案、入组、预计完成与读出）；已完成试验结果；任意数据点跳转来源；out — 登录、编辑。
- Acceptance: 6 项能力各有一条可演示的路径；演示主线（买方需求 → 候选 → 管线 → 试验 → 来源原文）能一次走通。

### H — Excel 导出与抽样核验

- Goal: 产出数据交付物，并量化数据质量。
- Scope: in — 从数据库导出《候选生物制药公司列表》（含来源列、发布日期、更新时间）；抽查约 50 个字段，写 `docs/verification.md`；out — 修复以外的新数据。
- Acceptance: Excel 覆盖题面第二部分 1–7 项；核验报告给出准确率与错误类型，发现的错误已修正。

### I — 部署与交付文档

- Goal: 题面第四部分 6 项交付物齐全。
- Scope: in — 部署到 Render；运行说明；架构说明；筛选方法与数据来源；AI 使用说明（基于 `docs/ai-log.md`）；已知限制与 4 周计划；演示彩排。
- Acceptance: 公网地址可访问；交付清单逐项有对应文件。

### J — 带引用的 RAG 问答（可选）

- Goal: 用自然语言问候选公司和试验，答案带引用。
- Scope: in — 只基于快照中的来源回答，找不到就明说；out — 联网检索。
- Acceptance: 仅在 11-02 前进度有富余时启动；否则移入 4 周计划。

## Out of scope

- 149 家全量深度研究：一周内不现实，题面允许 3–5 家深度填充。
- 定时增量更新、变更提醒、用户体系与审核流：属于生产系统，放入 4 周计划。
- 收购概率的量化模型：证据不足以支撑概率，只给定性匹配与成本区间。

## Follow-ups

（暂无）

## Open questions

- [NEEDS DECISION] 股价来源（非官方行情的具体选择）— 在 C 中由 Claude 提出、用户确认。

## Status log

- 2026-10-28 · 69dd30f7-bc86-4fc2-b36d-dea57ab87358 · v1 起草（draft）
- 2026-10-28 · 69dd30f7-bc86-4fc2-b36d-dea57ab87358 · v1 用户确认（confirmed）
