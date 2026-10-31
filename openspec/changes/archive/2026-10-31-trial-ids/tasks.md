## 1. 实现

- [x] 1.1 `trials.registry_names` 加入含数字的申办方研究编号；测试 VK2735-102 场景
- [x] 1.2 `load.match_program` 改为按全名、去括号名、括号代码对照，保留唯一子串后备并加反向包含；测试两个资产场景与不唯一时不写入
- [x] 1.3 `trial_aliases.csv` 补 TARGET-D 101、CAMPSIITE 两行（附来源与备注，`verified_by` 留空待用户签字）

## 2. 核验

- [x] 2.1 全部测试、ruff、`openspec validate` 通过；模拟签字构建对比修改前后的未匹配缺口数
- [x] 2.2 `docs/scoring-rules.md` §10 与 `docs/ai-log.md` 更新
