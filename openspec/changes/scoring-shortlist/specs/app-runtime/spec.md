## ADDED Requirements

### Requirement: Shortlist endpoint
API SHALL 提供候选名单接口，返回每家候选公司的主组合（资产、适应症、买方、各维度分数、保守分、乐观分、覆盖率、研究状态、是否入选）。请求可以带五个维度的权重；带权重时 SHALL 按新权重重新计算分数并排序，不修改快照。

#### Scenario: Default weights
- **WHEN** 请求不带权重
- **THEN** 按配置文件的权重返回，与快照中的保守分一致

#### Scenario: Custom weights
- **WHEN** 请求把买方契合度权重设为 0
- **THEN** 返回的保守分与排序按新权重计算
