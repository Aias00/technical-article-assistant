# 文章与网页PPT联合交付

这是完整处理的默认路径。用户只提供主题或资料时，先收集支持关键主张的资料并成稿；已有稿件时先核稿修订。最终由同一份revised.md派生公众号文章与演示，不将准备模板作为PPT成品。

## 宿主完成内容工作

1. 按article-types.md识别文种，加载对应types规则后生成review.md和revised.md，记录来源和验证范围。只有主题而缺事实依据时，主动查允许访问的官方资料；无法核实时明确草稿边界，不编造案例、数据或引用。
2. 读取presentation.md并安装/定位固定上游。根据用户要求或上游默认magazine风格，读取相应模板和版式；没有指定时长不填造时长。
3. 按文种选择演示叙事（技术：问题/机制/证据；总结：目标/成果/问题/行动；宣传：痛点/能力/案例/价值；观点：主张/论据/讨论/结论），生成slides-plan.json：每页一个明确主张，保留文章中的数字口径、引用归属、责任主体、限制和不确定性；不逐段搬运文章。默认短篇约5–8页，按内容增减，无须凑数。
4. 填写每页对应讲稿。图像使用用户提供或已获授权的真实资料；不得自动生成虚假图表或补造业务数据。

## 演示计划格式

先用inspect_article.py读取输入摘要。source_sha256必须等于revised.md字节的SHA-256；修改修订稿后重新生成计划。示意：

```json
{
  "style": "magazine",
  "source_sha256": "替换为真实修订稿摘要",
  "slides": [
    {
      "id": "review-scope",
      "title": "核稿范围",
      "classes": "hero dark",
      "animation": "hero",
      "content_html": "<div class=\"frame\"><h1 class=\"h-hero\">核稿范围</h1><p>这里填写文章已支持的主张。</p></div>",
      "notes": {
        "purpose": "讲清本页目的",
        "talk": ["补充背景", "解释依据", "提醒适用限制"],
        "transition": "衔接下一页的实际内容"
      }
    }
  ]
}
```

这是结构示意，不可原样当成品。content_html只包含section内部的布局，不再包section；脚本负责稳定ID、标题、页面包装与讲稿数组。classes、animation及实际布局需来自所选上游模板。swiss每页还必须有layout（S01–S22或登记的封面/封底标识），使用瑞士模板的canvas-card等骨架。
本项目不通过规则硬拆文章生成演讲内容，主张、布局与讲稿由宿主从修订稿编写。

图片资源：计划可增加`images`数组，如`[{"source":"/abs/diagram.png","name":"diagram.png"}]`，页面引用`images/diagram.png`。source相对计划文件目录解析，name仅允许唯一文件名。脚本复制已声明的本地素材并检查页面引用，不下载远端图片；远端图片可用性需另外说明。不要引用临时文件或把缺图标成通过。

## 一次装配文章与实际幻灯片

```bash
.venv/bin/python scripts/run.py --input /abs/revised.md --output /abs/delivery/article.html --slides-plan /abs/slides-plan.json
```

可选`--upstream /abs/pinned-checkout`复用固定依赖。命令先核对计划摘要、文章预检，再生成article.html、准备slides目录、写入实际幻灯片和讲稿、生成slides/outline.md并运行上游校验。不得停在prepared_not_authored。
需要手动布局或调试时，也可以依次运行run.py（仅文章）、presentation.py prepare、render --plan、validate；对用户仍是一次完整交付，不要求用户自己补写PPT。

输出目录已存在slides时选择新的版本目录，不覆盖旧演示。失败返回非零，可能保留部分产物；说明哪一支已完成、哪一支失败，不能把文章成功当成双交付成功。

## 完成条件

- revised.md是可读取的完整文章，review.md如实记录核验范围；文章HTML检查完成。
- slides/index.html包含真实页面及逐页讲稿，outline.md与页面对应，原稿摘要一致。
- 上游检查已执行；浏览器布局、互动和微信粘贴若未验证，明确待验。
- 若演示缺依赖、校验失败或只有空模板，报告“部分完成”，继续可恢复步骤，不声称双交付完成。
- 最终直接给出文章Markdown、公众号HTML和网页PPT入口，并附必要的未解决事项；不向用户只交代码或生成步骤。

HTML幻灯片不是.pptx，分发时保留slides/LICENSE、NOTICE.md及upstream-source。
