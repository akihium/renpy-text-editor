"""Atomic section operations. Existing dialogue IDs survive moves and merges."""
from .i18n import tr
import copy
from .core import identifier, new_row, uid, validate


def remap_links(sections,mapping):
    for section in sections:
        section['call']=mapping.get(section['call'],section['call'])
        for row in section['rows']:
            if row.get('kind') in ('jump','call'): row['text']=mapping.get(row['text'],row['text'])
            for choice in row.get('choices',[]): choice['target']=mapping.get(choice['target'],choice['target'])


def available_id(data, base='scene'):
    used = {s['id'] for s in data['sections']}
    value,number = base,2
    while value in used:
        value = f'{base}_{number}'
        number += 1
    return value


def update_section(data, original_id, sid, chapter, name, target=''):
    identifier(sid)
    if not chapter.strip() or not name.strip():
        raise ValueError(tr('請填寫章節名稱與段落名稱。'))
    draft = copy.deepcopy(data)
    if any(s['id'] == sid and s['id'] != original_id for s in draft['sections']):
        raise ValueError(tr('英文段落 ID 已存在：')+sid)
    section = next((s for s in draft['sections'] if s['id'] == original_id),None) if original_id else None
    if original_id and section is None:
        raise ValueError(tr('找不到段落'))
    if section is None:
        section = {'rows':[new_row()]}
        draft['sections'].append(section)
    section.update(id=sid,chapter=chapter.strip(),name=name.strip(),call=target)
    if original_id and sid != original_id:
        remap_links(draft['sections'],{original_id:sid})
    if section['call'] == sid:
        raise ValueError(tr('段落不能 call 自己。'))
    validate(draft)
    data['sections'] = draft['sections']
    return sid


def duplicate_sections(data, ids):
    draft = copy.deepcopy(data)
    copied = []
    # Remap calls within the copied set to its corresponding copies.
    mapping = {}
    for section in draft['sections'][:]:
        if section['id'] not in ids: continue
        clone = copy.deepcopy(section)
        clone['id'] = available_id(draft,section['id']+'_copy')
        clone['name'] += '（副本）'
        for row in clone['rows']: row['id'] = uid('d_')
        draft['sections'].append(clone)
        mapping[section['id']] = clone['id']
        copied.append(clone)
    if not copied: raise ValueError(tr('請選取要複製的段落。'))
    remap_links(copied,mapping)
    validate(draft)
    data['sections'] = draft['sections']
    return [s['id'] for s in copied]


def delete_sections(data, ids):
    remaining = [copy.deepcopy(s) for s in data['sections'] if s['id'] not in ids]
    if not remaining: raise ValueError(tr('專案至少要保留一個段落。'))
    for section in remaining:
        if section['call'] in ids: section['call'] = ''
    draft = dict(data,sections=remaining)
    validate(draft)
    data['sections'] = remaining


def merge_sections(data, ids):
    draft = copy.deepcopy(data)
    selected = [s for s in draft['sections'] if s['id'] in ids]
    if len(selected) < 2: raise ValueError(tr('請選取至少兩個段落進行合併。'))
    selected_ids = {s['id'] for s in selected}
    # Only a linear call to the next selected section can be absorbed safely.
    for i,section in enumerate(selected):
        target = section['call']
        if i < len(selected)-1 and target and target != selected[i+1]['id']:
            raise ValueError(tr('「{name}」有不能直接合併的 call，請先調整流程；只允許呼叫下一個待合併段落。',name=section['name']))
        if i == len(selected)-1 and target in selected_ids:
            raise ValueError(tr('合併後會呼叫自身，請先移除最後段落的內部 call。'))
    first = selected[0]
    first['rows'] = [r for s in selected for r in s['rows']]
    first['call'] = selected[-1]['call']
    removed = selected_ids-{first['id']}
    draft['sections'] = [s for s in draft['sections'] if s['id'] not in removed]
    remap_links(draft['sections'],{sid:first['id'] for sid in removed})
    validate(draft)
    data['sections'] = draft['sections']
    return first['id']
