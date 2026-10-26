from .i18n import tr
import copy
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel,
    QLineEdit, QComboBox, QDialogButtonBox, QPushButton, QTableWidget, QTableWidgetItem,
    QAbstractItemView, QMessageBox, QInputDialog)
from .core import validate
from .section_ops import (available_id, update_section, duplicate_sections,
                          delete_sections, merge_sections)


class SectionForm(QDialog):
    def __init__(self,data,section=None,parent=None):
        super().__init__(parent)
        self.data = data
        self.original_id = section['id'] if section else None
        self.result_id = None
        self.setWindowTitle(tr('編輯章節／段落') if section else tr('新增章節／段落'))
        self.resize(560,300)
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.chapter = QComboBox()
        self.chapter.setEditable(True)
        self.chapter.addItems(list(dict.fromkeys(s['chapter'] for s in data['sections'])))
        self.name = QLineEdit()
        self.sid = QLineEdit(available_id(data))
        self.sid.setPlaceholderText(tr('例如 chapter01_opening；只能使用英數字與底線'))
        self.label_preview = QLabel()
        self.sid.textChanged.connect(lambda value:self.label_preview.setText('Ren’Py label：adv_'+value))
        self.target = QComboBox()
        self.target.addItem(tr('無，直接 return'),'')
        for s in data['sections']:
            if s['id'] != self.original_id:
                self.target.addItem(s['name']+' ['+s['id']+']',s['id'])
        if section:
            self.chapter.setCurrentText(section['chapter'])
            self.name.setText(section['name'])
            self.sid.setText(section['id'])
            self.target.setCurrentIndex(max(0,self.target.findData(section['call'])))
        self.label_preview.setText('Ren’Py label：adv_'+self.sid.text())
        form.addRow(tr('章節（可直接輸入新名稱）'),self.chapter)
        form.addRow(tr('段落顯示名稱'),self.name)
        form.addRow(tr('英文段落 ID（不含 adv_）'),self.sid)
        form.addRow('',self.label_preview)
        form.addRow(tr('段落結尾 call'),self.target)
        layout.addLayout(form)
        note = QLabel(tr('修改英文 ID 會更新專案內的 call；手寫 .rpy 的引用請同步修改。'))
        note.setWordWrap(True)
        layout.addWidget(note)
        self.error = QLabel()
        self.error.setStyleSheet('color:#bd3535')
        self.error.setWordWrap(True)
        layout.addWidget(self.error)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save|QDialogButtonBox.StandardButton.Cancel)
        buttons.button(QDialogButtonBox.StandardButton.Save).setText(tr('確定'))
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText(tr('取消'))
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def accept(self):
        try:
            self.result_id = update_section(self.data,self.original_id,self.sid.text().strip(),
                self.chapter.currentText(),self.name.text(),self.target.currentData())
        except ValueError as error:
            self.error.setText(str(error))
            return
        super().accept()


