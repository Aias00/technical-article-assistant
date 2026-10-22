# 一次性环境准备

需要Python 3.10+。核心包仅Markdown、BeautifulSoup、cssutils、Pygments；basic演示使用标准库，不需要Git、Node、Playwright或字体下载。

## 首次准备

macOS/Linux：

```bash
python3 scripts/bootstrap.py
```

Windows PowerShell：

```powershell
py -3 scripts/bootstrap.py
```

脚本先检查技能目录.venv和当前解释器。已有可用环境则复用，不执行安装；依赖缺失时创建.venv并安装requirements.txt。首次安装需要包源网络。
不将venv放入安装包，避免跨系统路径或可执行文件损坏。不重复为每篇文章创建新环境。

## 后续运行

```bash
python3 scripts/bootstrap.py -- run.py --input /abs/revised.md --output /abs/article.html --slides-plan /abs/plan.json
```

Windows将python3改成`py -3`，其余参数相同。脚本自动选择解释器并保留目标命令退出码。
`--check`仅探测，缺依赖返回非零，绝不创建目录、pip安装或下载PPT模板。`--venv /path/to/env`可指定独立环境，用于部署及冷安装测试。

已有环境的旧用法仍有效：`.venv/bin/python scripts/run.py ...`（Windows：`.venv\Scripts\python.exe`）。
Guizang仅在明确使用magazine/swiss高级风格时另行下载固定版本，并需要Git及Node校验。quick/basic不会触发它。

Windows命令和分支已提供，尚未在实际Windows系统端到端实测。没有Python执行能力时可交付文字稿，但不得伪造已生成HTML或PPT。
