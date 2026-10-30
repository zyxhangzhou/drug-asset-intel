# GLUE（Monte Rosa Therapeutics）复核草稿报告

## 选定组合

- 资产 / 适应症：MRT-2359（口服 GSPT1 分子胶降解剂）/ Castration-Resistant Prostate Cancer（AR 突变 mCRPC），pack program_indication id 1875。
- 买方：Pfizer 第 2 治疗领域（肿瘤，补缺），preference_rank = 2。交易形式：收购。
- 选 Pfizer 而不选自动主推的 Merck 的原因：
  - 肿瘤行里只有 Pfizer 的 target_profile 同时写了「靶向小分子」和「泌尿」。Merck、BMS、J&J、AZ、Roche 的肿瘤行只写肺、乳腺、消化道、妇科或血液肿瘤。
  - Pfizer 的 Xtandi（enzalutamide）美国 LOE 为 2027（MNC-WB）。MRT-2359 的 1/2 期数据就是与 enzalutamide 联用得到的。
- 分数：buyer_fit 4（中）、stage_match 4（中高）、clinical 2（高）。catalyst 和 dealability 由 build 从 [event] 和 [rights] 推导。
- [event]：MODeFIRe-1 2 期数据更新，importance = medium，certainty = estimated，timing = 2027-10。公司只说「Ph 2 update in 2027」（MAN-GLUE-3），只有年份，不够「明确披露」的标准，所以时间用 CT.gov 的预计主要完成日期。另一项事件「2026 年底更新 1/2 期 enzalutamide 联用组」是明确披露的，但重要性为低，只写进事件文本。
- 组合冲突：10-K 竞争段把 Pfizer 列为适应症竞争者，但没有写同机制（GSPT1 降解剂）产品。结论：未核查组合冲突。Pfizer 自有的 mCRPC 联用项目没有逐一核查。

## 权益状态：full

10-K（MAN-GLUE-1）原句：

> "We currently retain exclusive worldwide rights to the programs shown in Figure 1 below, except for MGDs directed against VAV1 including MRT-6160, which we licensed to Novartis in October 2024, and the targets included in the Roche and Novartis relationships."

（原文在 "exclusive" 与 "worldwide" 之间有分页符。）GSPT1 专利列在「Wholly Owned Product Candidates」下，最早到期年份为 2040。10-K 和 10-Q 的合作协议段都没有 MRT-2359 的引进许可或对外授权。无借款，最新 10-Q 资产负债表上没有借款科目。

10-Q（SEC-0001193125-26-336711）现金跑道原句："We anticipate that our existing cash and cash equivalents and marketable securities support our cash runway into 2029."

整体收购时公司层面要一并承接的负担：
- Novartis 持有 MRT-6160 的全球权益。美国市场按 30% 分担损益，公司还要为 3 期共同出资。
- Novartis 持有两个免疫项目的期权。
- Roche 合作持续到 2028 年 10 月。

## 待核实

1. Figure 1 管线图没有出现在 10-K 文本抽取中，所以没有直接看到 MRT-2359 在图上。
2. Roche 合作的靶点清单没有公开。GSPT1 不在其中，这一点只能从「Wholly Owned」的归类推断。
3. J&J 的 apalutamide 临床供药协议只出现在 8-K 新闻稿（MAN-GLUE-2）中，条款未披露，10-Q 没有提及。协议中是否有期权或优先谈判权，待核实。
4. MODeFIRe-1 首例给药（计划在 2026 年第 3 季度）在已读文件中没有确认。
5. 第 6 例 AR 突变患者的数据没有公布。8-K 说该组共入组 6 例，10-K 的数据截点只有 5 例。
6. AR 野生型和 AR-V7 亚组的应答数据只在图表里，没有抽取。
7. Xtandi 的 LOE（2027）来自对方材料 MNC-WB，标注为「第三方引 10-K」，没有用 Pfizer 原始文件核对。
8. Pfizer 自有的 mCRPC 管线（组合冲突）没有核查。

## pack 的问题

- NCT05546268 是产生 mCRPC 数据的 1/2 期试验（MRT-2359 联用 enzalutamide），但 pack 只把它映射到「NSCLC」。CRPC 一行只挂了 MODeFIRe-1（NCT07745361）。
- MRT-8102（NEK7，ASCVD、痛风、化脓性汗腺炎）的 therapeutic_area 为 null，所以不进自动配对。它是公司当前的重点资产：GFORCE-1 随机 1 期结果阳性，GFORCE-2 2b 期计划在 2026 年下半年启动。它可作为第二候选，对应 Novo Nordisk #3 或 Novartis #1 的「代谢炎症 / 动脉粥样硬化」。但它处于 1 期，与这两个买方要求的「Phase 2-3」差一个阶段，证据也只有生物标志物。本稿没有选它。
- MRT-6160（VAV1）已全球授权给 Novartis，不在 pack 中，这样处理是正确的。

## 其他

- 预览构建：`preview_build.py` 失败，原因是其他公司草稿的来源未登记（ALT、CGON、CMPX）。这可能与其他 agent 同时写同一个 preview_build 目录有关。我改用 `intel.scoring.review.parse` 单独解析 GLUE.toml，解析通过，program 和 indication 都能匹配 pack。
- 用时：约 35 分钟。
