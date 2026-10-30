# REPL（Replimune Group）复核草稿报告

## 推荐组合

- 资产 / 适应症：RP2（sturlimgene erparepvec，HSV-1 溶瘤免疫疗法，表达抗 CTLA-4 抗体样分子）/ Metastatic Uveal Melanoma。注册导向随机 2/3 期 REVEAL（NCT06581406）正在入组，2027 年第一季度转入 3 期。
- 买方：GSK，治疗领域偏好第 1（肿瘤，ideal_stage「Phase 2-3」）。
- 交易形式：收购（权益完整，推断）。
- 分数：buyer_fit 3（中）、stage_match 4（高）、clinical 2（高）。catalyst 与 dealability 由 build 从 [event]（medium / disclosed）与 [rights]（full）推导。

选择理由：

- 公司价值主要在 RP1（TUDRIQEV）。它已于 2026-08-06 获 FDA 加速批准，2026-10-06 在美国上市（MAN-REPL-1、MAN-REPL-2）。但 RP1 与所有买方行都配不好：
  - 阶段：只有 AbbVie #3 的区间到「上市」。AbbVie 画像是「ADC、抗体药物或靶向小分子」，不含溶瘤病毒，buyer_fit 最多 2。GSK、BMS、Roche、AZ、J&J 的区间到 3 期，已上市资产 stage_match 为 0。Merck #1、Pfizer #2 到注册期，得 2。
  - 催化：RP1 唯一有时间的大事件是 IGNYTE-3 OS 数据，原文 "IGNYTE-3 randomized confirmatory trial ongoing with OS data expected in 2030"（MAN-REPL-3），在 24 个月窗口外。ARTACUS 发表与 CERPASS 研究报告只给了「in 2026」，属低重要性。
- RP2 / mUM 配 GSK #1：画像点名「实体瘤的…免疫肿瘤资产」，是唯一点名该技术类型的肿瘤行；阶段 Phase 2-3 吻合。画像没有点名葡萄膜黑色素瘤或溶瘤病毒，所以 buyer_fit 给 3，不给 4。
- 备选：RP1 / Advanced Melanoma / Merck #1。Merck 画像「能在KEYTRUDA单药/联用之外形成新标准治疗」与 RP1 的抗 PD-1 进展后适应症有对应。但黑色素瘤不在画像点名的癌种中，阶段差一档，而且 RP1 的标签联用的是 BMS 的 nivolumab。复核人如果认为必须围绕 TUDRIQEV 推荐，可改选此组合。
- 组合冲突：未核查组合冲突。10-K 竞争段只列类别，不列公司产品。

## 资产权益

- 状态：full（推断，中高）。10-K 与 10-Q 没有逐字写「全球权益」。
- 10-K 原句：
  - "Our proprietary RPx platform is based on a novel, engineered strain of herpes simplex virus 1"
  - "For the core technology in our RPx platform and each of our product candidates, we initially filed six patent applications under the Patent Cooperation Treaty"
  - BMS（RP2 供药）："BMS granted us a non-exclusive, non-transferrable, royalty-free license (with a right to sublicense) under its intellectual property to use nivolumab in the clinical trial"；"Both parties will own the study data produced in the clinical trial"
  - Roche（RP2 HCC 供药）："retaining all the rights to the development and commercialization of our product candidates"
- 10-Q 原句："BMS supplied nivolumab is being used in the conduct of the REVEAL clinical trial"。
- 10-K 附件清单中，协议类只有 BMS（RP1、RP2）与 Regeneron 的临床试验合作及供药协议，没有许可协议。没有找到对许可方的特许权使用费或里程碑义务。
- 债务（pack 中 total_debt 为 9,977 万美元）：Hercules 有担保定期贷款，"aggregate maximum principal amount of up to $ 200.0 million"；2026 年 9 月 "drew down the initial tranche 4 amount of $ 15.0 million"；未来应付本金 102,453 千美元；契约 "could prevent us from taking certain actions without the consent of our lenders"（10-Q）。
- 现金指引（10-Q）："sufficient to fund its operations and capital expenditure requirements for greater than twelve months from the issuance of these condensed consolidated financial statements"。pack 的 runway_months 为 13.2。
- EV：市值 15.22 亿 + 债务 0.998 亿 − 现金 3.078 亿 ≈ 13.1 亿美元（<20 亿档）。

## 待核实

1. 风险因素中有 "our licensed patents"、"issued patents that we license from third parties"。10-K 附件与 Item 1 中没有找到对应的许可协议。是否存在引进许可，需人工核实。
2. Hercules 贷款在控制权变更时是否必须提前还款，未核查。
3. REVEAL 转入 3 期时是否公布 2 期数据，公司没有说明。备选同期事件：RP2 HCC / BTC 初步结果，原文 "we expect to share preliminary findings in the first quarter of 2027"（10-Q）。BTC 不在 pack 中。
4. RP2 mUM 疗效数据只来自 10-K 对 2023 年 11 月会议更新的转述。会议摘要原文与同行评议论文都没有打开。
5. GSK 是否已有溶瘤病毒或 mUM 资产，未核查。
6. 卖方意愿：公司刚自行上市 TUDRIQEV，原文 "is now commercially available in the United States"（MAN-REPL-2）。这不在 §7 障碍项中，但影响收购谈判。

## Pack 问题

- RP1「Advanced Melanoma」的 stage 是 phase3，应为 approved（FDA 加速批准，2026-08-06，MAN-REPL-1）。approved_products 为空，可能是 openFDA 滞后。
- 全部 auto_pairs 都指向 RP1 / NSCLC。10-K 中 RP1 没有 NSCLC 项目，疑为 IGNYTE 试验条件映射噪声。
- RP2 的 program 名为「RP2 (RP2 MONOTHERAPY)」，但 REVEAL 是 RP2 联合 nivolumab。10-K 给出通用名 "sturlimgene erparepvec"。
- RP3：10-K 原文 "Due to program prioritization we are currently not pursuing further development of RP3 at this time"。CRC 试验已终止，SCCHN 试验已撤回。
- RP1「Merkel Cell Carcinoma」（ARTACUS）与「Cutaneous Squamous Cell Carcinoma」（CERPASS）均已关闭入组，原文 "We have closed enrollment in the ARTACUS trial"、"the CERPASS trial, is fully closed"。

## 用时

约 30 分钟。
