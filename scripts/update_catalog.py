"""Generate/check the query index from actual registered YAML resources."""
import argparse
from pathlib import Path

import yaml

ROOT=Path(__file__).resolve().parents[1]
TARGET=ROOT/'references/available-resources.md'
NAMES={'paper':'通用论文','blue-red':'蓝红','red-cyan':'红青','peach-teal':'桃橙青绿',
       'mist-blue-rose':'雾蓝玫粉','blue-magenta':'蓝洋红'}


def resources(kind):
    result={}
    for directory,prefix in [('assets',''),('user-library','user:')]:
        for file in sorted((ROOT/directory/kind).glob('*.yaml')):
            result[prefix+file.stem]=(file,yaml.safe_load(file.read_text(encoding='utf8')))
    return result


def content():
    palettes=resources('palettes');themes=resources('themes')
    lines=['# 现有主题与配色','',
           '<!-- Generated from registered resources by scripts/update_catalog.py; do not edit tables manually. -->','',
           '用户随时可询问“有哪些主题”“有哪些配色”“给我看主题示例”。直接回答现有资源，不要求先上传数据或开始绘图。',
           '主题与配色可分别选择；用途是建议，跨领域可以借用。所有绘图必须命中已有资源，imports 候选不列入。','',
           '## 主题','',
           '| 名称 | 调用名称 | 默认配色 | 默认图型 | 图片示例 |',
           '| --- | --- | --- | --- | --- |']
    for identifier,(path,theme) in themes.items():
        defaults=theme['defaults'];palette=defaults['palette']
        if palette not in palettes:raise ValueError(f'{identifier}: default palette missing: {palette}')
        if not (path.parent/theme['style']).is_file():raise ValueError(f'{identifier}: style file missing')
        label=theme.get('display_name',NAMES.get(path.stem,path.stem))
        preview=(ROOT/'user-library/examples'/path.stem/'preview.png') if identifier.startswith('user:') else ROOT/'assets/examples/line-with-band/preview.png'
        if not preview.is_file() and identifier.startswith('user:'):
            preview=ROOT/'user-library/examples'/path.stem/'reproduction.png'
        image=f'[预览](../{preview.relative_to(ROOT).as_posix()})' if preview.is_file() else '暂无预览'
        lines.append(f'| {label} | `{identifier}` | `{palette}` | `{defaults["template"]}` | {image} |')
    lines += ['','## 配色','','| 名称 | 调用名称 | 系列色号 |','| --- | --- | --- |']
    for identifier,(path,palette) in palettes.items():
        label=palette.get('display_name',NAMES.get(path.stem,path.stem))
        lines.append(f'| {label} | `{identifier}` | '+ '、'.join('`'+str(c)+'`' for c in palette['colors'])+' |')
    lines += ['','[主题图组总览](../assets/theme-gallery.png) · [用法与示例](usage.md) · [用途与文献来源](scene-routing.md) · [资源详情](../user-library/catalog.md)','',
              '图组总览展示已认可的文献参考重建，包含演示值/近似示意；单图预览展示通用绘图调用。普通命令的已实现图型以 gallery.md 为准。','',
              '维护：新增、改名、修改或移除主题/配色后运行 `python scripts/update_catalog.py`；打包前运行同一命令加 `--check`，发现索引过期或依赖缺失即失败。','']
    return '\n'.join(lines)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
    expected=content()
    if args.check:
        if not TARGET.is_file() or TARGET.read_text(encoding='utf8')!=expected:
            parser.error('资源查询索引已过期；运行 python scripts/update_catalog.py 更新')
        print('Resource index and dependencies are current.')
    else:
        TARGET.write_text(expected,encoding='utf8');print(TARGET)


if __name__=='__main__':main()
