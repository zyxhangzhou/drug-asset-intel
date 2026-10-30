# Design

## Context

- 快照构建（`src/intel/build.py`）按步骤从缓存与 `data/manual/` 离线重建 SQLite 快照；`snapshot-build` 规格禁止构建联网。
- 数据模型已支持 LLM 声明：`Claim.produced_by = llm` 时 `db.py` 强制要求 `quote` 与 `model`（`db.py:98-101`）。`Source` 已有 `local_path` 与 `content_hash`，`db.archived_source` / `archive_matches`（`db.py:120-147`）可直接复用。
- 目前没有代码写入 `Program.mechanism`、`Program.modality` 与 `Catalyst`；`TrialResult` 只由 CT.gov 已发布结果写入（`ingest/ctgov.py:323`）。抽取是这三处的第一个文档来源。
- 评分用的催化事件来自复核文件的 `[event]`，不读 `Catalyst` 表。本变更不改评分。
- `.env` 已配置 DeepSeek（`deepseek-v4-pro`）与 Qwen（北京地域 Model Studio，`qwen3.7-plus-2026-05-26`）的 OpenAI 兼容接口与密钥。
- DeepSeek 官方价格（https://api-docs.deepseek.com/zh-cn/quick_start/pricing ，2026-10-30 查询），每百万 token：v4-pro 输入缓存命中 0.15 元、未命中 4.5 元、输出 13.5 元（空闲时段）；高峰时段翻倍。高峰时段为北京时间周一至周五（不含法定节假日）9:00–12:00、14:00–18:00。
- 复核研究期间的临时工具 `SCRATCH/tools/sec_doc.py`（SEC 申报列表、HTML 转文本）验证可用，迁入包内。
- 运行环境的 SQLite 已编译 FTS5（`PRAGMA compile_options` 含 `ENABLE_FTS5`）。

## Goals / Non-Goals

**Goals:**

- 文档有存档、哈希与来源登记，抽取值可回到原文。
- 抽取值必须过片段校验与数字校验；两模型盲抽交叉核验；人工签字后才入库。
- 每次调用有账本，费用可重算；预算上限在调用前生效。
- 一份样例文档跑通全流程，并输出命中率、一致率与费用。

**Non-Goals:**

- 不做 OCR、表格结构识别、图片抽取。
- 不做异步并发、批量接口、缓存命中优化以外的调价策略。
- 不让抽取结果改变评分；评分仍以复核文件为准。
- 不为 149 家全量抽取；只服务变更 F 的 5 家。

## Decisions

### 1. 包结构

- `src/intel/docs/`：`documents.py`（清单读取与校验、来源 ID）、`fetch.py`（抓取存档、申报列表）、`text.py`（HTML / PDF 转文本、规范化）、`index.py`（切块与 FTS5）。
- `src/intel/extract/`：`client.py`（OpenAI 兼容客户端）、`ledger.py`（账本、价格、时段、预算）、`tasks.py`（三类条目的 schema、检索词与提示词）、`run.py`（抽取与核验流程）、`validate.py`（片段与数字校验）、`review.py`（复核文件读写）、`load.py`（构建步骤）。
- 规范化函数只有一份（`docs/text.py`），抽取校验与构建复检共用。

### 2. 文档清单与来源 ID

`data/manual/documents.csv` 列：`ticker,url,source_type,title,published_date,source_id,note`。`source_id` 留空时生成 `DOC-<TICKER>-<sha256(url)[:8]>`。填写已有 `MAN-` ID 时，构建用 `sources.csv` 的元数据，并补上 `local_path` 与 `content_hash`。`intel docs filings <TICKER> [--forms ...]` 打印申报与附件 URL（读取 EDGAR submissions 与申报索引页），只打印不写清单。

备选：自动把近 12 个月全部申报加入清单。放弃原因：10-K 动辄数十万字符，抽取费用与复核量都失控；人工挑选也是 F 的研究动作。

### 3. 存档布局

```
data/raw/docs/<TICKER>/<source_id>.<html|pdf|txt 原文扩展名>
data/raw/docs/<TICKER>/<source_id>.txt          # 转换后的文本，首行不加 URL 头
data/raw/docs/<TICKER>/<source_id>.meta.json    # url、fetched_at、raw_sha256、text_sha256、status
data/raw/docs/fetch_log.jsonl
data/raw/docs/index.sqlite                      # FTS5 索引，可重建，加入 .gitignore
```

`Source.content_hash` 记文本哈希（片段校验针对文本）；原文哈希留在 meta 中。PDF 文本按页写入，页首加 `[page N]` 标记。

### 4. 文本转换

