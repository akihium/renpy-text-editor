import copy
import sqlite3
import pytest
from adv_editor.core import *


def test_sqlite_ids_backup(tmp_path):
    data = sample()
    db = Database(tmp_path/'project.advdb')
    db.save(data)
    assert db.load() == data
    data['sections'][0]['rows'].reverse()
    db.save(data)
    assert db.load() == data
    db.backup()
    backup = next((tmp_path/'project_backups').glob('*.advdb'))
    other = Database(backup)
    assert other.load() == data
    other.close()
    db.close()


def test_export(tmp_path):
    data = sample()
    row = data['sections'][0]['rows'][0]
    row['text'] = '"路徑\\file"\n{b}粗體{/b} [字面值] 50% {custom}保留{/custom}'
    manual = tmp_path/'staging.rpy'
    manual.write_text('label start:\n    call adv_opening\n    return\n')
    folder = export_rpy(data,tmp_path)
    content = (folder/'dialogue.rpy').read_text()
    assert 'call adv_greeting' in content
    assert 'id '+row['id'] in content
    assert '\\"' in content and '\\\\file' in content and '\\n' in content
    assert '{custom}保留{/custom}' in content
    assert '[[字面值]' in content
    assert manual.read_text().startswith('label start:')


def test_excel_roundtrip(tmp_path):
    data = sample()
    data['sections'][0]['rows'][0]['text'] = '=SUM(A1:A2)\n{custom}原樣{/custom}'
    path = tmp_path/'dialogue.xlsx'
    export_excel(data,path)
    assert import_excel(path) == data


def test_invalid_transaction(tmp_path):
    db = Database(tmp_path/'a.advdb')
    data = sample()
    db.save(data)
    bad = copy.deepcopy(data)
    bad['sections'][0]['rows'][0]['character'] = 'missing'
    with pytest.raises(ValueError): db.save(bad)
    assert db.load() == data
    bad = copy.deepcopy(data)
    bad['sections'][0]['call'] = 'missing'
    with pytest.raises(ValueError): export_rpy(bad,tmp_path)
    db.close()


def test_character_colors_export_and_legacy_database(tmp_path):
    path = tmp_path/'legacy.advdb'
    with sqlite3.connect(path) as conn:
        conn.execute('CREATE TABLE characters(id TEXT PRIMARY KEY,name TEXT NOT NULL)')
    db = Database(path)
    data = sample()
    db.save(data)
    assert db.load()['character_colors'] == data['character_colors']
    folder = export_rpy(data,tmp_path)
    assert 'color="#e5b5a5"' in (folder/'characters.rpy').read_text()
    db.close()


def test_legacy_excel_without_color_column(tmp_path):
    from openpyxl import load_workbook
    data = sample()
    path = tmp_path/'old.xlsx'
    export_excel(data,path)
    wb = load_workbook(path)
    wb['角色'].delete_cols(3)
    wb.save(path)
    restored = import_excel(path)
    assert restored['character_colors'] == {}
    assert restored['characters'] == data['characters']
