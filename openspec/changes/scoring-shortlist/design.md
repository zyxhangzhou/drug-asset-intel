# Design

## Context

- 评分口径：`docs/scoring-rules.md`（已批准）。本文只写实现方式。
- 快照现状：133 家候选公司；推导管线 1392 条、管线适应症 2444 条，`therapeutic_area` 全部为空；`Program.mechanism` / `modality` 为空；1481 条试验结果的 `analysis` 字段含 p 值文本；130 家有市值。
- 买方偏好：每家买方 3 条治疗领域偏好（有 `ideal_stage`、`target_profile`）+ 3 条技术类型偏好（有 `deal_form`），标签是中文自由文本，如「肿瘤/血液肿瘤」「MASH及肝脏代谢」。
- 构建离线、确定性；人工文件放 `data/manual/`，`verified_by` 非空才生效（与 Stage 0 一致）。

## Goals / Non-Goals

**Goals:**

- 复核一家公司只需编辑一个文本文件，重建后分数、声明、名单同步更新。
- 任何分数都能追到理由与来源；改权重不需要重建。

**Non-Goals:**

- 自动判断技术类型（modality）和作用机制：初筛不用，复核时人工填写。
- 自动判断临床结果是否有临床意义。

## Decisions

### 1. 新表 `Recommendation`，每行一个组合

| 列 | 含义 |
|---|---|
| `target_id`、`program_indication_id`、`buyer_preference_id`（可空） | 组合三要素；买方由偏好行得到 |
| `is_primary` | 是否主组合 |
| `buyer_fit`、`stage_match`、`clinical`、`catalyst`、`dealability`（int 或空） | 五个维度分 |
| `need_item`、`match_note` | 买方需求条目、匹配说明 |
| `design`、`comparability`、`result`、`limitation` | 临床证据四项 |
| `next_event`、`event_timing`、`event_importance`、`event_certainty` | 下一事件 |
| `enterprise_value`、`rights_status`、`funding_flag`、`deal_form` | 可交易性三项与推荐交易形式 |
| `thesis` | 两句话论点 |
| `conservative`、`optimistic`、`coverage`、`research_status` | 计算结果 |

- `BUSINESS_FIELDS` 包含五个维度分与全部文本字段；每个维度分一条推断声明，理由写在备注。计算结果（保守分等）不是业务事实，不需要声明，但在 `MethodNote` 写明公式。
- 备选：把分数写进现有 `Match` 表。放弃原因：`Match` 是买方 × 公司粒度，没有资产维度。`Match` 保留作匹配表（每个公司 × 买方的最佳组合分与一句理由）。

### 2. 治疗领域：项目词表 + 两张人工映射表

- 词表（固定代码）：`oncology`、`heme_malignancy`、`immunology`、`obesity_metabolic`、`liver`、`cardiovascular`、`renal`、`neuroscience`、`infectious`、`respiratory`、`ophthalmology`、`rare_genetic`、`hematology`、`other`。
- `data/manual/ta_keywords.csv`（`ta`、`keyword`、`note`）：适应症文本小写后包含关键词即归入该领域，可归入多个。写入 `ProgramIndication.therapeutic_area`（推断，中，备注列出命中的关键词）。
- `data/manual/buyer_preference_map.csv`（`buyer`、`rank`、`ta_codes`、`stage_min`、`stage_max`、`note`、`verified_by`）：把 30 条治疗领域偏好对到词表代码，并把 `ideal_stage` 文本落成阶段区间。由 AI 起草、人工确认。
- 备选：重抓 CT.gov 的 MeSH 树。放弃原因：要重跑约 30 分钟抓取，且 MeSH 类目仍需映射到买方的自由文本标签。

### 3. 阶段距离

