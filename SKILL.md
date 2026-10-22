---
name: technical-article-assistant
description: 审阅、修订并排版中文技术文稿。适用于技术宣传稿、工程实践和技术分享文章，支持只核稿、核稿修订、完整处理及仅排版，交付问题清单、修订稿和微信公众号 HTML。
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

## 核稿与修订

核稿时读取 [评审依据](references/review-rubric.md)。按技术事实、证据、结构、表达的顺序检查；涉及平台退稿时再读 [平台要求](references/platform-compliance.md)，修订时读 [改写规则](references/rewrite-playbook.md)。

- 核实版本、API、数据、前提与代码示例，区分事实、推断与待核实项。没有依据就标记待核实，不编造数字、来源和测试结果。
- review.md 记录问题严重程度、段落位置、原文片段、原因、证据或待核实项、修改建议；没有发现时如实说明审阅范围。
- 修订保持原意、责任主体、术语、代码和用户指定的保护内容。事实纠正注明依据，无法核实的结论保持不确定性。
- revised.md 是后续排版的唯一来源。review.md 补充修改摘要及尚未解决的问题，不能因脚本通过就宣称技术内容准确。
- 只核稿模式不生成修改稿，也不执行排版。核稿修订模式对 revised.md 执行 `scripts/check_banned_scaffolding.py --input <文件>`。

## 检查与排版

首次使用，在技能根目录创建虚拟环境并安装 `requirements.txt`（Python 3.10+）。以下路径均相对本 SKILL.md，实际调用时解析为安装目录的绝对路径；使用同一个虚拟环境执行子脚本。

完整处理在AI核稿修订后运行：

```bash
.venv/bin/python scripts/run.py --input /绝对路径/revised.md --output /绝对路径/article.html --theme ai-tech
```

仅排版运行：

```bash
.venv/bin/python scripts/run.py --mode format --input /绝对路径/original.md --output /绝对路径/article.html --theme ai-tech
```

`format`跳过文风检查，仍检查HTML结构；不修改Markdown，HTML按公众号正文规则移除元数据和一级标题。默认模式`check-format`依次执行文风检查、排版、HTML检查；可选 `--cover /绝对路径/cover.png`。任何步骤失败都不得交付为通过，已生成文件只能视为中间产物。

文风命中需结合上下文判断，不能为了通过而改变事实；无法消除时说明阻塞。完整处理发现未核实的关键事实时，可生成排版草稿，但应在交付说明中明确“待核实”，不能宣称可直接发布。

科技色默认 `ai-tech`；其他主题和排版限制见 [排版说明](references/formatting.md)。有浏览器能力时检查图片、列表、代码块和主题；未做视觉检查应明确说明。

## 交付与边界

最终列出实际文件位置、修改摘要、检查结果与未解决事项，按模式交付，不能伪造缺失产物。
本技能不发布文章、不上传图片、不执行公众号账号操作；不能保证识别全部技术错误、涉密内容或合规问题。

本地脚本读取输入、主题及技能文件，写指定输出，调用包内Python子进程，无需Token或网络。依赖安装需要包源访问，宿主AI的数据处理遵循所在环境规定。使用脱敏数据，不打包凭据。

安装包以本目录为一个整体，保留唯一根SKILL.md、scripts、references、assets及requirements.txt。元景的文件读写、Python、依赖安装及子进程能力仍需真实环境验证。
