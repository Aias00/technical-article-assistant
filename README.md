# 技术文稿核稿与排版助手

一个可安装技能，默认从主题、资料或初稿直接交付技术文章与配套网页PPT：Markdown、公众号HTML、演示页面和逐页讲稿。只保留根 `SKILL.md`，不依赖另外安装审稿、预检或排版技能。

## 使用方式

安装整个目录后，让宿主AI使用本技能处理Markdown或粘贴正文：

- “只核稿，别改原文”：输出问题清单。
- “核稿并修订”：输出问题清单与修订稿。
- “完整处理这篇稿子”：默认输出问题清单、修订稿、公众号HTML和网页PPT。
- “只要文章，不需要PPT”：输出问题清单、修订稿及HTML。
- “只排版，别改文字”：跳过AI修订与文风检查，生成HTML。
- “把修订稿做成瑞士风分享PPT”：生成演示大纲、网页幻灯片和讲稿。

核稿与修订由宿主AI按SKILL.md执行，Python入口只执行本地检查和排版。

## 增强能力

- 来源留存：主张对应官方资料/源码、版本与读取时间。
- 代码验证记录：区分实跑、静态核对、未执行和伪代码；不会自动执行稿件代码。
- 本地预检：图片存在性、顶层代码围栏闭合、代码块清单和输入摘要。
- 平台交接：公众号HTML或修订Markdown交给独立腾讯发布器，不内置登录和提交。
- 修复代码保真：代码围栏和缩进代码里的`# `注释不会再作为标题删除。

## 默认成品

宿主AI完成核稿修订和演示计划后，统一命令实际装配文章与幻灯片：

```bash
.venv/bin/python scripts/run.py --input /abs/revised.md --output /abs/delivery/article.html --slides-plan /abs/slides-plan.json
```

计划由宿主根据文章编写，不要求用户手工填写。详见 [联合交付](references/joint-delivery.md)。只准备模板不能算交付完成；网页PPT为HTML而非.pptx。

## 本地运行（单独排版与检查）

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/run.py --input examples/article.md --output output/article.html
# 只排版（保留原文措辞）
.venv/bin/python scripts/run.py --mode format --input examples/article.md --output output/article.html
.venv/bin/python -m unittest discover -s tests -v
# 可追溯的本地检查报告（不执行代码）
.venv/bin/python scripts/inspect_article.py --input examples/article.md --output output/inspection.json
# 生成一个完整的技能安装包
.venv/bin/python scripts/package_skill.py
```

可选 `--theme mist-blue` 或 `--cover /path/to/cover.png`；默认科技色 `ai-tech`。

## 项目结构

```text
SKILL.md                 唯一技能入口及四种模式
scripts/                 统一执行入口、检查、排版与打包
references/              核稿、改写与排版规则
assets/themes/           CSS主题
examples/                脱敏演示样稿
tests/                   回归测试及样稿
requirements.txt         Python依赖
```

## 验证范围

普通文章本地流程不调用网络、不需要发布账号、不上传图片；可选演示能力的网络范围见下方说明。不能保证技术事实正确、涉密识别或全面合规；HTML检查不等于完成视觉验收。依赖安装需要访问包源。
宿主兼容性及语义核稿质量需按目标环境验证。行为试运行与用例见 `evals/`；项目提取历史单独保存在 `docs/extraction-history.md`。

## 来源

提取并整合自 https://github.com/Aias00/agent-skills ，保留Apache-2.0许可证。第三方依赖各自许可证仍适用。

Windows PowerShell使用 `.venv\Scripts\python.exe` 替换上述解释器路径，详见 [环境准备](references/environment.md)。

## 网页PPT运行时

整合 [Guizang PPT Skill](https://github.com/op7418/guizang-ppt-skill) 的杂志风与瑞士风模板、演讲者模式和校验器。输出是HTML，不是.pptx。

```bash
.venv/bin/python scripts/presentation.py setup
.venv/bin/python scripts/presentation.py prepare --input /abs/revised.md --output-dir /abs/slides --style swiss
# 宿主AI按联合交付规范生成页面计划后：
.venv/bin/python scripts/presentation.py render --directory /abs/slides --plan /abs/slides-plan.json
.venv/bin/python scripts/presentation.py validate --directory /abs/slides
```

prepare仅准备模板，不代表完成演示；校验需要Node.js。依赖安装需要Git和网络，演示可能访问字体/图标CDN。
上游使用AGPL-3.0，通过固定版本独立下载；模板不以本项目Apache许可证重新分发。生成目录保留上游LICENSE、来源及对应源码，分发时一并携带。详见 [演示流程](references/presentation.md)。
