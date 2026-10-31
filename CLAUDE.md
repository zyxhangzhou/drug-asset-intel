# 全球创新药资产情报平台（横店资本 FDE 技术作业）

把 10 家大型药企（买方）的资产偏好，与标普生物科技指数 149 家成分公司（标的）的管线对上，筛出 20–30 家有收购 / 授权潜力的公司，交付数据文件 + 可运行样板。
题面与验收标准：`docs/assignment/全球创新药资产情报平台任务说明.pdf`（第二部分第 8 项空白是笔误，已确认）。截止 2026-11-04。

## 数据诚信（最高优先级）

本项目的评分核心是**可追溯**：每个数据点都能回到一手来源。

- 每个数值、日期、临床结论都挂一个 `source_id`，指向来源登记（URL、发布日期、抓取时间）。
- 每条记录标 `fact`（来源原文直接支持）或 `inference`（我们的分析判断），推断另附置信度：高 / 中高 / 中 / 低。
- 找不到来源时，字段留空并标 `unknown`，在缺口清单里记一笔。空值是合格产出；看似合理的估算值是缺陷。
- 结构化字段走官方接口取数：试验状态 / 入组 / 完成时间 → ClinicalTrials.gov API v2；现金 / 债务 / 经营现金流 → SEC EDGAR XBRL；审批 → openFDA / FDA 官网。
- LLM 只做非结构化抽取（新闻稿、财报正文、电话会），每个抽取值附**原文引用片段**，入库前程序校验片段确实出现在源文中。
- 口径沿用对方材料《10家大型药企创新药资产偏好分析》的「来源登记」「方法口径」两张表：来源ID 体系、事实 / 推断划分、置信度档位都与之对齐。

## 原始材料

`docs/assignment/` 下三份对方附件（PDF + 两个 xlsx）只读。任何加工结果写到 `data/` 下。

## 目录

- `src/intel/` Python 包：数据模型与溯源规则（`models.py`、`db.py`）、API 路由（`api.py`）与页面查询（`views.py`）、命令行（`cli.py`）；后续管道加子包
- `tests/` pytest
- `web/` 前端（Vite + React + TS + Ant Design），开发时代理 `/api` 到 8000 端口
- `data/raw/` 抓取的原始响应与文档快照（带抓取时间）
- `data/manual/` 人工核实文件（`verified_by` 非空才生效）：Stage 0 排除名单、`buyer_preference_map.csv`（买方偏好 → 治疗领域与阶段）、`ta_keywords.csv`、`reviews/<TICKER>.toml`（复核文件，同名 `.md` 为研究说明）、`sources.csv`（`MAN-` 人工来源）、`debt_adjustments.csv`、`documents.csv`（待抓取的一手文档清单）、`extractions/<TICKER>.toml`（LLM 抽取复核文件，逐条 accept / reject 后签字）；`trial_aliases.csv`（CT.gov 未登记的研究名 → NCT 编号，带来源）；管线推导修正：`sponsor_aliases.csv`、`sponsor_code_prefixes.csv`、`program_aliases.csv`、`intervention_excludes.csv`
- `config/scoring.toml` 评分权重、EV 档位、长名单家数与人工加入（`longlist_extra`）
- `config/llm.toml` LLM 价格表（注明官方来源）、DeepSeek 高峰时段、各服务商预算上限；账本在 `data/raw/llm/ledger.jsonl`
- `data/processed/intel.db` 数据快照，提交进仓库；应用只读它，管道重建它
- `docs/` 方案、架构、筛选方法、AI 使用说明、核验记录、已知限制

## 数据模型要点

业务值存在各实体表的类型化列里；来源存在 `Claim`（指向 `entity_type, entity_id, field`）与 `Source`。每张实体表的 `BUSINESS_FIELDS` 列出必须有声明支撑的字段。写入规则在 `db.py` 的 `before_flush` 里强制执行：声明须引用已登记来源、推断须带置信度、LLM 声明须带原文片段与模型名、枚举字段只收受控取值。写完数据跑 `intel check-provenance`，非零退出就是有值没来源。

## 约定

- 文档与报告用中文；代码、标识符、commit message 用英文。
- 密钥只放 `.env`（已在 `.gitignore`），仓库只提交 `.env.example`。
- 每次 AI 辅助的抽取或核验，在 `docs/ai-log.md` 记一条：做了什么、用了什么工具、怎么核验、发现的错误。这份日志是 AI 使用说明的原始证据。

## 技术栈

Python 版本与依赖用 uv 管理（`uv sync`、`uv run ...`）；不直接调用系统 `python3` / `pip`。
完整方案见 `docs/plan.md`。

```bash
uv sync                                   # 安装依赖
uv run pytest                             # 测试
uv run ruff check . && uv run ruff format .
uv run intel fetch sec-tickers            # 联网抓取，只写 data/raw/（需 .env 中 SEC_USER_AGENT）
uv run intel fetch links                  # 检查对方来源链接，结果写 data/raw/links/
uv run intel fetch openfda                # openFDA drugsfda 全量导出（裁剪为 NDA / BLA）
uv run intel fetch labels                 # 候选公司获批产品的 FDA 说明书适应症（openFDA drug label）
uv run intel fetch ctgov                  # 候选池试验（约 30 分钟，CT.gov 限速）；已缓存的公司跳过
uv run intel fetch xbrl                   # SEC XBRL companyfacts（裁剪为所需标签）
uv run intel fetch prices                 # Nasdaq 快照日收盘价（非官方来源）
uv run intel docs filings VKTX            # 列出 EDGAR 近期申报及附件 URL，挑选后写入 documents.csv
uv run intel fetch docs                   # 抓取 documents.csv 中的文档，存原文、文本与哈希到 data/raw/docs/
uv run intel extract --dry-run            # 预估抽取费用，不调用模型
uv run intel extract                      # DeepSeek 抽取 + Qwen 盲抽核验，写 data/manual/extractions/；高峰时段默认拒绝
uv run intel extract report               # 费用、片段 / 数字校验通过率、双模型一致率
uv run intel extract --replay             # 用已保存的模型回复重新校验与配对，不调用模型、不计费
                                          # 批量抓取均支持 --only VKTX,MDGL 与 --refresh
uv run intel build                        # 离线从材料 + 缓存 + data/manual/ 重建快照，输出 gaps.csv、longlist.csv、shortlist.csv
uv run intel init-db                      # 建空库（可重复执行）
uv run intel check-provenance             # 溯源完整性检查
uv run intel check-scoring                # 评分检验：高分有事实支撑、前 10 覆盖率、权重敏感性
uv run intel serve                        # API，http://127.0.0.1:8000；/api/shortlist?weights=30,20,20,15,15 按权重重排
cd web && npm install && npm run dev      # 前端开发服务器（代理 /api）
cd web && npm run build                   # 构建前端，intel serve 会托管 web/dist；前端路由（如 /targets/VKTX）可直接打开
docker compose up --build                 # 一条命令启动完整应用，http://localhost:8000
```

## 工作流

规格驱动：变更拆解与顺序在 `mydoc/plans/drug-asset-intel/`（change-plan，读 README 指向的最新版本）；代码类变更用 OpenSpec（`openspec/changes/<name>/`，name 对应计划里的 Ref 列）。研究类变更只在计划里写任务与数据验收标准。变更状态变化时，同一回合更新计划的 Status 与 Status log。
