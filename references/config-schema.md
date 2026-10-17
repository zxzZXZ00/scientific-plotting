# 配置说明

## 主题与继承

红青主题 appearance.labelsize 为轴标题字号，tick_labelsize 为刻度字号（单位 pt），
max_major_ticks 为自动主刻度密度目标（默认 5）；自动定位器可能取附近整洁刻度值，
最终仍须查看可见数量。具体任务可以显式设置更稀疏的主刻度。
appearance.markers 是按系列分配的非空 marker 列表，优先于单个 marker；
markerfacecolor: none 表示空心。红青普通折线默认 [s, '^']，对应空心方形、三角形。
appearance.marker_threshold 默认 15：每组点数小于 15 时显示 marker，达到或超过 15 时不显示；图例跟随实际曲线。
appearance.full_frame 默认为 true：普通数据图显示四边闭合坐标框；不自动添加顶部或右侧刻度。

统一个人设置位于 user-library/settings.yaml，只支持 figure.width_mm/height_mm 和
output.dpi/transparent/formats，避免把任务路径或文件名设为全局值。
合并顺序：主题默认 → 个人统一设置 → 本次任务显式值。
省略字段或 default 均不覆盖上一层。因此任务 dpi: default 会沿用个人 DPI（若有），
个人 dpi: default 会沿用主题 DPI。具体 false 必须生效。
默认示例 line-with-band.yaml 明确写了 dpi 等参数，因此这些值会覆盖个人设置；
希望跟随个人设置时，将任务中的对应字段改为 default 或删除。

theme、palette 必须命中实际资源文件，不能使用库外系列颜色。用户显式指定分别优先；未指定时由用途建议选择已有主题，信息不足时借用 paper。文献领域不是使用限制。
内置主题位于 assets/themes，配色位于 assets/palettes。用途与选择逻辑见 scene-routing.md。
theme: user:名称、palette: user:名称、template: user:名称 引用已认可个人资源。
主题包括 style 路径、defaults（template、palette、figure、labels、appearance、output），
以及可选 layout 图组结构。style 相对主题文件解析，默认数据路径仍相对任务配置解析。
任务显式 style 覆盖时，相对任务配置解析。
任务字段省略或 default 时继承主题；显式值逐字段覆盖，false 和 0 不视为缺省。
appearance.marker 控制数据点形状；output.transparent 必须是布尔值。
主题的 layout 传给用户模板处理；内置模板不会自动解释任意布局。
当前配色执行器支持 colors 分类色列表；连续/发散配色由相应用户模板实现。
resolved-config.yaml 保存合并后的配置，便于核对。

最小任务配置：

```yaml
theme: paper
data:
  path: experiment.csv
  x: time
  y: response
```

配置是普通 YAML 数据，读取后逐项应用到绘图代码。

| 参数 | 作用 | 默认/约束 |
| --- | --- | --- |
| template | 选择图型 | line、line-with-band、spectrum、sticks 或 user:名称 |
| purpose | 可选用途建议 | auto、已知用途标识或自然语言；不限制用户选其他已有主题 |
| theme / palette | 已有资源名称 | 如 user:blue-magenta；两者可以分别指定 |
| style | mplstyle 文件路径 | 相对配置文件所在目录解析 |
| data.path | CSV 路径 | 相对配置文件所在目录解析；--data 可覆盖 |
| data.x/y/lower/upper/group | 数据列映射 | 必须对应 CSV 表头的不同列 |
| data.x_order | 连线顺序检查 | increasing、decreasing、monotonic 或 preserve；spectrum 默认 monotonic |
| figure.width_mm/height_mm | 最终画布尺寸 | 正数，单位毫米 |
| labels.x/y | 坐标轴标签 | 字符串，可包含单位 |
| appearance.colors | 各组颜色 | 非空列表，数量至少等于组数；只能重排/取用所选已有 palette 的色值 |
| appearance.linewidth | 折线宽度 | 正数，单位 point |
| appearance.band_alpha | 阴影透明度 | 0～1 |
| appearance.legend_location | 图例位置 | Matplotlib loc 字符串，如 upper left |
| output.stem | 显式文件名，不含扩展名 | 省略时取实际输入文件名；同名加 _2、_3，保留中文 |
| output.formats | 用户明确覆盖输出格式时填写 | 默认 png、svg、pdf 三种；非空且不重复 |
| output.dpi | 栅格导出分辨率 | 正整数；不能决定矢量线条的清晰度 |

--config、--data、--output 的相对路径按 --workspace 解析；未给 --workspace 时为运行时当前目录。CSV 在 YAML 中的相对路径仍按该 YAML 所在目录解析。
默认输出根目录为当前工作空间/sci_plots，图像分别写入 png、svg、pdf；元数据带相同 basename。--workspace 指定当前工作空间，--output 才覆盖输出根目录；--name/--formats 是显式覆盖。详见 output-policy.md。
不把安装目录、输入文件所在目录或上次工作空间设为隐式输出位置。自定义 YAML 可省略有主题默认值的字段。

覆盖顺序：mplstyle 提供基础风格；YAML 中的尺寸、颜色、线宽等显式参数优先。
毫米转为 Matplotlib 的英寸：inch = mm / 25.4。
