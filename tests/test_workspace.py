from adv_editor.preferences import settings
"""Launcher, project-folder exports and row-size interaction checks."""
import copy
import sys
from pathlib import Path
import pytest
from PySide6.QtCore import Qt, QSettings, QStandardPaths, QTimer
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QFileDialog, QDialog, QTableWidgetSelectionRange, QPushButton
from adv_editor.core import Database, sample
from adv_editor.gui import Window
from adv_editor.startup import StartupDialog
from adv_editor import i18n, projects


@pytest.fixture
def window(tmp_path):
    path = tmp_path/'project.advdb'
    db = Database(path); db.save(sample()); db.close()
    w = Window(path); w.show(); QApplication.processEvents()
    yield w
    w.commit(); w.dirty = False; w.close(); QApplication.processEvents()


def test_project_creation_preserves_existing_folder_contents(tmp_path):
    folder = tmp_path/'My novel'; folder.mkdir()
    marker = folder/'notes.txt'; marker.write_text('keep')
    path = projects.create_project(folder)
    assert path == folder/'My novel.advdb'
    assert path.is_file() and (folder/'My novel_assets').is_dir()
    db = Database(path); data = db.load(); db.close()
    assert len(data['sections']) == 1 and data['sections'][0]['rows'][0]['text'] == ''
    with pytest.raises(FileExistsError):
        projects.create_project(folder)
    assert marker.read_text() == 'keep'


def test_recent_order_filters_missing_files(tmp_path):
    paths = [tmp_path/(str(i)+'.advdb') for i in range(3)]
    for path in paths:
        db = Database(path); db.save(sample()); db.close()
        projects.remember_project(path)
    projects.remember_project(paths[0])
    paths[1].unlink()
    assert projects.recent_projects()[:2] == [str(paths[0]), str(paths[2])]
    assert str(paths[1]) not in projects.recent_projects()
    assert projects.default_directory() == str(tmp_path)


def test_startup_language_recent_and_folder_choice(tmp_path, monkeypatch):
    settings().setValue('recent_projects','[]')
    dialog = StartupDialog()
    assert dialog.recent.count() == 0
    dialog.language.setCurrentIndex(dialog.language.findData('ja'))
    assert i18n.LANGUAGE == 'ja'
    assert settings().value('language') == 'ja'
    folder = tmp_path/'New'; folder.mkdir()
    monkeypatch.setattr(QFileDialog, 'getExistingDirectory', lambda *a: '')
    dialog.new_button.click()
    assert dialog.project_path is None
    monkeypatch.setattr(QFileDialog, 'getExistingDirectory', lambda *a: str(folder))
    dialog.new_button.click()
    assert dialog.result() == QDialog.DialogCode.Accepted
    assert Path(dialog.project_path).parent == folder
    dialog.deleteLater()
    recent = StartupDialog()
    assert recent.recent.item(0).data(Qt.ItemDataRole.UserRole) == str(folder/'New.advdb')
    recent.recent_button.click()
    assert recent.project_path == str(folder/'New.advdb')
    recent.deleteLater()


def test_four_samples_are_editable_independent_copies(tmp_path):
    for code, word in [('en','Hello'), ('ja','こんにちは'), ('zh_TW','你好'), ('zh_CN','你好')]:
        source = projects.example_root()/code/'sample.advdb'
        original = source.read_bytes()
        first = projects.copy_example(code, destination=tmp_path)
        db = Database(first); data = db.load()
        assert word in data['sections'][0]['rows'][0]['text']
        data['sections'][0]['rows'][0]['text'] = 'My experiment'
        db.save(data); db.close()
        second = projects.copy_example(code, destination=tmp_path)
        assert second != first and source.read_bytes() == original
        db = Database(second)
        assert db.load()['sections'][0]['rows'][0]['text'] != 'My experiment'
        db.close()
    branch = projects.copy_example('ja','branches',tmp_path)
    db = Database(branch); data = db.load(); db.close()
    assert data['images']
    for filename in data['images']:
        assert (projects.asset_folder(branch)/'images'/filename).is_file()


def test_launcher_sample_uses_selected_language(tmp_path, monkeypatch):
    monkeypatch.setattr(QStandardPaths, 'writableLocation', lambda *_: str(tmp_path))
    dialog = StartupDialog()
    dialog.language.setCurrentIndex(dialog.language.findData('en'))
    dialog.sample_button.click()
    assert dialog.result() == QDialog.DialogCode.Accepted
    assert Path(dialog.project_path).is_relative_to(tmp_path)
    db = Database(dialog.project_path)
    assert 'Hello' in db.load()['sections'][0]['rows'][0]['text']
    db.close(); dialog.deleteLater()


