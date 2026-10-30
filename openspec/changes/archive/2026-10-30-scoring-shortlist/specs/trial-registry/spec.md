## ADDED Requirements

### Requirement: Partner compounds and manual merges
推导管线时，系统 SHALL 排除只以其他公司研发代号登记的干预（代号前缀与持有公司见 `data/manual/sponsor_code_prefixes.csv`；前缀属于本公司时不排除；同一干预另登记了本公司代号或通用名时不排除）。`data/manual/program_aliases.csv` 中人工确认为同一药物的两个名称 SHALL 合并为一条管线。给药频次与途径缩写（PO、QD、BID、TID）不作为药名的一部分。

#### Scenario: Partner code is not a program
- **WHEN** 某公司试验的干预只登记为 "PF-07220060"，且该公司不是辉瑞
- **THEN** 不为该公司生成该管线

#### Scenario: Manual alias merges code name and INN
- **WHEN** 人工文件写明 RLY-2608 与 zovegalisib 为同一药物
- **THEN** 两者归为同一条管线

#### Scenario: Dosing words do not split a program
- **WHEN** 试验分别登记 "Brepocitinib PO QD" 与 "Brepocitinib"
- **THEN** 两者归为同一条管线
