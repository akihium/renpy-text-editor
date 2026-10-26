import copy
from .core import validate


def update_characters(data,characters,colors,renames):
    draft = copy.deepcopy(data)
    draft['characters'] = dict(characters)
    draft['character_colors'] = dict(colors)
    for section in draft['sections']:
        for row in section['rows']:
            row['character'] = renames.get(row['character'],row['character'])
    validate(draft)
    data.update(draft)
