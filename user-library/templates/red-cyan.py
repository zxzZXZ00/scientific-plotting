"""正式入口：重放用户认可的固定图组，不将任意新数据冒充原演示数据。"""
from pathlib import Path
import hashlib
import importlib.util
import json
import math

BASE = Path(__file__).resolve().parents[1]
EXAMPLE = BASE / 'examples/red-cyan'


def render(config, data_path):
    manifest = json.loads((EXAMPLE/'approval.json').read_text(encoding='utf-8'))
    # The reviewed figure has synthetic numerical series and chemical schematics.
    # A general arbitrary-data adapter has not been approved or implemented.
    if hashlib.sha256(Path(data_path).read_bytes()).hexdigest() != manifest['files']['demo.csv']:
        raise ValueError('这是已审核固定图组，暂不支持替换 CSV。新数据请选 line/line-with-band，或创建新图组候选。')
    allowed_colors=['#EF424A','#00A6DA','#80BE44','#8D2695']
    if config['appearance']['colors'] != allowed_colors:
        raise ValueError('固定复现图组的换色需要新建候选；此配色可单独用于其他绘图模板。')
    if config['appearance'].get('linewidth') != 0.8 or config['appearance'].get('marker') != 'o':
        raise ValueError('固定图组包含各系列专属线宽和标记；修改请创建新候选。')
    expected_style=BASE/'styles/red-cyan.mplstyle'
    if Path(config['style']).read_bytes()!=expected_style.read_bytes():
        raise ValueError('固定图组的换样式需要新建候选。')
    source=EXAMPLE/'reproduce.py'
    spec=importlib.util.spec_from_file_location('approved_figure2',source)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    fig=module.draw_figure()
    width=float(config['figure']['width_mm'])
    height=float(config['figure']['height_mm'])
    if not all(math.isfinite(v) and v>0 for v in [width,height]):
        raise ValueError('图尺寸必须是有限正数')
    fig.set_size_inches(width/25.4,height/25.4)
    fig.set_dpi(config['output']['dpi'])
    checks=module.check_boundaries(fig)
    if any(checks[k] for k in ['text_outside_canvas','text_rectangle_overlaps','annotation_line_intersections']):
        raise ValueError(f'当前尺寸下排版检查未通过：{checks}')
    return fig