阶段序号：临床前 0、1 期 1、1/2 期 1.5、2 期 2、2/3 期 2.5、3 期 3、注册 4、上市 5。「Phase 2b」按 2 期处理（CT.gov 不区分 2a / 2b，备注写明）。资产阶段落在区间内 4 分；距区间 ≤ 1 得 2 分；更远 0 分。

### 4. 自动初筛规则

- 候选组合：每个阶段不是 `unknown` 的管线适应症 × 每条领域相交的治疗领域偏好行。没有任何相交时，取阶段最高的管线适应症，买方为空。
- 买方契合度：领域相交 2 分（标签匹配上限）。
- 临床证据：该管线适应症下任一 2 期及以上试验的主要终点分析中解析到 p < 0.05 → 2 分；否则留空（不能区分"没数据"和"结果阴性"）。
- 近期催化：该管线适应症下预计主要完成日期在窗口内的试验，按阶段定重要性（3 期 / 2-3 期 高，2 期 中，其余 低），确定性一律「登记估算」。
- 可交易性：EV 档位；权益「待核实」。
- 资金提示：资金可支撑 < 12 个月「融资压力」；经营现金流为正「自给」。

### 5. 复核文件：TOML

```toml
verified_by = "zyxhangzhou"
program = "VK2735"            # 推导管线名中包含即可匹配
indication = "Obesity"
buyer = "Novo Nordisk"
preference_rank = 1
deal_form = "收购"
need_item = "…"
match_note = "…"
thesis = ["第一句…", "第二句…"]
thesis_sources = ["CTG-NCT…", "MAN-VKTX-1"]

[scores.buyer_fit]
score = 4
reason = "…"
sources = ["MNC-…", "MAN-VKTX-1"]
# 其余维度同样格式；未写的维度沿用自动初筛

[clinical]
design = "…"; comparability = "…"; result = "…"; limitation = "…"
sources = ["…"]

[event]
text = "…"; timing = "2027H1"; importance = "high"; certainty = "disclosed"
sources = ["…"]

[rights]
status = "full"   # full / partial / restricted / unverified
note = "…"; sources = ["SEC-…"]
```

- 选 TOML：标准库 `tomllib` 可读，不加依赖；比 CSV 适合多行文本。
- `data/manual/sources.csv` 登记人工来源，ID 前缀 `MAN-`，`source_type` 取已有枚举（`press_release`、`company_ir`、`sec_filing`、`publication`、`fda_web`）。
- 复核文件中的事实性文本（事件时间、试验结果）写事实声明；分数与匹配说明写推断声明，置信度默认「中」，可在文件中指定。

### 6. 证据覆盖率

10 个必需字段逐个判断"该字段非空且有声明"：资产（管线名）、适应症、阶段、需求条目、匹配说明、研究设计、主要结果、下一事件、EV 三个输入（市值、现金、债务都有声明）、权益状态（非「待核实」）。

### 7. 配置与重排

- `config/scoring.toml`：权重、EV 档位、催化窗口月数、长名单家数（40）、入选上限（30）。
- 打分函数是纯函数（输入维度分与权重，输出保守 / 乐观分），构建与 API 共用。API `/api/shortlist?weights=30,20,20,15,15` 从快照读维度分后在内存中重算。

### 8. 输出与检验

- 构建写 `data/processed/longlist.csv`、`shortlist.csv`。
- `intel check-scoring`：高分无事实声明（失败）、前 10 覆盖率 < 70%（失败）、权重敏感性（只报告）。

## Risks / Trade-offs

- [关键词映射漏判或误判适应症] → 映射表人工可审；复核时以人工选定的适应症为准；抽查错误率写进 AI 日志。
- [p 值解析遗漏] → 只影响自动初筛的一个维度，且留空在乐观分里按满分计，不会让公司漏出长名单。
- [推导管线把别家药算进来] → 复核时人工改选资产；排除写入 `data/manual/intervention_excludes.csv`。
- [复核量大] → 长名单家数可配置；先做 10 家并计时，再决定是否缩减。
