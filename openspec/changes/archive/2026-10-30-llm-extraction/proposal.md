# Proposal

计划变更 D（文档获取存档与 LLM 抽取管道），计划文件 `mydoc/plans/drug-asset-intel/drug-asset-intel-v3.md`。

## Why

题面第二部分要求深度对象的作用机制、技术类型、关键临床数据、相对标准治疗的优势和 12–24 个月催化事件。这些字段只出现在新闻稿、财报正文和投资者演示里，官方接口取不到。变更 F（RGNX、CLDX、VKTX、ARWR、VSTM 深度填充）需要一条可核验的抽取管道：文档有存档和哈希，每个值有原文片段且程序校验过，两个模型交叉核对，人工签字后才入库，费用有记录和上限。

## What Changes

- 新增文档清单 `data/manual/documents.csv` 与抓取命令 `intel fetch docs`：下载 SEC 申报文件、新闻稿、IR 页面与 PDF，存原文和转换后的文本，记录抓取时间与哈希。另加 `intel docs filings <TICKER>` 列出 EDGAR 近期申报及其附件，供人工挑选。
- 新增抽取命令 `intel extract`：文本切块、SQLite FTS5 检索相关块、按 JSON schema 抽取三类字段（管线机制与技术类型、临床结果、催化事件）；DeepSeek 主抽取，Qwen 盲抽交叉核验。
- 原文片段校验与数字校验：不通过的条目写入拒收记录，不进入复核文件。
- 费用账本与预算上限：每次调用记录接口返回的原始用量与折算人民币；调用前按最坏情况预估，超出上限即停止；默认拒绝在 DeepSeek 高峰时段运行。
- 抽取复核文件 `data/manual/extractions/<TICKER>.toml`：一致条目预填接受，分歧条目留空；`verified_by` 非空才生效。
- 快照构建读取已签字的抽取复核文件，重新校验存档哈希与片段，写入 `produced_by = llm` 的声明。构建仍不联网。
- `intel extract report` 输出片段命中率、双模型一致率、累计费用。

不在范围内：5 家深度对象的具体研究结论与文档挑选（变更 F）；表格与图片中的数据抽取；收购成本估算（沿用变更 E 的财务口径）。

## Capabilities

### New Capabilities

- `document-archive`：一手文档的清单、抓取、文本转换与存档登记。
- `llm-extraction`：检索、结构化抽取、片段校验、双模型核验、费用账本与预算上限。
- `extraction-review`：抽取结果的人工复核文件及其进入快照的规则。

### Modified Capabilities

- `snapshot-build`：构建读取已签字的抽取复核文件，并在载入前重新校验存档与片段。

## Impact

- 代码：新增 `src/intel/docs/`（抓取、文本转换、切块索引）与 `src/intel/extract/`（LLM 客户端、账本、抽取、核验、复核文件读写）；修改 `cli.py`、`build.py`。
- 配置：新增 `config/llm.toml`（价格表、高峰时段、预算上限，无密钥）。`.env` 沿用已有的 `LLM_*` 键。
- 依赖：新增 `pypdf`。
- 数据：`data/raw/docs/`、`data/raw/llm/`（账本、原始响应、拒收记录）、`data/manual/documents.csv`、`data/manual/extractions/`。
