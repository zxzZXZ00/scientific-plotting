# 已认可的红青科研图组

在 scientific-plotting 根目录运行：

```text
python scripts/render.py --config user-library/configs/red-cyan.yaml --output outputs/red-cyan
```

重放已审核的固定图组；数据为合成演示值。原始候选代码 reproduce.py 与配套文件保持原样归档。
approval.json 记录用户认可语句、版本与文件 SHA-256；归档中的 review.md 为候选历史记录，
其中旧的“待认可”是历史状态，最终状态以 approval.json 和 catalog.md 为准。
导出尺寸、DPI、透明背景可按统一设置覆盖；改尺寸后自动检查版面，其他外观变更需新候选。

配色和主题也可以独立用于新数据，例如任务配置：

```yaml
theme: user:red-cyan
template: line
data:
  path: E:/experiment.csv
  x: time
  y: response
  group: method
```

这种用法采用新数据的普通折线图，不会套用原图组的断轴或化学示意。
仅换配色时使用 palette: user:red-cyan，并保留其他主题。
