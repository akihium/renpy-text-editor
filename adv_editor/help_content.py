"""Localized offline instructions with platform-appropriate shortcut names."""
import sys
from pathlib import Path
from . import i18n


def help_html():
    source=Path(__file__).parent/'resources'/('help.'+i18n.LANGUAGE+'.html')
    return source.read_text(encoding='utf-8').replace('{mod}','⌘' if sys.platform=='darwin' else 'Ctrl')
