## MODIFIED Requirements

### Requirement: Review files
每家复核过的公司 SHALL 有一个复核文件，记录：主推荐资产与适应症、主要买方与偏好行、买方需求条目与匹配说明、各维度分数与理由、研究设计 / 可比性 / 结果 / 局限、下一事件（重要性、时间、明确披露或估算）、资产权益状态、推荐逻辑、复核人。复核文件 SHALL 只在复核人非空时生效；生效的复核文件覆盖自动初筛的对应字段，研究状态变为「已复核」。

复核文件 SHALL 可以记录收购成本估算：下限与上限（美元）、计算方法、引用的来源与置信度；估算 SHALL 作为推断写入该公司财务快照的收购成本字段。复核文件 SHALL 可以把研究状态标为「深度研究」，此时 SHALL 同时有临床数据、下一事件与收购成本估算，否则构建失败并指出文件与缺少的部分。

#### Scenario: Unverified review is ignored
- **WHEN** 复核文件的复核人为空
- **THEN** 构建忽略该文件，公司保持自动初筛结果

#### Scenario: Review overrides auto score
- **WHEN** 复核文件把买方契合度定为 4 分并引用两条来源
- **THEN** 快照中该维度为 4 分，声明引用这两条来源，研究状态为「已复核」

#### Scenario: Acquisition cost estimate
- **WHEN** 已签字的复核文件写了收购成本估算 20–30 亿美元并引用溢价研究来源与快照行情来源
- **THEN** 快照中该公司的收购成本下限与上限为这两个值，声明为推断、带置信度并引用这些来源

#### Scenario: Deep research without a cost estimate
- **WHEN** 复核文件标为深度研究但没有收购成本估算
- **THEN** 构建失败，错误信息包含文件名与「收购成本估算」

### Requirement: Shortlist rule
入选名单 SHALL 只包含满足以下全部条件的公司，并按保守分排序：研究状态为已复核或深度研究；资产权益不是「待核实」，也不是与推荐交易形式不兼容的「受限」；推荐逻辑存在且引用了来源。入选公司 SHALL 记录入选理由（推荐逻辑）。

#### Scenario: Unverified rights block shortlisting
- **WHEN** 公司已复核、保守分最高，但资产权益为「待核实」
- **THEN** 公司不进入入选名单，并在长名单中注明原因
