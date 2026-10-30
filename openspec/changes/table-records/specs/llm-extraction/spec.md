## MODIFIED Requirements

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
