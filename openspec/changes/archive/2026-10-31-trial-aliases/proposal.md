# Proposal

计划变更 L（试验名称对照），计划文件 `mydoc/plans/drug-asset-intel/drug-asset-intel-v5.md`。

## Why

新闻稿与财报通常用研究名（SHASTA-3、EMBARQ-CSU1、VANQUISH-1）指代试验，很少写 NCT 编号。抽取的临床结果因此对不上快照中的试验，只能记缺口（VKTX 样例 5 条全部如此）。CT.gov 已为多数关键试验登记了简称，或把名称写在标题里，可以作为官方对照；少数没有登记的名称需要人工补充并签字。

## What Changes

- 构建载入抽取结果时，临床结果条目的试验字段没有 NCT 编号的，按名称对照到该公司快照中的试验：
  - CT.gov 自动对照：登记的简称（`acronym`）、标题括号内的名称、标题冒号前的名称；
  - 人工对照：新文件 `data/manual/trial_aliases.csv`（公司、名称、NCT 编号、来源 ID、备注、复核人），复核人非空才生效。
- 名称按字母、数字分词后比较；试验字段包含某个名称的完整词序列即命中。命中多个不同试验时不猜，记缺口 `extraction_trial_ambiguous`。
- 写入的结果声明在备注中注明对照依据（CT.gov 简称或人工对照及其来源）。

不在范围内：用适应症、阶段等其他字段推测试验；自动生成人工对照表的内容。

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `extraction-review`：「Mapping to snapshot entities」中临床结果的试验匹配规则。

## Impact

- 代码：`src/intel/extract/load.py`（新增对照索引）。无新依赖。
- 数据：新增 `data/manual/trial_aliases.csv`（人工签字）。
