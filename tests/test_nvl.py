import copy
import pytest
from PySide6.QtWidgets import QApplication
from adv_editor.core import sample,new_row,Database,export_excel,import_excel,export_rpy,statement,validate
from adv_editor.character_ops import update_characters
from adv_editor.characters import CharacterDialog
from adv_editor.stage import StageDialog
from adv_editor.gui import Window


def nvl_project():
    data=sample();data['character_modes']={'aki':'nvl'};data['narrator_mode']='nvl'
    data['sections'][0]['rows'].extend([
        dict(new_row(),kind='nvl_clear'),
        dict(new_row(),kind='menu',text='Question?',nvl_menu=True,nvl_clear_after=True,choices=[dict(text='Continue',target='greeting')])])
    return data


def test_nvl_sqlite_excel_export_roundtrip(tmp_path):
    data=nvl_project();original=copy.deepcopy(data)
    path=tmp_path/'mixed.advdb';db=Database(path);db.save(data);assert db.load()==data;db.close()
    export_excel(data,tmp_path/'mixed.xlsx');assert import_excel(tmp_path/'mixed.xlsx')==data
    out=export_rpy(data,tmp_path)
    characters=(out/'characters.rpy').read_text();dialogue=(out/'dialogue.rpy').read_text()
    assert 'kind=nvl' in next(line for line in characters.splitlines() if line.startswith('define aki '))
    assert 'kind=nvl' not in next(line for line in characters.splitlines() if line.startswith('define mei '))
    assert 'define narrator = nvl_narrator' in characters
    assert 'menu (nvl=True):' in dialogue and 'nvl_narrator "Question?" id ' in dialogue
    assert 'nvl clear' in dialogue and 'nvl clear\n            jump adv_greeting' in dialogue
    assert data==original


def test_nvl_rename_and_return_to_adv():
    data=nvl_project();original_ids=[r['id'] for s in data['sections'] for r in s['rows']]
    update_characters(data,{'renamed':'秋','mei':'美'},{},{'aki':'renamed','mei':'mei'})
    assert data['character_modes']=={'renamed':'nvl'}
    assert data['sections'][0]['rows'][0]['character']=='renamed'
    update_characters(data,data['characters'],{}, {},modes={},narrator_mode='adv')
    assert 'character_modes' not in data and 'narrator_mode' not in data
    assert [r['id'] for s in data['sections'] for r in s['rows']]==original_ids


def test_nvl_character_and_stage_controls():
    data=nvl_project();before=copy.deepcopy(data)
    dialog=CharacterDialog(data)
    assert dialog.table.cellWidget(0,3).currentData()=='nvl'
    assert dialog.narrator_mode.currentData()=='nvl'
    dialog.table.item(0,0).setText('new_name')
    assert dialog.modes()=={'new_name':'nvl'}
    assert data==before
    dialog.reject();dialog.deleteLater()
    menu=StageDialog(data,None)
    menu.kind.setCurrentIndex(menu.kind.findData('menu'))
    menu.table.item(0,0).setText('Go')
    menu.nvl_menu.setChecked(True);menu.nvl_clear_after.setChecked(False)
    menu.accept()
    assert menu.result_row['nvl_menu'] and not menu.result_row['nvl_clear_after']
    source=statement(menu.result_row)
    assert 'menu (nvl=True):' in source and 'nvl clear' not in source
    menu.deleteLater()
    clear=StageDialog(data,None)
    clear.kind.setCurrentIndex(clear.kind.findData('nvl_clear'));clear.accept()
    assert statement(clear.result_row)=='nvl clear'
    clear.deleteLater()


def test_nvl_clear_main_button_undo_text_only(tmp_path):
    path=tmp_path/'project.advdb';db=Database(path);db.save(nvl_project());db.close()
    w=Window(path);w.table.setCurrentCell(0,2)
    count=len(w.rows);w.nvl_clear_button.click()
    assert len(w.rows)==count+1 and w.rows[1]['kind']=='nvl_clear'
    assert w.table.item(1,0).text()=='nvl clear'
    w.toggle_text_only(True);assert w.table.isRowHidden(1)
    w.toggle_text_only(False);w.undo();assert len(w.rows)==count
    w.redo();assert w.rows[1]['kind']=='nvl_clear'
    assert w.save() and w.db.load()==w.data
    w.dirty=False;w.close();QApplication.processEvents()


@pytest.mark.parametrize('field,value',[('character_modes',{'aki':'bad'}),('character_modes',{'missing':'nvl'}),('narrator_mode','bad')])
def test_invalid_nvl_modes(field,value):
    data=sample();data[field]=value
    with pytest.raises(ValueError): validate(data)


def test_nvl_validation_reserved_and_boolean():
    data=sample();data['characters']['nvl']='Reserved';data['narrator_mode']='nvl'
    with pytest.raises(ValueError): validate(data)
    data=nvl_project();data['sections'][0]['rows'][-1]['nvl_menu']='yes'
    with pytest.raises(ValueError): validate(data)
