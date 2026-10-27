"""Project launcher with language selection and safe, editable examples."""
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QListWidget, QListWidgetItem, QFileDialog, QMessageBox)
from . import i18n, __version__
from .i18n import tr, APP_NAME, LANGUAGES, set_language, retranslate
from .projects import settings, recent_projects, default_directory, create_project, copy_example


def label(text):
    widget = QLabel(tr(text))
    widget.setProperty('_i18n_text', text)
    return widget


def button(text, callback):
    widget = QPushButton(tr(text))
    widget.setProperty('_i18n_text', text)
    widget.clicked.connect(callback)
    return widget


class StartupDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.project_path = None
        set_language(settings().value('language', 'zh_TW'))
        self.setWindowTitle(tr(APP_NAME))
        self.setProperty('_i18n_windowTitle', APP_NAME)
        self.resize(760, 570)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)
        title = label(APP_NAME)
        title.setStyleSheet('font-size: 25px; font-weight: 600;')
        layout.addWidget(title)
        layout.addWidget(QLabel(__version__))
        languages = QHBoxLayout()
        languages.addWidget(QLabel('Language /'))
        languages.addWidget(label('介面語言'))
        self.language = QComboBox()
        self.language.setProperty('project_content', True)
        for code, name in LANGUAGES.items():
            self.language.addItem(name, code)
        self.language.setCurrentIndex(self.language.findData(i18n.LANGUAGE))
        self.language.currentIndexChanged.connect(self.change_language)
        languages.addWidget(self.language)
        languages.addStretch()
        layout.addLayout(languages)
        actions = QHBoxLayout()
        self.new_button = button('新增專案', self.new_project)
        self.new_button.setDefault(True)
        self.open_button = button('開啟專案', self.open_project)
        actions.addWidget(self.new_button)
        actions.addWidget(self.open_button)
        layout.addLayout(actions)
        layout.addWidget(label('最近開啟的專案'))
        self.recent = QListWidget()
        self.recent.setProperty('project_content', True)
        self.recent.itemDoubleClicked.connect(self.open_recent)
        layout.addWidget(self.recent, 1)
        self.recent_button = button('開啟選取的專案', self.open_recent)
        layout.addWidget(self.recent_button)
        self.recent.itemSelectionChanged.connect(lambda: self.recent_button.setEnabled(bool(self.recent.selectedItems())))
        self.empty = label('尚未開啟過專案。可以新建專案，或從下方 Sample 開始。')
        self.empty.setWordWrap(True)
        layout.addWidget(self.empty)
        layout.addWidget(label('Sample · 示例'))
        examples = QHBoxLayout()
        self.sample_button = button('開啟台詞示例', lambda: self.open_example('sample'))
        self.branches_button = button('開啟分支／演出示例', lambda: self.open_example('branches'))
        examples.addWidget(self.sample_button)
        examples.addWidget(self.branches_button)
        layout.addLayout(examples)
        self.nvl_button = button('開啟 NVL 示例', lambda: self.open_example('nvl'))
        layout.addWidget(self.nvl_button)
        note = label('依目前語言開啟全新示例副本，可自由修改；修改後會出現在最近專案。')
        note.setWordWrap(True)
        layout.addWidget(note)
        self.refresh_recent()
        retranslate(self)

    def change_language(self, index):
        code = self.language.itemData(index)
        settings().setValue('language', code)
        set_language(code)
        retranslate(self)

    def refresh_recent(self):
        self.recent.clear()
        for path in recent_projects():
            item = QListWidgetItem(Path(path).stem + '\n' + path)
            item.setData(Qt.ItemDataRole.UserRole, path)
            item.setToolTip(path)
            self.recent.addItem(item)
        self.empty.setVisible(self.recent.count() == 0)
        self.recent_button.setEnabled(False)
        if self.recent.count():
            self.recent.setCurrentRow(0)

    def choose(self, path):
        if not Path(path).is_file():
            QMessageBox.warning(self, tr('操作未完成'), tr('找不到專案，可能已移動或刪除。'))
            self.refresh_recent()
            return
        self.project_path = str(path)
        self.accept()

    def open_recent(self, item=None):
        item = item if isinstance(item, QListWidgetItem) else self.recent.currentItem()
        if item:
            self.choose(item.data(Qt.ItemDataRole.UserRole))

    def open_project(self):
        path, _ = QFileDialog.getOpenFileName(self, tr('開啟專案'), default_directory(), tr('ADV 專案 (*.advdb)'))
        if path:
            self.choose(path)

    def new_project(self):
        folder = QFileDialog.getExistingDirectory(self, tr('選擇新專案資料夾（可建立新資料夾）'), default_directory())
        if not folder:
            return
        try:
            self.choose(create_project(folder))
        except Exception as error:
            QMessageBox.warning(self, tr('操作未完成'), str(error))

    def open_example(self, kind):
        try:
            self.choose(copy_example(self.language.currentData(), kind))
        except Exception as error:
            QMessageBox.warning(self, tr('操作未完成'), str(error))
