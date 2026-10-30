# 全球创新药资产情报平台 — v3

- Status: confirmed
- Supersedes: v2
- Date: 2026-10-30
- Session: 69dd30f7-bc86-4fc2-b36d-dea57ab87358
- Trigger: re-scope — 用户复读题面「AI 使用说明」5 问后确认：AI 产出需要可量化的核验证据；35 份复核为用户授权代签，必须补人工抽查并如实披露

## Changes since v2

| ID | Was | Now | Why |
|---|---|---|---|
| D | 片段校验 + 双模型核验 | 另加每次调用的 token 与费用记录、预算上限（DeepSeek 余额 20 元） | AI 使用说明要报用量与成本；预算有限 |
| F | 3–5 家 | 确定 5 家：RGNX、CLDX、VKTX、ARWR、VSTM（用户 2026-10-30 确认） | 分属 5 家买方、5 个领域，均在入选名单前 5 |
| H | 抽查约 50 个字段 | 分层随机抽样（结构化字段 + 复核文件字段 + LLM 抽取字段），按层报告错误率；另加提交前用户随机抽查 5 份复核文件 | 「如何验证 AI 产出」需要可量化证据；35 份复核为代签，需人工抽查后如实披露 |
| I | AI 使用说明（基于日志） | 按题面 5 问成文：工具与用量、参与环节表、4 层验证、AI 自查发现的缺陷清单、自动化与人工审核边界；如实写明复核为 AI 起草、用户抽查 | 直接对应题面要求；数字全部取自日志与核验结果 |

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
| 1 | A | 项目骨架与数据模型 | 代码 | `project-skeleton` | — | archived（`openspec/changes/archive/2026-10-29-project-skeleton`，主 spec：`app-runtime`、`intel-data-model`） |
| 2 | B | 基础材料导入与 Stage 0 排除 | 代码 + 研究 | `baseline-ingest` | A | archived（`openspec/changes/archive/2026-10-29-baseline-ingest`） |
| 3 | C | 官方结构化数据拉取（CT.gov + EDGAR + openFDA） | 代码 | `public-data-ingest` | B | archived（`openspec/changes/archive/2026-10-29-public-data-ingest`） |
| 3 | D | 文档获取存档与 LLM 抽取管道 | 代码 | `llm-extraction` | A | in progress（17/18，待用户复核签字样例） |
| 4 | E | 评分、买方匹配与候选名单 | 代码 + 研究 | `scoring-shortlist` | B, C | archived（`openspec/changes/archive/2026-10-30-scoring-shortlist`；45 家复核签字，入选 30 家） |
| 5 | F | 深度填充 3–5 家 | 研究 | — | D, E | planned |
| 5 | G | Web 应用样板 | 代码 | `web-app` | B, C, E | planned |
| 6 | H | Excel 导出与抽样核验 | 代码 + 研究 | `export-verify` | F, G | planned |
| 7 | I | 部署与交付文档 | 交付 | `deploy-docs` | H | planned |
| — | J | 带引用的 RAG 问答（可选） | 代码 | `ask-platform` | D, I | planned |

同一 Order 的变更可并行。

## 题面覆盖与进度

按题面（`docs/assignment/全球创新药资产情报平台任务说明.pdf`）的章节，列出每一项由哪些变更完成、在哪个变更收尾。变更状态变化时同步更新"进度"列。

