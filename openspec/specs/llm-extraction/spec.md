# llm-extraction Specification

## Purpose
规定如何用大模型从已存档文档中抽取管线机制、临床结果与催化事件：只抽取有原文片段支撑的值，程序校验片段，两个模型独立交叉核对，并对每次调用记录用量与费用、在预算上限内运行。

## Requirements

### Requirement: Extraction schema
抽取 SHALL 只产出以下三类条目，每条带取值与原文片段：
- 管线条目：资产名、作用机制、技术类型（小分子、抗体、ADC、基因疗法、siRNA 等，以原文用词为准）；
- 临床结果条目：资产名、试验（NCT 编号或原文中的试验名）、适应症、终点、结果、统计分析、对照组；
- 催化事件条目：资产名、事件描述、事件类型（data_readout、regulatory_filing、regulatory_decision、trial_start、other）、原文中的时间表述。
「相对标准治疗的优势」SHALL 只在原文直接作比较时抽取，并标为推断、附置信度。原文没有的字段 SHALL 留空，不得补全。

#### Scenario: Missing field left empty
- **WHEN** 新闻稿报告了主要终点达成但没有给出 p 值
- **THEN** 该临床结果条目的统计分析为空，不出现推测值

#### Scenario: Comparison marked as inference
- **WHEN** 原文写「compared with placebo」并给出差值
- **THEN** 条目的对照组为 placebo；相对标准治疗的优势只在原文点名标准治疗时填写，且标为推断

### Requirement: Retrieval before extraction
系统 SHALL 把存档文本切成带位置的块并建立全文索引；每类条目只把检索命中的块送给模型，而不是整份文档。每次调用 SHALL 记录送出的块编号。

#### Scenario: Only relevant chunks sent
- **WHEN** 对一份 10-Q 抽取临床结果
- **THEN** 送出的块来自检索命中，调用记录列出这些块编号

### Requirement: Quote validation
每个条目带原文片段：正文取值 1–4 段；表格取值每用到一格，引用该格的一行表格记录，不限段数。每段片段 SHALL 在规范化后是该文档文本的子串，且不少于 20 个字符。规范化规则：Unicode NFKC；所有空白折叠为一个空格；弯引号转直引号；各类连字符与破折号转为 `-`；比较时不区分大小写。条目取值中出现的每个数字 SHALL 出现在其片段中（资产代号所含数字除外）。管线条目的机制与技术类型不得同时为空。催化事件的时间表述 SHALL 含有年份。任一校验失败的条目 SHALL 写入拒收记录并注明原因，不进入复核文件。

#### Scenario: Reformatted quote accepted
- **WHEN** 片段与原文只在换行和弯引号上不同
- **THEN** 片段校验通过

#### Scenario: Invented quote rejected
- **WHEN** 片段在文档文本中找不到
- **THEN** 条目进入拒收记录，原因为片段不在原文中

#### Scenario: Number not in quote
- **WHEN** 取值为「ORR 42%」而片段中没有 42
- **THEN** 条目进入拒收记录，原因为数字不在片段中

#### Scenario: Multi-arm table value
- **WHEN** 一个临床结果列出 5 个剂量组在同一终点的数值，并为每个剂量组引用一行表格记录
- **THEN** 片段校验与数字校验通过

### Requirement: Blind cross-check
配置了核验模型时，系统 SHALL 让核验模型对同样的块、同样的指令独立抽取，不向它展示主模型的结果。两边条目按类型与关键字段配对；关键字段只是措辞不同时，按同一资产且片段在原文中位置重叠配对。资产名去掉连接词（plus、and、with、combination）后比较；名称与其括号内代码任一相同即视为同一资产。一致的条件按字段逐一判断：两边都为空（「none」「n/a」「not stated」视为空）；或两边都有值、数字集合相同，并且规范化后文本相同或两边片段在原文中的位置重叠。配对且一致的条目标为「一致」；不一致或只有一边抽出的条目标为「分歧」。未配置核验模型时，全部条目标为「单模型」。

#### Scenario: Models agree
- **WHEN** 两个模型对同一终点给出相同的数字集合，且片段都通过校验
- **THEN** 条目标为一致

#### Scenario: Verify model not configured
- **WHEN** 未设置核验模型的密钥
- **THEN** 抽取照常完成，全部条目标为单模型，命令输出提示未做交叉核验

#### Scenario: Same drug spelled differently
- **WHEN** 主模型写「BARZOLVOLIMAB」，核验模型写「BARZOLVOLIMAB (CDX-0159)」，其余字段相同
- **THEN** 两个条目配对并标为一致

#### Scenario: Empty and none comparator
- **WHEN** 一个模型对照组留空，另一个写「none」
- **THEN** 对照组字段视为一致

### Requirement: Replay saved replies
每次调用 SHALL 在保存的原始回复中记录提示词哈希（模型名、系统提示、用户提示）。`intel extract --replay` SHALL 用同一提示词哈希的最近一次保存回复代替调用，重新校验与配对，不发请求、不记账本、不重复写校验日志。找不到同一提示词的回复时 SHALL 报错，不得改用其他回复。

#### Scenario: Re-pair after a pairing fix
- **WHEN** 配对规则修改后以 `--replay` 重跑
- **THEN** 条目按新规则重新配对，账本与校验日志不变

#### Scenario: Prompt changed
- **WHEN** 提示词修改后以 `--replay` 重跑
- **THEN** 命令报错「no saved response」，提示去掉 `--replay` 重新调用

### Requirement: Cost ledger
每次模型调用 SHALL 在账本中追加一条记录：时间、服务商、请求模型名与接口返回的模型名、任务、来源 ID、块编号、接口返回的原始用量、按价格表折算的人民币费用、所处计费时段。价格表与计费时段 SHALL 放在仓库内的配置文件，并注明价格来源 URL 与查询日期。账本 SHALL 足以在价格表更正后重新计算费用。

#### Scenario: Usage recorded
- **WHEN** 一次调用返回缓存命中与未命中的输入用量
- **THEN** 账本记录两者原值，费用按对应单价分别计算

### Requirement: Budget cap
每个服务商 SHALL 有预算上限。每次调用前，系统 SHALL 按最坏情况预估本次费用（输入全按缓存未命中计价，输出按最大输出长度计价）；已花费加预估超过上限时 SHALL 停止，不发出该调用，并报告已花费金额。DeepSeek 处于高峰时段时，抽取命令 SHALL 默认拒绝运行，除非显式允许。

#### Scenario: Cap reached
- **WHEN** 账本累计 14.9 元，上限 15 元，本次预估 0.2 元
- **THEN** 命令停止且不发出调用，输出已花费 14.9 元与上限

#### Scenario: Peak hours refused
- **WHEN** 北京时间周三 10:00 执行抽取且未显式允许高峰运行
- **THEN** 命令退出并说明下一个空闲时段的开始时间

### Requirement: Extraction metrics
系统 SHALL 提供报告命令，按公司与服务商输出：调用次数、输入与输出用量、累计费用、片段校验通过率、数字校验通过率、双模型一致率、拒收原因分布。

#### Scenario: Report after a run
- **WHEN** 对一份文档完成抽取后执行报告命令
- **THEN** 输出包含该文档的条目数、各项校验通过率与费用
