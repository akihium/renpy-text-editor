# Quick start — Ren’Py Text Editor

A desktop GUI for writing Ren’Py dialogue in a table, with visual text formatting and script export.

[English](quickstart.en.md) · [日本語](quickstart.ja.md) · [简体中文](quickstart.zh-CN.md) · [繁體中文](quickstart.zh-TW.md)

## Download and launch

- [Download for Windows 10/11 x64](https://github.com/akihium/renpy-text-editor/releases/latest/download/RenPy-Text-Editor-Windows-x64.zip)
- [Download for macOS 14+ Apple Silicon](https://github.com/akihium/renpy-text-editor/releases/latest/download/RenPy-Text-Editor-macOS-arm64.zip)
- [All releases and release notes](https://github.com/akihium/renpy-text-editor/releases/latest)

Download the ZIP for your computer; Python is not required for these packaged builds. On Windows, extract the **whole** ZIP and open `RenPy Text Editor.exe` inside the extracted folder. Keep the accompanying files and folders beside it. On macOS, extract the ZIP and open `RenPy Text Editor.app`.

## Open a bundled example

1. Start the app. In the launcher, choose **English** beside **Language**.
2. Under **Sample · Examples**, open the dialogue, branching/staging or NVL sample. A fresh local working copy is created; you can edit it freely.
3. Reopen your edited copy from **Recent projects**. Opening a Sample again creates another clean copy, keeping your previous edits.
4. To choose your own location, use **Save as / Move** in the editor. Project assets are copied too.
5. Select a chapter/section, edit a cell and try the format buttons. Use visual mode for effects and source-tag mode for raw tags.

All four example languages are included:

| Language | Example folder in the extracted package |
| --- | --- |
| English | `examples/en/` |
| Japanese | `examples/ja/` |
| Simplified Chinese | `examples/zh_CN/` |
| Traditional Chinese | `examples/zh_TW/` |

If you downloaded the **source-code ZIP**, examples are under `examples/localized/<language>/` instead, and you must install Python and dependencies using the [source setup instructions](https://github.com/akihium/renpy-text-editor#run-from-source).

Open `.advdb` files with **Open project**. The `.xlsx` files are for Excel import/export; `renpy_game/adv_generated/` contains sample exported scripts. Changing the interface language changes the controls, not the dialogue stored in a project; open another language's example to try its dialogue.

## Create and edit your own project

Click **New project**, then choose a project folder (or create one in the folder picker). A database named after that folder and its asset folder are created inside it. Enter character IDs, dialogue and notes in the table. Use the main-window character manager to define display names and colors.

- **Tab / Shift+Tab:** next / previous cell.
- **Enter:** finish editing and advance to the next dialogue's character cell; a new row is added at the end.
- **Shift+Enter:** insert a line break within dialogue.
- **Ctrl+S / Cmd+S:** save. Use Ctrl on Windows and Command on macOS for formatting and undo shortcuts.

Create branch sections in chapter/section management, then add choices pointing to them. Add backgrounds and fonts using the main-window controls. **Text only** hides stage cues without deleting them.

When moving a project manually, keep `story.advdb` together with its matching `story_assets/` folder. **Save as / Move** copies both for you.

## Export

Click **Export .rpy** in the main window. The project folder is the default location; choose your game's `game` folder or a folder inside it. Name a subfolder or save directly in the selected folder. Fonts and images follow the output path, and existing handwritten `.rpy` files are preserved. The label prefix is configurable in chapter/section management: use `adv_`, your own prefix, or an empty prefix. With the default prefix, a handwritten entry point can use:

```renpy
label start:
    call adv_opening
    return
```

For your own sections, replace `adv_opening` with the generated label shown in the exported script. Word/PDF export lets you set a document title and include or hide dialogue IDs. The RPY ID switch is independent.

The editor runs offline. It does not include the Ren’Py SDK or a live game renderer; test exported scripts in Ren’Py before release. The packaged builds do not use commercial developer signing certificates or macOS notarization.

## NVL authoring

In character management, choose ADV or NVL separately for each character and for narration. Insert **Clear NVL page** where a page should end. In choice settings, enable **Show choices in NVL mode** and optionally clear the page after selection. Try `examples/en/nvl.advdb` or the launcher's NVL Sample. Your game's Ren’Py screens control the final appearance.

## Rows, help and version

Use **＋ Add dialogue** below the table, or press Enter at the last row. To resize several rows, select their cells or row numbers, enter a **Row height**, and click **Apply to selected rows**. You can also drag the bottom edge of a selected row number. Shift selects a range; Ctrl on Windows or Command on macOS selects separate rows. **Auto height** resets sizing.

**Help** lists shortcuts and shows the current version. **About** includes Akihium, GitHub and the MIT license. On macOS, About appears in the application's menu at the top-left of the screen. Word/PDF/Excel exports also default to the project folder; filenames and locations can be changed.
