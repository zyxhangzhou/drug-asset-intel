## ADDED Requirements

### Requirement: Approved stage from FDA labels
系统 SHALL 为每个候选公司的获批申请抓取 openFDA 药品说明书的适应症段落并缓存。管线推导之后，若某条管线名称包含该获批产品的活性成分或品牌名（生物制品去掉 FDA 四字母后缀），且该管线某个适应症的全部关键词都出现在说明书适应症段落中，则该（管线, 适应症）阶段 SHALL 改为已上市：原有阶段声明被替换为 inference（置信度 medium_high），来源为说明书。申请人名称中的缩写后缀（PHARMS、PHARM、THERAP、THERAPS、OPERATION）在匹配公司别名时去掉。

#### Scenario: Label lists the indication
- **WHEN** 某公司获批产品 AVLAYAH（tividenofusp alfa-eknm）的说明书适应症含 "Mucopolysaccharidosis type II"，推导管线 TIVIDENOFUSP ALFA 的适应症为 "Mucopolysaccharidosis II"
- **THEN** 该管线适应症阶段为已上市，声明来源为说明书

#### Scenario: Unlisted indication keeps its trial phase
- **WHEN** 同一药物另有适应症 "Myelofibrosis" 不在说明书中
- **THEN** 该适应症保留试验推导的阶段

#### Scenario: Abbreviated sponsor name matches
- **WHEN** openFDA 申请人名为 "PRIOVANT THERAP"，公司别名为 "Priovant Therapeutics"
- **THEN** 该申请记为该公司的获批产品
