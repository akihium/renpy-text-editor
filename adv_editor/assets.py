"""Project-owned font files, independent of the source font's original location."""
from .i18n import tr
import hashlib
import re
import shutil
from pathlib import Path


def asset_folder(project_path):
    path = Path(project_path)
    return path.parent / (path.stem+'_assets')


def font_file(project_path,filename):
    if not re.fullmatch(r'font_[0-9a-f]{16}\.(ttf|otf)',filename):
        raise ValueError(tr('無效的專案字體檔名：')+filename)
    return asset_folder(project_path)/'fonts'/filename


def copy_fonts(data,source_project,target_project):
    pairs = []
    for filename in data.get('fonts',{}):
        source = font_file(source_project,filename)
        target = font_file(target_project,filename)
        if not source.is_file(): raise ValueError(tr('找不到專案字體，請還原素材資料夾：')+str(source))
        pairs.append((source,target))
    for source,target in pairs:
        target.parent.mkdir(parents=True,exist_ok=True)
        if source.resolve() != target.resolve(): shutil.copy2(source,target)


def import_font(source,project_path):
    from PySide6.QtGui import QFontDatabase
    source = Path(source)
    if source.suffix.lower() not in ('.ttf','.otf'):
        raise ValueError(tr('請選擇 TTF 或 OTF 字體。'))
    raw = source.read_bytes()
    font_id = QFontDatabase.addApplicationFontFromData(raw)
    families = QFontDatabase.applicationFontFamilies(font_id) if font_id >= 0 else []
    if not families: raise ValueError(tr('無法讀取字體，請選擇有效的 TTF 或 OTF 檔案。'))
    filename = 'font_'+hashlib.sha256(raw).hexdigest()[:16]+source.suffix.lower()
    destination = font_file(project_path,filename)
    destination.parent.mkdir(parents=True,exist_ok=True)
    if not destination.exists(): destination.write_bytes(raw)
    return filename,families[0]


_REGISTERED_FONTS={}


def register_fonts(data,project_path):
    from PySide6.QtGui import QFontDatabase
    from .richtext import FONT_FAMILIES
    FONT_FAMILIES.clear()
    missing = []
    for filename,family in data.get('fonts',{}).items():
        path = font_file(project_path,filename)
        key=str(path.resolve())
        loaded=_REGISTERED_FONTS.get(key,[])
        if not loaded:
            font_id = QFontDatabase.addApplicationFont(str(path)) if path.is_file() else -1
            loaded = QFontDatabase.applicationFontFamilies(font_id) if font_id >= 0 else []
            if loaded: _REGISTERED_FONTS[key]=loaded
        if not loaded: missing.append(filename)
        FONT_FAMILIES['adv_generated/fonts/'+filename] = loaded[0] if loaded else family
    return missing


def image_file(project_path,filename):
    if not re.fullmatch(r'image_[0-9a-f]{16}\.(png|jpg|jpeg|webp)',filename):
        raise ValueError(tr('無效的專案圖片檔名：')+filename)
    return asset_folder(project_path)/'images'/filename


def import_image(source,project_path):
    from PySide6.QtGui import QImageReader
    source=Path(source)
    if source.suffix.lower() not in ('.png','.jpg','.jpeg','.webp') or not QImageReader(str(source)).canRead():
        raise ValueError(tr('請選擇有效的 PNG、JPEG 或 WebP 圖片。'))
    raw=source.read_bytes()
    filename='image_'+hashlib.sha256(raw).hexdigest()[:16]+source.suffix.lower()
    destination=image_file(project_path,filename)
    destination.parent.mkdir(parents=True,exist_ok=True)
    if not destination.exists(): destination.write_bytes(raw)
    return filename,Path(filename).stem.replace('image_','adv_image_')


def copy_assets(data,source_project,target_project):
    pairs=[]
    for category,resolver in [('fonts',font_file),('images',image_file)]:
        for filename in data.get(category,{}):
            source,target=resolver(source_project,filename),resolver(target_project,filename)
            if not source.is_file(): raise ValueError(tr('找不到專案素材：')+str(source))
            pairs.append((source,target))
    for source,target in pairs:
        target.parent.mkdir(parents=True,exist_ok=True)
        if source.resolve()!=target.resolve(): shutil.copy2(source,target)
