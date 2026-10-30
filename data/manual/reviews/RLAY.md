# RLAY（Relay Therapeutics）复核草稿报告

## 推荐组合

- 资产 / 适应症：zovegalisib（RLY-2608）/ PI3Kα 突变 HR+/HER2- 晚期乳腺癌（CDK4/6 抑制剂治疗后）。TOML 中 `indication = "PIK3CA Mutation"`，因为 pack 里没有乳腺癌这条适应症（见「pack 问题」）。
- 买方：Pfizer，肿瘤偏好第 2 位。交易形式：收购。
- 为什么不选自动主组合 Merck #1：Merck 的目标画像是“肺癌、胃肠癌、妇科癌或血液肿瘤”，不含乳腺癌。Pfizer #2 的画像写明“靶向小分子……覆盖乳腺”。Ibrance（palbociclib）美国 LOE 2027（MNC-WB），zovegalisib 的人群正是 CDK4/6 治疗后患者。Pfizer 已为 Relay 的 3 期试验供应 atirmociclib 与 palbociclib（10-Q）。
- 为什么不选其他肿瘤买方：10-K 竞争段点名 Novartis（Piqray，PI3Kα）、Roche（Itovebi，PI3Kα）、AstraZeneca（Truqap，AKT，且是 ReDiscover-2 对照药），三家都有同适应症资产，存在组合冲突。BMS、GSK、J&J 画像没有对应条目或不含乳腺癌。
- 分数：buyer_fit 4（中）、stage_match 4（高）、clinical 2（中）。catalyst 与 dealability 由构建推导（事件：高重要性 / 估算；权益 full，EV 约 34 亿美元）。

## 权益状态：full（推断）

10-Q（2026-06-30，SEC-0001193125-26-338056）与 10-K（MAN-RLAY-1）没有披露任何第三方持有 zovegalisib 的许可、选择权、优先谈判权或共同开发权。关键原文：

- 10-K：“D. E. Shaw Research has no involvement with the clinical development or potential commercialization of these compounds and products, regardless of any co-ownership rights pursuant to the terms of the DESRES Agreement, and instead receives solely milestone and royalty payments as described below.”
- 10-K：“Our PI3K, FGFR2, and NRAS programs are each directed to Category 1 Targets.” 义务：低个位数全球销售特许权使用费；每个产品开发 / 监管里程碑最高 730 万美元；销售里程碑最高 3,600 万美元；对外授权时分享低至高个位数比例的交易收益。
- 10-Q：Pfizer 只有临床试验合作（2024-06）和供药协议（2026-04）。
- 10-K 专利表述前后不一：组成物专利“co-own with D.E. Shaw Research”，另一处说已“obtained sole ownership of intellectual property rights relating to it”。收购尽调时需核实。

## 待核实

1. ReDiscover-2 读出时间：公司文件未披露，只有 CT.gov 预计主要完成日期 2028-04-30。
2. ReDiscover-2 主要终点：已读 10-K 中未找到 “primary endpoint” 表述；CT.gov 记录未在本次打开。
3. Pfizer 自有管线中是否有 PI3Kα / PI3K 通路资产：只查了 Relay 10-K 竞争段（未点名 Pfizer），没有查 Pfizer 自己的文件。组合冲突仅部分核查。
4. ESMO TAT 2026 摘要原文 / 同行评议论文：未打开，临床数据只来自公司 8-K 新闻稿。
5. 专利归属：共有还是独有（见上）。
6. Pfizer 供药协议中有没有 ROFN / 选择权条款：10-Q 只说是 supply agreement，协议原文未打开。

## pack 问题

- 适应症错：ZOVEGALISIB 只有 “PIK3CA Mutation”（生物标志物，不是疾病）。关键 3 期 NCT06982521 的疾病是 HR+/HER2- 晚期乳腺癌，pack 缺这条适应症，建议在 CT.gov 推导里加入 “Breast Cancer”。
- 资产未合并：RLY-2608 与 ZOVEGALISIB 是同一药物，pack 拆成两个 program（RLY-2608 下还有 PROS 与 1 期 ReDiscover）。
- 资产归属错：PF-07220060 是 Pfizer 的 atirmociclib（联合用药），不是 Relay 资产。
- 阶段：ReInspire（NCT06789913）在 10-Q 中写为 “global Phase 1/2 clinical trial”，pack 标 phase2。
- RLY-5836 的试验已完成，10-Q 管线描述未再提及，可能已停止开发（未核实）。

## 用时

约 25 分钟。
