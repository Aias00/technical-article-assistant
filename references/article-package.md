# 稿件包与证据留存

## 按需交付

quick默认只交付文章、HTML、轻量PPT及简短review.md；不强制生成本文件列出的完整档案。只核稿交付review.md；仅排版交付HTML；默认联合交付或用户要求可追溯稿件包时，使用：

```text
<output>/
  review.md          核稿报告、结论与未解决事项
  revised.md         唯一修订稿及下游输入
  article.html       由revised.md派生的公众号正文
  sources.md         实际使用的来源与主张对应关系
  verification.md    代码/配置的实际验证或未执行原因
  inspection.json    本地检查报告
  meta.json          标题、文种、来源文件和交付状态
  images/            实际使用且获准复制的图片（可选）
  slides-plan.json   从修订稿编写的页面与讲稿计划
  slides/
    index.html       实际网页PPT（不能是空模板）
    outline.md       逐页大纲与讲稿要点
    presentation.json 来源摘要、风格与演示检查状态
    LICENSE、NOTICE.md、upstream-source/ 上游授权及对应源码
```

原始稿件保留原路径；用户有article.md时，以它为输入，revised.md为本次修订结果，不再来回修改两个主稿。用户要求回写原文件时再按其指令执行。
原文引用的相对图片路径以Markdown所在目录解析。另存修订稿时，复制获准使用的图片到稿件包，或更新为在新目录有效的路径；不能把断开的图片引用当检查通过。

## 来源台账 sources.md

每条来源记录：标识（S1等）、标题、URL或本地路径、版本/提交、发布日期（已知时）、实际读取时间、支持的具体主张、原始事实与本次推断、访问限制。

- 官方文档应对应主张中的版本，不能以最新文档推断旧版。
- 仓库资料包括相关源码位置、提交和运行环境，不仅是README。
- 新闻及社交内容保留归属；讨论不能替代性能或API证据。
- 用户提供的内部资料可记录本地路径，不复制敏感正文到外部服务。
- 未查证时记录“未读取/待核实”；没有来源时如实注明。不得虚构检索时间或写“已查官方”代替来源。
- 不默认收集热点或大规模下载材料；只补足本次稿件关键主张需要的证据。

## meta.json

仅写实际发生的状态，示意结构：

```json
{
  "title": "稿件标题",
  "article_type": "technical|work-summary|promotion|opinion",
  "canonical_markdown": "revised.md",
  "review": {"verdict": "Needs revision", "report": "review.md"},
  "sources": "sources.md",
  "verification": "verification.md",
  "inspection": "inspection.json",
  "targets": ["wechat", "html-slides"],
  "presentation": {"index": "slides/index.html", "status": "pending"},
  "publication": {"status": "not_requested"}
}
```

article_type从四个标识中选择一个，混合稿可另加章节类型说明。没有代码/配置时verification.md记录not_applicable及实际核验范围，不生成伪造运行日志。

按实际文种和文件替换示意值，不生成不存在文件的引用。JSON使用UTF-8且能被标准解析器读取；本地报告中的输入摘要可用于判断后续修改是否让检查失效。修改Markdown后重新检查和排版。
