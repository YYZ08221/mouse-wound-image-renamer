# Mouse Wound Image Renamer | 小鼠伤口实验图片重命名工具

面向小鼠伤口愈合实验的 Windows 本地图片整理工具。逐张查看照片，按实验、分组、鼠号、时间点和拍摄部位命名，再复制到统一输出目录，为后续伤口检测、分割、面积测量准备数据。

**当前版本提供人工看图、重命名与图片整理，尚未实现自动伤口检测、分割、面积测量或愈合率计算。** 鼠号、组别和天数由研究人员核对并输入。

项目地址：<https://github.com/YYZ08221/mouse-wound-image-renamer>

## 适用场景

- 将相机导出的 `IMG_1234.jpg` 改成包含实验信息的文件名。
- 统一同一只小鼠在 D00、D03、D07 等时间点的图片名称。
- 在伤口检测、分割前人工核对图片，保留原始文件与新名称的对应日志。
- 大量图片需要逐张处理、跳过、撤销和中断后继续。

图片全部在本机处理。程序没有网络上传、AI 接口调用或模型推理功能。

## 功能一览

| 功能 | 当前行为 |
| --- | --- |
| 图片读取 | 读取所选目录第一层文件，不递归子目录，忽略非图片 |
| 自然排序 | `1.jpg`、`2.jpg`、`10.jpg` 按 1、2、10 排列 |
| 图片预览 | 随窗口等比例缩小，不拉伸 |
| 手动命名 | 逐张输入新名称，可以省略扩展名 |
| 自动编号 | 可配置前缀、起始编号、补零位数 |
| 保存 | 复制原始文件，尽量保留修改时间 |
| 同名处理 | 自动追加编号、重新输入或跳过，默认不覆盖 |
| 回退 | 上一张、跳过、撤销最近一次保存 |
| 操作记录 | CSV 日志、JSON 会话、最近会话恢复提示 |

支持 `.jpg`、`.jpeg`、`.png`、`.bmp`、`.webp`、`.tif`、`.tiff`，支持中文及含空格路径。

## 环境要求

- Windows 10/11，可交互桌面。
- Python 3.10 或更高版本，安装时包含 Tcl/Tk（tkinter）；已在 Python 3.14.5 验证。
- Pillow；tkinter 为 Python 组件，无需执行 `pip install tkinter`。
- 克隆安装需要 Git，也可在 GitHub 页面选择 Code → Download ZIP 后解压。

## 安装：普通用户

打开 PowerShell，执行以下命令。目录可以替换成自己的位置；已有项目时直接进入已有目录，不要克隆到非空目录。

```powershell
git clone https://github.com/YYZ08221/mouse-wound-image-renamer.git "D:\程序\图片重命名系统"
Set-Location -LiteralPath "D:\程序\图片重命名系统"
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

若通过 ZIP 下载，进入解压后包含 `main.py` 的目录，再从 `python -m venv .venv` 开始执行。
`.venv` 是项目独立环境，不需要手动激活。现有 Python 环境已安装 Pillow 时，也可直接运行 `python main.py`。

## 安装：自动脚本

在项目目录运行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\install.ps1 -GuiCheck
```

脚本自动创建 `.venv`、安装依赖、执行核心测试、语法检查及安装自检。
`-GuiCheck` 会短暂打开窗口，约半秒后关闭，不读取历史会话、不处理图片。
执行策略仅作用于该子进程，不修改系统级设置。

