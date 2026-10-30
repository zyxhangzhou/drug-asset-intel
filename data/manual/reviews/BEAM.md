# BEAM（Beam Therapeutics）复核草稿报告

## 选定组合

- 资产 / 适应症：BEAM-302 / α1-抗胰蛋白酶缺乏症（AATD）。TOML 中 `program = "BEAM-302"`、`indication = "Alpha 1-Antitrypsin Deficiency"`，匹配数据包 id 474（phase1_2，NCT06389877）。
- 买方：AstraZeneca #2（罕见病，「基因疗法、体内细胞疗法、补体/酶替代和遗传性疾病药物」，理想阶段「早期平台至Phase 3」）。deal_form = 收购。
- 分数：buyer_fit 4（中）、stage_match 4（高）、clinical 2（中高）；catalyst 由 [event] 推出（高 × 估算 = 3）；dealability 由 [rights] = full 与 EV 推出。

### 为什么选 BEAM-302 + AstraZeneca #2

- 公司定位：Q2 2026 新闻稿（MAN-BEAM-2）称 BEAM-302 为 "Beam’s lead genetic disease program"。
- 10-Q：体内 LNP 碱基编辑、一次性纠正 E342K；FDA 同意以 12 个月 AAT 生物标志物为主要终点的加速批准路径；"In July of 2026, we dosed the first patient in the pivotal cohort."
- AstraZeneca #2 的画像文字直接点名「基因疗法」「遗传性疾病药物」，不是标签匹配。AZ 技术类型偏好 #2（基因疗法与体内 CAR-NK，「递送和制造优势明显」）也一致。
- 10-K 的 AATD 竞争公司名单（Wave、YolTech、Prime、CRISPR、Moderna、Korro、Tessera、Arrowhead）不含 AstraZeneca。

### 为什么不选 risto-cel（BEAM-101，镰状细胞病）

- 它是离体自体造血干细胞疗法（需 busulfan 预处理），AZ #2 画像写的是「体内细胞疗法」；其他买方画像没有点名 SCD 或离体基因编辑。
- Sixth Street 信贷对 risto-cel 有专门限制："The Company is subject to restrictions on sales and licensing transactions with respect to its core intellectual property, including risto-cel"（10-Q）。
- 它的催化剂更强（10-Q："expect to submit a biologics license application, or BLA, for risto-cel as early as year-end 2026"），签核人如更看重近期催化可改选，但需另找买方需求条目。

## 权益状态（BEAM-302）：full（推断，置信度中）

- 10-K / 10-Q **没有**「BEAM-302 为全资资产」的原句。判断依据是合作披露的穷尽：10-K「Collaborations」一节列出 Pfizer、Apellis、Verve/Lilly、Orbital/BMS、Prime，均不涉及 BEAM-302 或 AATD；10-Q 由公司自己开展 1/2 期与关键性队列。
- 关键句（10-Q）："We are party to a license agreement with Pfizer Inc., or Pfizer, granting Pfizer an exclusive, worldwide license to a liver-targeted development candidate that employs our proprietary LNP to deliver base editing reagents. Under the terms of the license, Pfizer is responsible for all development activities…"。Pfizer 候选物的靶点未披露；因 BEAM-302 由 Beam 自己开发，判断它不是 BEAM-302。**签核人请确认。**
- 对第三方的义务：
  - 和解协议（10-Q）："make additional payments contingent upon the development and commercialization of BEAM-102 and BEAM-302"，含 "1 % royalty on net sales through 2038"，开发/监管里程碑上限 1,500 万美元、销售里程碑每项目上限 3,500 万美元。
  - Editas 许可（10-K）：转付 Broad/Harvard/MGH 上游费率，另加 "low- to mid-single digit royalty on net sales of licensed products"；每产品里程碑最高 6,880 万美元。是否覆盖 BEAM-302 待核实。
  - Harvard / Broad 成功付款：按股价倍数触发，各自 "up to an additional $ 90.0 million"（收购溢价可能触发）。
- 交易障碍（不改变权益状态）：Sixth Street 信贷，"secured on a first-priority basis … including its intellectual property"；限制 "effectuate mergers or consolidations, engage in asset sales and licensing transactions"；违约事件含 "change of control"。

## 资金

- Q2 2026 新闻稿（MAN-BEAM-2）原句："Beam expects that its cash, cash equivalents and marketable securities as of June 30, 2026, together with an additional $200 million expected to be drawn from the company’s facility with Sixth Street, will fund anticipated operating expenses and capital expenditure requirements into mid-2029"。
- 10-Q 只写 "will be sufficient to fund its operations for at least the next 12 months"。数据包 runway 37 个月与公司指引（含未提取的 2 亿美元）口径不同。

## 待核实

1. BEAM-302 的全球权益：没有「全资」原句，依据是合作披露的穷尽（见上）；Pfizer 候选物的靶点。
2. AstraZeneca 是否已有 AATD 资产（未核查组合冲突；10-K 名单不含 AZ，但不是完整核查）。
3. 临床意义阈值：AAT 保护水平（如 11 µM）没有找到可打开的来源，所以 clinical 定为 2 而非 3。
4. 2026-09 ERS 更新数据（公司 IR 新闻稿 HTTP 403，未打开；没有对应的 8-K）。本报告的临床数据截止 2026-02-10。
5. 关键性队列读出或 BLA 提交时间：公司文件未给，[event] 只用 CT.gov 估算 2028-05。
6. Editas 特许权使用费是否适用于 BEAM-302。
7. 2026-03 topline 新闻稿与 ATS 2026 新闻稿（IR PDF 403，未打开）。

## 数据包问题

- BEAM-101 已更名 ristoglogene autogetemcel（risto-cel）；BLA 预计最早 2026 年末提交，数据包看不到。
- BEAM-201（T-ALL/T-LL）：10-K 与最新 10-Q 都没有提及 BEAM-201，数据包仍按 phase1_2 列为在研程序，疑似已停止推进（待核实）。
- 程序名「BEAM-301 SINGLE OF BEAM-301 ADMINISTERED BY」是解析错误，应为 BEAM-301（GSDIa）。
- BEAM-304（PKU）IND 已获批（2026-06），数据包未收录（尚无 CT.gov 登记可能是原因）。
- BEAM-302 的 1/2 期包含关键性扩展队列，CT.gov 阶段 phase1_2 不反映这一点。
- total_debt 1.003 亿美元为 Sixth Street 首笔提款；公司预计 BLA 受理后再提 1 亿美元（Delayed Draw A）。

## 用时

约 30 分钟。
