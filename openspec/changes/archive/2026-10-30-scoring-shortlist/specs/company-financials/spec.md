## MODIFIED Requirements

### Requirement: Operating cash flow and runway
经营现金流 SHALL 按申报原样保存年初至今的累计值及其期间。资金可支撑时间 = 现金及投资 ÷ 月均经营现金消耗；月均消耗取「年初至今」与「最近一个完整财年（结束于资产负债表日或之前 15 个月内）」两者中较高者，以免一次性收入（如授权首付款）使消耗被低估。两者都没有现金消耗时不计算，并在缺口清单中说明。结果为 inference，置信度 medium，备注写明公式、所用数值与采用的期间。

#### Scenario: Runway from burn
- **WHEN** 现金及投资 5.0 亿美元、6 个月经营现金流 −2.4 亿美元，且没有消耗更高的完整财年
- **THEN** 资金可支撑时间为 12.5 个月，声明类别为 inference

#### Scenario: One-off inflow does not hide the burn
- **WHEN** 年初至今 6 个月经营现金流 −900 万美元（含一次性首付款），上一完整财年 −3.9 亿美元
- **THEN** 月均消耗按上一完整财年计算，备注写明采用的期间

## ADDED Requirements

### Requirement: Single-tag debt fallbacks
没有 LongTermDebt 及其流动 / 非流动分项时，债务 SHALL 依次取以下单一标签中第一个有值者：ConvertibleNotesPayable、ConvertibleDebtNoncurrent、ConvertibleLongTermNotesPayable、LongTermNotesPayable、LongTermLoansPayable、SecuredLongTermDebt、NotesPayable、LoansPayable。都没有时债务为空并记缺口。

#### Scenario: Notes payable counted as debt
- **WHEN** 公司只申报 LongTermNotesPayable 2.59 亿美元
- **THEN** 债务为 2.59 亿美元，备注记录该标签
