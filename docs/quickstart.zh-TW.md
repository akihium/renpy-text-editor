# 快速開始 — Ren’Py Text Editor

這是具備桌面圖形介面的 Ren’Py 台詞編輯器，可以在表格中寫作、直接查看文字格式，並匯出劇本。

[English](quickstart.en.md) · [日本語](quickstart.ja.md) · [简体中文](quickstart.zh-CN.md) · [繁體中文](quickstart.zh-TW.md)

## 下載與啟動

- [下載 Windows 10/11 x64 版](https://github.com/akihium/renpy-text-editor/releases/latest/download/RenPy-Text-Editor-Windows-x64.zip)
- [下載 macOS 14 以上 Apple Silicon 版](https://github.com/akihium/renpy-text-editor/releases/latest/download/RenPy-Text-Editor-macOS-arm64.zip)
- [所有版本與更新說明](https://github.com/akihium/renpy-text-editor/releases/latest)

選擇適合自己電腦的 ZIP；打包版不需要安裝 Python。Windows 請**完整解壓縮**，再於解壓縮後的資料夾中執行 `RenPy Text Editor.exe`，保留旁邊的檔案與資料夾。macOS 解壓縮後開啟 `RenPy Text Editor.app`。

## 載入附帶的範例工程

1. 啟動軟體，在啟動視窗的 **Language / 介面語言** 選擇 **繁體中文**。
2. 在 **Sample · 示例** 選擇台詞、分支／演出或 NVL 示例。程式會建立全新本機副本，可以自由修改。
3. 修改後從 **最近開啟的專案** 繼續編輯。再次按 Sample 會建立另一份乾淨副本，不會清除先前修改。
4. 想自行指定位置時，在編輯器按 **另存／變更位置**，程式會一併複製素材。
5. 選擇章節／段落，編輯儲存格並試用格式按鈕。視覺模式顯示效果，原始標籤模式顯示完整標籤。

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

點擊 **新增專案**，選擇專案資料夾，或在選擇視窗中建立新資料夾。程式會在裡面建立同名資料庫與素材資料夾。在表格中填寫角色代號、台詞與備註；透過主介面的角色管理設定顯示名稱及顏色。

- **Tab / Shift+Tab：** 下一欄／上一欄。
- **Enter：** 完成編輯，跳到下一行角色欄；最後一行會自動新增一行。
- **Shift+Enter：** 台詞內換行。
- **Ctrl+S / Cmd+S：** 儲存。格式與復原等快捷鍵在 Windows 使用 Ctrl，macOS 使用 Command。

在章節／段落管理中建立分支，再新增選項並指定目標。主介面也能匯入背景與字體。**只顯示文本** 會暫時隱藏演出，不會刪除資料。

手動搬移工程時，請把 `story.advdb` 與對應的 `story_assets/` 一起搬移。使用 **另存／變更位置** 會自動複製兩者。

## 匯出

主介面的 **匯出 .rpy** 預設在專案資料夾。用於 Ren’Py 時，請選擇遊戲的 `game` 資料夾或其中的資料夾；可自訂子資料夾名稱，或直接儲存在所選資料夾。字體與圖片路徑會同步調整，既有手寫 `.rpy` 檔案會保留。章節／段落管理可把預設 label 前綴 `adv_` 改成自己的前綴，或留空。使用預設前綴時，手寫入口範例：

```renpy
label start:
    call adv_opening
    return
```

使用自己的段落時，請把 `adv_opening` 換成匯出檔案裡的對應 label。Word／PDF 支援自訂標題及是否包含台詞 ID；RPY 的 ID 開關獨立控制。

軟體完全離線運行，不包含 Ren’Py SDK 或遊戲內預覽，發布前請在 Ren’Py 中測試匯出結果。打包版未使用商業開發者憑證簽章，也未進行 macOS 公證。

## NVL 寫作

角色管理中可分別為角色與旁白設定 ADV 或 NVL。適當位置按 **NVL 清頁** 分頁；選項設定可勾選 **以 NVL 模式顯示選項**，並決定選擇後是否清頁。啟動視窗可開啟 NVL 示例，也可直接開啟 `examples/zh_TW/nvl.advdb`。實際遊戲樣式由 Ren’Py 專案的 screen 決定。

## 行高、說明與版本

表格下方的 **＋ 新增台詞** 或最後一行的 Enter 都能加行。多選儲存格或行號，輸入 **選取行高** 並按 **套用至選取行**；也可拖曳已選行的行號下緣一起調整。Shift 選取連續行，Windows 的 Ctrl／Mac 的 Command 選取不連續行。**自動行高** 可還原。

**Help** 顯示快捷鍵及版本；**關於** 包含 Akihium、GitHub 與 MIT 許可證。Mac 的關於位於畫面左上方應用程式選單。Word／PDF／Excel 同樣預設儲存到專案資料夾，可自行改檔名及位置。
