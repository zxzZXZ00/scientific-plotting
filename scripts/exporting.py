"""All production exports belong to the active workspace, never the skill folder."""
from pathlib import Path
import json
import re
import os

import yaml
from layout_checks import validate_figure
from settings import resource
from matplotlib import font_manager
from matplotlib.colors import to_hex

if os.environ.get('SCI_PLOT_ARIAL'):
    font_manager.fontManager.addfont(os.environ['SCI_PLOT_ARIAL'])

FORMATS=('png','svg','pdf')


def output_root(workspace=None,output=None):
    base=Path(workspace).expanduser().resolve() if workspace is not None else Path.cwd().resolve()
    value=Path(output).expanduser() if output is not None else Path('sci_plots')
    return (value if value.is_absolute() else base/value).resolve()


def choose_stem(data_path=None,stem=None):
    value=str(stem) if stem not in (None,'default','') else (Path(data_path).stem if data_path else 'figure')
    value=re.sub(r'[<>:"/\\|?*\x00-\x1f]','_',value).strip().rstrip('. ')
    if not value or value in {'.','..'}:value='figure'
    if re.fullmatch(r'(?i)(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])',value):value='_'+value
    return value


def reserve_stem(root,stem,formats):
    candidate=stem;index=2
    while any((root/ext/f'{candidate}.{ext}').exists() for ext in FORMATS) or (root/f'{candidate}.resolved-config.yaml').exists() or (root/f'{candidate}.layout-checks.json').exists():
        candidate=f'{stem}_{index}';index+=1
    return candidate


def export_figure(fig,*,data_path=None,stem=None,workspace=None,output=None,formats=None,
                  dpi=300,transparent=False,config=None,full_frame=True):
    if not isinstance(config,dict) or not all(config.get(k) for k in ['theme','palette']):
        raise ValueError('导出前必须明确选择库中已有的 theme 和 palette')
    for key,kind in [('theme','themes'),('palette','palettes')]:
        if not resource(kind,config[key]).is_file():raise ValueError(f'{key} 不在资源库中：{config[key]}')
    palette=yaml.safe_load(resource('palettes',config['palette']).read_text(encoding='utf8'))
    allowed={to_hex(c).lower() for c in palette['colors']}
    if any(to_hex(c).lower() not in allowed for c in config.get('appearance',{}).get('colors',[])):
        raise ValueError('系列颜色必须来自所选已有配色')
    formats=list(FORMATS if formats is None else formats)
    if not formats or len(formats)!=len(set(formats)) or not set(formats)<=set(FORMATS):
        raise ValueError('formats must be a nonempty unique list of png/svg/pdf')
    if type(dpi) is not int or dpi<=0:raise ValueError('dpi 必须是正整数')
    if type(transparent) is not bool:raise ValueError('transparent 必须是 true 或 false')
    root=output_root(workspace,output);root.mkdir(parents=True,exist_ok=True)
    for ext in FORMATS:(root/ext).mkdir(exist_ok=True)
    name=reserve_stem(root,choose_stem(data_path,stem),formats)
    fig.set_dpi(dpi)
    validate_figure(fig,root/f'{name}.layout-checks.json',full_frame=full_frame)
    resolved=dict(config or {})
    if data_path is not None:
        source=Path(data_path)
        if not source.is_absolute():source=(Path(workspace) if workspace else Path.cwd())/source
        resolved['data']={**resolved.get('data',{}),'path':str(source.resolve())}
    resolved['output']={**resolved.get('output',{}),'stem':name,'directory':str(root),'formats':formats,
                        'dpi':dpi,'transparent':transparent}
    (root/f'{name}.resolved-config.yaml').write_text(yaml.safe_dump(resolved,allow_unicode=True,sort_keys=False),encoding='utf-8')
    targets=[]
    try:
        for ext in formats:
            target=root/ext/f'{name}.{ext}'
            targets.append(target)
            fig.savefig(target,dpi=dpi,transparent=transparent)
    except Exception:
        # Only remove files allocated by this failed export, never prior output.
        for target in targets:target.unlink(missing_ok=True)
        raise
    return targets
