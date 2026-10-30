# app-runtime Specification

## Purpose

规定情报平台应用如何运行：基于只读数据快照对外提供 API 与前端，配置通过环境变量注入，本地与部署环境行为一致。

## Requirements

### Requirement: Read-only snapshot serving
应用运行时 SHALL 以只读方式打开数据快照，运行期间不调用任何外部数据源。

#### Scenario: Write attempt fails at runtime
- **WHEN** 应用运行期间任何代码路径尝试写入数据快照
- **THEN** 写入失败，快照文件内容不变

#### Scenario: Missing snapshot
- **WHEN** 启动时配置的快照文件不存在
- **THEN** 应用启动失败并给出指明快照路径的错误信息

### Requirement: Health endpoint
应用 SHALL 提供健康检查接口，返回服务状态。

#### Scenario: Healthy service
- **WHEN** 请求健康检查接口
- **THEN** 返回 HTTP 200 与表示正常的状态字段

### Requirement: Snapshot metadata endpoint
应用 SHALL 提供快照元信息接口，返回快照生成时间与每个领域实体的记录数。

#### Scenario: Empty snapshot
- **WHEN** 快照刚由建库命令生成、尚无数据，请求元信息接口
- **THEN** 返回快照生成时间，且每个实体的记录数为 0

### Requirement: Same-origin frontend
前端页面与 API SHALL 由同一服务、同一来源提供；前端首页显示快照元信息。

#### Scenario: Frontend shows snapshot metadata
- **WHEN** 打开应用首页
- **THEN** 页面显示快照生成时间与各实体记录数，数据来自元信息接口

### Requirement: Environment-based configuration
应用与数据管道的配置 SHALL 来自环境变量；仓库提供列出全部配置项与占位值的示例文件，且不包含任何真实密钥。

#### Scenario: Example config is complete
- **WHEN** 代码读取某个配置项
- **THEN** 该配置项出现在示例配置文件中

### Requirement: One-command local start
系统 SHALL 支持用一条命令在本地构建并启动完整应用（API 加前端）。

#### Scenario: Local container start
- **WHEN** 在仓库根目录执行一条启动命令
- **THEN** 应用在本地端口可访问，健康检查返回正常

### Requirement: Shortlist endpoint
API SHALL 提供候选名单接口，返回每家候选公司的主组合（资产、适应症、买方、各维度分数、保守分、乐观分、覆盖率、研究状态、是否入选）。请求可以带五个维度的权重；带权重时 SHALL 按新权重重新计算分数并排序，不修改快照。

#### Scenario: Default weights
- **WHEN** 请求不带权重
- **THEN** 按配置文件的权重返回，与快照中的保守分一致

#### Scenario: Custom weights
- **WHEN** 请求把买方契合度权重设为 0
- **THEN** 返回的保守分与排序按新权重计算