| 题面 | 要求 | 由哪些变更完成 | 收尾变更 | 进度 |
|---|---|---|---|---|
| 二·第一部分 | 学习 10 家买方偏好 | B（导入对方材料，逐格保留来源与事实 / 推断口径） | B | 已完成 |
| 二·第一部分 | 结合 149 家最新公开信息筛出 20–30 家 | B（Stage 0 排除）→ C（试验、财务、审批数据）→ E（五维评分、买方匹配） | E | Stage 0 完成（候选池 133 家）；C 已归档（试验、财务、审批数据就绪）；E 已归档：复核池 45 家全部复核签字，入选 30 家（`data/processed/shortlist.csv`）——第一部分完成 |
| 二·第一部分 | 说明筛选逻辑、评价维度、判断依据，区分事实与推断 | E（方法文档初稿）→ I（定稿） | I | 初稿：`docs/scoring-rules.md`（含样例检验与已知限制） |
| 二·第二部分 1 | 公司基本信息及入选理由 | B（公司名、CIK）+ E（入选理由） | E | 已完成：30 家入选公司均有两句话论点及来源 |
| 二·第二部分 2–3 | 核心管线、作用机制、适应症、各适应症研发阶段 | C（CT.gov 试验 → 适应症与阶段）+ D / F（文档抽取：作用机制、核心管线） | F | C 部分完成：132 家 3205 项试验、推导管线 1392 条（推断） |
| 二·第二部分 4 | 关键临床数据及相对标准治疗的优势 | C（CT.gov 已发布结果）+ F（新闻稿、会议数据，经 D 抽取） | F | C 部分完成：1481 条已发布结果（主要终点） |
| 二·第二部分 5 | 未来 12–24 个月催化事件 | C（预计完成日期）+ F（公司披露的读出、PDUFA 日期） | F | C 部分完成：试验预计完成日期；读出时间待 F |
| 二·第二部分 6 | 市值、现金、债务、资金可支撑时间、收购成本估算 | C（XBRL、股价、可支撑期）+ F（收购成本区间） | F | C 部分完成：133 家现金 / 债务 / 市值 / 可支撑期；收购成本待 F |
| 二·第二部分 7 | 信息来源、发布日期、数据更新时间 | A（来源与声明模型）+ 每个变更写入时附来源 | H（导出时带来源列） | 模型已就绪 |
| 二·第二部分 | Excel 文件；3–5 家深度填充并说明其余完成情况 | F（深度填充）→ H（导出、抽样核验） | H | 未开始 |
| 二·第三部分 1 | 查看 10 家买方的财务、战略信号、并购与授权信息 | B（数据）+ G（页面） | G | 数据已就绪 |
| 二·第三部分 2 | 浏览、筛选、比较候选公司 | E（数据）+ G | G | 未开始 |
| 二·第三部分 3 | 查看管线、适应症、研发阶段 | C / F（数据）+ G | G | 数据已就绪（推导管线） |
| 二·第三部分 4 | 试验状态、方案、招募、预计结束与读出时间 | C（数据）+ G | G | 数据已就绪 |
| 二·第三部分 5 | 已完成试验的主要结果 | C / F（数据）+ G | G | 数据已就绪 |
| 二·第三部分 6 | 从关键数据跳转到来源 | A（溯源模型）+ G | G | 模型已就绪 |
| 三 | AI 使用说明（工具、环节、验证、降低幻觉、自动化与人工审核的边界） | 全程记 `docs/ai-log.md` → H（分层抽样错误率、用户抽查）→ I（按 5 问成文） | I | 日志 26 条；验证方法已在用（溯源强制、原文比对、检验命令、人工抽查） |
| 四 1–6 | 应用与运行说明、Excel、架构说明、源码与配置、方法与 AI 说明、限制与后续计划 | H（Excel）+ I（部署与文档） | I | 未开始 |
| 演示 | 30–45 分钟演示与讨论（含四周计划） | I（彩排） | I | 未开始 |

里程碑：

- E 归档：第一部分完成。
- H 归档：第二部分完成。
- G 归档：第三部分功能完成。
- I 归档：全部交付物齐全。

### A — 项目骨架与数据模型

- Goal: 一个能跑起来的空壳，承载后续所有变更。
- Scope: in — uv 项目、FastAPI 骨架、SQLite schema（Buyer、BuyerPreference、Target、Program、ProgramIndication、Trial、TrialResult、Catalyst、FinancialSnapshot、Match、Source、Claim；Source 含来源类型、本地存档路径、内容哈希）、Vite + React 前端壳、Dockerfile、`.env.example`；out — 任何真实数据。
- Acceptance: `docker compose up` 后前端能访问并调用到 API 健康检查；建表脚本可重复执行；Claim 表能表达 fact / inference、置信度、原文片段、source_id。

### B — 基础材料导入与 Stage 0 排除

- Goal: 把对方给的两份材料变成库里的数据，并完成第一轮规则排除。
- Scope: in — 导入 MNC Excel 全部 6 张表（保留对方来源ID）；导入 149 家指数清单；ticker → CIK 映射（SEC `company_tickers.json`）；Stage 0 排除规则与逐条核实；对方来源登记的链接可达性检查（失效链接标出，不替换）；out — 评分。
- Acceptance: 10 家买方及其偏好、来源登记与原表逐条一致；149 家每家要么带排除原因与来源，要么进入候选池；排除名单经人工逐个核实。

