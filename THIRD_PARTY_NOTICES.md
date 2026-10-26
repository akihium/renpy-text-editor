# Third-party notices

The application's original source is licensed under MIT. Bundled dependencies retain their own licenses; MIT does not replace those licenses.

- **Qt / PySide6 / Shiboken6**: LGPL-3.0 / GPL / commercial alternatives, as applicable to each module. This application uses the unmodified shared libraries. Sources and license information: [Qt for Python](https://code.qt.io/pyside/pyside-setup.git/), [Qt](https://code.qt.io/qt/qtbase.git/), [licenses](https://doc.qt.io/qtforpython-6/licenses.html). Match the version in `LICENSES/DEPENDENCIES.json`; source archives are available from [Qt downloads](https://download.qt.io/official_releases/QtForPython/).
- **Python**: Python Software Foundation license. [Source](https://www.python.org/downloads/source/).
- **openpyxl / et_xmlfile / python-docx**: MIT licenses.
- **ReportLab**: BSD license. Included font resources have separate notices copied into `LICENSES`.
- **lxml**: BSD and licenses for included libxml2/libxslt code.
- **Pillow**: HPND and associated third-party notices.
- **PyInstaller**: GPL with its bootloader exception, allowing application distribution under the application's chosen license.

The release `LICENSES` folder contains collected license texts and exact installed dependency versions. Build-time packages may also appear in the manifest even if they are not included in the executable.

Libraries remain dynamically linked. The Windows portable folder keeps runtime DLLs alongside the EXE; do not move the EXE out by itself. Rebuild from the public source or replace the appropriate compatible shared libraries. On macOS, modified bundles need to be signed again, for example with an ad-hoc signature, before local use.

The demo projects and solid-color background were created for this application and are included under MIT. No macOS or Windows font files are redistributed. Imported fonts and images in your own projects retain their original licenses.

Ren'Py is a separate project. This editor is not affiliated with or endorsed by the Ren'Py project. Ren'Py SDK, game engine and third-party game assets are not bundled.
