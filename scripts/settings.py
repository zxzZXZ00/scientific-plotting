"""主题默认值、用户覆盖和资源定位。用户资源仅在显式选择时使用。"""
from pathlib import Path
import re
import yaml
from scenes import select_scene, PROFILES
from matplotlib.colors import to_hex

ROOT = Path(__file__).resolve().parents[1]


def resource(kind, name, suffix=".yaml"):
    if not isinstance(name, str):
        raise ValueError("资源名必须是字符串")
    user = name.startswith("user:")
    identifier = name[5:] if user else name
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", identifier):
        raise ValueError("资源名只能使用小写字母、数字和连字符")
    base = ROOT / ("user-library" if user else "assets")
    return base / kind / (identifier + suffix)


def merge(base, overrides):
    result = dict(base)
    for key, value in overrides.items():
        if value == "default":
            continue
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = merge(result[key], value)
        else:
            result[key] = value
    return result


def load_settings(path,data_override=None):
    task = yaml.safe_load(path.read_text(encoding="utf-8"))
    purpose,evidence=select_scene(task,path,data_override)
    profile=PROFILES[purpose]
    theme_path = resource("themes", task.get("theme", profile['theme']))
    if not theme_path.is_file():raise ValueError('主题不在资源库中：'+str(task.get('theme',profile['theme'])))
    theme = yaml.safe_load(theme_path.read_text(encoding="utf-8"))
    defaults = dict(theme["defaults"])
    defaults['theme']=task.get('theme',profile['theme'])
    defaults['output']={**defaults.get('output',{}),'formats':['png','svg','pdf']}
    if purpose!='general':defaults['template']=profile['template']
    defaults['purpose']=purpose
    defaults['selection']={**evidence,'purpose':purpose,'theme':task.get('theme',profile['theme'])}
    if profile['template']=='spectrum':
        defaults['appearance']={**defaults.get('appearance',{}),'markers':[None]}
        defaults['data']={'x_order':'monotonic'}
    if profile['template']=='sticks':defaults['data']={'x_order':'increasing'}
    if "layout" in theme:
        defaults["layout"] = theme["layout"]
    style = Path(theme["style"])
    defaults["style"] = str((theme_path.parent / style).resolve())
    personal_path = ROOT / "user-library/settings.yaml"
    if personal_path.exists():
        personal = yaml.safe_load(personal_path.read_text(encoding="utf-8")) or {}
        if not isinstance(personal, dict) or set(personal) - {"figure", "output"}:
            raise ValueError("个人统一设置仅支持 figure 和 output")
        for section, allowed in (("figure", {"width_mm", "height_mm"}),
                                 ("output", {"dpi", "transparent", "formats"})):
            values = personal.get(section, {})
            if not isinstance(values, dict) or set(values) - allowed:
                raise ValueError(f"个人统一设置 {section} 包含不支持的字段")
        defaults = merge(defaults, personal)
    config = merge(defaults, task)
    if task.get('purpose','auto')=='auto':config['purpose']=purpose
    # 任务显式 style 路径相对任务配置解析。
    if task.get("style", "default") != "default":
        config["style"] = str((path.parent / task["style"]).resolve())
    palette_path=resource('palettes',config['palette'])
    if not palette_path.is_file():raise ValueError('配色不在资源库中：'+str(config['palette']))
    palette = yaml.safe_load(palette_path.read_text(encoding="utf-8"))
    config.setdefault("appearance", {})
    if task.get("appearance", {}).get("colors", "default") == "default":
        config["appearance"]["colors"] = palette["colors"]
    allowed={to_hex(c).lower() for c in palette['colors']}
    if any(to_hex(c).lower() not in allowed for c in config['appearance']['colors']):
        raise ValueError('系列颜色必须来自所选的已有配色；库外配色需先按资源新增流程登记')
    config.setdefault('selection',{}).update({'theme_resource':str(theme_path.relative_to(ROOT)),
                                             'palette_resource':str(palette_path.relative_to(ROOT))})
    # Theme names are never the implicit export filename. Task-level names are
    # explicit overrides; otherwise use the actual input file, including --data.
    if task.get('output',{}).get('stem','default')=='default':
        value=data_override or task.get('data',{}).get('path')
        config['output']['stem']=Path(value).stem if value else 'figure'
    return config
