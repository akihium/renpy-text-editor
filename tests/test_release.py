import copy
import importlib.util
import json
import string
from pathlib import Path
import pytest
from PySide6.QtWidgets import QApplication
from adv_editor import i18n
from adv_editor.gui import Window
from adv_editor.core import Database,validate
from scripts.create_examples import create_examples,TEXT


def test_japanese_interface_preserves_project():
    w=Window();before=copy.deepcopy(w.data)
    w.language_combo.setCurrentIndex(w.language_combo.findData('ja'))
    assert w.character_button.text()=='キャラクター管理'
    assert w.table.horizontalHeaderItem(2).text()=='セリフ'
    assert w.show_ids.text()=='セリフ ID を表示'
    assert w.data==before
    w.dirty=False;w.close();QApplication.processEvents()


def test_translation_catalogs_have_same_keys_and_placeholders():
    source=set(i18n.CATALOGS['en'])
    formatter=string.Formatter()
    def fields(value): return {field for _,field,_,_ in formatter.parse(value) if field}
    for code,catalog in i18n.CATALOGS.items():
        assert set(catalog)==source
        for key,value in catalog.items(): assert fields(value)==fields(key),(code,key)


def test_four_localized_example_sets(tmp_path):
    create_examples(tmp_path/'examples')
    ids=[]
    for code in ['zh_TW','zh_CN','ja','en']:
        folder=tmp_path/'examples'/code
        for filename in ['sample.advdb','branches.advdb']:
            db=Database(folder/filename);data=db.load();db.close();validate(data)
            assert data['fonts']=={}
            if filename=='sample.advdb':
                assert data['sections'][0]['rows'][0]['text']==TEXT[code]['hello']
                ids.append([r['id'] for s in data['sections'] for r in s['rows']])
            else:
                assert data['sections'][0]['rows'][-1]['choices'][0]['text']==TEXT[code]['choices'][0]
                assert list((folder/'branches_assets'/'images').glob('*.png'))
                assert 'menu:' in (folder/'renpy_game'/'adv_generated'/'dialogue.rpy').read_text()
        assert (folder/'sample.xlsx').is_file() and (folder/'branches.xlsx').is_file()
    assert all(value==ids[0] for value in ids)


def test_windows_font_candidates_are_host_relative(monkeypatch,tmp_path):
    import adv_editor.platform_fonts as fonts
    monkeypatch.setattr(fonts.sys,'platform','win32')
    monkeypatch.setenv('WINDIR',str(tmp_path/'Windows'))
    assert fonts.document_font_family()=='Microsoft JhengHei'
    assert fonts.pdf_font_candidates()[0]==tmp_path/'Windows'/'Fonts'/'msjh.ttc'
    assert fonts.pdf_font_candidates(bold=True)[0].name=='msjhbd.ttc'



def test_frozen_export_checks_use_utf8_with_legacy_windows_defaults(monkeypatch,tmp_path):
    from adv_editor.verify import verify_exports
    read=Path.read_text
    def legacy_read(path,encoding=None,errors=None):
        return read(path,encoding=encoding or 'cp1252',errors=errors)
    monkeypatch.setattr(Path,'read_text',legacy_read)
    verify_exports(tmp_path)
    assert json.loads((tmp_path/'result.json').read_text(encoding='utf-8'))['ok']
