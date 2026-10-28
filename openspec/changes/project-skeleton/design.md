# Design

## Context

全新仓库，只有文档与对方材料。动机见 proposal.md。整体架构与技术栈已在 `docs/plan.md` 第 4 节确定（uv、FastAPI、SQLite、Vite + React + Ant Design、Docker）。本设计只确定骨架层面的结构与几个会影响后续所有变更的数据模型决策。

## Goals / Non-Goals

**Goals:**
- 一套后续变更直接写入、无需改结构的数据模型，溯源规则在写入时强制执行。
- 快照可由管道确定性重建；应用只读快照。

**Non-Goals:**
- 数据库迁移体系、多用户、写入 API。

## Decisions

### 1. 仓库布局：根目录单个 uv 项目 + `web/` 前端

`src/intel/`（Python 包：`models`、`db`、`api`、`cli`，后续变更加 `ingest`、`extract` 等子包）、`tests/`、`web/`（Vite 项目）。
备选：`backend/` + `frontend/` 两个顶层目录。放弃原因：数据管道和 API 共用模型，同一个包最简单；`CLAUDE.md` 原写的 `app/` 目录改为 `web/` + `src/intel/`。

### 2. 类型化实体列 + Claim 表承载溯源

业务实体保留类型化列（便于筛选、排序、导出 Excel），每个"有值的业务字段"必须有至少一条 Claim 指向 `(entity_type, entity_id, field)`。
备选 A：纯 EAV（所有值都存在 Claim 里）。灵活但查询和前端都很别扭，放弃。
备选 B：每个字段配 `_source_id` 列。字段数翻倍，且无法表达一个值有多个来源或 fact / inference 并存，放弃。
不变量由 Claim 写入时的校验（引用已登记来源、inference 必带置信度、llm 必带原文片段）与 `intel check-provenance` 命令共同保证。哪些字段算"业务字段"由模型上的元数据声明，排除 ID、外键、时间戳。

### 3. SQLModel，不引入 Alembic

SQLModel 让表模型与 API 响应模型共用 Pydantic 定义。快照由管道从 `data/raw/` 缓存确定性重建，建库命令用 `create_all`，不需要迁移；结构变化即重建。代价：不能在旧库上增量升级，对本项目可接受。

### 4. 受控枚举用 Python `StrEnum`，以字符串存储

数据库里是可读字符串，导出 Excel 时无需转换；校验在模型层完成，错误信息列出允许取值。

### 5. 只读：SQLite URI `mode=ro`

服务模式下用 `file:<path>?mode=ro` 打开连接，任何写入都会被 SQLite 拒绝。管道与建库命令使用读写连接。快照路径由环境变量 `INTEL_DB_PATH` 指定，默认 `data/processed/intel.db`。快照文件提交进仓库，供部署镜像直接使用。

### 6. 前端由 FastAPI 静态托管

生产：`web/dist` 由 FastAPI 挂载在 `/`，API 在 `/api/*`。开发：Vite dev server 代理 `/api` 到 Uvicorn。
Docker 多阶段构建：Node 阶段构建前端 → Python 阶段（uv 安装依赖）复制 `dist` 与快照。`compose.yaml` 提供一条命令启动。

### 7. 快照元信息

快照内建 `snapshot_meta` 表记录生成时间与生成命令版本；元信息接口返回它和各实体计数。

## Risks / Trade-offs

- [快照二进制入库导致仓库膨胀] → 本项目数据量小（预计 < 20 MB）；超过时改为构建时生成。
- [类型化列与 Claim 可能不一致] → `check-provenance` 在 CI / 提交前运行，且导出与前端都从同一列读值、从 Claim 读来源。
- [Ant Design 包体较大] → 演示场景可接受，不做优化。
