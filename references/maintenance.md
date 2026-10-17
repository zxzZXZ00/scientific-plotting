# 制作与更新时必须同步的文件

用户要求资源、帮助和检查一起维护。每次创建、导入、修改、改名或移除资源时，完成适用项后才报告完成；不适用项无需生成无关文件。

| 变更 | 必须同步 |
| --- | --- |
| 新增/修改/改名/移除主题、配色 | 实际 themes/palettes/styles 文件、依赖引用、user-library/catalog.md；运行 scripts/update_catalog.py 更新 available-resources.md |
| 新主题或视觉效果改变 | 对应 examples 的预览、参考/重建与来源、review.md、认可记录；更新 assets/theme-gallery.png；改动认可图后重新展示评审 |
| 新图型、数据字段、配置参数 | references/gallery.md、data-format.md、config-schema.md、可运行示例与对应实现；usage.md 中涉及的用法不得过期 |
| 用途建议或文献理解改变 | references/scene-routing.md、相关主题 applications、scripts/scenes.py 中适用的推荐逻辑；保持用户显式选择优先及仅用已有资源 |
| 导出行为、文件命名或跨空间调用改变 | references/output-policy.md、usage.md、installation.md 的安装后说明、统一导出代码与执行回归测试 |
| 环境依赖改变 | requirements.txt、references/installation.md、scripts/check_environment.py 的说明/检查，并记录实际验证环境 |
| 用户指出可复用错误 | 当前图、references/visual-constraints.md、创建时防御、可自动化检查和对应回归用例；不能只追加文字 |
| 清理体积或制作轻量 ZIP | 检查代码/文档引用，保留主题预览、代码/配置/数据和真实运行依赖；历史截图、对照图和重复导出移到技能目录外归档；同步链接及认可记录的打包说明，再验证重放和查询索引 |

SKILL.md 只保留查询/绘图/导入/安装的路由与关键约束，不重复复制全部目录和帮助内容。
查询说明可独立读取，用户询问“有哪些”或“怎么用”时不应被引导去先提供 CSV。
新增资源必须先完成用户要求的评审流程；草稿不能提前出现在现有资源查询中。
制作时可在技能目录外保留完整原图、对照图和开发过程；轻量安装包无需重复分发这些图片。更新预览后保留所需展示图即可，静态 SVG/PDF 不因日常生成支持这两种格式就必须打进包内。

维护或打包前：

```text
python scripts/update_catalog.py --check
python scripts/test_execution.py
python scripts/test_layout_checks.py
```

另外检查新/变更预览是否存在、显示是否正确、用法中的资源名和命令是否仍可调用。索引生成器能检测表格过期和默认配色/样式缺失，不能自动证明全部自然语言说明或示例图片都已同步；这些仍需制作时核对。
