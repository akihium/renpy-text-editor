"""Project label-prefix persistence and linked Ren'Py output."""
import copy
import pytest
from PySide6.QtWidgets import QApplication, QDialog
from adv_editor.core import (Database, sample, new_row, export_rpy, export_excel,
    import_excel, statement, validate)
from adv_editor.gui import Window
from adv_editor.sections import SectionDialog, SectionForm


def linked_project():
    data=sample()
    data['sections'][0]['rows'].extend([
        dict(new_row(),kind='call',text='greeting'),
        dict(new_row(),kind='jump',text='greeting'),
        dict(new_row(),kind='menu',text='Choice',choices=[dict(text='Go',target='greeting')])])
    return data


@pytest.mark.parametrize('prefix',['adv_','story_','', 'project2'])
def test_prefix_all_links_and_roundtrip(tmp_path,prefix):
    data=linked_project();data['label_prefix']=prefix
    original_ids=[r['id'] for s in data['sections'] for r in s['rows']]
    before=copy.deepcopy(data)
    path=tmp_path/'project.advdb'
    db=Database(path);db.save(data);assert db.load()==data;db.close()
    db=Database(path);assert db.load()['label_prefix']==prefix;db.close()
    excel=tmp_path/'project.xlsx';export_excel(data,excel)
    assert import_excel(excel)==data
    folder=export_rpy(data,tmp_path,subfolder='custom')
    source=(folder/'dialogue.rpy').read_text()
    assert 'label '+prefix+'opening:' in source
    assert 'label '+prefix+'greeting:' in source
    assert source.count('call '+prefix+'greeting')==2
    assert source.count('jump '+prefix+'greeting')==2
    assert statement(data['sections'][0]['rows'][-1],label_prefix=prefix).endswith('jump '+prefix+'greeting')
    assert data==before
    assert [r['id'] for s in data['sections'] for r in s['rows']]==original_ids


def test_legacy_database_defaults_to_adv(tmp_path):
    path=tmp_path/'legacy.advdb';data=sample()
    db=Database(path);db.save(data)
    db.conn.execute('DROP TABLE project_settings');db.conn.execute('PRAGMA user_version=4');db.conn.commit();db.close()
    db=Database(path);assert db.load()==data
    assert db.conn.execute('PRAGMA user_version').fetchone()[0]==6
    db.close()
    text=(export_rpy(data,tmp_path)/'dialogue.rpy').read_text()
    assert 'label adv_opening:' in text


@pytest.mark.parametrize('prefix',['2start_','bad prefix','bad-prefix','中文','a\n',None])
def test_invalid_prefix_rejected_before_write(tmp_path,prefix):
    data=sample();data['label_prefix']=prefix
    with pytest.raises(ValueError): validate(data)
    with pytest.raises(ValueError): export_rpy(data,tmp_path,subfolder='output')
    assert not (tmp_path/'output').exists()


def test_section_dialog_draft_validation_and_form_preview():
    data=sample();before=copy.deepcopy(data)
    dialog=SectionDialog(data,'opening')
    assert dialog.label_prefix.text()=='adv_'
    dialog.label_prefix.setText('story_')
    form=SectionForm(dialog.data,dialog.data['sections'][0])
    assert form.label_preview.text().endswith('story_opening')
    form.sid.setText('chapter2')
    assert form.label_preview.text().endswith('story_chapter2')
    form.reject();form.deleteLater()
    dialog.label_prefix.setText('bad-prefix')
    dialog.accept()
    assert dialog.result()!=QDialog.DialogCode.Accepted and dialog.status.text()
    dialog.reject();dialog.deleteLater()
    assert data==before


def test_prefix_updates_live_preview_undo_and_save(tmp_path,monkeypatch):
    path=tmp_path/'gui.advdb';data=linked_project()
    db=Database(path);db.save(data);db.close()
    w=Window(path)
    def apply(dialog):
        dialog.label_prefix.setText('story_');dialog.accept()
        return dialog.result()
    monkeypatch.setattr(SectionDialog,'exec',apply)
    w.manage_sections()
    assert w.data['label_prefix']=='story_'
    assert '[story_opening]' in w.sections.currentText()
    assert 'call story_greeting' in w.table.item(2,0).text()
    assert 'jump story_greeting' in w.table.item(4,0).text()
    w.undo();assert 'label_prefix' not in w.data
    assert '[adv_opening]' in w.sections.currentText()
    w.redo();assert w.data['label_prefix']=='story_'
    assert w.save() and w.db.load()==w.data
    w.dirty=False;w.close();QApplication.processEvents()
