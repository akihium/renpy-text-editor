import sys
import os
from PySide6.QtWidgets import QApplication, QDialog
from adv_editor.gui import Window
from adv_editor import __version__


def main():
    checking=len(sys.argv)==3 and sys.argv[1]=='--verify-exports'
    if checking:
        from pathlib import Path
        os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
        os.environ.setdefault('RENPY_EDITOR_SETTINGS_FILE',str(Path(sys.argv[2])/'settings.ini'))
    app = QApplication(sys.argv)
    app.setApplicationName('RenPy Text Editor')
    app.setApplicationVersion(__version__)
    if checking:
        from adv_editor.verify import verify_exports
        verify_exports(sys.argv[2])
        return 0
    from adv_editor.startup import StartupDialog
    path = sys.argv[1] if len(sys.argv)>1 else None
    while True:
        if not path:
            launcher = StartupDialog()
            if launcher.exec() != QDialog.DialogCode.Accepted:
                return 0
            path = launcher.project_path
        window = Window(path)
        if window.db:
            break
        window.dirty = False
        window.close()
        window.deleteLater()
        path = None
    window.show()
    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
