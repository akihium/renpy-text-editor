from .i18n import tr
import re
import copy
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QWidget, QColorDialog, QDialogButtonBox, QLabel, QMessageBox, QComboBox)
from .core import identifier


class ColorField(QWidget):
    def __init__(self,color='',parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(2,2,2,2)
        self.input = QLineEdit(color)
        self.input.setPlaceholderText(tr('#RRGGBB（留空使用預設）'))
        self.button = QPushButton(tr('選色…'))
        self.button.clicked.connect(self.choose)
        self.input.textChanged.connect(self.update_color)
        layout.addWidget(self.input)
        layout.addWidget(self.button)
        self.update_color()

    def update_color(self):
        text = self.input.text().strip()
        self.button.setStyleSheet('background-color:'+text+';' if re.fullmatch(r'#[0-9a-fA-F]{6}',text) else '')

    def choose(self):
        color = QColorDialog.getColor(QColor(self.input.text() or '#ffffff'),self,tr('選擇角色顏色'))
        if color.isValid(): self.input.setText(color.name())


def mode_combo(mode='adv'):
    combo=QComboBox()
    combo.addItem(tr('ADV（逐句對話）'),'adv')
    combo.addItem(tr('NVL（整頁文字）'),'nvl')
    combo.setCurrentIndex(max(0,combo.findData(mode)))
    return combo


class CharacterDialog(QDialog):
    def __init__(self,data,parent=None):
        super().__init__(parent)
        self.source_data=copy.deepcopy(data)
        self.setWindowTitle(tr('角色管理'))
        self.resize(980,480)
        self.used = {r['character'] for s in data['sections'] for r in s['rows'] if r['character']}
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(tr('可修改代號、顯示名稱與顏色。儲存時檢查重名，並同步更新所有台詞的角色引用。')))
        self.table = QTableWidget(0,4)
        self.table.setHorizontalHeaderLabels([tr('代號（可改名）'),tr('實際顯示名字'),tr('角色顏色'),tr('文字模式')])
        self.table.setColumnWidth(0,150)
        self.table.setColumnWidth(1,180)
        self.table.setColumnWidth(2,280)
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)
        for cid,name in data['characters'].items(): self.add_row(cid,name,data.get('character_colors',{}).get(cid,''),data.get('character_modes',{}).get(cid,'adv'))
        narration=QHBoxLayout()
        narration.addWidget(QLabel(tr('旁白文字模式')))
        self.narrator_mode=mode_combo(data.get('narrator_mode','adv'))
        narration.addWidget(self.narrator_mode)
        narration.addStretch()
        layout.addLayout(narration)
        note=QLabel(tr('NVL 會在同一頁累積多段文字，請在適當位置插入「NVL 清頁」。'))
        note.setWordWrap(True);layout.addWidget(note)
        controls = QHBoxLayout()
        for title,fn in [(tr('新增角色'),lambda:self.add_row()),(tr('刪除選取角色'),self.delete_row)]:
            button = QPushButton(title)
            button.clicked.connect(fn)
            controls.addWidget(button)
        controls.addStretch()
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save|QDialogButtonBox.StandardButton.Cancel)
        buttons.button(QDialogButtonBox.StandardButton.Save).setText(tr('儲存'))
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText(tr('取消'))
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        controls.addWidget(buttons)
        layout.addLayout(controls)

    def add_row(self,cid='',name='',color='',mode='adv'):
        row = self.table.rowCount()
        self.table.insertRow(row)
        item = QTableWidgetItem(cid)
        item.setData(Qt.ItemDataRole.UserRole,cid)
        self.table.setItem(row,0,item)
        self.table.setItem(row,1,QTableWidgetItem(name))
        self.table.setCellWidget(row,2,ColorField(color))
        self.table.setCellWidget(row,3,mode_combo(mode))
        self.table.setRowHeight(row,42)
        self.table.setCurrentCell(row,0)

    def delete_row(self):
        row = self.table.currentRow()
        if row < 0: return
        if (self.table.item(row,0).data(Qt.ItemDataRole.UserRole) or self.table.item(row,0).text()) in self.used:
            QMessageBox.warning(self,tr('角色仍在使用'),tr('不能刪除使用中的角色。'))
            return
        self.table.removeRow(row)

    def renames(self):
        return {self.table.item(row,0).data(Qt.ItemDataRole.UserRole):self.table.item(row,0).text().strip()
                for row in range(self.table.rowCount()) if self.table.item(row,0).data(Qt.ItemDataRole.UserRole)}

    def modes(self):
        return {self.table.item(row,0).text().strip():'nvl' for row in range(self.table.rowCount()) if self.table.cellWidget(row,3).currentData()=='nvl'}

    def values(self):
        chars,colors = {},{}
        for row in range(self.table.rowCount()):
            cid = self.table.item(row,0).text().strip()
            identifier(cid)
            if cid in chars: raise ValueError(tr('角色代號重複：')+cid)
            chars[cid] = self.table.item(row,1).text()
            color = self.table.cellWidget(row,2).input.text().strip()
            if color:
                if not re.fullmatch(r'#[0-9a-fA-F]{6}',color): raise ValueError(tr('顏色請輸入 #RRGGBB，例如 #ffcc00'))
                colors[cid] = color.lower()
        mapping = self.renames()
        if {mapping.get(cid,cid) for cid in self.used}-set(chars): raise ValueError(tr('不能刪除使用中的角色代號'))
        return chars,colors

    def accept(self):
        try:
            chars,colors=self.values()
            from .character_ops import update_characters
            update_characters(copy.deepcopy(self.source_data),chars,colors,self.renames(),self.modes(),self.narrator_mode.currentData())
        except ValueError as error:
            QMessageBox.warning(self,tr('請修正角色資料'),str(error))
            return
        super().accept()
