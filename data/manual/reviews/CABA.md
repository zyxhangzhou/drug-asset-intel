# CABA（Cabaletta Bio）复核草稿报告

## 推荐组合

- 资产 / 适应症：CABA-201（现名 rese-cel，全人源 CD19-CAR T）/ Systemic Sclerosis。1/2 期已完成，单臂注册研究（约 25 例 SSc-ILD，52 周 FVC 终点）计划 2026 年第四季度启动（SEC-0001759138-26-000039）。
- 买方：Bristol Myers Squibb，治疗领域偏好第 2（免疫炎症，ideal_stage「Phase 1b-3」）。
- 交易形式：合作（权益为 restricted，收购不兼容）。
- 分数：buyer_fit 3（中）、stage_match 4（中高）、clinical 2（中高）；catalyst 与 dealability 由 build 从 [event] / [rights] 推导（预计 catalyst 3 = 高 + 估算；dealability 受 restricted 限制最高 1）。

选择理由：

- BMS #2 画像点名「免疫重置」「风湿病」。公司原文：\"designed to reset the immune system in patients living with autoimmune diseases\"（MAN-CABA-2）。SSc 为风湿病。
- buyer_fit 不给 4：10-K 竞争段把 BMS 列入已上市 CAR T 公司，并说其中「一部分」已宣布自身免疫 CD19 疗法（含 SSc），没有点名。组合冲突无法排除。
- 没有选 BMS #3（细胞治疗及自身免疫重编程）：该行画像强调「可重复给药或可在体内…重编程」，rese-cel 是自体、单次输注；ideal_stage 只到 Phase 2，SSc 已进入注册阶段。
- 没有选自动初筛的 Novartis #3 / RMS：RESET-MS（NCT07006805）在 CT.gov 为 WITHDRAWN，Novartis #3 画像（神经退行性遗传药物、放射性配体、ADC）也不对应 CAR-T。
- 最佳适应症其实是肌炎（DM/ASyS 注册队列，BLA 计划 2H27），但 pack 中没有这一条（见 Pack 问题），因此按简报选 pack 内最接近的 SSc，事件用同一资产的肌炎顶线并写明适应症。

## 资产权益

- 状态：restricted（按简报规则「他方持有 ROFN 即受限」）。范围很窄，复核人可能改判为 full 或 partial。
- 10-K 原句：\"IASO has the right of first negotiation if we desire to grant a third party an exclusive license to develop, manufacture, commercialize or otherwise exploit the licensed products in the Greater China region.\"（MAN-CABA-1；10-Q Note 同句，SEC-0001759138-26-000039）
- 全球许可原句：\"we received an exclusive, worldwide license under certain IASO intellectual property to use a novel clinical-stage anti-CD19 binder\"（MAN-CABA-1）。未见任何区域对外授权、选择权或共同开发。
- 引进义务：IASO 总对价最高 1.62 亿美元 + 分档中个位数特许权使用费 + 再许可收入的低两位数比例；IASO 控制许可专利的维护；双方互有竞业限制。Penn/CHOP 里程碑合计约 2,100 万美元 + 低个位数特许权使用费。
- 先例对照：OLMA（买方对资产任何区域交易持 ROFN）判 restricted；BHVN（ROFN 只涉及后续化合物）判 partial。本例 ROFN 涉及资产本身但只限大中华区独家再许可，处于两者之间。

## 资金

- Q2 新闻稿现金指引："will enable it to fund its operating plan into mid-2027"（MAN-CABA-2）；10-Q 持续经营："we have concluded that substantial doubt exists about the Company’s ability to continue as a going concern"（SEC-0001759138-26-000039）。距快照约 8 个月，低于 pack 的 16.1 个月。
- 9 月 8-K：7 月 1 日至 9 月 12 日认股权证行权 46,011,900 份，募资约 1.15 亿美元（MAN-CABA-3）。pack 的现金、股本（169,545,445 股，截至 2026-08-07）与市值都早于这笔行权，EV 偏低。未重算。
- pack total_debt 为空，但 10-Q 有 Lonza 嵌入式融资租赁负债 15,238 + 4,738 千美元（约 2,000 万美元）。

## 待核实

1. 权益判定：IASO 大中华区 ROFN 是否应按 restricted 处理（见上）。改判会影响 deal_form（可改回收购）与入选资格。
2. 组合冲突：BMS 是否已有自身免疫 CD19 CAR-T 用于 SSc。10-K 只说 "A subset of these companies"，未点名；未打开 BMS 文件核查。
3. SSc 注册研究是否已于 2026 年第四季度启动：截至 2026-09-14 的 8-K 未见公告；Q3 10-Q 尚未提交。
4. SSc 临床数据来自 10-Q / 新闻稿对 EULAR 2026 的摘要，未打开会议摘要原文或同行评议文献。
5. 肌炎顶线只给 "mid-2027"，按估算处理；是否算明确披露需人工决定。
6. EV 与资金：需用行权后股本与现金重算 EV（MAN-CABA-3）。
7. IASO 为中国公司，10-Q 提及 BIOSECURE 法案风险，未评估对许可的影响。

## Pack 问题

- 肌炎缺失：CT.gov 缓存（data/raw/ctgov/CABA.json）含 RESET-Myositis NCT06154252（含 "Dermatomyositis"），但 pack 的派生项目中没有肌炎这一条。它是公司首个注册队列与 BLA 适应症，应补入。
- 资产名：CABA-201 已更名 resecabtagene autoleucel（rese-cel）：\"Resecabtagene autoleucel (rese-cel), formerly referred to as CABA-201\"（SEC-0001759138-26-000039）。
- 自动主组合用的是 RMS，但 NCT07006805 为 WITHDRAWN。
- SSc 阶段 phase2_3 来自 CT.gov；公司披露为 1/2 期完成、注册研究待启动。
- Pemphigus Vulgaris 同时挂在 CABA-201 与 DSG3-CAART 下（同一试验 NCT04422912）。
- 财务：total_debt 空（实有融资租赁负债）；runway 16.1 个月与公司指引（到 2027 年年中）不一致；现金与股本早于 9 月行权。

## 用时

约 30 分钟。
