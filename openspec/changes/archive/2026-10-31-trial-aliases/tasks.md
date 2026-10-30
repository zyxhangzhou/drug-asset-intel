# Tasks

## 1. 对照规则

- [x] 1.1 （实现时补充：同一文本命中多个名称时取最具体的名称；以本公司另一试验简称开头的括号名称也收录，例如 Venture Oral Dosing）在 `src/intel/extract/load.py` 建试验名称索引：从 CT.gov 缓存取该公司快照试验的简称、标题括号内名称、标题冒号前名称；读取 `data/manual/trial_aliases.csv` 中已签字的行（来源 ID 必须已登记，否则构建失败）；名称同时指向多个试验的从自动对照中剔除。验证：测试覆盖简称命中、标题括号命中、冒号前名称命中、多义名称不命中、未签字行忽略、未登记来源使构建失败。
- [x] 1.2 临床结果写入时按「NCT 编号 → 名称对照」顺序匹配；多个试验命中记缺口 `extraction_trial_ambiguous`；声明备注写明对照依据。验证：测试覆盖规格中的 4 个场景。

## 2. 数据与文档

- [x] 2.1 新建 `data/manual/trial_aliases.csv`（表头）；用 VKTX 样例重建快照，报告 5 条临床结果的对照结果。验证：`intel build` 成功、`check-provenance` 为 0。
- [x] 2.2 `CLAUDE.md` 人工文件清单与 `docs/scoring-rules.md` §10 映射规则补充试验名称对照。验证：文档含新规则；`uv run pytest`、`uv run ruff check .` 通过。

## Workflow follow-up

- 核验并归档；F 的抽取结果中仍对不上的研究名，补入人工对照表并由用户签字。
