# RGNX（REGENXBIO）复核草稿报告

## 选定组合

- 资产 / 适应症：RGX-202 / 杜氏肌营养不良（DMD）。TOML 中 `program = "RGX-202"`、`indication = "Duchenne Muscular Dystrophy"`，匹配数据包 id 2189（NCT05693142）。
- 买方：AstraZeneca #2（罕见病，「基因疗法、体内细胞疗法、补体/酶替代和遗传性疾病药物」，理想阶段「早期平台至Phase 3」）。deal_form = 收购。
- 分数：buyer_fit 4（中）、stage_match 4（中）、clinical 3（中）；catalyst 由 [event] 推出（高 × 明确披露 = 4）；dealability 由 [rights] = full 与 EV 推出。

### 为什么选 RGX-202 + AstraZeneca #2

- RGX-202 是公司唯一未对外授权的后期资产。关键性 3 期已达主要终点；公司计划 2026 年三季度启动加速批准 BLA，"supporting potential approval in 2H 2027"（Q2 新闻稿，MAN-RGNX-2）。
- AZ #2 画像直接点名「基因疗法」「遗传性疾病药物」。AZ 技术偏好 #2（「递送和制造优势明显、可重复生产的临床平台」）也与公司自建产线相符。
- 10-K DMD 竞争段落点名 Sarepta/Roche（Elevidys，同机制同适应症）与 Novartis（早期 DMD 基因疗法），所以不选 Roche、Novartis。AstraZeneca 不在名单中；名单不完整，记「未核查组合冲突」。

### 为什么不选数据包自动主组合（RGX-121-3102 / MPS II / AZ #2）

- 2026-02 FDA 发出 CRL（10-Q）。
- 2026-08-24 8-K："placed on clinical hold and that the Company does not expect to resubmit the RGX-121 BLA in the near term"（MAN-RGNX-3）。
- RGX-121 / RGX-111 与 Nippon Shinyaku 合作开发与商业化，权益受限。

### 不选 sura-vec（ABBV-RGX-314）

- 与 AbbVie 合作开发与商业化（"in collaboration with AbbVie"），美国利润分成，权益为 restricted。湿性 AMD 关键性 topline 预计 2026 Q4，但不能作为收购标的资产。

## 权益状态（RGX-202）：full（推断，置信度中）

- 10-K / 10-Q **没有**「RGX-202 为全资资产」的原句。
- 依据（10-Q）："Sura-vec is being developed and commercialized in collaboration with AbbVie Global Enterprises Ltd. (AbbVie), a subsidiary of AbbVie Inc. RGX-121 and RGX-111 are being developed and commercialized in collaboration with Nippon Shinyaku Co., Ltd. (Nippon Shinyaku)." RGX-202 不在合作列表中；公司自行开展试验并生产商业供货。
- 上游许可（10-K）：
  - Penn："low- to mid-single digit royalties on net sales of licensed pharmaceutical products sold by us or our affiliates"；里程碑 "up to $20.5 million"。
  - GSK：销售分成转付 Penn；GSK 保留 "AAV9 for the treatment of Muscular Dystrophy" 的权利（RGX-202 用 AAV8，判断不冲突，请签核人确认）；存在分许可费争议。
- 债务（数据包 total_debt 为空）：10-Q Note 7 "Royalty monetization liabilities are accounted for as debt"，2026-06-30 合计 1.815 亿美元（2020 HCR 协议 0.118 亿、2025 Royalty Bond 1.697 亿）。Royalty Bond 以 Novartis / Nippon Shinyaku / Rocket / Ultragenyx 许可收入为担保，不涉及 RGX-202；"may not be prepaid prior to maturity"。10-K/10-Q 未见控制权变更条款。

## 资金

- 10-Q 原句："Management believes the Company's cash, cash equivalents and marketable securities as of June 30, 2026, along with the milestone payment and offering proceeds received in July 2026, are sufficient to fund operations into the fourth quarter of 2027."
- 数据包 runway 4.6 个月只用 6 月末现金 1.055 亿美元，未计 7 月 AbbVie 里程碑 1 亿美元与增发净额 1.078 亿美元（备考约 3.13 亿美元）。
- 数据包 EV（3.72 亿美元）未计 1.815 亿美元特许权货币化负债，也未计 7 月流入与增发股份。
- 2026-09-23 8-K：与 Sarepta 和解，Sarepta 支付 3,900 万美元（未作为来源写入 TOML）。

## 待核实

1. RGX-202 BLA 是否已在 2026 Q3 实际启动 / 完成提交。所有已打开文件只说"计划"；公司 IR 新闻页 HTTP 403，未打开。已提交则 stage_match 应降为 2，事件时间不变。
2. RGX-202 的全球权益：无「全资」原句，依据是合作披露的穷尽。
3. AstraZeneca 是否已有 DMD 或同类 AAV 资产（未核查组合冲突）。
4. clinical 3 分的依据：FDA 只说外部对照"may be adequate"，同时建议随机对照；签核人可改为 2。
5. 关键性 topline 新闻稿（2026-05，DOC-RGNX-a7b98e30）已存档；功能评分差值来自其图 1（图片，已存档于 `data/raw/docs/RGNX/DOC-RGNX-a7b98e30.images/`），签核时请对照图片。图 2 的相关系数为 0.94 / 0.92，正文写作 .094 / .092，按图判断正文为笔误；已入库的两条抽取结果按正文引用了 .094 / .092。会议摘要与详细安全性数据未取得。
6. GSK 保留的肌营养不良权利是否完全限于 AAV9；GSK 分许可费争议金额。
7. 2026 Q3 10-Q 尚未发布，未核对 9 月 30 日现金与 BLA 状态。

## 数据包问题

- 自动主组合 RGX-121-3102 已被临床暂停，且有 Nippon Shinyaku 合作（见上）。RGX-121 程序还缺 CRL 信息。
- RGX-202 阶段为 phase2_3，实际关键性部分是 3 期且已读出（10-Q："the pivotal Phase III AFFINITY DUCHENNE trial"）；CT.gov 预计主要完成 2026-09 已过。
- RGX-314 显示 phase1_2，实际为关键性 ATMOSPHERE / ASCENT（topline 2026 Q4）和 2b/3 期 NAAVIGATE（DR）；且是与 AbbVie 合作的资产。
- RGX-111 也有临床暂停（8-24 新闻稿提到 "the clinical hold related to RGX-111"）；数据包显示 SUSPENDED，一致。
- 两个 HoFH 程序（RGX-501）已终止 / 状态未知，不是在研资产。
- total_debt 为空，但有按债务核算的 1.815 亿美元特许权货币化负债。
- 预览构建（preview_build.py）运行时报 sqlite "disk I/O error"，可能是并行构建冲突，本次未完成构建校验；tomllib 解析与 check_quotes（29 条引文，0 条缺失）通过。

## 用时

约 30 分钟。
