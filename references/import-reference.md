# 导入图片或文章图组

## 评审先行

收到图片、文章或图组后，先查看原始素材；论文 PDF 需要查看有关页面和图注。
确认用户要复现整组还是某个子图。没有原文件或可访问内容时，请用户提供素材。
不要承诺完美复现。目标是可编辑、可复用的绘图逻辑，不能把原图贴进输出当作复现。

## 1. 创建候选资源

候选内容只写入 imports/<资源名>/，不加入正式索引，不改变内置默认值。
保存 source 图片或来源说明、原文图注和版本。分析并记录：
- 图型和每个子图的数据要求；无法从图片确定的统计含义。
- 字体、marker、边框、图例、色值和配色类型；不确定项标为估计。
- 图组行列、面板标号、尺寸比例、共享坐标轴/图例、留白。
- 新主题的普通数据图默认四边封闭；若参考图属于特殊开放边框主题，在候选主题显式声明 appearance.full_frame: false 并说明原因。此规则同时检查代码与最终图片。

图组结构保存在候选 theme.yaml 的 layout 中。例如：

```yaml
layout:
  rows: 1
  columns: 2
  panels:
    - {id: a, type: line, row: 0, column: 0}
    - {id: b, type: bar, row: 0, column: 1}
  shared_legend: false
```

layout 是候选模板需要解释的约定，内置渲染器不会自动实现任意布局。
生成 template.py，用 render(config, data_path) 返回 Matplotlib Figure，
由代码实现布局、CSV 检查与各子图绘制。不得仅保存布局而没有实现。
候选可由 reproduce.py 或明确记录的命令独立运行，尚未注册时不要用 user:入口。

## 2. 复现和比较

优先使用用户原始数据。有图而无数据时，使用明确标记的演示数据复现风格；
若用户要求提取数值，注明数字化近似、误差和坐标标定，不能当作原始数据。
生成 reproduction.png，并排生成 comparison.png；查看实际图片，调整明显差异。
写 review.md：来源、运行命令、数据来源、已知差异、候选文件列表、当前版本。
保存完整配置、配色、样式、模板和示例输入，避免依赖个人机器绝对路径。

## 3. 给用户评审

向用户显示复现图与比较图，指出已知差异，询问是否认可这一版并加入用户资源。
在收到明确回复前停止入库，只保留候选；可继续按用户意见迭代。
这是用户要求的评审环节，不是自动质量阈值。相似度分数不能替代用户认可。
认可必须对应具体候选版本；认可后又修改视觉结果，需要重新展示确认。

## 4. 认可后入库

只把认可的资源复制到 user-library/：
- themes/<名称>.yaml：主题，默认配色/模板/输出与图组布局。
- palettes/<名称>.yaml：配色。
- styles/<名称>.mplstyle：样式。
- templates/<名称>.py：自包含绘图函数，或显式带上其依赖。
- examples/<名称>/：来源说明、参考图、复现图、演示输入、评审记录。

主题引用使用 user:<名称>，style 相对主题文件设置为 ../styles/<名称>.mplstyle。
主题 defaults.palette 使用 user:<名称>。已有通用模板满足需求时，defaults.template 可为 line 或 line-with-band；只有自定义 render(config, data_path) 已实现并通过实际数据验证时，才登记 user:<名称> 模板。
参考图组仅能固定重放时，将其代码和依赖归档到 examples/<名称>/，并在 layouts 中明确 arbitrary_csv_supported: false；不能只因参考图片获认可，就宣称任意 CSV 已能生成全部参考图型。
模板在 config 中读取主题传入的 layout，按数据规范检查实际输入。
运行正式用户入口验证；再更新 user-library/catalog.md，记录用途、数据字段、
模板/主题/配色名称和用户认可的版本。不覆盖同名已有资源，使用新名称或版本。
不修改 assets 中的内置资源，不把新增主题设为全局默认。
单独新增配色也需要本轮预览认可，但不必生成无关主题/模板。

入库后按 maintenance.md 同步查询和帮助文件：运行 scripts/update_catalog.py 更新 available-resources.md，更新 catalog、相关用法/预览及主题总览；核对 usage.md 中的资源名仍可调用。只有索引、说明和实际资源一致后才报告入库完成。
