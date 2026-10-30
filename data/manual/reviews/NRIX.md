# NRIX 复核报告（草稿，待人工签核）

**结论：建议不入选。** 主资产 bexobrutideg（NX-5948）已在 2026-06 授权给 Roche（全球独家许可，美国 50/50 共同开发与共同商业化，美国以外由 Roche 商业化）。其他买方没有可收购或可许可的权益。Nurix 其余资产不足以支撑推荐（见下文）。

## 组合

- 资产 / 适应症：NX-5948（bexobrutideg，口服 BTK 降解剂）/ Chronic Lymphocytic Leukemia。
- 买方：Roche 第 1 治疗领域偏好（肿瘤/精准医疗，画像「血液瘤的精准小分子」），交易形式「合作」（即现有合作）。
- 选 Roche 的理由：Roche 是唯一能就该资产交易的对象。选其他买方（如 BMS 技术行「CELMoD/靶向蛋白降解」）在文字上更贴合，但该买方无权益可得，属于编造配对。
- 分数：buyer_fit 3（中，Roche 已持有该资产；签核人可改 0）；stage_match 4（高）；clinical 2（中，只有 1 期单臂）。catalyst 由 [event] 推导（高 + 估算 → 3）。dealability：EV 约 18.8 亿美元（< 20 亿档 → 4），受限权益封顶 1。

## 资产权益：restricted

最新 10-Q（截至 2026-08-31，SEC-0001549595-26-000049）原句：

- "the Company granted Roche an exclusive, worldwide license, including with respect to the Company and its affiliates, to develop, manufacture, commercialize and otherwise exploit bexobrutideg"
- "The Company and Roche will co-develop and co-commercialize bexobrutideg in the United States across all indications, and Roche will commercialize bexobrutideg outside the United States."
- "The parties will equally share net profits and net losses from commercialization in the United States."
- 美国以外特许权使用费："tiered royalties at rates ranging from the low teens to the high teens"；预付款 700 百万美元已收到，另有最多约 16 亿美元里程碑。
- Roche 可无因终止："each of Gilead, Sanofi, Pfizer and Roche can terminate its agreement with us in its entirety ... for convenience"。
- 引进许可：未见。bexobrutideg 为自有发现（10-K："Our wholly owned pipeline ..."）。
- 债务：10-Q 资产负债表无票据或贷款；负债为应付、应计、经营租赁、递延收入、递延合作资金（Total liabilities 226,987 千美元）。
- 资金指引：Q3 新闻稿 "runway into the second half of 2029"（MAN-NRIX-3）；10-Q "sufficient to fund our operations for at least the next 12 months"。包内经营现金流 YTD 为正（+447 百万美元），来自 Roche 一次性预付款，不代表经营自给。

## 待核实

1. CLL-201 读出与加速批准申请时间：公司文件未披露季度。2028-01 是 CT.gov NCT07221500 预计主要完成日（估算）。
2. CLL-306 读出时间：CT.gov 预计主要完成 2029-10，超出 24 个月窗口。
3. Roche 协议的控制权变更条款：10-Q 只写 Sanofi 可在控制权变更时终止；Roche 协议原文（附件）未打开。
4. 组合冲突：未打开 Roche 文件核查其 CLL 产品线；buyers.json Roche #2 证据栏提到 fenebrutinib（神经科学行），与 CLL 无直接关系。
5. 1 期数据未见同行评议全文，只有公司新闻稿与 EHA 报告。

## 包数据问题

- NX-5948 3 期试验 NCT07516093（"Versus Pirtobrutinib in R/R CLL/SLL"）被归到 "B-cell Lymphoma" 行；应归 CLL 行。CLL 行阶段标 phase2，实际已进 3 期（10-Q："This Phase 3 study, the DAYBreak CLL-306 trial, enrolled its first patient in August 2026."）。
- NX-2127（zelebrudomide）：2026-08 已停止开发（10-Q："we decided to discontinue further clinical development of zelebrudomide"），包内试验仍标 RECRUITING。应删除或标停止。
- PRODUCT DE-TIL-0255：试验 TERMINATED，子公司 DeTIL Therapeutics 于 2023-11 解散（10-K）。应删除。
- NX-1607：包内适应症 "Ovarian Cancer, Epithelial" 来自 CT.gov 条件列表；10-K 全文无 "ovarian"。实际 1b 期扩展队列为 MSS CRC、NSCLC、CRPC、黑色素瘤，另有联用 pembrolizumab 队列（MAN-NRIX-3）。NX-1607 是唯一全资临床资产；若修正适应症，可重评 Merck #1（「KEYTRUDA 单药/联用之外」，肺癌/胃肠癌），但仍只有 1 期，stage_match 2，仍偏弱。
- 自动配对 Novartis #3 / NX-1607 / 卵巢癌应删除。

## 用时

约 25 分钟。
