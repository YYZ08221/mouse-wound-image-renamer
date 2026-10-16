# 让 Agent 安装和启动

本指南面向能执行本机终端命令的编程 Agent。安装的是本地 Python GUI 应用，
不需要模型 API Key、GPU、云服务或 Agent 插件。Agent 负责部署，研究人员在窗口中查看并命名图片。

## 可以直接发给 Agent 的指令

```text
请安装 https://github.com/YYZ08221/mouse-wound-image-renamer 到 Windows 本地。
先阅读仓库 README.md 和 AGENTS.md，按照 docs/AGENT_INSTALL.md 操作。
使用项目独立的 .venv，安装 requirements.txt，运行核心测试和安装自检。
有交互桌面时执行 GUI 启动检查，向我报告安装目录、Python 路径和启动命令。
用于小鼠伤口实验图片的人工核对和重命名，保留原图，不上传实验图片。
安装完成后告诉我如何打开程序；需要实际数据命名时由我提供分组、鼠号和时间点。
```

仓库公开，可直接通过 HTTPS 克隆，无需 GitHub Token。不要把 Token 写进脚本或仓库。

## 终端步骤

需要 Git，以及包含 tkinter 的 Python 3.10 或更高版本；已验证版本见 README。
以下为 PowerShell 命令，可按需要调整安装路径：

```powershell
git clone https://github.com/YYZ08221/mouse-wound-image-renamer.git "D:\程序\图片重命名系统"
Set-Location -LiteralPath "D:\程序\图片重命名系统"
powershell -NoProfile -ExecutionPolicy Bypass -File .\install.ps1 -GuiCheck
.\.venv\Scripts\python.exe main.py
```

若目标目录已存在且非空，先检查其中内容；已有本项目 checkout 就使用该目录，
否则选择新目录，不要覆盖用户文件。若 `python` 指向 Microsoft Store 占位程序，
用 `-Python` 参数指定真实解释器：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\install.ps1 -Python "C:\Path\To\Python\python.exe" -GuiCheck
```

`-GuiCheck` 创建窗口并在约半秒后关闭，不读取历史会话、不处理图片。
无交互桌面时省略该参数；自检通过不代表 GUI 已实际验证。
`-Launch` 可在安装成功后直接进入程序，持续到用户关闭窗口。

## 手动安装与验收

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m compileall -q main.py src scripts
.\.venv\Scripts\python.exe scripts/check_install.py --gui
```

验收时确认测试通过、自检输出 `Installation check: OK`，有桌面时还应看到
`GUI startup: OK`。只使用临时合成图片验证保存和撤销，确认输出内容与原图相同。
此程序目前没有无界面批量处理接口；启动 GUI 后仍需人工操作。

## 常见故障

- `No module named PIL`：使用 `.venv\Scripts\python.exe -m pip install -r requirements.txt`。
- 缺少 tkinter：修复 Python 安装，启用 Tcl/Tk 组件；不要执行 `pip install tkinter`。
- 无法拉取仓库：确认 GitHub 登录账号有访问私有仓库的权限。
- 无法创建窗口：切换到已登录的 Windows 桌面会话，服务/无界面环境只能完成非 GUI 检查。
- 输出目录不可写：选择有写权限的新目录，并与输入目录分开。
