# CGEM（Cullinan Therapeutics）复核草稿报告

## 推荐组合

- 资产 / 适应症：CLN-978（CD19xCD3 T 细胞衔接器，皮下给药）/ 系统性红斑狼疮（SLE），全球 1 期 OUTRACE SLE。
- 买方：Bristol Myers Squibb，治疗领域偏好第 2（免疫炎症，ideal_stage「Phase 1b-3」）。
- 交易形式：收购。
- 分数：buyer_fit 4（中）、stage_match 4（高）、clinical 2（高）。catalyst 与 dealability 由 build 推导。预览构建结果：catalyst 1、dealability 4、rights full、保守分 78.8。

选择理由：

- 公司战略重心是自免 T 细胞衔接器。10-Q 原文："developing potential first- or best-in-class, disease-modifying T cell engagers for autoimmune diseases and cancer"。CLN-978 是自研、全资资产，权益最干净。
- 适应症选 SLE，不选 RA。SLE 数据更多：14 例中 5 例 DORIS 缓解。RA 只有 7 例，1–2 例 DAS28-ESR 缓解。公司也计划 2027 年初在 SLE 与狼疮肾炎启动 2 期扩展。
- 买方选 BMS #2。画像中的「免疫重置」「持久缓解」「风湿病」与公司表述对应："including indicators of immune reset"、"durable, treatment-free remissions"（MAN-CGEM-2）。
- 不选 Novartis #2。10-K 竞争段把 Novartis 列为有自免 CD19 TCE 项目的公司，构成同机制冲突。同一名单还有 Roche、AstraZeneca、Merck、GSK。BMS 不在名单中。
- 不选 J&J #2（画像含「自身抗体清除」）。J&J 的 ideal_stage 为 Phase 2-3，1 期只能得 2 分。
- 不选 velinotamig。它从 Genrix 引进（只有大中华区以外权益），须付最高 2.92 亿美元开发 / 监管里程碑、4 亿美元销售里程碑和中个位数至十几的分级特许权使用费。SLE 试验由 Genrix 在中国进行，pack 中没有。pack 只有尚未启动的 ITP 篮式试验。
- 不选 zipalertinib（CLN-081），尽管它阶段最晚：NDA 已受理，PDUFA 2027-02-27；REZILIENT3 3 期阳性。原因是 Taiho 持有知识产权，Cullinan 只分享美国利润 50%，权益受限。J&J 已有获批的 EGFR ex20ins 药物（10-K 竞争段）。

## 资产权益

- 状态：full（事实）。
- 10-Q 原句："We hold worldwide intellectual property rights for CLN-978."（SEC-0001193125-26-336717）
- 10-K 原句："We hold the worldwide intellectual property rights for CLN-978."（SEC-0001193125-26-099362）
- 新闻稿："CLN-978 was developed by an internal Cullinan team and is a wholly owned asset."（MAN-CGEM-1）
- 10-K 许可段未见 CLN-978 的引进或对外许可，因此无特许权使用费 / 里程碑义务（推断，中高）。
- 专利仍为申请："which, if issued, are expected to expire in 2040"。
- 债务：pack 的 total_debt 为空。10-Q 资产负债表负债只有应付账款、应计费用和经营租赁负债，未见借款。
- 整体收购时的公司层面负担：
  - zipalertinib：Taiho 持有知识产权，美国利润五五分成。
  - CLN-049：放在持股 98% 的子公司中，10-K 提到少数股东的 "drag-along rights"。
- 资金：pack runway 为 22.8 个月。Q2 新闻稿给的指引是 "runway into 2029"（MAN-CGEM-3）。10-Q 只有 12 个月持续经营的套话。另有 2 亿美元 ATM，截至 6 月 30 日未使用："We made no sales under the ATM through June 30, 2026."

## 待核实

1. 组合冲突：只按 Cullinan 10-K 竞争段核查。BMS 自己的 CD19 细胞疗法（如 CAR-T）是否已在 SLE 开发，没有打开来源核查。若属实，同靶点、同适应症，buyer_fit 可能需降到 3 或以下。
2. 「免疫重置」「持久缓解」是公司基于 1 期单次目标剂量数据的表述。EULAR 海报原文（POS1179）未打开。
3. RA 多剂量数据：Q2 新闻稿计划在 2026 年第三季度发布，9 月 24 日新闻稿改为 12 月与 SLE、SjD 一起发布，时间延后。
4. 2 期扩展启动只披露了「early 2027」。它不是关键性试验，未作为主事件。
5. 未查 Q3 2026 10-Q（截至 2026-10-30 尚未提交）。
6. 事件重要性为 low（1 期数据），catalyst 只有 1 分。窗口内没有更高级别的 CLN-978 事件。

## Pack 问题

- velinotamig 的程序名是「VELINOTAMIG SPECIFIED ON SPECIFIED DAYS」，是解析错误。
- SLE、NHL 两行的 therapeutic_area 为 null。预览构建时 SLE 仍可匹配，不影响构建。
- RA 适应症字符串被截断（「Rheumatoid Arthritis (RA」）。
- CLN-081（zipalertinib）在 pack 中为 phase1_2。实际 NDA 已受理（PDUFA 2027-02-27），一线 REZILIENT3 3 期已在中期分析达到主要终点，一线 NDA 已按 RTOR 启动提交（8-K 2026-08-12、2026-10-02）。
- CLN-619、CLN-617 已于 2025 年 11 月停止开发（10-Q："we discontinued further development of CLN-619"），但 pack 中 CLN-619 的试验仍为 ACTIVE_NOT_RECRUITING。
- CLN-049 的潜在注册性 2 期（R/R AML）计划于 2026 年第三季度启动，pack 中不可见。CLN-049 的 auto_pair 只到 1 期，而且资产在子公司中，属噪声。
- 自动初筛主组合为 CLN-978 / RA / BMS #2。本复核把适应症改为 SLE。

## 用时

约 30 分钟。
