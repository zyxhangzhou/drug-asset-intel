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

### Requirement: Approved stage from FDA labels
系统 SHALL 为每个候选公司的获批申请抓取 openFDA 药品说明书的适应症段落并缓存。管线推导之后，若某条管线名称包含该获批产品的活性成分或品牌名（生物制品去掉 FDA 四字母后缀），且该管线某个适应症的全部关键词都出现在说明书适应症段落中，则该（管线, 适应症）阶段 SHALL 改为已上市：原有阶段声明被替换为 inference（置信度 medium_high），来源为说明书。按申请号查不到说明书时，SHALL 改用品牌名在说明书产品文本中检索；仍查不到时记入缺口清单，阶段不修正。申请人名称中的缩写后缀（PHARMS、PHARM、THERAP、THERAPS、OPERATION）在匹配公司别名时去掉。

#### Scenario: Label lists the indication
- **WHEN** 某公司获批产品 AVLAYAH（tividenofusp alfa-eknm）的说明书适应症含 "Mucopolysaccharidosis type II"，推导管线 TIVIDENOFUSP ALFA 的适应症为 "Mucopolysaccharidosis II"
- **THEN** 该管线适应症阶段为已上市，声明来源为说明书

#### Scenario: Unlisted indication keeps its trial phase
- **WHEN** 同一药物另有适应症 "Myelofibrosis" 不在说明书中
- **THEN** 该适应症保留试验推导的阶段

#### Scenario: Abbreviated sponsor name matches
- **WHEN** openFDA 申请人名为 "PRIOVANT THERAP"，公司别名为 "Priovant Therapeutics"
- **THEN** 该申请记为该公司的获批产品
