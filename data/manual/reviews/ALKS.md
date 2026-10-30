# ALKS 复核报告（草稿，待人工签核）

## 推荐组合

- 资产 / 适应症：alixorexton（ALKS 2680，口服选择性 OX2R 激动剂）/ 1 型发作性睡病（NT1）。TOML 中 `program = "ALKS 2680"`，`indication = "Narcolepsy Type 1"`，build 取最高阶段行（3 期，Brilliance NT1）。
- 买方：AbbVie 第 2 治疗领域偏好（神经科学，Phase 2b-3），交易形式「收购」。
- 理由：10 家买方的画像都没有点名发作性睡病、嗜睡症、orexin 或睡眠。AbbVie 匹配度最高：治疗领域行写「可形成新神经平台的资产」，技术类型行写「口服中枢小分子，Phase 2b-3，有明确认知/情绪疗效」。alixorexton 是每日一次的口服中枢小分子，Vibrance-1 的认知量表（BC-CCI）有改善（探索性终点）。公司正把 OX2R 激动剂扩展到 ADHD、MS / 帕金森病相关疲劳（MAN-ALKS-6），可以算作平台。备选买方：Roche #2（技术类型行「覆盖新神经适应症」，但治疗领域画像是 MS / AD / 神经炎症）；J&J #3（「新机制药物」，但适应症是抑郁、精神分裂症、神经退行性疾病）。两者都比 AbbVie 弱。
- 买方 LOE：AbbVie 的 LOE 产品（Humira、Imbruvica、Venclexta、Skyrizi）都不在睡眠 / 神经领域，所以不能走 LOE 路径给 4 分。
- 分数：buyer_fit 3（中）、stage_match 4（高）、clinical 3（中高）。catalyst 由 [event] 推导（高 + 估算 → 3）。dealability 由 [rights]=full 与 EV 档推导：EV ≈ 75.91 亿市值 + 15.25 亿债务 − 6.91 亿现金 ≈ 84.2 亿美元，属 50–150 亿档 → 2。

## 资产权益：full（推断，中高）

- 10-K（FY2025）「Collaborative Arrangements」只列两项：Janssen（NANOCRYSTAL 技术，用于 INVEGA 产品）与 Biogen（VUMERITY）。两项都是 Alkermes 对外许可，与 alixorexton 无关。该段引语有保留："including the arrangements described below"。
- 10-K 专利段原文："We have U.S. patent protection that extends to 2041, several U.S. patent applications, and a number of corresponding non-U.S. counterparts that cover alixorexton."
- 10-K 和 10-Q 都没有逐字写「wholly owned」或「worldwide rights」。在 alixorexton 段落前后 ±1500 字符内搜索 licensor / royalty / milestone / option，命中项都与 LUMRYZ（Jazz 和解协议）或 Janssen 有关，没有一项与 alixorexton 有关。
- 未发现 alixorexton 有引进许可或对许可方负有里程碑 / 特许权使用费义务。泛称句 "We have exclusive rights through licensing agreements with third parties to issued U.S. patents" 未指明产品。签核时请人工确认。
- 债务：Avadel 收购时全额借入定期贷款 A/B，原文："borrowed the full $ 1.525 billion available under the Facilities"。TLA 2031-02-12 到期，TLB 2031-08-12 到期。
- 资金：公司已有盈利，无融资压力。10-Q 原文："We expect that our existing cash, cash equivalents and investments will be sufficient to finance our anticipated working capital and other cash requirements, including debt service and capital expenditures, for at least the twelve months"。

## 下一事件

- 选用：Brilliance NT1 3 期主要终点完成。CT.gov 预计 NCT07455383 为 2027-05，NCT07540897 为 2027-06；公司没有披露读出季度，所以确定性为「估算」。
- 更近的次要事件：Vibrance-3（特发性嗜睡症 IH，2 期）顶线结果。Q2 新闻稿原文："topline results from our alixorexton phase 2 idiopathic hypersomnia study expected toward year-end"（MAN-ALKS-4）。"toward year-end" 不是季度或半年的表述，所以不标「明确披露」。重要性为中，按估算计 2 分，低于 Brilliance。

## 待核实

1. 组合冲突：AbbVie 是否已有 OX2R 激动剂或发作性睡病资产（未打开 AbbVie 文件）。
2. alixorexton 是否为自主发现、是否有第三方引进许可：文件没有逐字写全资。
3. Brilliance 3 期读出的季度 / 半年：公司文件没有给出。
4. Vibrance-1 / Vibrance-2 的同行评议全文没有打开，只用了公司新闻稿。
5. 2026 年第 3 季度 10-Q 尚未在 EDGAR 列出（截至 2026-10-30）。财务与权益依据 2026-06-30 的 10-Q。

## 包数据问题

- 资产名：包里没有通用名「alixorexton」，只有代号。派生名 "ALKS 2680 1 (ALKS 2680 2, ALKS 2680 3)" 是乱码（成因未查），应合并到 "ALKS 2680"。
- 阶段：NT1 行同时有 phase2_3（id 375，NCT06767683 长期扩展研究）和 phase3（id 377）两行。阶段 3 期与 10-Q 一致。
- 治疗领域：IH 行（id 374）的 therapeutic_area 为空，应为 neuroscience。
- 自动主组合选中 LYBALVI（已上市）/ J&J #3。改选理由：LYBALVI 已上市，与「Phase 2b-3」偏好不符，而且不是可推荐的新资产。
- 包缺失 ALKS 7290（OX2R 激动剂，ADHD）的最新进展：1b 期阳性，2 期数据预计 2027 年（MAN-ALKS-6）。可作为平台论据，但不是主推荐资产。

## 用时

约 30 分钟。
