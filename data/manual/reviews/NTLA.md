# NTLA（Intellia Therapeutics）复核草稿报告

## 选定组合

- 资产 / 适应症：lonvo-z（NTLA-2002，lonvoguran ziclumeran）/ 遗传性血管性水肿（HAE）。TOML 中 `program = "NTLA-2002"`、`indication = "Hereditary Angioedema"`，匹配数据包 id 1468（phase3，HAELO NCT06634420）。
- 买方：AstraZeneca #2（罕见病，「基因疗法、体内细胞疗法、补体/酶替代和遗传性疾病药物」，理想阶段「早期平台至Phase 3」）。deal_form = 收购。
- 分数：buyer_fit 4（中）、stage_match 2、clinical 3；catalyst 由 [event] 推出（高 × 明确披露 = 4）；dealability 由 [rights] = full 与 EV 推出。

### 为什么不选 nex-z（NTLA-2001，ATTR）

1. 权益受限。10-Q（SEC-0001193125-26-337952）原文："Nex-z is the subject of a co-development and co-promotion (“Co/Co”) agreement (the “ATTR Co/Co”) with Regeneron, for which we are the clinical and commercial lead party and Regeneron is the participating party. Regeneron shares in approximately 25% of worldwide development costs and commercial profits for the ATTR program and has an option to enter into a co-promotion agreement for the U.S. commercialization." 按 brief 定义，rights = **restricted**（共同开发 + 利润分成 + 美国共同推广选择权）。10-Q 还写明 "there have been no material changes to the key terms of the 2016 Regeneron Agreement, ATTR Co/Co"。10-K（MAN-NTLA-1）有相同表述。
2. 安全事件（公司文件）：10-Q 原文 "On October 29, 2025, the FDA placed a clinical hold on the investigational new drug (“IND”) applications for the MAGNITUDE and MAGNITUDE-2 Phase 3 clinical trials"；起因是 "Grade 4 liver transaminase elevations and increased total bilirubin in a patient who was dosed with nex-z"，该患者 "passed away on November 5, 2025"（研究者报告死因为十二指肠溃疡穿孔继发脓毒性休克）。"In January 2026, we announced that the FDA lifted the clinical hold on the IND for MAGNITUDE-2"；"In March 2026, we announced that the FDA lifted the clinical hold on the IND for MAGNITUDE"。2026 年 8 月与 Regeneron 的基因组分析发现 "the highest observed liver transaminase elevations were in patients carrying one specific human leukocyte antigen (“HLA”) allele"，公司正就此与 FDA 沟通。当前无生效的临床暂停，但安全信号未完全解决。
3. 无 3 期疗效数据；下一事件只有 CT.gov 估算日期（MAGNITUDE 2027-12）。
4. ATTR 领域买方冲突：10-K 的 ATTR 竞争公司名单含 "AstraZeneca Pharmaceuticals LP"、"Novo Nordisk A/S, Pfizer, Inc."（MAN-NTLA-1），若改推 nex-z，这三家买方需先核查组合冲突。

### 为什么选 lonvo-z + AstraZeneca #2

- 10-Q："Lonvo-z is a wholly owned"；3 期 HAELO "met its primary endpoint"，"reduced attacks by 87% versus placebo"（p<0.0001）；8-K（MAN-NTLA-2）BLA 获受理、优先审评，"target action date of March 10, 2027"。
- 没有任何免疫类买方的 target_profile 提到 HAE / 激肽释放酶（AbbVie #1、BMS #2、J&J #2、Novartis #2、GSK #3 都只是标签匹配，最多 2 分）。AstraZeneca #2 的文字「基因疗法……遗传性疾病药物」与「体内 CRISPR、遗传病、一次性治疗」直接对应。
- 注意：自动初筛把 HAE 归入 immunology，不在 AZ #2 的 ta_codes 内；`reviewed_pair` 只校验 buyer + rank 存在，构建不会失败，但这是人工判断，签核人请确认。

## 权益状态（lonvo-z）：full

- 10-Q 原句："Lonvo-z is a wholly owned, investigational in vivo CRISPR-based therapeutic candidate designed to inactivate the kallikrein B1 (“KLKB1”) gene in the liver …"
- Regeneron 2016 协议给了 Regeneron 若干独家体内靶点，10-K/10-Q 没有列出靶点名单；但上面的 "wholly owned" 已直接说明 lonvo-z 不受其约束。
- 许可方义务：Caribou 独家许可（10-K："low- to mid-single-digit royalty obligations under its in-license agreement with Caribou Biosciences, Inc."，该句出现在 Regeneron 协议段落中，是否适用于 lonvo-z 待核实）；10-Q 风险因素提到可能向 "Caribou and Rewrite Therapeutics, Inc." 支付里程碑与特许权使用费。
- 交易障碍（不改变权益状态）：OrbiMed 信贷协议（MAN-NTLA-3，2026-09-04）以 "substantially all assets of the Company, including its intellectual property" 作第一顺位担保；限制 "effectuate mergers or consolidations, engage in asset sales and licensing transactions"；"change of control" 是违约事件（收购时贷款需偿还或谈判）。

## 待核实

1. AstraZeneca 是否已有 HAE 资产或体内基因编辑 HAE 资产（未核查组合冲突；10-K 的 HAE 竞争名单不含 AZ，但不是完整核查；AZ 的 20-F 不在允许来源内）。
2. Caribou 低至中个位数特许权使用费是否适用于 lonvo-z，以及 Rewrite 许可是否涉及 lonvo-z。
3. lonvo-z 与现有 HAE 长期预防药物的可比性（无有来源的同终点间接比较）。
4. NEJM 论文本身未打开（10-Q 提到 "a manuscript published in the New England Journal of Medicine"），结果数据目前只引自 10-Q。
5. nex-z HLA 等位基因发现后 FDA 的反馈及是否影响 MAGNITUDE 时间线。
6. EV：OrbiMed 已提款 7,500 万美元（MAN-NTLA-3），未计入。

## 数据包问题

- NTLA-2002 阶段：数据包为 phase3，公司最新披露为注册申请（BLA 已受理，2026-09-08）。stage_match 按 filed 打分。
- 同一资产拆成两个程序名：「BIOLOGICAL NTLA-2002」（phase1_2）与「NTLA-2002」（phase3）；用 `NTLA-2002` 子串时构建取最高阶段，没有问题。
- 资产通用名缺失：NTLA-2002 = lonvoguran ziclumeran（lonvo-z）；NTLA-2001 = nexiguran ziclumeran（nex-z）。
- 「NTLA-2001 / Neuromuscular Disease」（NCT06672237，MAGNITUDE-2）应为 ATTRv-PN；ATTR-CM 与 ATTR-PN 的 therapeutic_area 分别为 attr;cardiovascular 与 attr，Neuromuscular 一行为 null。
- HAE 被映射为 immunology；HAE 是遗传病，可考虑同时映射 rare_genetic。
- financials.total_debt 为 null：2026-09-04 已提取 OrbiMed 贷款 7,500 万美元（快照日 2026-06-30 之后），EV 约低估 7,500 万美元，仍在 < 20 亿美元档位（自动 EV 约 12.4 亿美元）。
- NTLA-3001（AATD 肺病）试验 WITHDRAWN、NTLA-5001 试验 TERMINATED，仍列为 phase1_2 程序。

## 用时

约 30 分钟。
