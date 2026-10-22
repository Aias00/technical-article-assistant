---
name: technical-article-assistant
description: 审稿、核稿、润色技术文章及公众号排版，将 Markdown 转微信公众号 HTML。用于技术宣传稿、工程实践和架构分享的 review、polish、Markdown-to-WeChat formatting，可留存来源与代码验证记录，交付问题清单、修订稿或排版文件。
---

# 技术文稿核稿与排版助手

一个技能完成核稿、修订、检查和排版。AI语义审阅由宿主执行，本地脚本提供文风检查和HTML生成，不需要调用其他技能。

## 选择模式

| 用户需求 | 模式 | 交付 |
|---|---|---|
| 只审不改、找问题 | 只核稿 | review.md |
| 审稿并修改、润色 | 核稿修订 | review.md、revised.md |
| 核稿并排版、生成完整稿件包 | 完整处理（未指定时默认） | review.md、revised.md、article.html |
| 只排版、原文不要改 | 仅排版 | article.html，保留原文措辞 |

输入是Markdown文件或用户提供的正文；可附目标读者、修改边界、证据、主题和封面。缺省按中文技术分享稿处理。原文保留，所有交付写入独立输出目录；已有同名文件先读取，避免覆盖其他任务产物。

## 来源与验证记录

完整处理或用户要求可追溯稿件包时，按 [稿件包规范](references/article-package.md) 保存sources.md、verification.md和meta.json；简单核稿或仅排版不强制增加文件。来源留存只记录实际读取的资料，版本、源码位置、检索时间与主张对应；另存修订稿时保持图片路径有效。

代码或配置支撑主要结论时，读取 [代码验证规范](references/code-verification.md)：核对固定版本与实际输出，有工具及合适环境时实跑可执行示例；伪代码与不可执行片段分别注明。未执行记not_run，不把静态检查通过当运行验证。

## 核稿与修订

核稿时读取 [评审依据](references/review-rubric.md)。按文种检查技术事实、证据、结构和表达，不强制宣传稿或架构分享包含命令；涉及平台退稿时再读 [平台要求](references/platform-compliance.md)，修订时读 [改写规则](references/rewrite-playbook.md)。

- 有检索或源码读取能力时主动核对版本号、API行为与关键主张，以对应版本官方文档或源码为准并记录来源；工具不可用或无法确认时标待核实。外部检索不发送内部资料。区分事实、推断与待核实项，不编造数字、来源和测试结果。
- 按 [核稿报告模板](references/review-template.md) 输出review.md：包含文种、Ready/Needs revision/Blocked结论、核验限制及Critical/Major/Minor问题，记录位置、原文、原因、依据和建议；不打百分制分数。
- 修订保持原意、责任主体、术语、代码和用户指定的保护内容。事实纠正注明依据，无法核实的结论保持不确定性。
- revised.md 是后续排版的唯一来源。review.md 补充修改摘要及尚未解决的问题，不能因脚本通过就宣称技术内容准确。
- 只核稿模式不生成修改稿，也不执行排版。核稿修订模式对 revised.md 执行 `scripts/check_banned_scaffolding.py --input <文件>`。

## 检查与排版

首次使用，先检查Python版本及Markdown、BeautifulSoup、cssutils、Pygments能否导入；仅在缺少环境或依赖时创建虚拟环境并安装 `requirements.txt`（Python 3.10+）。跨平台命令见 [环境准备](references/environment.md)。以下路径均相对本 SKILL.md，实际调用时解析为安装目录的绝对路径；使用同一个虚拟环境执行子脚本。

完整处理在AI核稿修订后运行：

```bash
.venv/bin/python scripts/run.py --input /绝对路径/revised.md --output /绝对路径/article.html --theme ai-tech
```

仅排版运行：

```bash
.venv/bin/python scripts/run.py --mode format --input /绝对路径/original.md --output /绝对路径/article.html --theme ai-tech
```

`format`跳过文风检查，仍检查HTML结构；不修改Markdown，HTML按公众号正文规则移除元数据和一级标题。默认模式`check-format`依次执行Markdown本地检查、文风检查、排版、HTML检查；Markdown检查发现缺图或未闭合顶层代码围栏时失败，不下载远端图片，也不运行代码；可选 `--cover /绝对路径/cover.png`。任何步骤失败都不得交付为通过，已生成文件只能视为中间产物。

文风命中需结合上下文判断，不能为了通过而改变事实；无法消除时说明阻塞。完整处理发现未核实的关键事实时，可生成排版草稿，但应在交付说明中明确“待核实”，不能宣称可直接发布。

以上为macOS/Linux命令；Windows使用 `.venv\Scripts\python.exe` 替换解释器路径。科技色默认 `ai-tech`；其他主题和排版限制见 [排版说明](references/formatting.md)。有浏览器能力时检查图片、列表、代码块和主题；未做视觉检查应明确说明。

完整稿件包可另存本地检查报告：

```bash
.venv/bin/python scripts/inspect_article.py --input /绝对路径/revised.md --output /绝对路径/inspection.json
```

该报告只证明本地图片存在与顶层围栏闭合，并列出代码块摘要及not_run状态，不证明事实、图片内容或代码正确。

## 交付与边界

最终列出实际文件位置、修改摘要、检查结果与未解决事项，按模式交付，不能伪造缺失产物。交付公众号HTML时提醒在浏览器复制渲染正文，在公众号后台重新上传并替换本地图片，最后在微信编辑器及手机预览核对标题、图片、代码和样式；未经验证不得宣称粘贴效果一致。
目标为腾讯社区或用户要求后续发布时，按 [平台交接说明](references/platform-handoff.md) 准备Markdown和图片，确认实际安装的发布器能力后交接，不把公众号HTML当通用输入。本技能不发布文章、不上传图片、不执行公众号账号操作；不能保证识别全部技术错误、涉密内容或合规问题。

本地脚本读取输入、主题及技能文件，写指定输出，调用包内Python子进程，无需Token或网络。依赖安装需要包源访问，宿主AI的数据处理遵循所在环境规定。使用脱敏数据，不打包凭据。

安装包以本目录为一个整体，保留唯一根SKILL.md、scripts、references、assets及requirements.txt。目标宿主的文件读写、Python、依赖安装及子进程能力需按实际环境验证。