def test_packaged_sample_discovery(tmp_path, monkeypatch):
    monkeypatch.setattr(sys, 'frozen', True, raising=False)
    monkeypatch.setattr(sys, '_MEIPASS', str(tmp_path), raising=False)
    assert projects.example_root() == tmp_path/'examples'


def select_rows(window, first=0, last=1):
    window.table.clearSelection()
    window.table.setRangeSelected(QTableWidgetSelectionRange(first,0,last,3),True)


def test_batch_height_drag_and_persistence(window):
    w = window
    before = copy.deepcopy(w.data)
    ids = [r['id'] for r in w.rows]
    select_rows(w)
    w.row_height.setValue(137)
    w.apply_height_button.click()
    assert [w.table.rowHeight(i) for i in range(2)] == [137,137]
    # A resize from the header follows exactly the same selected-row signal path.
    w.table.verticalHeader().resizeSection(0,163)
    assert [w.table.rowHeight(i) for i in range(2)] == [163,163]
    assert w.data == before and not w.dirty
    w.refresh()
    assert [w.table.rowHeight(i) for i in range(2)] == [163,163]
    w.table.setCurrentCell(0,1); w.move_row(1)
    assert [r['id'] for r in w.rows] == ids[::-1]
    assert w.table.rowHeight(0) == 163
    w.save()
    path = w.db.path
    reopened = Window(path)
    assert [reopened.table.rowHeight(i) for i in range(2)] == [163,163]
    reopened.dirty = False; reopened.close()
    select_rows(w)
    w.reset_height_button.click()
    assert [w.table.rowHeight(i) for i in range(2)] == [w.automatic_row_height(row) for row in w.rows]
    assert not w.row_heights


def test_noncontiguous_batch_height(window):
    w = window
    w.add_row(); w.add_row()
    w.table.clearSelection()
    for row in [0,3]:
        w.table.setRangeSelected(QTableWidgetSelectionRange(row,0,row,3),True)
    middle = [w.table.rowHeight(i) for i in [1,2]]
    w.row_height.setValue(190); w.apply_height_button.click()
    assert [w.table.rowHeight(i) for i in [0,3]] == [190,190]
    assert [w.table.rowHeight(i) for i in [1,2]] == middle


def test_add_button_keyboard_and_help(window):
    w = window; count = len(w.rows)
    w.add_row_button.click(); QApplication.processEvents()
    assert len(w.rows) == count+1
    assert w.editor and (w.editor.row,w.editor.col) == (count,1)
    QTest.keyClick(w.editor,Qt.Key.Key_Tab)
    assert w.editor.col == 2
    w.editor.setPlainText('New line')
    QTest.keyClick(w.editor,Qt.Key.Key_Return,Qt.KeyboardModifier.ShiftModifier)
    w.editor.insertPlainText('Still the same dialogue')
    QTest.keyClick(w.editor,Qt.Key.Key_Return)
    assert len(w.rows) == count+2
    assert '\n' in w.rows[count]['text']
    checked = []
    def inspect_help():
        from PySide6.QtWidgets import QTextBrowser
        dialog = QApplication.activeModalWidget()
        text = dialog.findChild(QTextBrowser).toPlainText()
        checked.append('Shift+Enter' in text and '選取行高' in text and '子資料夾' in text)
        dialog.reject()
    QTimer.singleShot(0,inspect_help)
    w.help_button.click()
    assert checked == [True]


def test_exports_default_to_project_folder_and_allow_override(window,tmp_path,monkeypatch):
    w = window
    chosen = tmp_path/'alternate'; chosen.mkdir()
    folders = []
    from adv_editor.rpy_options import RenPyExportDialog
    def choose_folder(dialog):
        folders.append(dialog.directory.text())
        dialog.directory.setText(str(chosen))
        dialog.mode.setCurrentIndex(1)
        return True
    monkeypatch.setattr(RenPyExportDialog,'exec',choose_folder)
    button = next(b for b in w.findChildren(QPushButton) if b.text() == '匯出 .rpy')
    button.click()
    assert folders == [str(w.db.path.parent)]
    assert (chosen/'dialogue.rpy').is_file()
    import adv_editor.gui as gui
    files = []; exports = []
    def choose_file(*args):
        files.append(args[2]); return str(chosen/Path(args[2]).name), ''
    monkeypatch.setattr(QFileDialog,'getSaveFileName',choose_file)
    monkeypatch.setattr(gui,'export_excel',lambda data,path,project: exports.append(Path(path)))
    class Options:
        def __init__(self,*args):
            from PySide6.QtWidgets import QLineEdit,QCheckBox
            self.title_input=QLineEdit('My title'); self.include_ids=QCheckBox()
        def exec(self): return True
    monkeypatch.setattr(gui,'DocumentExportDialog',Options)
    import adv_editor.documents as documents
    monkeypatch.setattr(documents,'export_word',lambda data,path,**kwargs: exports.append(Path(path)))
    monkeypatch.setattr(documents,'export_pdf',lambda data,path,*args,**kwargs: exports.append(Path(path)) or [])
    w.excel_out(); w.document_out('docx'); w.document_out('pdf')
    assert files == [str(w.db.path.with_suffix('.'+suffix)) for suffix in ['xlsx','docx','pdf']]
    assert all(path.parent == chosen for path in exports)


