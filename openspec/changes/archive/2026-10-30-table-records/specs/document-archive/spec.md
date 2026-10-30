## MODIFIED Requirements

### Requirement: Text conversion
系统 SHALL 把 HTML 与 PDF 转为纯文本：去掉脚本、样式与内联 XBRL 头；块级元素与表格行换行；PDF 按页提取并标注页码。HTML 中的表格 SHALL 另外逐格展开，追加在正文之后：每个数据格一行，同一行内写出表序号、表题（若有）、行名、列名与格内的值，使引用这一行就能同时引用该值的表头。表头 SHALL 取自表格中的文字，不得补写；无法识别表头的表格行按原样输出、不展开。转换结果 SHALL 是确定的：同一原文两次转换得到相同文本。无法提取文本的 PDF（扫描件）SHALL 记入缺口，不做 OCR。

#### Scenario: Inline XBRL header removed
- **WHEN** 转换一份含 `ix:header` 的 10-Q
- **THEN** 文本不含 XBRL 头中的隐藏事实，正文段落保留

#### Scenario: Scanned PDF reported
- **WHEN** 一份 PDF 提取出的文本为空
- **THEN** 该文档记为无可用文本，后续抽取跳过它

#### Scenario: Table cell carries its headers
- **WHEN** 转换一张表：表题「Change in Body Weight Following 21 Weeks」，列标题「VK2735 15 mg QW (n=14)」，行名「Mean percent change from baseline」，格值「-16.3%」
- **THEN** 文本中有一行同时含表题、行名、列标题与「-16.3%」

#### Scenario: Split table keeps header
- **WHEN** 一张表在网页中被拆成两张，后一张没有表头且列数相同
- **THEN** 后一张的数据格沿用前一张的列标题展开

#### Scenario: Unrecognized table left as rows
- **WHEN** 一张表找不到全为文字的表头行
- **THEN** 该表按原样逐行输出，不生成逐格记录
