# Contributing

Use Python 3.12, install `requirements.txt`, and run the Qt tests with `QT_QPA_PLATFORM=offscreen` (PowerShell: `$env:QT_QPA_PLATFORM='offscreen'`).

Keep project IDs and asset paths stable. Do not translate user-authored dialogue when changing the interface language. For new interface strings, add matching keys to `adv_editor/locales/en.json`, `zh_CN.json` and `ja.json`; Traditional Chinese is the source text.

Regenerate curated demos with `python scripts/create_examples.py examples/localized`. Do not commit personal projects, backup folders, imported proprietary fonts, virtual environments or built applications. Attach built applications to Releases instead.

Add regression coverage for data changes and meaningful GUI behavior. Build and verify on Windows and macOS before publishing a release. The MIT license covers original contributions; dependencies retain their own terms.
