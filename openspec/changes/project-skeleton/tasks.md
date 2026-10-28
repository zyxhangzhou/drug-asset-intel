# Tasks

## 1. Python 项目与工具链

- [ ] 1.1 用 uv 初始化 Python 3.12 项目（`src/intel/` 包布局），加入 FastAPI、SQLModel、Uvicorn、pytest、ruff；验证 `uv run pytest` 与 `uv run ruff check` 可执行
- [ ] 1.2 添加 `.env.example`（`INTEL_DB_PATH`、`SEC_USER_AGENT`、`LLM_BASE_URL`、`LLM_MODEL`、`LLM_API_KEY`、`LLM_VERIFY_*` 占位）与配置加载模块；测试验证代码读取的每个配置项都出现在 `.env.example` 中

## 2. 数据模型与溯源

- [ ] 2.1 定义受控枚举（研发阶段、置信度、声明类别、产生方式、催化事件类型）；测试验证非法取值被拒绝且错误信息列出允许取值
- [ ] 2.2 定义 10 个领域实体与 Source、Claim、snapshot_meta 表，并标注业务字段元数据；测试验证从标的公司可逐级查到试验、从试验可反查标的
- [ ] 2.3 实现 Claim 写入校验（来源须已登记、inference 须带置信度、llm 须带原文片段）；三条规则各有通过 / 拒绝测试
- [ ] 2.4 实现 `intel init-db` 命令（可重复执行、不丢数据）；测试验证两次执行后表与已有数据都在
- [ ] 2.5 实现 `intel check-provenance` 命令；测试覆盖"有值无声明 → 列出并非零退出"与"空值不算缺口"

## 3. API

- [ ] 3.1 实现只读快照连接（`mode=ro`）与快照缺失时的启动错误；测试验证写入失败、快照不存在时报错含路径
- [ ] 3.2 实现 `/api/health` 与 `/api/meta`；用 TestClient 测试空快照返回生成时间且各实体计数为 0

## 4. 前端壳

- [ ] 4.1 用 Vite 初始化 `web/`（React + TypeScript + Ant Design），开发代理 `/api`；验证 `npm run build` 成功
- [ ] 4.2 首页调用 `/api/meta`，显示快照时间与各实体记录数；在本地启动后打开页面验证显示正确

## 5. 容器与集成

- [ ] 5.1 编写多阶段 `Dockerfile` 与 `compose.yaml`，FastAPI 托管 `web/dist`；验证 `docker compose up --build` 后 `/api/health` 返回 200、首页显示元信息
- [ ] 5.2 生成空快照 `data/processed/intel.db` 并提交；更新 `CLAUDE.md` 的目录与常用命令小节，验证文档中的命令照抄可运行

## Workflow follow-up

- 完成后在 change plan 中把 A 标为 shipped，并记录 Status log。
- 用 `/opsx:verify` 核对实现与 spec 一致后再 archive。
