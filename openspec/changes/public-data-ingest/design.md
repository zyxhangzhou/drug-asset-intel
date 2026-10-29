# Design

## Context

B 交付了构建框架：`intel fetch` 联网、只写 `data/raw/`；`intel build` 离线，从零重建快照并输出缺口清单。候选池为 133 家（未排除的标的），其中 130 家有 CIK。

实测接口结果（2026-10-29）：

- **XBRL companyfacts**：每家 1.6–3.6 MB，全量缓存约 270 MB，不能提交进仓库。
- **CT.gov**：按申办方检索，全字段的响应 INCY 有 24 MB，只取所需字段后为 2.6 MB。`query.lead` 是全文检索，会混入其他申办方的试验。
- **openFDA**：没有匹配时返回 404。sponsor 名为大写缩写，例如 `MADRIGAL`。
- **Nasdaq 历史行情**：纳斯达克和纽交所上市的股票都可用。价格是 `"$214.165"` 形式的字符串。
- **经营现金流**：XBRL 中是年初至今的累计值，例如 VKTX 为 2026-01-01 至 06-30。

## Goals / Non-Goals

**Goals:**

- 每个结构化数值都可以回到一个可点击的官方页面：试验页、申报文件、Drugs@FDA、行情页。
- 抓取可以中断后续跑；单家公司失败不影响其他公司。

**Non-Goals:**

- 管线推导做到完全准确：推导结果标为推断，深度对象的管线在 F 中人工复核。
- 20-F / IFRS 申报主体。

## Decisions

### 1. 来源粒度：一条记录对应一个来源

| 数据 | 来源 ID | 链接 | 来源类型 |
|---|---|---|---|
| 试验 | `CTG-<NCT>` | `https://clinicaltrials.gov/study/<NCT>` | `ctgov` |
| XBRL 申报文件 | `SEC-<accn>` | 该申报的 EDGAR 索引页 | `sec_xbrl` |
| 股价 | `NASDAQ-<TICKER>-<交易日>` | Nasdaq 历史行情页 | `market_data` |
| openFDA 申请 | `FDA-<申请号>` | Drugs@FDA 申请页 | `openfda` |

备选是一家公司一个来源。放弃原因：应用里要从具体数值跳到具体原文，粒度太粗做不到。

### 2. 缓存瘦身

| 接口 | 缓存内容 | 文件 |
|---|---|---|
| XBRL | 只保留标签清单中的 `units` 条目（原样），另存 `entityName` | `data/raw/sec/companyfacts/<CIK>.json` |
| CT.gov | 请求时用 `fields` 参数只取 identification、status、sponsor、design、conditions、armsInterventions、`hasResults` | `data/raw/ctgov/<TICKER>.json` |
| CT.gov 试验结果 | 对 `hasResults` 为真的试验，再单独请求 `resultsSection.outcomeMeasuresModule` | `data/raw/ctgov/results/<NCT>.json` |
| Nasdaq | 快照日前 10 个交易日 | `data/raw/nasdaq/<TICKER>.json` |
| openFDA | 原样保存（体量小） | `data/raw/openfda/<TICKER>.json` |

- 旁注文件 `.meta.json` 记录请求 URL、抓取时间和完整响应的 sha256。
- 已有缓存默认跳过；加 `--refresh` 才重新抓取。

### 3. 申办方别名

- 别名由三部分组成：
  - 指数公司名去掉后缀（Inc.、Corporation、plc、N.V.、AG、Ltd.、Holding(s) 等）；
  - SEC 登记名；
  - `data/manual/sponsor_aliases.csv`（列：`ticker`、`alias`、`note`）。
- 规范化：转小写，去掉标点与后缀。
- 检索时每个别名各查一次，合并结果、按 NCT 去重，再按规范化后的牵头申办方名称精确过滤。
- openFDA 用同一套别名，查询 `sponsor_name` 时转大写。

### 4. XBRL 标签清单

