## ADDED Requirements

### Requirement: Scoring outputs
构建 SHALL 在导入数据之后执行评分，并在快照旁输出两个文件：复核长名单（按乐观分排序，含保守分、乐观分、覆盖率、研究状态、未入选原因）与入选名单（按保守分排序的入选公司及两句话论点）。复核池 SHALL 为乐观分前 N 家（有推导资产），加上配置 `longlist_extra` 中人工列出的公司。

#### Scenario: Lists written on build
- **WHEN** 执行构建
- **THEN** 快照旁生成长名单与入选名单文件；没有复核过的公司时入选名单只有表头

#### Scenario: Manual addition to the review pool
- **WHEN** 配置 `longlist_extra` 列出某家有推导资产、但乐观分不在前 N 的公司
- **THEN** 该公司在长名单中标为进入复核池
