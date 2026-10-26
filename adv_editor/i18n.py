"""Offline interface translations. Project text and stable schema keys are never translated."""
import json
from pathlib import Path

APP_NAME='Ren’Py 文本編輯器'
LANGUAGES={'zh_TW':'繁體中文','zh_CN':'简体中文','en':'English','ja':'日本語'}
LANGUAGE='zh_TW'
CATALOGS={language:json.loads((Path(__file__).parent/'locales'/(language+'.json')).read_text(encoding='utf-8')) for language in ('en','zh_CN','ja')}
_QT_TRANSLATOR=None


def tr(text,**values):
    translated=CATALOGS.get(LANGUAGE,{}).get(text,text)
    return translated.format(**values) if values else translated


def set_language(language):
    global LANGUAGE,_QT_TRANSLATOR
    if language not in LANGUAGES: language='zh_TW'
    unchanged=LANGUAGE==language and _QT_TRANSLATOR is not None
    LANGUAGE=language
    from PySide6.QtCore import QCoreApplication,QLibraryInfo,QTranslator
    app=QCoreApplication.instance()
    if app is not None:
        if unchanged: return
        if _QT_TRANSLATOR is not None:
            app.removeTranslator(_QT_TRANSLATOR)
            _QT_TRANSLATOR.deleteLater()
        _QT_TRANSLATOR=QTranslator(app)
        if language!='en' and _QT_TRANSLATOR.load('qtbase_'+language,QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)):
            app.installTranslator(_QT_TRANSLATOR)
        app.setApplicationDisplayName(tr(APP_NAME))


def source_key(text):
    if text in CATALOGS['en']: return text
    for catalog in CATALOGS.values():
        for source,value in catalog.items():
            if text==value: return source
    return None


def retranslate(root):
    """Update presentation strings only, preserving edits, item data and project content."""
    from PySide6.QtCore import QObject,Qt
    from PySide6.QtGui import QAction
    from PySide6.QtWidgets import QLabel,QAbstractButton,QLineEdit,QComboBox,QTableWidget,QMenu
    for obj in [root]+root.findChildren(QObject):
        if obj.property('project_content'): continue
        for getter,setter in [('windowTitle','setWindowTitle'),('toolTip','setToolTip')]:
            if hasattr(obj,getter):
                prop='_i18n_'+getter
                key=obj.property(prop) or source_key(getattr(obj,getter)())
                if key: obj.setProperty(prop,key);getattr(obj,setter)(tr(key))
        if isinstance(obj,(QLabel,QAbstractButton,QAction)):
            key=obj.property('_i18n_text') or source_key(obj.text())
            if key: obj.setProperty('_i18n_text',key);obj.setText(tr(key))
        if isinstance(obj,QMenu):
            key=obj.property('_i18n_menu') or source_key(obj.title())
            if key: obj.setProperty('_i18n_menu',key);obj.setTitle(tr(key))
        if isinstance(obj,QLineEdit):
            key=obj.property('_i18n_placeholder') or source_key(obj.placeholderText())
            if key: obj.setProperty('_i18n_placeholder',key);obj.setPlaceholderText(tr(key))
        if isinstance(obj,QComboBox) and not obj.isEditable() and not obj.property('project_content'):
            obj.blockSignals(True)
            for index in range(obj.count()):
                role=int(Qt.ItemDataRole.UserRole)+17
                key=obj.itemData(index,role) or source_key(obj.itemText(index))
                if key: obj.setItemData(index,key,role);obj.setItemText(index,tr(key))
            obj.blockSignals(False)
        if isinstance(obj,QTableWidget):
            for col in range(obj.columnCount()):
                item=obj.horizontalHeaderItem(col)
                if item is None: continue
                role=int(Qt.ItemDataRole.UserRole)+17
                key=item.data(role) or source_key(item.text())
                if key: item.setData(role,key);item.setText(tr(key))
