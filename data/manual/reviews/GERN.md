# GERN（Geron Corporation）复核草稿报告

## 选定组合

- 资产：imetelstat（RYTELO）。适应症：输血依赖的低危骨髓增生异常综合征（LR-MDS），pack 中匹配 `Myelodysplastic Syndromes`。
- 买方：AbbVie，偏好第 3 位（肿瘤，理想阶段「Phase 2-3或上市」）。交易形式：收购。
- 分数：buyer_fit 2，stage_match 4，clinical 3。catalyst 由 [event] 推导，预计为 1（低 / 估算）。dealability 由 [rights] 推导（full，EV 约 4.17 亿美元）。

### 为什么选已获批适应症，不选骨髓纤维化

- imetelstat 已获 FDA 批准用于 LR-MDS：Drugs@FDA NDA217779 原始申请 2024-06-06 批准（MAN-GERN-5）。EC 于 2025-03 批准（MAN-GERN-1）。
- 骨髓纤维化扩展已失败：2026-10-28 的 8-K 宣布停止 3 期 IMpactMF，原文 "the trial was unlikely to meet its primary endpoint of overall survival"（MAN-GERN-2）。
- 所以能推荐的只剩已获批的 LR-MDS 适应症。骨髓纤维化不能作为后期扩展来推荐。

### 为什么选 AbbVie #3

- 只有 AbbVie #3 这一行治疗领域偏好的阶段区间包含「已上市」，stage_match 得 4 分。
- 备选是 Merck #1。它的画像明确写了「血液肿瘤…新标准治疗」，但理想阶段上限是注册期，已上市资产只得 2 分。其他血液瘤买方的上限是 Phase 3，得 0 分。
- buyer_fit 只给 2 分。原因是 imetelstat 为静脉给药的寡核苷酸，不属于 AbbVie 的 ADC、抗体或靶向小分子偏好。
- 「可扩适应症」这一要求因 IMpactMF 停止而变弱。
- 我读了 10-K 的竞争段落，没有看到 AbbVie 的同类资产，但没有读 AbbVie 自己的管线。因此记为「未核查组合冲突」。

## 权益状态：full

10-K（MAN-GERN-1，2026-03-02）原文：

> "We have no material license agreements. We have global rights to imetelstat, which was discovered and developed at Geron."
> "There are no other royalties payable on RYTELO, which was developed internally and is exclusively owned by Geron."

与 Janssen 的合作于 2018 年终止，原文："without any economic obligations to Janssen with respect to such license"。

需要承担的义务：

- **Royalty Pharma**：按美国净销售收取 7.75% / 3.0% / 1.0% 的分成，上限为 1.25 亿美元的 1.65 倍或 2.0 倍。控制权变更时可一次性清偿。该协议限制 IP 转让和对外许可，所以选收购而不选许可。
- **Pharmakon 贷款**：1.25 亿美元，2029-11-01 到期。
- **欧盟商业化**：公司计划找第三方合作，2026 Q2 10-Q 没有披露已签协议。

## 待核实

1. 2026 Q2 10-Q 写有 "certain in-license agreements that require us to pay milestones"。它与 10-K 的 "no material license agreements" 是什么关系，需要人工确认。
2. 低危 MDS 适应症在 24 个月内没有找到公司披露了时间的事件。[event] 只用了 IMproveMF 1 期的 CT.gov 估算日期（2027-02）。IMpactMF 停止后 IMproveMF 是否继续，公司没有说明。
3. AbbVie 是否已有同机制、同适应症的资产：未核查。
4. 没有 imetelstat 与 luspatercept 的直接比较数据，因此 clinical 维持 3 分。
5. IMpactMF 的详细数据，公司只说 "at a future date" 公布，没有日期。
6. Royalty Pharma 的累计已付金额（关系到收购时的清偿成本）没有从文件中取到。

## Pack 的问题

- pack 中的 8 条 auto_pairs 全部以骨髓纤维化 NCT04576156（3 期，估算 2028-06-30）为依据。该试验已于 2026-10-28 停止，这些组合与 catalyst 3 分已经失效。
- pack 把 `Myelodysplastic Syndromes` 的阶段记为 `phase2_3`，实际已上市（NDA217779，2024-06-06 获批）。
- `Myelofibrosis` 的阶段仍记为 `phase3`，应在下次重建时反映试验已停止。CT.gov 状态可能还没有更新。
- 资产名称没有问题，"imetelstat" 可以匹配。

## 用时

约 25 分钟。