### C — 官方结构化数据拉取

- Goal: 对候选池自动填充试验与财务字段，证明管道可扩展。
- Scope: in — ClinicalTrials.gov API v2（状态、设计、入组、预计完成）；申办方别名表；SEC EDGAR XBRL companyfacts（现金、债务、经营现金流、股本）；openFDA drugsfda（已获批产品与申请号）；CT.gov 已发布的试验结果（resultsSection）；资金可支撑期计算；股价来源定案并标注；原始响应缓存到 `data/raw/`；out — LLM 抽取。
- Acceptance: 候选池每家都有试验和财务记录，或在缺口清单中写明原因；每个数值带 source_id 与截至日；外国申报主体列为已知限制。

### D — 文档获取存档与 LLM 抽取管道

- Goal: 把非结构化一手文档取回、存档，并从中抽取字段，且每个值都可验证。
- Scope: in — 文档获取：EDGAR submissions API 定位 10-K / 10-Q / 8-K（含 Ex-99.1 新闻稿、投资者演示），按 URL 抓取 IR 页面与 PDF；HTML / PDF 转文本；原文存档到 `data/raw/` 并登记 Source（类型、抓取时间、哈希）；限速与 SEC User-Agent；可切换服务商的 LLM 客户端（`.env` 配置）；每次调用记录 token 与费用，超预算上限即停止；文档切块 + SQLite FTS5 检索；JSON schema 抽取；原文片段校验；DeepSeek / Qwen 双模型交叉核验；不一致进人工复核队列；out — 具体公司的研究结论。
- Acceptance: 对一份样例文档跑通全流程；片段命中率、双模型一致率、累计费用可统计输出；校验失败的条目不会入库。

### E — 评分、买方匹配与候选名单

- Goal: 从候选池选出 20–30 家，并说明每家匹配哪家买方、为什么。
- Scope: in — 五维加权评分（权重配置化）；买方 × 标的匹配表；入选理由；选出 3–5 家深度对象；筛选方法文档初稿；out — 深度临床数据。
- Acceptance: 名单 20–30 家，每家有分数、匹配买方与理由，全部标为推断并给置信度；调整权重可重新生成排名。

### F — 深度填充 5 家

- Goal: 按题面第二部分 1–7 项把 RGNX、CLDX、VKTX、ARWR、VSTM 做透（用户 2026-10-30 确认）。
- Scope: in — Claude 辅助检索并列出每家深度对象的一手文档 URL（IR 新闻稿、投资者演示、会议摘要、FDA 页面），由 D 的管道抓取存档后再抽取；核心管线、MoA、适应症与阶段；关键临床数据及相对标准治疗的优势；12–24 个月催化事件；收购成本估算区间；out — 其余候选公司的同等深度（在交付说明中注明完成情况）。
- Acceptance: 深度对象的题面 1–7 项字段齐全或标 `unknown`；每个字段有来源；全部经过人工复核。

### G — Web 应用样板

- Goal: 覆盖题面第三部分 6 项能力。
- Scope: in — 买方画像页；候选列表（筛选、排序、对比）；公司详情（管线、适应症、阶段）；试验视图（状态、方案、入组、预计完成与读出）；已完成试验结果；任意数据点跳转来源；out — 登录、编辑。
- Acceptance: 6 项能力各有一条可演示的路径；演示主线（买方需求 → 候选 → 管线 → 试验 → 来源原文）能一次走通。

### H — Excel 导出与抽样核验

- Goal: 产出数据交付物，并量化数据质量。
- Scope: in — 从数据库导出《候选生物制药公司列表》（含来源列、发布日期、更新时间）；分层随机抽样核验（结构化字段、复核文件字段、LLM 抽取字段各一层，固定随机种子），写 `docs/verification.md`；提交前用户随机抽查 5 份复核文件（对照 `.md` 中的原文链接核对权益与关键数据），结果记入日志；out — 修复以外的新数据。
- Acceptance: Excel 覆盖题面第二部分 1–7 项；核验报告按层给出错误率与错误类型，发现的错误已修正；用户抽查结果（份数、错误数）已记录。

