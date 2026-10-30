# CMPX 复核草稿报告

## 选定组合
- 资产 / 适应症：tovecimig（pack 中名为 CTX-009）/ Biliary Tract Cancer（二线）。
- 买方：Merck & Co. #1（肿瘤/血液肿瘤，ideal_stage Phase 2b-注册期）。
- 原因：画像写「能在KEYTRUDA单药/联用之外形成新标准治疗的…胃肠癌」。10-K 写明 BTC 是胃肠道肿瘤，Keytruda 已获批一线 BTC，二线没有公认标准治疗。10-K 竞争段中 Merck 只有 Keytruda（PD-1），不是同机制。
- 备选：BMS #1（画像写「消化道癌的双抗」，与模态更贴）。没有选它，因为 buyers.json 证据列中 BMS 正推进 VEGF 相关双抗 pumitamig，可能部分机制重叠；该机制未在本次打开的文件中核实。
- 交易形式：收购（权益为 partial，与收购兼容）。

## 评分
- buyer_fit 4（中）；stage_match 4（中高）；clinical 3（中，ORR 替代终点封顶 3；ITT OS HR=1.05，FDA 要求生存试验，复核人可降为 2）。
- event：BLA 提交，importance high / certainty estimated，时间未披露 → 构建将给 catalyst 3。

## 权益
- 状态：partial。10-K 原文："We have licensed exclusive global rights to tovecimig, outside of South Korea, from ABL Bio"；"South Korean rights are held by Handok Pharmaceuticals, Inc. (“Handok”) and China rights were out-licensed to Elpiscience Biopharmaceuticals Co., Limited (“Elpiscience”)."
- 引进义务（ABL Bio）：肿瘤领域至多 9,600 万美元开发/监管里程碑、3.03 亿美元商业里程碑、单位数分级特许权使用费。
- 协议有 "jointly develop" 字样，但分工是 ABL Bio 负责到 1 期、公司负责 2 期起；未见选择权、ROFN、共同商业化。复核人确认是否维持 partial。
- 债务：10-Q 负债只有应付、应计、租赁（总负债 2,412 万美元），无借款。资金指引（10-Q）："the Company expects such cash resources will fund operating expenses and capital expenditure requirements into 2028"。

## 重大事项
- 2026-09-22 8-K：FDA 建议先做证明生存获益的试验再提交 BLA。公司表示不认为需要新试验，继续准备 BLA，但没给时间。
- 公司 7 月路演材料曾写 "potential approval in 2H 2027"、"BLA filing initiating in late 2026"，已被 9 月公告取代，未引用。
- 事件确定性存疑：如果公司接受 FDA 建议，24 个月窗口内可能没有高重要性事件，catalyst 应降为 0 或 1。请复核人决定是否覆盖。
- 建议：可写出论点，但 FDA 反馈使注册路径不确定；是否入选请人工判断。

## 待核实
1. Elpiscience 中国授权的经济条款（10-K 正文未写）。
2. ESMO 2026 口头报告全文 / 摘要（含 DoR），未找到可打开的来源；公司 IR 页面返回 403。
3. 9 月 22 日之后公司是否与 FDA 再次沟通或给出 BLA 时间（EDGAR 上 10 月无 8-K）。
4. Merck 早期管线中是否有 DLL4 / VEGF 双抗（组合冲突只查了 10-K 竞争段）。
5. PFS2 p 值不一致：4 月新闻稿 p=0.0016，7 月路演 p=0.065；本草稿未引用 PFS2。

## Pack 问题
- 资产名：pack 用旧名 CTX-009，公司现名 tovecimig。
- 阶段：phase2_3 正确，但 FDA 已表示该研究不足以支撑 BLA。
- 自动事件 "NCT05506943 主要终点数据（估算）2027-08-31" 已过时：主要终点 2025 年已读出，终版分析 2026 年 4 月已公布。
- total_debt 为空正确（无借款）。

## 用时
约 25 分钟。
