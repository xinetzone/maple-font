# maple-font

一个 Python 包装器，直接调用 Maple Mono 官方 Local Build 流程构建字体，并自动注册到 Matplotlib / Pillow 中使用，提供了丰富的命令行和 Python API 接口。

## 📚 项目简介

Maple Mono 是一款优雅的等宽编程字体，支持英文、中文和各种编程符号。本包装器极大简化了 Maple Mono 字体的构建和使用流程，让您可以轻松在 Python 项目中使用这款美观的字体。

## 🚀 快速开始

### 安装

#### 普通安装
```bash
pip install maple-font
```

#### 开发模式安装
如果您需要参与开发或修改源码：
```bash
pip install -ve .
```

### 首次使用

首次导入或执行命令时，包装器会自动构建字体文件（约需要 2-3 分钟）：
```python
import maple_font
```

## 🖥️ 命令行使用

包装器提供了功能丰富的命令行接口：

```bash
# 构建字体（默认使用最小样式）
maple-font build

# 构建完整版本字体
maple-font build --full

# 强制重新构建字体
maple-font build --force

# 构建指定参数的版本
maple-font build --args --ttf-only --nf --cn

# 注册已构建字体到 Matplotlib
maple-font register

# 注册特定类型的字体
maple-font register --font-type NF

# 一键设置 Matplotlib 使用 Maple Mono 字体
maple-font set-font

# 检查字体安装状态
maple-font check
```

### 命令说明

| 命令 | 说明 | 常用选项 |
|------|------|---------|
| `build` | 构建字体文件 | `--force`（强制重建）, `--full`（完整版本）, `--args`（自定义参数） |
| `register` | 注册字体到 Matplotlib | `--font-type`（字体类型，如 NF-CN, NF）, `--silent`（静默模式） |
| `set-font` | 一键设置 Matplotlib 使用 Maple Mono 字体 | `--font-type`（字体类型） |
| `check` | 检查字体安装状态 | `--font-type`（指定字体类型） |

### 常用构建参数

| 参数 | 说明 |
|------|------|
| `--ttf-only` | 仅生成 TTF 格式字体 |
| `--nf` | 包含 Nerd Font 图标 |
| `--cn` | 包含中文字符支持 |
| `--least-styles` | 仅生成最基本的字重样式 |
| `--normal` | 生成常规版本（非变宽版本） |

## 🐍 Python API 使用

### 基础用法

在 Python 代码中快速使用 Maple Mono 字体：

```python
# 最简单的方式：一键设置字体
from maple_font import set_font
set_font()  # 默认使用 NF-CN 类型

# 然后就可以直接使用 Matplotlib 绘图了
import matplotlib.pyplot as plt
plt.plot([1, 2, 3], [4, 5, 6])
plt.title("使用 Maple Mono 字体展示")  # 中文会正常显示
plt.show()
```

### 高级用法

更多控制选项：

```python
from maple_font import enhanced_register_fonts, get_font_family_name, fonts_dir, get_font_path
import matplotlib.pyplot as plt

# 注册特定类型的字体
success = enhanced_register_fonts(font_type="NF", silent=False)
if success:
    # 获取字体族名称
    font_family = get_font_family_name("NF")
    # 设置 Matplotlib 使用这个字体
    plt.rcParams["font.family"] = font_family
    print(f"已设置 Matplotlib 使用字体: {font_family}")

# 创建示例图表
plt.figure(figsize=(10, 6))
plt.plot([1, 2, 3], [4, 5, 6])
plt.title("Maple Mono 字体示例")
plt.xlabel("X轴示例")
plt.ylabel("Y轴示例")
plt.grid(True)
plt.show()

# 获取字体目录路径
print("字体目录:", fonts_dir())

# 获取特定字体文件路径
font_path = get_font_path("MapleMono-NF-CN-Regular.ttf")
print("特定字体路径:", font_path)
```

### 可用函数

- `set_font(font_type="NF-CN", silent=False)`: 一键设置 Matplotlib 使用指定的 Maple Mono 字体
  - `font_type`: 字体类型，可选值为 'NF-CN', 'NF', 'TTF', 'TTF-AutoHint', 'Variable'
  - `silent`: 是否静默执行，不打印提示信息
  - 返回值: 是否成功设置字体 (bool)

- `enhanced_register_fonts(font_type="NF-CN", silent=False)`: 增强的字体注册函数
  - `font_type`: 要注册的字体类型
  - `silent`: 是否静默执行
  - 返回值: 是否成功注册字体 (bool)

- `register_fonts(silent=False)`: 注册字体到 Matplotlib/Pillow
  - `silent`: 是否静默执行

- `fonts_dir()`: 返回字体文件存储目录

- `get_font_path(name)`: 获取特定字体文件的完整路径
  - `name`: 字体文件名或相对于字体目录的路径
  - 返回值: 字体文件的绝对路径字符串

- `get_font_family_name(font_type="NF-CN")`: 获取指定字体类型的 Matplotlib 字体族名称
  - `font_type`: 字体类型
  - 返回值: 字体族名称字符串

- `ensure_latest()`: 确保使用最新版本的字体（重新构建并注册）

## 🎨 字体特性

- 支持英文、中文和日文等多语言字符
- 集成 Nerd Font 图标，适用于各种终端和编辑器
- 等宽设计，完美适配编程场景
- 支持多种字重（Regular、Bold 等）
- 支持斜体样式

## 📝 示例脚本

项目提供了一系列示例脚本，存放在 `examples/` 目录下，展示了所有主要功能的使用方法：

### 基础示例

基础示例脚本展示了 maple-font 包的基本功能：

```bash
cd examples
python basic_usage.py
```

基础示例包含以下内容：
- 基本用法：注册字体并设置 Matplotlib 使用它
- 一键设置：使用 `set_font` 函数快速设置字体
- 不同字体类型：尝试不同类型的 Maple Mono 字体
- 创建图形：使用 Maple Mono 字体创建包含中文的图形
- 静默模式：在不打印信息的情况下使用字体

### 高级示例

高级示例脚本展示了 maple-font 包的更多高级功能和复杂使用场景：

```bash
cd examples
python advanced_usage.py
```

高级示例包含以下内容：
- 高级字体选择：自动检测系统上的字体可用性并选择最佳字体
- 字体设置保存与恢复：保存当前字体设置并在需要时恢复
- 多图表环境：在一个脚本中为不同图表使用不同字体
- 复杂可视化：创建包含多种元素的复杂图表

详细的示例说明可以在 `examples/README.md` 文件中找到。

## 🎨 字体特性

- 支持英文、中文和日文等多语言字符
- 集成 Nerd Font 图标，适用于各种终端和编辑器
- 等宽设计，完美适配编程场景
- 支持多种字重（Regular、Bold 等）
- 支持斜体样式

## 📁 项目结构

```
maple-font/
├── build.py               # 官方构建脚本
├── requirements.txt       # 依赖清单
├── pyproject.toml         # 项目配置
├── README_PYPI.md         # 本文件
└── src/maple_font/
    ├── __init__.py        # 包入口
    ├── _builder.py        # 构建封装
    ├── _register.py       # 字体注册功能
    ├── cli.py             # 命令行接口
    └── data/fonts/        # 构建后的字体存储位置
```

## 📝 注意事项

- 首次构建字体可能需要 2-3 分钟时间，请耐心等待
- 字体构建需要足够的磁盘空间（约 500MB）
- 确保您的 Python 版本 ≥ 3.8

## 🤝 贡献指南

欢迎提交 Issue 或 Pull Request 来帮助改进这个项目！

## 📄 许可证

本项目基于 MIT 许可证开源。
