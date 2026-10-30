# BBOT 复核草稿报告

## 选定组合

- 资产 / 适应症：BBO-8520 / Non-small Cell Lung Cancer（包 id 2455，KRAS G12C 突变 NSCLC，1 期 ONKORAS-101，NCT06343402）
- 买方：GSK #1（肿瘤），交易形式：收购
- 分数：buyer_fit 4（中）、stage_match 2（高）、clinical 2（高）；catalyst 1、dealability 4 由构建推导（预览构建：保守 68.8）

理由：
- 公司 2026-09-08 把战略重点定在 "BBO-8520 in combination with pembrolizumab in 2L+, KRAS G12C inhibitor-experienced NSCLC patients"（MAN-BBOT-2）。BBO-8520 是唯一有像样疗效数据的资产：联合 ORR 53%（N=17），单药 63%（26/41）。
- GSK 画像写明"肺癌……已验证靶点小分子"，技术偏好写明"清晰生物标志物和注册路径"，并以 Nuvalent（ROS1/ALK）为先例。已读文件中没有出现 GSK。
- 排除的买方：
  - Roche：画像点名 KRAS，但 divarasib 是同靶点资产，演示材料引用 "Roche Q1 2026 earnings presentation"，构成冲突。
  - BMS：Krazati（adagrasib）是同靶点资产，演示材料引用 "Amgen and BMS FY2025 filings"。
  - Merck：画像最贴近（KEYTRUDA 联用、肺癌），但 calderasib / MK-1084 的归属在已读文件中没有写明，冲突无法排除；阶段差两档。
  - Novartis（自动主组合）：画像是放射性配体 / ADC / payload，不符合。
  - AstraZeneca #1：同样契合，可作备选。

## 权益状态：full（推断，中）

- 10-K / 10-Q 未披露 BBO-8520 有任何对外授权、选择权、ROFN 或共同开发安排。
- 10-K 原文（LLNS）："received a worldwide, exclusive, royalty-bearing, sublicensable (through no more than two tiers) license under certain patent rights relating to the KRAS G12C inhibitor compounds"
- 10-K 原文（Leidos PLA II）："received a worldwide, exclusive, royalty-bearing, sublicensable (through multiple tiers) license under patent rights relating to the KRAS G12C inhibitor compounds"
- 附带条件：
  - 两家许可方各收低个位数特许权使用费。
  - 里程碑：LLNS 最高 $7.0M，Leidos 首个适应症 $6.75M。
  - 转授权收入分成：LLNS 45–55%（10-Q：每个适应症每年上限 $2.0M），Leidos 5–15%。
  - LLNS 协议有 assignment fee。
  - 美国政府保留非独家许可。
  - 专利申请与 LLNS / Leidos 共有。
  - UCSF 主张控制权变更时应付 <$5.0M，公司有争议。
- 债务：10-Q 未见票据或贷款。
- 现金指引："sufficient to enable us to fund our operating expenses and capital expenditure requirements into 2028"。演示材料写明跑道只覆盖 "full phase 1 development across all three clinical programs"。

## 待核实

1. 2025-07 关联方研究合作协议（RCA）向关联方授予的知识产权许可，涉及哪个化合物、哪个适应症（10-Q 未写明）。
2. GSK 自有管线是否有 KRAS G12C 资产（只查了 BBOT 的 10-K 竞争段）。
3. calderasib / MK-1084 是否属于 Merck（决定 Merck 能否作为备选买方）。
4. 是否有 pembrolizumab 供药协议；GSK 收购后联合用药的安排。
5. "mid-2027" 不是季度口径，已标为 disclosed；如按严格口径，需复核人确认。
6. 联合队列的确认 ORR、PFS、缓解持续时间均未公布；联合 ORR 含未确认缓解。
7. 关键性试验的设计与启动时间：已读文件中未见。

## 数据包问题

- 自动组合都放在 BBO-11818 上；公司实际重点是 BBO-8520 联合 pembrolizumab（2L+ G12C 抑制剂经治 NSCLC）。BBO-8520 一线和 BBO-10203 乳腺癌已被降级："BBO-8520 in 1L NSCLC and BBO-10203 in breast cancer have been deprioritized"（MAN-BBOT-3）。
- "NAB-PACLITAXEL" 不是 BBOT 的项目，是 NCT06917079 的联合 / 化疗药物，应剔除。
- BBO-10203 的两条 NSCLC 行（引自 NCT06917079、NCT06343402）没有挂试验，疑为联合用药误归。适应症大小写不一（"Non-Small" / "Non-small"）。
- 包中缺少适应症：BBO-11818 / BBO-10203 的 CRC、PDAC，以及 BBO-10203 的乳腺癌。
- total_debt 为空：10-Q 确实未见债务。

## 用时

约 35 分钟。
