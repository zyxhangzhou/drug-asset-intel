# VNDA 复核报告（草稿，待人工签核）

## 推荐组合

- 资产 / 适应症：TRADIPITANT（NEREUS）/ Nausea and Vomiting。这一行对应 GLP-1 受体激动剂引起的呕吐（NCT07446439 = Study 3601，org id VP-VLY-686-3601）。
- 买方：Novo Nordisk 第 1 治疗领域偏好（肥胖/糖尿病）。交易形式「许可」。
- 分数：buyer_fit 3（中），stage_match 4（高），clinical 3（中）。catalyst 由 [event] 推导：高 × 估算 = 3。dealability 由 rights=full 与 EV 档推导：4。预览构建结果为 83.8 / 83.8。
- 理由：Novo 画像写「更少胃肠道副作用……的GLP-1」。tradipitant 的 2 期试验以 Novo 的 Wegovy 作诱发药（"GLP-1 receptor agonist Wegovy"，10-K）。3 期用 semaglutide 1 mg（"a single 1 mg dose of semaglutide"，Study 3601 新闻稿）。在全部买方画像中，这是唯一与本公司资产几乎逐字对上的需求条目。buyer_fit 不给 4 分：画像要的是本身胃肠耐受更好的 GLP-1/胰淀素分子，本资产是联用的止吐药。
- 交易形式选「许可」：NEREUS 已上市（晕动病），公司还有 Fanapt、BYSANTI、HETLIOZ、PONVORY 等业务。买方只要这一个适应症时，区域或适应症许可更合理。但 Lilly 协议是否允许转授权未披露，见待核实。如改为「收购」，与 full 权益并不冲突。EV 很小：包内约 0.72 亿美元；按 Q3 现金 1.405 亿美元重算约 1.01 亿美元。

## 为什么不选其他资产

- 伊潘立酮（Fanapt，自动主推荐）：已上市，没有买方需求条目能对上。权益只有美国和加拿大："Novartis transferred all U.S. and Canadian rights in the Fanapt ® franchise to us"（10-K）。另有 Titan 许可风险："We may lose our rights to develop and commercialize Fanapt ® if we fail to comply with certain requirements in the Titan license agreement"。
- milsaperidone（BYSANTI）辅助治疗 MDD，3 期：读出时间已明确披露（"results expected in the first half of 2027"，Q3 8-K）。不选的原因有四个。第一，它是伊潘立酮的活性代谢物（"the active metabolite of Fanapt"），对不上 J&J #3 画像的「新机制」。第二，J&J 证据行点名的 Caplyta 是同类精神科药，可能构成组合冲突。第三，MDD 没有疗效数据，clinical 只能给 1 分。第四，已打开的文件都没有写明 BYSANTI 是否受 Fanapt 的 Novartis/Titan 权益链约束，而且 Fanapt 权益只覆盖美国和加拿大。如签核人偏好神经科学方向，这是第二选择，rights 需标「待核实」。
- imsidolimab（Quimilza），GPP：数据扎实。GEMINI-1 主要终点达标（53% 对 13%，P=0.023，NEJM Evidence，PMID 42047557），PDUFA 日为 2026-12-12（明确披露），权益为 full（引进自 Anaptys，10% 特许权使用费）。不选的原因：没有买方画像点名 IL-36 或 GPP，buyer_fit 最多 3 分；BLA 已在审，比所有免疫行的理想阶段（最高到 3 期）多一个阶段，stage_match 只得 2 分。批准后会变成「已上市」，stage_match 降到 0。备选买方为 Novartis #2（画像写「皮炎和自身免疫的抗体……生物标志物分层」，摘要提到 IL36RN 变异）。
- ponesimod（PONVORY）银屑病 / 溃疡性结肠炎，3 期：只买入了美国和加拿大权益（"purchased the rights to market and sell PONVORY ® in the U.S. and Canadian markets from Actelion Pharmaceuticals Ltd. (Janssen)"），权益为 partial，许可方又是 J&J。
- VQW-765：2 期结果只有 "numerically lower stress levels"，权益引进自 Novartis。tasimelteon：已有仿制药，没有对应买方领域。

## 资产权益：full

- 最新 10-Q（2026-09-30）原文："the Company entered into a license agreement with Lilly under which it acquired an exclusive worldwide license under certain patents and patent applications, and other licenses to intellectual property, to develop and commercialize NEREUS TM for all human indications."
- 引进义务：特许权使用费 "percentage rates up to the low double digits"。剩余里程碑："a $ 5.0 million milestone for the first approval of an application for marketing authorization for NEREUS TM in the E.U. and up to $ 80.0 million for sales milestones"。协议终止时权益回归 Lilly（10-K）。
- 检索结果：10-K 与 10-Q 中没有与 NEREUS 相关的选择权、ROFN、共同商业化或利润分成条款。
- 债务：没有借款或票据，只有融资租赁负债（非流动 2,345 千美元，流动 4,022 千美元）。包内 total_debt 为空，与此一致。
- 资金指引原文（Q3 10-Q）："will be sufficient for at least the next 12 months as of the date the financial statements were issued"。Q3 末现金 1.405 亿美元，Q3 现金减少 2,950 万美元。

## 待核实

1. sNDA 提交时间。公司只写 FDA 讨论 "proposed sNDA submission during 2027"，没有给季度或半年，因此事件标「估算」，timing 只写 2027。
2. Lilly 协议是否允许转授权，以及给 Novo 做许可是否需要 Lilly 同意。文件未披露。Lilly 是 Novo 的主要竞争对手，这是交易障碍。
3. 组合冲突：Novo 是否已有同机制（NK-1）或其他 GLP-1 止吐联用资产。没有打开 Novo 的文件，未核查组合冲突。
4. Study 3601 只有公司新闻稿（PR Newswire）。公司 IR 站点返回 403，EDGAR 上没有对应的 8-K。没有同行评议全文。
5. CT.gov 上的 NCT07446439 仍为 RECRUITING、预计入组 280，与新闻稿的 306 例分析人数不一致（记录未更新）。
6. 激发模型（未滴定单次 1 mg）外推到真实用法能否被 FDA 接受。
7. stage_match 按适应症阶段（3 期）计。若签核人按资产阶段（NEREUS 已上市）计，按 §3.2 示例降为 2 分。

## 包数据问题

- 适应症标注错误：包内 "TRADIPITANT (VLY-686) | Obesity | phase2" 实为 GLP-1 相关恶心呕吐 2 期（NCT06804603，VP-VLY-686-2601），不是肥胖治疗。"Nausea and Vomiting" 行的 therapeutic_area 为空。预览构建能接受该行与 Novo #1 配对。
- 阶段错误：imsidolimab GPP 在包内为 phase3，实际 BLA 已在审（PDUFA 2026-12-12），应为「注册申请」。milsaperidone 在包内只有 MDD 3 期行，BYSANTI 已于 2026-02-20 获批（包内 approved_products 已列出）。
- 伊潘立酮 "Hypertension | phase2" 行：10-K 写的是 LAI 剂型（"long acting injectable formulation of Fanapt ® in people with treatment-resistant hypertension"）。
- NCT07446439 在包内为「RECRUITING，2026-12-01 估算」，但结果已于 2026-10-27 公布。自动初筛如把它当未来读出，会高估催化。
- 财务过时：包用 2026-06-30 数据（现金 1.700 亿美元）。Q3 10-Q（2026-09-30）为 1.405 亿美元，EV 应重算为约 1.01 亿美元，仍在 < 20 亿档。

## 用时

约 35 分钟。
