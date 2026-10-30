## Purpose

规定非结构化一手文档（SEC 申报正文与附件、公司新闻稿、IR 页面、PDF 演示与会议摘要）如何列入清单、抓取、转为文本并存档登记，使每个抽取值都能回到一份带哈希的本地原文。

## ADDED Requirements

### Requirement: Document list
系统 SHALL 从人工维护的文档清单读取待抓取文档。每行记录公司 ticker、URL、来源类型、标题、发布日期（可为年月）与来源 ID。来源 ID 可以填已登记的来源 ID（例如复核文件已引用的 `MAN-` 来源），此时抓取结果挂到该来源上，不重复登记；留空时系统按 URL 生成稳定的 `DOC-` 来源 ID。来源类型 SHALL 取 sec_filing、press_release、company_ir、publication、fda_web 之一。

#### Scenario: Reuse an existing source id
- **WHEN** 清单一行的来源 ID 是人工来源登记中已有的 `MAN-VKTX-2`
- **THEN** 该文档的存档登记在 `MAN-VKTX-2` 下，快照中只有一条该来源

#### Scenario: Generated id is stable
- **WHEN** 来源 ID 留空的同一行在两次抓取之间未改动 URL
- **THEN** 两次得到相同的 `DOC-` 来源 ID

#### Scenario: Invalid row rejected
- **WHEN** 一行的来源类型不在允许集合内，或 URL 不是 http(s)
- **THEN** 抓取命令报告该行号与原因，跳过该行，其余行照常抓取

### Requirement: Filing discovery
系统 SHALL 提供命令，按 ticker 列出 EDGAR 近期 10-K、10-Q、8-K 申报及每份申报的附件（文件名、类型、说明），供人工挑选写入文档清单。该命令只打印结果，不改动清单。

#### Scenario: Exhibits listed
- **WHEN** 对一家公司执行申报列表命令
- **THEN** 输出每份 8-K 的 Exhibit 99.1 等附件的完整 URL

### Requirement: Fetch and archive
文档抓取 SHALL 把原始字节与转换后的纯文本写入 `data/raw/docs/<TICKER>/`，并记录 URL、抓取时间、原文哈希与文本哈希。sec.gov 的请求 SHALL 使用已配置的 SEC 联系人信息并遵守 SEC 限速；其他站点每次请求之间至少间隔 0.5 秒。已存档的文档默认不重新抓取。站点拒绝访问（401/403/429 重试后仍失败）时 SHALL 记录为拒绝访问，不绕过站点防护。

#### Scenario: Cached document skipped
- **WHEN** 文档已存档且未指定重新抓取
- **THEN** 不发起网络请求，存档与哈希不变

#### Scenario: Blocked site recorded
- **WHEN** 某 IR 页面返回 403
- **THEN** 该文档记为拒绝访问并写入抓取日志，其余文档继续抓取

### Requirement: Text conversion
系统 SHALL 把 HTML 与 PDF 转为纯文本：去掉脚本、样式与内联 XBRL 头；块级元素与表格行换行；PDF 按页提取并标注页码。转换结果 SHALL 是确定的：同一原文两次转换得到相同文本。无法提取文本的 PDF（扫描件）SHALL 记入缺口，不做 OCR。

#### Scenario: Inline XBRL header removed
- **WHEN** 转换一份含 `ix:header` 的 10-Q
- **THEN** 文本不含 XBRL 头中的隐藏事实，正文段落保留

#### Scenario: Scanned PDF reported
- **WHEN** 一份 PDF 提取出的文本为空
- **THEN** 该文档记为无可用文本，后续抽取跳过它

### Requirement: Archive integrity
快照中被抽取引用的文档来源 SHALL 记录本地存档路径与文本哈希。存档文本被改动后，依赖它的抽取结果 SHALL 不能进入快照。

#### Scenario: Tampered archive
- **WHEN** 存档文本在签字后被修改
- **THEN** 构建失败，指出来源 ID 与哈希不一致