HTML：沿用 `sec_doc.py` 的规则（去 `script`、`style`、`ix:header`；块级标签与 `<br>` 换行；单元格以 ` | ` 分隔；`html.unescape`；行内空白折叠）。PDF：新增依赖 `pypdf`，逐页 `extract_text()`。空文本记 `status = no_text`。

### 5. 规范化

`normalize(s)`：NFKC → 弯引号 `‘’“”` 转 `'"` → `‐‑‒–—―−` 转 `-` → 空白（含 NBSP）折叠为单个空格 → `casefold()`。每个条目带 1–4 段片段（`quotes`）。片段校验：每段 `normalize(quote) in normalize(doc_text)`，且至少 20 字符（防止「42%」这类过短片段到处命中）。数字校验：从取值提取数字（去千分位逗号与小数末尾的 0，不计正负号），每个数字须出现在全部片段的数字集合中；资产代号所含数字（VK2735 的 2735）除外。另有字段规则：管线条目机制与技术类型不能都为空；催化事件的时间表述须含年份。

### 6. 切块与检索

按段落累积切块，目标约 6,000 字符，相邻块重叠 600 字符；块记录 `(source_id, chunk_no, start, end)`。文本不超过 12,000 字符时整份作为一块。每类任务有固定检索词（如临床结果：`primary endpoint OR met OR "p<" OR placebo OR response OR topline`），FTS5 `bm25` 取每份文档前 4 块。送出块按原文顺序拼接，块间注明块号。

### 7. 模型调用

`httpx` 直接 POST `{base_url}/chat/completions`，不加 `openai` 依赖。参数：`temperature = 0`、`response_format = {"type": "json_object"}`、`max_tokens` 取配置值（默认 4,000）。系统提示要求只输出 JSON、每个条目带逐字片段、原文没有就留空。返回的 `model` 字段与 `usage` 原样存入账本；原始响应写 `data/raw/llm/responses/<call_id>.json`。超时或 5xx 重试 2 次；JSON 解析失败的响应记账本并计为失败，不重试第二次以免重复计费。

DeepSeek v4-pro 与 Qwen 3.7-plus 默认开启思考模式。样例运行中，DeepSeek 的临床结果任务把 4,000 个输出 token 全部用于思考，没有给出答案；思考模式也忽略 `temperature`。实现时调整：`config/llm.toml` 按服务商配置额外请求字段 `request_extra`，DeepSeek 设 `thinking = {type = "disabled"}`，Qwen 设 `enable_thinking = false`。

### 8. 账本、价格与预算

`config/llm.toml`（提交，无密钥）：

```toml
[providers.deepseek]
match_base_url = "api.deepseek.com"
currency = "CNY"
price_source = "https://api-docs.deepseek.com/zh-cn/quick_start/pricing (2026-10-30)"
offpeak = { input_hit = 0.15, input_miss = 4.5, output = 13.5 }  # 元 / 百万 token
peak    = { input_hit = 0.30, input_miss = 9.0, output = 27.0 }
peak_windows = ["Mon-Fri 09:00-12:00", "Mon-Fri 14:00-18:00"]  # Asia/Shanghai
budget_cny = 15.0
refuse_peak = true

[providers.qwen]
match_base_url = "maas.aliyuncs.com"
# 价格待从阿里云百炼官方价格页核实后填写；未填写时拒绝调用
budget_cny = 5.0
```

账本 `data/raw/llm/ledger.jsonl`，每行：`call_id, ts, provider, requested_model, returned_model, task, ticker, source_id, chunks, usage(原样), tier, cost_cny, status`。费用：DeepSeek 用 `prompt_cache_hit_tokens` 与 `prompt_cache_miss_tokens`；没有命中字段的服务商全按未命中计。预估：`ceil(len(prompt_chars) / 2.5)` 个输入 token 全按未命中价 + `max_tokens` 按输出价，按当前时段价格。法定节假日不维护日历，一律按工作日处理，结果只会偏保守。价格表缺失时拒绝调用该服务商。

DeepSeek 预算上限 15 元：账户余额 20 元，留 5 元余量。

### 9. 盲抽与配对

主模型与核验模型收到相同的块与提示词。配对键：管线条目为规范化资产名；临床结果为（资产名，试验 ID 或规范化终点）；催化事件为（资产名，事件类型，时间表述中的年份）。键不同时，同一资产且片段位置区间重叠的条目也配对（样例运行中两边终点措辞不同）。一致判定逐字段：两边都为空；或两边都有值、数字集合相同，且规范化后相同或片段位置重叠。只有一边抽出的条目为「分歧」。

### 10. 抽取复核文件

