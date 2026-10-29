# Spec Delta

## Purpose

把对方提供的《10家大型药企创新药资产偏好分析》完整导入为买方画像，保留对方的来源ID 体系与事实 / 推断口径，使每个买方字段都能追溯到对方材料的具体单元格与一手来源。

## ADDED Requirements

### Requirement: Source register import
系统 SHALL 把对方「来源登记」表的每一行登记为来源，来源ID、公司、资料类型、原始日期文本、标题、链接与用途原样保留，来源类型为 mnc_material。对方工作簿本身 SHALL 另登记为一条来源，记录本地路径与内容哈希。

#### Scenario: Register matches the sheet row for row
- **WHEN** 导入完成
- **THEN** 来源登记表的每一行都有同 ID 的来源，链接与原始日期文本与单元格一致，且没有多余的 mnc_material 来源（工作簿本身除外）

### Requirement: Buyer summary import
系统 SHALL 为「执行摘要」的每一行建立一个买方，并为每个非空字段生成声明。声明类别按对方「方法口径」划分：最新财务与战略信号、核心证据为 fact；优先治疗领域、优先技术类型、最可能交易阶段 / 形式、购买动因为 inference，置信度取该行「判断置信度」。单元格列出多个来源ID 时，每个ID 生成一条声明。每条声明的备注记录原表名与单元格坐标。

#### Scenario: Multi-source cell yields one claim per source
- **WHEN** 某买方「核心证据」单元格的来源ID 为 `MRK-1;MRK-2;MRK-3`
- **THEN** 该字段有 3 条 fact 声明，分别引用这 3 个来源ID，取值与单元格一致

#### Scenario: Inference carries the sheet's confidence
- **WHEN** 辉瑞一行的「判断置信度」为"中高"
- **THEN** 辉瑞优先治疗领域的声明类别为 inference，置信度为 medium_high

### Requirement: Preference import
系统 SHALL 把「治疗领域分析」与「技术类型分析」的每一行导入为买方偏好，保留优先级与各列内容。事实证据为 fact；领域 / 技术类型名称、需求类型、目标资产画像、分析推断、购买逻辑、理想阶段、建议交易形式为 inference。这两张表没有置信度列，inference 置信度继承该买方在执行摘要中的判断置信度，并在声明备注中注明是继承所得。

#### Scenario: Preferences keep sheet order
- **WHEN** 导入默沙东的治疗领域偏好
- **THEN** 依次得到优先级 1、2、3 的偏好，名称分别与原表一致

### Requirement: Buyer overview import
系统 SHALL 导入「MNC买方概览」的买方能力评估与产品专利到期两张子表，数值按原币种、原单位（十亿）保存；声明以对方工作簿为来源，原表「数据来源」或「口径备注」的文字记入声明备注。由公式计算的单元格（如美国收入占比）不入库。含"待核实"标记的数值单元格、以及内容仅为"待核实"的单元格 SHALL 留空并记入缺口清单；其余含该标记的文本单元格原样保留（含标记），在声明备注中注明，并以"部分待核实"记入缺口清单。

#### Scenario: Unverified number becomes a gap
- **WHEN** 某收入单元格内容为"待核实"
- **THEN** 对应字段为空，缺口清单中有一条指明表名、单元格坐标与原文的记录

#### Scenario: Partially unverified text keeps its caveat
- **WHEN** 某备注单元格内容为"近年无大型并购[待核实]"
- **THEN** 字段保留原文（含标记），声明备注注明含待核实标记，缺口清单中有一条"部分待核实"记录

#### Scenario: Overview values match the sheet
- **WHEN** 导入默沙东的能力评估行
- **THEN** FY2025 总收入为 65.01、币种为 USD，并有一条以工作簿为来源的 fact 声明

### Requirement: Method notes are retained
系统 SHALL 保存「方法口径」表的全部条目，作为买方画像的口径说明，供应用展示。

#### Scenario: Method notes available
- **WHEN** 导入完成
- **THEN** 可以查到「事实与推断」条目及其原文说明
