# Spec Delta

## MODIFIED Requirements

### Requirement: Domain entities
系统 SHALL 持久化以下领域实体：买方（Buyer）、买方偏好（BuyerPreference）、买方财务（BuyerFinancial）、买方产品专利到期（BuyerProductLoe）、标的公司（Target）、管线（Program）、管线适应症（ProgramIndication）、临床试验（Trial）、试验结果（TrialResult）、催化事件（Catalyst）、财务快照（FinancialSnapshot）、获批产品（ApprovedProduct）、买方×标的匹配（Match）。临床试验 SHALL 直接关联所属标的公司，并保留登记的原始适应症与干预措施文本；关联到管线适应症是可选的。

#### Scenario: Fresh database contains every entity
- **WHEN** 在空目录执行建库命令
- **THEN** 生成的数据库包含上述每个实体对应的表，且建库命令可重复执行而不报错、不丢失已有数据

#### Scenario: Pipeline hierarchy is navigable
- **WHEN** 某标的公司有一条管线、该管线有一个适应症、该适应症关联一项临床试验
- **THEN** 可以从标的公司逐级查询到该临床试验，也可以从试验反查到所属标的公司

#### Scenario: Buyer detail is navigable
- **WHEN** 某买方有偏好、财务与产品专利到期记录
- **THEN** 可以从该买方查询到这三类记录

#### Scenario: Trial without derived program
- **WHEN** 某试验无法归入任何管线
- **THEN** 仍可从标的公司直接查到该试验及其原始适应症与干预文本
