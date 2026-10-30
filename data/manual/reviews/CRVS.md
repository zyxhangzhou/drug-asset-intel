# CRVS 复核草稿报告

## 组合

- 资产 / 适应症：SOQUELITINIB (CPI-818) / Atopic Dermatitis（AD 2 期）。
- 买方：Novartis #2（免疫，ideal_stage Phase 1-3），交易形式：收购。
- 选择理由：Novartis #2 的 target_profile 写明「过敏、哮喘、皮炎和自身免疫的抗体或免疫调节剂…生物标志物」。soquelitinib 是口服 ITK 免疫调节剂，AD 2 期在入组，哮喘 2 期在计划中，1 期有 IL-4 / IL-5 / Treg 标志物数据。画像中的「长效」不符（每日口服）。
- 未选自动主推（Merck #1 / PTCL）：该配对只在标签层面匹配。PTCL 1/1b 的 9/24 缓解率来自事后筛选的亚组（"it was determined that patients with between ≥1 and ≤3 prior therapies ... were most likely to be responders"）。BMS #1（淋巴瘤新靶点）是备选。
- 组合冲突：只按 10-K 竞争段核查。AD 竞品公司为 "Abbvie, Pfizer, Sanofi, Amgen, GSK and Lilly"，不含 Novartis。未核查 Novartis 自身早期管线。

## 分数

| 维度 | 分 | 置信度 |
|---|---|---|
| buyer_fit | 4 | 中 |
| stage_match | 4 | 高 |
| clinical | 2 | 高（1 期随机安慰剂对照，n=12 对 10，p=0.035） |
| catalyst（由 [event] 推导） | 高 / 估算 → 预计 3 | — |
| dealability（由 [rights] 推导） | partial → 最高 3 | — |

[event] 用同一资产的 PTCL 3 期主要终点数据（CT.gov NCT06561048 预计主要完成 2027-11，估算）。事件文本写明了 PTCL。AD 2 期 SIERRA1 读出（CT.gov NCT07441395 预计 2027-06，中 / 估算）写在事件文本中作参考。PTCL 中期无效性分析时间为 "sometime in early 2027"，没有季度，所以不算明确披露。

## 权益

- 状态：partial（大中华区已授权给 Angel Pharmaceuticals）。
- 10-Q（2026-08-06）与 10-K 原句："Except for Greater China, we own the world-wide rights to these product candidates."
- 10-K 原句："We have issued patents covering composition of matter and uses of our ITK inhibitors and hold exclusive worldwide rights (except for greater China) for all indications."
- 区域：10-Q 原文 "for distribution within the countries of China, Taiwan, Macao, and Hong Kong"。Angel 由 Corvus 持股约 48.6%（不含 ESOP 预留）。
- 10-K 与 10-Q 中未检索到 ROFN、option、co-commercialization、profit share。
- 引进许可：soquelitinib 无。10-Q 附注 7 只列 Vernalis（ciforadenant）、Scripps（抗 CD73）、Monash（CXCR2）。
- 债务：10-Q 中未检索到借款或票据。ATM 余额 2 亿美元未使用。
- 资金：10-Q 原文 "we expect that our cash resources will be sufficient to enable us to advance our programs into the second quarter of 2028"。Pack 的 runway_months 为 50.1 个月，比公司指引（约 21–24 个月，到 2028 年第 2 季度）长得多。推断原因：pack 用 2026 年上半年经营现金流 -2,577 万美元外推，公司指引包含 3 期、2 期及新试验启动后增加的支出。

## 待核实

1. SID 2026 会议摘要（AD 1 期最终数据）本次未打开。临床数值只引用 10-Q 的公司表述。
2. NCT07441395 是否就是 SIERRA1：按标题、阶段、状态推断，未打开 CT.gov 记录核对。
3. Novartis 自身管线中是否有 ITK 或同类口服 T 细胞调节剂（组合冲突未全面核查）。
4. 2026-06-30 时点未行权的预融资认股权证数量。10-Q 封面普通股为 84,120,944 股，但二季度基本加权股数为 92,368,013 股（"common shares and pre-funded warrants"）。Pack 的市值只按封面股数计算，可能低估约 9%。EV 档位（<20 亿美元）不变。
5. Angel 许可对 Corvus 的经济条款（特许权使用费或里程碑）及收购时的处理方式。10-K / 10-Q 中未找到。

## Pack 问题

- "CPI-006" 即 mupadolimab，pack 未写资产名。"CPI-006 CIFORADENANT" 是没有试验的派生条目（合并试验拆分产生）。
- 缺少的试验：Angel 在中国开展的 AD 1b/2 期、NIAID 的 ALPS 2 期、计划中的哮喘 2 期。
- ciforadenant RCC：10-Q 原文 "No further trials are planned"。Pack 仍把它列为 1 期在研。
- 校验工具 `tools/preview_build.py` 运行失败：报 ALT.toml "unregistered source id(s) MAN-ALT-1 … MAN-ALT-6"，加或不加 `CRVS` 参数都失败。原因未查，与 CRVS 无关。CRVS.toml 已通过 tomllib 解析，所有英文引文已在源文中程序化检索确认。

## 用时

约 25 分钟。
