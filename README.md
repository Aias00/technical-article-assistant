# 技术文稿核稿与排版助手

从 agent-skills 提取的独立技能项目，包含技术文章审阅、发布前检查与微信公众号 HTML 排版。

## 模块

- technical-article-review：由宿主 AI 执行技术文稿审阅与修改。
- technical-article-preflight：本地文案、HTML、封面检查；原发布干跑依赖未打包的 wechat-publisher。
- wechat-article-formatter：Markdown 转内联样式 HTML。

## 当前边界

推荐使用下方统一入口，历史发布预检接口仅供溯源。

尚未验证元景数字员工兼容性；本地脚本检查不能证明技术事实准确、涉密合规或内容质量。外部发布服务不在提取范围内。

## 来源

提取自 https://github.com/Aias00/agent-skills ，保留原项目 Apache-2.0 许可证。第三方组件依其各自许可证使用；参赛原创归属仍需另行确认。

## 统一入口

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/run.py --input examples/article.md --output output/article.html --theme ai-tech
.venv/bin/python -m unittest discover -s tests -v
```

由宿主 AI 按根 SKILL.md 先生成问题清单与修订稿，再执行本地脚本。脚本不会调用模型，也不会发布文章。科技色使用 ai-tech 主题。
封面检查为可选项，可追加 `--cover /path/to/cover.png`。命中风格规则、排版失败或 HTML 校验失败均返回非零状态。

## 元景参赛待办

- 在干净元景环境验证安装、Python依赖、文件读写与子进程能力。
- 用脱敏样稿验证 AI 核稿和修订，人工标注漏报、误报与事实保真情况。
- 实测人工处理与技能处理耗时，记录可复现交互；不预填提效比例。
- 核实独立开发归属与第三方授权，补技能介绍、附件一及3分钟内真实录屏。
- 当前仓库是开发版，未声明已满足市场上架条件。
