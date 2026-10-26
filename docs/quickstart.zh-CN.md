# 快速开始

1. 完整解压软件包。Windows 在文件夹中运行 `RenPy Text Editor.exe`；macOS 打开 `RenPy Text Editor.app`。
2. 选择界面语言。打开 `examples/zh_CN/branches.advdb` 体验示例，或新建项目并选择保存位置。
3. 移动项目时，请保留 `.advdb` 与同名 `_assets` 文件夹。修改示例前可以先另存。
4. 填写角色代号、台词和备注。Tab 切换列，Enter 下一句，Shift+Enter 换行。Windows 使用 Ctrl，macOS 使用 Command 配合格式、保存和撤销快捷键。
5. 在章节／段落管理建立分支，再新增选项并指定目标。支持导入背景和字体；「只显示文本」暂时隐藏演出，不会删除数据。
6. 将 Ren’Py 导出到游戏的 `game` 文件夹，仅更新 `adv_generated`。手写的 `label start` 中使用 `call adv_opening`。
7. Word／PDF 支持自定义标题以及是否包含台词 ID，RPY 的 ID 开关独立控制。

程序完全离线，不包含 Ren’Py SDK 或游戏内预览。导出后请使用自己的 SDK 验收。执行文件未使用商业 Windows／macOS 开发者证书签名。
