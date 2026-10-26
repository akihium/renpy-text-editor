# 快速開始

1. 完整解壓縮套件。Windows 在資料夾中執行 `RenPy Text Editor.exe`；macOS 開啟 `RenPy Text Editor.app`。
2. 選擇介面語言。可開啟 `examples/zh_TW/branches.advdb` 試用，或按新增專案選擇保存位置。
3. 搬移專案時，請一起保留 `.advdb` 與同名 `_assets` 資料夾。修改範例前可先另存。
4. 填角色代號、台詞與備註。Tab 切換欄位，Enter 下一句，Shift+Enter 換行。Windows 使用 Ctrl，macOS 使用 Command 搭配格式、儲存及復原快捷鍵。
5. 在章節／段落管理建立分支，再新增選項指定目標。可匯入背景及字體；「只顯示文本」暫時隱藏演出，不會刪除資料。
6. 匯出 Ren’Py 到遊戲的 `game` 資料夾，僅更新 `adv_generated`。手寫的 `label start` 以 `call adv_opening` 呼叫。
7. Word／PDF 可自訂標題及是否包含台詞 ID；RPY 的 ID 開關獨立控制。

程式完全離線，不包含 Ren’Py SDK 或遊戲內預覽。匯出後請用自己的 SDK 驗收。執行檔未使用商業 Windows／macOS 開發者憑證簽章。
