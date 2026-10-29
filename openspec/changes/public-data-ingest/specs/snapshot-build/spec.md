# Spec Delta

## ADDED Requirements

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
