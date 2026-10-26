"""Use fonts installed on the host; never redistribute operating-system fonts."""
import os
import sys
from pathlib import Path


def windows_fonts():
    return Path(os.environ.get('WINDIR','C:/Windows'))/'Fonts'


def document_font_family():
    if sys.platform=='win32': return 'Microsoft JhengHei'
    if sys.platform=='darwin': return 'Arial Unicode MS'
    return 'Noto Sans CJK TC'


def pdf_font_candidates(bold=False):
    if sys.platform=='win32':
        names=['msjhbd.ttc','msyhbd.ttc','msjh.ttc','msyh.ttc','simsun.ttc'] if bold else ['msjh.ttc','msyh.ttc','simsun.ttc','arialuni.ttf']
        return [windows_fonts()/name for name in names]
    if sys.platform=='darwin':
        return [Path('/System/Library/Fonts/STHeiti Medium.ttc')] if bold else [Path('/System/Library/Fonts/Supplemental/Arial Unicode.ttf'),Path('/System/Library/Fonts/STHeiti Light.ttc')]
    return [Path('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')]


def importable_system_font():
    candidates=[windows_fonts()/'arial.ttf'] if sys.platform=='win32' else [Path('/System/Library/Fonts/Supplemental/Arial.ttf')]
    candidates.extend([Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')])
    return next((path for path in candidates if path.is_file()),None)
