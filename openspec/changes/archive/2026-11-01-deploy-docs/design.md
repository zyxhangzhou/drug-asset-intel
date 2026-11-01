# Design

## Context

- `intel serve` 用 `create_app()` 起 FastAPI，同一服务托管 `web/dist`；`/api/health` 已存在。`load_settings()` 对未设置的配置项返回 None，网页服务不需要任何密钥（SEC User-Agent 与 LLM 密钥只在抓取与抽取命令中使用）。
- `Dockerfile` 已把快照、存档原文与前端构建产物打进镜像，启动命令读取平台注入的 `PORT`。
- 网站显示对方材料（买方偏好分析），用户决定部署时加访问密码。
- 交付文档的素材已存在：`docs/ai-log.md`（逐条 AI 使用记录）、`docs/verification.md`（核验报告）、`docs/scoring-rules.md`（评分细则，含未核验假设）、`config/llm.toml` 与 `data/raw/llm/ledger.jsonl`（LLM 费用）。

## Goals / Non-Goals

**Goals:**
- 部署后公网地址可访问，需密码；本地与 Docker 启动方式不变。
- 评审能从 README 找到每一项交付物，并用一条命令跑起应用。
- AI 使用说明逐一回答题面三的 5 个问题，数字与日志、核验报告一致。

**Non-Goals:**
- 多用户账号、权限分级、登录页面。
- 带引用的问答（J）。
- 改动快照数据或评分规则。

## Decisions

1. **认证用 HTTP 基本认证中间件，不做登录页。** 浏览器原生弹框即可满足「拿到密码才能看」；不需要会话与前端改动。备选：前端登录页 + 令牌——要改前端路由与接口，收益只是界面更好看，不值得。
2. **健康检查豁免认证。** Render 的健康检查不带凭据；只豁免 `/api/health`，它不返回任何数据。
3. **只比较密码，用户名任意。** 对方只需记一个密码；用 `secrets.compare_digest` 比较，避免计时差异。
4. **密码配置项 `INTEL_ACCESS_PASSWORD`。** 加进 `CONFIG_KEYS` 与 `.env.example`（占位为空），已有测试保证示例文件完整。`render.yaml` 里声明为 `sync: false`，值由用户在 Render 控制台填写，不进仓库。
5. **Render 用 Docker 运行时与免费套餐。** 复用现有 `Dockerfile`；免费实例闲置会休眠，README 写明首次打开约需等待数十秒。演示前由用户预先打开一次。
6. **文档拆成独立文件、README 做索引。** 题面 6 项各对应一个入口；`docs/plan.md` 保留为开工前方案（历史），架构以 `docs/architecture.md` 为准，避免改写历史文档。
7. **AI 使用说明的数字只取自已有记录。** 工具、环节、费用、错误率逐项引用 `docs/ai-log.md`、`docs/verification.md` 与 LLM 账本，并如实写明：复核文件由 AI 起草、用户签字；抽样核验由 AI 子代理执行；人工核对是用户抽查 5 份复核文件与 Excel 两行。

## Risks / Trade-offs

- 基本认证在 HTTP 下明文传输 → Render 默认提供 HTTPS，README 只给 https 地址。
- 免费实例休眠导致演示时首屏慢 → 演示提纲里写「提前 1 分钟打开」。
- 文档与日志数字不一致 → 写完后逐项对照来源文件核对，核对结果记入 `docs/ai-log.md`。
- 镜像包含对方材料 → 只部署在需密码的地址；仓库本身为私有。
