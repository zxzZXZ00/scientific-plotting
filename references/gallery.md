# 模板目录

每张图都要选择库中实际存在的主题和配色。主题样例见 [主题图片](../assets/theme-gallery.png) 和 [用户库](../user-library/catalog.md)。用途推荐见 [文献场景与借用规则](scene-routing.md)：推荐不限制领域，用户指定优先。

## spectrum

连续光谱/色谱线。CSV 映射 x、y，可选 group；每组严格单调递增或递减，保留输入方向，不画点、不拟合、不平滑、不自动归一化。
通过 template: spectrum 调用 scripts/render.py；优先借用蓝洋红的 XANES/EXAFS/IR 风格，NMR/EPR/UV–vis 和色谱可借用红青，仍可明确指定任意其他已有主题、配色。

## sticks

离散质谱 m/z–强度等竖线图；从0画到已有 y 值，要求映射 x、y，可选 group，不自动生成峰。仅在数据适合离散棒谱时使用；连续扫描谱仍可选择 spectrum。

## line

别名：普通折线、趋势曲线。适合有序 x-y 数据。
需要 x、y 列，可选 group；每组至少两个点，组内 x 默认严格递增。用户明确的循环轨迹可使用 data.x_order: preserve，不自动排序。
使用 scripts/render.py，配置 template: line；不需要 lower/upper。
paper 主题默认选用此图型，但仍须确认连线符合数据含义。

个人资源在 ../user-library/catalog.md 中按用途和输入字段查找。
不得读取 imports 草稿作为正式模板。

## line-with-band

适合比较多组随 x 变化的数值，并用已有上下界展示不确定性。
每组一条折线、一条阴影带。没有上下界时，选择其他模板或明确修改代码。

- 入口：[../assets/templates/line-with-band.py](../assets/templates/line-with-band.py)
- 默认配置：[../assets/configs/line-with-band.yaml](../assets/configs/line-with-band.yaml)
- 示例数据：[../assets/examples/line-with-band/demo.csv](../assets/examples/line-with-band/demo.csv)
- 模板预览：[../assets/examples/line-with-band/preview.png](../assets/examples/line-with-band/preview.png)

preview.png 使用演示 CSV 渲染，不来自论文。重复的演示 reference.png 不随轻量包分发。
demo.csv 的上下界是人为构造的演示区间，不代表实际置信区间。
真实使用时，可替换参考图并记录来源，再调整模板和配置。
