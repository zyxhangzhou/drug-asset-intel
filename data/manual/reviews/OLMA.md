# OLMA（Olema Pharmaceuticals）复核草稿报告

## 选定组合

- 资产 / 适应症：PALAZESTRANT (OP-1250) / Breast Cancer（推导管线 program_indication 2073，3 期）。
- 买方：Novartis，偏好第 3 位（神经科学及精准肿瘤），deal_form = 许可。
- 评分：buyer_fit 2，stage_match 4，clinical 2；构建结果 catalyst 4，dealability 1（restricted 上限），保守分 63.7，覆盖率 1.0（预览构建，仅含 OLMA）。

### 为什么选 Novartis

- Novartis 画像（NVS-3）写的是"放射性配体、ADC或新payload肿瘤药"，与口服 SERD 只是领域匹配。buyer_fit 只给 2，没有因为交易结构上调。
- 选它的原因是权益：Novartis 持有 palazestrant 任何许可或转让的优先谈判权，并为 OPERA-02 供应 ribociclib。只有对 Novartis，交易形式与权益限制兼容。
- 画像匹配更好的买方都有组合冲突（10-K 竞品清单，MAN-OLMA-1）：
  - Pfizer #2（乳腺 + 靶向小分子 + Ibrance 2027 LOE）："vepdegestrant (ARV‑471), being developed by Arvinas, Inc. in partnership with Pfizer, Inc."
  - Roche #1（画像明写 ER）："giredestrant (GDC-9545), being developed by Roche Holding AG/Genentech, Inc."
  - AstraZeneca #1（乳腺癌 + 靶向小分子）："camizestrant (AZD9833), being developed by AstraZeneca PLC"
- 备选：BMS #1 画像写明乳腺癌，但限定"双抗、ADC或新靶点资产"，同样只得 2；且对第三方任何交易都触发 Novartis 优先谈判权。
- 人工签核时请决定：限制对 Novartis 有利，dealability 被机械限到 1 分是否需要覆盖；若改 deal_form 为 收购，按现行规则会被名单门槛拦下。

## 权益状态：restricted

- 10-K 原句（MAN-OLMA-1）："We own full worldwide development and commercialization rights to both palazestrant and OP-3136."
- 同一 10-K 原句："We granted Novartis a right of first negotiation with respect to (a) the grant to any person or entity any right, license or sublicense to exploit palazestrant, in any field or territory, other than to third party service providers, or (b) the sale or other transfer to any person or entity of palazestrant and any related assets"
- 最新 10-Q（SEC-0001193125-26-342383）保留同一条款（"The Company granted Novartis a right of first negotiation ..."）及偿付义务："the proportion of approximately $ 275 million that is represented by the number of units of ribociclib actually supplied"。
- 公司主动出售时 Novartis 有 45 天排他尽调与谈判期；收到主动收购要约须 24 小时内通知 Novartis。
- 期限：至 "the date that is 120 days after filing of the New Drug Application for the Olema Combination" 等较早者。
- Pfizer 两项协议（Ibrance、atirmociclib）为非排他临床供应协议，不涉及权益。Bayer 协议（8-K EX-99.1）只涉及 OP-3136。
- 引进许可：Aurigene 许可只覆盖 OP-3136（里程碑最高 4,500 万美元临床/监管 + 3.7 亿美元商业，另有特许权使用费）。palazestrant 未见对许可方的付费义务。

## 下一事件

- OPERA-01 顶线数据 2027Q1，明确披露（MAN-OLMA-2，2026-08-10）。10-K 原写 "fall of 2026"，已推迟。

## 待核实

- Novartis 是否持有同机制（ER 降解剂 / 拮抗剂）乳腺癌资产：未核查组合冲突（10-K 竞品清单未列 Novartis，但不能作为否定证据）。
- 2 期与 1b/2 期数据只取自 10-K 转述，未打开 ESMO 2023 / ESMO 2025 摘要原文。
- OPERA-01 主要终点定义（PFS 人群、ESR1 突变亚组）未从注册记录或公司文件逐字核对。
- 收购成本：偿付 Novartis 金额取决于已供应 ribociclib 比例，未披露当前比例。

## 资料包问题

- `total_debt` 为空，但 10-Q 原文 "As of June 30, 2026, we had an outstanding liability of $3.0 million under the Credit Facility"。EV 少计约 300 万美元，不改变 EV 档位（<20 亿美元）。预览构建 gaps.csv 也记为 debt_not_reported。
- 自动下一事件（NCT06016738 PCD 2026-10-31，估算）已过时；公司已披露 2027Q1。
- 同名资产拆成 4 条推导管线（mBC phase1、Breast Cancer phase3、HR+ phase1_2、Metastatic phase1），阶段与 3 期一致的是 2073；substring "Breast Cancer" 已在预览构建中解析到 2073。
- ATIRMOCICLIB 被推导为 Olema 管线，实为 Pfizer 化合物（10-K："Pfizer’s proprietary investigative selective CDK4 inhibitor atirmociclib"），应从 OLMA 管线中删除。

## 用时

约 25 分钟。
