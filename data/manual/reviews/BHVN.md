# BHVN（Biohaven Ltd.）复核草稿报告

## 选定组合

- 资产 / 适应症：BHV-1300 / Graves 病（`indication = "Graves Disease"`，只匹配 pack 中 id 1866 的 phase3 行）
- 买方：Johnson & Johnson，第 2 优先（免疫炎症），目标资产画像「FcRn、IL-23、自身抗体清除和慢性炎症疾病的长效生物药」
- 交易形式：许可（美欧中权益；公司明确策略是“建立平台并合作”）
- 分数：buyer_fit 4（中）、stage_match 4（高）、clinical 2（中高）；event = 高重要性 / 估算（NCT07661056，2028-01）

### 为什么不选自动主推的 BHV-1400 / IgAN

- 3 期没有启动。10-Q 原文："We are targeting to initiate a pivotal study in IgAN in the second half of 2026"；8-K 原文："On track to initiate the pivotal Phase 3 trial of BHV-1400 ... during 4Q 2026"。实际阶段是 1b 期。
- 对 Novartis 心肾行（Phase 2-3），实际阶段只得 2 分；数据只有 Gd-IgA1 下降（替代指标）。

### 为什么不选 BHV-7000（opakalim）

- 已全球独家授权给 SK Biopharmaceuticals，原文："SKBP will have an exclusive, royalty-bearing, worldwide license to Biohaven's Kv7 ion channel platform, including opakalim (BHV-7000)"（MAN-BHVN-2）。不可交易。

### 为什么选 BHV-1300

- 已在 3 期（2026 年 6 月启动），是公司最晚期且美欧权益仍在手的资产。
- 强生画像中「自身抗体清除」是具体需求条目，直接对应 IgG 降解机制。

## 权益

状态：partial。10-Q（2026-10-29，MAN-BHVN-1）原文：

> "The Company retains all rights to the licensed portfolio outside the Ono Licensed Territory, including in the United States, Europe and China."

Ono 区域 = 日本、韩国、台湾、东盟。可能把状态推向 restricted 的条款（请复核人判断）：

- Ono "sharing specified costs of global clinical studies"（全球试验成本分摊）
- Ono 对区域内部分后续化合物的 ROFN："right of first negotiation with respect to certain follow-on compounds in the Ono Licensed Territory"（不含 BHV-1300 本身）
- 双方竞品限制："specified restrictions on each party’s activities involving competing IgG degraders"

引进许可与对外义务（10-Q Note 11，单位千美元）：

- Yale MoDE 协议（2021-01，"worldwide, exclusive"）：净销售额 "low single digit royalties"；剩余开发里程碑 1.063 百万、商业里程碑 4.988 百万美元；最低年费 up to 1 百万美元；分许可收入付 Yale "low single-digit percentage"。
- Moda 顾问协议：剩余开发 27.995、监管 22.0、商业 104.612 百万美元里程碑。
- Oberland 票据（Note 6）：2.5 亿美元；任何公司产品获 FDA/EMA 批准时付 35% Total Funded Amount 里程碑；控制权变更时持有人可行使 Put Option；限制 "merge or consolidate"。这是收购路线的主要摩擦。

## 待核实

1. J&J 是否已有 Graves 病同机制资产：未打开 J&J 一手来源，记「未核查组合冲突」。J&J 已有 FcRn 抗体 nipocalimab（不同机制，同样降低 IgG），可能被视为功能重叠。
2. buyer_fit 是否应为 3：画像写「长效生物药」，BHV-1300 是小分子每周皮下注射。
3. 1b 期设计（是否随机 / 有对照、样本量）：10-Q 未列明。
4. 3 期读出时间：公司未披露，只有 CT.gov 预计主要完成日期 2028-01。
5. Ono 全球成本分摊是否构成 co-development（影响 partial / restricted 判定）。
6. Oberland 票据与 Ono 首付款对资金提示的影响（见下）。

## Pack 问题

1. BHV-1400 / IgA Nephropathy 阶段 `phase3` 错误：3 期试验 NCT07642050 状态 NOT_YET_RECRUITING，公司称 4Q 2026 启动。实际阶段 1b 期。
2. BHV-1300 有两行 Graves 适应症（"Graves Disease" phase3、"Graves' Disease" phase2_3），重复。
3. 两行 Graves 的 `therapeutic_area` 为 null，因此 BHV-1300 没有任何 auto_pair。**构建时可能不接受 BHV-1300 与强生免疫行的配对**；如构建失败，需在推导层把 Graves 病映射到 immunology。
4. BHV-7000 已全球授权给 SKBP（8-K 2026-10-29），4 个 BHV-7000 auto_pair 不可交易。
5. `total_debt` 为空，但 10-Q 披露 Oberland 票据余额 2.5 亿美元（"amounted to $ 250,000"）。EV 少算 2.5 亿美元；加上后约 23.3 亿美元，仍在 20–50 亿档。
6. 「融资压力」提示可能过时：Ono 首付 8000 万美元已收到，SKBP 4 亿美元待交割；10-Q 称现金与首付款 "will be sufficient to fund operating and financial commitments ... for at least one year"。两份文件发布于 2026-10-29，晚于快照日 2026-10-28。

## 用时

约 25 分钟。
