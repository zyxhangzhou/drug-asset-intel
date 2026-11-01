# data-verification Specification

## Purpose

规定数据质量的抽样核验：按层随机抽样、逐条对照一手来源核对、给出各层错误率与错误类型，结果可复现。

## Requirements

### Requirement: Stratified sample with a fixed seed
系统 SHALL 提供抽样命令，从快照的声明中分三层抽样：结构化字段（官方接口产生的事实）、复核字段（人工产生）、LLM 抽取字段；每层抽取数量可配置（默认 30），使用固定随机种子，同一快照与种子 SHALL 得到相同样本。抽样结果 SHALL 导出为核对表，每行含实体、字段、取值、来源 ID、来源网址或存档路径、原文片段（有时）。

#### Scenario: Reproducible sample
- **WHEN** 用相同快照与种子运行两次抽样
- **THEN** 两次的样本相同

### Requirement: Structured layer checked against cached responses
结构化层的每条样本 SHALL 自动与本地缓存的原始接口响应比对（CT.gov 研究记录、SEC XBRL、openFDA），结果为一致、不一致或无法比对（附原因）。

#### Scenario: Value differs from the raw response
- **WHEN** 某试验入组人数与缓存的 CT.gov 记录不同
- **THEN** 该行标为不一致，并给出两边的值

### Requirement: Verification report
核验结果 SHALL 写入 `docs/verification.md`：抽样规则与种子、每层样本数、核对方法、错误数与错误率（含 95% 置信区间上限）、错误类型、每个错误的处理结果；人工核对的层 SHALL 记录核对人与复查方式。发现的错误 SHALL 修正并重建快照，报告注明修正后的状态。

#### Scenario: Error found and fixed
- **WHEN** 复核层有一条取值与来源原文不符
- **THEN** 报告列出该条、错误类型与修正方式，修正后的快照中该值已更正

### Requirement: User spot check
系统 SHALL 用固定种子从已签字的复核文件中抽 5 份，生成核对清单（每份的推荐方向、资产权益、关键临床数据、下一事件及其来源链接），供用户人工抽查；抽查结果（份数、错误数、发现的问题）SHALL 记入 AI 使用日志。

#### Scenario: Spot-check list
- **WHEN** 生成用户抽查清单
- **THEN** 清单含 5 份复核文件，每项关键数据都附来源网址或存档路径
