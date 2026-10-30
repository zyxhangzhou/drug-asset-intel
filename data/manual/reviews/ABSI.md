# ABSI（Absci Corporation）复核草稿报告

## 选定组合

- 资产 / 适应症：ABS-201（抗 PRLR 长效单抗）/ 雄激素性脱发（Androgenetic Alopecia；公司文件现称 pattern hair loss, PHL）。TOML 用 `program = "ABS201 SINGLE"`（推导管线 1816，挂 NCT07317544），阶段 1/2a 期。
- 买方：Novartis，偏好第 2 位（免疫，理想阶段 Phase 1-3），deal_form = 许可。
- 评分：buyer_fit 2（中），stage_match 4（高），clinical 1（高）；event 中等重要性、明确披露（2026H2）；rights full（推断，中）。

### 为什么选 Novartis #2

- 画像（NVS-3）原文"过敏、哮喘、皮炎和自身免疫的抗体或免疫调节剂，强调长效及生物标志物分层"。ABS-201 是长效抗体（"engineered with an extended half-life"；1 期半衰期"at least 65 days"），技术类型对上。
- 适应症对不上：脱发不是过敏、哮喘、皮炎或自身免疫疾病。所以 buyer_fit 只给 2。人工若认为脱发不属免疫领域，可降为 1。
- 阶段：Novartis #2 理想区间 phase1–phase3，1/2a 期落在区间内，得 4。
- 备选：BMS #2（Phase 1b-3）画像限定自身免疫，匹配更差；AbbVie #1 写明"长效抗体……皮炎"，但理想阶段 Phase 2-3，阶段只得 2。
- 第二适应症子宫内膜异位症不在任何买方的治疗领域偏好内。
- 10-K 竞品清单（PHL：HMI-115、VDPHL01、PP405、Clascoterone；子宫内膜异位症：HMI-115、Chugai AMY-109、GenSci Genakumab）未列 Novartis 产品。不能作为否定证据：未核查组合冲突。
- Eli Lilly 有 4,000 万美元战略股权投资，但 Lilly 不在 10 家买方中，且"does not confer any program rights to Eli Lilly"（MAN-ABSI-2）。

## 权益状态：full（推断，置信度中）

- 10-K 与 10-Q 都没有"拥有 ABS-201 全球权益"的明确句子。
- 10-K 原句（MAN-ABSI-1）："We intend to advance a limited number of internally developed programs, such as ABS-201, through clinical development and potential commercialization."
- 10-K Item 15 附件清单无任何许可、合作或期权协议；引进许可只在风险因素中以将来时出现："We may come to rely on in-licenses from third parties"。
- Merck、AstraZeneca、Almirall 合作属于平台"Partnered Programs"，文中未与 ABS-201 关联。
- Lilly 股权投资不含项目权利（Q2 新闻稿，MAN-ABSI-2；10-Q 正文未提 Lilly）。
- 未见对许可方的里程碑或特许权使用费义务。
- 人工签核时请确认：是否接受以"内部开发 + 无许可协议附件"推断 full；若不接受，应改为 unverified（会挡在入选名单外）。

## 下一事件

- HEADLINE MAD（脱发患者）中期概念验证数据，含探索性疗效终点，2026 年下半年，明确披露（10-Q 与 MAN-ABSI-2）。完整 PoC 数据"early 2027"。
- EDGAR 上 2026-08-11 之后没有新的 8-K；截至 2026-10-30 中期数据尚未发布。
- 重要性定为 medium（1/2a 期中的随机安慰剂对照 PoC 部分）。疗效终点为探索性，不做多重性校正；人工若按"1 期数据"处理，应降为 low（catalyst 3 → 1）。
- 同资产其他适应症：子宫内膜异位症 2 期"in the fourth quarter of 2026"启动，PoC"potential … in the second half of 2027"（MAN-ABSI-2）。
- Q2 新闻稿前瞻声明提到"the possibility of advancing directly from Phase 1/2a into Phase 3"，仅为可能性，未计入。

## 财务

- 债务：pack `total_debt` 为空；10-Q 资产负债表流动负债 "Long-term debt | 150"（千美元），来自设备融资 MFA。金额可忽略，不改变 EV 档位（EV 约 18.4 亿美元，< 20 亿）。
- 现金跑道：pack 为 22.4 个月。10-Q 原文 "sufficient to meet our operating expenses, working capital and capital expenditure needs over at least the next 12 months following the date of this filing"；Q2 新闻稿原文 "sufficient to fund its operating plans into the second half of 2028"。

## 待核实

- ABS-201 全球权益：无明确肯定句，以推断给 full。
- Novartis 是否持有抗 PRLR 或脱发资产：未核查组合冲突。
- 中期 PoC 数据是否已在 2026 年 10 月发布（只查了 EDGAR 8-K 列表，未查公司 IR 页面）。
- HEADLINE MAD 队列的疗效终点定义（目标区域毛发计数）与样本量仅取自 10-K 描述，未与 CT.gov 记录逐字核对。
- AAD / EADV 2026 摘要原文未打开（均为临床前数据，不影响评分）。

## 资料包问题

- 推导管线名是 CT.gov 组别标签（"ABS-201 MULTIPLE DOSES"、"SAD 1 - ABS201 SINGLE"），应合并为 ABS-201。"ABS-201"（带连字符）只匹配 1815，该条无试验；故 TOML 用 "ABS201 SINGLE" 指向 1816。
- 缺子宫内膜异位症适应症（2 期计划 2026Q4 启动，尚无 CT.gov 登记，pack 中看不到）。
- 治疗领域标为 immunology：脱发更接近皮肤科，免疫归类本身偏宽，影响自动配对。
- ABS-101（抗 TL1A，IBD）已不再自行推进，10-K 原文 "we will seek a partner for ABS-101 rather than advance it through later-stage development ourselves"；pack 中没有该资产，正确。

## 用时

约 25 分钟。
