# CTMX（CytomX Therapeutics）复核草稿报告

## 推荐组合

- 资产 / 适应症：VARSETATUG MASETECAN（Varseta-M，CX-2051，遮蔽式 EpCAM Topo-1 ADC）/ Colo-rectal Cancer（晚线转移性 CRC），1 期。
- 买方：Bristol Myers Squibb，治疗领域偏好第 1（肿瘤/血液肿瘤，ideal_stage「Phase 2-3」）。
- 交易形式：许可。依据是 BMS 技术类型第 1 行（双抗、ADC 与 T 细胞连接器）的交易形式「全球/区域许可、共同开发」（BMY-2/4/5）。权益完整，收购也成立；EV 在许可方案下只作参考。
- 分数：buyer_fit 4（中）、stage_match 2（高）、clinical 2（中高）。build 推导：catalyst 3、dealability 4。预览 build 结果：保守 / 乐观均为 76.2，覆盖率 1.0。

选择理由：

- BMS #1 画像「肺癌、乳腺癌、消化道癌…的双抗、ADC或新靶点资产」同时点名适应症（消化道癌）、技术类型（ADC）和新靶点。Varseta-M 三项都符合：\"the only EpCAM-directed antibody drug conjugate (ADC) in clinical development\"（MAN-CTMX-1）。
- 10-K 的 CRC 竞品段未列 BMS。BMS 只出现在泛 ADC 开发者名单中。
- 备选：Novartis #3（「ADC或新payload肿瘤药」，ideal_stage「早期平台至Phase 3」）。阶段匹配得 4 分，但画像只对上 ADC 一项；载荷是 ImmunoGen 的 Topo-1，不是新 payload。auto_pair 主组合即 Novartis #3。
- 不选 Merck #1：画像有「胃肠癌」，但 ideal_stage「Phase 2b-注册期」，与 1 期差两个阶段（0 分）。
- 不选 AbbVie #3：AbbVie 是许可方（载荷与项目都来自 ImmunoGen），且自有 CRC 3 期 ADC：\"AbbVie is developing ABBV-400 for a subset of CRC patients in a Phase 3 clinical trial\"（MAN-CTMX-2）。

## 资产权益

- 状态：full（事实）。
- 10-Q 原句：\"The license gives the Company the sole ability to develop, manufacture, use and commercialize any licensed product that incorporates, is comprised of, or otherwise derived from PROBODY technology that targets EpCAM in any human therapeutic field on a worldwide basis.\"（SEC-0001193125-26-337950）
- 10-K 原句：\"we obtained a worldwide, exclusive, sublicensable license to the EpCAM conditionally activated ADC program from ImmunoGen\"（MAN-CTMX-2）。
- 未见对外授权、选择权、ROFN 或共同开发。BMS 平台合作已终止（2026 年 5 月），与 Varseta-M 无关。10-Q 中 Regeneron 合作的标的是双特异抗体：\"conditionally-activated investigational bispecific cancer therapies\"，不涉及 ADC。
- 引进义务（欠 AbbVie）：2 期启动里程碑 1,000 万美元、3 期启动 2,000 万美元；监管与商业里程碑最高 3.2 亿美元；销售提成 \"mid-to-high single digits percentages\"。
- 债务：10-Q 检索 loan / borrow / notes payable，未见借款。pack 的 total_debt 为空与此一致。
- 现金跑道，10-Q 原句：\"we expect our existing capital resources will be sufficient to fund operations into at least the second half of 2028\"。另有 2026 年 7 月收到的 Regeneron 3,700 万美元，不在 6 月 30 日现金中（MAN-CTMX-1）。

## 待核实

1. 组合冲突：只按 10-K 竞品段核查。BMS 早期管线中是否有 EpCAM ADC 或 CRC ADC，未核查。
2. 剂量优化组数据（2026 年底前更新）未公布。临床分数基于 2026-01-16 截止的中期数据（10-K）。未打开会议摘要或同行评议原文。
3. 注册研究设计（单臂还是随机）未披露。启动时间取决于与 FDA 对齐（公司用词 \"aims to\"）。
4. UCSB 平台许可（低个位数提成 + 每适应症最高 110 万美元里程碑）是否适用于 Varseta-M，文件未写明。
5. 2026 年 3 月 8-K（d100765）是股票发行，未逐项读其条款（权证等）。
6. Q3 2026 10-Q 截至 2026-10-30 尚未提交，未查。
7. 卖方/买方意愿：BMS 2026 年 5 月放弃了 CytomX 平台剩余临床前项目。这不涉及 Varseta-M，但可能影响 BMS 对 PROBODY 平台的态度。未写进论点。

## Pack 问题

- 同一资产拆成两个程序：`CX-2051 / Solid Tumor, Adult`（1 期单药 NCT06265688，疗效数据来源）与 `VARSETATUG MASETECAN / Colo-rectal Cancer`（联合用药 NCT07900165，NOT_YET_RECRUITING）。应合并为一个别名。
- `VARSETATUG MASETECAN` 的 stage = phase1_2 来自尚未入组的联合试验。实际阶段是 1 期：\"Varseta-M, which is currently in Phase 1 development\"（10-Q）。
- auto_pair 主组合的适应症为 Solid Tumor, Adult，应为 CRC。
- CX-072（PD-L1，试验均已终止）的 8 条 auto_pair 是噪声。CX-2009、CX-2029、CX-904、CX-188 均已终止或撤回（10-K）。
- CX-801（遮蔽式 IFNα2b，黑色素瘤 1 期）未作为推荐资产。联合 KEYTRUDA 的初始数据预计 2027 年上半年（MAN-CTMX-1）。

## 用时

约 30 分钟。