若 `python` 指向 Microsoft Store 占位程序或版本不合适，可指定真实解释器：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\install.ps1 -Python "C:\Path\To\Python\python.exe" -GuiCheck
```

加 `-Launch` 可在安装后直接打开程序，直到用户关闭窗口命令才结束。
以后使用无需重新安装，进入项目目录执行：

```powershell
.\.venv\Scripts\python.exe main.py
```

## 让 Agent 智能体安装

将下面的文字交给有本地终端权限的编程 Agent：

```text
请从 https://github.com/YYZ08221/mouse-wound-image-renamer 安装这个 Windows 应用。
先阅读 README.md、AGENTS.md 和 docs/AGENT_INSTALL.md。
选择不会覆盖已有文件的安装目录，使用项目内 .venv 安装依赖。
执行 install.ps1 -GuiCheck，报告核心测试、自检和 GUI 启动验证结果。
若没有交互桌面，省略 -GuiCheck，并明确说明 GUI 尚未验证。
向我提供实际安装目录、Python 路径和启动命令。
不要把我的实验图片、日志和本机会话提交到仓库。
这个工具用于小鼠伤口实验图片的人工核对、命名和整理。
```

详细部署步骤见 [Agent 安装指南](docs/AGENT_INSTALL.md)。
不需要把项目安装成 Agent Skill，不需要模型 API Key 或 GPU。
Agent 负责部署；GUI 中的实验信息由研究人员确认。目前没有无界面批量处理接口。

## 第一次使用

1. 点击“选择输入文件夹”，选择原始图片目录。
2. 点击“选择输出文件夹”，选择独立的重命名结果目录。
3. 点击“开始”，程序按自然顺序显示图片。
4. 核对当前图片，在“新文件名”输入框填写名称。
5. 点击“保存并下一张”或按 Enter，生成重命名副本并显示下一张。
6. 不处理当前图片时点击“跳过”；全部处理后提示“全部完成”。

建议将输入和输出分开，例如输入 `D:\wound_study\raw\D03`，输出 `D:\wound_study\renamed\D03`。
首次使用可以准备几张测试图片，熟悉保存、冲突和撤销。

## 小鼠伤口实验命名示例

建议先统一命名格式：

```text
实验编号_分组_鼠号_时间点_伤口部位_重复序号.扩展名
W01_CTRL_M003_D00_dorsal_01.jpg
W01_CTRL_M003_D03_dorsal_01.jpg
W01_TREAT_M008_D07_left_01.tif
```

| 字段 | 示例 | 用途 |
| --- | --- | --- |
| 实验编号 | W01 | 区分实验批次 |
| 分组 | CTRL、TREAT | 研究人员确认的组别，盲法流程可用编码 |
| 鼠号 | M003 | 同一只小鼠跨时间点保持一致 |
| 时间点 | D00、D03、D07 | 按实验约定填写时间点 |
| 伤口部位 | dorsal、left、right | 区分同一只小鼠的部位或伤口 |
| 重复序号 | 01、02 | 区分同条件下重复拍摄 |

示例：选择 D03 图片目录，从实验记录核对鼠号后，输入
`W01_CTRL_M003_D03_dorsal_01`，按 Enter。程序沿用原扩展名，CSV 记录原路径和新文件名。
命名格式是建议，软件不会自动识别或校验这些实验字段。

整理后可以导入 ImageJ/Fiji 或其他伤口检测、分割软件。
本程序 CSV 是文件操作日志，不包含伤口面积、像素标定、检测框或分割掩膜。

## 手动命名与同名处理

输入 `mouse_003` 时沿用原后缀，例如保存为 `mouse_003.jpg`。
输入扩展名时只接受支持的图片后缀。**复制操作不会转换图像编码**，
建议省略扩展名或保持原后缀，避免 JPEG 内容却使用 PNG 后缀。
名称中最后一个点后的部分会被视为扩展名，推荐用下划线连接字段。

文件名不能为空，不能包含以下 Windows 禁用字符：

```text
\ / : * ? " < > |
```

避免 CON、NUL 等系统保留名、末尾句点、控制字符及过长名称。
程序会检查常见非法字符及后缀；其他系统限制可能在保存时报错。

遇到输出重名时：

| 弹窗按钮 | 操作 |
| --- | --- |
| 是 | 自动追加 _001、_002 等编号后保存 |
| 否 | 留在当前图片重新输入名称 |
| 取消 | 跳过当前图片 |

## 自动编号模式

勾选“自动编号模式”的“启用”，填写前缀 `W01_CTRL_D03_`、起始编号 `1`、位数 `3`。
结果例如 `W01_CTRL_D03_001.jpg`、`W01_CTRL_D03_002.jpg`。

当前编号为“起始编号 + 图片在列表中的索引”，跳过会留下空号，返回上一张仍沿用该张的位置编号。
自动编号依赖文件顺序，不代表识别鼠号；重复照片或混合时间点建议手动命名。
自动编号参数目前不随会话恢复，续做时请重新核对。

## 跳过、上一张与撤销

- 跳过：不复制当前图片，记录 skipped 并进入下一张。
- 上一张：只移动浏览位置，不删除已保存文件；再次保存可能出现重名。
- 撤销上一次保存：删除最近副本，回到对应图片并恢复输入，记录 undone。
- 目标已被手动删除：提示“目标文件不存在，已仅回退进度”。

撤销会删除对应输出路径的文件，请勿在撤销前用其他文件替换该副本。
保存默认使用 `shutil.copy2` 复制，尽量保留修改时间，不移动或修改原图。

## 快捷键

| 快捷键 | 功能 |
| --- | --- |
| Enter / Ctrl + S | 保存并下一张 |
| Ctrl + Z | 撤销上一次保存 |
| Left | 上一张 |
| Right | 跳过当前图片 |
| Esc | 清空当前输入框 |

方向键用于图片导航，编辑名称时可用鼠标定位光标。

## 日志与断点续做

输出目录生成 `rename_log_YYYYMMDD_HHMMSS.csv` 和 `session_state.json`。
CSV 为 UTF-8 BOM 编码，可以用 Excel 打开：

| 字段 | 内容 |
| --- | --- |
| index | 图片位置索引，从 0 开始 |
| original_path / original_name | 原始路径和名称 |
| new_name / output_path | 副本名称和路径 |
| action | saved、skipped、undone |
| timestamp | 操作时间 |
| status / note | 操作状态及备注 |

成功保存、跳过和撤销时追加日志；重新开始或恢复会话可能生成新的日志文件。
会话文件记录目录、当前进度、已处理/跳过文件及保存记录。
项目内 `logs/last_session.json` 记录最近会话位置，便于启动时提示恢复。

下次启动发现最近会话时询问是否继续；也可选择原输出目录触发询问。
恢复前应保持原图目录、文件列表及输出副本不变，避免增删图片造成位置偏移。
恢复目前基于排序位置，已完成会话可能再次显示最后一张，应先核对进度。
每个输出目录只保存一份会话，不同实验或批次建议使用独立输出目录。

## 项目结构

```text
mouse-wound-image-renamer/
├─ main.py                 # 应用入口
├─ requirements.txt        # Pillow
├─ install.ps1             # Windows 自动安装
├─ README.md               # 用户教程
├─ AGENTS.md               # Agent 部署及修改约定
├─ docs/AGENT_INSTALL.md    # Agent 安装指南
├─ scripts/check_install.py
├─ src/                    # GUI、图片加载、命名、日志、会话
├─ tests/test_core.py       # 核心逻辑测试
├─ logs/                   # 本机会话指针，不上传
└─ backup/                 # 预留目录，目前无自动备份逻辑
```

## 验证安装

在项目根目录运行：

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m compileall -q main.py src scripts
.\.venv\Scripts\python.exe scripts/check_install.py --gui
```

