import copy
from .core import validate


def update_characters(data,characters,colors,renames,modes=None,narrator_mode=None):
    draft = copy.deepcopy(data)
    draft['characters'] = dict(characters)
    draft['character_colors'] = dict(colors)
    selected_modes = modes if modes is not None else {renames.get(cid,cid):mode for cid,mode in data.get('character_modes',{}).items() if renames.get(cid,cid) in characters}
    if selected_modes: draft['character_modes']=dict(selected_modes)
    else: draft.pop('character_modes',None)
    if narrator_mode is not None:
        if narrator_mode=='nvl': draft['narrator_mode']='nvl'
        else: draft.pop('narrator_mode',None)
    for section in draft['sections']:
        for row in section['rows']:
            row['character'] = renames.get(row['character'],row['character'])
    validate(draft)
    data.clear()
    data.update(draft)
