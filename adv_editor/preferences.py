"""Local preferences, with an optional separate store for verification runs."""
import os
from PySide6.QtCore import QSettings


def settings():
    filename = os.environ.get('RENPY_EDITOR_SETTINGS_FILE')
    if filename:
        return QSettings(filename, QSettings.Format.IniFormat)
    return QSettings('ADVScript', 'Editor')
