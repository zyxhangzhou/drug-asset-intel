# target-universe Specification

## Purpose
建立 149 家标普生物科技指数成分公司的标的全集，附 SEC CIK 映射，并记录第一轮规则排除（Stage 0）的类别、理由与一手来源，产出后续数据拉取所用的候选池。

## Requirements

### Requirement: Index universe import
系统 SHALL 把指数清单的每一行导入为一个标的公司，保留原表的 ticker 与公司名，并以指数工作簿为来源。

#### Scenario: Every index row becomes a target
- **WHEN** 导入完成
- **THEN** 标的公司数为 149，ticker 集合与原表一致

### Requirement: CIK mapping
系统 SHALL 用 SEC 发布的 ticker → CIK 对照文件为每个标的填写 CIK（10 位、补零），并生成以该文件为来源的 fact 声明。对照文件中找不到的 ticker 留空并记入缺口清单，不得凭公司名猜测。

#### Scenario: Mapped ticker
- **WHEN** 对照文件中有某标的 ticker
- **THEN** 该标的 CIK 为对照文件中的值补零到 10 位，并有一条引用对照文件来源的声明

#### Scenario: Unmapped ticker
- **WHEN** 对照文件中没有某标的 ticker
- **THEN** 该标的 CIK 为空，缺口清单中有该 ticker

### Requirement: Stage 0 exclusions require verified sources
Stage 0 排除名单 SHALL 由人工核实文件驱动，每条包含 ticker、排除类别（acquired、buyer_scale、non_therapeutic）、理由、来源 URL 与来源类型、核实标记。只有标记为已核实的条目才把标的标为排除，并生成引用该来源的声明：acquired 为 fact；buyer_scale、non_therapeutic 为 inference 并带置信度。未核实条目不生效，构建时报告其数量。

#### Scenario: Verified exclusion
- **WHEN** 核实文件中某 ticker 已核实、类别为 acquired、附收购公告 URL
- **THEN** 该标的为排除状态，排除类别为 acquired，排除理由有一条引用该公告来源的 fact 声明

#### Scenario: Unverified draft row has no effect
- **WHEN** 核实文件中某 ticker 的核实标记为空
- **THEN** 该标的仍在候选池中，构建输出提示存在未核实条目

### Requirement: Candidate pool
未被排除的标的 SHALL 构成候选池；每个标的要么在候选池中，要么带排除类别、理由与来源。

#### Scenario: Pool and exclusions partition the universe
- **WHEN** 导入与排除完成
- **THEN** 候选池数量加排除数量等于 149，且每个排除标的都有带来源的排除理由
