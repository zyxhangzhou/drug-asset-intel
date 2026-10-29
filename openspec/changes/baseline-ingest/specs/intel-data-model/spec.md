# Spec Delta

## MODIFIED Requirements

### Requirement: Domain entities
系统 SHALL 持久化以下领域实体：买方（Buyer）、买方偏好（BuyerPreference）、买方财务（BuyerFinancial）、买方产品专利到期（BuyerProductLoe）、标的公司（Target）、管线（Program）、管线适应症（ProgramIndication）、临床试验（Trial）、试验结果（TrialResult）、催化事件（Catalyst）、财务快照（FinancialSnapshot）、买方×标的匹配（Match）。

#### Scenario: Fresh database contains every entity
- **WHEN** 在空目录执行建库命令
- **THEN** 生成的数据库包含上述每个实体对应的表，且建库命令可重复执行而不报错、不丢失已有数据

#### Scenario: Pipeline hierarchy is navigable
- **WHEN** 某标的公司有一条管线、该管线有一个适应症、该适应症关联一项临床试验
- **THEN** 可以从标的公司逐级查询到该临床试验，也可以从试验反查到所属标的公司

#### Scenario: Buyer detail is navigable
- **WHEN** 某买方有偏好、财务与产品专利到期记录
- **THEN** 可以从该买方查询到这三类记录

### Requirement: Source registry
系统 SHALL 维护来源登记，每条来源具有唯一的来源ID、URL、来源类型、发布日期（可为未知）与抓取时间；被抓取存档的文档另记本地存档路径与内容哈希。来源类型取值：mnc_material、sec_filing、sec_xbrl、ctgov、openfda、fda_web、company_ir、press_release、publication、market_data、other。来源 SHALL 保留原始日期文本；只有原始日期精确到日时才填写发布日期，不得把"2026-08"或"2026"补成具体某一天。来源 SHALL 记录链接状态与检查时间。

#### Scenario: Source keeps external identifiers
- **WHEN** 登记一条来自对方材料、ID 为 `MRK-1` 的来源
- **THEN** 来源ID 原样保存为 `MRK-1`，可以通过该 ID 查到其 URL 与发布日期

#### Scenario: Archived document is verifiable
- **WHEN** 登记一条已抓取存档的 8-K 新闻稿来源
- **THEN** 该来源记录本地存档路径与内容哈希，按路径读取的文件哈希与记录一致

#### Scenario: Unknown publish date
- **WHEN** 登记一条无法确定发布日期的来源
- **THEN** 发布日期为空，抓取时间仍必填

#### Scenario: Partial publish date
- **WHEN** 登记一条原始日期为 "2026-08" 的来源
- **THEN** 原始日期文本保存为 "2026-08"，发布日期为空

### Requirement: Controlled vocabularies
研发阶段、置信度、声明类别、催化事件类型、排除类别、链接状态 SHALL 使用固定取值集合；研发阶段取值为 preclinical、phase1、phase1_2、phase2、phase2_3、phase3、filed、approved、unknown；排除类别取值为 acquired、buyer_scale、non_therapeutic；链接状态取值为 unchecked、ok、blocked、broken、local_file。

#### Scenario: Out-of-vocabulary stage is rejected
- **WHEN** 写入研发阶段为 "Ph III" 的管线适应症
- **THEN** 写入被拒绝，且错误信息列出允许的取值

#### Scenario: Out-of-vocabulary exclusion category is rejected
- **WHEN** 写入排除类别为 "too_big" 的标的公司
- **THEN** 写入被拒绝，且错误信息列出允许的取值

## ADDED Requirements

### Requirement: Source link check
系统 SHALL 提供链接检查命令，逐条检查来源 URL 的可达性并记录结果：2xx/3xx 为 ok；401/403/429 为 blocked（站点拒绝自动访问，不等于失效）；404/410、域名无法解析为 broken；非 http(s) 的本地路径为 local_file，不发起请求。检查结果只标注状态，不修改或替换 URL。

#### Scenario: Local path is not fetched
- **WHEN** 来源的链接是 `D:\...` 形式的本地路径
- **THEN** 链接状态为 local_file，且不发起任何网络请求

#### Scenario: Dead link is flagged, not replaced
- **WHEN** 来源 URL 返回 404
- **THEN** 链接状态为 broken，URL 保持原值
