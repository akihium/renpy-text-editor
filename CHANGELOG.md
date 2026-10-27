# Changelog

## Ren’Py Text Editor 0.2.0

An offline desktop GUI for writing Ren’Py dialogue. This release adds NVL authoring and makes the first-run and everyday editing workflow easier.

### What changed since 0.1.1

- **Project launcher:** choose English, Japanese, Simplified Chinese or Traditional Chinese; open recent projects, create a project folder, or explore an editable Sample copy.
- **NVL support:** set individual characters and narration to ADV or NVL, insert `nvl clear`, and create NVL choices with optional page clearing after selection. Mixed ADV/NVL characters are supported. A localized NVL example is included for every language.
- **Main-window controls:** export `.rpy`, add dialogue with a visible button, read keyboard tips, and open the complete Help guide.
- **Row heights:** resize several selected rows together by entering a height or dragging a selected row boundary. Heights stay with permanent dialogue IDs across sorting, refreshes and reopening the project.
- **Export location:** exports start in the project folder. Ren’Py output can use a custom subfolder name or go directly into the chosen folder; image and font paths follow the selected layout. Existing handwritten `.rpy` files are preserved.
- **Label prefix:** change the default `adv_` prefix or leave it blank. Generated labels, calls, jumps, choices and preview stay in sync. External handwritten references need to be updated separately.
- **Language discovery and About:** the English word “Language” remains visible beside language selectors. About and Help show the version; About includes Akihium, GitHub and the bundled MIT license.
- New controls and Help are translated into all four interface languages. Windows Help uses Ctrl; macOS Help uses Command.

### Downloads and examples

- **Windows 10/11 x64:** extract the entire `RenPy-Text-Editor-Windows-x64.zip`, then run `RenPy Text Editor.exe` inside it.
- **macOS 14+ Apple Silicon:** extract `RenPy-Text-Editor-macOS-arm64.zip`, then open `RenPy Text Editor.app`.
- **Source:** `RenPy-Text-Editor-source-v0.2.0.zip`, or clone the repository.
- Both platform packages contain all four UI languages, three examples per language (dialogue, branching/staging and NVL), quick-start guides and license notices. Choose a language and a Sample from the launcher to create a fresh editable local copy.
- `SHA256SUMS.txt` lets you check download integrity.

### Validation and scope

The release workflow tests and builds on both Windows and macOS and runs export/UI checks on each frozen executable before publishing. The NVL example was also checked with Ren’Py 8.5.3 Lint and an engine test covering the NVL screen, choices, page clearing and the branch destination.

The editor uses `.advdb` projects and exports Ren’Py scripts; it does not import arbitrary existing `.rpy` files or provide a live game renderer. Game presentation still follows your Ren’Py screens. Test custom tags and handwritten integration in your game. Packages have no paid developer signing certificate or macOS notarization. Ren’Py is a separate project and does not endorse this editor.

**Author:** Akihium · **License:** MIT (dependencies retain their own licenses).

Please try the app and report problems, reproduction steps and your OS/version in [GitHub Issues](https://github.com/akihium/renpy-text-editor/issues). Feedback from writers is welcome.

---

**繁體中文：** 新增啟動視窗、最近專案、語言對應的示例副本、NVL 角色／旁白／清頁與選項、多選行高、自訂匯出資料夾、可修改的 label 前綴、Help 與關於。兩個平台套件均包含四語介面、操作說明與三類示例。歡迎試用並到 GitHub Issues 回報。

**简体中文：** 新增启动界面、最近项目、对应语言的示例副本、NVL 角色／旁白／清页与选项、多选行高、自定义导出文件夹、可修改的 label 前缀、Help 和关于。两个平台的包都包含四语界面、操作说明和三类示例。欢迎试用并到 GitHub Issues 反馈。

**日本語：** 起動画面、最近のプロジェクト、言語別の編集可能なサンプル、NVL キャラクター・ナレーション・ページクリア・選択肢、複数行の高さ調整、書き出し先とラベル接頭辞の設定、ヘルプとアプリ情報を追加しました。両 OS のパッケージに4言語の画面・説明と3種類のサンプルを同梱しています。感想や不具合は GitHub Issues にお寄せください。


## 0.1.1

Initial public Windows/macOS release with four interface languages, visual formatting, branching, project backups and Ren’Py/Excel/Word/PDF exports. Fixed archive names to match SHA-256 checksums.
