"""Assemble public docs, localized demos and third-party license notices."""
import json
import shutil
import sys
from importlib.metadata import distributions
from pathlib import Path
try:
    from .create_examples import create_examples
except ImportError:
    from create_examples import create_examples


def prepare(destination):
    destination=Path(destination);destination.mkdir(parents=True,exist_ok=True)
    root=Path(__file__).resolve().parents[1]
    for name in ['README.md','CHANGELOG.md','LICENSE','THIRD_PARTY_NOTICES.md']:
        shutil.copy2(root/name,destination/name)
    for name in ['quickstart.zh-TW.md','quickstart.zh-CN.md','quickstart.ja.md','quickstart.en.md']:
        folder=destination/'docs';folder.mkdir(exist_ok=True);shutil.copy2(root/'docs'/name,folder/name)
    create_examples(destination/'examples')
    from adv_editor import __version__
    if 'preview' in __version__ and (root/'docs'/'preview.zh-TW.md').is_file():
        shutil.copy2(root/'docs'/'preview.zh-TW.md',destination/'README-PREVIEW.zh-TW.md')
    screenshots=destination/'screenshots';screenshots.mkdir(exist_ok=True)
    for name in ['public-en.png','public-ja.png','public-startup-en.png']:
        shutil.copy2(root/'screenshots'/name,screenshots/name)
    licenses=destination/'LICENSES';licenses.mkdir(exist_ok=True)
    for source in (root/'LICENSES').glob('*.txt'): shutil.copy2(source,licenses/source.name)
    for name in ['LICENSE.txt','LICENSE']:
        source=Path(sys.base_prefix)/name
        if source.is_file(): shutil.copy2(source,licenses/'Python-LICENSE.txt');break
    manifest=[]
    for dist in sorted(distributions(),key=lambda d:d.metadata['Name'].lower()):
        name=dist.metadata['Name'];version=dist.version
        if name.lower() in ['pytest','pluggy','iniconfig','pygments','pip']: continue
        entry={'name':name,'version':version,'license':dist.metadata.get('License-Expression') or dist.metadata.get('License','See upstream'),'files':[]}
        for relative in dist.files or []:
            value=str(relative)
            basename=Path(value).name.lower()
            if not any(key in basename for key in ['license','copying','copyright','notice']): continue
            source=dist.locate_file(relative)
            if not source.is_file() or source.suffix.lower() not in ('.txt','.md','.rst',''): continue
            target=licenses/name/Path(value)
            target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
            entry['files'].append(target.relative_to(licenses).as_posix())
        manifest.append(entry)
    (licenses/'DEPENDENCIES.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')


if __name__=='__main__': prepare(sys.argv[1])
