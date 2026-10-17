# 打包、环境与安装后的说明

## 已验证环境

实际验证环境为 Windows 11 x64、CPython 3.12.10：Matplotlib 3.11.2、NumPy 2.5.2、PyYAML 6.0.3、PyMuPDF 1.28.2，Arial 来自系统字体。
requirements.txt 固定这组 Python 包版本。当前 NumPy 版本要求 Python 3.12 或以上；优先使用 Python 3.12 建立独立虚拟环境。其他系统尚未在本项目验证，不应声称已测试。

Matplotlib、NumPy、PyYAML 用于绘图、检查与配置；PyMuPDF 用于阅读/提取 PDF 和重放矢量参考图。不需要 Excel、pandas、SciPy、LaTeX 或外部 PDF 编译器。
Arial 不随 ZIP 分发。系统没有 Arial 时，使用用户合法持有的 Arial 字体进行安装，或将 SCI_PLOT_ARIAL 环境变量设置为字体文件路径；脚本不会悄悄替换为其他字体。

以实际安装目录替换 <SKILL_DIR>，以实际虚拟环境解释器替换 <PYTHON>：

```text
python -m venv <ENV_DIR>
<PYTHON> -m pip install -r <SKILL_DIR>/requirements.txt
<PYTHON> <SKILL_DIR>/scripts/check_environment.py
```

Windows 的虚拟环境解释器为 <ENV_DIR>/Scripts/python.exe，macOS/Linux 通常为 <ENV_DIR>/bin/python。可直接使用解释器完整路径，不依赖激活虚拟环境。
保留用户选择的环境；有可用且兼容的现有环境时先检查，不重复安装。只报告实际完成的步骤。

## ZIP 与跨工作空间

ZIP 顶层是 scientific-plotting/，其下直接包含 SKILL.md、agents/、scripts/、references/、assets/、user-library/ 和 requirements.txt。
user-library 必须保留已认可主题、配色、样式及 examples 中的依赖；矢量归档的 source.pdf 不可遗漏。
排除 imports/、outputs/、sci_plots/、__pycache__/、*.pyc 和本机虚拟环境，不把候选、测试输出或绝对路径当作安装资源。
轻量包只保留有展示用途的主题 PNG 预览与总览；重复原图截图、对照图、局部检查图、静态 SVG 导出和开发阶段输出移到技能目录外归档，不随 ZIP 分发。SVG/PDF 可随时从代码重新生成。
清理前检查代码的真实读取依赖：本库的两个 source.pdf 被矢量复现脚本直接使用，必须保留；代码、CSV、主题/配色/样式、来源及认可记录也要保留。不能按“所有非预览文件都删掉”处理。

将完整目录安装到用户的全局技能目录：设置了 CODEX_HOME 时为其 skills/scientific-plotting，否则通常为 ~/.codex/skills/scientific-plotting。不要只解压到某一个项目并声称换工作空间后仍能自动发现。
Python 环境可放在用户自行选择的持久位置，并在以后调用时继续使用同一解释器；不要在资源文件中固定开发机器的 E: 盘或用户名。
代码从 __file__ 定位技能资源，从当前工作空间定位生成结果。因此调用程序时不要为了找资源而把运行目录切到安装目录。

## 安装后主动告知用户

确认资源安装且环境检查通过后，主动给出简短说明，不等待用户追问：

用法直接读取 usage.md；当前主题/配色读取 available-resources.md。用户之后随时询问也同样回答，不限安装后的第一次。

1. 安装结果和 Python/字体检查状态。
2. 一个自然语言用法，例如“使用蓝洋红主题，读取 spectrum.csv，绘制光谱图”；再给一个可选项示例，如“使用红青主题和雾蓝玫粉配色，读取 experiment.csv，绘制折线图”。
3. 说明所有绘图必须使用库中已有的主题与配色；用户指定优先。未指定时从现有库酌情挑选，文献领域是推荐依据，不是使用限制。
4. 说明默认输出到当前工作空间的 sci_plots/png、sci_plots/svg、sci_plots/pdf，默认三格式齐全，名字沿用输入文件名；明确要求可覆盖格式、位置及名称。
5. 尽可能内嵌展示 assets/theme-gallery.png；也可展示 user-library/examples/<名称>/preview.png 或 reproduction.png。不能内嵌时给出实际可访问的文件链接，不编造图片。

示例安装后回复：

“已安装，Python 3.12 与 Arial 检查通过。可说：‘使用蓝洋红主题读取 spectrum.csv，绘制光谱图。’也可分别指定已有主题和配色；不指定时从库内选择合适的一套。默认生成 sci_plots/png/spectrum.png、svg/spectrum.svg、pdf/spectrum.pdf。下面是现有主题示例。”

环境未就绪时说明缺失项及上面的安装/检查命令，不声称已经可以正常绘图。主题预览只是风格示例，不是用户的新实验结果。

维护或打包前运行 scripts/test_execution.py 和 scripts/test_layout_checks.py。前者验证已有资源限制、三格式/命名、--data 覆盖及跨工作空间调用；后者验证排版防御。运行测试不会安装依赖。
同时运行 scripts/update_catalog.py --check，防止打包进过期的资源查询目录；同步要求见 maintenance.md。
