# CLDX（Celldex Therapeutics）复核草稿报告

## 推荐组合

- 资产 / 适应症：BARZOLVOLIMAB（CDX-0159，抗 KIT 单抗）/ Chronic Spontaneous Urticaria（CSU），3 期已读出顶线（2026-09-22，MAN-CLDX-1）。
- 买方：Bristol Myers Squibb，治疗领域偏好第 2（免疫炎症，ideal_stage「Phase 1b-3」）。
- 交易形式：收购（权益完整）。
- 分数：buyer_fit 4（中）、stage_match 4（高）、clinical 3（高）；catalyst 与 dealability 由 build 从 [event] / [rights] 推导。

选择理由：

- 适应症改选 CSU。自动初筛选的是 Chronic Inducible Urticaria。CSU 同为 3 期，并且是 3 期读出与 2027 年 BLA 所在的适应症。
- 买方不用自动初筛的 AbbVie #1。AbbVie 画像点名「IL-13、TSLP、IL-23、TL1A」通路与「皮炎、哮喘、炎症性肠病」。KIT 与 CSU 都不在其中，最多 2 分。（注：Celldex 的 CDX-622 是 SCF/TSLP 双抗，与 AbbVie 画像吻合，但只在 1 期。）
- Novartis #2 的标签（过敏 / 抗体 / 长效）也符合。但 10-K 竞争表显示 Novartis 已在 CSU 持有 Xolair 与 remibrutinib。机制不同，不构成组合冲突，但「需求」论证最弱。
- BMS #2 画像「持久缓解…或免疫重置…覆盖皮肤」与 EAACI 停药后数据对应：\"sustained off-treatment improvement in patients with CSU\"、\"shift treatment goals from symptom control to disease modification\"（MAN-CLDX-2）。BMS 不在 10-K 的 CSU 竞品表中。J&J #2（「慢性炎症疾病的长效生物药」）为备选。

## 资产权益

- 状态：full（推断，中高）。10-K 没有逐字写「全球权益」。
- 10-K 原句：\"Summarized below is our significant research collaboration and license agreement for our current clinical drug candidates.\" 其后只列 Yale 一项（引进方向）。另一句：\"We own a portfolio of patents and patent applications directed to barzolvolimab and other anti-KIT receptor antibodies.\"（MAN-CLDX-3）
- 10-K 附件清单「License, Collaboration, Supply and Distribution Agreements」下只有 Yale 协议。
- 对外义务：Yale 商业里程碑 300 万美元 + 低个位数全球销售特许权使用费（MAN-CLDX-3）。另有 Kolltan 原股东的里程碑，FDA 或 EMA 首次批准时支付 5,250 万美元（10-Q，SEC-0001104659-26-091984）。

## 待核实

1. 事件确定性：公司只说「BLA … in 2027」，只到年份。按简报规则记为 estimated。是否应记为 disclosed，需人工决定。
2. 组合冲突：只按 10-K 竞争表（只列已启动 3 期或已上市的竞品）核查。BMS 早期免疫管线中是否有肥大细胞 / KIT 或 CSU 资产，未核查。
3. 「持久缓解」证据来自 2 期长期随访的会议报告（EAACI 2026）。公司新闻稿是唯一来源，未打开会议摘要原文。
4. 3 期结果只有顶线新闻稿，无同行评议全文。52 周数据与安全性细节待公布。
5. total_debt 在 pack 中为空。在 10-Q 文本中检索 debt / borrowing / loan，只出现在可售债务证券（投资）和 Kolltan 收购段落，未见借款；但没有逐项核实资产负债表。EV 按市值减现金计算，约 16.1 亿美元。
6. 未查 Q3 2026 10-Q（截至 2026-10-30 尚未提交）。
7. buyer_fit 4 是对应「持久缓解 / 免疫重置」这一疗效属性，证据是 2 期停药后随访（公司新闻稿），不是 3 期主要终点。§3.1 的 4 分示例是适应症、机制或给药方式。复核人可能降为 3 分。
8. 卖方意愿：公司表示要自建商业化团队，原文："establishing a commercial-stage organization committed to delivering barzolvolimab to patients"（MAN-CLDX-1）。这不是 §7 模板里的障碍项，没有写进论点，但影响收购谈判。

## Pack 问题

- auto_pair 主组合的适应症选成 CIndU，应为 CSU。
- CSU 3 期 NCT06445023 / NCT06455202 的 primary_completion 为「2026-10 ESTIMATED」，但顶线已于 2026-09-22 公布（data cutoff 2026-09-09）。
- PN 2 期 NCT06366750 显示 ACTIVE_NOT_RECRUITING。公司已宣布终止：\"Celldex is discontinuing the Phase 2 PN study\"（MAN-CLDX-2）。
- 「Cold Urticaria」（1 期）与「Chronic Inducible Urticaria」（3 期 EMBARQ-ColdU/SD）分成两条，实为同一疾病群。
- KLH / Glioblastoma（phase3，无试验）以及 CDX-011、CDX-1401 等肿瘤项目都是历史项目。Merck、Pfizer、Roche 的 auto_pair 是噪声。
- AD 2 期（NCT06727552）顶线预计「late 2026」（MAN-CLDX-2），是窗口内的中等事件，未作为主事件。

## 用时

约 25 分钟。
