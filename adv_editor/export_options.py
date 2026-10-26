from .i18n import tr
from PySide6.QtWidgets import (QDialog,QVBoxLayout,QFormLayout,QLineEdit,QCheckBox,
    QDialogButtonBox,QLabel)


class DocumentExportDialog(QDialog):
    def __init__(self,title,include_ids=False,parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr('文件匯出設定'))
        self.resize(520,180)
        layout=QVBoxLayout(self)
        form=QFormLayout()
        self.title_input=QLineEdit(title)
        self.title_input.setPlaceholderText(tr('輸入顯示在文件首頁的標題'))
        form.addRow(tr('文件標題'),self.title_input)
        layout.addLayout(form)
        self.include_ids=QCheckBox(tr('文件包含台詞 ID'))
        self.include_ids.setChecked(include_ids)
        layout.addWidget(self.include_ids)
        self.error=QLabel();self.error.setStyleSheet('color:#bd3535');layout.addWidget(self.error)
        buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Save|QDialogButtonBox.StandardButton.Cancel)
        buttons.button(QDialogButtonBox.StandardButton.Save).setText(tr('匯出'))
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText(tr('取消'))
        buttons.accepted.connect(self.accept);buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def accept(self):
        if not self.title_input.text().strip():
            self.error.setText(tr('請輸入文件標題。'))
            return
        super().accept()
