# VIR（Vir Biotechnology）复核草稿报告

## 选定组合

- 资产：VIR-3434 (TOBEVIBART)，实际推荐的是 tobevibart + elebsiran 联合方案，用于慢性丁型肝炎（CHD）。
- 适应症：pack 中的 "Viral Hepatitis"（这一行下挂 ECLIPSE 1/2/3 三个试验）。
- 买方：Merck & Co. 第 2 偏好（抗感染与长效抗病毒，ideal_stage Phase 2-3）。
- 交易形式：许可（美国及 Norgine / Brii 区域以外的市场）。理由：权益为 partial；10-K 写明公司考虑合作商业化："we will also consider collaborating with one or more biopharmaceutical companies to enhance our commercial capabilities going forward, as we have with the exclusive license granted to Norgine."（MAN-VIR-1）。不选「收购」的原因：公司另有肿瘤业务（VIR-5500 已与 Astellas 共同开发，另与 Gilead 签了 PRO-XTEN 合作），并且 Alnylam、IRB、Rockefeller 都分享转授权收入。签核人可改为「收购」；partial 与收购兼容。

为什么选 Merck #2：画像写的是「长效预防或治疗性抗病毒…能减少给药频率」。可以对上的资产属性有两个来源：tobevibart 含 Xtend Fc 半衰期延长技术（10-K），联合方案每月皮下注射一次（Q2 新闻稿）。

考虑过但没选的买方（每行都读了 target_profile）：
- GSK #3（呼吸/免疫及肝病）：「HBV功能性治愈、MASH和肝病核酸药物」。字面上对得上 elebsiran（HBV siRNA）。但 pack 中要推荐的 program 是抗体；适应症是 CHD，不是 HBV 功能性治愈（10-K："Vir Bio decided not to pursue Phase 3 development of combinations of tobevibart, and elebsiran in CHB"）；映射表 ta_codes 也不含 infectious。这是次优选择。
- GSK #2（HIV与抗感染）：画像以长效 HIV、整合酶抑制剂为主，对应弱。
- Pfizer #3（疫苗、抗感染与ATTR）：画像重点是成人疫苗、呼吸道感染，ideal_stage 为「上市或Phase 3」，对应弱。
- Novo #2、Roche #3：画像是 MASH / 代谢，不相关。

分数：buyer_fit 3，stage_match 4，clinical 2。catalyst 和 dealability 由 build 推导（事件 high + disclosed；权益 partial，可交易性最高 3）。

## 权益状态：partial

10-K 原句（MAN-VIR-1）：
- "Norgine holds exclusive license for the commercial rights to the combination of tobevibart and elebsiran in Europe, Australia and New Zealand"
- "Brii Bioscience retains rights to the combination of tobevibart and elebsiran in the Greater China Territory (People’s Republic of China, Hong Kong, Taiwan and Macau)"
- Norgine 协议："we granted Norgine an exclusive license for the commercial rights to the combination of tobevibart and elebsiran for the treatment of CHD in Europe, Australia, and New Zealand (collectively, the Norgine Territory), while we will retain commercial rights for the combination in the United States and all other international markets outside of the Greater China Territory."
  - 条款：已收 €5,500 万；里程碑最高再收 €4.95 亿；区域内提成 mid-teen 到 high-twenties；Norgine 承担 ECLIPSE 约 25% 的外部费用。
- Brii 行使选择权的时间：elebsiran 2020-06-12，tobevibart 2022-07。

各成分归属：
- elebsiran：从 Alnylam 引进（全球独占许可，覆盖 HBV / HDV）。Alnylam 于 2025-03 选择不参与利润分成。Vir 仍需支付：开发 / 监管里程碑最高 1.45 亿美元、销售里程碑最高 2.5 亿美元、low double-digits 到 mid-teens 的提成，并分享转授权收入。
- tobevibart：自研（"identified using our proprietary antibody discovery platform"），使用三项许可技术：
  - Xencor Xtend：非独占许可，HBV 项目里程碑最高 7,780 万美元，提成为低至中个位数。
  - Rockefeller：年费 100 万美元；6 个产品合计里程碑最高 8,030 万美元；提成为低个位数；分享转授权收入。
  - IRB：提成为低个位数；转授权收入的 sub-teen 百分比。

判断说明：判为 partial，不判 restricted。Norgine 有 "certain development rights"，且双方设有联合委员会，但都只限 Norgine 区域；美国权益在 Vir 手中。10-Q 对保留区域的写法（"outside of the People’s Republic of China and Taiwan"）与 10-K（"outside of the Greater China Territory"）不完全一致。需要签核人确认。

## 资金跑道：pack 的 665 个月是错的

- pack 值的算法：H1 2026 经营现金流 −906 万美元，按 6 个月年化。
- 10-Q 说明这段现金流被一次性收入拉低："Cash used in operating activities during the six months ended June 30, 2026 decreased compared to the same period in 2025 primarily due to $240.0 million upfront payment received under the Astellas Collaboration Agreement, partially offset by a $48.0 million payment to Sanofi"（SEC-0001628280-26-053549）。
- 参考数：2025 年 H1 经营现金流 −1.983 亿美元（10-Q）；FY2025 −3.918 亿美元（10-K）。
- 公司自己的指引："expects its cash, cash equivalents and investments to fund operations into the second half of 2028"（MAN-VIR-2）。
- 建议：资金提示改用公司指引，或在计算中扣除一次性的预付款。管道应识别这类一次性流入。我没有自行估算替代月数。

## pack 问题

1. 适应症标签 "Viral Hepatitis" 是 CT.gov 汇总标签。真实适应症是慢性丁型肝炎（CHD）。
2. 联合方案被拆成两个 program：
   - TOBEVIBART 的 "Viral Hepatitis" 行（3 期，含 ECLIPSE 试验）。
   - ELEBSIRAN 的 "Viral Hepatitis" 行（3 期，无试验）。
   - 两者的 "Hepatitis D, Chronic" 行仍标 2 期（SOLSTICE），已过时。
3. "BULEVIRTIDE"、"NRTI"、"TDF"、"PEG-IFNα" 是对照药或背景用药，不是 Vir 的资产。
4. ECLIPSE 3（NCT07142811）在 pack 中标为 phase2。公司称其为 "Phase 2b head-to-head trial"，二者一致；它不是 3 期。
5. 肿瘤 TCE 的阶段：
   - 10-K 写 VIR-5818 为 Phase 1。pack 为 phase1_2，来自 CT.gov 登记，可接受。
   - VIR-5500（与 Astellas 合作）不在 pack 中。

## 待核实

1. Merck 是否已有 HDV / HBV 同机制资产（未核查组合冲突）。
2. 相对标准治疗的给药频率比较来源：bulevirtide 在美国未获批，没有在允许的来源里查。查到后 buyer_fit 可升 4 分。
3. Norgine 的 "certain development rights" 加联合委员会，是否应算作共同开发（即 restricted）。
4. Norgine / Brii 协议的控制权变更条款：已读的 10-K / 10-Q 正文未提到。
5. Gates 全球可及承诺是否覆盖 tobevibart：10-K 只说覆盖 vaccinal antibody 项目，未见 tobevibart。
6. SOLSTICE 第 96 周数据（88%）只来自公司新闻稿，未见同行评审版本。
7. NEJM 原文只读了 PubMed 摘要，未读全文。

## 用时

约 35 分钟。
