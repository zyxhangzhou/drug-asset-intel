# Proposal

对应计划变更 A（项目骨架与数据模型），见 `mydoc/plans/drug-asset-intel/`。

## Why

后续所有变更（材料导入、官方数据拉取、LLM 抽取、评分、应用、Excel 导出）都要写入同一套数据模型，并且都要满足 `CLAUDE.md` 的数据诚信规则：每个数据点可追溯到来源，并区分事实与推断。这套模型和运行骨架必须先落地，否则各变更会各自发明字段和来源格式，最后无法统一溯源。

## What Changes

- 新建 Python 项目（uv 管理），包含领域数据模型与建库命令。
- 领域实体：买方、买方偏好、标的公司、管线、管线适应症、临床试验、试验结果、催化事件、财务快照、买方×标的匹配。
- 溯源实体：来源登记（Source）与声明（Claim）。业务字段通过 Claim 关联到 Source，Claim 标注事实 / 推断、置信度、原文片段、截至日、产生方式。
- 溯源完整性检查命令：列出缺少来源支撑的业务字段。
- 只读 HTTP API 骨架：健康检查与数据快照元信息（快照时间、各实体记录数）。
- 前端壳：能调用上述 API 并显示快照元信息。
- 单个容器镜像同时提供 API 与前端；本地一条命令启动。
- `.env.example`，列出后续变更需要的配置项（占位值）。

## Capabilities

### New Capabilities

- `intel-data-model`: 领域实体、受控枚举（研发阶段、置信度、事实 / 推断等）与溯源规则（Source / Claim）及其完整性检查。
- `app-runtime`: 应用的运行方式：只读数据快照、健康检查与快照元信息接口、前端与 API 同源提供、配置通过环境变量注入。

### Modified Capabilities

（无，项目首个变更）

## Impact

- 新增：`pyproject.toml`、`src/intel/`、`tests/`、`web/`、`Dockerfile`、`compose.yaml`、`.env.example`。
- 新增依赖：FastAPI、SQLModel、Uvicorn、pytest、ruff；前端 React、Vite、TypeScript、Ant Design。
- `CLAUDE.md` 的目录与命令小节更新。

**Out of scope**：任何真实数据导入（变更 B、C）、LLM 客户端（D）、业务页面（G）、部署到公网（I）。
