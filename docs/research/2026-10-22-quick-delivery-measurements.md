# 快速交付本机验证

日期：2026-10-22。环境：macOS arm64、Python 3.12。输入为examples/work-summary.md，同一内容的4页PPT。

## 测量结果

| 项目 | 结果 | 范围 |
|---|---|---|
| 优化前Guizang本地装配，3次中位数 | 0.4180秒 | 依赖和内容计划已准备 |
| basic本地装配，3次中位数 | 0.3591秒 | 同一文章和页面要点 |
| 首次创建干净venv并安装4项核心包 | 4.5575秒 | 本机pip缓存/网络环境，不代表首次网络下载耗时 |
| 已准备环境的再次bootstrap探测 | 0.1171秒 | 无pip安装 |
| 相同内容计划UTF-8大小 | 2126 → 1369字节 | 减少35.6%，不是token或端到端耗时测量 |

冷环境明确确认lxml、watchdog均未安装；35项测试通过。Python仍需预装，首次依赖安装仍可能受网络影响。

本地装配从约0.42秒到0.36秒，只节省很少的绝对时间。主要优化意图是减少模型逐页HTML输出、默认上下文加载、首次Guizang准备和重复安装，未测量模型生成延迟，不宣称三分钟端到端已达标。

## 浏览器检查

Chrome本地file页面实测：4页可见布局无要点溢出；右箭头翻页、P讲稿开关、Esc总览及选页工作正常；资源请求列表为空。
窄窗口实测实际viewport为500×721，舞台保持16:9且放入视口；窗口未成功缩到390像素，不宣称完成390px手机测试。
桌面截图已在会话内目视检查。自动测量不代替所有内容密度与平台的视觉验收。Windows、元景及手机触屏尚未端到端实测。

## 可复现命令

```bash
python3 scripts/bootstrap.py --check
python3 scripts/bootstrap.py -- run.py --input examples/work-summary.md --output output/demo/article.html --slides-plan examples/basic-plan.json
# 同一目录再次运行，测试缓存：
python3 scripts/bootstrap.py -- run.py --input examples/work-summary.md --output output/demo/article.html --slides-plan examples/basic-plan.json --reuse
```

时间报告位于输出目录timings.json，缓存命中信息在slides/presentation.json。报告不会把缓存当独立事实来源。
