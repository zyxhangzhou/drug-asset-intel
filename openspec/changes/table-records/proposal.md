# Proposal

计划变更 K（HTML 表格逐格展开），计划文件 `mydoc/plans/drug-asset-intel/drug-asset-intel-v4.md`。

## Why

变更 D 的样例运行中，新闻稿表格里的结果（各剂量组体重变化、p 值等）全部被数字校验拒收：剂量与周数写在列标题和表题里，模型只摘抄了数据行。变更 F 的关键临床数据多在表格中。原型验证：把每个数据格展开成带表题、行名、列名的一行文字，数字与表头就在同一行，现有校验不需要放宽。

## What Changes

- HTML 转文本时，在正文之后追加「表格记录」段：每个数据格一行，格式为 `[table N] <表题> — <行名> | <列名>: <值>`。
- 处理 SEC 网页表格的常见写法：单元格内换行补空格、去掉脚注上标、合并 `$` / `)` / `%` 等独立符号格、跨页拆开的表格沿用上一张表的表头、表格内单格行作为表题。
- 抽取提示词说明表格记录的用法。
- 已存档的文档重新转换（`intel fetch docs --refresh`），记录新的文本指纹。

不在范围内：PDF 中的表格（继续由分析师复核文件 `[clinical]` 记录，用户 2026-10-30 确认）；图片中的表格；按单元格坐标引用的抽取方式。

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `document-archive`：「Text conversion」要求增加 HTML 表格逐格展开。

## Impact

- 代码：`src/intel/docs/text.py`、`src/intel/extract/tasks.py`。无新依赖（使用标准库 `html.parser`）。
- 数据：`data/raw/docs/` 下 HTML 文档的 `.txt` 与 `text_sha256` 更新；正文部分不变，已签字条目的片段仍可在文本中找到。
