# Tasks

## 1. 数据模型扩展

- [x] 1.1 新增 `ExclusionCategory`、`LinkStatus` 枚举；`Source` 增加 `published_date_text`、`link_status`、`link_checked_at`；`Target` 增加 `exclusion_category`。测试：非法排除类别被拒且错误信息列出允许取值；"2026-08" 只存原文，发布日期为空。
- [x] 1.2 `BuyerPreference` 改为按列存储；新增 `BuyerFinancial`、`BuyerProductLoe`、`method_note` 表；前端 `ENTITY_LABELS` 同步。测试：可以从买方查到偏好、财务、专利到期；`/api/meta` 计数包含新表。

## 2. 构建框架

- [x] 2.1 实现 `intel build`：写临时文件，成功后替换；输出缺口清单 `data/processed/gaps.csv` 和按原因汇总的计数。测试：校验错误时旧快照不变、命令非零退出；同一输入构建两次，实体与声明一致。
- [x] 2.2 实现 `intel fetch sec-tickers`：未配置 `SEC_USER_AGENT` 时报错，并指出配置项名；结果写入 `data/raw/sec/`。httpx 移到运行依赖。测试：未配置时报错、不发请求（用 mock 传输层）。

## 3. 买方材料导入

- [x] 3.1 导入来源登记（43 条）与两个工作簿来源，处理原始日期精度。测试：逐行与原表对账；`D:\` 路径的条目被保留。
- [x] 3.2 导入执行摘要：列映射表、按来源 ID 拆分声明、置信度映射、单元格坐标写入备注。测试：默沙东「核心证据」的声明数等于来源 ID 数；辉瑞的推断置信度为 medium_high；10 个买方逐字段与原表一致。
- [x] 3.3 导入治疗领域分析与技术类型分析（置信度继承并在备注中注明）。测试：每家 3 条、按优先级排序，名称与原表一致；60 行全部导入。
- [x] 3.4 导入买方概览两张子表与方法口径（列位置读取、公司别名表、"待核实"单元格进缺口）。测试：默沙东总收入 65.01 USD；含"待核实"的单元格为空并出现在缺口清单；未知公司名报错。

## 4. 标的全集

- [x] 4.1 导入 149 家指数清单；读取 SEC 缓存写入 CIK 与声明，未映射的进缺口；缓存不存在时整体记缺口，构建不失败。测试：使用小型 fixture 对照文件，覆盖已映射、未映射、缓存缺失三种情况。
- [x] 4.2 实现 Stage 0 CSV 读取：只应用已核实的行，生成带来源的声明，打印未核实行数。测试：已核实的 acquired 行生成 fact 声明；未核实的行不生效；候选池数加排除数等于 149。
- [x] 4.3 [人工] AI 起草 `data/manual/stage0_exclusions.csv`（类别、理由、一手来源 URL），交用户逐行核实并填写 `verified_by`。验收：每行都有可打开的一手来源；用户核实完毕。

## 5. 链接检查

- [x] 5.1 实现 `intel fetch links`：HEAD 失败时回退到 GET，按状态码分类，本地路径不发请求，结果写入 `data/raw/links/`；`build` 把结果写入来源表。测试：用 mock 传输层覆盖 200、403、404、DNS 失败、本地路径五种情况。

## 6. 真实数据构建与验收

- [x] 6.1 [人工] 用户在 `.env` 中设置 `SEC_USER_AGENT`；执行 `intel fetch sec-tickers`、`intel fetch links` 和 `intel build`；提交快照、缺口清单与原始缓存。验收：`intel check-provenance` 退出码为 0；构建输出中买方 10 家、标的 149 家（实际来源 59 条：对方 43 + 两个工作簿 + SEC 对照表 + Stage 0 新增 13）；缺口清单汇总已审阅。
- [x] 6.2 更新 `CLAUDE.md` 命令小节（fetch / build），并在 `docs/ai-log.md` 记录本变更中 AI 的工作（导入映射、排除名单起草及核实结果）。验收：文档中的命令照抄即可运行。

## Workflow follow-up

- 完成后用 `/opsx:verify` 核对，再归档；在 change plan 中勾选 B。
