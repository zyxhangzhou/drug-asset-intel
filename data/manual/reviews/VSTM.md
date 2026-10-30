# VSTM（Verastem）复核草稿报告

## 选定组合

- 资产 / 适应症：VS-7375（口服 KRAS G12D ON/OFF 抑制剂）/ Pancreatic Ductal Adenocarcinoma (PDAC)，pack 中 phase2 行（NCT07644559，TARGET-D 201）。
- 买方：Merck & Co. #1（肿瘤/血液肿瘤，理想阶段 Phase 2b-注册期）。交易形式：收购。
- 理由：Merck 画像“能在KEYTRUDA单药/联用之外形成新标准治疗的……胃肠癌……资产”。G12D 尚无获批药物。1L mPDAC 3 期含无化疗组（VS-7375 + anti-EGFR）。Keytruda 2028 LOE。10-K 的 G12D / pan-KRAS 竞争者名单不含 Merck。
- 排除：Roche 画像点名 KRAS，但 10-K 竞争者名单含 Genentech 和 AstraZeneca（同机制）。BMS #1 为备选。
- 覆盖自动初筛：自动配对选的是 avutometinib（LGSOC，已上市，AbbVie #3）。该产品已于 2025-05-08 获批，且 Chugai 持有欧盟 / 日本 / 台湾的 opt-back 权利（10-K："Chugai also obtained opt back rights"，并称无意行使）。VS-7375 是公司估值核心，所以改选它。

## 分数

- buyer_fit 4（中）；stage_match 4（高）；clinical 3（中，单臂 + 跨试验，封顶 3）。
- event：TARGET-D 201 2L PDAC 初步数据，2027Q2，medium，disclosed（→ catalyst 3）。
- rights：partial（→ dealability 最高 3）。

## 权益

- 状态：partial。依据 10-Q 原文："GenFleet granted the Company the option to obtain exclusive development and commercialization rights worldwide outside of mainland China, Hong Kong, Macau, and Taiwan (the “Territory”)"；"In January 2025, the Company exercised its GenFleet Option with respect to VS-7375"。
- 大中华区不是公司授出，而是许可方 GenFleet 保留。按“部分”处理，复核人可确认这个口径。
- 未见选择权、优先谈判权、共同开发条款。
- 对许可方义务：里程碑最高 $622.0M；中至高个位数特许权使用费；GenFleet 供货。
- Oberland 票据：初始 $75.0M；2026-08-28 新增 $50.0M 收入票据（快照 total_debt $73.8M 未含此笔）。控制权变更时可要求按本金 135% / 175% / 195% 赎回。1% 收入分成覆盖全部产品。GenFleet 相关知识产权设有负面质押。

## 资金

- 10-Q 没有跑道指引句，只有持续经营疑虑："raise substantial doubt about the Company’s ability to continue as a going concern"。
- 2026-10-14 增发，净额约 $234.7M（8-K 0001104659-26-115880）。
- 9-30 初步现金 $172.8M（8-K Item 2.02，未经审计）。
- pack 的 runway 8.5 个月、"融资压力"、股本和市值都早于这次增发，已过时。

## 待核实

- Merck 自有管线有没有 KRAS G12D 或 pan-RAS 资产（只核查了 10-K 竞争段）。
- 把胰腺癌归入画像中的“胃肠癌”是我们的解释。
- 临床数据只来自 8-K 附件（新闻稿和演示材料），未见同行评议或会议摘要。
- TARGET-D 301 是否已按计划在 2026 年底前开启。
- Erasca 联合研究是否会签订正式协议（目前只做临床前评估）。
- 2026-08-28 的 $50M 收入票据是否已实际发行（10-Q 写的是 "will be issued"）。
- 新 CEO（2027-01-01 上任）对 BD 策略的影响。

## pack 问题

- VS-7375 PDAC 有两行重复："Pancreatic Ductal Adenocarcinoma"（phase1_2，NCT07020221）和 "Pancreatic Ductal Adenocarcinoma (PDAC)"（phase2）。TOML 用了完整字符串，只匹配 phase2 行。
- DEFACTINIB 行 2411（PDAC，phase1_2）的来源是 VS-7375 的试验 NCT07020221，归属错误。
- DEFACTINIB "Ovarian Cancer" 被标成 approved：来源是 FDA 标签，但标签只批准 LGSOC。
- 财务数据早于 2026-10 增发和 8 月收入票据。

## 校验

- TOML 可解析。
- check_quotes：46 条引文，缺 0 条。
- preview_build 成功（reviews: 42）。第一次运行遇到 sqlite "disk I/O error"，疑似与并发构建冲突，重试后通过。

## 用时

约 25 分钟。
