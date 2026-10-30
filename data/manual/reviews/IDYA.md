# IDYA（IDEAYA Biosciences）复核草稿报告

## 推荐组合

- 资产 / 适应症：darovasertib（口服 PKC 抑制剂）+ crizotinib / 一线 HLA-A*02:01 阴性转移性葡萄膜黑色素瘤（mUM）。注册性 2/3 期 OptimUM-02 已达到主要终点。NDA 在 RTOR 下滚动提交。
- TOML 匹配：`program = "DAROVASERTIB"`，`indication = "Metastatic Uveal Melanoma"`（pack 第 1495 行）。
- 买方：Pfizer，治疗领域偏好第 2（肿瘤，ideal_stage「Phase 2b-注册期」）。
- 交易形式：收购（整体收购）。
- 分数：buyer_fit 3（中高）、stage_match 4（高）、clinical 3（高）。catalyst 与 dealability 由 build 推导：事件为 high + disclosed，权益为 partial，dealability 最高 3 分。

选择理由：

- Pfizer 的画像点名「靶向小分子」，技术偏好第 2 行是「ADC、双特异和靶向小分子」。darovasertib 是口服靶向小分子。联用药 crizotinib 是 Pfizer 自有产品，双方已有临床供药协议（10-Q："crizotinib, Pfizer’s oral c-MET inhibitor"）。
- buyer_fit 只给 3 分：Pfizer 点名的瘤种是乳腺、肺、泌尿和血液肿瘤，不含葡萄膜黑色素瘤，也不对应 Pfizer 的 LOE 产品。
- Pfizer 的 ideal_stage「Phase 2b-注册期」覆盖「关键试验阳性 + NDA 提交中」，stage_match 4 分。
- 不选 Merck #1。画像中「能在 KEYTRUDA 单药/联用之外形成新标准治疗」与 OptimUM-02 打败含 pembrolizumab / ipi+nivo 的对照臂相符，但点名的瘤种（肺、胃肠、妇科、血液）不含 UM。Merck 的技术偏好行也不含肿瘤靶向小分子，只能得 2 分。自动初筛主组合为 Merck #1，buyer_fit 2 分。
- 不选 Novartis #3。10-K 竞争段列出 Novartis DYP688（GNAQ/11 抑制剂 payload 的 ADC，mUM 1/2 期），属同适应症冲突。Novartis 也是 darovasertib 的原始许可方。
- 不选 IDE849（DLL3 TOP1 ADC）。它从恒瑞引进，只有大中华区以外权益，仍在 1/2 期。
- 组合冲突：只按 IDEAYA 10-K 竞争段核查，名单不含 Pfizer。

## 资产权益

- 状态：partial（美国以外区域已许可给 Servier）。
- 10-Q 原句："The Company retains all rights to darovasertib in the United States."（SEC-0001193125-26-332774）
- 10-K 原句："We retain all rights to darovasertib in the United States."（MAN-IDYA-1）
- Servier 区域："to develop and commercialize products in all countries worldwide except for the United States"。Servier 负责美国以外的监管与商业化。双方共同开发、分担费用："The Company and Servier will collaborate on the development of darovasertib and share the associated costs"。本草稿把这句读作区域许可下的研发分担，不是美国共同商业化。
- **ROFN（10-Q / 10-K 正文未披露，出自许可协议原文，Exhibit 10.1，MAN-IDYA-6）**：
  - §2.5(a)：IDEAYA 若单独许可或出售美国权益，须先通知 Servier，并给予排他谈判期。
  - 并购与控制权变更不在 ROFN 范围内："other than (x) in connection with any merger, consolidation, sale of substantially all of IDEAYA’s assets or business"。
  - §17.11：控制权变更只需通知 Servier；收购方若是 Servier 的直接竞争者，须设防火墙。
  - "Post-ROFN Protection . [***]" 被涂黑，内容未知。
- 引进义务（Novartis）：
  - 剩余开发 / 监管里程碑最高 800 万美元，销售里程碑最高 2,000 万美元。
  - 另付中至高个位数分级特许权使用费。
  - 原文："subject to certain economic obligations pursuant to its exclusive, worldwide license to darovasertib with Novartis"。
- crizotinib 只有临床供药协议，不涉及商业权益。
- 债务：无。10-Q 资产负债表负债只有应付账款、应计费用和经营租赁负债，总负债 110,794 千美元。
- 资金：pack runway 为 45.6 个月。Q2 新闻稿给的指引是 "cash runway guidance into 2030 is unchanged"（MAN-IDYA-4）。10-Q 只有 "sufficient to fund its planned operations for at least twelve months" 的套话。

## 待核实

1. **权益分类需签字人决定（最重要）。** Servier 对美国区域的单独许可或出售持有 ROFN（Ex. 10.1 §2.5）。并购与控制权变更不在 ROFN 范围内，所以「收购」不受阻挡，本草稿据此标 partial。如果按 brief 的字面定义（有 ROFN 即 restricted），状态要改为 restricted，「收购 + restricted」会被挡出入选名单。注意：单独许可美国权益不能作为备选交易形式，这正是 ROFN 的触发条件。另外，ROFN 只出现在许可协议原文中，不在最新 10-K / 10-Q 正文里。
2. Novartis 2018 许可协议原文未打开。10-K / 10-Q 只写 "certain economic obligations"。在 10-K 中检索 change of control / right of first / co-commercial / profit，未见与 Novartis 相关的条款。
3. 与 Servier「共同开发、分担费用」的具体比例与治理（JSC）条款未细读。
4. Pfizer 是否已有同机制、同适应症资产：只核查了 IDEAYA 10-K 的竞争段，Pfizer 自身管线未核查。
5. OptimUM-02 的 OS 未成熟，预设中期分析在 2027 年年中，结果未知。没有同行评议全文，只有 8-K、ASCO 海报和新闻稿。
6. NDA 截至 2026-10-19 尚未完成提交。是否已完成、何时受理、PDUFA 日期都未知。EDGAR 文件列表只到 2026-08-04；2026 年第三季度 10-Q 尚未提交。
7. ESMO 2026 的 OptimUM-01 / 09 数据只经 WebFetch 摘要读取，未作为评分依据。

## Pack 问题

- 阶段偏低：pack 中 mUM 为 phase2_3（CT.gov）。实际上，注册性 2/3 期已于 2026 年 4 月达到主要终点，NDA 正在 RTOR 下滚动提交，2026 年下半年完成。
- 「Uveal Melanoma」行为 phase3，依据是 OptimUM-10 / OptimUM-11。10-Q 称 OptimUM-10（新辅助）因招募问题正在重新评估资本配置；OptimUM-11（辅助）2026-09 已首例给药，由 Servier 合作开展。
- 程序名重复：同一 PARG 抑制剂出现为「IDE-161」和「IDE161」两行。「IDE161 / Small-cell Lung Cancer」实际是与 IDE849 的联合试验。「IDE397 / NSCLC Adenocarcinoma」借用了 IDE892 的试验（NCT07277413）。
- IDE849 从恒瑞引进，只有大中华区以外权益，pack 中看不出来。
- NCT05987332 的 primary_completion_date 2027-01-15 可能对应 OS 终点（推断，未核对 CT.gov 登记）。PFS 主要分析已于 2026-04 读出，因此自动初筛的「主要终点数据（估算）」事件已过时。

## 用时

约 35 分钟。
