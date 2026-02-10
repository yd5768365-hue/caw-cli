# 大模型RAG应用开发之PDF解析工具对比

# 一 汇总

| 类型 | 名称 | 地址 | OCR | 提取表格内容 | 保留文本顺序 | 提取图片 | 保存成md格式 | 其他特性 |
|---|---|---|---|---|---|---|---|---|
| 传统PDF解析库 | pymupdf | github.com/pymupdf/PyM… | ❌ | ✔️ | ✔️ | ✔️ | ❌ | ● 表格提取 ● 自定义字体 |
| 传统PDF解析库 | pdfminer | github.com/pdfminer/pd… | ❌ | ❌ | ✔️ | ❌ | ❌ | ● 版面分析 |
| 传统PDF解析库 | pdfplumber | github.com/jsvine/pdfp… | ❌ | ✔️ | ❌ | ❌ | ❌ | ● 表格提取，但存在丢失列的问题 |
| 传统PDF解析库 | pypdf2 | github.com/py-pdf/pypd… | ❌ | ❌ | ✔️ | ❌ | ❌ | ● pdf合并与拆分 ● 添加水印 |
| 基于模型的PDF解析一体库 | llama-parse | github.com/run-llama/l… | ✔️ | ✔️ | ✔️ | ✔️ | ✔️ | ● 付费API每天有免费额度 |
| 基于模型的PDF解析一体库 | open-parse | github.com/Filimoa/ope… | ✔️ | ✔️ | ✔️ | ❌ | ✔️ | ● 文本支持保存markdown和html格式 ●内置表格模型，可自由选择 ●表格带markdown格式 |
| 基于模型的PDF解析一体库 | deepdoc | github.com/infiniflow/… | ✔️ | ✔️ | ✔️ | ✔️ | ❌ | ● 支持版面分析 ●表格带html格式 |
| 基于模型的PDF解析一体库 | MinerU | github.com/opendatalab… | ✔️ | ✔️ | ✔️ | ✔️ | ✔️ | ●  文本带markdown格式 ● 解析保留中间过程，可用于二次调优 ● 表格提取非常慢，目前效果一般 |

# 二 总结

- 非扫描件无OCR要求直接使用 `pymupdf(fitz)` 即可，能正确保留双列布局的文本顺序，同时能提取表格和图片，而且表格是以 `List` 的格式保留。
- 其余几个传统的PDF解析库倾向于对pdf进行编辑，比如添加水印，增加或者删除页面等。
- `llama-parse` 中文文档效果不好，而且还是通过API使用，但是每天有固定的免费额度，可以用于处理扫描件。
- `deepdoc` 和 `MinerU` 是近期开源项目中比较强大的RAG解析工具。 `deepdoc` 优势点在于表格效果较好，亲测无边框的表格有大多数效果仍可圈可点，并且保留为html格式，因此允许合并单元格； `MinerU` 优势在于识别的文本带有markdown格式，因此用于RAG切分文档中可以省去不少功夫。
