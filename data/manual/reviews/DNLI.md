# DNLI（Denali Therapeutics）复核草稿

## 推荐组合

- 资产 / 适应症：TIVIDENOFUSP ALFA（AVLAYAH，ETV:IDS）/ Mucopolysaccharidosis II
- 买方：AstraZeneca #2（罕见病），需求条目「补体/酶替代和遗传性疾病药物」（AZ-1、AZ-3）
- 交易形式：收购
- 分数：buyer_fit 4、stage_match 0、clinical 3；catalyst 由 [event] 推导（high / estimated → 3）；dealability 由 [rights] 与 EV 推导

选择理由：tividenofusp alfa 是公司唯一上市产品，也是价值核心。它是酶替代疗法，对应 AZ 画像中的「酶替代和遗传性疾病药物」。全球权益在 10-Q 中有明确原文。

备选：zafinofusp alfa（DNL126，MPS IIIA，1/2 期）。按规则它的分数更高：stage 4（在 AZ「早期平台至Phase 3」内）、clinical 2、catalyst 3（公司称 "Denali expects a Biologics License Application (BLA) submission and potential accelerated approval for zafinofusp alfa for Sanfilippo syndrome type A in 2027"，只给到年份，按估算计）。但 10-K / 10-Q 没有一句话明确它的全球权益。10-K 只写了 "Of the 12 patent families, 3 families relate to the composition of matter of our ETV:SGSH structures, including DNL126"，研发表中 Operational Control 为 Denali。按 brief，权益未定须留空，即「待核实」，不能进入入选名单。因此主组合仍取 tividenofusp alfa。复核人如认可「自有专利 + 无授权协议」足以判定 full，可改选 DNL126。

## 权益状态：full

10-Q（2026-06-30，SEC-0001714899-26-000097）Note 9 原文：

> "The Company retains all worldwide development and commercialization rights to AVLAYAH."

合作方核查（均不涉及 ETV:IDS）：

- Biogen：LRRK2 共同开发 + TV 平台 ROFN/期权。10-K 原文 "The side letter also effected the immediate termination of the ROFN and Option Agreement"。
- Sanofi：仅 RIPK1 抑制剂（eclitasertib 由 Sanofi 开发）。
- Takeda：PTV:PGRN（2026 年 4 月通知终止，"all rights in the DNL593 program reverted to Denali"）与 ATV:TREM2（已终止）。

随资产转移的负担：

- Royalty Pharma 合成特许权使用费："a 9.25 % royalty on worldwide net sales of AVLAYAH"；EMA 批准后再付 7,500 万美元。
- F-star Gamma 收购产生的或有付款："$ 24.0 million due upon regulatory approval of AVLAYAH in the European Union, and up to $ 150.0 million in commercial contingent payments"。美国批准触发的 3,600 万美元已到期（已付 2,880 万）。

## FDA 监管事件（任务方提示）

PDUFA 日期（最初 2026-01-05，延至 2026-04-05）已过。FDA 于 2026-03-24 授予加速批准（10-Q 原文；openFDA Drugs@FDA BLA761485 "AP" 20260324，MAN-DNLI-3）。因此 24 个月窗口内没有待定的美国监管决定。下一事件取 COMPASS 主要完成（CT.gov 2027-12，估算）。

## 待核实

1. AstraZeneca 组合冲突：未打开 AZ 管线文件，不能确认其是否已有 MPS II 或入脑酶替代资产（「未核查组合冲突」）。
2. COMPASS 读出时间：公司文件未给季度 / 半年，只有 CT.gov 估算日期。
3. 欧盟 MAA 提交与 EMA 决定时间：文件未披露。
4. 与 idursulfase 的直接对比数据：COMPASS 未读出。
5. 未直接打开 NEJM 原文（Muenzer et al., NEJM 2026）；临床数值取自 10-K 对该文的转述。
6. 总债务：数据包 total_debt 为空；Royalty Pharma 2 亿美元按 ASC 470 记为债务性负债，EV 是否应计入请复核人决定。

## 数据包问题

- TIVIDENOFUSP ALFA 阶段为 phase2_3，错误：实际已上市（美国加速批准，2026-03-24）。build 会继续用 phase2_3 推导阶段，需修正推导或在 TOML 中保留 stage_match = 0 的覆盖。
- DNL126 未带通用名 zafinofusp alfa。
- BIIB122 (DNL151) 的 4 个自动组合（Novartis / AbbVie / J&J / Roche）已过时：LUMA 2b 期 "did not meet its primary or secondary endpoints"，特发性 PD 开发已停止；只剩 LRRK2 携带者 2a 期 BEACON。
- 自动主组合的下一事件取 NCT06075537（扩展研究）而非确证性 COMPASS（NCT05371613），已在 [event] 中改正。

## 用时

约 35 分钟。
