# 高级文章转网页演示文稿

默认quick使用自有basic模板，见quick-delivery.md；本文件仅在明确需要高级风格时加载。

本模式整合[歸藏 Guizang PPT Skill](https://github.com/op7418/guizang-ppt-skill)，提供两种风格：magazine（杂志风）和swiss（瑞士国际主义）。输出是浏览器打开的HTML演示，不是.pptx；不加入视频渲染流程。

## 输入与输出

输入：revised.md、受众、场合、风格、可选时长/页数及图像。只要求转演示时保留原稿；用户已有大纲时复用。没有指定风格时用magazine，有明确科技/工程数据汇报需求可推荐swiss；说明选择，缺少的信息不影响初稿时按保守假设继续。
输出：slides/outline.md、slides/index.html、图片与本地动效资源、讲稿备注、presentation.json，以及上游LICENSE、NOTICE.md和对应源码。素材或环境未验证处写入交付说明。

先按article-types.md和对应文种规则选择叙事，再基于原稿拟定outline.md：每页稳定ID、页面目的、主张/证据、选用版式、讲稿要点、转场及可选时长。不把文章按段落机械拆页，不虚构数据做大字报；保留待核实标记。仅演示模式不额外生成公众号HTML；默认联合交付同时生成文章HTML。

## 固定依赖安装与模板准备

这部分是可选能力，普通核稿排版无需下载上游。首次演示请求时执行：

```bash
.venv/bin/python scripts/presentation.py setup
.venv/bin/python scripts/presentation.py prepare --input /abs/revised.md --output-dir /abs/slides --style magazine
```

setup下载脚本中固定的上游提交到用户缓存，不修改本技能、不自动追最新版。已有可信的固定版本checkout可用`prepare --upstream /abs/guizang-ppt-skill`，不修改该目录；版本不符或有工作树变更时拒绝。
prepare只生成工作骨架，**不能作为完成交付**。source-article.md是用于追溯的原稿快照，实际演示以outline.md和index.html为准，原稿修订后应同步更新大纲与幻灯片。

## 宿主生成演示

从slides/upstream-source中读取上游规范，按需加载：

- magazine：references/themes.md、references/layouts.md、assets/template.html，必要时components.md。
- swiss：references/themes-swiss.md、references/swiss-layout-lock.md、references/layouts-swiss.md、assets/template-swiss.html。每页按S01–S22登记data-layout，不用杂志风类名替代。
- 两者均读取references/presenter-mode.md和checklist.md，保留现有运行时。
- 原始截图需保真时读取screenshot-framing.md；默认使用用户素材，不自动调用付费配图或生成图片。

按joint-delivery.md生成slides-plan.json后使用`presentation.py render --directory /abs/slides --plan /abs/slides-plan.json`装配实际section.slide和讲稿，也可由宿主直接编辑。每页有data-slide-id。为每页填写SPEAKER_NOTES，ID与页面顺序一致，包含title、purpose、3–5条talk和transition；已知时长才填minutes，不捏造现场信息。不要把项目赞助信息放入演示正文。
按上游模板、主题与版式调整布局，保留键盘翻页、总览、P演讲模式与B低功耗。不删JS来消除检查失败；用户要静态版时另行说明能力变化。图片复制到slides/images并更新路径，不拷贝原稿目录里的无关资料。

## 验证与交付

```bash
.venv/bin/python scripts/presentation.py validate --directory /abs/slides
```

需要Node.js；两种风格均运行上游演讲者校验，swiss额外运行版式校验。空模板不能通过。上游swiss校验在可解析到Playwright时还会尝试启动浏览器测量并可能请求CDN；缺少Playwright则明确跳过测量。不能把静态通过或自动测量当作演讲者交互已实测。
浏览器中核对逐页布局、溢出、图片、前后翻页、ESC总览、P演讲模式、讲稿、观众窗口同步和B低功耗；没有浏览器工具时明确未测。Google字体、Lucide及动效fallback可能访问CDN，不宣称整个PPT完全离线。离线交付需实际断网检查字体替代、图标与内容可读性。

## 授权与来源

上游是AGPL-3.0。本项目的适配脚本保持自身授权，独立下载的上游模板和由其改编的运行时不能改标Apache；生成目录携带AGPL LICENSE、NOTICE和完整上游源码，index.html保留改编来源。分发演示时一起提供这些文件及改编后的可编辑HTML。不得把第三方模板当个人独立原创成果申报。
本安装包包含适配器和规范，不捆绑上游仓库；使用网页演示能力时下载一次固定版本。上游源码是功能依赖，不注册第二个技能入口。
