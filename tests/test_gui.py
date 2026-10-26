import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import pytest
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
from adv_editor.gui import Window
from adv_editor.core import Database


@pytest.fixture(scope='session')
def app():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def window(app,tmp_path):
    w = Window()
    w.db = Database(tmp_path/'gui.advdb')
    w.db.save(w.data)
    w.show()
    app.processEvents()
    yield w
    w.editor = None
    w.dirty = False
    w.close()
    app.processEvents()


def edit(w,row,col):
    w.table.setCurrentCell(row,col)
    w.table.editItem(w.table.item(row,col))
    QApplication.processEvents()
    assert w.editor
    return w.editor


def test_navigation(window):
    w = window
    e = edit(w,0,1)
    QTest.keyClick(e,Qt.Key.Key_Tab)
    assert w.table.currentColumn() == 2
    QTest.keyClick(w.editor,Qt.Key.Key_Backtab,Qt.KeyboardModifier.ShiftModifier)
    assert w.table.currentColumn() == 1
    QTest.keyClick(w.editor,Qt.Key.Key_Return)
    assert (w.table.currentRow(),w.table.currentColumn()) == (1,1)
    before = len(w.rows)
    QTest.keyClick(w.editor,Qt.Key.Key_Return)
    assert len(w.rows) == before+1
    assert w.table.currentColumn() == 1


def test_format_newline_save(window):
    w = window
    original = w.rows[0]['id']
    e = edit(w,0,2)
    e.setPlainText('hello')
    e.selectAll()
    QTest.keyClick(e,Qt.Key.Key_B,Qt.KeyboardModifier.ControlModifier)
    assert e.toPlainText() == 'hello'
    assert e.source() == '{b}hello{/b}'
    e.selectAll()
    QTest.keyClick(e,Qt.Key.Key_I,Qt.KeyboardModifier.ControlModifier)
    assert e.toPlainText() == 'hello'
    assert '{i}' in e.source() and '{b}' in e.source()
    QTest.keyClick(e,Qt.Key.Key_End)
    QTest.keyClick(e,Qt.Key.Key_Return,Qt.KeyboardModifier.ShiftModifier)
    e.insertPlainText('下一行')
    e.wrap('custom')
    assert '\n' in e.toPlainText()
    QTest.keyClick(e,Qt.Key.Key_Return)
    w.commit()
    assert w.save()
    assert w.db.load() == w.data
    assert w.rows[0]['id'] == original
    assert '{custom}' in w.rows[0]['text']


def test_paste_undo_reorder(window):
    w = window
    w.paste_grid('aki\t甲\t備註\nmei\t乙\t第二行',0,1)
    assert w.rows[1]['text'] == '乙'
    ids = [r['id'] for r in w.rows]
    w.table.setCurrentCell(0,1)
    w.move_row(1)
    assert [r['id'] for r in w.rows] == ids[::-1]
    w.undo()
    assert [r['id'] for r in w.rows] == ids
    w.undo()
    assert w.rows[0]['text'] != '甲'
    w.redo()
    assert w.rows[0]['text'] == '甲'


def test_visual_unknown_tags(window):
    w = window
    e = edit(w,0,2)
    e.set_source('{b}粗{/b}{unrecognized=1}保留{/unrecognized}')
    w.commit()
    w.change_mode(1)
    w.change_mode(0)
    assert '{unrecognized=1}' in w.rows[0]['text']
    QApplication.processEvents()
    image = w.grab()
    assert not image.isNull()


def test_autosave_preserves_editor(window):
    w = window
    e = edit(w,0,2)
    e.set_source('尚在輸入 {b}儲存{/b}')
    w.save_if_dirty()
    assert w.editor is e
    assert w.db.load()['sections'][0]['rows'][0]['text'] == e.source()
    e.insertPlainText('繼續')
    w.save_if_dirty()
    assert '繼續' in w.db.load()['sections'][0]['rows'][0]['text']


def test_search_replace_all_sections(window):
    w = window
    w.find_text.setText('午後')
    w.find_next()
    assert w.section_index == 1
    w.replace_text.setText('清晨')
    w.replace_all()
    assert '清晨' in w.rows[0]['text']
    w.undo()
    assert '午後' in w.rows[0]['text']


