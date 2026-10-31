# extraction-review Specification

## Purpose
规定大模型抽取结果如何经过人工复核进入快照：每家公司一个抽取复核文件，人工逐条决定接受或拒绝并签字，未签字的抽取结果不进入快照。

## Requirements

### Requirement: Extraction review file
抽取命令 SHALL 为每家公司写出抽取复核文件 `data/manual/extractions/<TICKER>.toml`。每个条目记录：条目类型、取值、原文片段、来源 ID、主模型名与返回的模型名、核验状态（一致、分歧、单模型）、核验模型的取值与片段（若有）、决定、备注。一致的条目决定 SHALL 预填为接受；分歧与单模型的条目决定 SHALL 留空。文件顶层 `verified_by` SHALL 为空。重新抽取 SHALL 保留已有条目的人工决定与备注，只追加新条目。

#### Scenario: Agreed item prefilled
- **WHEN** 一个临床结果条目两模型一致
- **THEN** 复核文件中该条目的决定为接受，`verified_by` 为空

#### Scenario: Rerun keeps decisions
- **WHEN** 人工已拒绝某条目后重新运行抽取
- **THEN** 该条目的决定仍为拒绝，新抽出的条目追加在后

### Requirement: Signed review takes effect
抽取复核文件 SHALL 只在 `verified_by` 非空时生效。生效时，只有决定为接受的条目进入快照；决定为空的条目视为未复核，不进入快照，并在构建输出中计数。人工可以修改条目取值，但原文片段 SHALL 仍须通过片段校验。

#### Scenario: Unsigned file ignored
- **WHEN** 复核文件 `verified_by` 为空
- **THEN** 构建不载入其中任何条目

#### Scenario: New items clear the signature
- **WHEN** 已签字的复核文件在重新抽取时追加了新条目
- **THEN** `verified_by` 被清空，人工复核新条目后重新签字才生效

#### Scenario: Undecided items counted
- **WHEN** 已签字的文件中有 3 个条目决定为空
- **THEN** 这 3 个条目不进入快照，构建输出报告「未复核 3」

### Requirement: Mapping to snapshot entities
被接受的条目 SHALL 按以下规则写入快照，并为每个字段写一条产生方式为 llm 的声明（带片段、模型名、来源 ID，截至日为文档发布日期）：
- 管线条目写入资产名匹配的管线的作用机制与技术类型。资产名与管线名各自拆成全名、去掉括号部分的名称、括号内各代码，比较时去掉连接词与标点；两边任一名称完全相同即命中，命中多条管线时取全名相同者，仍不唯一则不写入。没有完全相同的名称时，资产名包含于唯一一条管线名、或唯一一条管线名（至少 5 个字符）包含于资产名，也算命中；
- 临床结果条目写入匹配试验的结果记录。试验字段含 NCT 编号时按编号匹配；否则按名称对照到该公司快照中的试验，名称来自 CT.gov 登记的简称、标题括号内名称、标题冒号前名称、含数字的申办方研究编号，以及复核人已签字的人工对照表。名称按字母、数字分词比较，试验字段包含某名称的完整词序列即命中；同时命中多个名称时取最具体的名称（一个名称是另一个的完整词序列时取较长者）；仍命中多个不同试验时不写入，记缺口。写入的声明备注 SHALL 注明对照依据；
- 催化事件条目写入该公司的催化事件，并在资产名匹配时关联管线；原文时间表述为季度、半年或年份时换算为日期窗口，无法换算时窗口留空并保留原文表述。
资产名或 NCT 编号在快照中找不到时，条目 SHALL 不写入并记入缺口清单。相对标准治疗的优势 SHALL 写为推断声明并带置信度。

#### Scenario: Unknown asset
- **WHEN** 被接受的管线条目的资产名不匹配任何推导出的管线
- **THEN** 条目不写入，缺口清单记录 ticker、资产名与原因

#### Scenario: Asset matched by bracketed code
- **WHEN** 资产名为「clemidsogene lanparvovec (RGX-121)」，公司管线有「RGX-121」与「RGX-121-3102」
- **THEN** 条目写入管线 RGX-121

#### Scenario: Asset matched by name without brackets
- **WHEN** 资产名为「defactinib」，管线有「DEFACTINIB (PART A - VS-6063, VS-6063)」与「AVUTOMETINIB AND DEFACTINIB」
- **THEN** 条目写入前者

#### Scenario: Half-year window
- **WHEN** 催化事件的时间表述为「second half of 2027」
- **THEN** 窗口为 2027-07-01 至 2027-12-31，事件声明带原文片段

#### Scenario: Trial matched by registry acronym
- **WHEN** 临床结果条目的试验字段为「SHASTA-3 study」，快照中该公司试验 NCT06347003 在 CT.gov 登记的简称为「SHASTA-3」
- **THEN** 结果写入 NCT06347003，声明备注注明按 CT.gov 简称对照

#### Scenario: Trial matched by sponsor study id
- **WHEN** 试验字段为「VK2735-102 Maintenance Study」，快照中 NCT07838740 在 CT.gov 登记的申办方研究编号为「VK2735-102」
- **THEN** 结果写入 NCT07838740，声明备注注明按 CT.gov 登记名称对照

#### Scenario: Ambiguous trial name
- **WHEN** 试验字段为「SHASTA-3 and SHASTA-4」
- **THEN** 条目不写入，缺口清单记录试验名称不唯一

#### Scenario: Trial matched by signed manual alias
- **WHEN** 人工对照表有已签字的一行「VKTX, VK2735-102, NCT00000002, MAN-VKTX-4」，试验字段为「VK2735-102 Maintenance Study」
- **THEN** 结果写入 NCT00000002，声明备注注明按人工对照及其来源

#### Scenario: Unsigned manual alias ignored
- **WHEN** 人工对照表的一行复核人为空
- **THEN** 该行不参与对照

#### Scenario: Most specific name wins
- **WHEN** 公司有简称为「MUIR」与「MUIR-3」的两项试验，试验字段为「MUIR-3 trial」
- **THEN** 结果写入简称为「MUIR-3」的试验
