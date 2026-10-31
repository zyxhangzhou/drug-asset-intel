## Why

5 家抽取复核后模拟构建：159 条接受条目中约 54 条对不上快照里的药物或试验，只能记缺口。其中一部分是对照规则不够用，而不是来源缺信息：

- VKTX 维持期研究「VK2735-102」就是 NCT07838740 在 CT.gov 登记的申办方研究编号（orgStudyId），L 只用了简称与标题；
- 「clemidsogene lanparvovec (RGX-121)」对不上管线 RGX-121，「defactinib」在 VSTM 管线里命中多个名称而被判不唯一。

## What Changes

- 试验名称对照：CT.gov 登记的申办方研究编号（含数字时）纳入自动对照名称。
- 管线对照：抽取的资产名与管线名都拆成「全名、去括号名、括号内各代码」，任一完全相同即命中；仍不唯一时不写入。原有的唯一子串匹配保留为后备，并加上反向包含（管线名完整出现在资产名中，如 ABBV-RGX-314 → RGX-314），同样要求唯一。
- `data/manual/trial_aliases.csv` 补两行人工对照（附来源，待复核人签字）：TARGET-D 101 → NCT07020221，CAMPSIITE → NCT03566043。

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `extraction-review`：映射到快照实体的规则增加申办方研究编号与括号代码对照。

## Impact

- `src/intel/extract/trials.py`、`src/intel/extract/load.py`、`src/intel/extract/run.py`（资产名拆分函数改为公开）
- `data/manual/trial_aliases.csv`
- 不调用模型，不产生费用。