核心测试覆盖自然排序、图片后缀过滤、基础命名、同名编号及文件复制。
`--gui` 验证窗口创建和短暂事件循环，不等于所有按钮完整交互测试。
无桌面时去掉 `--gui`，只能验证依赖和模块导入。

## 常见问题

| 问题 | 处理方法 |
| --- | --- |
| python 不存在或跳转商店 | 安装 Python 或为脚本指定真实解释器 |
| No module named PIL | 用项目 .venv 的 Python 安装 requirements.txt |
| 缺少 tkinter | 修复 Python 安装并启用 Tcl/Tk |
| 找不到图片 | 检查文件后缀和层级，当前不递归子目录 |
| 图片打不开 | 状态栏提示损坏，可手动跳过后检查源文件 |
| 输出不可写 | 选择有写权限的独立目录 |
| 会话 JSON 损坏 | 保留副本后移走损坏记录，开始新会话 |
| 无法创建窗口 | 使用交互式 Windows 桌面，避免无桌面服务环境 |

## 当前边界与后续方向

当前重点是小鼠伤口检测前的数据整理。后续可增加缩略图列表、结构化实验字段、
盲法编码映射、CSV 命名表导入，以及独立的伤口检测/分割模块。
面积与愈合率分析还需要单独实现标定、测量与验证。

.gitignore 排除了常见图片、数据目录、会话、日志和虚拟环境。研究数据应独立管理。
