from .i18n import tr
import copy
from PySide6.QtWidgets import (QDialog,QVBoxLayout,QHBoxLayout,QFormLayout,QLabel,QComboBox,
    QLineEdit,QPushButton,QTableWidget,QTableWidgetItem,QDialogButtonBox,QFileDialog,QCheckBox)
from .core import new_row,validate_action
from .assets import import_image

KINDS={'scene':'背景切換','show':'顯示圖片／角色','hide':'隱藏圖片／角色','transition':'轉場效果',
       'menu':'選項與分支','jump':'跳轉分支','call':'呼叫段落','return':'返回','nvl_clear':'NVL 清頁'}


class StageDialog(QDialog):
    def __init__(self,data,project_path,row=None,parent=None):
        super().__init__(parent)
        self.data=copy.deepcopy(data)
        self.project_path=project_path
        self.original=copy.deepcopy(row) if row else new_row()
        self.result_row=None
        self.setWindowTitle(tr('演出與分支設定'))
        self.resize(700,500)
        layout=QVBoxLayout(self)
        form=QFormLayout()
        self.kind=QComboBox()
        for key,title in KINDS.items(): self.kind.addItem(tr(title),key)
        form.addRow(tr('類型'),self.kind)
        self.value=QLineEdit(row['text'] if row else '')
        self.value.setPlaceholderText(tr('圖片標籤，例如 bg classroom；選項類型時可輸入提問文字'))
        form.addRow(tr('圖片標籤／提問'),self.value)
        self.transition=QComboBox()
        for title,key in [(tr('無轉場'),''),(tr('淡入淡出 dissolve'),'dissolve'),(tr('黑場淡入 fade'),'fade'),(tr('立即 None'),'None')]: self.transition.addItem(title,key)
        self.transition.setCurrentIndex(max(0,self.transition.findData(row.get('transition','') if row else '')))
        form.addRow(tr('轉場效果'),self.transition)
        self.target=QComboBox()
        for section in data['sections']: self.target.addItem(section['chapter']+' / '+section['name']+' ['+section['id']+']',section['id'])
        if row: self.target.setCurrentIndex(max(0,self.target.findData(row['text'])))
        form.addRow(tr('跳轉／呼叫目標'),self.target)
        self.effects=QComboBox()
        self.effects.addItems(['dissolve','fade','None'])
        if row: self.effects.setCurrentText(row['text'])
        form.addRow(tr('單獨轉場'),self.effects)
        layout.addLayout(form)
        self.import_button=QPushButton(tr('匯入背景／圖片…'))
        self.import_button.clicked.connect(self.import_background)
        layout.addWidget(self.import_button)
        self.nvl_menu=QCheckBox(tr('以 NVL 模式顯示選項'))
        self.nvl_menu.setChecked(row.get('nvl_menu',False) if row else False)
        self.nvl_menu.toggled.connect(lambda _: self.update_controls())
        layout.addWidget(self.nvl_menu)
        self.nvl_clear_after=QCheckBox(tr('選擇後清除 NVL 頁面'))
        self.nvl_clear_after.setChecked(row.get('nvl_clear_after',True) if row else True)
        layout.addWidget(self.nvl_clear_after)
        self.table=QTableWidget(0,2)
        self.table.setHorizontalHeaderLabels([tr('選項文字'),tr('選擇後跳轉的段落')])
        self.table.setColumnWidth(0,280)
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)
        bar=QHBoxLayout()
        self.add_button=QPushButton(tr('新增選項'))
        self.add_button.clicked.connect(lambda:self.add_choice())
        self.delete_button=QPushButton(tr('刪除選項'))
        self.delete_button.clicked.connect(lambda:self.table.removeRow(self.table.currentRow()) if self.table.currentRow()>=0 else None)
        bar.addWidget(self.add_button);bar.addWidget(self.delete_button);bar.addStretch()
        layout.addLayout(bar)
        help_label=QLabel(tr('分支直接使用既有段落；可先到「章節／段落管理」新增分支。背景圖片匯入後會跟隨專案保存。'))
        help_label.setWordWrap(True)
        layout.addWidget(help_label)
        self.error=QLabel();self.error.setWordWrap(True);self.error.setStyleSheet('color:#bd3535');layout.addWidget(self.error)
        buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Save|QDialogButtonBox.StandardButton.Cancel)
        buttons.button(QDialogButtonBox.StandardButton.Save).setText(tr('確定'))
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText(tr('取消'))
        buttons.accepted.connect(self.accept);buttons.rejected.connect(self.reject);layout.addWidget(buttons)
        for choice in (row.get('choices',[]) if row else []): self.add_choice(choice['text'],choice['target'])
        if not self.table.rowCount(): self.add_choice()
        self.kind.currentIndexChanged.connect(self.update_controls)
        self.kind.setCurrentIndex(max(0,self.kind.findData(row.get('kind','scene') if row else 'scene')))
        self.update_controls()

    def update_controls(self):
        kind=self.kind.currentData()
        self.value.setEnabled(kind in ('scene','show','hide','menu'))
        self.transition.setEnabled(kind in ('scene','show'))
        self.effects.setEnabled(kind=='transition')
        self.target.setEnabled(kind in ('jump','call'))
        self.import_button.setEnabled(kind in ('scene','show'))
        self.nvl_menu.setVisible(kind=='menu')
        self.nvl_clear_after.setVisible(kind=='menu' and self.nvl_menu.isChecked())
        for widget in (self.table,self.add_button,self.delete_button): widget.setVisible(kind=='menu')

    def add_choice(self,text='',target=''):
        row=self.table.rowCount();self.table.insertRow(row)
        self.table.setItem(row,0,QTableWidgetItem(text))
        combo=QComboBox()
        for section in self.data['sections']: combo.addItem(section['name']+' ['+section['id']+']',section['id'])
        combo.setCurrentIndex(max(0,combo.findData(target)))
        self.table.setCellWidget(row,1,combo)

    def import_background(self):
        path,_=QFileDialog.getOpenFileName(self,tr('匯入背景／圖片'),'',tr('圖片 (*.png *.jpg *.jpeg *.webp)'))
        if path:
            try:
                filename,tag=import_image(path,self.project_path)
                self.data.setdefault('images',{})[filename]=tag
                self.value.setText(tag)
            except Exception as error: self.error.setText(str(error))

    def accept(self):
        row={key:self.original[key] for key in ('id','character','text','note')}
        kind=self.kind.currentData()
        row['kind']=kind;row['character']=''
        row['text']=self.value.text().strip()
        if kind in ('jump','call'): row['text']=self.target.currentData()
        if kind in ('return','nvl_clear'): row['text']=''
        if kind=='transition': row['text']=self.effects.currentText()
        if kind in ('scene','show') and self.transition.currentData(): row['transition']=self.transition.currentData()
        if kind=='menu' and self.nvl_menu.isChecked():
            row['nvl_menu']=True;row['nvl_clear_after']=self.nvl_clear_after.isChecked()
        if kind=='menu': row['choices']=[dict(text=self.table.item(i,0).text(),target=self.table.cellWidget(i,1).currentData()) for i in range(self.table.rowCount())]
        try: validate_action(row,{s['id'] for s in self.data['sections']})
        except ValueError as error: self.error.setText(str(error));return
        self.result_row=row
        super().accept()
