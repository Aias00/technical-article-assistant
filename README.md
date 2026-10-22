# 技术文稿核稿与排版助手

一个可安装技能，完成技术文稿核稿、修订、预检和公众号排版。只保留根 `SKILL.md`，不依赖另外安装审稿、预检或排版技能。

## 使用方式

安装整个目录后，让宿主AI使用本技能处理Markdown或粘贴正文：

- “只核稿，别改原文”：输出问题清单。
- “核稿并修订”：输出问题清单与修订稿。
- “核稿并用科技色排版”：输出问题清单、修订稿及HTML。
- “只排版，别改文字”：跳过AI修订与文风检查，生成HTML。

核稿与修订由宿主AI按SKILL.md执行，Python入口只执行本地检查和排版。

## 本地运行

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/run.py --input examples/article.md --output output/article.html
# 只排版（保留原文措辞）
.venv/bin/python scripts/run.py --mode format --input examples/article.md --output output/article.html
.venv/bin/python -m unittest discover -s tests -v
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

## 验证与参赛边界

本地流程不调用网络、不需要发布账号、不上传图片。不能保证技术事实正确、涉密识别或全面合规；HTML检查不等于完成视觉验收。依赖安装需要访问包源。
元景安装、宿主AI核稿效果、真实提效数据与竞赛录屏尚待验证；不声明已满足市场上架条件。

## 来源

提取并整合自 https://github.com/Aias00/agent-skills ，保留Apache-2.0许可证。第三方依赖各自许可证仍适用；参赛独立开发归属需要另行核实。
