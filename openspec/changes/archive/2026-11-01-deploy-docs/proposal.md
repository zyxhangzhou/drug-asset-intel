# Proposal

计划变更 I（`deploy-docs`）。

## Why

题面第四部分要求 6 项交付物，并建议提供访问地址。代码、快照和 Excel 已经就绪，但仓库没有面向评审的 README，AI 使用说明、架构说明、已知限制与后续计划都还没有成文，应用也没有部署。网站会显示对方提供的买方材料，用户决定部署时加访问密码。

## What Changes

- 应用支持可选的访问密码：配置了密码时，除健康检查外的所有页面与接口都要求 HTTP 基本认证；不配置时行为不变（本地与 Docker 启动不受影响）。
- 新增 `render.yaml`（Docker 部署，健康检查 `/api/health`，密码作为不入库的环境变量由用户在 Render 填写）。
- 新增 `README.md`：项目简介、交付物索引、一条命令启动、本地开发、配置说明、部署步骤、目录说明（含 `mydoc/`、`.claude/` 作为 AI 工作流证据）。
- 新增交付文档：`docs/ai-usage.md`（按题面三的 5 个问题成文）、`docs/architecture.md`（按实际建成的系统）、`docs/data-sources.md`、`docs/limitations-roadmap.md`（未完成事项、已知限制、四周计划）、`docs/demo.md`（演示提纲）。
- `docs/scoring-rules.md` 定稿（统一用语、去掉「初稿」标记）；`docs/plan.md` 标为开工前方案，指向架构说明。

不做：可选变更 J（带引用的问答，移入四周计划）；用户账号体系；Render 账号操作（由用户完成）。

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `app-runtime`: 新增可选访问密码要求；健康检查在启用密码时仍可匿名访问。

## Impact

- 代码：`src/intel/api.py`（认证中间件）、`src/intel/config.py` 与 `.env.example`（新配置项 `INTEL_ACCESS_PASSWORD`）、`tests/test_api.py`。
- 部署：新增 `render.yaml`；`Dockerfile` 不变。
- 文档：`README.md` 与 `docs/` 下 5 个新文件，修改 `docs/scoring-rules.md`、`docs/plan.md`、`CLAUDE.md`（目录与命令）。
- 依赖：不新增。
