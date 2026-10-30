# BCAX（Bicara Therapeutics）复核草稿报告

## 选定组合

- 资产 / 适应症：ficerafusp alfa（原 BCA101），1L R/M HPV 阴性 HNSCC（包内 program `FICERAFUSP ALFA (BCA101)`，indication `Metastatic Head and Neck Squamous Cell Carcinoma`）。
- 买方：Merck & Co. #1（肿瘤/血液肿瘤，ideal_stage「Phase 2b-注册期」），交易形式：收购。
- 选择理由：资产与 pembrolizumab 联用，联用数据由 Bicara 与 MSD 共有；Keytruda 美国核心专利约 2028 年到期（MNC-WB）。资产有望在 Keytruda 一线头颈癌方案之上形成新标准治疗。
- 弱点：Merck 画像点名肺癌、胃肠癌、妇科癌、血液肿瘤，不含头颈癌。因此 buyer_fit 给 3，不给 4，置信度为中。
- 备选买方：
  - AbbVie #3（「实体瘤…抗体药物，要求明确差异化和可扩适应症」）。10-K 的 HNSCC 竞争名单里没有 AbbVie。
  - GSK #1（「实体瘤的已验证靶点…免疫肿瘤资产」）。10-K 把 GSK 列为 HNSCC 在研公司，但没写产品或机制。
  - 两者的字面匹配度与 Merck 相近，复核人可以改选。

## 分数

| 维度 | 分 | 要点 |
|---|---|---|
| buyer_fit | 3（中） | 领域与技术偏好相符；画像瘤种不含头颈癌；未核查 Merck 早期管线 |
| stage_match | 4（高） | 2026-02 已转入 3 期部分 |
| clinical | 2（中高） | 仅有 1/1b 期单臂数据，ORR 54%、CR 25%（1500 mg QW，n=28）；只有跨试验比较 |
| catalyst（由 [event] 推导） | 预计 3 | FORTIFI-HN01 期中顶线，公司称 "mid-2027"；重要性高，确定性按估算 |
| dealability（由 [rights] 推导） | 预计 4 | 权益 full；快照 EV 约 1.49 亿美元 |

- clinical 的另一种读法：可以把单臂 ORR 归入肿瘤领域「单臂数据可作注册依据」条款，给 3 分。
- 我没有这样给。原因是注册路径依赖随机双盲试验的期中 ORR，不依赖单臂数据。复核人可以上调。
- event 的确定性："mid-2027" 不是季度，也不是半年，所以按 brief 记为 estimated。复核人如果认为「年中」算明确披露，可以改为 disclosed。改后 catalyst 从 3 变为 4。

## 权益状态：full（推断，中高）

- 10-K 原文（许可授予）："Pursuant to the Biocon Agreement, we and Biocon agreed that Biocon would grant us a license, with the right to grant and authorize sublicenses to make, use, sell, offer to sell, import, and otherwise exploit certain fusion protein products of which ficerafusp alfa was the most advanced program."
- 10-K 原文（付款义务）："Additionally, there are no future milestone payments, royalty terms or any additional payments required."
- 10-K 和 10-Q 都没有逐字写「worldwide」，也都没有披露对外授权、选择权、ROFN 或共同开发。MSD 协议只是 1/1b 期的供药合作，联用数据由双方共有，不构成限制。
- 无债务：10-Q 的总负债为 4,347.5 万美元，只有应付款、应计费用和经营租赁。包内 `total_debt` 为空，这是正确的。
- 现金跑道，10-Q 原文："sufficient to fund our operations and capital expenditure requirements into the first half of 2029"。

## 待核实

1. Biocon 许可的地域范围：10-K 没有写明「全球」，需要读许可协议原文（10-K 附件）确认。
2. Merck 早期管线中有没有 EGFR、TGF-β 或同类双功能分子用于 HNSCC：未核查，组合冲突未核查。
3. FORTIFI-HN01（3 期）的 pembrolizumab 由谁供应：10-K 中 MSD 协议只覆盖 1/1b 期，关键研究的供药或合作条款没有找到。
4. Y-Trap 发明人更正诉讼与 PTAB 复审（2026-07-15 立案）的结果，以及它们对许可专利的影响：诉讼尚未结案。
5. 不良事件的具体发生率：只引用了公司的笼统表述，没有读 ASCO 海报全文。
6. 1500 mg QW 组的 3 年 OS 31% 和中位 OS 21.3 个月来自公司新闻稿，没有同行评议全文。

## 数据包问题

- 阶段：包内为 `phase2_3`。10-K 写明 2026 年 2 月已完成向 3 期部分的过渡，应按 3 期读。
- 适应症：包内为「Metastatic HNSCC」，缺少「1L / HPV 阴性 / PD-L1 CPS≥1」限定。真实注册人群是 1L R/M HPV 阴性、CPS≥1 的 HNSCC。
- NCT07807163 是 FORTIFI-FLEX，一项给药方案研究（负荷剂量后改为 Q3W 维持），不是第二项疗效研究。公司预计在潜在的美国加速批准之前拿到它的结果。
- NCT04429542 的 indication 为「Head and Neck Squamous Cell Carcinoma」，阶段为 phase1。这是 1/1b 期研究，也包括 mCRC 扩展队列；包内没有 mCRC 适应症（数据预计 2026 年下半年公布）。

## 用时

约 35 分钟。
