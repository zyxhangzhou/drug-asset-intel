# Tasks

## 1. 表格展开

- [x] 1.1 在 `src/intel/docs/text.py` 用 `html.parser` 解析 HTML 表格：单元格内换行与块级标签补空格、去掉 `<sup>` 脚注、合并只含 `$`、`)`、`%` 的符号格、去掉空格；表格内单格行与表前最近一段短文字作为表题；识别表头行（数据格全为非数值文字）；列数相同且无表头的后续表沿用上一张表头。验证：用 VKTX 新闻稿夹具测试「Table cell carries its headers」「Split table keeps header」「Unrecognized table left as rows」三个场景，以及两次转换结果相同。
- [x] 1.2 （实现时补充：表格取值的片段不限段数，见 `llm-extraction` 规格修改）`to_text` 对 HTML 输出「正文 + 表格记录段」；抽取提示词说明表格记录的格式与引用方式。验证：现有 `tests/test_docs.py` 全部通过；提示词测试检查含表格记录说明。

## 2. 样例重跑

- [x] 2.1 `intel fetch docs --refresh` 重新转换 VKTX 样例；确认已签字复核文件仍能构建（片段仍在文本中、指纹已更新）。验证：`intel build` 成功，`check-provenance` 为 0。
- [x] 2.2 [人工] 空闲时段对 VKTX 样例重跑抽取（另存当前复核文件的新条目，已签字条目保留），用 `intel extract report` 对比表格结果的数字校验通过率。验证：报告中表格来源条目通过校验；结果写入 `docs/ai-log.md`。

## Workflow follow-up

- 用户复核新增条目后签字；核验并归档本变更。
