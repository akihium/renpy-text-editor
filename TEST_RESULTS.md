# Validation

The application has an automated Qt and data test suite. The latest local macOS run passed **61 tests**. Tests exercise real Qt editors and key/button events, SQLite transactions, backups, asset copies, text formatting, character/section renaming, branch export, Word/PDF contents, four interface languages and four localized example sets.

The build scripts run the frozen application with `--verify-exports` before packaging. This creates SQLite, fonts, Excel, Ren’Py, Word and PDF outputs and verifies the four built-in translation catalogs. Binary release jobs are published only when both OS builds succeed.

For exact Windows/macOS results, see the repository's GitHub Actions run for the release commit. A prepared workflow is not a claim that a remote build has passed.

Ren’Py SDK lint, engine rendering, commercial code signing/notarization, Windows ARM64 and Intel Mac builds are outside the current verification scope.

Public screenshots are created from authored demos without opening a personal project. Bundled demos contain no operating-system fonts.
