---
name: technical-article-assistant
description: 技术文稿核稿与排版助手。审阅中文技术宣传稿、技术分享稿和工程实践文章，输出问题清单、修订稿及适配微信公众号的 HTML；不执行外部发布。
---

# 技术文稿核稿与排版助手

## 适用范围

技术宣传稿、工程实践、技术分享文章。暂不承诺支持公文格式审查、自动涉密识别或全面合规判断。

## 输入与输出

输入：Markdown 原稿、目标读者、修改边界、可选事实依据与主题。
输出：review.md（问题、位置、依据与待核实项）、revised.md（修订稿）、article.html。

## 执行流程

1. 读取 `technical-article-review/SKILL.md` 及其 references 中的评审规则。只审不改时仅输出 review.md。
2. 由宿主 AI 检查结构、技术表述、术语一致性和证据。未提供依据的事实标为待核实，不编造来源、数据或结论。
3. 保留原稿，将修改稿另存为 revised.md。重大事实修改在 review.md 中说明；保留代码与用户指定不可修改内容。
4. 在技能根目录安装 Python 3.10+ 依赖：`python3 -m pip install -r requirements.txt`。优先使用虚拟环境。
5. 使用同一 Python 环境运行：

   ```bash
   python scripts/run.py --input /绝对路径/revised.md --output /绝对路径/article.html --theme ai-tech
   ```

   可选 `--cover /绝对路径/cover.png`。脚本路径相对于本技能根目录，运行时据实际安装位置解析。
6. 风格规则命中时人工判断，不能为通过检查而改变事实。重新修改后再运行。失败时不得宣称检查通过。
7. 交付三份产物，说明待核实事实及校验范围。脚本只检查预置表达模式、排版和部分 HTML 结构；不替代 AI 核稿或人工确认。

## 权限与数据

本地入口读输入和技能文件、写用户指定输出，调用包内 Python 子进程。运行本地入口无需 Token、不调用网络、不发布内容。
安装依赖需要访问包源；宿主 AI 的数据传输按元景环境规定执行。不得提交涉密资料、真实凭据或未脱敏客户数据。

## 安装与兼容性

安装包保留根 SKILL.md、scripts、三个模块及 requirements.txt。元景的 Python、文件读写和子进程支持尚待实测；不支持时不得宣称兼容。
原 `technical-article-preflight/scripts/run_preflight.py` 为历史发布预检接口，依赖未打包的发布器，不作为本项目入口。
