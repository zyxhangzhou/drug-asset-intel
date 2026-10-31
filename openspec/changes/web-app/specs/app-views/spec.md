## Purpose

规定应用对用户展示的只读视图与对应接口：买方画像、候选公司浏览与对比、公司管线、临床试验、试验结果，以及从任意值追溯到一手来源。

## ADDED Requirements

### Requirement: Value provenance in responses
买方详情、公司详情、试验详情接口 SHALL 随其中每个实体附带支撑其字段的来源声明，按字段分组；公司详情中的试验列表只是摘要，每行附该试验登记记录的来源 ID，完整声明在试验详情中返回。每条声明 SHALL 包含：取值、事实或推断、推断的置信度、产生方式（官方接口、人工、LLM）、模型名（LLM 产生时）、原文片段（有时）、截至日期，以及来源的 ID、标题、类型、发布者、发布日期、网址。没有声明的字段 SHALL 返回空列表，不编造来源。

#### Scenario: LLM value carries its quote
- **WHEN** 请求一家公司的详情，其中某药物的作用机制来自已签字的 LLM 抽取
- **THEN** 该药物的作用机制字段带一条声明，产生方式为 LLM，含模型名与原文片段，来源指向存档文档

#### Scenario: Field without source
- **WHEN** 某字段在快照中没有任何声明
- **THEN** 该字段的声明列表为空

### Requirement: Buyer profiles
应用 SHALL 列出 10 家买方，并为每家提供画像：财务信号、治疗领域与技术偏好、交易偏好、收购逻辑、关键证据；财务数据（收入、现金、债务、自由现金流、资本配置、近期交易）；专利到期产品；按偏好排序的偏好行（标签、目标资产画像、理想阶段、交易形式）；与该买方匹配分最高的候选公司。

#### Scenario: Buyer detail
- **WHEN** 打开某买方的画像页
- **THEN** 页面显示该买方的偏好行、财务、专利到期产品与匹配候选，每个带来源的值可以查看来源

#### Scenario: Unknown buyer
- **WHEN** 请求不存在的买方代码
- **THEN** 接口返回 HTTP 404

### Requirement: Candidate browsing and comparison
候选列表 SHALL 显示每家公司的主推荐方向与分数，并支持：按买方、治疗领域、研发阶段、研究状态、是否入选筛选；按名称或代码搜索；按任一分数列排序；调整五个维度的权重后重新排序；勾选 2–4 家公司并排对比主推荐方向、各维度分数、下一事件、企业价值与资产权益。

#### Scenario: Filter by buyer and stage
- **WHEN** 用户在候选列表选择买方 Pfizer 与阶段「3 期」
- **THEN** 列表只显示主推荐方向买方为 Pfizer 且阶段为 3 期的公司

#### Scenario: Compare companies
- **WHEN** 用户勾选 3 家公司并选择对比
- **THEN** 对比视图并排显示这 3 家的主推荐方向、各维度分数与保守分 / 乐观分

### Requirement: Company pipeline view
公司详情 SHALL 显示：公司基本信息与是否入选、入选理由；主推荐方向的复核结论（各维度分数与理由、研究设计、可比性、结果、局限、下一事件、资产权益、两句话论点）；管线（药物、作用机制、技术类型，每个适应症的治疗领域与研发阶段）；获批产品；催化事件；最新财务快照（现金、债务、经营现金流、可支撑月数、市值、收购成本区间）。阶段 SHALL 区分事实与推断（来源声明的类型）。

#### Scenario: Deep-dive company
- **WHEN** 打开 VKTX 的公司详情
- **THEN** 页面显示 VK2735 的适应症与阶段、复核结论与推荐逻辑、催化事件与财务快照

#### Scenario: Unknown company
- **WHEN** 请求不存在的公司代码
- **THEN** 接口返回 HTTP 404

### Requirement: Trial view
应用 SHALL 列出公司的临床试验（NCT 编号、标题、阶段、状态、入组人数与类型、开始日期、主要完成日期与类型、预计数据读出），并为每项试验提供详情：设计、适应症、干预、完成日期与已有结果。预计日期 SHALL 标明登记类型（预计或实际）。

#### Scenario: Trial detail
- **WHEN** 打开一项试验的详情
- **THEN** 页面显示其状态、方案设计、入组人数、预计结束时间与预计读出时间

#### Scenario: Unknown trial
- **WHEN** 请求不存在的 NCT 编号
- **THEN** 接口返回 HTTP 404

### Requirement: Completed trial results
应用 SHALL 显示试验的主要结果（终点、结果、统计分析、对照、相对标准治疗的优势），包括 CT.gov 已发布结果与已签字的 LLM 抽取结果；公司详情 SHALL 汇总该公司全部有结果的试验。

#### Scenario: Results of a company
- **WHEN** 打开有已发布结果的公司详情中的结果部分
- **THEN** 显示每条结果所属试验、终点与结果，并可查看来源

### Requirement: Source view
应用 SHALL 为每个来源提供来源页：ID、标题、类型、发布者、发布日期、抓取时间、网址、文本指纹。来源有存档文本时 SHALL 可查看存档原文，并能定位到声明的原文片段。存档文本只从快照记录的存档路径读取，且该路径 SHALL 位于项目的原始数据目录内。

#### Scenario: Jump from value to original text
- **WHEN** 用户点开某临床结果的来源标记并进入来源页
- **THEN** 来源页显示该文档的存档原文，原文片段被标出

#### Scenario: Source without archive
- **WHEN** 来源没有存档文本（例如只有网址的人工来源）
- **THEN** 来源页显示元信息与网址，注明没有存档原文

#### Scenario: Unknown source
- **WHEN** 请求不存在的来源 ID
- **THEN** 接口返回 HTTP 404
