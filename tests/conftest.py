import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import gc
import tempfile
import pytest
from PySide6.QtCore import QCoreApplication,QEvent,QSettings
from PySide6.QtGui import QFontDatabase
from PySide6.QtWidgets import QApplication
QSettings.setDefaultFormat(QSettings.Format.IniFormat)
QSettings.setPath(QSettings.Format.IniFormat,QSettings.Scope.UserScope,tempfile.mkdtemp(prefix='renpy-editor-test-settings-'))
# A single application owns the Qt font/cache lifetime for every test module.
_APPLICATION=QApplication.instance() or QApplication([])


@pytest.fixture(scope='session',autouse=True)
def dispose_qt_objects():
    yield
    # Drain deleteLater while Qt is alive, including hidden accepted/rejected dialogs.
    for widget in _APPLICATION.topLevelWidgets(): widget.deleteLater()
    QCoreApplication.sendPostedEvents(None,QEvent.Type.DeferredDelete)
    gc.collect()
    QCoreApplication.sendPostedEvents(None,QEvent.Type.DeferredDelete)
    QFontDatabase.removeAllApplicationFonts()


@pytest.fixture(autouse=True)
def default_interface_settings():
    from adv_editor.i18n import set_language
    settings=QSettings('ADVScript','Editor')
    for key,value in {'language':'zh_TW','show_ids':False,'export_ids':True,'role_background':True}.items(): settings.setValue(key,value)
    set_language('zh_TW')
    yield
    QCoreApplication.sendPostedEvents(None,QEvent.Type.DeferredDelete)
