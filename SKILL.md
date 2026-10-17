---
name: scientific-plotting
description: 查询现有科研绘图主题、配色和用法示例；使用库内资源从 CSV 绘图与光谱，默认在当前工作空间生成 PNG/SVG/PDF；支持参考图复现评审、资源入库和安装说明。
---

## 安装与安装后的主动说明

先按 [references/installation.md](references/installation.md) 检查 Python 3.12、requirements.txt 中依赖和 Arial，使用 scripts/check_environment.py，不将本机环境路径写死给用户。
确认安装与环境就绪后，主动简短说明用法、提供自然语言调用示例、说明 sci_plots 三格式输出，并尽可能展示 assets/theme-gallery.png 中的现有主题图片；不等待用户追问。
例如：“使用蓝洋红主题，读取 spectrum.csv，绘制光谱图。”也可分别指定已有主题和配色。环境未就绪时说明缺少什么，不声称绘图已可用。

## 执行模式

用户随时询问“有哪些主题/配色”“看看主题图片”“怎么用/给示例”时，分别读取 [references/available-resources.md](references/available-resources.md) 和 [references/usage.md](references/usage.md)，直接回答或展示已有图片；不要求上传数据，不启动绘图或重复安装。
索引与实际资源可能不一致时运行 scripts/update_catalog.py --check 核对；只列出现存已登记资源，不列 imports 候选。
制作或修改本 skill 时遵守 [references/maintenance.md](references/maintenance.md)，同步资源索引、用法、预览和相关约束/检查；不能只改代码或只添说明。

用户发来参考图片、文章或图组，希望提取配色、图型或主题时，使用
[references/import-reference.md](references/import-reference.md) 的复现与评审流程。
先生成并展示复现结果，只有用户明确认可具体版本后才加入 user-library。
不能以“完美复现”作为预先保证；不能未经认可加入索引或覆盖内置默认配置。

普通绘图按下面流程执行：

1. 阅读 [references/gallery.md](references/gallery.md)，按需求选择已有主题、配色与图型。内置模板支持 line、line-with-band、spectrum、sticks。
   个人资源见 [user-library/catalog.md](user-library/catalog.md)；未指定时按 [references/scene-routing.md](references/scene-routing.md) 从已有库选择相同或相近视觉用途，陌生领域也可借用。用户显式选择分别优先，领域推荐不是硬限制。
   所有绘图的 theme、palette 必须在库中实际存在；不能临时编造库外主题/配色。用户指定库外资源时先走新增资源流程，不静默替换。系列色值只取所选已有 palette。
   候选区 imports 不参与检索。
2. 阅读 [references/data-format.md](references/data-format.md)，核对 CSV 字段和上下界含义。用户未提供数据时询问路径；只有明确要求演示时使用 demo.csv。
3. 需要修改参数时阅读 [references/config-schema.md](references/config-schema.md)。复制配置到输出目录，修改数据路径（建议绝对路径）、轴标签和样式参数。
   用户未指定的部分按用途建议和主题默认选择；无足够用途信息时借用已有 paper，不推断科学含义。显式要求覆盖建议。
   字段省略或 default 表示继承，false/0 是具体值，不视为缺省。模板数据不兼容时报告，不编造字段。
   user-library/settings.yaml 提供统一个人尺寸和导出设置，优先级为主题默认 < 个人统一设置 < 本次任务。
   用户要求“以后统一”时更新此文件；只要求“这张图”时仅修改任务配置。
4. 按 [references/output-policy.md](references/output-policy.md) 运行 scripts/render.py。默认在本次用户工作空间的 sci_plots/png、svg、pdf 分别生成三种格式，basename 沿用实际输入文件名；用户明确要求时才改目录、格式或名称。
   换工作空间后重新确定输出根目录；从 __file__ 定位技能资源，不把工作目录切到安装目录。独立脚本统一使用 scripts/exporting.py，传入已有 theme/palette。不要修改源 CSV；检查失败时报错，不补值、不删除行。
5. 查看输出 PNG，检查文字裁切、图例和上下界。交付图片与复现所需的脚本、配置、样式和输入数据说明。
   导出前调用 scripts/layout_checks.py 的 validate_figure；普通入口已内置。新模板或独立脚本同样接入，发现重叠、越界或重复边框先修复再导出，并保存 layout-checks.json。
   用户纠错须同时修正当前图、更新创建约束，并为可检测错误增加检查或回归用例；不能只记录注意事项。公式与单位必须作为完整文本排版。
   所有图的轴标题、刻度、图例和注释默认 Arial 正体，仅明确需要斜体的科学符号等例外；文字按实际成图尺寸检查，避免偏小。
   所有现有和新增主题的图尽量保持封闭图框，普通直角坐标图默认保留上、下、左、右四边，检查实际导出效果；刻度不必四边都显示。
   只有明确声明的特殊主题、用户指定或不适合矩形框的特殊图型才例外，不沿用绘图库省略边框的默认习惯。
   复用参考主题时区分单面板和整组画布，检查字号、marker 与实际绘图区的相对比例。
   所有图例放在图框内空白处；空间不足先增加图内留白，不自动移出图框。单图不能直接沿用整组尺寸。
   所有主题先遵守 [references/visual-constraints.md](references/visual-constraints.md) 的通用约束，再应用各主题的文字、刻度和标记设置。

依赖与已验证版本见 requirements.txt 和安装说明。以下从**当前用户工作空间**调用，SKILL_DIR 是实际安装目录；无参数绘图使用演示数据，只用于明确要求演示时：

```text
python <SKILL_DIR>/scripts/render.py
```

指定用户数据并覆盖默认数据路径：

```text
python <SKILL_DIR>/scripts/render.py --config plot.yaml --data experiment.csv
```

模板入口 assets/templates/line-with-band.py 也接受相同参数。
两种入口均调用相同的绘图实现。脚本资源从安装位置解析，结果写入运行时工作空间。
本示例只读取 CSV；不计算置信区间、不拟合、不自动排序或聚合。

主题在 assets/themes，配色在 assets/palettes；用户资源在 user-library 对应子目录。
主题可以提供默认形式、配色、marker 和导出参数。运行后保存 resolved-config.yaml 供复现。
用户图组模板通过 render(config, data_path) 返回 Figure；layout 由该模板实现。
