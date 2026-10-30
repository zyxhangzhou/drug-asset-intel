# ALT（Altimmune）复核草稿报告

## 选定组合

- 资产 / 适应症：pemvidutide（`PEMVIDUTIDE (ALT-801)`）/ MASH（pack 中 phase3 行 `Metabolic Dysfunction-Associated Steatohepatitis (MASH)`，NCT07795164）。
- 买方：Novo Nordisk #2「MASH及肝脏代谢」，ideal_stage Phase 2b-3，需求条目「联合减重的MASH资产」（NVO-1）。
- deal_form：收购。
- 分数：buyer_fit 3（中）、stage_match 4（高）、clinical 3（中高）；catalyst 与 dealability 由 build 推导（event = 中重要性 + 明确披露 → 预计 3；rights = full）。

为什么选 MASH，不选其他适应症：

- MASH：证据最强。随机 2b 期 IMPACT 达到 MASH 缓解主要终点，3 期 PERFORMA 已启动。Novo #2 的 target_profile 直接写「联合减重的MASH资产」。
- AUD：RECLAIM 2 期阳性（MAN-ALT-4），但 10 家买方中没有 target_profile 覆盖成瘾 / AUD 的行。AbbVie #2 神经科学画像是「抑郁、精神分裂症、阿尔茨海默病/抗tau、偏头痛」，不匹配。pack 中该行 therapeutic_area 为 null。
- ALD：RESTORE 2 期数据 2027H2 才出，目前没有疗效数据。任何买方画像都没有写 ALD。
- 肥胖：pack 中最新为 2023 年完成的 2 期。公司 2026 年材料只写 MASH、AUD、ALD 三个适应症，没有在研肥胖项目。

买方组合冲突（已核查，不写「未核查组合冲突」）：FDA 页面显示 Novo 的 Wegovy（semaglutide，GLP-1 单激动剂）已获批 MASH（MAN-ALT-6）。买方材料也写明 Novo 已收购 efruxifermin（FGF21）。两者都不是 glucagon/GLP-1 双激动剂，所以不按同机制冲突给 0 分。但适应症重叠，GLP-1 成分也重叠，所以 buyer_fit 从 4 降到 3。

## 权益状态：full（推断，中高）

- 10-K 没有「worldwide rights」字面句子。判断依据：10-K Item 1、10-K 附注和 2026Q2 10-Q 都没有对外授权、选择权、ROFN、共同开发或利润分成的披露。
- 10-K 原文：
  - "We obtained pemvidutide as part of the acquisition Spitfire Pharma Inc., in July of 2019."
  - "we are the exclusive licensee of patent rights owned by Mederis to develop and commercialize surfactant functionalized ("EuPort domain") incretin-based peptide therapeutics, including (GLP-1-glucagon)/oxyntomodulin, and variants thereof, including pemvidutide, for any indication"
- 下游义务：
  - Mederis 许可含 "diligence, milestone payment, royalty" 义务，费率未披露。
  - Spitfire 原股东最高 8000 万美元销售里程碑（10-Q：SEC-0001326190-26-000052）。
  - Adocia 协议（2024-12-24）是公司获得口服制剂知识产权的独家权利，不是对外授权。

## 待核实

1. Mederis 许可的特许权使用费率、里程碑金额，以及是否有地域限制。10-K 正文只写 "for any indication"，没有写地域。协议原文是 2019-11-13 10-Q 的 Exhibit 10.2，本次未打开。
2. AUD 的 FDA 2 期结束会议：没有披露时间，所以未作为 [event]。
3. IMPACT 的同行评议全文或会议摘要：本次只用了公司新闻稿顶线数据。
4. MAN-ALT-6（FDA 页面）是通过 WebFetch 读取的，没有本地存档。引用片段需人工打开页面再核对一次。
5. PERFORMA 3 期 52 周读出预计 2029 年（MAN-ALT-4），在 24 个月窗口外。窗口内的 [event] 改用同一资产的 ALD 读出（2027H2）。人工判断这是否符合「主推荐资产事件」口径。

## pack 问题

- 同一适应症被拆成两个名称：IMPACT（NCT05989711，本次的证据试验）在 `Non-Alcoholic Steatohepatitis (NASH)` 行（phase2），PERFORMA 在 `...(MASH)` 行（phase3）。另外还有 `NASH - Nonalcoholic Steatohepatitis` 行，但该行实际是 DDI 健康人试验 NCT04972396，不是 NASH 试验。
- 垃圾程序名：`SUBJECTS WERE ADMINISTERED NASOVAX`（NCT03760549），应并入 NASOVAX。
- AUD 行（NCT06987513）的 therapeutic_area 为 null。
- auto_pairs 的主组合是 ALD（catalyst 2）。复核后改为 MASH，因为 MASH 证据更强，需求条目也更具体。

## 用时

约 35 分钟。
