# 使用方法与调用示例

用户在安装后任何时候都可以询问用法，不必再次安装，也不必先提交数据。

## 查询与查看示例

- “现在有哪些主题和配色？”——按 available-resources.md 分别列出名称与调用名称；询问配色时可补充具体色号。
- “给我看蓝洋红的示例。”——展示该主题已有预览；需要参考图组时展示归档 reproduction.png，并说明是参考重建。
- “怎么使用，给两个例子。”——直接给自然语言例子和默认输出说明；只有用户要脚本/配置时再展开命令或 YAML。

可用资源见[实时维护的查询索引](available-resources.md)，图片总览见[现有主题示例](../assets/theme-gallery.png)。

## 普通绘图示例

1. “使用红青主题，读取 experiment.csv，x 列作横轴，y 列作纵轴，绘制折线图。”
2. “使用蓝洋红主题，读取 spectrum.csv，绘制光谱；横轴 wavenumber，纵轴 absorbance。”
3. “使用桃橙青绿主题，但配色选雾蓝玫粉，读取 data.csv 绘图。”——主题和配色分别使用两个已有资源。
4. “根据这份 CSV 选一个适合的已有主题和配色。”——按信息选择或借用，说明本次选择，不把领域对应当硬限制。
5. “本次只导出 PNG，命名为 sample_A。”——只覆盖此次格式和名称；以后仍默认三格式。

不指定格式、位置和名称时，假设输入为 experiment.csv：

```text
当前工作空间/sci_plots/png/experiment.png
当前工作空间/sci_plots/svg/experiment.svg
当前工作空间/sci_plots/pdf/experiment.pdf
```

换工作空间后结果写到新空间。依赖、Arial 与安装方法见 installation.md；精确字段和命令见 config-schema.md 与 output-policy.md。
当前直接读取 CSV；没有明确支持的数据格式不应声称已支持。没有原始数据时不要把预览数据当成用户数据。

## 需要配置时的最小例子

```yaml
theme: user:blue-magenta
palette: user:mist-blue-rose
template: spectrum
data:
  path: spectrum.csv
  x: wavenumber
  y: absorbance
```

这里的主题与配色都来自现有资源库。使用实际安装位置的 scripts/render.py，传入 --config plot.yaml，在用户工作空间运行即可；不需要把技能复制到每个新项目。
