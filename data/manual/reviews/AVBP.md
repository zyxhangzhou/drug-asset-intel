# AVBP（ArriVent BioPharma）复核草稿报告

## 推荐组合

- 资产 / 适应症：ARR-217（MRG007，CDH17 靶向 ADC）/ 经治结直肠癌等胃肠道肿瘤。TOML 中 `program = "MRG007"`、`indication = "Solid Tumors"`，因为 pack 里 MRG007 只有 “Locally Advanced or Metastatic Solid Tumors” 这一条适应症（见「pack 问题」）。
- 买方：Merck & Co.，肿瘤 / 血液肿瘤偏好第 1 位。交易形式：许可（权益为 partial，大中华区在 Lepu）。
- 分数：buyer_fit 4（中）、stage_match 2（高）、clinical 2（中）。catalyst 由构建推导（事件：低重要性 / 估算 → 1）；dealability 由构建推导（权益 partial，上限 3；EV 约 4.0 亿美元）。
- 为什么选 Merck #1：画像写明 “胃肠癌”，且要求 “KEYTRUDA单药/联用之外” 的新标准治疗；技术偏好第 1 位写明 “ADC”。代价是阶段：ARR-217 是 1 期，Merck 理想阶段 “Phase 2b-注册期”，stage_match 只有 2。
- 为什么不选 Novartis #3（阶段 0–3 期，stage_match 可得 4）：画像是 “神经退行性疾病遗传药物、放射性配体、ADC或新payload肿瘤药”，不点名胃肠癌；ARR-217 的载荷是 exatecan（"utilizing a glycan-linked, exatecan-based payload"，MAN-AVBP-2），不属 “新payload”。按画像文本，Merck 更贴合。
- 组合冲突：AVBP 10-K 竞争段只覆盖 EGFR 突变 NSCLC，未核查 Merck 自有管线中是否有 CDH17 或胃肠道 ADC。

## 为什么不选 firmonertinib（自动组合里的 9 个肺癌配对）

1. FURVENT 3 期失败（2026-10-06）："did not meet its primary endpoint of progression free survival (PFS) by blinded independent central review (BICR)"；BICR PFS 240mg 11.0 vs 9.5 个月，p=0.0654（MAN-AVBP-4）。公司在 "evaluating the full FURVENT dataset as we determine the most appropriate development path for firmonertinib"。
2. PACC 适应症（ALPACCA，NCT07185997）证据只有 1b 单臂：240mg 一线确认 ORR 68%、BICR 中位 PFS 16.0 个月（MAN-AVBP-5）。ALPACCA 读出时间公司未披露，CT.gov 预计主要完成日期 2029-02，超出 24 个月窗口 → catalyst 0。
3. 权益偏 restricted：firmonertinib 是自 Allist 引进的大中华区以外权益，并有 Joint Clinical Collaboration Agreement（联合委员会、全球研究分担费用、终止后 Allist 回收权），ALPACCA "being conducted jointly with Allist"（MAN-AVBP-1）。按 brief 定义属于共同开发 → restricted，阻断收购。
4. 买方冲突：10-K / 10-Q 竞争段点名 AstraZeneca、Johnson & Johnson；10-Q 原文 "In July 2026, AstraZeneca announced it had entered into an exclusive global license agreement for sunvozertinib"（SEC-0001104659-26-094902）。ALPACCA 对照药 osimertinib 也是 AstraZeneca 产品。

ARR-002（自动主组合，Novartis #3）不选：2026-10 刚完成首例给药，无人体数据；大中华区已授权 Allist，且 8-K 写有 "collaboration committee to oversee and coordinate the joint global development of ARR-002"（MAN-AVBP-6），权益可能为 restricted。

## 权益状态：partial（大中华区在 Lepu）

10-Q（2026-06-30，SEC-0001104659-26-094902）原文：

> Lepu granted to the Company: (i) an exclusive, royalty-bearing, sublicensable license under certain intellectual property owned or controlled by Lepu, to develop, manufacture and commercialize any product containing ARR-217 for all uses in all countries and territories other than Greater China (the “ArriVent Territory”)

10-K（MAN-AVBP-1）原文：

> On January 21, 2025, we entered into the Lepu Biopharma License Agreement with Lepu Biopharma, pursuant to which Lepu Biopharma granted us a right to develop and commercialize ARR-217 (MRG007), an antibody drug conjugate for gastrointestinal cancers, outside greater China, which is mainland China, Hong Kong, Macau and Taiwan.

- 对 Lepu 的义务：里程碑最高约 11.7 亿美元；大中华区以外净销售额高个位数至低双位数特许权使用费；2026 上半年 Lepu 已获 1,200 万美元开发里程碑（已付 600 万）。
- Lepu 段未见选择权、优先谈判权、联合委员会或利润分成；但 10-K 风险因素写 "are collaborating with Lepu Biopharma with respect to ARR-217"。协议原文未打开。
- 债务：SVB 7,500 万美元贷款额度，"No amounts have been drawn on this Term Loan as of June 30, 2026"（10-Q）。pack 的 `total_debt` 为空与此一致（未提取）。
- 现金指引：Q2 新闻稿原文 "Cash and investments of $373.1 million as of June 30, 2026 expected to fund operations into 2028"（MAN-AVBP-3）。pack runway 27.5 个月。

## 待核实

1. Lepu 许可协议原文：有无共同开发、优先谈判权或控制权变更条款（10-K 只摘要；Alphamab 协议有控制权变更终止条款，Lepu 段未见）。
2. Merck 自有管线中是否有 CDH17 或胃肠道 ADC：未查 Merck 文件，组合冲突未核查。
3. ESMO 2026 摘要原文：未打开，临床数据只来自公司 8-K 新闻稿。
4. 1b 剂量优化数据的具体时间：公司只说 "expected in 2027"。
5. 结直肠癌三线及以后标准治疗的关键试验数据：未打开，无法做跨试验比较。

## pack 问题

- MRG007（ARR-217）只有 “Locally Advanced or Metastatic Solid Tumors”，缺 “Colorectal Cancer / Gastrointestinal Cancers”。程序名建议合并 MRG007 与 ARR-217。阶段 phase1 正确（已进入 1b 剂量优化）。
- FURMONERTINIB “Metastatic Non-Small Cell Lung Cancer”（NCT05607550，FURVENT）仍标 phase3，CT.gov 状态 ACTIVE_NOT_RECRUITING；但 2026-10-06 已宣布主要终点失败（MAN-AVBP-4）。自动配对给该行 stage_match 4 不合理。
- FURMONERTINIB 的 “Non-Small-Cell Lung Cancer”（NCT07185997）实为 EGFR PACC 突变一线 NSCLC（ALPACCA）。
- 自动主组合 ARR-002 / Novartis #3 偏弱（无人体数据）。

## 用时

约 30 分钟。
