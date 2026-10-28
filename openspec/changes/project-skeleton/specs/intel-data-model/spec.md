# Spec Delta

## Purpose

定义情报平台的领域实体与溯源规则，使每一个业务数据点都能追溯到一手来源，并明确区分客观事实与分析推断。

## ADDED Requirements

### Requirement: Domain entities
系统 SHALL 持久化以下领域实体：买方（Buyer）、买方偏好（BuyerPreference）、标的公司（Target）、管线（Program）、管线适应症（ProgramIndication）、临床试验（Trial）、试验结果（TrialResult）、催化事件（Catalyst）、财务快照（FinancialSnapshot）、买方×标的匹配（Match）。

#### Scenario: Fresh database contains every entity
- **WHEN** 在空目录执行建库命令
- **THEN** 生成的数据库包含上述每个实体对应的表，且建库命令可重复执行而不报错、不丢失已有数据

#### Scenario: Pipeline hierarchy is navigable
- **WHEN** 某标的公司有一条管线、该管线有一个适应症、该适应症关联一项临床试验
- **THEN** 可以从标的公司逐级查询到该临床试验，也可以从试验反查到所属标的公司

### Requirement: Source registry
系统 SHALL 维护来源登记，每条来源具有唯一的来源ID、URL 或本地文件路径、来源类型、发布日期（可为未知）与抓取时间。

#### Scenario: Source keeps external identifiers
- **WHEN** 登记一条来自对方材料、ID 为 `MRK-1` 的来源
- **THEN** 来源ID 原样保存为 `MRK-1`，可以通过该 ID 查到其 URL 与发布日期

#### Scenario: Unknown publish date
- **WHEN** 登记一条无法确定发布日期的来源
- **THEN** 发布日期为空，抓取时间仍必填

### Requirement: Claims link fields to sources
系统 SHALL 用声明（Claim）把业务字段关联到来源。每条声明指明所属实体与字段、取值、类别（fact 或 inference）、来源ID、截至日、产生方式（manual、api 或 llm 加模型名），以及可选的原文片段。

#### Scenario: Fact claim
- **WHEN** 为某试验的入组人数记录一条来自 ClinicalTrials.gov 的声明
- **THEN** 该声明类别为 fact，引用一个已登记的来源ID，产生方式为 api

#### Scenario: Claim must reference a registered source
- **WHEN** 写入一条引用未登记来源ID 的声明
- **THEN** 写入被拒绝

### Requirement: Inference carries confidence
类别为 inference 的声明 SHALL 带有置信度，取值为 high、medium_high、medium、low 之一；类别为 fact 的声明不要求置信度。

#### Scenario: Inference without confidence is rejected
- **WHEN** 写入一条类别为 inference 但未给置信度的声明
- **THEN** 写入被拒绝

### Requirement: LLM claims carry a verbatim quote
产生方式为 llm 的声明 SHALL 带有原文片段，以便核验该值确实出现在来源中。

#### Scenario: LLM claim without quote is rejected
- **WHEN** 写入一条产生方式为 llm、原文片段为空的声明
- **THEN** 写入被拒绝

### Requirement: Controlled vocabularies
研发阶段、置信度、声明类别、催化事件类型 SHALL 使用固定取值集合；研发阶段取值为 preclinical、phase1、phase1_2、phase2、phase2_3、phase3、filed、approved、unknown。

#### Scenario: Out-of-vocabulary stage is rejected
- **WHEN** 写入研发阶段为 "Ph III" 的管线适应症
- **THEN** 写入被拒绝，且错误信息列出允许的取值

### Requirement: Provenance completeness check
系统 SHALL 提供一个检查命令，列出每个有值但没有任何声明支撑的业务字段；存在缺口时命令以非零状态退出。

#### Scenario: Unsupported value is reported
- **WHEN** 某标的公司的现金字段有值，但没有任何声明指向该字段
- **THEN** 检查命令输出该公司与字段名，并以非零状态退出

#### Scenario: Empty value is not a gap
- **WHEN** 某字段为空（未知）且没有声明
- **THEN** 检查命令不把它列为缺口