```toml
ticker = "VKTX"
verified_by = ""

[[items]]
id = "r-c6903ab3"          # 前缀 p- / r- / e- 加 sha256(source_id|type|配对键)[:8]
type = "clinical_result"   # program | clinical_result | catalyst
source_id = "MAN-VKTX-2"
asset = "VK2735"
trial = "NCT06068946"
indication = "obesity"
endpoint = "mean percent change in body weight from baseline at week 13"
result = "up to 14.7%"
analysis = "p<0.0001"
comparator = "placebo"
quotes = ["…逐字片段…", "…表头或小标题行…"]   # 1–4 段
model = "deepseek-v4-pro"
returned_model = "…"
check = "agreed"           # agreed | disputed | single
verify = { asset = "…", endpoint = "…", result = "…" }   # 核验模型配对条目的取值
verify_quotes = ["…"]
decision = "accept"        # accept | reject | ""
note = ""
```

`program` 条目字段：`asset, mechanism, modality`；`catalyst` 条目字段：`asset, event, event_type, timing`。`advantage_vs_soc` 附在临床结果条目上，另带 `confidence`。重跑时以 `id` 合并：已有条目保留 `decision` 与 `note`，新条目追加。

### 11. 构建载入

新步骤 `extract.load`，插在 `screen` 之后（实现时调整：`screen` 负责登记 `MAN-` 人工来源，抽取条目可能复用这些来源；评分不读抽取结果，所以放在后面不影响评分）。逐个读取已签字文件：

1. 来源须在快照中且有 `local_path`；`archive_matches` 失败或文件缺失 → 构建失败。
2. 重跑片段与数字校验；失败 → 构建失败（规格要求，人工改动后的片段也要过）。
3. 映射：资产名按「不区分大小写的子串」匹配本公司管线（与复核文件规则一致）；NCT 须在快照中；匹配失败 → 缺口 `extraction_unmatched`。
4. 写声明：`kind = fact`（优势为 `inference` 带置信度），`produced_by = llm`，`model = returned_model`，`as_of = 来源发布日期`。
5. 时间表述换算：`Q1–Q4 YYYY`、`first/second half of YYYY`、`H1/H2 YYYY`、`mid-YYYY`（06-01–08-31）、`YYYY`、`end of YYYY`（10-01–12-31）；其他写法窗口留空。换算规则写入 `docs/scoring-rules.md`。

### 12. 命令

```
uv run intel docs filings VKTX [--forms 8-K,10-Q]
uv run intel fetch docs [--only VKTX] [--refresh]
uv run intel extract [--only VKTX] [--source MAN-VKTX-2] [--tasks program,clinical_result,catalyst] [--no-verify] [--allow-peak] [--dry-run]
uv run intel extract report
```

`--dry-run` 只打印将送出的块数、预估 token 与预估费用，不调用模型。

### 13. 测试

全部离线：`httpx.MockTransport` 模拟两个服务商的响应（含用量字段、非法 JSON、5xx）；`time` 注入以测高峰拒绝；样例 HTML 与小 PDF 夹具测转换；构建测试用临时目录的存档与签字文件。真实调用只在任务的样例运行中做一次。

## Risks / Trade-offs

- [模型给出的片段是转述而非原文] → 片段校验拒收；拒收率进入报告。若某类拒收率过高，调整提示词，而不是放宽校验。
- [两模型一致但同样错误] → 一致只预填接受，仍需人工签字；变更 H 抽样核验时对 LLM 字段单独分层。
- [规范化过宽导致误命中] → 片段至少 20 字符；不做模糊匹配。
- [PDF 文本顺序错乱（多栏、表格）] → 片段在错乱文本中找不到时会被拒收，不会产生错值；表格数据不在范围内。
- [Qwen 价格未核实] → 价格表缺失时拒绝调用 Qwen；核实前可以 `--no-verify` 运行，条目标为单模型。
- [IR 站点拒绝脚本访问] → 记拒绝访问；优先使用 EDGAR 上 8-K Exhibit 99.1 的同一份新闻稿。
- [预估偏低导致实际超支] → 预估用 2.5 字符 / token 与满额输出，偏保守；账本按实际用量记账，下一次调用前即生效。

## Migration Plan

新增文件与命令，不改动已有数据。`.gitignore` 增加 `data/raw/docs/index.sqlite`。回滚：删除 `extract.load` 步骤即恢复原构建。

## Open Questions

- Qwen（北京地域 Model Studio）`qwen3.7-plus-2026-05-26` 的官方单价：实现前从阿里云官方价格页核实并填入 `config/llm.toml`。
- Qwen 返回的用量字段是否区分缓存命中：以第一次真实调用的原始响应为准。
