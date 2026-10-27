"""Local project creation, history and writable demo copies."""
import hashlib
import json
import shutil
import sys
from pathlib import Path
from PySide6.QtCore import QStandardPaths
from .assets import asset_folder, copy_assets
from .core import Database, new_row, validate
from .i18n import LANGUAGES, tr
from .preferences import settings


def recent_projects():
    try:
        paths = json.loads(settings().value('recent_projects', '[]'))
    except (TypeError, ValueError):
        paths = []
    if not isinstance(paths, list):
        return []
    return [str(Path(p)) for p in paths if isinstance(p, str) and Path(p).is_file()][:12]


def remember_project(path):
    path = str(Path(path).resolve())
    paths = [path] + [p for p in recent_projects() if p != path]
    settings().setValue('recent_projects', json.dumps(paths[:12]))
    settings().setValue('project_directory', str(Path(path).parent))


def default_directory():
    path = Path(settings().value('project_directory', str(Path.home())))
    return str(path if path.is_dir() else Path.home())


def create_project(folder):
    folder = Path(folder).resolve()
    if not folder.is_dir():
        raise ValueError(tr('請先選擇專案資料夾。'))
    path = folder / (folder.name + '.advdb')
    if path.exists():
        raise FileExistsError(tr('這個資料夾已有同名專案，請開啟原專案或選擇另一個資料夾。'))
    data = dict(characters={}, character_colors={}, fonts={}, images={}, sections=[
        dict(id='opening', chapter=tr('第一章'), name=tr('開場'), call='', rows=[new_row()])])
    db = Database(path)
    try:
        db.save(data)
        asset_folder(path).mkdir(parents=True, exist_ok=True)
    finally:
        db.close()
    remember_project(path)
    return path


def example_root():
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS) / 'examples'
    return Path(__file__).resolve().parents[1] / 'examples' / 'localized'


def copy_example(language, kind='sample', destination=None):
    if language not in LANGUAGES or kind not in ('sample', 'branches', 'nvl'):
        raise ValueError('Invalid example selection')
    source = example_root() / language / (kind + '.advdb')
    if not source.is_file():
        raise FileNotFoundError(tr('找不到內建示例：') + str(source))
    if destination is None:
        destination = Path(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppLocalDataLocation)) / 'Examples'
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    # Always create a fresh working copy so experiments never alter bundled demos.
    stem = kind + '-' + language
    folder = destination / stem
    index = 2
    while folder.exists():
        folder = destination / (stem + '-' + str(index))
        index += 1
    folder.mkdir()
    target = folder / (kind + '.advdb')
    try:
        shutil.copyfile(source, target)
        db = Database(target)
        try:
            data = db.load()
            validate(data)
        finally:
            db.close()
        copy_assets(data, source, target)
        asset_folder(target).mkdir(parents=True, exist_ok=True)
    except Exception:
        shutil.rmtree(folder)
        raise
    remember_project(target)
    return target


def height_key(path):
    return 'row_heights/' + hashlib.sha256(str(Path(path).resolve()).encode()).hexdigest()


def load_heights(path):
    try:
        values = json.loads(settings().value(height_key(path), '{}'))
        if not isinstance(values, dict):
            return {}
        return {rid: h for rid, h in values.items() if isinstance(rid, str) and type(h) is int and 32 <= h <= 2000}
    except (TypeError, ValueError):
        return {}


def save_heights(path, heights):
    settings().setValue(height_key(path), json.dumps(heights))
