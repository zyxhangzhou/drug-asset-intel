# Tasks

## 1. 文档清单与存档

- [x] 1.1 新增 `pypdf` 依赖；建 `src/intel/docs/text.py`：HTML / PDF 转文本（迁入 `sec_doc.py` 规则）与 `normalize()`。验证：夹具测试覆盖 `ix:header` 去除、表格行分隔、PDF 页码标记、空文本 PDF、弯引号与破折号规范化、两次转换结果相同。
- [x] 1.2 建 `src/intel/docs/documents.py`：读取并校验 `data/manual/documents.csv`（含表头的空文件），生成稳定的 `DOC-` 来源 ID，允许复用 `MAN-` ID。验证：测试覆盖非法来源类型、非 http URL、ID 稳定性、复用已有 ID。
- [x] 1.3 建 `src/intel/docs/fetch.py` 与 `intel fetch docs [--only] [--refresh]`：SEC 用 User-Agent 与 SEC 限速，其他站点间隔 0.5 秒；写原文、文本、meta 与抓取日志；已存档跳过；403 记拒绝访问。验证：MockTransport 测试覆盖缓存跳过、403 记录、哈希写入。
- [x] 1.4 `intel docs filings <TICKER> [--forms]`：列出申报与附件 URL（含 8-K Exhibit 99.1）。验证：用已缓存的 submissions / 索引页夹具测试输出含附件 URL。

## 2. 切块与检索

- [x] 2.1 建 `src/intel/docs/index.py`：按段落切块（约 6,000 字符、重叠 600、短文档整份一块），写入 FTS5 索引 `data/raw/docs/index.sqlite`（加入 `.gitignore`），按任务检索词取每份文档前 4 块。验证：测试覆盖块位置连续、短文档一块、检索命中含关键词的块。

## 3. 模型客户端、账本与预算

- [x] 3.1 新增 `config/llm.toml`（DeepSeek 官方价格、高峰时段、预算 15 元、拒绝高峰；Qwen 预算 5 元、价格待填）；建 `src/intel/extract/ledger.py`：价格匹配、时段判定（Asia/Shanghai）、费用计算、最坏情况预估、预算检查、账本追加。验证：测试覆盖缓存命中 / 未命中分别计价、周三 10:00 为高峰、周六为空闲、上限 15 元时 14.9 + 0.2 被拒、价格表缺失时拒绝调用。
- [x] 3.2 建 `src/intel/extract/client.py`：OpenAI 兼容 POST，`temperature = 0`、JSON 输出、`max_tokens`；原始响应落盘；超时与 5xx 重试 2 次；非法 JSON 记失败不重试；每次调用前过预算检查、后写账本。验证：MockTransport 测试覆盖正常响应、5xx 重试、非法 JSON、预算拒绝时不发请求。
- [x] 3.3 [人工] 从阿里云百炼官方价格页核实（2026-10-30 由 Claude 查官方帮助文档 qwen3-7-plus 页面，用户授权网上查询；按原价、不计限时优惠） `qwen3.7-plus-2026-05-26`（北京地域）的单价，填入 `config/llm.toml` 并注明 URL 与日期。验证：配置含价格与来源；未核实前 Qwen 调用被拒绝。

## 4. 抽取、校验与交叉核验

- [x] 4.1 建 `src/intel/extract/tasks.py`：三类条目（program、clinical_result、catalyst）的 JSON schema、检索词、系统提示与用户提示。验证：测试检查每类 schema 都要求 `quote` 字段，提示词包含「原文没有就留空」的指令。
- [x] 4.2 建 `src/intel/extract/validate.py`：片段校验（规范化子串、至少 20 字符）、数字校验、片段在原文中的位置。验证：测试覆盖换行与弯引号差异通过、编造片段拒收、取值数字不在片段中拒收、过短片段拒收。
- [x] 4.3 建 `src/intel/extract/run.py` 与 `intel extract`：检索 → 主模型抽取 → 校验（每个条目的校验结果写 `data/raw/llm/validation.jsonl`，拒收条目带原因）→ 核验模型盲抽 → 配对判定一致 / 分歧 / 单模型；支持 `--only`、`--source`、`--tasks`、`--no-verify`、`--allow-peak`、`--dry-run`。验证：MockTransport 端到端测试覆盖一致、分歧、只有一边抽出、未配置核验模型、dry-run 不发请求、高峰时段拒绝。
- [x] 4.4 建 `src/intel/extract/review.py`：写 / 合并 `data/manual/extractions/<TICKER>.toml`（一致预填接受，其余留空，`verified_by` 为空；重跑保留决定与备注）。验证：测试覆盖预填规则与重跑合并。
- [x] 4.5 `intel extract report`：按公司与服务商输出调用次数、用量、费用、片段与数字校验通过率、一致率、拒收原因分布。验证：用夹具账本与拒收记录测试输出数字。

## 5. 构建载入

- [x] 5.1 建 `src/intel/extract/load.py`，在 `build.py` 中 `screen` 之后加入 `extract.load`：只读已签字文件；登记或补全来源的 `local_path` 与 `content_hash`；复检存档哈希、片段与数字，失败即构建失败；未复核条目计数。验证：测试覆盖未签字忽略、篡改存档失败、改坏片段失败、未复核计数、构建不联网（无密钥也成功）。
- [x] 5.2 映射写入：管线机制与技术类型、试验结果、催化事件（时间表述换算为窗口），LLM 声明带片段、模型名、截至日；优势写推断带置信度；匹配失败记缺口 `extraction_unmatched`。验证：测试覆盖三类写入、半年与季度换算、无法换算时窗口为空、未知资产记缺口；`intel check-provenance` 为 0。

## 6. 样例运行与文档

- [x] 6.1 [人工] 选一份样例文档（MAN-VKTX-4，2026-09-22 维持期研究顶线新闻稿；5 次空闲时段运行，见 `docs/ai-log.md`）（深度对象的一份 8-K Exhibit 99.1 新闻稿）写入 `data/manual/documents.csv`，抓取后先 `--dry-run` 报告预估费用，再在 DeepSeek 空闲时段做一次真实抽取（含 Qwen 核验）。验证：账本有记录，复核文件生成，`intel extract report` 输出命中率、一致率与费用。
- [x] 6.2 [人工] 复核样例文档的复核文件并签字（2026-10-30 用户确认 4 条全部接受，签字 zyxhangzhou；3 条机制入库，1 条临床结果无 NCT 编号记缺口），重建快照。验证：`intel build` 成功，`intel check-provenance` 为 0，快照中出现 `produced_by = llm` 的声明。
- [x] 6.3 文档：`CLAUDE.md` 命令与人工文件清单、`docs/scoring-rules.md` 时间表述换算规则、`docs/ai-log.md` 记录样例运行的命中率、一致率、拒收原因与费用。验证：文档包含以上内容；`uv run pytest` 与 `uv run ruff check .` 通过。

## Workflow follow-up

- 核验（`/opsx:verify llm-extraction`）后归档，并在计划 v3 中把 D 标为 archived。
- 变更 F 用本管道处理 5 家深度对象的文档。
