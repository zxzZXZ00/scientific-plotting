"""只负责数据检查和画图；不解析命令行，不保存文件。"""
import csv
import math

import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator


def read_data(path, mapping, band=True):
    keys = ["x", "y"] + (["lower", "upper"] if band else [])
    columns = [mapping[key] for key in keys]
    if "group" in mapping:
        columns.append(mapping["group"])
    if len(set(columns)) != len(columns):
        raise ValueError("数据字段必须映射到不同的列")
    groups = {}
    order=mapping.get('x_order','increasing')
    if order not in {'increasing','decreasing','monotonic','preserve'}:
        raise ValueError('x_order 应为 increasing、decreasing、monotonic 或 preserve')
    with open(path, encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        headers = reader.fieldnames or []
        if len(headers) != len(set(headers)):
            raise ValueError("CSV 表头重复")
        missing = set(columns) - set(headers)
        if missing:
            raise ValueError(f"CSV 缺少列：{', '.join(sorted(missing))}")
        for number, row in enumerate(reader, start=2):
            try:
                if None in row or any(v is None for v in row.values()):
                    raise ValueError("字段数量与表头不符")
                name = row[mapping["group"]].strip() if "group" in mapping else "Data"
                if not name:
                    raise ValueError("分组为空")
                x, y = [float(row[mapping[c]]) for c in ("x", "y")]
                low, high = ([float(row[mapping[c]]) for c in ("lower", "upper")] if band else (y, y))
                if not all(math.isfinite(v) for v in (x, y, low, high)):
                    raise ValueError("数值必须有限")
                if not low <= y <= high:
                    raise ValueError("应满足 lower ≤ y ≤ upper")
                points = groups.setdefault(name, [])
                if points and order=='increasing' and x <= points[-1][0]:
                    raise ValueError("组内 x 必须严格递增")
                if points and order=='decreasing' and x>=points[-1][0]:raise ValueError('组内 x 必须严格递减')
                if points and order=='monotonic':
                    if x==points[-1][0] or len(points)>1 and (x-points[-1][0])*(points[-1][0]-points[-2][0])<=0:
                        raise ValueError('光谱 x 必须严格单调；不会自动排序或合并点')
                points.append((x, y, low, high))
            except (ValueError, TypeError) as error:
                raise ValueError(f"CSV 第 {number} 条记录：{error}") from error
    if not groups or any(len(points) < 2 for points in groups.values()):
        raise ValueError("每组至少需要两个点，CSV 不能为空")
    return groups


def plot_line_with_band(groups, config):
    appearance = config["appearance"]
    colors = appearance["colors"]
    if len(colors) < len(groups):
        raise ValueError("配置中的颜色数量少于分组数")
    width = float(config["figure"]["width_mm"])
    height = float(config["figure"]["height_mm"])
    linewidth = float(appearance["linewidth"])
    alpha = float(appearance["band_alpha"])
    if not all(math.isfinite(v) and v > 0 for v in (width, height, linewidth)):
        raise ValueError("尺寸和线宽必须是有限正数")
    if not 0 <= alpha <= 1:
        raise ValueError("band_alpha 必须在 0～1 之间")
    fig, ax = plt.subplots(figsize=(width / 25.4, height / 25.4))
    full_frame=appearance.get("full_frame",True)
    if type(full_frame) is not bool:
        raise ValueError("full_frame 必须是 true 或 false")
    for name,spine in ax.spines.items():
        spine.set_visible(full_frame or name in {"left","bottom"})
    markers=appearance.get("markers",[appearance.get("marker")])
    if not isinstance(markers,list) or not markers:
        raise ValueError("markers 必须是非空列表")
    for index,((name, points), color) in enumerate(zip(groups.items(), colors)):
        x, y, low, high = zip(*points)
        marker=markers[index % len(markers)]
        if len(x)>=appearance.get("marker_threshold",15):
            marker=None
        if config['template']=='sticks':
            ax.vlines(x,0,y,color=color,linewidth=linewidth,label=name)
        else:
            ax.plot(x, y, color=color, linewidth=linewidth, label=name, marker=marker,
                    markersize=appearance.get("markersize", 3.2),
                    markerfacecolor=appearance.get("markerfacecolor",color),markeredgewidth=.6)
        if config["template"] == "line-with-band":
            ax.fill_between(x, low, high, color=color, alpha=alpha)
    ax.set(xlabel=config["labels"]["x"], ylabel=config["labels"]["y"])
    if config['template']=='spectrum':
        first=next(iter(groups.values()))
        # Preserve a supplied decreasing spectral axis, e.g. an IR wavenumber
        # scan. No axis inversion is inferred from a colour or theme alone.
        if first[0][0]>first[-1][0]:ax.invert_xaxis()
    if "labelsize" in appearance:
        ax.xaxis.label.set_size(appearance["labelsize"])
        ax.yaxis.label.set_size(appearance["labelsize"])
    if "tick_labelsize" in appearance:
        ax.tick_params(labelsize=appearance["tick_labelsize"])
    if "max_major_ticks" in appearance:
        nbins=max(1,int(appearance["max_major_ticks"])-1)
        ax.xaxis.set_major_locator(MaxNLocator(nbins=nbins))
        ax.yaxis.set_major_locator(MaxNLocator(nbins=nbins))
    ax.legend(loc=appearance["legend_location"])
    fig.tight_layout()
    return fig
