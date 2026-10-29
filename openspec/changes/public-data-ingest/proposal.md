# Proposal

对应计划变更 C（官方结构化数据拉取），见 `mydoc/plans/drug-asset-intel/`。

## Why

候选池（133 家）目前只有公司名和 CIK。评分（E）、Excel 第二部分第 2–6 项、应用第三部分第 3–5 项，都需要试验、管线、财务和审批数据。这些结构化字段有官方接口可取，应当由程序批量拉取并逐值挂上来源，而不是靠人工或 LLM 填写。

## What Changes

- **ClinicalTrials.gov API v2**：按牵头申办方拉取候选池每家公司的试验，包括状态、阶段、方案、入组、开始与主要完成日期（区分预计 / 实际），以及已发布结果的主要终点。
  - 文本检索之后，再按申办方名称别名表做精确过滤。
  - 每项试验登记为一条来源，链接到该试验页面。
- **管线推导**：从试验的药物类干预和适应症推导管线、适应症与最高登记阶段，全部标为推断（中置信度）。
- **SEC EDGAR XBRL**：读取现金及投资、债务、经营现金流（年初至今）、流通股数。
  - 标签按固定优先顺序取值，不重复相加。
  - 每个值的来源是对应申报文件（按 accession 号登记）。
- **Nasdaq 历史行情**：取快照日收盘价，计算市值。来源标为非官方。
- **资金可支撑时间**：由现金与经营现金流推算，标为推断。
- **openFDA drugsfda**：查询已获批产品与申请号；查无结果视为零个产品，不算失败。
- **快照日**：声明快照日 2026-10-28，记入快照元信息。
- **原始缓存瘦身**：XBRL 只缓存所需标签的原文条目，CT.gov 只缓存所需字段，同时记录完整响应的哈希。
- **数据模型**：
  - 试验增加所属标的、原始适应症与干预文本、日期类型；
  - 新增获批产品实体。

## Capabilities

### New Capabilities

- `trial-registry`：试验拉取、申办方匹配、试验结果、管线推导。
- `company-financials`：XBRL 财务、股价与市值、资金可支撑时间。
- `fda-approvals`：已获批产品。

### Modified Capabilities

- `intel-data-model`：
  - 试验增加所属标的、原始文本与日期类型；
  - 新增获批产品实体。
- `snapshot-build`：
  - 缓存瘦身；
  - 快照日；
  - 外部接口限速。

## Impact

- 新增：`src/intel/ingest/` 下新增三个步骤；`src/intel/fetch.py` 扩展；`data/manual/sponsor_aliases.csv`；`tests/fixtures/`。
- 缓存目录：`data/raw/ctgov/`、`data/raw/sec/companyfacts/`、`data/raw/nasdaq/`、`data/raw/openfda/`。
- 前端实体计数标签同步更新。

**Out of scope**：

- 收购成本估算（F）；
- 公司指引中的数据读出日期（F）；
- 文档抽取（D）；
- 20-F / IFRS 申报主体的财务数据（列为已知限制）；
- 子公司作为申办方的试验，只能通过别名表人工补充。
