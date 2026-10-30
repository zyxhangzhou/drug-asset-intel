# SPRY（ARS Pharmaceuticals）复核草稿报告

## 选定组合

- 资产 / 适应症：ARS-2（鼻喷肾上腺素）/ 慢性自发性荨麻疹（CSU）急性发作。pack 映射为 `EPINEPHRINE (NEFFY)` / `Urticaria Chronic`（NCT06927999，2b 期）。
- 买方：Novartis #2「免疫」。画像点名「过敏」，理想阶段 Phase 1-3。
- 分数：buyer_fit 2；stage_match 4；clinical 3（置信度中）。catalyst 由 [event] 推导（中重要性 + 明确披露，应为 3）。dealability 由 [rights] 推导（partial，最高 3）。
- 结论：边缘候选，低优先级。理由：资产有阳性随机 2 期数据，2027Q1 有明确披露的 2b 期读出。但没有买方画像点名肾上腺素、鼻内给药或荨麻疹。Novartis 画像要求「抗体或免疫调节剂」，ARS-2 不满足。buyer_fit 只能给 2。
- 选 Novartis 的原因：10 家买方的治疗领域行中，只有它的画像点名「过敏」，阶段窗口也最宽。AbbVie #1、AstraZeneca #3、GSK #3 都限定长效抗体或生物药，契合度更低。

## 权益

状态：partial。美国权益由公司持有；美国以外已授出。最新 10-Q 原文：

> "exclusive license under certain of the Company’s patents and know-how to develop, manufacture and commercialize products containing epinephrine administered intranasally, including EURneffy ... for all human uses, including the immediate or emergency treatment of allergic reactions (including Type I) and anaphylaxis and urticaria, and other future indications as agreed by the parties."

- ALK：除美国、日本、大中华区、澳新以外的全球区域。许可字段明确包含 urticaria。
- Alfresa：日本。Pediatrix：中国大陆、香港、澳门、台湾。Seqirus：澳新。
- 引进许可：Aegis 的 Intravail 技术。特许权使用费为中个位数百分比，付给 OrbiMed 关联方。截至 2026-06-30，剩余里程碑 9.0 百万美元。
- 债务：RA Capital 牵头的有担保定期贷款，已提取 Term A 1 亿美元。担保物含知识产权。控制权变更构成违约事件。
- 资金：10-Q 写 "sufficient to meet its anticipated cash requirements for at least the 12 months following the date these financial statements are issued"。8-K 写 "anticipates a path to reaching cash flow breakeven by the end of 2027"。pack 的 runway 是 8.2 个月，按上半年烧钱率计算；上半年的消费者广告支出已经削减。

## 待核实

1. **partial 还是 restricted**：ALK 协议有新产品条款，原文 "upon ALK’s request such New Product will be included as a Product"。ARS-2 若单独递交 NDA，ALK 可要求把它纳入 ALK 区域的许可。我判为 partial，理由是该条款只涉及已经授出的区域，不限制美国权益。复核人如果把它视为选择权，应改为 restricted；那样 收购 + restricted 会阻止 SPRY 入选。
2. **组合冲突**：10-K 在 CSU 段点名 Xolair，但没有写上市方。Xolair 是否属于 Novartis，我没有在本次打开的来源中核实，所以写「未核查组合冲突」。即使属于 Novartis，两者机制也不同：Xolair 是维持治疗，ARS-2 是急性发作按需救急。
3. **clinical 3 还是 2**：CT.gov 登记 masking NONE，而论文写 "placebo-controlled"。主要终点是患者自报评分。CT.gov 结果没有登记统计分析，P 值只出现在论文摘要中。我只读了 PubMed 摘要，没有读全文。
4. **关键性研究时间**：10-K 写 "potential initiation of a single pivotal efficacy study in mid-2027"。10-Q 和 Q2 新闻稿没有重申这个时间。
5. **2026 年 8 月以后的进展**：EDGAR 上最新的文件是 2026-08-13（Q2 10-Q / 8-K），之后没有新文件。Q3 业绩尚未发布，2b 期时间表可能有变化。
6. **预览构建**：`preview_build.py` 运行失败，报错 sqlite "disk I/O error"，原因可能是其他进程同时在写。build 能否通过还没有验证。TOML 已能被 tomllib 解析；`check_quotes.py SPRY` 检查 33 条引文，缺失 0 条。

## pack 问题

- CSU 资产在公司文件中叫 ARS-2（"intranasal epinephrine technology known as ARS-2"），pack 把它挂在 `EPINEPHRINE (NEFFY)` 下。2b 期剂量为 0.5 mg 和 1 mg；neffy 是 1 mg 和 2 mg。
- 同一个荨麻疹项目被拆成两个 program：`ARS-1` / `Urticaria`（NCT05496465）与 `EPINEPHRINE (NEFFY)` / `Urticaria Chronic`（NCT06927999）。
- `ADRENALINE (ARS-1 WITH URTI)` / `Allergic Reactions` 的 stage 为 approved，但 stage_sources 是 `CTG-NCT06834165`，不是 `FDA-LABEL-` 来源。`ARS-1 WITHOUT URTI` 是从试验标题拆出来的伪 program。
- 10-Q 显示 neffy 已在加拿大获批（"China and Canada (in the case of neffy 2 mg)"）。pack 中没有加拿大获批的信息；这一点不影响本次配对。

## 用时

约 35 分钟。
