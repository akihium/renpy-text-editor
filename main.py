import sys
import os
from PySide6.QtWidgets import QApplication
from adv_editor.gui import Window


def main():
    checking=len(sys.argv)==3 and sys.argv[1]=='--verify-exports'
    if checking: os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
    app = QApplication(sys.argv)
    app.setApplicationName('RenPy Text Editor')
    if checking:
        from adv_editor.verify import verify_exports
        verify_exports(sys.argv[2])
        return 0
    window = Window(sys.argv[1] if len(sys.argv)>1 else None)
    window.show()
    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
