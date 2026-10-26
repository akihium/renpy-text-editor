# 快速开始 — Ren’Py Text Editor

这是带有桌面图形界面的 Ren’Py 台词编辑器，可以在表格中写作、直接查看文字格式，并导出剧本。

[English](quickstart.en.md) · [日本語](quickstart.ja.md) · [简体中文](quickstart.zh-CN.md) · [繁體中文](quickstart.zh-TW.md)

## 下载与启动

- [下载 Windows 10/11 x64 版](https://github.com/akihium/renpy-text-editor/releases/latest/download/RenPy-Text-Editor-Windows-x64.zip)
- [下载 macOS 14 及以上 Apple Silicon 版](https://github.com/akihium/renpy-text-editor/releases/latest/download/RenPy-Text-Editor-macOS-arm64.zip)
- [所有版本与更新说明](https://github.com/akihium/renpy-text-editor/releases/latest)

选择适合自己电脑的 ZIP；打包版不需要安装 Python。Windows 请**完整解压**，然后在解压后的文件夹中运行 `RenPy Text Editor.exe`，保留它旁边的文件和文件夹。macOS 解压后打开 `RenPy Text Editor.app`。

## 加载附带的示例工程

1. 启动软件，在主界面的 **界面语言** 选择 **简体中文**。
2. 点击 **开启项目**，找到刚才解压软件包的文件夹。
3. 打开 `examples/zh_CN/sample.advdb` 查看基本台词示例；打开 `examples/zh_CN/branches.advdb` 体验背景、点击后继续显示和选项分支。
4. 编辑前，先点击 **另存／变更位置**，选择自己的文件名和保存位置。软件会一起复制工程素材。
5. 选择章节／段落后查看表格。点击台词单元格，选中文字后试用格式按钮；切换视觉模式和原始标签模式，查看文字效果及 Ren’Py 标签。

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

点击 **新增项目**，选择文件名和保存位置。在表格中填写角色代号、台词和备注；通过主界面的角色管理设置显示名称和颜色。

- **Tab / Shift+Tab：** 下一列／上一列。
- **Enter：** 完成编辑，跳到下一行角色栏；最后一行会自动新增一行。
- **Shift+Enter：** 台词内换行。
- **Ctrl+S / Cmd+S：** 保存。格式与撤销等快捷键在 Windows 使用 Ctrl，macOS 使用 Command。

在章节／段落管理中创建分支，再新增选项并指定目标。主界面也能导入背景和字体。**只显示文本** 会暂时隐藏演出，不会删除数据。

手动移动工程时，请把 `story.advdb` 和对应的 `story_assets/` 一起移动。使用 **另存／变更位置** 会自动复制两者。

## 导出

将 Ren’Py 导出到游戏的 `game` 文件夹，生成文件会存放在 `adv_generated/`。手写脚本调用附带示例的方式：

```renpy
label start:
    call adv_opening
    return
```

使用自己的段落时，请把 `adv_opening` 换成导出文件里的对应 label。Word／PDF 支持自定义标题及是否包含台词 ID；RPY 的 ID 开关独立控制。

软件完全离线运行，不包含 Ren’Py SDK 或游戏内预览，发布前请在 Ren’Py 中测试导出结果。打包版未使用商业开发者证书签名，也未进行 macOS 公证。