class SectionDialog(QDialog):
    def __init__(self,data,current_id,parent=None):
        super().__init__(parent)
        self.data = copy.deepcopy(data)
        self.current_id = current_id
        self.setWindowTitle(tr('章節／段落管理'))
        self.resize(1040,540)
        layout = QVBoxLayout(self)
        description = QLabel(tr('章節按名稱分組。可多選段落複製、刪除、合併或移至其他章節；按「套用」才會修改專案，套用後可復原。'))
        description.setWordWrap(True)
        layout.addWidget(description)
        self.table = QTableWidget(0,5)
        self.table.setHorizontalHeaderLabels([tr('章節'),tr('段落名稱'),tr('英文段落 ID'),tr('台詞數'),tr('結尾 call')])
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        for col,width in enumerate([160,210,240,70]): self.table.setColumnWidth(col,width)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.cellDoubleClicked.connect(lambda row,col:self.edit_section())
        layout.addWidget(self.table)
        bar = QHBoxLayout()
        self.buttons = {}
        for title,callback in [(tr('新增段落'),self.add_section),(tr('編輯名稱／ID'),self.edit_section),(tr('複製'),self.duplicate),(tr('刪除'),self.delete),(tr('合併選取'),self.merge),(tr('變更章節'),self.assign_chapter),(tr('上移'),lambda:self.move(-1)),(tr('下移'),lambda:self.move(1))]:
            button = QPushButton(title)
            button.clicked.connect(callback)
            bar.addWidget(button)
            self.buttons[title] = button
        layout.addLayout(bar)
        help_text = QLabel(tr('合併順序依表格由上到下，保留第一段的名稱／ID 和最後一段的 call。其他段的外部引用改指向第一段。刪除會清除指向被刪段落的 call。'))
        help_text.setWordWrap(True)
        layout.addWidget(help_text)
        self.status = QLabel()
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save|QDialogButtonBox.StandardButton.Cancel)
        buttons.button(QDialogButtonBox.StandardButton.Save).setText(tr('套用'))
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText(tr('取消'))
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.refresh([current_id])

    def selected_ids(self):
        return [self.data['sections'][row]['id'] for row in sorted({i.row() for i in self.table.selectedIndexes()})]

    def refresh(self,selected=()):
        self.table.setRowCount(len(self.data['sections']))
        self.table.clearSelection()
        from PySide6.QtCore import QItemSelectionModel
        for row,section in enumerate(self.data['sections']):
            for col,value in enumerate([section['chapter'],section['name'],section['id'],str(len(section['rows'])),section['call'] or 'return']):
                self.table.setItem(row,col,QTableWidgetItem(value))
            if section['id'] in selected:
                self.table.selectionModel().select(self.table.model().index(row,0),QItemSelectionModel.SelectionFlag.Select|QItemSelectionModel.SelectionFlag.Rows)
        if selected: self.current_id = selected[0]

    def run(self,operation):
        try: operation()
        except ValueError as error: self.status.setText(tr('未完成：')+str(error))

    def add_section(self):
        form = SectionForm(self.data,parent=self)
        if form.exec():
            self.refresh([form.result_id])
            self.status.setText(tr('已新增段落；按套用儲存到專案。'))

    def edit_section(self):
        selected = self.selected_ids()
        if len(selected) != 1:
            self.status.setText(tr('請選取一個段落編輯。'))
            return
        section = next(s for s in self.data['sections'] if s['id'] == selected[0])
        form = SectionForm(self.data,section,self)
        if form.exec(): self.refresh([form.result_id])

    def duplicate(self):
        def operation():
            copied = duplicate_sections(self.data,self.selected_ids())
            self.refresh(copied)
            self.status.setText(tr('已複製 {count} 個段落，副本使用新的永久台詞 ID。',count=len(copied)))
        self.run(operation)

    def delete(self):
        def operation():
            selected = self.selected_ids()
            if not selected: raise ValueError(tr('請先選取段落。'))
            count = sum(s['call'] in selected for s in self.data['sections'] if s['id'] not in selected)
            delete_sections(self.data,selected)
            self.refresh([self.data['sections'][0]['id']])
            self.status.setText(tr('已刪除 {count} 個段落，清除 {refs} 個 call 引用。尚未套用，可取消。',count=len(selected),refs=count))
        self.run(operation)

    def merge(self):
        def operation():
            selected = self.selected_ids()
            sid = merge_sections(self.data,selected)
            self.refresh([sid])
            self.status.setText(tr('已合併 {count} 個段落，保留既有台詞 ID；手寫 label 引用請同步修改。',count=len(selected)))
        self.run(operation)

    def assign_chapter(self):
        selected = self.selected_ids()
        if not selected:
            self.status.setText(tr('請先選取要變更章節的段落。'))
            return
        value,ok = QInputDialog.getItem(self,tr('變更章節'),tr('選擇章節或輸入新章節名稱'),list(dict.fromkeys(s['chapter'] for s in self.data['sections'])),0,True)
        if ok and value.strip():
            for section in self.data['sections']:
                if section['id'] in selected: section['chapter'] = value.strip()
            self.refresh(selected)

    def move(self,delta):
        selected = self.selected_ids()
        if not selected: return
        sections = self.data['sections']
        indices = range(len(sections)) if delta < 0 else range(len(sections)-1,-1,-1)
        for row in indices:
            target = row+delta
            if sections[row]['id'] in selected and 0 <= target < len(sections) and sections[target]['id'] not in selected:
                sections[row],sections[target] = sections[target],sections[row]
        self.refresh(selected)

    def accept(self):
        try: validate(self.data)
        except ValueError as error:
            self.status.setText(str(error))
            return
        super().accept()