def test_click_format_toolbar_keeps_selection(window):
    from PySide6.QtGui import QTextCursor, QFont
    w = window
    e = edit(w,0,2)
    e.set_source('甲乙丙')
    cursor = e.textCursor()
    cursor.setPosition(1)
    cursor.setPosition(2,QTextCursor.MoveMode.KeepAnchor)
    e.setTextCursor(cursor)
    QTest.mouseClick(w.format_buttons['b'],Qt.MouseButton.LeftButton)
    assert w.editor is e
    assert e.toPlainText() == '甲乙丙'
    assert e.source() == '甲{b}乙{/b}丙'
    assert e.textCursor().charFormat().fontWeight() >= QFont.Weight.Bold
    # Clicking/repositioning within the styled text never exposes markup.
    cursor.setPosition(2)
    e.setTextCursor(cursor)
    assert '{b}' not in e.toPlainText()
    w.mode.setCurrentIndex(1)
    assert w.editor.toPlainText() == '甲{b}乙{/b}丙'
    w.mode.setCurrentIndex(0)
    assert w.editor.toPlainText() == '甲乙丙'


def test_wait_chip_and_opaque_tags_survive_edits(window):
    from PySide6.QtGui import QTextCursor
    from adv_editor.richtext import TOKEN, token_label
    w = window
    e = edit(w,0,2)
    source = '😀{b}你好{w=0.5}世界{/b}{custom=abc}尾{/custom}'
    e.set_source(source)
    assert e.source() == source
    assert '{' not in e.toPlainText()
    assert token_label('{w=0.5}') == '等待 0.5s'
    cursor = e.textCursor()
    cursor.movePosition(QTextCursor.MoveOperation.End)
    e.setTextCursor(cursor)
    QTest.keyClicks(e,'!')
    result = e.source()
    assert '{w=0.5}' in result
    assert '{custom=abc}' in result and '{/custom}' in result
    assert result.endswith('!') and '😀' in result
    w.commit()
    assert w.save()
    assert w.db.load()['sections'][0]['rows'][0]['text'] == result


def test_insert_wait_button_and_undo(window):
    from PySide6.QtGui import QTextCursor
    w = window
    e = edit(w,0,2)
    e.set_source('前後')
    cursor = e.textCursor()
    cursor.setPosition(1)
    e.setTextCursor(cursor)
    QTest.mouseClick(w.wait_button,Qt.MouseButton.LeftButton)
    assert e.source() == '前{w=0.5}後'
    assert e.toPlainText() == '前\ufffc後'
    e.undo()
    assert e.source() == '前後'
    e.redo()
    assert '{w=0.5}' in e.source()


def test_role_background_and_character_dialog(window):
    from adv_editor.characters import CharacterDialog
    from PySide6.QtCore import QSettings
    w = window
    w.role_background.setChecked(True)
    color = w.data['character_colors']['aki']
    assert w.table.item(0,1).background().color().name() == color
    before = len(w.undo_stack)
    w.role_background.setChecked(False)
    assert w.table.item(0,1).data(Qt.ItemDataRole.BackgroundRole) is None
    assert w.data['character_colors']['aki'] == color
    assert len(w.undo_stack) == before
    w.role_background.setChecked(True)
    dialog = CharacterDialog(w.data,w)
    assert dialog.table.item(0,0).flags() & Qt.ItemFlag.ItemIsEditable
    dialog.table.item(0,1).setText('新名字')
    dialog.table.cellWidget(0,2).input.setText('#123456')
    chars,colors = dialog.values()
    assert chars['aki'] == '新名字' and colors['aki'] == '#123456'
    dialog.add_row('new_person','新角色','#abcdef')
    assert dialog.values()[0]['new_person'] == '新角色'
    dialog.table.cellWidget(0,2).input.setText('bad')
    with pytest.raises(ValueError): dialog.values()
    dialog.close()


def test_visual_plain_typing_and_literal_braces(window):
    from PySide6.QtGui import QTextCursor
    w = window
    e = edit(w,0,2)
    e.set_source('A{{B')
    assert e.toPlainText() == 'A{B'
    cursor = e.textCursor()
    cursor.movePosition(QTextCursor.MoveOperation.End)
    e.setTextCursor(cursor)
    QTest.keyClicks(e,'C')
    assert e.source() == 'A{{BC'


