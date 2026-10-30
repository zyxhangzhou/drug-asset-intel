# ORIC 复核草稿报告

## 推荐组合

- 资产：rinzimetostat（ORIC-944，PRC2/EED 变构抑制剂），pack 中的 program 为 `RINZIMETOSTAT (ORIC-944)`。
- 适应症：Metastatic Castration Resistant Prostate Cancer（阿比特龙治疗后 mCRPC）。
- 阶段：3 期。8-K 2026-08-03 原文："initiated the Himalayas-1 global Phase 3 registrational trial"（MAN-ORIC-2）。
- 买方：AbbVie #3（肿瘤）。交易形式：收购。
- 分数：buyer_fit 3，stage_match 4，clinical 2。catalyst 与 dealability 由 [event] 与 [rights] 推导，预期分别为 3（高重要性，估算）与 4（EV 约 5.8 亿美元，权益完整）。

### 选择理由

- Pfizer #2 的文字契合度最高（画像含「泌尿」，Xtandi 2027 LOE）。但 Pfizer 有组合冲突，所以排除：
  - 10-K 竞争段："including Ipsen, Novartis, Daiichi Sankyo, Pfizer"（MAN-ORIC-1）。
  - MEVPRO-1 为 Pfizer 的 mevrometostat（EZH2）联合 enzalutamide 3 期，人群为阿比特龙治疗后 mCRPC，主要终点 rPFS。与 Himalayas-1 的人群与终点相同（MAN-ORIC-4）。
- Novartis 也在 10-K 竞品名单中，所以排除。
- Merck、BMS、J&J、Roche、AZ 的画像点名的瘤种不含前列腺癌，只是标签匹配（2 分）。BMS 通过收购 Mirati 成为 rinzimetostat 的许可方；这一点只记在报告中，不作为推荐组合。
- AbbVie #3 画像为「血液瘤和实体瘤ADC、抗体药物或靶向小分子，要求明确差异化和可扩适应症」。它能对应公司原文 "clearly differentiated safety profile" 与 "Several Development Opportunities in Other Solid Tumors"（MAN-ORIC-3）。GSK #1 是备选；它的画像强调「已验证靶点」与「清晰生物标志物」，而 rinzimetostat 不按生物标志物选择患者。
- buyer_fit 给 3，不给 4：AbbVie 画像没有点名前列腺癌或 PRC2，buyers.json 中 AbbVie 也没有前列腺癌 LOE 产品。AbbVie 自身管线未核查（未核查组合冲突）。

## 资产权益：full

- 10-K 原文："We own or license full worldwide development and commercialization rights to each of our programs (other than with respect to our brain-penetrant EGFR program, enozertinib, for which we own exclusive rights worldwide excluding the People's Republic of China, Hong Kong, Macau and Taiwan (the ORIC Territory))."（MAN-ORIC-1）
- 10-Q 原文："The Company will conduct and sponsor the Himalayas-1 trial and maintain full economic ownership and control of rinzimetostat."（SEC-0001193125-26-330631）
- 引进许可来自 Mirati（现为 BMS 子公司）：
  - 许可性质："worldwide, exclusive, sublicensable, royalty-free license"。
  - 付款义务："The Company is not obligated to pay Mirati milestones or royalties."
- 终止条件与后果：
  - 终止后须返还："assign to Mirati, or grant an exclusive license to Mirati"。
  - Mirati 的终止权：如果停止开发达到约定期限，Mirati 可以终止许可。
- 与 Bayer、J&J 的协议都只是供药合作。Bayer 协议原文："does not grant Bayer any license, option, or other rights"。
- 债务：无借款。10-Q 中负债合计为 2,342.9 万美元，只有应付账款、应计负债与其他长期负债。
- 现金跑道：
  - 10-Q 原文："sufficient to fund our operations into the second half of 2028"。
  - pack 中的 runway 为 36.3 个月，到 2029 年中前后，比公司指引更乐观。按公司指引，现金能支撑到 2028 下半年，与 Himalayas-1 读出时间（估算 2028-03）接近。

## 待核实

1. Mirati 许可协议是否有控制权变更或转让限制条款。10-Q 与 10-K 的摘要没有披露这一点。BMS 是许可方，这会影响收购。
2. AbbVie 自身在前列腺癌和 PRC2/EZH2 方面的管线（组合冲突）未核查。
3. Himalayas-1 读出时间只有 CT.gov 估算（2028-03）。公司没有给出季度或半年。8-K 中的规模约 600 例，同年 3 月的幻灯片为每组 300 例，两处一致。
4. 「2H 2026 Program update」的内容与重要性不明。截至 2026-10-30，没有找到对应的 8-K。
5. Himalayas-2（apalutamide 联合）在 3 月幻灯片中写为 "in 2027"，只有年份，所以不计为明确披露。
6. 疗效数据只有公司幻灯片，没有同行评议全文或会议摘要。

## Pack 问题

- rinzimetostat 拆成两行：phase3 mCRPC（NCT07723248）与 phase1 Metastatic Prostate Cancer（NCT05413421）。NCT05413421 实际是 1b 期剂量探索与优化试验，即本复核引用的临床数据来源。
- ORIC-114 = enozertinib，但 pack 中只有 "Solid Tumors"，缺 NSCLC 适应症，也没有通用名。
  - 阶段：8-K 2026-10-23 写 1b 期，并计划 2027 上半年启动全球 3 期："plans to initiate a global Phase 3 registrational trial of enozertinib in the first half of 2027"（MAN-ORIC-5）。
  - 疗效：1L EGFR atypical 研究者评估 ORR 84%（21/25）。
  - 权益：partial（不含大中华区），并欠 Voronoi 里程碑与特许权使用费。
  - 结论：enozertinib 是第二资产，本次不作为推荐组合。
- NAB-PACLITAXEL 是 ORIC-101 联合用药臂，不是 ORIC 资产，应从推导管线中剔除。
- ORIC-101（试验已终止）与 ORIC-533（1 期已完成）不在公司当前管线描述中。8-K 中的 "ORIC's clinical stage product candidates include" 只列了 rinzimetostat 与 enozertinib。

## 用时

约 35 分钟。
