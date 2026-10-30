# Proposal

## Why

计划变更 E（评分、买方匹配与候选名单）。C 已为候选池 133 家备齐试验、财务和审批数据，但还不能回答"这家公司值得推荐给哪家买方、为什么"。题面第一部分要求筛出 20–30 家并说明依据；E 归档即完成第一部分。评分口径已定稿于 `docs/scoring-rules.md`（2026-10-30 用户批准）。

## What Changes

- **推荐组合评分**：为每家候选公司生成"资产 × 适应症 × 买方"组合，按五个维度打 0–4 分；公司分取主组合分。分数、理由全部写成推断声明。
- **自动初筛**：只用快照中的结构化数据打分，买方契合度和临床证据最高 2 分；缺失维度留空，计算保守分与乐观分；按乐观分输出复核长名单（约 40 家）。
- **治疗领域映射**：人工维护的映射文件把 CT.gov 适应症文本归入治疗领域，并把每条买方偏好对应到治疗领域与理想阶段区间。
- **人工复核文件**：`data/manual/reviews/<TICKER>.toml` 记录复核后的推荐组合、各维度分数与理由、资产权益、下一事件、两句话论点及引用的来源；新来源登记在 `data/manual/sources.csv`。`verified_by` 非空才生效。
- **入选规则**：已复核、权益已核实、两句话论点有来源的公司按保守分排序，取 20–30 家，写入 `Target.shortlisted` 与 `selection_rationale`；买方 × 标的匹配表写入 `Match`。
- **权重可调**：权重与档位在 `config/scoring.toml`；API 按传入权重重新排序。
- **检验**：`intel check-scoring` 执行证据一致性、覆盖偏差、权重敏感性三项检验。

**Out of scope**：前端界面（G）；LLM 抽取（D）；3–5 家深度填充（F）；Excel 导出（H）。

## Capabilities

### New Capabilities
- `asset-scoring`: 推荐组合的生成、五维评分、保守分 / 乐观分 / 证据覆盖率 / 研究状态，以及按权重重新排序。
- `analyst-review`: 人工复核文件与人工来源登记的格式、生效条件和入选规则。

### Modified Capabilities
- `intel-data-model`: 新增推荐组合实体（Recommendation）。
- `snapshot-build`: 构建步骤增加评分；构建输出复核长名单与入选名单。
- `app-runtime`: 新增候选名单接口，支持按权重重新排序。

## Impact

- 代码：`src/intel/models.py`、新增 `src/intel/scoring/`、`src/intel/build.py`、`src/intel/api.py`、`src/intel/cli.py`。
- 文件：`config/scoring.toml`、`data/manual/ta_keywords.csv`、`data/manual/buyer_preference_map.csv`、`data/manual/reviews/`、`data/manual/sources.csv`；输出 `data/processed/longlist.csv`、`shortlist.csv`。
- 无新依赖（TOML 用标准库 `tomllib` 读取）。
