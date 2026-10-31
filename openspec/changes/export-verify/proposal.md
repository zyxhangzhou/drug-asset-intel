# Proposal

计划变更 H（`export-verify`）。

## Why

题面第二部分要求交付《候选生物制药公司列表》Excel，覆盖 7 项内容；目前数据只在快照与页面里，没有 Excel。第 6 项「收购成本估算」在快照中全部为空，题面允许的「3–5 家深度填充」也没有一家标为深度研究。数据质量目前只有溯源检查，没有抽样得出的错误率，AI 使用说明缺这一项证据。

## What Changes

- 新增 `intel export`：从快照生成 Excel，工作表覆盖第二部分 1–7 项，关键字段旁带来源 ID，另有来源、缺口与说明表（说明其余公司的完成情况）。
- 复核文件可以记录收购成本估算（EV × 有来源的收购溢价区间，推断 + 置信度）；F 的 5 家（ARWR、CLDX、RGNX、VKTX、VSTM）补估算并标为深度研究，复核文件改动后由用户重新签字。
- 快照内残留的旧称「两句话论点」改为「推荐逻辑」，重建快照。
- 新增 `intel verify sample`：分三层（结构化字段、复核字段、LLM 抽取字段）按固定种子各抽 30 条，导出核对表；结构化层自动与缓存原始响应比对，另两层人工核对（本助手核对，独立子代理复查）。结果与错误率写 `docs/verification.md`，发现的错误修正后重建。
- 用户按固定种子抽中的 5 份复核文件做抽查，结果记入 `docs/ai-log.md`。

不做：修复以外的新数据（不扩大深度研究范围、不补其他公司的收购成本）；部署与交付文档（变更 I）。

## Capabilities

### New Capabilities

- `baseline-export`: 《候选生物制药公司列表》Excel 的内容、来源列与完成情况说明。
- `data-verification`: 分层随机抽样核验：抽样规则、核对方法、错误率报告。

### Modified Capabilities

- `analyst-review`: 复核文件增加收购成本估算；深度研究的条件；入选理由改称推荐逻辑。

## Impact

- 代码：`src/intel/export.py`、`src/intel/verify.py`（新）、`src/intel/scoring/review.py` 与 `screen.py`（收购成本、用语）、`cli.py`。
- 数据：5 份复核文件、`data/manual/sources.csv`（溢价研究来源）、重建 `data/processed/intel.db`；交付文件 `deliverables/候选生物制药公司列表.xlsx`。
- 依赖：沿用已有 `openpyxl`，不新增。
