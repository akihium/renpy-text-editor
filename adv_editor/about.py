"""Offline application credits and the bundled project license."""
import html
from pathlib import Path
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QTextBrowser, QDialogButtonBox
from . import __version__
from .i18n import APP_NAME, tr

REPOSITORY_URL = 'https://github.com/akihium/renpy-text-editor'
AUTHOR = 'Akihium'


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr('關於 / About'))
        self.resize(660, 620)
        layout = QVBoxLayout(self)
        title = QLabel(tr(APP_NAME))
        title.setStyleSheet('font-size: 22px; font-weight: 600;')
        layout.addWidget(title)
        details = QLabel(
            html.escape(tr('版本：{version}',version=__version__)) + '<br>' +
            html.escape(tr('作者：{author}',author=AUTHOR)) + '<br>' +
            tr('授權：MIT') + '<br><br>' +
            'GitHub: <a href="' + REPOSITORY_URL + '">akihium/renpy-text-editor</a>')
        details.setOpenExternalLinks(True)
        details.setWordWrap(True)
        layout.addWidget(details)
        license_text = (Path(__file__).parent / 'resources' / 'LICENSE.txt').read_text(encoding='utf-8')
        browser = QTextBrowser()
        browser.setHtml('<pre style="white-space: pre-wrap;">' + html.escape(license_text) + '</pre>')
        layout.addWidget(browser, 1)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
