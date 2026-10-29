# Spec Delta

## Purpose

记录候选池公司已获 FDA 批准的产品与申请号，来源为 openFDA drugsfda，并链接到 Drugs@FDA 对应申请页面。

## ADDED Requirements

### Requirement: Approved products from openFDA
系统 SHALL 按公司别名查询 openFDA drugsfda，为每个申请记录申请号、品牌名、活性成分、首次批准日期，均为 fact，来源为该申请并链接到 Drugs@FDA 页面。接口返回"无匹配"视为该公司没有获批产品，不算抓取失败。

#### Scenario: No approvals is not an error
- **WHEN** 某公司查询结果为无匹配
- **THEN** 该公司没有获批产品记录，抓取日志中不记为失败

#### Scenario: Approved product recorded
- **WHEN** 某公司有一个 NDA 申请及其批准记录
- **THEN** 有一条获批产品记录，申请号与品牌名与接口一致，来源链接到该申请页面
