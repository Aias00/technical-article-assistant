# 环境准备

先检查 `python3 --version`（Windows为 `py -3 --version`），要求Python 3.10+。已有可用隔离环境时复用，不重复安装。

macOS/Linux：

```bash
python3 -m venv .venv
.venv/bin/python -c "import markdown, bs4, cssutils, pygments"
# 上一步报缺少模块时再执行：
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/run.py --help
```

Windows PowerShell：

```powershell
py -3 -m venv .venv
.venv\Scripts\python.exe -c "import markdown, bs4, cssutils, pygments"
# 上一步报缺少模块时再执行：
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe scripts/run.py --help
```

无需激活虚拟环境，使用解释器绝对路径可从其他工作目录执行。宿主无法执行Python时，核稿仍可进行，但明确说明无法生成或验证HTML，不伪造排版产物。
Markdown解析、HTML处理与CSS内联依赖成熟解析器，不为减少安装步骤改写成不完整的标准库解析器。
Windows命令为使用说明，尚未在Windows系统实测。
