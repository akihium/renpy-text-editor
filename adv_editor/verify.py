"""Packaged-app export check, callable with --verify-exports OUTPUT_DIRECTORY."""
import json
from pathlib import Path
from .core import sample,new_row,Database,export_rpy,export_excel,import_excel,statement
from .assets import import_font
from .platform_fonts import importable_system_font
from .documents import export_word,export_pdf


def verify_exports(folder):
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    project=folder/'check.advdb'
    data=sample()
    data['sections'][0]['rows'][0]['text']='前半{w}{b}後半{/b}'
    data['sections'][0]['rows'].append(dict(new_row(),kind='menu',text='選擇',choices=[dict(text='繼續',target='greeting')]))
    font=importable_system_font()
    if font is not None:
        filename,family=import_font(font,project)
        data['fonts'][filename]=family
    db=Database(project);db.save(data);assert db.load()==data;db.close()
    export_excel(data,folder/'check.xlsx',project)
    assert import_excel(folder/'check.xlsx')==data
    export_rpy(data,folder/'game',project)
    export_word(data,folder/'check.docx',title='Packaged export check',include_ids=False)
    export_pdf(data,folder/'check.pdf',project,title='Packaged export check',include_ids=False)
    assert ' id ' not in statement(data['sections'][0]['rows'][0],include_ids=False)
    from . import i18n
    original_language=i18n.LANGUAGE
    for code,expected in [('en','Show dialogue IDs'),('zh_CN','显示台词 ID'),('zh_TW','顯示台詞 ID'),('ja','セリフ ID を表示')]:
        i18n.set_language(code)
        assert i18n.tr('顯示台詞 ID')==expected
    i18n.set_language(original_language)
    assert (folder/'check.docx').read_bytes()[:2]==b'PK'
    assert (folder/'check.pdf').read_bytes().startswith(b'%PDF')
    verify_workspace(folder,project)
    (folder/'result.json').write_text(json.dumps({'ok':True,'checks':['SQLite','fonts','Excel','RenPy menu','Word','PDF','Custom title','Optional IDs','EN / zh_CN / zh_TW / JA','Startup','Bundled editable samples','Keyboard navigation','Visual formatting','Batch row heights','Direct/custom RenPy folders','Configurable label prefix','About and bundled MIT license','Language discovery labels','NVL modes, page clears and choices']},ensure_ascii=False,indent=2),encoding='utf-8')



def verify_workspace(folder,project):
    from PySide6.QtCore import Qt,QTimer
    from PySide6.QtGui import QKeyEvent
    from PySide6.QtWidgets import QApplication,QTableWidgetSelectionRange,QLabel,QTextBrowser
    from .gui import Window
    from .startup import StartupDialog
    from .projects import copy_example
    for language in ('zh_TW','zh_CN','ja','en'):
        for kind in ('sample','branches','nvl'):
            path=copy_example(language,kind,folder/'samples')
            db=Database(path)
            assert db.load()['sections']
            db.close()
    launcher=StartupDialog()
    launcher.show();QApplication.processEvents()
    launcher.grab().save(str(folder/'startup.png'))
    launcher.close()
    nvl_path=copy_example('en','nvl',folder/'samples')
    nvl_db=Database(nvl_path);nvl_data=nvl_db.load();nvl_db.close()
    assert nvl_data['narrator_mode']=='nvl' and nvl_data['character_modes']
    nvl_export=export_rpy(nvl_data,folder/'nvl-game')
    assert 'kind=nvl' in (nvl_export/'characters.rpy').read_text()
    assert 'menu (nvl=True):' in (nvl_export/'dialogue.rpy').read_text()
    window=Window(project)
    from .sections import SectionDialog
    draft=SectionDialog(window.data,window.data['sections'][0]['id'])
    draft.label_prefix.setText('story_');draft.accept()
    window.snapshot();window.data=draft.data;window.refresh()
    assert '[story_opening]' in window.sections.currentText()
    window.show();QApplication.processEvents()
    window.table.setCurrentCell(0,2)
    window.table.editItem(window.table.item(0,2))
    QApplication.processEvents()
    editor=window.editor
    editor.set_source('Packaged formatting')
    editor.selectAll()
    QApplication.sendEvent(editor,QKeyEvent(QKeyEvent.Type.KeyPress,Qt.Key.Key_B,Qt.KeyboardModifier.ControlModifier))
    assert editor.source()=='{b}Packaged formatting{/b}'
    QApplication.sendEvent(editor,QKeyEvent(QKeyEvent.Type.KeyPress,Qt.Key.Key_Tab,Qt.KeyboardModifier.NoModifier))
    assert window.table.currentColumn()==3
    QApplication.sendEvent(window.editor,QKeyEvent(QKeyEvent.Type.KeyPress,Qt.Key.Key_Return,Qt.KeyboardModifier.NoModifier))
    assert (window.table.currentRow(),window.table.currentColumn())==(1,1)
    window.commit()
    window.table.setRangeSelected(QTableWidgetSelectionRange(0,0,1,3),True)
    window.table.verticalHeader().resizeSection(0,153)
    assert window.table.rowHeight(1)==153
    window.refresh()
    assert window.table.rowHeight(0)==153
    count=len(window.rows)
    window.add_row_button.click()
    assert len(window.rows)==count+1 and window.editor.col==1
    window.commit()
    assert window.save() and window.db.load()==window.data
    export_rpy(window.data,folder/'custom-game',project,subfolder='My script')
    import copy
    direct=copy.deepcopy(window.data);direct['label_prefix']=''
    export_rpy(direct,folder/'direct-game',project,subfolder='')
    export_excel(window.data,folder/'prefix.xlsx',project)
    assert import_excel(folder/'prefix.xlsx')==window.data
    assert (folder/'custom-game'/'My script'/'dialogue.rpy').is_file()
    assert (folder/'direct-game'/'dialogue.rpy').is_file()
    assert 'label story_opening:' in (folder/'custom-game'/'My script'/'dialogue.rpy').read_text()
    assert 'jump story_greeting' in (folder/'custom-game'/'My script'/'dialogue.rpy').read_text()
    assert 'label opening:' in (folder/'direct-game'/'dialogue.rpy').read_text()
    from . import __version__
    assert 'Language /' in [label.text() for label in window.findChildren(QLabel)]
    assert 'Language /' in [label.text() for label in launcher.findChildren(QLabel)]
    from .about import AboutDialog,REPOSITORY_URL,AUTHOR
    about=AboutDialog(window)
    about.show();QApplication.processEvents()
    details=' '.join(label.text() for label in about.findChildren(QLabel))
    assert __version__ in details and AUTHOR in details and REPOSITORY_URL in details
    license_text=about.findChild(QTextBrowser).toPlainText()
    assert 'MIT License' in license_text
    assert 'Copyright (c) 2026 '+AUTHOR in license_text
    about.grab().save(str(folder/'about.png'))
    about.reject()
    help_checked=[]
    def check_help():
        dialog=QApplication.activeModalWidget()
        help_checked.append(any(__version__ in label.text() for label in dialog.findChildren(QLabel)))
        dialog.reject()
    QTimer.singleShot(0,check_help)
    window.show_help()
    assert help_checked==[True]
    window.grab().save(str(folder/'editor.png'))
    window.dirty=False;window.close()
    QApplication.processEvents()
