# asset-scoring Specification

## Purpose
为候选池每家公司生成"资产 × 适应症 × 买方"推荐组合，按 `docs/scoring-rules.md` 的五维刻度评分，并把吸引力与研究充分程度分开呈现，供排序与入选使用。

## Requirements

### Requirement: Recommendation pairs
系统 SHALL 为每家候选公司生成推荐组合（资产、适应症、买方、对应的买方偏好行），并标出唯一一个主组合。五个维度 SHALL 全部针对同一个组合打分；公司分 SHALL 等于主组合的分数，其他组合不计入公司分。主组合 SHALL 取保守分最高者，同分取证据覆盖率高者；人工复核文件指定的组合优先。

#### Scenario: Company score equals primary pair score
- **WHEN** 一家公司有两个组合，保守分分别为 60 与 45
- **THEN** 60 分的组合为主组合，公司分为 60，45 分的组合只出现在详情中

#### Scenario: No buyer matches any asset
- **WHEN** 公司所有资产的治疗领域都不在任何买方偏好中
- **THEN** 公司仍有一个主组合（研发阶段最高的资产，买方为空），买方契合度与研发阶段匹配度为 0

### Requirement: Five-dimension scale
每个维度 SHALL 取 0–4 整数分或留空（缺失）。权重 SHALL 从配置文件读取，初始为买方契合度 30%、研发阶段匹配度 20%、临床证据与差异化 20%、近期催化 15%、可交易性 15%。每个已打分的维度 SHALL 写一条推断声明（含置信度与理由），理由引用所依据的来源。

#### Scenario: Stage match does not reward later stage by default
- **WHEN** 买方偏好行的理想阶段为 2–3 期，资产已上市
- **THEN** 研发阶段匹配度为 2，而不是 4

#### Scenario: Funding pressure is not scored
- **WHEN** 公司资金可支撑时间少于 12 个月
- **THEN** 组合带「融资压力」提示，可交易性分数不因此提高

### Requirement: Automatic screening caps
仅凭快照结构化数据打出的分数（研究状态为自动初筛）SHALL 满足：买方契合度最高 2 分（只按治疗领域标签匹配）；临床证据与差异化最高 2 分；近期催化只用 CT.gov 预计主要完成日期，标为「估算」；资产权益为「待核实」。没有已发布结果的资产，临床证据维度 SHALL 留空而不是 0。

#### Scenario: Registry estimate catalyst
- **WHEN** 资产有一项 3 期试验，预计主要完成日期在快照日后 24 个月内
- **THEN** 近期催化为 3 分（高重要性 × 登记估算），事件标「估算」

#### Scenario: Auto buyer fit is capped
- **WHEN** 资产治疗领域与买方第一治疗领域相同
- **THEN** 自动初筛的买方契合度为 2

### Requirement: Cost tiers and rights gate
可交易性 SHALL 只按企业价值（市值 + 债务 − 现金及投资）分档计分，档位从配置文件读取。资产权益为「部分」时可交易性最高 3 分；为「受限」时最高 1 分。市值缺失时可交易性留空。

#### Scenario: EV tier
- **WHEN** 市值 30 亿美元、现金 5 亿、债务 0
- **THEN** EV 为 25 亿，可交易性 3 分

#### Scenario: Partial rights cap
- **WHEN** EV 档位给 4 分，资产权益为「部分」
- **THEN** 可交易性为 3 分

### Requirement: Conservative and optimistic scores
系统 SHALL 为每个组合计算保守分（缺失维度按 0 分）与乐观分（缺失维度按 4 分），公式为 Σ 权重 × 维度分 / 4 × 100。系统 SHALL 计算证据覆盖率（10 个必需字段中有来源支撑的比例）与研究状态（自动初筛 / 已复核 / 深度研究）。缺失字段 SHALL 显示为「待核实」，不得填估算值。

#### Scenario: Missing dimension widens the range
- **WHEN** 组合的临床证据维度缺失，其余维度满分
- **THEN** 保守分为 80，乐观分为 100

### Requirement: Reweighted ranking
系统 SHALL 支持用任意一组非负权重（自动归一化）重新计算分数与排序，而不重新构建快照。

#### Scenario: Weight change reorders the list
- **WHEN** 把买方契合度权重从 30% 改为 0
- **THEN** 返回的排序按新权重计算，快照文件不变

### Requirement: Scoring checks
系统 SHALL 提供检验命令，输出：每个 3–4 分维度是否有事实声明支撑；保守分前 10 名中证据覆盖率低于 70% 的公司数；每个权重 ±10 个百分点时前 20 名的变动家数。前两项不通过时 SHALL 以非零状态退出。

#### Scenario: Unsupported high score fails the check
- **WHEN** 某组合的买方契合度为 4 分，但没有任何事实声明支撑
- **THEN** 检验命令列出该组合并以非零状态退出

### Requirement: Manual debt adjustments
系统 SHALL 读取 `data/manual/debt_adjustments.csv`（ticker、金额、来源 ID、说明、`verified_by`），把已签字的金额计入该公司 EV 的债务部分，EV 声明增加该来源，备注写明金额与说明。用于 XBRL companyfacts 接口缺失的债务类负债（如公司自定义标签的特许权出售负债）。

#### Scenario: Royalty liability raises EV
- **WHEN** 已签字的调整行为某公司加 1 亿美元，市值 18 亿、现金 5 亿、无申报债务
- **THEN** 该公司 EV 为 14 亿美元，声明引用调整行的来源
