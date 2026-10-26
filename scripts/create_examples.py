"""Create only authored, localized demo projects, with stable IDs and no OS fonts."""
import copy
import hashlib
import shutil
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from adv_editor.core import Database,export_rpy,export_excel

TEXT={
 'zh_TW':dict(names=['秋','美'],chapter='第一章',opening='相遇',greeting='問候',hello='你好，{b}世界{/b}！',wait='等一下{w=0.5}，一起走吧。',narration='午後的陽光灑落。',click='先顯示前半句。{w}{b}點擊後再顯示後半句。{/b}',prompt='你要怎麼做？',choices=['跟她打招呼','再看一次開場'],note='微笑',background='切換背景'),
 'zh_CN':dict(names=['秋','美'],chapter='第一章',opening='相遇',greeting='问候',hello='你好，{b}世界{/b}！',wait='等一下{w=0.5}，一起走吧。',narration='午后的阳光洒落。',click='先显示前半句。{w}{b}点击后再显示后半句。{/b}',prompt='你要怎么做？',choices=['跟她打招呼','再看一次开场'],note='微笑',background='切换背景'),
 'ja':dict(names=['アキ','メイ'],chapter='第1章',opening='出会い',greeting='あいさつ',hello='こんにちは、{b}世界{/b}！',wait='ちょっと待って{w=0.5}、一緒に行こう。',narration='午後の日差しが差し込む。',click='まず前半を表示します。{w}{b}クリックすると後半が表示されます。{/b}',prompt='どうしますか？',choices=['彼女にあいさつする','冒頭をもう一度見る'],note='笑顔',background='背景を切り替え'),
 'en':dict(names=['Aki','Mei'],chapter='Chapter 1',opening='First meeting',greeting='Greeting',hello='Hello, {b}world{/b}!',wait='Wait{w=0.5}, let’s go together.',narration='The afternoon sunlight streams in.',click='Show the first half.{w}{b}Click to reveal the second half.{/b}',prompt='What will you do?',choices=['Say hello to her','Replay the opening'],note='Smile',background='Change background')}


def localized_project(code):
    t=TEXT[code]
    def row(rid,cid,text,note=''): return dict(id=rid,character=cid,text=text,note=note)
    return dict(characters=dict(zip(['aki','mei'],t['names'])),character_colors={'aki':'#e5b5a5','mei':'#b0c9ed'},fonts={},images={},sections=[
        dict(id='opening',chapter=t['chapter'],name=t['opening'],call='greeting',rows=[row('d_sample_001','aki',t['hello'],t['note']),row('d_sample_002','mei',t['wait'])]),
        dict(id='greeting',chapter=t['chapter'],name=t['greeting'],call='',rows=[row('d_sample_003','',t['narration'])])])


def create_examples(destination):
    destination=Path(destination)
    image_source=Path(__file__).resolve().parents[1]/'examples'/'branches_assets'/'images'/'image_5f79e3ef605c06ba.png'
    raw=image_source.read_bytes()
    filename='image_'+hashlib.sha256(raw).hexdigest()[:16]+'.png'
    tag=Path(filename).stem.replace('image_','adv_image_')
    for code,t in TEXT.items():
        folder=destination/code;folder.mkdir(parents=True,exist_ok=True)
        data=localized_project(code)
        path=folder/'sample.advdb'
        db=Database(path);db.save(data);db.close()
        export_excel(data,folder/'sample.xlsx')
        branch=copy.deepcopy(data)
        branch['sections'][0]['call']=''
        branch['images'][filename]=tag
        branch['sections'][0]['rows'][0]['text']=t['click']
        branch['sections'][0]['rows'].insert(0,dict(id='d_stage_001',character='',text=tag,note=t['background'],kind='scene',transition='fade'))
        branch['sections'][0]['rows'].append(dict(id='d_menu_001',character='',text=t['prompt'],note='',kind='menu',choices=[dict(text=t['choices'][0],target='greeting'),dict(text=t['choices'][1],target='opening')]))
        project=folder/'branches.advdb'
        assets=folder/'branches_assets'/'images';assets.mkdir(parents=True,exist_ok=True);(assets/filename).write_bytes(raw)
        db=Database(project);db.save(branch);db.close()
        export_excel(branch,folder/'branches.xlsx',project)
        export_rpy(branch,folder/'renpy_game',project)
    (destination/'README.md').write_text('# Example projects\n\nChoose `zh_TW`, `zh_CN`, `ja` or `en`, then open `sample.advdb` or `branches.advdb`.\n\nKeep each project beside its matching `_assets` folder. Use Save as before editing a bundled demo.\nThe same permanent dialogue IDs are intentionally used in each language version.\nBackground images are original solid-color placeholders. No operating-system fonts are included.\n',encoding='utf-8')


if __name__=='__main__': create_examples(sys.argv[1] if len(sys.argv)>1 else 'examples/localized')
