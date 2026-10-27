# 快速开始 — Ren’Py Text Editor

这是带有桌面图形界面的 Ren’Py 台词编辑器，可以在表格中写作、直接查看文字格式，并导出剧本。

[English](quickstart.en.md) · [日本語](quickstart.ja.md) · [简体中文](quickstart.zh-CN.md) · [繁體中文](quickstart.zh-TW.md)

## 下载与启动

- [下载 Windows 10/11 x64 版](https://github.com/akihium/renpy-text-editor/releases/latest/download/RenPy-Text-Editor-Windows-x64.zip)
- [下载 macOS 14 及以上 Apple Silicon 版](https://github.com/akihium/renpy-text-editor/releases/latest/download/RenPy-Text-Editor-macOS-arm64.zip)
- [所有版本与更新说明](https://github.com/akihium/renpy-text-editor/releases/latest)

选择适合自己电脑的 ZIP；打包版不需要安装 Python。Windows 请**完整解压**，然后在解压后的文件夹中运行 `RenPy Text Editor.exe`，保留它旁边的文件和文件夹。macOS 解压后打开 `RenPy Text Editor.app`。

## 加载附带的示例工程

1. 启动软件，在启动界面的 **Language / 界面语言** 选择 **简体中文**。
2. 在 **Sample · 示例** 选择台词、分支／演出或 NVL 示例。程序会创建全新本机副本，可以自由修改。
3. 修改后从 **最近打开的项目** 继续编辑。再次点击 Sample 会创建另一份干净副本，不会清除之前的修改。
4. 想自己指定位置时，在编辑器点击另存／变更位置，程序会一起复制素材。
5. 选择章节／段落，编辑单元格并尝试格式按钮。视觉模式显示效果，原始标签模式显示完整标签。

软件包内包含四种语言的示例：

| 语言 | 解压后的示例文件夹 |
| --- | --- |
| 简体中文 | `examples/zh_CN/` |
| 繁体中文 | `examples/zh_TW/` |
| 日语 | `examples/ja/` |
| 英语 | `examples/en/` |

如果下载的是**源代码 ZIP**，示例位于 `examples/localized/<语言>/`；请先按照 [源代码启动说明](https://github.com/akihium/renpy-text-editor#run-from-source) 安装 Python 与依赖。

**开启项目** 应选择 `.advdb` 文件。`.xlsx` 用于 Excel 导入导出；`renpy_game/adv_generated/` 是已导出的 Ren’Py 脚本示例。切换界面语言只会改变操作界面，不会翻译工程里的台词；想看另一种语言的台词，请打开对应语言的示例。

## 创建与编辑自己的工程

点击 **新增项目**，选择项目文件夹，或在选择窗口中创建新文件夹。程序会在其中创建同名数据库和素材文件夹。在表格中填写角色代号、台词和备注；通过主界面的角色管理设置显示名称和颜色。

- **Tab / Shift+Tab：** 下一列／上一列。
- **Enter：** 完成编辑，跳到下一行角色栏；最后一行会自动新增一行。
- **Shift+Enter：** 台词内换行。
- **Ctrl+S / Cmd+S：** 保存。格式与撤销等快捷键在 Windows 使用 Ctrl，macOS 使用 Command。

在章节／段落管理中创建分支，再新增选项并指定目标。主界面也能导入背景和字体。**只显示文本** 会暂时隐藏演出，不会删除数据。

手动移动工程时，请把 `story.advdb` 和对应的 `story_assets/` 一起移动。使用 **另存／变更位置** 会自动复制两者。

## 导出

点击主界面的 **导出 .rpy**，默认保存位置是项目文件夹。用于 Ren’Py 时，请选择游戏的 `game` 文件夹或其中的文件夹。可自定义子文件夹名，或直接保存到所选文件夹；字体和图片路径同步更新，已有手写文件会保留。章节／段落管理可修改或清空 label 前缀 `adv_`。默认前缀的入口示例：

```renpy
label start:
    call adv_opening
    return
```

使用自己的段落时，请把 `adv_opening` 换成导出文件里的对应 label。Word／PDF 支持自定义标题及是否包含台词 ID；RPY 的 ID 开关独立控制。

软件完全离线运行，不包含 Ren’Py SDK 或游戏内预览，发布前请在 Ren’Py 中测试导出结果。打包版未使用商业开发者证书签名，也未进行 macOS 公证。

## NVL 写作

在角色管理中，可以分别为角色和旁白设置 ADV 或 NVL。在适当位置点击 **NVL 清页** 分页；选项设置可勾选 **以 NVL 模式显示选项**，并决定选择后是否清页。启动界面可以打开 NVL 示例，也可直接打开 `examples/zh_CN/nvl.advdb`。游戏实际样式由 Ren’Py 项目的 screen 决定。

## 行高、说明和版本

点击表格下方的 **＋ 新增台词**，或在最后一行按 Enter，都能加行。多选单元格或行号，输入 **选中行高** 并点击 **应用到选中行**；也可以拖动选中行的行号下边缘一起调整。Shift 选择连续行，Windows 的 Ctrl／Mac 的 Command 选择不连续行。**自动行高** 可恢复默认值。

**Help** 显示快捷键和版本；**关于** 包含 Akihium、GitHub 和 MIT 许可证。Mac 的关于位于屏幕左上角的应用程序菜单。Word／PDF／Excel 同样默认保存到项目文件夹，可以修改文件名和位置。
