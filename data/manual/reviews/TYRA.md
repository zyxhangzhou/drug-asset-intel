# TYRA（Tyra Biosciences）复核草稿报告

## 推荐组合

- 资产 / 适应症：dabogratinib（TYRA-300，口服 FGFR3 选择性小分子）/ FGFR3 突变低级别中危非肌层浸润性膀胱癌（LG IR NMIBC），2 期 SURF302。
- 买方：Pfizer，治疗领域偏好第 2（肿瘤，ideal_stage「Phase 2b-注册期」）。
- 交易形式：收购。
- 分数：buyer_fit 4（中）、stage_match 4（高）、clinical 2（高）。catalyst 与 dealability 由 build 推导。预览构建结果：catalyst 3、dealability 4、rights full、保守分 86.2、覆盖率 1.0。

选择理由：

- dabogratinib 是公司唯一的核心资产（"dabogratinib 3x3" 策略：LG-UTUC、IR NMIBC、ACH）。NMIBC 是唯一已有 2 期疗效数据的适应症（2026-09-09 8-K）。
- 买方选 Pfizer #2。它是唯一同时点名模式（「靶向小分子」）和器官（「泌尿」）的治疗领域画像行。
- 不选自动初筛主组合 Merck #1。Merck 画像只点名肺癌、胃肠癌、妇科癌和血液肿瘤，没有泌尿系肿瘤。
- 排除 J&J #1（自动初筛列为备选）。原因是同机制、同适应症的组合冲突，10-K 原文："Johnson & Johnson has initiated a Phase 3 trial for TAR-210 in low grade IR NMIBC patients"。TAR-210 是 erdafitinib（FGFR 抑制剂）膀胱内释放装置，J&J 另有已上市的 Balversa。按 §3.1，J&J 应为 0 分。
- 备选：GSK #1（「已验证靶点小分子」）。它没有点名泌尿系肿瘤，最多 3 分。
- 不选 ACH / AstraZeneca #2（罕见病，「遗传性疾病药物」）。原因：BEACH301 还没有疗效数据，首批数据预计 2027 年第一季度末。读出后可重新评估这一组合。

## 资产权益

- 状态：full（事实）。
- 10-K 原句："all of which are solely owned by us. We do not license any material patent rights from any third party."（MAN-TYRA-1）
- 10-K 原句："We currently solely own intellectual property covering our product candidates."（MAN-TYRA-1）
- 10-Q 原句："we have built a wholly-owned pipeline of oral small molecule product candidates"（SEC-0001193125-26-332995）
- 未见对外授权、选择权、合作或引进许可，因此没有应付的特许权使用费或里程碑（推断，中高）。10-K 全文检索 "right of first"、"co-develop"、"co-commerciali" 无结果，"option agreement" 只出现在股票期权计划中。
- 专利到期时间："expected to expire on dates ranging from 2040 to 2046"（10-K）。
- 债务：无借款。10-Q 资产负债表的负债只有应付账款、租赁负债和应计费用，总负债 29.7 百万美元。
- 资金指引：10-Q 原句："will be sufficient to fund our operating expenses and capital expenditures into the second half of 2028"。
- 这条指引早于 2026-09-14 定价的约 4 亿美元增发（MAN-TYRA-4）。另有 ATM 额度 2.5 亿美元（MAN-TYRA-3）。

## 下一事件

- 选定：BEACH301（ACH）安全哨兵队列 2 期初步数据，2027 年第一季度末，明确披露。重要性 medium，确定性 disclosed。
- 这一事件属于同一资产的另一个适应症，事件文本已写明 achondroplasia。
- NMIBC 注册性辅助治疗研究的启动只披露了「2027」，没有季度，所以不作计分事件。
- SURF303（LG-UTUC）初步结果也只披露了「2027」，同样不作计分事件。
- 自动初筛的事件「NCT06995677 主要终点 2028-02（估算）」已用公司披露覆盖。

## 待核实

1. 组合冲突：只按 Tyra 10-K 竞争段核查，该段没有出现 Pfizer。Pfizer 自身在 NMIBC 或 FGFR 方向的在研资产，没有打开来源核查。
2. SURF302 是中期数据，公司没有声明主要终点（3 个月 CR 率）达到，也没有披露预设阈值。只有 8-K 正文，没有会议摘要或论文。
3. 3 期辅助治疗研究的设计和剂量须等 FDA 反馈（"subject to that feedback"）。启动时间只到年份。
4. 2026 年第三季度 10-Q 尚未提交（截至 2026-10-30），9 月增发后的现金和股本未核实。
5. TAR-210 的「90% CR rate」只引用自 Tyra 10-K，没有打开 J&J 一手来源。

## Pack 问题

- 财务数据过时：截至 2026-06-30 的现金 353.9 百万美元和 59.68M 股，没有包含 2026-09-15 交割的增发。该次增发为 9,079,000 股加 9,078,529 份预融资认股权证，总额约 4 亿美元。
- 因此快照市值（按旧股数）和现金都偏低。现金增加与市值增加大致抵消，EV 仍远低于 20 亿美元，可交易性档位不变（推断）。
- 「TYRA-300 (DABOGRATINIB) / Locally Advanced Urothelial Carcinoma」（SURF301）对应的转移性尿路上皮癌不再开发。10-K 原文："no further development is planned at this time"。
- 「TYRA-300 KG」（ACH）、「PHASE 1 PART A/B … TYRA-200 …」是试验组名解析错误。TYRA-200 两行的 therapeutic_area 为 null。
- J&J #1 的 auto_pair buyer_fit 应为 0（组合冲突，见上）。
- 适应症「Low-grade NMIBC」准确，阶段 phase2 与公司披露一致。

## 用时

约 25 分钟。
