## MODIFIED Requirements

### Requirement: Mapping to snapshot entities
被接受的条目 SHALL 按以下规则写入快照，并为每个字段写一条产生方式为 llm 的声明（带片段、模型名、来源 ID，截至日为文档发布日期）：
- 管线条目写入资产名匹配的管线的作用机制与技术类型；
- 临床结果条目写入匹配试验的结果记录。试验字段含 NCT 编号时按编号匹配；否则按名称对照到该公司快照中的试验，名称来自 CT.gov 登记的简称、标题括号内名称、标题冒号前名称，以及复核人已签字的人工对照表。名称按字母、数字分词比较，试验字段包含某名称的完整词序列即命中；同时命中多个名称时取最具体的名称（一个名称是另一个的完整词序列时取较长者）；仍命中多个不同试验时不写入，记缺口。写入的声明备注 SHALL 注明对照依据；
- 催化事件条目写入该公司的催化事件，并在资产名匹配时关联管线；原文时间表述为季度、半年或年份时换算为日期窗口，无法换算时窗口留空并保留原文表述。
资产名或 NCT 编号在快照中找不到时，条目 SHALL 不写入并记入缺口清单。相对标准治疗的优势 SHALL 写为推断声明并带置信度。

#### Scenario: Unknown asset
- **WHEN** 被接受的管线条目的资产名不匹配任何推导出的管线
- **THEN** 条目不写入，缺口清单记录 ticker、资产名与原因

#### Scenario: Half-year window
- **WHEN** 催化事件的时间表述为「second half of 2027」
- **THEN** 窗口为 2027-07-01 至 2027-12-31，事件声明带原文片段

#### Scenario: Trial matched by registry acronym
- **WHEN** 临床结果条目的试验字段为「SHASTA-3 study」，快照中该公司试验 NCT06347003 在 CT.gov 登记的简称为「SHASTA-3」
- **THEN** 结果写入 NCT06347003，声明备注注明按 CT.gov 简称对照

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
