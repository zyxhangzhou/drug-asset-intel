## Purpose

规定人工复核结果如何以文件形式进入快照：复核文件记录推荐组合、各维度分数与理由、资产权益、下一事件和两句话论点，并引用已登记或人工登记的来源；入选名单只从复核过的公司中产生。

## ADDED Requirements

### Requirement: Review files
每家复核过的公司 SHALL 有一个复核文件，记录：主推荐资产与适应症、主要买方与偏好行、买方需求条目与匹配说明、各维度分数与理由、研究设计 / 可比性 / 结果 / 局限、下一事件（重要性、时间、明确披露或估算）、资产权益状态、两句话论点、复核人。复核文件 SHALL 只在复核人非空时生效；生效的复核文件覆盖自动初筛的对应字段，研究状态变为「已复核」。

#### Scenario: Unverified review is ignored
- **WHEN** 复核文件的复核人为空
- **THEN** 构建忽略该文件，公司保持自动初筛结果

#### Scenario: Review overrides auto score
- **WHEN** 复核文件把买方契合度定为 4 分并引用两条来源
- **THEN** 快照中该维度为 4 分，声明引用这两条来源，研究状态为「已复核」

### Requirement: Manual sources
复核引用的来源 SHALL 是快照中已有的来源，或在人工来源登记文件中登记（来源 ID、URL、标题、发布者、发布日期、访问日期）。引用未登记来源的复核文件 SHALL 使构建失败并指出文件与来源 ID。

#### Scenario: Unknown source id
- **WHEN** 复核文件引用的来源 ID 既不在快照中，也不在人工来源登记中
- **THEN** 构建失败，错误信息包含该文件名与来源 ID

### Requirement: Shortlist rule
入选名单 SHALL 只包含满足以下全部条件的公司，并按保守分排序：研究状态为已复核或深度研究；资产权益不是「待核实」，也不是与推荐交易形式不兼容的「受限」；两句话论点存在且引用了来源。入选公司 SHALL 记录入选理由（两句话论点）。

#### Scenario: Unverified rights block shortlisting
- **WHEN** 公司已复核、保守分最高，但资产权益为「待核实」
- **THEN** 公司不进入入选名单，并在长名单中注明原因

### Requirement: Buyer by target matrix
系统 SHALL 为每个候选公司 × 每个买方记录最佳组合的保守分与一句理由，作为买方 × 标的匹配表。

#### Scenario: Matrix row per buyer
- **WHEN** 公司的资产与两家买方的偏好匹配
- **THEN** 匹配表中这两家买方各有一行该公司的分数与理由

### Requirement: Analyst exclusion
复核文件 SHALL 可以写 `exclude = "<理由>"`。签字生效后，该公司不进入入选名单，长名单的未入选原因写「复核建议不入选：<理由>」。用于资产已授权给他方、主资产失败等规则门槛未覆盖的情形。

#### Scenario: Excluded by the analyst
- **WHEN** 已签字的复核文件写明 exclude = "资产已授权给合作方"
- **THEN** 该公司不入选，未入选原因为「复核建议不入选：资产已授权给合作方」