@pytest.mark.parametrize('subfolder,nested,expected_prefix', [('My script',False,'My script/'), ('',False,''), ('',True,'dialogue/'), ('章節',True,'dialogue/章節/')])
def test_custom_export_paths_and_assets(tmp_path,subfolder,nested,expected_prefix):
    from adv_editor.core import export_rpy,new_row
    from adv_editor.assets import import_font,font_file,image_file
    from adv_editor.platform_fonts import importable_system_font
    source = projects.copy_example('en','branches',tmp_path/'source')
    db = Database(source); data = db.load(); db.close()
    font_path = importable_system_font()
    assert font_path is not None
    font,family = import_font(font_path,source)
    data['fonts'][font] = family
    original_tag = '{font=adv_generated/fonts/'+font+'}'
    data['sections'][0]['rows'][1]['text'] = original_tag+'Bold{/font} literal: {'+original_tag
    data['sections'][0]['rows'][-1]['choices'][0]['text'] = original_tag+'Choice{/font}'
    before = copy.deepcopy(data)
    game = tmp_path/'game'; game.mkdir()
    destination = game/'dialogue' if nested else game
    destination.mkdir(exist_ok=True)
    result = export_rpy(data,destination,source,subfolder=subfolder)
    assert result == destination/subfolder
    text = (result/'dialogue.rpy').read_text()
    remapped = '{font='+expected_prefix+'fonts/'+font+'}'
    assert remapped+'Bold{/font}' in text and remapped+'Choice{/font}' in text
    assert 'literal: {'+original_tag in text
    assert data == before
    assert (result/'fonts'/font).read_bytes() == font_file(source,font).read_bytes()
    image = next(iter(data['images']))
    assert (result/'images'/image).read_bytes() == image_file(source,image).read_bytes()
    assert '"'+expected_prefix+'images/'+image+'"' in (result/'characters.rpy').read_text()
    assert not (destination/'adv_generated').exists()
    export_rpy(data,destination,source,subfolder=subfolder)


def test_direct_export_preserves_handwritten_files(tmp_path):
    from adv_editor.core import export_rpy
    existing = tmp_path/'dialogue.rpy'; existing.write_text('label handwritten:\n    return\n')
    with pytest.raises(FileExistsError):
        export_rpy(sample(),tmp_path,subfolder='')
    assert existing.read_text().startswith('label handwritten:')
    assert not (tmp_path/'characters.rpy').exists()
    with pytest.raises(ValueError):
        export_rpy(sample(),tmp_path,subfolder='../escaped')
    assert not (tmp_path.parent/'escaped').exists()


def test_rpy_options_validation_and_preview(tmp_path):
    from adv_editor.rpy_options import RenPyExportDialog
    dialog = RenPyExportDialog(tmp_path,'My export')
    assert str(tmp_path/'My export') in dialog.preview.text()
    dialog.folder_name.setText('../outside')
    dialog.accept()
    assert dialog.result() != QDialog.DialogCode.Accepted and dialog.error.text()
    dialog.mode.setCurrentIndex(1)
    assert not dialog.folder_name.isEnabled()
    assert dialog.subfolder == ''
    dialog.accept()
    assert dialog.result() == QDialog.DialogCode.Accepted
    dialog.deleteLater()



def test_dragging_selected_row_boundary(window):
    from PySide6.QtCore import QPoint
    w = window
    select_rows(w)
    header = w.table.verticalHeader()
    old = w.table.rowHeight(0)
    start = QPoint(header.width()//2,header.sectionViewportPosition(0)+old-1)
    end = start + QPoint(0,35)
    QTest.mousePress(header.viewport(),Qt.MouseButton.LeftButton,Qt.KeyboardModifier.NoModifier,start)
    QTest.mouseMove(header.viewport(),end,20)
    QTest.mouseRelease(header.viewport(),Qt.MouseButton.LeftButton,Qt.KeyboardModifier.NoModifier,end)
    assert w.table.rowHeight(0) > old
    assert w.table.rowHeight(0) == w.table.rowHeight(1)
