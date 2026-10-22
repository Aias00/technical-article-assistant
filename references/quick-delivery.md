# 快速交付（默认）

目标是减少模型工作量和首次准备，不保证固定三分钟；实际耗时受模型、原稿长度与材料完整度影响。用户限定只核稿/只文章时仍尊重范围。

## 最短内容路径

1. 判断文种，只加载article-types.md中相关的一份types规则。使用用户提供材料；不为总结或宣传稿扩展无关检索。关键事实冲突或依据缺失须明确待核实，不能为速度跳过披露。
2. 一次写完整revised.md，随后做一次重点核对（数字、日期、责任主体、引用、限制）。默认短稿约800–1200中文字；已有长稿按用户范围保留，不静默截短。长文或研究型任务可使用standard/research。
3. review.md简记结论、实际修改和待核实事项。有来源才补来源台账，没有代码时不生成代码实跑报告；不强制分析稿、候选标题、多份大纲和meta.json。用户要求完整档案时再提供。
4. 写3–5页内容计划，每页1–4条要点与简短讲稿。默认basic轻模板，不写HTML/CSS，不加载Guizang模板、风格目录或演讲者手册。支持封面、要点和收束版式，不包含高级双屏演讲者模式。

## 紧凑计划

用inspect_article.py读取修订稿字节摘要；文件改动后更新计划摘要，不自动把过期计划当有效。

```json
{
  "style": "basic",
  "source_sha256": "实际修订稿SHA-256",
  "slides": [
    {"id":"scope","layout":"cover","title":"阶段复盘","bullets":["这里填写材料已支持的主张。"],"notes":["这里填写补充讲述。"]},
    {"id":"actions","title":"后续行动","bullets":["区分建议与已经决定的事项。"],"notes":["提醒尚未明确的责任人与时间。"]}
  ]
}
```

id稳定，便于局部更新。title不超过40字符，每页1–4条要点且每条不超过90字符；超出时拆页，不删改事实。layout为cover、bullets（默认）、closing。notes为非空文字数组。
basic只支持纯文本，所有内容由脚本转义，不处理原始HTML、生成图片或下载字体。需要图片、自由布局或Guizang演讲者模式时进入高级演示路径，不把快速档的能力夸大为高级效果。

## 环境与运行

首次使用标准Python执行`python scripts/bootstrap.py`，有可用环境则直接复用，只在依赖缺失时安装4项核心包。Windows可用`py -3`；演示不会要求另装Git或Node。

```bash
python scripts/bootstrap.py -- run.py --input /abs/revised.md --output /abs/delivery/article.html --slides-plan /abs/plan.json
```

以后继续使用同一命令，探测成功时不会再pip install。无需用户手动激活venv或记住平台解释器路径。若已知解释器可用，直接运行run.py更省一次环境探测。

修改同一稿件时保留页面id、更新真实源稿摘要及受影响页面，追加`--reuse`。未变页面复用缓存，手动修改过的HTML会拒绝覆盖；选择新输出目录可保留旧版。
文章仍重新执行轻量检查，不能因为复用页面跳过对改稿的核对。缓存仅用于派生页面，不是事实或来源的独立权威。

## 交付

默认给出revised.md、article.html、slides/index.html与slides/outline.md，附简短核稿结论和剩余事项。
纯HTML演示内置CSS/JS，无CDN，支持键盘/触屏翻页、页面总览和讲稿切换。无需编译；浏览器测试与语义核验分开报告。
timings.json记录本地各阶段耗时，**不包含模型写稿、检索、Python环境准备或人工预览**。有缺图、结构错误、事实阻断等问题仍明确失败或部分完成。
