# PTCT 复核草稿报告

## 选定组合

Sephience（sepiapterin，pack 程序名 `PTC923 (SEPIAPTERIN, CNSA-001)`）/ Phenylketonuria / AstraZeneca #2（罕见病），交易形式：收购。

理由：
- Sephience 是 PTC 的核心收入资产。2026 年第三季度单季净销售 1.819 亿美元（MAN-PTCT-2："During the three months ended September 30, 2026, we recognized $181.9 million in net sales of Sephience."）。
- AZ #2 画像含「遗传性疾病药物」。PKU 是遗传性代谢病（MAN-PTCT-1："a rare, inherited metabolic disease"）。画像没有点名 PKU 或 PAH 机制，AZ 三条技术类型偏好也都不对应。按 §3.1，buyer_fit 给 2（只符合治疗领域）。
- 请签核人判断：如果把「遗传性疾病药物」视为具体需求条目，可改为 4（竞争段未见 AZ 冲突）。本草稿未这样处理，因为这个短语就是 rare_genetic 标签的来源。
- 10-K 竞争段只列出 Kuvan、Palynziq 及 Otsuka、SOM Biotech、Maze、Agios 的在研药。没有 AstraZeneca 产品。其他来源未核查。
- 没有选 pack 的自动主组合（vatiquinone / FA / AbbVie #2），原因：
  - MOVE-FA "did not meet its primary endpoint"。
  - 2025 年 8 月 NDA 收到 CRL（"substantial evidence of efficacy was not demonstrated"）。
  - 新研究 PROVE-FA 于 2026 年第三季度启动，主要终点为第 24 个月 mFARS。读出几乎肯定落在 24 个月窗口外。
  - AbbVie 画像没有点名 FA。
- PTC844 / RA 也没有选：Phase 2a 刚启动，只是 PK/PD 研究，公司称适应症尚未确定（"help inform the ultimate target indications for PTC844"）。

分数：
- buyer_fit：2
- stage_match：2（已上市，对应「早期平台至Phase 3」，按 §3.2 示例给 2）
- clinical：4（APHENITY 是安慰剂对照 RCT；AMPLIPHY 是对标准治疗 sapropterin 的随机交叉直接对比，结果为优效；血 Phe 是注册终点）
- [event]：不写。24 个月窗口内，公司没有披露 Sephience 的关键读出或监管决定，所以 catalyst 预计为 0。

## 权益状态

`full`，推断，置信度中高。10-K 原句："We do not license any material patent rights relating to sepiapterin to unaffiliated parties."（MAN-PTCT-1）

引进资产与付款义务：
- Shiratori 制造工艺许可，原文："a low single digit percentage of annual net sales of the Sepiapterin Products"。
- Censa 销售里程碑：第三季度新触发 5,000 万美元。另有 "other contingent payments"（MAN-PTCT-2）。

公司层面：
- 债务：2031 年到期 0% 可转债，共 5.5 亿美元（MAN-PTCT-2）。
- 资金：10-Q 写明 "will be sufficient to fund its operations for at least the next twelve months"。8-K 写明 "on track to achieve our cash flow breakeven milestone this year"（MAN-PTCT-3）。
- Royalty Pharma 特许权融资按债务入账，2026-09-30 余额约 23.06 亿美元（"these fundings should be classified as debt"）。PTC 已出售 Evrysdi 特许权 100% 的权益，收购方拿不到这部分现金流。pack 的 total_debt（5.91 亿美元）没有包含这笔负债，因此 EV 被低估。
- votoplam 由 Novartis 负责全球开发与商业化，PTC 保留 "a 40% share of U.S. profits and losses"。votoplam 在受限状态。

## 待核实

1. 窗口内 Sephience 的关键事件。8-K 只给出 2026–2027 年的地域上市扩张，没有给出具体监管日期。NCT06302348（3 期）的预计完成日是 2031-02，在窗口外。
2. 区域权益已部分核实。10-Q 写明公司在 "the United States, the EEA, Latin America, Japan and other territories" 自行商业化。10-K 所述第三方只是经销商（"act as intermediaries"）。剩余待核实：个别小市场的经销协议有没有含许可条款。
3. AstraZeneca 的 PKU 或代谢罕见病管线（组合冲突）。本次只看了 PTC 10-K 竞争段。
4. 长期认知与生活质量获益。目前只有公司演示材料引用 Genet Med 2026（MAN-PTCT-4），原文未读。
5. Censa 剩余或有付款的金额上限。10-Q 只写 "other contingent payments"。

## Pack 问题

- votoplam（PTC518）/ 亨廷顿病不在 pack 中。即使补入，Novartis 持有全球开发与商业化权，加上 40% 美国损益分成，权益为 restricted。
- ST-920（isaralgagene civaparvovec，Fabry 病 AAV 基因疗法）不在 pack 中。PTC 于 2026 年 9 月从 Sangamo 收购，"BLA submission expected to be completed in Q4 2026"（MAN-PTCT-3）。它与 AZ #2 画像中的「基因疗法……遗传性疾病药物」最贴合，而且窗口内有高重要性、已明确披露的事件。建议 pack 补入后改选它，或作为备选组合复核。
- PTC612（口服 NLRP3 抑制剂，1 期）不在 pack 中。
- ELADOCAGENE EXUPARVOVEC 的 stage 为 phase2。实际上已上市：Upstaza（欧洲经济区和英国）、Kebilidi（美国）（MAN-PTCT-1："This gene therapy is approved"）。
- Vatiquinone FA 被拆成两行："Friedreich Ataxia" 和 "Friedreich's Ataxia"。
- Eladocagene AADC Deficiency 行的 therapeutic_area 为空。

## 其他

- 引号校验 `check_quotes.py PTCT`：25 条，缺失 0。
- `preview_build.py PTCT` 因 sqlite "disk I/O error" 失败。原因可能是并发写入同一预览库，未能验证 build。
- 用时约 35 分钟。
