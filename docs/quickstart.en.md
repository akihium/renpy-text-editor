# Quick start

1. Extract the **whole** package. On Windows, run `RenPy Text Editor.exe` inside its folder. On macOS, open `RenPy Text Editor.app`.
2. Choose an interface language. Open `examples/en/branches.advdb` for a demo, or create a new project and choose its save location.
3. Keep your `.advdb` file beside its matching `_assets` folder. Use Save as to copy a demo before editing it.
4. Enter a character ID, dialogue and notes. Tab moves between cells, Enter advances to the next dialogue, and Shift+Enter inserts a line break. Use Ctrl on Windows or Command on macOS for formatting/save/undo shortcuts.
5. Create branch sections, add choices pointing to them, and add background cues. Text only hides cues without deleting them.
6. Export Ren'Py into the game's `game` folder. Only `adv_generated` is generated. Call `adv_opening` from your handwritten `label start`.
7. Word/PDF export lets you set the title and include or hide dialogue IDs. The RPY ID switch is independent.

The app runs offline. It does not include Ren'Py SDK or a live game renderer. Test exported scripts with your Ren'Py SDK before distribution. Binaries are not signed with a commercial Windows/macOS developer certificate.
