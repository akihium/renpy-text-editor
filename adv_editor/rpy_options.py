"""Ren'Py output location controls, independent of the project database."""
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QHBoxLayout, QLineEdit,
    QComboBox, QPushButton, QLabel, QFileDialog, QDialogButtonBox)
from .i18n import tr
from .core import valid_folder_name


class RenPyExportDialog(QDialog):
    def __init__(self, directory, name='renpy_export', parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr('匯出 Ren’Py'))
        self.resize(660, 310)
        layout = QVBoxLayout(self)
        form = QFormLayout()
        destination = QHBoxLayout()
        self.directory = QLineEdit(str(directory))
        browse = QPushButton(tr('選擇資料夾…'))
        browse.clicked.connect(self.browse)
        destination.addWidget(self.directory,1)
        destination.addWidget(browse)
        form.addRow(tr('儲存位置'),destination)
        self.mode = QComboBox()
        self.mode.addItem(tr('建立自訂名稱的子資料夾'), 'subfolder')
        self.mode.addItem(tr('直接儲存在所選資料夾'), 'direct')
        form.addRow(tr('匯出方式'),self.mode)
        self.folder_name = QLineEdit(name)
        form.addRow(tr('子資料夾名稱'),self.folder_name)
        layout.addLayout(form)
        self.preview = QLabel()
        self.preview.setWordWrap(True)
        self.preview.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(self.preview)
        note = QLabel(tr('輸出 characters.rpy、dialogue.rpy 及所需素材。使用 Ren’Py 時，請選擇 game 資料夾或其中的資料夾。'))
        note.setWordWrap(True)
        layout.addWidget(note)
        self.error = QLabel()
        self.error.setStyleSheet('color:#bd3535')
        layout.addWidget(self.error)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.button(QDialogButtonBox.StandardButton.Save).setText(tr('匯出'))
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.mode.currentIndexChanged.connect(self.update_preview)
        self.directory.textChanged.connect(self.update_preview)
        self.folder_name.textChanged.connect(self.update_preview)
        self.update_preview()

    def browse(self):
        folder = QFileDialog.getExistingDirectory(self,tr('選擇匯出資料夾'),self.directory.text())
        if folder:
            self.directory.setText(folder)

    @property
    def subfolder(self):
        return self.folder_name.text().strip() if self.mode.currentData() == 'subfolder' else ''

    def update_preview(self):
        self.folder_name.setEnabled(self.mode.currentData() == 'subfolder')
        self.preview.setText(tr('實際輸出位置：') + str(Path(self.directory.text()).expanduser() / self.subfolder))
        self.error.clear()

    def accept(self):
        if not self.directory.text().strip() or not Path(self.directory.text()).expanduser().is_dir():
            self.error.setText(tr('請選擇已存在的儲存資料夾。'))
            return
        if self.mode.currentData() == 'subfolder' and not valid_folder_name(self.subfolder):
            self.error.setText(tr('請輸入有效的子資料夾名稱，且不要包含斜線或特殊路徑字元。'))
            return
        super().accept()
