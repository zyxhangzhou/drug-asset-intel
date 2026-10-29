# Tasks

## 1. 模型与配置

- [x] 1.1 新增 `Recommendation` 表（含 `BUSINESS_FIELDS`）、`Target.recommendations` 关系；`config/scoring.toml`；纯函数打分（保守 / 乐观、权重归一化、EV 档位、阶段距离）。测试：80 / 100 的缺失样例；已上市对 2–3 期偏好得 2；EV 25 亿得 3；部分权益封顶 3。

## 2. 治疗领域映射

- [x] 2.1 `data/manual/ta_keywords.csv` 与 `buyer_preference_map.csv`（AI 起草，30 条偏好全部覆盖）；构建步骤写 `ProgramIndication.therapeutic_area` 及推断声明。测试：关键词命中多个领域；未确认的映射行不生效。
- [ ] 2.2 [人工] 确认 `buyer_preference_map.csv` 30 行，填 `verified_by`；抽查 50 条适应症的领域映射并记错误率到 `docs/ai-log.md`。

## 3. 自动初筛

- [x] 3.1 候选组合生成、主组合选择、五维自动打分（含上限、p 值解析、登记估算催化、资金提示）、声明写入。测试：无买方匹配时仍有主组合；3 期窗口内得 3；无已发布结果时临床留空。
- [x] 3.2 覆盖率与研究状态；`Match` 匹配表；`longlist.csv` / `shortlist.csv` 输出。测试：长名单按乐观分排序；无复核时入选名单只有表头。

## 4. 人工复核

- [x] 4.1 复核文件与 `sources.csv` 读取：生效条件、覆盖自动字段、未登记来源报错、入选规则写 `Target.shortlisted` / `selection_rationale`。测试：复核人为空被忽略；未知来源 ID 使构建失败；权益待核实不入选。
- [x] 4.2 `intel check-scoring`。测试：4 分无事实声明时非零退出。

## 5. API 与 CLI

- [x] 5.1 `/api/shortlist`（可带权重）。测试：默认权重与快照一致；买方契合度权重为 0 时重新排序。

## 6. 真实数据

- [ ] 6.1 全量构建，生成长名单；`check-provenance` 退出码 0；把长名单前 40 家汇报给用户。
- [ ] 6.2 [人工] 首批 10 家复核文件（AI 起草材料与来源，用户确认 `verified_by`）；记录每家耗时。
- [ ] 6.3 [人工] 样例检验四项（含用户独立分档），结果写入 `docs/scoring-rules.md` 与 `docs/ai-log.md`；决定是否调权重。
- [ ] 6.4 [人工] 复核其余长名单公司，产出 20–30 家入选名单与 3–5 家深度对象建议；用户确认。
- [ ] 6.5 更新计划题面进度与 `CLAUDE.md` 命令小节。

## Workflow follow-up

- `/opsx:verify` 后归档；在 change plan 中勾选 E（第一部分完成）。
