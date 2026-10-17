# 工作空间、格式和命名

此规则适用于安装后的一般绘图、新建独立脚本和参考重放。技能目录中的已认可样例属于静态资源，不在日常绘图时覆盖。

- 默认根目录为**本次用户工作空间/sci_plots**，不是输入文件所在目录、上次工作空间或技能安装目录。
- 所有图默认同时导出 PNG、SVG、PDF，分别写入 png/、svg/、pdf/ 子目录。三种文件来自同一个 Figure，数据、画布和排版一致。用户明确要求其他格式组合时才覆盖。
- 默认使用本次输入文件的文件名去掉最后一个扩展名，例如 数据.csv → png/数据.png、svg/数据.svg、pdf/数据.pdf；--data 覆盖输入后，名字跟随真正的新输入。用户明确命名时采用该名称。
- 多图时使用 数据_光谱、数据_柱图 等有意义后缀；无原文件的直接文本数据可使用简短语义名，无法确定时用 figure。所有格式使用相同 basename。
- 已有同名输出不覆盖，自动依次添加 _2、_3；不得因换了格式而覆盖先前结果。文件名保留中文，跨平台非法字符替换为下划线。
- <basename>.resolved-config.yaml 和 <basename>.layout-checks.json 放在 sci_plots 根目录，记录实际输入、已有主题/配色、选择依据、输出路径与检查结果。不要保存开发者机器的解释器路径作为用户永久配置。
- scripts/render.py 的 --workspace 可显式传入当前工作空间；未传时使用运行时当前目录。--output 显式覆盖输出根目录，相对路径按 --workspace 解析。配置和资源的解析不依赖当前工作空间。
- Agent 从当前会话确定用户工作空间，调用时将 workdir 设为该空间，或显式传 --workspace。更换工作空间后重新取当前值，不缓存上一次结果目录。
- 自定义脚本统一调用 scripts/exporting.py 的 export_figure，传入实际 data_path、包含已有 theme/palette 的 config、可选 workspace/output 等参数；不能绕过检查自行 savefig 到技能目录。

例如，用户工作空间为 ProjectB，输入为另一目录的 experiment.csv：

```text
ProjectB/
└── sci_plots/
    ├── png/experiment.png
    ├── svg/experiment.svg
    ├── pdf/experiment.pdf
    ├── experiment.resolved-config.yaml
    └── experiment.layout-checks.json
```

从任意工作空间调用已安装技能的例子（以实际路径替换占位符）：

```text
<PYTHON> <SKILL_DIR>/scripts/render.py --config <WORKSPACE>/plot.yaml --workspace <WORKSPACE>
```

plot.yaml 最小示例：

```yaml
theme: user:blue-magenta
palette: user:mist-blue-rose
template: spectrum
data:
  path: spectrum.csv
  x: wavenumber
  y: absorbance
labels:
  x: Wavenumber (cm$^{-1}$)
  y: Absorbance (a.u.)
```

显式要求仅 PNG 时可用 --formats png；显式改名用 --name 样品A。普通使用不需要写 output.formats 或 output.stem。