### I — 部署与交付文档

- Goal: 题面第四部分 6 项交付物齐全。
- Scope: in — 部署到 Render；运行说明；架构说明；筛选方法与数据来源；AI 使用说明（按题面 5 问成文：工具与用量、环节表、验证方法、AI 自查发现的缺陷清单、自动化与人工审核边界；数字取自 `docs/ai-log.md` 与核验报告；如实写明复核为 AI 起草、用户抽查）；已知限制与 4 周计划；演示彩排。
- Acceptance: 公网地址可访问；交付清单逐项有对应文件。

### J — 带引用的 RAG 问答（可选）

- Goal: 用自然语言问候选公司和试验，答案带引用。
- Scope: in — 只基于快照中的来源回答，找不到就明说；out — 联网检索。
- Acceptance: 仅在 11-02 前进度有富余时启动；否则移入 4 周计划。

## Out of scope

- 付费数据：电话会逐字稿（Seeking Alpha 等）、付费会议摘要、付费数据库。改用公司 8-K 披露的新闻稿与投资者演示。

- 149 家全量深度研究：一周内不现实，题面允许 3–5 家深度填充。
- 定时增量更新、变更提醒、用户体系与审核流：属于生产系统，放入 4 周计划。
- 收购概率的量化模型：证据不足以支撑概率，只给定性匹配与成本区间。

## Follow-ups

（暂无）

## Open questions

- [RESOLVED 2026-10-29] 股价来源：Nasdaq 官网历史行情接口（api.nasdaq.com），取快照日收盘价，来源类型 market_data，标为非官方。曾选 Stooq，实测已加 JavaScript 验证、脚本无法下载，不予绕过，改选 Nasdaq。

## Status log

- 2026-10-29 · 69dd30f7-bc86-4fc2-b36d-dea57ab87358 · v2：信息源获取方式逐项落到 A / B / C / D / F

