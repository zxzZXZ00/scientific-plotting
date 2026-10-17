"""读取配置 → 读取数据 → 应用样式 → 绘图 → 导出。"""
import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import yaml
import importlib.util
import os
from matplotlib import font_manager

from plotting import read_data, plot_line_with_band
from settings import load_settings, resource
from layout_checks import validate_figure
from exporting import export_figure

ROOT = Path(__file__).resolve().parents[1]


def resolve_path(base, value):
    path = Path(value)
    return path if path.is_absolute() else base / path


def main():
    parser = argparse.ArgumentParser(description="CSV 科研绘图示例")
    parser.add_argument("--config", type=Path, default=ROOT / "assets/configs/line-with-band.yaml")
    parser.add_argument("--data", type=Path, help="覆盖配置中的 CSV 路径")
    parser.add_argument("--workspace",type=Path,help='当前用户工作空间；默认运行时当前目录')
    parser.add_argument("--output", type=Path, help='覆盖 sci_plots 根目录；相对 --workspace 解析')
    parser.add_argument('--formats',nargs='+',choices=['png','svg','pdf'],help='仅在用户明确要求时覆盖三格式默认值')
    parser.add_argument('--name',help='显式指定文件名，不含扩展名；默认使用 CSV 文件名')
    args = parser.parse_args()
    try:
        working=args.workspace.resolve() if args.workspace else Path.cwd()
        config_path = resolve_path(working,args.config).resolve()
        data_override=resolve_path(working,args.data) if args.data else None
        config = load_settings(config_path,data_override=data_override)
        template = config["template"]
        if template not in {"line", "line-with-band",'spectrum','sticks'} and not template.startswith("user:"):
            raise ValueError("内置支持 line、line-with-band、spectrum、sticks；用户模板使用 user:名称")
        base = config_path.parent
        data_path = data_override or resolve_path(base, config["data"]["path"])
        config["data"]["path"] = str(data_path.resolve())
        style_path = resolve_path(base, config["style"])
        output = config["output"]
        if args.formats:output['formats']=args.formats
        if args.name:output['stem']=args.name
        formats, stem, dpi = output["formats"], output["stem"], output["dpi"]
        if not isinstance(formats, list) or not formats or not set(formats) <= {"png", "pdf", "svg"}:
            raise ValueError("formats 只能是 png/pdf/svg 的非空列表")
        if not isinstance(stem,str) or not stem.strip():raise ValueError('stem 必须是非空名称；非法文件名字符由导出器替换')
        if type(dpi) is not int or dpi <= 0:
            raise ValueError("dpi 必须是正整数")
        if os.environ.get('SCI_PLOT_ARIAL'):font_manager.fontManager.addfont(os.environ['SCI_PLOT_ARIAL'])
        try:font_manager.findfont('Arial',fallback_to_default=False)
        except ValueError:raise ValueError('缺少 Arial 字体；安装合法 Arial 字体或设置 SCI_PLOT_ARIAL 为字体文件路径，不静默替换字体')
        with plt.style.context(str(style_path)):
            if template.startswith("user:"):
                module_path = resource("templates", template, ".py")
                spec = importlib.util.spec_from_file_location("user_plot", module_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                fig = module.render(config, data_path)
            else:
                groups = read_data(data_path, config["data"], band=template == "line-with-band")
                fig = plot_line_with_band(groups, config)
            try:
                for target in export_figure(fig,data_path=data_path,stem=stem,workspace=args.workspace,
                                           output=args.output,formats=formats,dpi=dpi,
                                           transparent=output['transparent'],config=config,
                                           full_frame=config['appearance'].get('full_frame',True)):
                    print(target.resolve())
            finally:
                plt.close(fig)
    except (OSError, ValueError, TypeError, KeyError, AttributeError, yaml.YAMLError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
