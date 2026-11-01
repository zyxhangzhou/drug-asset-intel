# Tasks

## 1. 收购成本与深度研究

- [x] 1.1 [人工] 收购溢价区间的来源：未找到给出样本与口径的公开研究，改为自建样本（31 宗交易的 SEC 原文溢价，`data/manual/takeover_premiums.csv`），前一交易日收盘口径 18 宗登记为 `MAN-PREM-*` 来源；记 `docs/ai-log.md`
- [x] 1.2 复核文件解析 `[acquisition_cost]`（low、high、method、confidence、sources）与「深度研究须有临床、下一事件、收购成本」校验；构建写入财务快照收购成本字段与人工推断声明；测试：带估算的复核写入两列与声明、标深度研究但缺估算时构建失败（`uv run pytest`）
- [x] 1.3 [人工] 为 ARWR、CLDX、RGNX、VKTX、VSTM 计算估算（快照 EV + 市值 × 溢价区间），写入复核文件并加 `status = "deep"`；列出差异请用户确认并重新签字
- [x] 1.4 快照中的「两句话论点」改为「推荐逻辑」（缺口原因、声明说明）；重建快照，`intel check-provenance` 为 0，5 家研究状态为深度研究

## 2. Excel 导出

- [x] 2.1 新增 `intel export`：说明、候选公司、管线、临床数据、催化事件（三个出处）、来源、缺口七张表，关键字段带来源列；写到 `deliverables/候选生物制药公司列表.xlsx`
- [x] 2.2 测试：同一快照两次导出内容相同；来源列中的每个 ID 都在来源表；说明表各状态公司数之和等于候选公司行数；入选公司行有推荐逻辑与财务列
- [x] 2.3 [人工] 打开 Excel 检查 VKTX、RGNX 两行与对应管线、临床、催化事件行，与公司详情页一致

## 3. 抽样核验

- [x] 3.1 新增 `intel verify sample`（三层、默认每层 30、种子 20261101）导出核对表；结构化层自动与缓存原始响应比对；测试：同种子样本相同、比对能识别篡改的值
- [x] 3.2 [人工] 复核层与 LLM 层逐条核对；独立子代理盲核同一批，分歧逐条裁定
- [x] 3.3 修正发现的错误并重建；写 `docs/verification.md`（规则、种子、各层错误率与 95% 上限、错误类型、处理结果）
- [x] 3.4 生成用户抽查清单 `docs/spot-check.md`（固定种子抽 5 份复核文件，关键数据附来源链接）
- [x] 3.5 [人工] 用户抽查 5 份并把结果（份数、错误数、问题）记入 `docs/ai-log.md`

## 4. 收尾

- [x] 4.1 `CLAUDE.md` 补 `intel export`、`intel verify sample` 命令；`uv run pytest`、`uv run ruff check .` 通过；`docs/ai-log.md` 记一条

## Workflow follow-up

- 校验规格后归档 `export-verify`，计划 v6 中 H 标为 done。
