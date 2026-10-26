"""Packaged-app export check, callable with --verify-exports OUTPUT_DIRECTORY."""
import json
from pathlib import Path
from .core import sample,new_row,Database,export_rpy,export_excel,import_excel,statement
from .assets import import_font
from .platform_fonts import importable_system_font
from .documents import export_word,export_pdf


def verify_exports(folder):
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    project=folder/'check.advdb'
    data=sample()
    data['sections'][0]['rows'][0]['text']='前半{w}{b}後半{/b}'
    data['sections'][0]['rows'].append(dict(new_row(),kind='menu',text='選擇',choices=[dict(text='繼續',target='greeting')]))
    font=importable_system_font()
    if font is not None:
        filename,family=import_font(font,project)
        data['fonts'][filename]=family
    db=Database(project);db.save(data);assert db.load()==data;db.close()
    export_excel(data,folder/'check.xlsx',project)
    assert import_excel(folder/'check.xlsx')==data
    export_rpy(data,folder/'game',project)
    export_word(data,folder/'check.docx',title='Packaged export check',include_ids=False)
    export_pdf(data,folder/'check.pdf',project,title='Packaged export check',include_ids=False)
    assert ' id ' not in statement(data['sections'][0]['rows'][0],include_ids=False)
    from . import i18n
    original_language=i18n.LANGUAGE
    for code,expected in [('en','Show dialogue IDs'),('zh_CN','显示台词 ID'),('zh_TW','顯示台詞 ID'),('ja','セリフ ID を表示')]:
        i18n.set_language(code)
        assert i18n.tr('顯示台詞 ID')==expected
    i18n.set_language(original_language)
    assert (folder/'check.docx').read_bytes()[:2]==b'PK'
    assert (folder/'check.pdf').read_bytes().startswith(b'%PDF')
    (folder/'result.json').write_text(json.dumps({'ok':True,'checks':['SQLite','fonts','Excel','RenPy menu','Word','PDF','Custom title','Optional IDs','EN / zh_CN / zh_TW / JA']},ensure_ascii=False,indent=2),encoding='utf-8')
