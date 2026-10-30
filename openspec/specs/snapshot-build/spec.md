# snapshot-build Specification

## Purpose
规定数据快照如何生成：联网抓取只写本地缓存，快照构建只读缓存、对方材料与人工核实文件，从零确定性重建，并输出缺口清单，使任何人都能复现同一份快照。

## Requirements

### Requirement: Fetch is separate from build
联网抓取 SHALL 只把原始响应写入 `data/raw/` 并记录抓取时间；快照构建 SHALL 不发起网络请求。需要联系人信息的接口（SEC）在未配置时 SHALL 拒绝抓取并说明需要配置的项，而不是使用占位值。大模型调用同样是联网操作：只有抽取命令 SHALL 调用模型，它把原始响应与账本写入 `data/raw/llm/`，把待复核结果写入 `data/manual/extractions/`；快照构建 SHALL 只读取已签字的抽取复核文件，不调用模型。

#### Scenario: Build works offline
- **WHEN** 缓存与材料齐全，在无网络环境执行构建
- **THEN** 构建成功，生成的快照内容与联网时一致

#### Scenario: SEC fetch without contact info
- **WHEN** 未配置 SEC 联系人信息时执行 SEC 抓取
- **THEN** 命令失败，错误信息指出需要设置的配置项名

#### Scenario: Missing cache is reported
- **WHEN** 构建时缺少某个抓取缓存
- **THEN** 依赖该缓存的字段留空并记入缺口清单，构建本身不失败

#### Scenario: Build without model keys
- **WHEN** 未配置任何模型密钥，且存在已签字的抽取复核文件
- **THEN** 构建成功，被接受的条目进入快照

### Requirement: Deterministic rebuild
快照构建 SHALL 从零生成新的快照并在成功后替换旧快照；同样的输入两次构建，除生成时间外业务数据与声明完全相同。构建失败时旧快照保持不变。

#### Scenario: Rebuild is repeatable
- **WHEN** 对相同输入连续构建两次
- **THEN** 两次的实体与声明内容一致

#### Scenario: Failed build keeps old snapshot
- **WHEN** 构建过程中出现写入校验错误
- **THEN** 原快照文件不变，命令以非零状态退出

### Requirement: Gap report
构建 SHALL 输出缺口清单文件，每条记录实体、字段、原因与原始位置（表名与单元格，或接口名），并在命令输出中给出汇总计数。

#### Scenario: Gap report written
- **WHEN** 构建完成且存在待核实单元格或未映射 ticker
- **THEN** 缺口清单文件列出每一条，命令输出按原因汇总数量

### Requirement: Trimmed raw caches
抓取 SHALL 只缓存构建所需的字段或条目，被保留的内容与接口返回的原文一致；同时记录完整响应的 sha256 哈希、请求 URL 与抓取时间，以便事后对照官方接口复核。

#### Scenario: Trimmed cache keeps verbatim entries
- **WHEN** 抓取某公司的 XBRL companyfacts
- **THEN** 缓存只含所需标签，每个保留条目的字段与原响应完全相同，且旁注文件中记录了完整响应的哈希

### Requirement: Snapshot date
快照 SHALL 声明一个快照日；股价取不晚于快照日的最近收盘价，财务取快照日之前已申报的最近一期。快照日记录在快照元信息中，可通过元信息接口查到。

#### Scenario: Snapshot date in metadata
- **WHEN** 请求快照元信息接口
- **THEN** 返回快照日

### Requirement: Polite external access
对外部接口的抓取 SHALL 限速：SEC 每秒不超过 10 次请求，ClinicalTrials.gov 每分钟不超过约 50 次，其他接口每次请求之间至少间隔 0.5 秒；收到 429 时按 Retry-After 退避后重试；单个公司的抓取失败只记录到抓取日志，不中断其余公司的抓取。

#### Scenario: One failing company does not stop the batch
- **WHEN** 批量抓取时某公司的接口请求失败
- **THEN** 其余公司照常抓取，失败公司与原因写入抓取日志

### Requirement: Scoring outputs
构建 SHALL 在导入数据之后执行评分，并在快照旁输出两个文件：复核长名单（按乐观分排序，含保守分、乐观分、覆盖率、研究状态、未入选原因）与入选名单（按保守分排序的入选公司及两句话论点）。复核池 SHALL 为乐观分前 N 家（有推导资产），加上配置 `longlist_extra` 中人工列出的公司，以及所有已复核的公司。

#### Scenario: Lists written on build
- **WHEN** 执行构建
- **THEN** 快照旁生成长名单与入选名单文件；没有复核过的公司时入选名单只有表头

#### Scenario: Manual addition to the review pool
- **WHEN** 配置 `longlist_extra` 列出某家有推导资产、但乐观分不在前 N 的公司
- **THEN** 该公司在长名单中标为进入复核池

### Requirement: Extractions revalidated at build
构建载入已签字的抽取复核文件时，SHALL 对每个被接受的条目重新校验：来源有本地存档，存档文本哈希与登记一致，原文片段按抽取规格的规范化规则仍是存档文本的子串，取值中的数字出现在片段中。任一校验失败 SHALL 使构建失败，并指出文件、条目与原因。

#### Scenario: Edited quote fails build
- **WHEN** 人工把某条目的片段改成原文中没有的句子并签字
- **THEN** 构建失败，错误信息指出该复核文件与条目

#### Scenario: Missing archive fails build
- **WHEN** 被接受条目的来源存档文件不存在
- **THEN** 构建失败，错误信息指出来源 ID
