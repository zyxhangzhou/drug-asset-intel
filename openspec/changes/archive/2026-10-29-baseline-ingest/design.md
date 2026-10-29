# Design

## Context

A 已提供数据模型、`before_flush` 写入校验与 `check-provenance`。对方材料的实际结构（已逐表检查）：

- 「执行摘要」：10 行，每行带「判断置信度」和「来源ID」（`MRK-1;MRK-2`）。
- 「治疗领域分析」「技术类型分析」：各 30 行，带来源 ID，不带置信度。
- 「来源登记」：43 行。原始日期精度不一（`2026-08`、`2026`、`2026-07-30`）；有一条链接是 `D:\...` 本地路径。
- 「MNC买方概览」：两张子表（第 5–15 行能力评估、第 18–56 行专利到期）；没有来源 ID 列，含公式单元格和"[待核实]"标记，公司名写法不统一（`Merck`、`J&J`、`AZ`）。
- 指数清单：149 行，没有空值和重复。

## Goals / Non-Goals

**Goals:**

- 与原表逐格可对账：每条声明记录表名和单元格坐标。
- 快照能离线、确定性地重建。

**Non-Goals:**

- 复核对方材料中的事实是否准确：沿用对方口径，在应用里标注"来自对方材料"。
- 增量更新。

## Decisions

### 1. 抓取与构建分离：`intel fetch <target>` 与 `intel build`

- `fetch sec-tickers`、`fetch links` 只写 `data/raw/`。
- `build` 只读三类输入：`docs/assignment/`、`data/raw/`、`data/manual/`。它先写临时文件 `intel.db.tmp`，全部成功后再 `os.replace` 覆盖正式快照。
- 后续变更（C、D）往 `build` 里追加步骤，不再各自建库。
- 备选：抓取时顺手写库。放弃原因：联网结果不可复现，而且一次失败会留下半截库。

### 2. 对方材料的来源结构

- 「来源登记」43 行登记为 `mnc_material` 来源，ID 原样保留。
- 两个工作簿各登记一条来源：`MNC-WB`、`SPSIBI-WB`，`local_path` 指向 `docs/assignment/` 下的文件，`content_hash` 用 sha256。概览表的声明引用 `MNC-WB`。
- `fetched_at` 统一取材料接收日 2026-10-28，写成模块常量。原因是用文件修改时间会让重建结果不确定。

### 3. 列 → 字段 → 类别映射写成声明式表

每张表的映射写成一个常量表，行内容是 `(列名, 字段名, fact|inference)`。导入逻辑共用这张表；测试也从同一张表出发，逐格与原表对账。

类别依据对方「方法口径」：最新信号和证据为事实；"最希望 / 最可能"、资产画像、阶段、交易形式为推断。「购买动因」「分析推断」「购买逻辑」本身是分析结论，归为推断。

### 4. 偏好表按列存储

`BuyerPreference` 删除 `detail`，改为以下列，每列都是业务字段：

- `label`
- `need_type`
- `target_profile`
- `evidence`
- `analysis`（对应「分析推断」或「购买逻辑」）
- `ideal_stage`
- `deal_form`

### 5. 新增 `BuyerFinancial`、`BuyerProductLoe`

- **`BuyerFinancial`**：财年、币种、总收入、美国收入、现金及短期投资、总债务、净债务、自由现金流、资本配置备注、近期并购、重点领域。
- **`BuyerProductLoe`**：产品、全球收入、美国收入、美国 LOE 时点、仿制药 / 生物类似药进展、防御策略、口径备注。

规则：

- **按列位置读取。** 某些行缺值时，其余值不会左移，所以要按列位置而不是按非空值的顺序读取。
- **数值单元格。** 能解析为数字才写入；解析不了、或带有"待核实"的，字段留空并记入缺口。
- **文本单元格。** 内容只有"待核实"时留空；其余原样保留，连同原文的标记一起保存，并以"部分待核实"计入缺口。原因是这类单元格多数只有一小段待核实（如"美国收入拆分待核实；净债务/EBITDA 1.2x……"），整格清空会丢掉大量有来源的信息。
- **[计算值]、[管理层预测] 一类标记。** 保留在文本中，不留空。
- **公式列。** 用 `data_only=True` 读取，美国占比列直接跳过，由应用自行计算。
- **公司名。** 用别名表映射到 ticker，例如 `J&J → JNJ`、`AZ → AZN`、`Novo → NVO`。别名表之外的名字直接报错，不猜。

### 6. 来源日期与链接状态

- `Source` 增加 `published_date_text`（原文）、`link_status`（`LinkStatus` 枚举）、`link_checked_at`；另增加 `publisher`、`doc_kind`、`note`，原样保存来源登记的「公司」「资料类型」「要点」三列。
- 只有 `YYYY-MM-DD` 格式才解析成 `published_date`。
- `fetch links` 先用 HEAD 请求，不支持时回退到 GET。超时 15 秒，请求间隔 0.5 秒，结果写入 `data/raw/links/mnc_sources.json`；`build` 读取这份结果填写状态。
- 403 归为 blocked 而不是 broken，因为药企官网常拒绝脚本访问。

### 7. Stage 0：人工核实 CSV

文件为 `data/manual/stage0_exclusions.csv`，列如下：

- `ticker`
- `category`
- `reason`
- `kind`
- `confidence`
- `source_id`
- `source_type`
- `source_url`
- `source_title`
- `published_date`
- `accessed_on`（打开来源核对的日期，作为抓取时间）
- `verified_by`

流程：

1. AI 起草，`verified_by` 留空。
2. 用户逐行打开来源确认，在 `verified_by` 填上姓名缩写。
3. `build` 只应用 `verified_by` 非空的行，并打印未核实的行数。

`Target` 增加 `exclusion_category` 列（`ExclusionCategory` 枚举）。

备选：直接把排除名单写进代码。放弃原因：核实动作无处留痕，而且名单本身就是需要提交、可审阅的数据。

### 8. CIK 映射

- 来源是 `https://www.sec.gov/files/company_tickers.json`，缓存到 `data/raw/sec/company_tickers.json`，来源 ID 为 `SEC-TICKERS`，类型 `sec_filing`。
- 匹配时，ticker 统一大写；`.` 与 `-` 视为等价，例如 `BRK.B` / `BRK-B`。
- 请求头的 User-Agent 只从配置读取，未配置时拒绝执行。

### 9. 方法口径与缺口清单

- 「方法口径」存入非领域表 `method_note`（来源工作簿、项目、说明），不参与溯源检查。
- 缺口清单写入 `data/processed/gaps.csv`（实体、标识、字段、原因、位置），与快照一起提交。

## Risks / Trade-offs

- [对方材料的事实本身可能有误] → 声明备注写明来自对方材料；抽样核验放在 H。
- [药企官网屏蔽脚本，链接检查大量 blocked] → blocked 与 broken 分开统计；只有 broken 才算失效。
- [`company_tickers.json` 不含已退市或已被收购的公司（如 APGE）] → 留空，记入缺口，并作为排除核实的旁证线索；不作为排除依据。
- [删除偏好表的 `detail` 属于结构变化] → 快照由 `build` 整体重建，没有存量数据需要迁移。
