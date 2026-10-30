# ERAS（Erasca, Inc.）复核草稿报告

## 推荐组合

- 资产 / 适应症：ERAS-0015（pan-RAS 分子胶）/ pack 适应症「Metastatic Solid Tumors」。实际数据集中在 2L+ KRAS G12X 非小细胞肺癌（NSCLC）与胰腺癌（PDAC）。
- 买方：AstraZeneca，治疗领域偏好第 1（肿瘤，ideal_stage「Phase 2-3」）。
- 交易形式：收购。
- 分数：buyer_fit 4（中）、stage_match 2（高）、clinical 2（中高）。catalyst 与 dealability 由 build 推导。
- 预览构建结果（只构建 ERAS）：组合解析到 program_indication 169（ERAS-0015 / NCT06983743），catalyst 3、dealability 3、rights full、保守分 72.5、覆盖率 1.0。

选择理由：

- 公司只剩 RAS 管线。10-Q 原文："two clinical-stage programs (ERAS-0015, a pan-RAS molecular glue; and ERAS-4001, a pan-KRAS inhibitor)"。ERAS-0015 是唯一有人体疗效数据的资产。
- 买方选 AZ #1。画像点名「肺癌」「靶向小分子」。ERAS-0015 的首个潜在注册试验在 2L+ NSCLC："Potentially registration-enabling trial in 2L+ NSCLC expected to initiate in the first half of 2027"。
- AZ 不在 10-K 竞争段的 RAS/MAPK 在研公司名单中。AZ 自身 RAS 管线没有用一手来源核查（未核查组合冲突）。
- 「分子胶 = 靶向小分子」是推断（中高）。10-K 只写 "pan-RAS molecular glue" 和 "oral bioavailability"。
- 不选 Roche #1。Roche 画像点名 KRAS，文字最贴近。但 Roche/Genentech 在 10-K 竞争名单中，同机制冲突无法排除，buyer_fit 最高 3。
- 不选 Merck #1。Merck 也在竞争名单中。Merck 与公司有 Keytruda 供药协议（CTCSA），这是供药，不是权益。
- 所有肿瘤买方（Novartis 除外）的 ideal_stage 从 2 期起，ERAS-0015 为 1 期，stage_match 都是 2。不选 Novartis #3：画像是放射性配体 / ADC / 新 payload，不含小分子。

## 资产权益

- 状态：full（事实）。来源为 10-Q 第 7 项附注（SEC-0001193125-26-344611）。
- 引进许可原句："exclusive, worldwide (except mainland China, Hong Kong, and Macau), royalty-bearing license"。
- 期权行使原句："In March 2026, the Company sent Joyo notice that the Company was exercising its option to expand its territory under the Joyo License Agreement to include mainland China, Hong Kong, and Macau"。公司支付 1.5 亿美元。
- 对 Joyo 的义务：开发 / 监管里程碑最高 5,750 万美元，销售里程碑最高 1.25 亿美元，"tiered royalties on net sales of all licensed products, in the low- to mid-single digit percentages"。
- 终止条款（10-K）："Joyo has an option to negotiate a license"。
- 未见对外授权、选择权或共同开发。Tango 与 Merck 协议只是临床试验合作与供药。
- 债务：pack 的 total_debt 为空。10-Q 资产负债表负债只有应付账款、应计费用、经营租赁负债与其他负债，未见借款。
- 资金：10-Q 原句："together with the net proceeds of $593.5 million received from the July 2026 Offering, will be sufficient to achieve the anticipated corporate milestones set forth in this quarterly report"。

## 主要风险

- 监管状态（参考）：8-K 原文："has granted Fast Track Designation" 给 ERAS-0015，"for the treatment of patients with metastatic pancreatic adenocarcinoma"（MAN-ERAS-3）。不改变评分。

- 知识产权：2026-04-24 Revolution Medicines 来函，指控 ERAS-0015 等同侵犯其 '225 专利，并涉及商业秘密盗用。RevMed 要求公司停止在美国制造和使用 ERAS-0015（Hatch-Waxman 安全港以外）。公司称指控无依据。
- 诉讼：证券集体诉讼（2026-06-10）与股东派生诉讼（2026-08），派生诉讼涉及 ERAS-0015 的披露。
- 安全性：1 例 3 级肺炎进展为 5 级（死亡）。

## Pack 问题

- 自动主组合用的是 naporafenib，资产不对。公司已停止开发，Novartis 许可 2026-06-03 终止。10-Q 原文："the Company made a decision to stop development of naporafenib"。全部 9 个 auto_pairs 都基于 naporafenib，都无效。
- ERAS-007（Asana）与 ERAS-601（NiKang）的许可在 2025 年终止（10-K），pack 里仍作为在研项目。
- ERAS-0015 的适应症在 pack 中只有「Metastatic Solid Tumors」。缺少 KRAS G12X NSCLC 与 PDAC 的细分适应症。
- `program = "ERAS-0015"` 同时是 program 169 和 170（"ERAS-0015 IN COMBINATION (ERAS-4001 IN COMBINATION)"）的子串。预览构建解析到 169，结果正确，但匹配有歧义。
- 财务：pack 现金 3.843 亿美元为 6 月 30 日数据，未计 7 月增发净额 5.935 亿美元。快照 EV 约 49 亿美元，计入增发后约 43 亿美元，成本档位都是 20–50 亿。pack 的股本是否已含 7 月增发的 3,614 万股，未核查。
- 阶段：许可方 Joyo 已在中国启动 2 期（"Joyo had dosed the first patient in a Phase 2 clinical trial"）。pack 中没有这项试验。

## 待核实

- AZ 是否有同机制（pan-RAS / pan-KRAS）的肺癌资产。
- Joyo 中国试验（JYP0015M101 及其 2 期）的数据归属，以及中国 2 期的设计。
- 1L PDAC 3 期启动时间只披露到年份（"expected to initiate in 2027"）。
- RevMed 争议是否已进入诉讼（10-Q 截至 2026-08-11 只写 "may seek to initiate litigation"）。
- 2026 年第三季度 10-Q 尚未发布。ERAS-4001 的 1 期数据预计 2026 年下半年发布（不同资产，未计入事件）。

## 用时

约 35 分钟。
