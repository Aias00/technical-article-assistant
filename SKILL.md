---
name: technical-article-assistant
description: 从主题、资料或初稿生成文章与配套网页PPT，支持技术文章、工作总结/复盘、企业宣传/产品介绍、行业观察/观点。默认快速交付Markdown、公众号HTML及轻量演示讲稿；也支持只审稿、润色或排版（article review, writing, slides, Markdown-to-WeChat）。
---

# 文章与演示文稿助手

文章和PPT共用revised.md。宿主负责内容与语义，脚本负责检查与渲染；不把脚本通过当作事实、代码实跑或视觉验收通过。

## 输出模式

| 用户需求 | 交付 |
|---|---|
| 写文章、完整处理、文章与PPT | review.md、revised.md、article.html、slides/index.html与逐页讲稿（默认） |
| 只核稿、只找问题 | review.md，不改原文 |
| 审稿修订、润色 | review.md与revised.md |
| 只要文章、不需要PPT | review.md、revised.md、article.html |
| 仅排版、不改文字 | article.html，跳过语义修订与文风检查 |
| 仅转PPT | slides/index.html与outline.md，不额外生成文章HTML |

主题、URL、Markdown或正文均可作为输入。原稿保留，修订稿另存；同名输出先读取，避免覆盖其他任务。

## 工作量档

- **quick（默认）**：只加载 [快速交付](references/quick-delivery.md)与一种文种规则。一次成稿、一次重点核对；模型只写PPT要点与讲稿，不写HTML、不加载高级模板。默认短稿与3–5页basic纯文本演示，尊重用户明确的篇幅和保留要求。
- **standard**：用户要求完整资料留存、图片/自由布局或magazine/swiss风格时，读 [完整联合交付](references/joint-delivery.md)，必要时加载 [高级演示](references/presentation.md)。
- **research**：深度查证、代码实跑或研究长稿时扩大验证；不承诺三分钟完成。

输出模式和工作量档独立，用户明确要求优先。不把高级风格降成basic却声称已满足，也不自动给只要文章的任务附PPT。

## 内容规则

1. 按 [文种选择](references/article-types.md)判断，用户指定优先，仅加载相应types规则；混合稿按章节适用。核稿使用 [通用依据](references/review-rubric.md)，不让非技术稿补代码。
2. quick优先核对用户提供材料；缺证据标待核实/待补充，不扩大无关检索。重要公开主张需要进一步确认时升级查证或保留待核实状态，不能为速度给未经证实的Ready结论。
3. 不编造数字、客户案例、业绩或引语。区分事实、推断、建议、预测和已完成事项，保留原意、责任主体、数字口径、限定词、代码与引用归属。
4. review.md按 [报告结构](references/review-template.md)简记结论、修改与剩余事项，不打百分制。standard/research或用户要求追溯时再按 [稿件包](references/article-package.md)留完整台账。
5. 只在代码/配置支撑结论时读 [代码验证](references/code-verification.md)；没有执行就记not_run，不生成假日志。内部资料不发送外部检索。
6. 修订时按需读 [改写规则](references/rewrite-playbook.md)。文风默认advisory只提示，strict仅在明确要求严格去套话时使用；不因关键词命中改动事实或引用。

## 快速运行

首次`python scripts/bootstrap.py`：复用可用环境，缺依赖才安装4项核心包。需要Python 3.10+；Windows可用`py -3`，详见 [环境准备](references/environment.md)。无需每篇稿件重建环境。

宿主按quick-delivery.md编写绑定真实源稿摘要的basic计划后，直接装配成品：

```bash
python scripts/bootstrap.py -- run.py --input /abs/revised.md --output /abs/delivery/article.html --slides-plan /abs/plan.json
```

单独文章不传slides-plan；仅排版加`--mode format`。文风可用`--style-check advisory|strict|off`。改稿时稳定页面ID、更新计划摘要，basic可加`--reuse`复用未变页面；手工改过的HTML拒绝覆盖。
科技色为ai-tech；其他主题及微信图片交付见 [排版说明](references/formatting.md)。basic纯HTML无CDN，不需要Git/Node；高级Guizang首次需要独立下载固定依赖并保留AGPL来源和对应源码。

## 完成条件

按模式给出实际成品路径与简短核稿结论。默认必须有完整文章、实际幻灯片和逐页讲稿，不能只交空模板或操作步骤。失败说明哪部分完成，继续可恢复步骤；不伪造产物或检查结果。
保留文章到PPT的数字、口径及不确定性。timings.json记录脚本阶段，不含模型写稿、检索、Python环境准备或人工预览；高级上游下载若发生会计入setup阶段。没有实测就不承诺三分钟。
有浏览器能力时检查翻页、讲稿、布局与图片，未测则说明。公众号本地图片需上传替换并预览；网页PPT不是.pptx。
用户要求后续发布时读 [平台交接](references/platform-handoff.md)，本技能不自动登录、上传或发布。
