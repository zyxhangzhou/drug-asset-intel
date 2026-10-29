# fda-approvals Specification

## Purpose
记录候选池公司已获 FDA 批准的产品与申请号，来源为 openFDA drugsfda，并链接到 Drugs@FDA 对应申请页面。

## Requirements

### Requirement: Approved products from openFDA
系统 SHALL 下载 openFDA drugsfda 全量导出（只保留 NDA / BLA），按公司别名匹配申请的 sponsor 名称，为每个已批准的申请记录申请号、品牌名、活性成分、首次批准日期，均为 fact，来源为该申请并链接到 Drugs@FDA 页面。没有匹配的公司视为没有获批产品，不算失败。同一份数据 SHALL 提供"已获批活性成分及其持有公司"，供管线推导识别其他公司的已上市药（联用药或对照药）。

#### Scenario: No approvals is not an error
- **WHEN** 某公司在 drugsfda 数据中没有匹配的申请
- **THEN** 该公司没有获批产品记录，构建不报错

#### Scenario: Approved product recorded
- **WHEN** 某公司有一个 NDA 申请及其批准记录
- **THEN** 有一条获批产品记录，申请号与品牌名与接口一致，来源链接到该申请页面
