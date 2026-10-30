## Purpose

规定大模型抽取结果如何经过人工复核进入快照：每家公司一个抽取复核文件，人工逐条决定接受或拒绝并签字，未签字的抽取结果不进入快照。

## ADDED Requirements

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

#### Scenario: Undecided items counted
- **WHEN** 已签字的文件中有 3 个条目决定为空
- **THEN** 这 3 个条目不进入快照，构建输出报告「未复核 3」

### Requirement: Mapping to snapshot entities
被接受的条目 SHALL 按以下规则写入快照，并为每个字段写一条产生方式为 llm 的声明（带片段、模型名、来源 ID，截至日为文档发布日期）：
- 管线条目写入资产名匹配的管线的作用机制与技术类型；
- 临床结果条目写入 NCT 编号匹配的试验的结果记录；
- 催化事件条目写入该公司的催化事件，并在资产名匹配时关联管线；原文时间表述为季度、半年或年份时换算为日期窗口，无法换算时窗口留空并保留原文表述。
资产名或 NCT 编号在快照中找不到时，条目 SHALL 不写入并记入缺口清单。相对标准治疗的优势 SHALL 写为推断声明并带置信度。

#### Scenario: Unknown asset
- **WHEN** 被接受的管线条目的资产名不匹配任何推导出的管线
- **THEN** 条目不写入，缺口清单记录 ticker、资产名与原因

#### Scenario: Half-year window
- **WHEN** 催化事件的时间表述为「second half of 2027」
- **THEN** 窗口为 2027-07-01 至 2027-12-31，事件声明带原文片段

