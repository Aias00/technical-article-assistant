# 平台交接

交接生成材料或给出命令形状，不等于已获发布授权。只有用户明确请求发布时，才交给目标环境实际安装的发布技能，并先读取它的最新说明；找不到时交付材料并说明缺少发布器，不静默换平台。

## 微信公众号

交付revised.md、article.html及实际使用的图片。使用内置formatter生成正文，标题单独填写；上传/替换本地图片后在编辑器和手机预览。详见formatting.md。
如果下游微信发布器要求Markdown，就传revised.md，不以旧原稿替代；不要假设它接受本项目HTML或已经上传图片。

## 腾讯开发者社区

交付修订后的Markdown，不把公众号HTML直接传给腾讯发布器。由已安装的tencent-dev-community-publisher负责平台Markdown转换、登录、封面与正文图片上传、标签、提交和成功判断。

交接前：

- 核对平台当前标题限制，保持传入标题与Markdown一级标题一致。
- 相对图片路径在revised.md目录下有效；提供实际存在的封面，或明确无封面。
- 阅读发布器实际支持矩阵，尤其嵌套列表、原始HTML和任务列表；不为兼容而静默删正文。
- 不硬编码用户HOME路径、浏览器登录态或特定平台活动标签；活动要求由当前发布器和用户配置决定。

命令形状（实际脚本和参数以安装版本为准）：

```bash
python <publisher-dir>/scripts/run.py publisher.py --title "标题" --content /absolute/path/revised.md --dry-run
```

发布器的dry-run可能打开浏览器并填表，不是本地无副作用检查；仅在用户已请求该交接操作时运行。不把审核中误报为发布失败，不在提交成功后自动重复提交。

## 状态说明

未要求发布时：not_requested。
已准备材料：prepared，说明目标平台和未完成的人工检查。
确实交给发布器执行后，按其结果记录submitted/failed与真实结果证据；没有收到文章URL就不要编造。