| 字段 | 取值规则 |
|---|---|
| 现金及投资 | 合并标签优先：`CashCashEquivalentsAndShortTermInvestments`、`CashCashEquivalentsAndMarketableSecuritiesCurrent`（自定义扩展标签不使用）。没有合并标签时相加：`CashAndCashEquivalentsAtCarryingValue`，加上第一个命中的流动性投资标签（`ShortTermInvestments` / `MarketableSecuritiesCurrent` / `AvailableForSaleSecuritiesDebtSecuritiesCurrent`），再加第一个命中的非流动投资标签（`MarketableSecuritiesNoncurrent` / `AvailableForSaleSecuritiesDebtSecuritiesNoncurrent` / `LongTermInvestments`） |
| 债务 | 优先 `LongTermDebt`（含一年内到期部分）；否则 `LongTermDebtNoncurrent` + `LongTermDebtCurrent`；否则 `ConvertibleNotesPayable` / `ConvertibleDebtNoncurrent`。都没有时字段留空，不填 0：留空表示没有申报，与"零债务"不同 |
| 经营现金流 | `NetCashProvidedByUsedInOperatingActivities` |
| 流通股 | `dei:EntityCommonStockSharesOutstanding` |

通用规则：

- 只用 form 为 10-K / 10-Q 的条目。
- 各分项必须取同一个期间结束日：以现金标签的最新期间为准，其他分项取同一结束日的条目，没有该期间就不计入，并在备注中注明。
- 同一期间有多次申报时，取申报日最晚的那条。

### 5. 推导的管线

- **哪些干预算管线**：只取类型为 DRUG / BIOLOGICAL / GENETIC 的干预。
- **排除**：安慰剂、溶媒、标准治疗等词，以及 `data/manual/intervention_excludes.csv` 中的名称。
- **合并**：名称规范化（去括号内容、剂量、给药途径与剂型词）后合并为同一管线。
- **适应症**：取原始 condition 文本，排除 "Healthy" 类条目；每个（管线, 适应症）一行。
- **阶段**：取该适应症下试验的最高登记阶段。
- **试验关联**：试验关联到它第一个干预与第一个适应症对应的管线适应症；无法关联的试验只挂在公司下。
- **已知缺陷**：联用药、对照药可能被当成公司管线，例如在别家试验里的 pembrolizumab。处理办法：全部标为推断（中置信度）；在 E 筛选和 F 深挖时人工剔除，剔除结果写进排除文件。

### 6. 阶段映射

| CT.gov 登记阶段 | 本库研发阶段 |
|---|---|
| EARLY_PHASE1 / PHASE1 | `phase1` |
| PHASE1 + PHASE2 | `phase1_2` |
| PHASE2 | `phase2` |
| PHASE2 + PHASE3 | `phase2_3` |
| PHASE3 | `phase3` |
| PHASE4 | `approved`（上市后研究意味着已获批） |
| NA / 缺失 | `unknown` |

### 7. 模型变化

- **`Trial`**：
  - 增加 `target_id`（必填）、`conditions`、`interventions`（原文，以 `; ` 连接）、`enrollment_type`、`primary_completion_type`；
  - 把 `enrollment_target` / `enrollment_actual` 合并为 `enrollment`，并加类型列。
- **新增 `ApprovedProduct`**：`target_id`、`application_number`、`brand_name`、`active_ingredients`、`first_approval_date`。
- **`TrialResult`**：增加 `analysis`，记录 p 值与方法。
- **`snapshot_meta`**：增加 `snapshot_date`；`/api/meta` 返回该字段。

### 8. 快照日

快照日为常量 `SNAPSHOT_DATE = 2026-10-28`（最近一个完整交易日）。多数公司第三季度 10-Q 在 11 月初才申报，所以财务大多截至 2026-06-30。这一点列为已知限制。

## Risks / Trade-offs

- [联用药 / 对照药被推导为管线] → 标为推断；在 E / F 中人工剔除，并维护排除文件。
- [子公司作为申办方（Roivant 旗下各 Vant、BridgeBio 子公司）导致试验少算] → 用别名文件补充；匹配不到的列入缺口清单。
- [Nasdaq 接口未公开文档，可能变化] → 缓存原始响应；失败时股价与市值留空，记入缺口。
- [XBRL 标签使用不一致] → 固定清单加备注记录实际命中的标签；在 H 中抽样核验。
