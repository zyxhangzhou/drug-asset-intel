## MODIFIED Requirements

### Requirement: Same-origin frontend
前端页面与 API SHALL 由同一服务、同一来源提供；前端首页显示快照元信息。非 API 路径中不对应静态文件的请求 SHALL 返回前端首页，使前端页面的链接可以直接打开或刷新；未知的 API 路径 SHALL 仍返回 HTTP 404。

#### Scenario: Frontend shows snapshot metadata
- **WHEN** 打开应用首页
- **THEN** 页面显示快照生成时间与各实体记录数，数据来自元信息接口

#### Scenario: Deep link
- **WHEN** 直接请求前端页面路径（例如某公司的详情页）
- **THEN** 服务返回前端首页，前端显示该页面

#### Scenario: Unknown API path
- **WHEN** 请求不存在的 API 路径
- **THEN** 返回 HTTP 404，不返回前端首页

### Requirement: Shortlist endpoint
API SHALL 提供候选名单接口，返回每家候选公司的主组合（资产、适应症、治疗领域、研发阶段、买方、各维度分数、保守分、乐观分、覆盖率、研究状态、是否入选）。请求可以带五个维度的权重；带权重时 SHALL 按新权重重新计算分数并排序，不修改快照。

#### Scenario: Default weights
- **WHEN** 请求不带权重
- **THEN** 按配置文件的权重返回，与快照中的保守分一致

#### Scenario: Custom weights
- **WHEN** 请求把买方契合度权重设为 0
- **THEN** 返回的保守分与排序按新权重计算