- 2026-10-28 · 69dd30f7-bc86-4fc2-b36d-dea57ab87358 · v1 起草（draft）
- 2026-10-28 · 69dd30f7-bc86-4fc2-b36d-dea57ab87358 · v1 用户确认（confirmed）
- 2026-10-28 · 69dd30f7-bc86-4fc2-b36d-dea57ab87358 · A OpenSpec 产物完成（proposal / specs / design / tasks），strict 校验通过
- 2026-10-29 · 69dd30f7-bc86-4fc2-b36d-dea57ab87358 · A 实现完成：28 个测试通过，docker compose 启动验证通过
- 2026-10-29 · 69dd30f7-bc86-4fc2-b36d-dea57ab87358 · A verify 通过（0 critical / 0 warning / 2 suggestion：前端与容器场景待 G 补端到端测试；溯源缺口场景待 C 用现金字段覆盖），已同步主 spec 并归档
- 2026-10-29 · 69dd30f7-bc86-4fc2-b36d-dea57ab87358 · B OpenSpec 产物完成（proposal / 4 个 spec / design / tasks），strict 校验通过；新增 buyer-profiles、target-universe、snapshot-build 三个能力
- 2026-10-29 · 69dd30f7-bc86-4fc2-b36d-dea57ab87358 · B 实现 12/15：导入、构建、抓取完成，61 个测试通过；Stage 0 草案 16 家待人工核实；SEC CIK 抓取等 .env 配置
- 2026-10-29 · 69dd30f7-bc86-4fc2-b36d-dea57ab87358 · 新增「题面覆盖与进度」表（题面各项 → 变更 → 收尾变更）；SEC CIK 抓取完成：146/149 映射，未映射的 3 家正是 Stage 0 草案中的已收购公司（APGE、NUVL、CPRX）
- 2026-10-29 · 69dd30f7-bc86-4fc2-b36d-dea57ab87358 · B 用户核实 Stage 0（16 家全部认可）；verify 无严重问题，归档并同步主 spec（新增 buyer-profiles、target-universe、snapshot-build；intel-data-model 修改 3 条、新增 1 条）
- 2026-10-29 · 69dd30f7-bc86-4fc2-b36d-dea57ab87358 · 股价来源定案：Nasdaq 历史行情接口（Stooq 实测需浏览器验证，放弃）
- 2026-10-29 · 69dd30f7-bc86-4fc2-b36d-dea57ab87358 · C OpenSpec 产物完成（trial-registry、company-financials、fda-approvals 三个新能力；试点测得 XBRL 全量缓存约 270 MB，改为裁剪缓存）
- 2026-10-29 · 69dd30f7-bc86-4fc2-b36d-dea57ab87358 · C 实现完成：132/133 家有试验（TRAX 无登记），133 家有财务快照，51 个获批产品，3587 条来源，check-provenance 为 0；市值交叉核对发现并修复流通股过期问题；待用户抽查 5 家
- 2026-10-29 · 69dd30f7-bc86-4fc2-b36d-dea57ab87358 · C 归档：人工抽查 VKTX / RLAY / MDGL / MRNA / IMVT 全部一致；SEC 来源链接改为申报索引页；spec 同步到 trial-registry、company-financials、fda-approvals、snapshot-build、intel-data-model
- 2026-10-30 · 69dd30f7-bc86-4fc2-b36d-dea57ab87358 · E 开始：评分细则经用户批准（docs/scoring-rules.md），OpenSpec `scoring-shortlist` 已建
- 2026-10-30 · 69dd30f7-bc86-4fc2-b36d-dea57ab87358 · E 自动初筛完成：用户确认买方偏好映射 30 行；全量构建长名单 40 家（Merck 18、AbbVie 11），check-provenance 0、check-scoring 通过；下一步首批 10 家复核
- 2026-10-30 · 69dd30f7-bc86-4fc2-b36d-dea57ab87358 · E 修复：openFDA 申请人缩写导致 18 家漏关联获批产品、ROIV 无管线；修复后长名单 SPRY、SRPT 进，IONS、VNDA 出
- 2026-10-30 · 69dd30f7-bc86-4fc2-b36d-dea57ab87358 · E：用户确认 IONS、VNDA 手工加入复核池（config longlist_extra）；首批复核 10 家：CLDX、GERN、NTLA、OLMA、VKTX、RLAY、ALT、BHVN、DNLI、VIR；来源限 SEC 申报、论文 / 学会摘要、FDA（另含公司公告）
- 2026-10-30 · 69dd30f7-bc86-4fc2-b36d-dea57ab87358 · E：首批 10 家复核草稿完成并做样例检验（用户分档）；按用户确认修正 ALT 临床分、DNLI 注记、催化可跨适应症；修复 4 类数据问题（资金月数、债务标签、合作方代号、已上市阶段）；待用户签字
- 2026-10-30 · 69dd30f7-bc86-4fc2-b36d-dea57ab87358 · E：首批 10 家复核签字生效（入选名单 10 家）；样例检验完成，权重暂不调整（待全部复核后重测敏感性）；开始其余 35 家复核
- 2026-10-30 · 69dd30f7-bc86-4fc2-b36d-dea57ab87358 · E：45 家复核草稿完成，按用户确认统一权益口径并修正 MPLT、CMPX、NRIX、CABA；人工债务调整与说明书回退检索；临时入选 30 家，待用户确认签字
- 2026-10-30 · 69dd30f7-bc86-4fc2-b36d-dea57ab87358 · v3：D 加费用记录与预算上限；F 定 5 家；H 改分层随机抽样并加用户抽查 5 份复核；I 按题面 AI 使用 5 问成文
- 2026-10-30 · 69dd30f7-bc86-4fc2-b36d-dea57ab87358 · E 归档：20/20 任务完成；新增主 spec asset-scoring、analyst-review，同步 app-runtime、company-financials、fda-approvals、intel-data-model、snapshot-build、trial-registry；第一部分完成
- 2026-10-30 · 69dd30f7-bc86-4fc2-b36d-dea57ab87358 · D：建 OpenSpec 变更 `llm-extraction`（提案、4 份规格、设计、18 项任务）；核实 DeepSeek 官方价格与高峰时段；待用户确认后实现
- 2026-10-30 · 69dd30f7-bc86-4fc2-b36d-dea57ab87358 · D：实现完成 17/18 任务；VKTX 样例 5 次运行累计 0.76 元，关闭思考模式、逐字段一致判定、按片段配对、空条目与无年份时间拒收；待用户复核签字样例（任务 6.2）
