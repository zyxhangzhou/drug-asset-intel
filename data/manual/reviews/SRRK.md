# SRRK 复核报告（草稿，待人工签核）

**先看这一条：apitegromab 已于 2026-09-11 获 FDA 批准用于 SMA（ISEMBYLD）。包中 SMA 行仍标 phase3。** 按已上市计，SMA 方向只有 J&J #3 的阶段区间覆盖已上市，但其画像以精神科与神经退行性疾病为主，没有神经肌肉病的具体条目。因此本草稿选肥胖（肌肉保留）方向，交易形式为合作。签核人可改选 SMA / J&J #3，见下文「备选」。

## 推荐组合

- 资产 / 适应症：APITEGROMAB (SRK-015) / Overweight and Obesity（GLP-1 减重期间的瘦体重保留）。
- 买方：Novo Nordisk 第 3 治疗领域偏好（心血管-肾脏-代谢并发症），交易形式「合作」。
- 理由：Novo 画像点名「肌肉保留」（治疗领域第 3 位）。Novo 技术行第 3 位「FGF21、肌肉保留和代谢RNA」也点名，并要求「有组织学、心血管或体成分结局的中后期资产」。EMBRAZE 的主要终点是 DEXA 瘦体重，即体成分结局（MAN-SRRK-2）。公司在 10-K 与最新 10-Q 中写明正为该方向找合作方："seeking partners to further evaluate the potential for myostatin inhibition in combination with GLP-1 weight loss approaches"（SEC-0001193125-26-336732）。
- 分数：buyer_fit 4（中）、stage_match 4（中高）、clinical 3（中高，替代终点封顶）。catalyst 由 [event] 推导为 2（中 + 估算）。dealability 由 rights=full 与 EV 推导为 3（EV 约 49.7 亿美元，20–50 亿档）。预览构建通过，保守分 83.8。
- 组合冲突：10-K 竞争段只列 SMA 竞争者（"including Roche, Biogen, and NMD Pharma"）。没有打开 Novo 的文件。未核查组合冲突。
- 已知弱点（论点第二句的主要障碍写资金；以下两点放在 match_note）：
  1. EMBRAZE 的背景药是 Lilly 的 tirzepatide，不是 Novo 的 semaglutide。
  2. 公司写的合作对象是 "myostatin inhibition"，没有指名 apitegromab。皮下分子 SRK-439 也有肥胖临床前数据（10-K："we have explored SRK-439 in preclinical models of obesity"）。实际合作标的可能是 SRK-439。SRK-439 不在包中。
  3. 肥胖适应症在 24 个月窗口内没有事件。[event] 借用同一资产的 FSHD 2 期 FORGE（2028-06，估算），事件文本写明 FSHD。
- 备选：Pfizer #1（画像「……兼具减重、维持体重和肌肉保留」）。但该画像的主体是「口服非肽、胰淀素或双/三重激动剂」，肌肉保留是这些分子的附加属性，apitegromab 不属于这些分子类别，故次选。SMA / J&J #3：阶段 4 分；clinical 可到 4（SAPPHIRE 3 期 RCT，HFMSE 注册终点，对照为 SMN2 标准治疗）；buyer_fit 最多 3（SMA 是否属「神经退行性疾病」是推断）。AbbVie #2、Roche #2、Novartis #3 的理想阶段止于 3 期，已上市资产与之差两个阶段，stage_match 为 0。另外 Roche 在 10-K 竞争段被列为 SMA 抗 myostatin 竞争者，有组合冲突风险。

## 资产权益：full（事实）

- 10-K 原句："We have worldwide rights to our proprietary platform and to all of our product candidates."
- Gilead 合作已终止：期权期 "had been terminated as of January 6, 2022"。Janssen 许可（只涉及 GARP-TGFβ 专利族）"was terminated in July 2022"。
- 引进许可：
  - Adimab：行权产品需付 "a low-to-mid single-digit percentage of annual worldwide net sales" 的销售提成，以及每产品不超过 "mid-teen millions" 的里程碑款。10-K 只点名 SRK-181。apitegromab 是否受此协议约束：待核实。
  - Children's Medical Center 2013 年独家许可：只出现在 10-K 附件清单，正文未描述。是否涉及 apitegromab：待核实。
- 债务：Blue Owl 定期贷款，已提取 2 亿美元（"To date, the Company has received $ 200.0 million of Term Loans"），到期 2032-02-26。获批后另有不超过 1.5 亿美元的延迟提款额度，可用至 2027-09-30。包中 total_debt 为 1.962 亿美元，与之相符。
- 资金指引原句（10-Q）："will enable us to fund our operating expenses and capital expenditure requirements into the second half of 2027"。包中推算为约 19 个月。另有新的 2 亿美元 ATM（MAN-SRRK-5）。

## 待核实

1. Novo 是否已持有同机制（myostatin / activin 通路）的肌肉保留资产。没有打开 Novo 的文件。
2. 合作标的：公司寻求的是 apitegromab 还是 SRK-439（文件写 "myostatin inhibition"）。
3. Adimab 协议与 Children's Medical Center 许可是否涉及 apitegromab，以及对应的销售提成与里程碑义务。
4. FORGE 读出时间：公司未披露。2028-06 是 CT.gov 预计主要完成日，读出时间为推断。
5. EMA MAA / CHMP 意见时间：公司称将 "provide updated guidance on timelines"，目前未披露。若披露，可作为 SMA 方向的高重要性事件。
6. EMBRAZE 全文或会议摘要：只读到顶线新闻稿，分析人群为完成者。
7. Q3 2026 10-Q 尚未发布。现金与债务按 2026-06-30。

## 包数据问题

- SMA 行（id 285）阶段错误：包标 phase3，来源是 OLE NCT05626855。实际已上市（BLA761463，2026-09-11；MAN-SRRK-4）。自动配对把 ONYX 长期扩展研究（开放标签）的主要完成日当作「phase3 高重要性事件」，这不对。AbbVie #2 / Roche #2 / Novartis #3 自动配对的 stage_match 4 应为 0。
- 「ANTI-PD- 1 ANTIBODY THERAPY」不是公司资产。它是从 SRK-181 联用试验标题里拆出的名称。BMS #1、GSK #1 两个自动配对应删除。SRK-181 本身只是 1 期完成，公司在为它找合作方，不自行推进。
- 「SMA」行（id 284）是扩展使用项目（EAP），阶段 unknown，应并入 SMA 或删除。
- 缺少 SRK-439（皮下抗 myostatin，1 期健康志愿者，顶线 "anticipated in late 2026"，MAN-SRRK-3）。
- SAPPHIRE 数据：批准新闻稿把 10 mg/kg 的 p 值标为 "nominal"。如改选 SMA 方向，需要先在 10-K 中确认主要分析的定义。

## 用时

约 35 分钟。
