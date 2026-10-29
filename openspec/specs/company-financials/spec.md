# company-financials Specification

## Purpose
为候选池公司生成财务快照：现金及投资、债务、经营现金流、流通股、股价、市值与资金可支撑时间，申报值直接取自 SEC XBRL，股价取自 Nasdaq 行情并标为非官方，推算值标为推断并写明公式。

## Requirements

### Requirement: XBRL values with fixed tag precedence
系统 SHALL 按固定标签清单取值：现金及投资优先使用合并标签，没有合并标签时才把现金与各类有价证券分项相加，合并标签与其分项不得同时计入；债务按固定清单相加。只采用 10-K / 10-Q 的条目，同一期间有多次申报时取最近申报的值。每个值是 fact，来源为该值所在申报文件，声明备注记录使用的标签、期间结束日与申报日。

#### Scenario: Components summed when no combined tag
- **WHEN** 公司申报了现金与短期可供出售证券两个分项、没有合并标签
- **THEN** 现金及投资为两者之和，备注列出两个标签

#### Scenario: Combined tag is not double counted
- **WHEN** 公司同时申报了合并标签和其分项
- **THEN** 现金及投资只取合并标签的值

#### Scenario: Foreign filer is a gap
- **WHEN** 某公司没有 us-gaap 财务数据（如 20-F 申报主体）
- **THEN** 财务字段为空，缺口清单记录原因

### Requirement: Operating cash flow and runway
经营现金流 SHALL 按申报原样保存年初至今的累计值及其期间。资金可支撑时间 = 现金及投资 ÷（−经营现金流 ÷ 期间月数），仅在经营现金流为负时计算；结果为 inference，置信度 medium，备注写明公式与所用数值。经营现金流为正时不计算，并在备注中说明。

#### Scenario: Runway from burn
- **WHEN** 现金及投资 5.0 亿美元、6 个月经营现金流 −2.4 亿美元
- **THEN** 资金可支撑时间为 12.5 个月，声明类别为 inference

### Requirement: Price and market cap
股价 SHALL 取 Nasdaq 历史行情中不晚于快照日的最近收盘价，来源类型为 market_data，备注注明非官方来源与实际交易日。市值 = 收盘价 × 封面页流通股数，分别引用行情与申报来源各一条声明，备注记录两个日期。

#### Scenario: Weekend snapshot date
- **WHEN** 快照日没有交易
- **THEN** 使用之前最近一个交易日的收盘价，并记录该交易日

#### Scenario: Market cap cites both sources
- **WHEN** 市值计算完成
- **THEN** 市值字段有两条声明，分别引用行情来源和申报来源
