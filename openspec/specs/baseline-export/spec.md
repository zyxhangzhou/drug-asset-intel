# baseline-export Specification

## Purpose

规定《候选生物制药公司列表》Excel 交付文件：内容覆盖题面第二部分 1–7 项，每个关键值可以追到来源，并说明各公司的完成程度。

## Requirements

### Requirement: Export from the snapshot
系统 SHALL 提供一条离线命令，只读数据快照生成《候选生物制药公司列表》Excel，不联网、不修改快照。同一快照两次导出的单元格内容 SHALL 相同。

#### Scenario: Offline export
- **WHEN** 在没有网络的环境运行导出命令
- **THEN** 生成 Excel 文件，快照文件未被修改

### Requirement: Contents cover the brief
Excel SHALL 包含：候选公司表（只列入选公司，按名次排序；基本信息、研究状态、入选理由、推荐逻辑、市值、现金、债务、可支撑月数、企业价值、收购成本估算）；其余评估公司表（其余有主推荐方向的公司，注明未入选原因）；管线表、临床数据表与催化事件表只列入选公司的行。管线表（药物、作用机制、技术类型、适应症、治疗领域、研发阶段）；临床数据表（试验、终点、结果、对照、相对标准治疗的优势）；催化事件表（未来 12–24 个月，注明出处是公司披露、复核结论还是 CT.gov 预计主要完成日）；来源表；缺口表；说明表。

#### Scenario: Shortlisted company row
- **WHEN** 打开候选公司表中一家入选公司的行
- **THEN** 该行有名次、入选理由、推荐逻辑与财务各列，空值单元格为空白而不是估算值

#### Scenario: Company not shortlisted
- **WHEN** 一家已评分但未入选的公司
- **THEN** 它不在候选公司表，而在其余评估公司表，并写明未入选原因

#### Scenario: Catalyst from CT.gov
- **WHEN** 催化事件来自 CT.gov 预计主要完成日
- **THEN** 该行的出处列写明「CT.gov 预计主要完成日（推断）」，并带该试验登记的来源 ID

### Requirement: Source columns
每张数据表的关键字段 SHALL 有对应的来源列，列出支撑该值的来源 ID，并标明事实或推断（推断附置信度）。来源表 SHALL 列出被引用的每个来源的 ID、标题、类型、发布者、发布日期、抓取时间与网址。数据表引用的每个来源 ID SHALL 都能在来源表中找到。

#### Scenario: Every cited source is listed
- **WHEN** 导出完成后收集所有数据表来源列中的来源 ID
- **THEN** 每个 ID 都出现在来源表中

### Requirement: Completion statement
说明表 SHALL 写明快照日期、导出时间、事实 / 推断 / LLM 抽取的区分方法，以及按研究状态（深度研究、已复核、自动初筛）统计的公司数与各状态填充了哪些字段，回应题面「说明其余公司的完成情况」。

#### Scenario: Status counts match the snapshot
- **WHEN** 读取说明表的研究状态统计
- **THEN** 各状态公司数之和等于候选公司表与其余评估公司表的行数之和，并与快照一致