def test_font_controls_focus_and_visual_color(window):
    from PySide6.QtGui import QTextCursor
    from PySide6.QtWidgets import QColorDialog
    w = window
    e = edit(w,0,2)
    e.set_source('文字')
    e.selectAll()
    w.font_size.setFocus()
    w.font_size.setValue(32)
    QApplication.processEvents()
    assert w.editor is e
    w.format_text('size=32')
    w.format_text('color=#ff0000')
    assert e.toPlainText() == '文字'
    assert 'size=32' in e.source() and 'color=#ff0000' in e.source()
    assert e.textCursor().charFormat().fontPointSize() == 32
    assert e.textCursor().charFormat().foreground().color().name() == '#ff0000'


def test_visual_copy_paste_preserves_chips_and_format(window):
    from PySide6.QtGui import QTextCursor
    w = window
    e = edit(w,0,2)
    e.set_source('{b}文字{/b}{w=0.5}')
    e.selectAll()
    mime = e.createMimeDataFromSelection()
    cursor = e.textCursor()
    cursor.movePosition(QTextCursor.MoveOperation.End)
    e.setTextCursor(cursor)
    e.insertFromMimeData(mime)
    assert e.source().count('{w=0.5}') == 2
    assert e.source().count('{b}') == 2
    assert '{b}' not in e.toPlainText()


def test_section_form_edit_english_id_and_validation(window):
    from adv_editor.sections import SectionForm
    from PySide6.QtWidgets import QDialog
    import copy
    data = copy.deepcopy(window.data)
    form = SectionForm(data)
    form.chapter.setCurrentText('第二章 Chapter 2')
    form.name.setText('新相遇')
    form.sid.setText('chapter02_opening')
    assert form.label_preview.text().endswith('adv_chapter02_opening')
    form.accept()
    assert form.result() == QDialog.DialogCode.Accepted
    assert data['sections'][-1]['id'] == 'chapter02_opening'
    bad = SectionForm(data)
    bad.name.setText('重複')
    bad.sid.setText('opening')
    before = copy.deepcopy(data)
    bad.accept()
    assert data == before
    assert '已存在' in bad.error.text()


def test_section_manager_batch_and_cancel(window):
    from adv_editor.sections import SectionDialog
    w = window
    dialog = SectionDialog(w.data,'opening')
    dialog.show()
    QApplication.processEvents()
    dialog.refresh(['opening','greeting'])
    QTest.mouseClick(dialog.buttons['複製'],Qt.MouseButton.LeftButton)
    assert len(dialog.data['sections']) == 4
    assert dialog.selected_ids() == ['opening_copy','greeting_copy']
    QTest.mouseClick(dialog.buttons['合併選取'],Qt.MouseButton.LeftButton)
    assert len(dialog.data['sections']) == 3
    assert len(dialog.data['sections'][-1]['rows']) == 3
    dialog.reject()
    assert len(w.data['sections']) == 2


def test_main_section_manager_apply_and_undo(window,monkeypatch):
    from adv_editor.sections import SectionDialog
    from adv_editor.section_ops import update_section
    from PySide6.QtWidgets import QDialog
    def accepted(dialog):
        update_section(dialog.data,None,'new_scene','第二章','新場景')
        dialog.current_id = 'new_scene'
        return QDialog.DialogCode.Accepted
    monkeypatch.setattr(SectionDialog,'exec',accepted)
    QTest.mouseClick(window.section_button,Qt.MouseButton.LeftButton)
    assert len(window.data['sections']) == 3
    assert window.data['sections'][window.section_index]['id'] == 'new_scene'
    assert 'adv_new_scene' in window.sections.currentText()
    window.undo()
    assert len(window.data['sections']) == 2
    window.redo()
    assert len(window.data['sections']) == 3


def test_section_manager_move_and_delete(window):
    from adv_editor.sections import SectionDialog
    dialog = SectionDialog(window.data,'opening')
    dialog.refresh(['greeting'])
    dialog.move(-1)
    assert dialog.data['sections'][0]['id'] == 'greeting'
    dialog.delete()
    assert len(dialog.data['sections']) == 1
    assert dialog.data['sections'][0]['call'] == ''
    dialog.refresh(['opening'])
    dialog.delete()
    assert len(dialog.data['sections']) == 1
    assert '至少' in dialog.status.text()
