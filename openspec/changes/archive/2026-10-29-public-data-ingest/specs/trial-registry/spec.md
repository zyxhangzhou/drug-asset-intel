# Spec Delta

## Purpose

从 ClinicalTrials.gov 为候选池公司取得临床试验的状态、方案、入组、关键日期与已发布结果，并据此推导管线、适应症与登记阶段，所有值可回溯到具体试验页面。

## ADDED Requirements

### Requirement: Lead-sponsor matching
系统 SHALL 只把牵头申办方名称与公司别名集合匹配的试验归入该公司。别名集合由指数公司名（去掉公司后缀）、SEC 登记名与人工别名文件组成；名称比较忽略大小写、标点与公司后缀。匹配不到任何试验的候选公司记入缺口清单。

#### Scenario: Text-search false positive is dropped
- **WHEN** 按 "Relay Therapeutics" 检索返回一项牵头申办方为其他公司的试验
- **THEN** 该试验不归入 RLAY

#### Scenario: Company with no matched trials
- **WHEN** 某候选公司过滤后没有任何试验
- **THEN** 缺口清单中有该公司，原因为 no_lead_sponsor_match

### Requirement: Trial facts
每项匹配的试验 SHALL 记录：NCT 号、标题、登记阶段、总体状态、设计（分配、干预模型、设盲、主要目的）、入组人数及其类型（预计 / 实际）、开始日期、主要完成日期及其类型、完成日期、原始适应症与干预文本。每个值有一条 fact 声明，来源为该试验，链接到试验页面。登记阶段按固定映射转换为研发阶段取值（PHASE4 视为 approved，NA 或缺失为 unknown）。数据读出时间不从试验登记推断，留空。

#### Scenario: Estimated completion is labelled
- **WHEN** 某试验的主要完成日期类型为 ESTIMATED
- **THEN** 主要完成日期写入，日期类型记为预计，声明备注注明为预计值

#### Scenario: Readout is not guessed
- **WHEN** 试验登记中只有主要完成日期
- **THEN** 预计数据读出字段为空

### Requirement: Posted results
对登记阶段为 Phase 2 及以上且已发布结果的试验，系统 SHALL 为每个主要终点记录终点名称、各组结果摘要（组名、数值、单位、离散度），以及登记的统计分析（p 值、方法），均为 fact，来源为该试验。不对结果做优劣判断。

#### Scenario: Primary outcome captured
- **WHEN** 某完成试验已发布结果，含一个主要终点
- **THEN** 有一条试验结果记录，终点名称与各组数值与登记内容一致

### Requirement: Derived pipeline
系统 SHALL 从匹配试验中类型为药物、生物制品或基因疗法的干预推导管线：排除安慰剂类名称、人工排除文件中的名称，以及由其他公司持有 FDA 批准的活性成分或品牌（视为联用药或对照药）；同一药物的代号、通用名与品牌名（依据试验登记的其他名称与 FDA 品牌—成分对应）合并为一条管线。每项试验以第一个登记适应症为其适应症；每个（管线, 适应症）的阶段取其试验的最高登记阶段。管线、适应症与阶段均为 inference，置信度 medium，备注注明"由 CT.gov 登记推导，登记阶段不等于公司公告的研发阶段"。

#### Scenario: Highest registered phase wins
- **WHEN** 某药在同一适应症有 Phase 2 与 Phase 3 两项试验
- **THEN** 该管线适应症阶段为 phase3，声明类别为 inference

#### Scenario: Another company's marketed drug is not a program
- **WHEN** 某公司试验的干预包括由其他公司持有 FDA 批准的 fulvestrant
- **THEN** 不为该公司生成 fulvestrant 管线

#### Scenario: Code name and INN are one program
- **WHEN** 试验登记 MGL-3196，其他名称为 resmetirom
- **THEN** 两者归为同一条管线

#### Scenario: Placebo is not a program
- **WHEN** 某试验干预包括 "Placebo"
- **THEN** 不生成名为 Placebo 的管线
