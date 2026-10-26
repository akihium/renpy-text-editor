import copy
import pytest
from adv_editor.core import sample, Database, export_rpy, validate
from adv_editor.section_ops import (available_id, update_section, duplicate_sections,
    delete_sections, merge_sections)


def test_add_english_id_rename_and_refs(tmp_path):
    data = sample()
    original_ids = [r['id'] for r in data['sections'][1]['rows']]
    update_section(data,None,'chapter02_scene01','第二章','新的段落','opening')
    assert data['sections'][-1]['id'] == 'chapter02_scene01'
    update_section(data,'greeting','greeting_renamed','第一章','重新命名')
    assert data['sections'][0]['call'] == 'greeting_renamed'
    assert [r['id'] for r in data['sections'][1]['rows']] == original_ids
    path = tmp_path/'sections.advdb'
    db = Database(path)
    db.save(data)
    assert db.load() == data
    db.close()
    result = export_rpy(data,tmp_path)
    source = (result/'dialogue.rpy').read_text()
    assert 'label adv_chapter02_scene01:' in source
    assert 'call adv_greeting_renamed' in source


@pytest.mark.parametrize('sid',['bad name','中文','2scene','opening','call',''])
def test_invalid_id_is_atomic(sid):
    data = sample()
    before = copy.deepcopy(data)
    with pytest.raises(ValueError): update_section(data,None,sid,'第一章','測試')
    assert data == before


def test_copy_batch_ids_and_calls():
    data = sample()
    originals = copy.deepcopy(data['sections'])
    copies = duplicate_sections(data,['opening','greeting'])
    assert copies == ['opening_copy','greeting_copy']
    assert data['sections'][2]['call'] == 'greeting_copy'
    assert data['sections'][:2] == originals
    old_ids = {r['id'] for s in originals for r in s['rows']}
    new_ids = {r['id'] for s in data['sections'][2:] for r in s['rows']}
    assert not old_ids & new_ids
    duplicate_sections(data,['opening'])
    assert data['sections'][-1]['id'] == 'opening_copy_2'
    validate(data)


def test_delete_clears_refs_and_keeps_one():
    data = sample()
    original = data['sections'][0]['rows'][0]['id']
    delete_sections(data,['greeting'])
    assert data['sections'][0]['call'] == ''
    assert data['sections'][0]['rows'][0]['id'] == original
    before = copy.deepcopy(data)
    with pytest.raises(ValueError): delete_sections(data,['opening'])
    assert data == before


def test_merge_ids_order_and_call_redirection():
    data = sample()
    update_section(data,None,'external','第二章','外部','greeting')
    update_section(data,None,'tail','第二章','後續')
    data['sections'][1]['call'] = 'tail'
    old_rows = copy.deepcopy(data['sections'][0]['rows']+data['sections'][1]['rows'])
    sid = merge_sections(data,['greeting','opening'])
    assert sid == 'opening'
    assert data['sections'][0]['rows'] == old_rows
    assert data['sections'][0]['call'] == 'tail'
    assert data['sections'][1]['call'] == 'opening'
    assert len(data['sections']) == 3
    validate(data)


def test_merge_rejects_ambiguous_flow_atomically():
    data = sample()
    update_section(data,None,'external','第二章','外部')
    data['sections'][0]['call'] = 'external'
    before = copy.deepcopy(data)
    with pytest.raises(ValueError,match='call'): merge_sections(data,['opening','greeting'])
    assert data == before
    data['sections'][0]['call'] = 'greeting'
    data['sections'][1]['call'] = 'opening'
    with pytest.raises(ValueError,match='自身'): merge_sections(data,['opening','greeting'])
