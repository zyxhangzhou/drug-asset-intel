# CATX（Perspective Therapeutics）复核草稿报告

## 推荐组合

- 资产 / 适应症：VMT-Α-NET（[212Pb]bamzireotide navoxetan，SSTR2 靶向 α 放射性配体）/ Neuroendocrine Tumors（pack 程序 id 2392），1/2a 期，计划 2027 年启动 3 期（MAN-CATX-1）。
- 买方：Johnson & Johnson，治疗领域偏好第 1（肿瘤/血液肿瘤，ideal_stage「Phase 2-3」）。
- 交易形式：许可（权益受限，不能写收购）。
- 分数：buyer_fit 4（中）、stage_match 2（高）、clinical 2（中高）。catalyst 与 dealability 由 build 从 [event] / [rights] 推导：事件为 medium / estimated，预期 catalyst 2；权益 restricted，dealability 最高 1。

选择理由：

- 资产选 VMT-α-NET。它是公司的主资产，数据最多（68 例），也是唯一有 3 期计划的项目。自动初筛选的是 PSV359（PDAC）。PSV359 只有安全性数据，下一次临床更新在 2027 年：\"The next clinical update is planned in 2027.\"（SEC-0001193125-26-342512）。
- 买方不用自动初筛的 Novartis #3。Novartis 画像点名「放射性配体」，但 10-K 竞争段写明 Novartis 的 Lutathera 是 SSTR2 阳性 GEP-NET 的已上市放射性配体：\"Novartis’ Lutathera®, which was approved in 2018, uses 177 Lu for the treatment of individuals with somatostatin receptor-positive gastroenteropancreatic neuroendocrine tumors\"（MAN-CATX-2）。同靶点、同适应症，属组合冲突，buyer_fit 0。
- BMS #1 也排除：10-K 把 BMS（RayzeBio）列为 NET 放射性配体开发者（MAN-CATX-2）。
- Pfizer #2 画像点名「放射性药物」，但覆盖乳腺、肺癌、泌尿和血液肿瘤，未点名 NET；阶段要求 Phase 2b-注册期，同样差一档。
- J&J #1 画像点名「放射性靶向药」，J&J 不在 10-K 的 NET 竞品句中，只在 α 放射性药物开发者泛列名单中（适应症未写）。
- 备选（未打分）：VMT01（MC1R，黑色素瘤）→ Novartis #3。权益完整（只有 UIRF 引进），阶段匹配 4 分；但证据只有 3.0 mCi 单药 7 例中 2 例部分缓解（SEC-0001193125-26-342512），且未见明确时间的下一事件。

## 资产权益

- 状态：restricted（受限）。
- 10-Q 原句：\"Lantheus was granted an exclusive option to negotiate an exclusive, worldwide, royalty- and milestone-bearing right and license to [ 212 Pb]VMT-α-NET\"；\"If good-faith negotiations fail, Lantheus has a one-year right to reenter negotiations if a third party offers to purchase or license the [ 212 Pb] VMT-α-NET program.\"（SEC-0001193125-26-342512；10-K 同文，MAN-CATX-2）
- 选择权未见到期。资产负债表 \"Deferred Income (Note 3)\" 在 2026-06-30 与 2025-12-31 均为 26,600 千美元。期权负债在\"various options expire\"时才转为收入。已到期的只有公司层面的优先要约与最后一看权（2025-01-08）。
- 引进义务：VMT-α-NET 与 VMT01 的专利由 University of Iowa 独家许可。UIRF 许可收销售分成（\"royalty-bearing\"），并分成再许可收入（MAN-CATX-2）。费率未披露。
- 其他：Lantheus 2024 年认购 19.99% 股份，并有 ATM 参与权。债务只有 Coralville 房产抵押票据 159.7 万美元，2027-12-29 到期约 150 万美元一次性还款（SEC-0001193125-26-342512）。
- 资金：10-Q 原句 \"will be sufficient to fund our current planned clinical milestones and operational investments into late 2027\"（SEC-0001193125-26-342512）。pack 的 runway_months 为 27.3。公司指引为「到 2027 年底」，自 2026-06-30 起约 18 个月，比 pack 短。3 期启动会增加开支。

## 待核实

0. **入选门槛**：许可是否与 Lantheus 的独家谈判选择权及一年重新谈判权兼容，由复核人判断。若判不兼容，建议不入选（§3.5「受限」且交易形式不兼容）。
1. buyer_fit 4 依据的是画像中的「放射性靶向药」。J&J 画像以血液瘤为主，未点名 NET。J&J 自己的 α 放射性药物管线（10-K 只列名、未写适应症）未核查。复核人可能降为 3。
2. 3 期启动只披露到年份（\"Phase 3 initiation expected in 2027\"），且以 FDA 2 期结束会议为前提。确定性按 estimated 处理。8 月 10-Q 说「站点激活目标约在 2026 年底」，10 月新闻稿改为「2026 年底完成站点准备，2027 年启动」，即时间已后移。
3. Lantheus 选择权的期限与行权条件：10-K / 10-Q 没有写。Option Agreement 原文（附件）未打开。
4. UIRF 特许权使用费率与里程碑金额未披露。
5. 临床数据只有公司新闻稿（ESMO 2026 快速口头报告）。会议摘要原文与 Lutathera FDA 标签未打开，故没有给任何与标准治疗的数值比较。
6. Q3 2026 10-Q 截至 2026-10-30 尚未提交。

## Pack 问题

- 自动初筛的主组合是 PSV359 / PDAC。PSV359 试验 NCT06710756 是 FAP 阳性泛实体瘤，PDAC 只是登记适应症之一；公司 2026-09 与 Merck 合作的联合用药针对 NSCLC 与结直肠癌，2026-10 Fast Track 针对孤立性纤维性肿瘤（SFT）。pack 的 PSV359 只有 PDAC 一个适应症。
- VMT-α-NET 只有「Neuroendocrine Tumors Unresectable」一条。同一试验已开脑膜瘤队列（\"evaluate the safety, dosimetry and preliminary anti-tumor activity of [ 212 Pb]VMT-α-NET in patients with meningioma\"，SEC-0001193125-26-342512），pack 未体现。
- VMT02 没有试验，stage_sources 指向 VMT01 的成像试验 NCT04904120。10-Q 的管线中没有 VMT02。
- pack 程序名用希腊大写字母「VMT-Α-NET」（Α 为 U+0391）。TOML 已照抄。

## 用时

约 25 分钟。
