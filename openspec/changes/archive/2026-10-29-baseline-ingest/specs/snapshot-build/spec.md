# Spec Delta

## Purpose

规定数据快照如何生成：联网抓取只写本地缓存，快照构建只读缓存、对方材料与人工核实文件，从零确定性重建，并输出缺口清单，使任何人都能复现同一份快照。

## ADDED Requirements

### Requirement: Fetch is separate from build
联网抓取 SHALL 只把原始响应写入 `data/raw/` 并记录抓取时间；快照构建 SHALL 不发起网络请求。需要联系人信息的接口（SEC）在未配置时 SHALL 拒绝抓取并说明需要配置的项，而不是使用占位值。

#### Scenario: Build works offline
- **WHEN** 缓存与材料齐全，在无网络环境执行构建
- **THEN** 构建成功，生成的快照内容与联网时一致

#### Scenario: SEC fetch without contact info
- **WHEN** 未配置 SEC 联系人信息时执行 SEC 抓取
- **THEN** 命令失败，错误信息指出需要设置的配置项名

#### Scenario: Missing cache is reported
- **WHEN** 构建时缺少某个抓取缓存
- **THEN** 依赖该缓存的字段留空并记入缺口清单，构建本身不失败

### Requirement: Deterministic rebuild
快照构建 SHALL 从零生成新的快照并在成功后替换旧快照；同样的输入两次构建，除生成时间外业务数据与声明完全相同。构建失败时旧快照保持不变。

#### Scenario: Rebuild is repeatable
- **WHEN** 对相同输入连续构建两次
- **THEN** 两次的实体与声明内容一致

#### Scenario: Failed build keeps old snapshot
- **WHEN** 构建过程中出现写入校验错误
- **THEN** 原快照文件不变，命令以非零状态退出

### Requirement: Gap report
构建 SHALL 输出缺口清单文件，每条记录实体、字段、原因与原始位置（表名与单元格，或接口名），并在命令输出中给出汇总计数。

#### Scenario: Gap report written
- **WHEN** 构建完成且存在待核实单元格或未映射 ticker
- **THEN** 缺口清单文件列出每一条，命令输出按原因汇总数量
