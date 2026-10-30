# CGON（CG Oncology）复核草稿报告

## 推荐组合

- 资产 / 适应症：cretostimogene grenadenorepvec（CG0070，膀胱内给药溶瘤腺病毒免疫疗法）/ Non Muscle Invasive Bladder Cancer（pack 程序 id 227）。
- 阶段：单臂 3 期 BOND-003 Cohort C 已发表（Lancet Oncology 2026）；BLA 滚动提交中，公司预计 2026 年第四季度完成（SEC-0001193125-26-336918、MAN-CGON-2）。
- 买方：Pfizer，治疗领域偏好第 2（肿瘤，ideal_stage「Phase 2b-注册期」）。
- 交易形式：收购（权益为 partial，与收购兼容）。
- 分数：buyer_fit 3（中）、stage_match 4（高）、clinical 3（中高）。catalyst 与 dealability 由 build 推导：事件为 high / disclosed，预期 catalyst 4；EV 约 46.4 亿美元（20–50 亿档），权益 partial，预期 dealability 3。

选择理由：

- 买方选 Pfizer #2。它的画像点名「泌尿」肿瘤：\"覆盖乳腺、肺癌、泌尿和血液肿瘤\"（PFE-1、PFE-3）。ideal_stage 上限到「注册期」，BLA 提交完成后阶段分仍为 4。
- buyer_fit 只给 3，不给 4。原因一：画像技术类型（ADC、双抗、靶向小分子、放射性药物）不含溶瘤病毒。原因二：10-K 把 Pfizer 列为 NMIBC 开发者（\"including ... Pfizer, Inc.\"，MAN-CGON-1），但未写机制；Pfizer 自身文件未打开，组合冲突未核查。
- 不选自动初筛的 Merck #1。Merck 画像点名肺癌、胃肠癌、妇科癌、血液肿瘤，未点名膀胱 / 泌尿。10-K 写明 Merck 的 pembrolizumab 已获批同一适应症（\"pembrolizumab, sold by Merck, was approved by the FDA to treat high-risk BCG-unresponsive NMIBC\"），且 Merck 是 BCG 唯一主要供应商。机制不同，但属同适应症已有资产。
- 不选 J&J #1。10-K 写明 J&J 的 TAR-200 已获批同一适应症，CR 82%（MAN-CGON-1）；画像也未点名泌尿。
- BMS、Roche 同样在 10-K 的 NMIBC 开发者名单中，画像未点名泌尿。
- 备选（未打分）：GSK #1。画像点名「实体瘤的……免疫肿瘤资产」，GSK 不在 10-K 的 NMIBC 开发者名单中。缺点：ideal_stage「Phase 2-3」，BLA 提交完成（预计 2026Q4）后阶段分降为 2。复核人若重视组合冲突，可改选 GSK #1，buyer_fit 3。

## 资产权益

- 状态：partial（部分）。
- 10-Q 原句（SEC-0001193125-26-336918）：
  - Lepu：\"granted to Lepu an exclusive license to develop, manufacture and commercialize cretostimogene and/or n-Dodecyl-beta-Maltoside (DDM) to treat and/or prevent cancer in mainland China, including Hong Kong and Macau (the Lepu Territory)\"。
  - Kissei：\"granted to Kissei an exclusive license to certain intellectual property rights in Bangladesh, Bhutan, Brunei, Cambodia, India, Indonesia, Japan, South Korea, Laos, Malaysia, Myanmar, Nepal, Pakistan, Palau, Philippines, Singapore, Sri Lanka, Taiwan, Thailand and Vietnam (the Kissei Territory)\"。
- 对收购方的负担（同一 10-Q）：
  - 付给 Kissei 的区域外销售分成，含美国：\"in a low-single digit percentage\"。
  - 全球开发费用 Kissei 分担 \"a low-double digit percentage\"。
  - 全球竞品限制：\"the Company is prohibited from commercializing certain competing products worldwide\"（持续到首个批准后一段时间）。对已有膀胱癌资产的收购方有影响。
- 引进：无引进许可。10-K 称知识产权是购买所得（\"the entity from which we purchased the intellectual property rights to cretostimogene\"，MAN-CGON-1）。原转让方 ANI 主张 5% 特许权使用费，公司一审胜诉，2026-07-16 法院驳回 ANI 的新审动议；ANI 仍可上诉。
- 债务：Biovire 无担保票据 300 万美元，2028-02-28 到期（与 pack 的 total_debt 一致）。
- 资金：8-K Ex 99.1 原句 \"sufficient to fund operations through 2029\"（MAN-CGON-2）；10-Q 只写 \"for at least the next twelve months from the date of this Quarterly Report\"。pack 的 runway_months 为 59.7，与公司「到 2029 年」大致一致。

## 待核实

1. Pfizer 的 NMIBC 资产机制：10-K 只列名，未写机制。若为同机制（溶瘤 / 基因疗法）资产，buyer_fit 应为 0，改选 GSK #1。若确认机制不同，buyer_fit 可升为 4。
2. Kissei 的全球开发费用分担是否算「共同开发」：若复核人判为共同开发，权益改为 restricted，「收购」与之不兼容，需改交易形式或不入选。
3. Kissei 协议的竞品限制期限（\"a certain period of time\"）和控制权变更条款未披露；协议原文未打开。
4. BOND-003 预设成功阈值：PubMed 摘要未写。Lancet 全文页面返回 403，全文未读。
5. PIVOT-006（中危 NMIBC，随机 3 期）顶线时间：1 月指引 \"1H 2026\"（MAN-CGON-4），8 月改为 \"anticipated in the near-term\"（MAN-CGON-2），已推迟；CT.gov 预计主要完成 2026-11。截至 2026-10-30 公司官网新闻列表无读出公告（只列到 10-13 的 CCO 任命）。
6. BLA 是否在 2026Q4 按期完成提交、FDA 是否受理及 PDUFA 日期：未见文件。
7. Q3 2026 10-Q 截至 2026-10-30 尚未提交。

## Pack 问题

- 同一资产拆成 5 条适应症行（Bladder Cancer、High-Risk Non-Muscle-Invasive Bladder Cancer、Non Muscle Invasive Bladder Cancer、Non-Muscle Invasive Bladder Cancer、Transitional Cell Carcinoma），写法只差连字符。TOML 用无连字符的「Non Muscle Invasive Bladder Cancer」（id 227），只匹配这一行。
- id 227 的 stage_sources 指向 PIVOT-006（NCT06111235，中危 NMIBC），而推荐的适应症（高危 BCG 无应答）对应 BOND-003（NCT04452591）。两者都在同一行。
- BLA 滚动提交（10-K：2025Q4 启动；10-Q：预计 2026Q4 完成）在 pack 中不可见，pack 阶段为 phase3。
- 自动初筛的事件取 NCT06111235 估算日期 2026-11；公司已披露的更强事件是 BLA 提交完成（2026Q4）。

## 用时

约 30 分钟。
