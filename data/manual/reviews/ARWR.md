# ARWR 复核草稿报告

## 推荐组合

- 资产 / 适应症：plozasiran（APOC3 siRNA）/ 重度高甘油三酯血症（sHTG），pack 第 530 行 `Severe Hypertriglyceridemia`（含 SHASTA-3 NCT06347003、SHASTA-4 NCT06347016）。
- 买方：Novartis #1（心血管-肾脏-代谢）。画像点名「血脂」（NVS-1/3/4），且技术偏好 #1 为「xRNA/siRNA及递送」（NVS-4/7），对应 plozasiran 的机制和适应症。Pfizer #1 的画像是 GLP-1 类激动剂，不对应 plozasiran，最多给 2 分，所以没有选。
- 交易形式：收购。部分权益（大中华区）与收购兼容。
- 分数：buyer_fit 4（置信度中）/ stage_match 4 / clinical 3（替代终点，只有安慰剂对照，按规则封顶 3 分）。catalyst 与 dealability 由 build 计算：事件为 high + disclosed；EV 约 78–82 亿美元，属 50–150 亿档。

## 权益

状态 `partial`：大中华区权益已归 Sanofi。

- 10-Q（2026-06-30）原文："(1) Greater China rights for plozasiran are out-licensed to Sanofi"
- 8-K Ex.99.1 原文："Arrowhead retaining rights to REDEMPLO in all geographies, outside of Greater China"
- 10-K（FY2025）原文："Severe Hypertriglyceridemia - plozasiran (formerly ARO-APOC3, Greater China rights out-licensed to Sanofi)"

其他障碍：
- Ionis 的 '333 专利诉讼。
- 债务：7 亿美元 0% 可转债（2032 年到期）；Sixth Street 信贷余额 1.814 亿美元，其条款限制 "asset sales and licensing transactions"；与 olpasiran 相关的特许权出售负债 3.925 亿美元，会计上按债务处理。
- 资金：10-Q 原文 "sufficient liquidity to fund its operations through at least the next twelve months"。

## 待核实

1. plozasiran 的 sHTG sNDA 是否已在 2026-08 之后提交。EDGAR 全文检索（2026-08-05 至 2026-10-30）没有找到 Arrowhead 提及 plozasiran 的文件；公司 IR 网站返回 403。
2. 事件确定性：公司原文是 "anticipated before the end of 2026"。这句给出了截止日期，但没有给季度。我标为 disclosed，timing 填 2026Q4。签核人可以把它降为 estimated。
3. 组合冲突：Novartis 是否持有 APOC3 或 sHTG 资产未核查。Leqvio 的靶点与适应症不在已打开的文件中。
4. APOC3 是否在 Alnylam–Novartis 许可的「30 undisclosed gene targets」之内，以及 plozasiran 是否欠 Alnylam 特许权使用费。
5. SHASTA 的设计细节未核实（是否随机、盲法），急性胰腺炎终点的统计层级也未核实。没有打开 ESC 摘要或论文。

## Pack 问题

- 财务数据过期。pack 的 `as_of` 为 2024-06-30，现金 4.367 亿美元，`total_debt` 为空，runway 为 12.1 个月。最新 10-Q（2026-06-30）显示：现金与投资合计 15.669 亿美元，信贷 1.814 亿美元，可转债 6.827 亿美元，特许权出售负债 3.925 亿美元。按最新数据重算，EV 约 78–82 亿美元，与 pack 的 80.7 亿美元同属 50–150 亿档，分档不变。需要重新抓取 XBRL 数据。
- auto_pair 选的是 `Hypertriglyceridemia`（第 528 行，MUIR-3 / OLE），没有选包含 SHASTA 读出的 sHTG 行。另外，"Hypertriglyceridemia" 同时是第 528 行和第 530 行的子串，匹配有歧义，所以复核用了 "Severe Hypertriglyceridemia"。
- pack 的阶段与公司披露一致：sHTG 为 3 期，FCS 已上市。pack 的 ARO-HSD、ARO-MMP7、ARO-ATXN2 等行没有标出 GSK 或 Sarepta 持有权益（10-Q 管线表），这些行不应作为可收购资产推荐。

## 来源

MAN-ARWR-1（10-K FY2025）、MAN-ARWR-2（8-K Ex.99.1，2026-08-04）、SEC-0000879407-26-000057（10-Q，2026-06-30，pack 已有）。

用时：约 25 分钟。
