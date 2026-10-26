# Quick start — Ren’Py Text Editor

A desktop GUI for writing Ren’Py dialogue in a table, with visual text formatting and script export.

[English](quickstart.en.md) · [日本語](quickstart.ja.md) · [简体中文](quickstart.zh-CN.md) · [繁體中文](quickstart.zh-TW.md)

## Download and launch

- [Download for Windows 10/11 x64](https://github.com/akihium/renpy-text-editor/releases/latest/download/RenPy-Text-Editor-Windows-x64.zip)
- [Download for macOS 14+ Apple Silicon](https://github.com/akihium/renpy-text-editor/releases/latest/download/RenPy-Text-Editor-macOS-arm64.zip)
- [All releases and release notes](https://github.com/akihium/renpy-text-editor/releases/latest)

Download the ZIP for your computer; Python is not required for these packaged builds. On Windows, extract the **whole** ZIP and open `RenPy Text Editor.exe` inside the extracted folder. Keep the accompanying files and folders beside it. On macOS, extract the ZIP and open `RenPy Text Editor.app`.

## Open a bundled example

1. Start the app and select **English** from **Interface language** in the main window.
2. Click **Open project**, then browse to the folder you extracted from the ZIP.
3. Open `examples/en/sample.advdb` for a small dialogue example, or `examples/en/branches.advdb` for backgrounds, click-to-continue and branching choices.
4. Click **Save as / Move** and choose your own filename and save location before editing. The app also copies the project's assets.
5. Select a chapter/section to see its rows. Click a dialogue cell, select some text, and try the formatting buttons. Switch between visual and source-tag modes to see the rendered text or its Ren’Py tags.

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

Click **New project**, then choose a filename and save location. Enter character IDs, dialogue and notes in the table. Use the main-window character manager to define display names and colors.

- **Tab / Shift+Tab:** next / previous cell.
- **Enter:** finish editing and advance to the next dialogue's character cell; a new row is added at the end.
- **Shift+Enter:** insert a line break within dialogue.
- **Ctrl+S / Cmd+S:** save. Use Ctrl on Windows and Command on macOS for formatting and undo shortcuts.

Create branch sections in chapter/section management, then add choices pointing to them. Add backgrounds and fonts using the main-window controls. **Text only** hides stage cues without deleting them.

When moving a project manually, keep `story.advdb` together with its matching `story_assets/` folder. **Save as / Move** copies both for you.

## Export

Export Ren’Py into your game's `game` folder. Generated files go under `adv_generated/`. To start the bundled example from a handwritten script, use:

```renpy
label start:
    call adv_opening
    return
```

For your own sections, replace `adv_opening` with the generated label shown in the exported script. Word/PDF export lets you set a document title and include or hide dialogue IDs. The RPY ID switch is independent.

The editor runs offline. It does not include the Ren’Py SDK or a live game renderer; test exported scripts in Ren’Py before release. The packaged builds do not use commercial developer signing certificates or macOS notarization.
