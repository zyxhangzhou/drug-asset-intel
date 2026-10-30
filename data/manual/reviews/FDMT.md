# FDMT（4D Molecular Therapeutics）复核草稿报告

## 结论

- 组合：4D-710 / Cystic Fibrosis（数据包适应症 "Cystic Fibrosis Lung"）/ AstraZeneca #2（罕见病）。交易形式：许可。
- 分数：buyer_fit 4（中）、stage_match 4（高）、clinical 2（中高）；catalyst 由 [event] 推出 2（中重要性、估算）；dealability 由 [rights] full + EV 约 3.03 亿美元推出 4。本地预览构建通过（主推荐行 4/4/2/2/4）。
- 重要提示：公司真正的主导资产是眼科 4D-150（湿性 AMD 两项 3 期、DME 3 期已启动）。买方偏好图（`buyer_preference_map.csv`）中没有眼科治疗领域，4D-150 在任何可选买方下 buyer_fit 最高只能 1–2 分，写不出 §7 第一句。所以改推第二资产 4D-710。是否扩充偏好图以覆盖眼科，需要人工决定。

## 为什么选 AstraZeneca #2

- 画像原文「基因疗法、体内细胞疗法、补体/酶替代和遗传性疾病药物」同时点名了技术类型和疾病类别。4D-710 是 AAV 基因疗法，CF 是遗传病（10-Q："an inherited disorder"；"orphan drug designation in the United States for 4D-710"）。
- 理想阶段「早期平台至Phase 3」；4D-710 "is currently in Phase 2 development"（10-Q）→ 4 分。
- 10-Q 竞争段落列出的大药企不含 AstraZeneca；10-K 称最直接竞争者为 Vertex。未做完整组合冲突核查。
- 自动配对的其他买方被放弃：AbbVie #1（IL-13/TSLP/IL-23/TL1A 抗体，且 AbbVie 在 10-Q 竞争名单中）、Novartis #2（过敏/哮喘抗体或免疫调节剂）、GSK #3（哮喘/COPD 抗体、HBV、MASH）、Merck #3（PCSK9、PAH、COPD，理想阶段上市或 3 期）——画像均未提到基因疗法或 CF。
- 数据包把 4D-710 标为 respiratory，与 AZ #2 的 ta_codes（rare_genetic）不相交；构建只校验买方+排序存在，已通过。

## 权益状态（4D-710：full）

10-Q（SEC-0001193125-26-349173）原句：
> "To date, the Company has not developed a commercial product in connection with the CFF Agreement, and it has not licensed, sold or otherwise transferred to another party the product developed under the CFF Agreement or the underlying technology."

附带义务（不改变 full，但影响交易经济性）：
- CFF：首次商业销售后付 "six times the actual award received"；对许可/出售收入付 "royalties of a mid-single digit percentage"；"In the event of a change of control of the Company, CFF will receive certain payments"；停止开发 180 天则须授予 CFF 条件性 "interruption license"；2025-10 成立的 CFF Joint Steering Committee 判断为资助方治理，非共同开发（推断，中）。
- A101 载体为 UC Regents 引进许可（10-K："We have also licensed ... relating to our targeted and evolved vector, A101, which is used in 4D-710"）：低个位数销售分成，转授权对价 "in the mid-teens to the mid-twenties-range"——对许可方案直接相关。
- 债务：Hercules 贷款 "$20.0 million was funded at closing"（与数据包 total_debt 1958.7 万美元一致），"secured by a security interest in substantially all of our assets, including our intellectual property"，限制 "merge with other companies or consummate certain changes of control"。
- 对比 4D-150：partial。Otsuka 持有 "Japan, Korea, China, Australia, and certain other Asia-Pacific markets"，公司 "retains full development and commercialization rights for 4D-150 outside the Otsuka Territory, including the United States, Latin America, and Europe"。

## 资金

- 数据包 runway 18.7 个月；公司指引（MAN-FDMT-2）："sufficient to fund our operating expenses and capital expenditure requirements at least into the second half of 2028"（含 Otsuka 预期付款）。

## 待核实

1. AEROW 1 期各剂量组 ppFEV1、LCI2.5、CFQ-R 的具体数值与例数（10-K 只有定性描述；需 2025-12 新闻稿或会议摘要）。
2. 2026 Q4 "AEROW Phase 1/2 clinical trial and program update" 是否包含 2 期数据；2 期读出的公司披露时间（目前只有 CT.gov 估算 2027-06）。
3. 2026-10-21 Investor Day 材料（EDGAR 上没有对应 8-K，未打开）。
4. AstraZeneca 是否已有 CF 或吸入基因疗法资产（未核查组合冲突）。
5. CFF 控制权变更付款的金额区间（10-Q 只说 "certain payments, depending on the timing of the change of control and the size of the transaction"）。

## 数据包问题

- "EYELEA" 被识别成一个程序（应为对照药 aflibercept/EYLEA，且拼写错误），来源 NCT07867080 实为 4D-150 DME 3 期。
- 4D-110（无脉络膜症）、4D-125（XLRP）、4D-310（Fabry）在 10-K / 10-Q 中均未出现；10-K："strategic pipeline prioritization to focus on the development of 4D-150 and 4D-710"（2025-07）。这些 CT.gov 条目应视为已停止/不再推进的项目，4D-310 的 rare_genetic 标签不应产生配对。
- 4D-150 DME 3 期（4SIGHT）已于 2026-09-28 宣布入组首批患者（MAN-FDMT-3）；数据包同一适应症另有一条 "phase2" 记录（NCT05930561，是否即 SPECTRA 未核实）。
- 4D-710 治疗领域标为 respiratory，未加 rare_genetic。

## 用时

约 30 分钟。
