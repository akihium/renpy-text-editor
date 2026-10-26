# 快速開始 — Ren’Py Text Editor

這是具備桌面圖形介面的 Ren’Py 台詞編輯器，可以在表格中寫作、直接查看文字格式，並匯出劇本。

[English](quickstart.en.md) · [日本語](quickstart.ja.md) · [简体中文](quickstart.zh-CN.md) · [繁體中文](quickstart.zh-TW.md)

## 下載與啟動

- [下載 Windows 10/11 x64 版](https://github.com/akihium/renpy-text-editor/releases/latest/download/RenPy-Text-Editor-Windows-x64.zip)
- [下載 macOS 14 以上 Apple Silicon 版](https://github.com/akihium/renpy-text-editor/releases/latest/download/RenPy-Text-Editor-macOS-arm64.zip)
- [所有版本與更新說明](https://github.com/akihium/renpy-text-editor/releases/latest)

選擇適合自己電腦的 ZIP；打包版不需要安裝 Python。Windows 請**完整解壓縮**，再於解壓縮後的資料夾中執行 `RenPy Text Editor.exe`，保留旁邊的檔案與資料夾。macOS 解壓縮後開啟 `RenPy Text Editor.app`。

## 載入附帶的範例工程

1. 啟動軟體，在主介面的 **介面語言** 選擇 **繁體中文**。
2. 點擊 **開啟專案**，找到剛才解壓縮軟體套件的資料夾。
3. 開啟 `examples/zh_TW/sample.advdb` 查看基本台詞範例；開啟 `examples/zh_TW/branches.advdb` 體驗背景、點擊後繼續顯示與選項分支。
4. 編輯前，先點擊 **另存／變更位置**，選擇自己的檔名與儲存位置。軟體會一起複製工程素材。
5. 選擇章節／段落後查看表格。點擊台詞儲存格，選取文字後試用格式按鈕；切換視覺模式與原始標籤模式，查看文字效果及 Ren’Py 標籤。

套件內包含四種語言的範例：

| 語言 | 解壓縮後的範例資料夾 |
| --- | --- |
| 繁體中文 | `examples/zh_TW/` |
| 簡體中文 | `examples/zh_CN/` |
| 日文 | `examples/ja/` |
| 英文 | `examples/en/` |

如果下載的是**原始碼 ZIP**，範例位於 `examples/localized/<語言>/`；請先依照 [原始碼啟動說明](https://github.com/akihium/renpy-text-editor#run-from-source) 安裝 Python 與相依套件。

**開啟專案** 應選擇 `.advdb` 檔案。`.xlsx` 用於 Excel 匯入匯出；`renpy_game/adv_generated/` 是已匯出的 Ren’Py 腳本範例。切換介面語言只會改變操作介面，不會翻譯工程裡的台詞；想看另一種語言的台詞，請開啟對應語言的範例。

## 建立與編輯自己的工程

點擊 **新增專案**，選擇檔名與儲存位置。在表格中填寫角色代號、台詞與備註；透過主介面的角色管理設定顯示名稱及顏色。

- **Tab / Shift+Tab：** 下一欄／上一欄。
- **Enter：** 完成編輯，跳到下一行角色欄；最後一行會自動新增一行。
- **Shift+Enter：** 台詞內換行。
- **Ctrl+S / Cmd+S：** 儲存。格式與復原等快捷鍵在 Windows 使用 Ctrl，macOS 使用 Command。

在章節／段落管理中建立分支，再新增選項並指定目標。主介面也能匯入背景與字體。**只顯示文本** 會暫時隱藏演出，不會刪除資料。

手動搬移工程時，請把 `story.advdb` 與對應的 `story_assets/` 一起搬移。使用 **另存／變更位置** 會自動複製兩者。

## 匯出

將 Ren’Py 匯出到遊戲的 `game` 資料夾，生成檔案會放在 `adv_generated/`。手寫腳本呼叫附帶範例的方式：

```renpy
label start:
    call adv_opening
    return
```

使用自己的段落時，請把 `adv_opening` 換成匯出檔案裡的對應 label。Word／PDF 支援自訂標題及是否包含台詞 ID；RPY 的 ID 開關獨立控制。

軟體完全離線運行，不包含 Ren’Py SDK 或遊戲內預覽，發布前請在 Ren’Py 中測試匯出結果。打包版未使用商業開發者憑證簽章，也未進行 macOS 公證。
