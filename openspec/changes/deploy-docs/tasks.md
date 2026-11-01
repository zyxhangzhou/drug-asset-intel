# Tasks

## 1. 访问密码与部署配置

- [ ] 1.1 新增配置项 `INTEL_ACCESS_PASSWORD`（`config.py`、`.env.example`）；`create_app` 在配置了密码时加基本认证中间件，豁免 `/api/health`；测试覆盖规格 4 个场景（`uv run pytest`）
- [ ] 1.2 新增 `render.yaml`（Docker 运行时、健康检查 `/api/health`、密码 `sync: false`）；本地 `docker compose up --build` 带与不带密码各验证一次
- [ ] 1.3 [人工] 用户在 Render 连接仓库、填写密码并部署；记录访问地址，带密码打开首页与一个公司详情页确认可用

## 2. README 与 AI 使用说明

- [ ] 2.1 写 `README.md`：简介、交付物索引（题面第四部分 1–6 项逐项对应文件）、一条命令启动、本地开发、配置说明、部署步骤、目录说明
- [ ] 2.2 写 `docs/ai-usage.md`：按题面三的 5 个问题成文，工具与用量、环节表、验证方法与错误率、AI 自查发现的缺陷、自动化与人工审核边界；数字逐项对照日志、核验报告与 LLM 账本

## 3. 架构、方法与数据来源

- [ ] 3.1 写 `docs/architecture.md`：组件与数据流、数据模型与溯源规则、构建与核验流程、扩展方式；`docs/plan.md` 顶部注明为开工前方案
- [ ] 3.2 `docs/scoring-rules.md` 定稿（统一「推荐逻辑」「推荐方向」用语，去掉初稿标记）；写 `docs/data-sources.md`（来源类型、接口、口径、更新时间、来源 ID 规则）

## 4. 限制、计划与演示

- [ ] 4.1 写 `docs/limitations-roadmap.md`：未完成事项、已知限制（汇总评分细则第 9 节、核验报告第 6 节与其他遗留问题）、四周计划（含 J）
- [ ] 4.2 写 `docs/demo.md`：30–45 分钟演示提纲与演示路径
- [ ] 4.3 [人工] 用户通读交付文档并按演示提纲彩排一次

## 5. 收尾

- [ ] 5.1 `CLAUDE.md` 更新目录与配置说明；`uv run pytest`、`uv run ruff check .`、`npm run build` 通过；交付清单逐项有对应文件；`docs/ai-log.md` 记一条

## Workflow follow-up

- 校验规格后归档 `deploy-docs`，计划 v6 中 I 标为 done。
