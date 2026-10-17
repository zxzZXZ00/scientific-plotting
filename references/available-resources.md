# 现有主题与配色

<!-- Generated from registered resources by scripts/update_catalog.py; do not edit tables manually. -->

用户随时可询问“有哪些主题”“有哪些配色”“给我看主题示例”。直接回答现有资源，不要求先上传数据或开始绘图。
主题与配色可分别选择；用途是建议，跨领域可以借用。所有绘图必须命中已有资源，imports 候选不列入。

## 主题

| 名称 | 调用名称 | 默认配色 | 默认图型 | 图片示例 |
| --- | --- | --- | --- | --- |
| 通用论文 | `paper` | `blue-red` | `line` | [预览](../assets/examples/line-with-band/preview.png) |
| 蓝洋红 | `user:blue-magenta` | `user:blue-magenta` | `line` | [预览](../user-library/examples/blue-magenta/preview.png) |
| 雾蓝玫粉 | `user:mist-blue-rose` | `user:mist-blue-rose` | `line` | [预览](../user-library/examples/mist-blue-rose/preview.png) |
| 桃橙青绿 | `user:peach-teal` | `user:peach-teal` | `line` | [预览](../user-library/examples/peach-teal/preview.png) |
| 红青 | `user:red-cyan` | `user:red-cyan` | `line` | [预览](../user-library/examples/red-cyan/reproduction.png) |

## 配色

| 名称 | 调用名称 | 系列色号 |
| --- | --- | --- |
| 蓝红 | `blue-red` | `#4477AA`、`#EE6677` |
| 蓝—洋红 | `user:blue-magenta` | `#0072B2`、`#CC79A7`、`#9E3D73`、`#377EB8` |
| 雾蓝—玫粉 | `user:mist-blue-rose` | `#71A9CE`、`#FF7DC5`、`#00629F`、`#C5689B` |
| 桃橙—青绿 | `user:peach-teal` | `#F19E65`、`#7FBFBB` |
| 红青 | `user:red-cyan` | `#EF424A`、`#00A6DA`、`#80BE44`、`#8D2695` |

[主题图组总览](../assets/theme-gallery.png) · [用法与示例](usage.md) · [用途与文献来源](scene-routing.md) · [资源详情](../user-library/catalog.md)

图组总览展示已认可的文献参考重建，包含演示值/近似示意；单图预览展示通用绘图调用。普通命令的已实现图型以 gallery.md 为准。

维护：新增、改名、修改或移除主题/配色后运行 `python scripts/update_catalog.py`；打包前运行同一命令加 `--check`，发现索引过期或依赖缺失即失败。
