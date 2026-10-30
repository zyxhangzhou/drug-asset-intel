## MODIFIED Requirements

### Requirement: Fetch is separate from build
联网抓取 SHALL 只把原始响应写入 `data/raw/` 并记录抓取时间；快照构建 SHALL 不发起网络请求。需要联系人信息的接口（SEC）在未配置时 SHALL 拒绝抓取并说明需要配置的项，而不是使用占位值。大模型调用同样是联网操作：只有抽取命令 SHALL 调用模型，它把原始响应与账本写入 `data/raw/llm/`，把待复核结果写入 `data/manual/extractions/`；快照构建 SHALL 只读取已签字的抽取复核文件，不调用模型。

#### Scenario: Build works offline
- **WHEN** 缓存与材料齐全，在无网络环境执行构建
- **THEN** 构建成功，生成的快照内容与联网时一致

#### Scenario: SEC fetch without contact info
- **WHEN** 未配置 SEC 联系人信息时执行 SEC 抓取
- **THEN** 命令失败，错误信息指出需要设置的配置项名

#### Scenario: Missing cache is reported
- **WHEN** 构建时缺少某个抓取缓存
- **THEN** 依赖该缓存的字段留空并记入缺口清单，构建本身不失败

#### Scenario: Build without model keys
- **WHEN** 未配置任何模型密钥，且存在已签字的抽取复核文件
- **THEN** 构建成功，被接受的条目进入快照

## ADDED Requirements

### Requirement: Extractions revalidated at build
构建载入已签字的抽取复核文件时，SHALL 对每个被接受的条目重新校验：来源有本地存档，存档文本哈希与登记一致，原文片段按抽取规格的规范化规则仍是存档文本的子串，取值中的数字出现在片段中。任一校验失败 SHALL 使构建失败，并指出文件、条目与原因。

#### Scenario: Edited quote fails build
- **WHEN** 人工把某条目的片段改成原文中没有的句子并签字
- **THEN** 构建失败，错误信息指出该复核文件与条目

#### Scenario: Missing archive fails build
- **WHEN** 被接受条目的来源存档文件不存在
- **THEN** 构建失败，错误信息指出来源 ID
