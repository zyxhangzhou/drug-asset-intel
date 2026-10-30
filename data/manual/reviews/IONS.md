# IONS 复核报告（草稿，待人工签核）

## 推荐组合

- 资产 / 适应症：obudanersen（原 ION582，鞘内 ASO，抑制 UBE3A 反义转录本）/ Angelman 综合征（AS）。TOML 中 `program = "OBUDANERSEN"`（对应派生名 "OBUDANERSEN (ION582)"，id 944），`indication = "Angelman Syndrome"`，阶段 3 期，与 10-Q 一致。
- 买方：Novartis 第 3 治疗领域偏好（神经科学及精准肿瘤，「早期平台至Phase 3」），交易形式「许可」。
- 选资产的理由：用户要求优先选全资晚期资产。逐项排除如下。
  - donidalorsen（DAWNZERA）：已上市（2025-08 FDA 批准）。欧洲与亚太商业化权利已许可给 Otsuka（10-Q）。
  - olezarsen（TRYNGOLZA）：已上市，FCS 与 sHTG 两个适应症（10-Q："In June 2026, the U.S. Food and Drug Administration, or FDA, approved TRYNGOLZA for the treatment of sHTG"）。
  - zilganersen（ZANVASTRO）：2026-09 获 FDA 批准（MAN-IONS-3）。美国以外权利已许可给 Recordati（10-Q）。
  - ulefnersen（包内 ION363，FUS-ALS，3 期）：10-Q 原文 "We licensed global commercialization rights for ulefnersen to Otsuka"，属受限权益。
  - 剩下的全资 3 期资产只有 obudanersen。10-Q 把它列在 "Ionis-Owned Investigational Medicines" 下。
- 选买方的理由：
  - Roche #2（神经科学）已排除。Ionis 10-K 竞争表列出 "Rugonersen | Oak Hill Bio / Roche | A locked nucleic acid that targets UBE3A gene | Phase 3"，与 obudanersen 同机制、同适应症，属组合冲突。Roche 还持有 alogabat（AS，2 期）。
  - Novartis #3 画像写「神经退行性疾病遗传药物」。技术类型第 1 位是「xRNA/siRNA及递送」。在剩下的买方中，只有 Novartis 同时点名遗传药物和寡核苷酸类技术。
  - AbbVie #2、J&J #3 只匹配神经科学标签，技术偏好是中枢小分子，所以比 Novartis 弱。
  - 局限：AS 是神经发育障碍，不是神经退行性疾病，所以 buyer_fit 给 3，不给 4。
- 分数：
  - buyer_fit 3（中）
  - stage_match 4（高）
  - clinical 2（中高）。HALOS 是开放标签 MAD 研究，没有对照组。
  - catalyst 由 [event] 推导：高重要性 + 明确披露，得 4。REVEAL 数据 "anticipated in the second half of 2027"。
  - dealability 由 rights=full 与 EV 档推导。EV ≈ 74.62 亿市值 + 13.45 亿可转债本金 − 27.02 亿现金及投资 ≈ 61.0 亿美元，属 50–150 亿档，得 2 分。交易形式为许可，所以 EV 只作参考。
- 交易形式选「许可」的理由：Ionis 是有 7 个上市产品的商业化公司。整体收购要连带买下全部商业平台和可转债。Ionis 处理全资资产的惯例是区域或全球商业化许可（Otsuka、Recordati 均见 10-Q）。

## 资产权益：full（推断，中高）

- 10-K 原文："We currently have three wholly owned medicines in late-stage development, including obudanersen (formerly ION582) for Angelman syndrome"
- 10-K 原文："In 2024, Biogen’s option to license obudanersen, an investigational antisense medicine for the potential treatment of Angelman syndrome, or AS, expired unexercised."
- 最新 10-Q（2026-06-30）原文："We currently have two wholly owned medicines and eight partnered medicines in Phase 3 development, including obudanersen"
- 10-Q 的合作附注涵盖 Biogen、GSK、Ono、Otsuka、Recordati、Roche，均未提到 obudanersen 的新许可。2026-07 至 2026-10 的 8-K Ex.99.1 也没有提到。
- 没有发现引进许可，也没有发现应付许可方的特许权使用费。SPINRAZA 对 Cold Spring Harbor 和 UMass 有付款义务，与 obudanersen 无关。
- 债务：
  - 0% 可转债，2030 年到期，本金 7.70 亿美元。
  - 1.75% 可转债，2028 年到期，本金 5.75 亿美元。
  - Royalty Pharma 特许权出售负债 5.63 亿美元，涉及 SPINRAZA 与 pelacarsen。
  - 包内 `total_debt` 为空，实际有上述可转债。
- 资金：10-Q 原文 "will be sufficient to fund our planned operations and these obligations"。10-Q 没有给出按月计的现金跑道。

## 下一事件

- 3 期 REVEAL（NCT06914609）数据读出，时间为 2027 年下半年，属明确披露（MAN-IONS-2）。CT.gov 预计主要完成日为 2027-08。
- 第二项 3 期 CHAMPION（NCT07782827）预计 2028-05 完成。它的设计没有在公司文件中核对。

## 待核实

1. HALOS 的量化结果（例数、各量表数值、各剂量组改善比例）。公司 IR 新闻稿返回 403，没有打开；同行评议全文和会议摘要也没有打开。TOML 只用了 10-K / 10-Q 的定性描述。
2. Novartis 是否已有 AS 或 UBE3A 资产：没有打开 Novartis 文件。Ionis 10-K 竞争表中没有 Novartis。
3. Biogen 选择权失效后，obudanersen 是否仍对 Biogen 有付款义务：文件没有写明。
4. REVEAL 的主要终点、样本量和随机比例：本次打开的文件没有写。
5. CHAMPION（NCT07782827）与 REVEAL 的关系，以及它是否属于注册研究。
6. 2026 年第 3 季度 10-Q 截至 2026-10-30 尚未列出。权益判断依据 2026-06-30 的 10-Q 和其后的 8-K。

## 包数据问题

- 自动主组合选中 donidalorsen / AbbVie #1。donidalorsen 已上市，欧亚太权利在 Otsuka，不应作为主推荐。
- 阶段错误：
  - donidalorsen（id 890、891）显示 phase3，但它已在 `approved_products`（NDA219407）中。阶段来源应为 FDA-LABEL。
  - zilganersen（id 955）显示 phase3，但它已获批（NDA220210，2026-09-03）。
- 资产名：ION363 就是 ulefnersen，包内没有通用名。
- sapablursen 在包内为 phase2。Q2 新闻稿的 3 期事件表写 "Sapablursen | | Polycythemia Vera | | Phase 3 initiation | Achieved"，阶段可能已到 3 期。
- 债务：包内 `total_debt` 为空，10-Q 有 13.45 亿美元可转债本金。
- 治疗领域：AxD、FCS 等多行 `therapeutic_area` 为空。

## 用时

约 35 分钟。
