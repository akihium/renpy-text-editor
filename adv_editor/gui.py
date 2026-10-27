from __future__ import annotations
import copy
import csv
import html
import io
import re
from pathlib import Path
from PySide6.QtCore import Qt, QTimer, QEvent, QUrl
from PySide6.QtGui import QAction, QKeySequence, QTextDocument, QColor, QBrush, QDesktopServices
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QStyledItemDelegate, QPlainTextEdit, QComboBox,
    QFileDialog, QMessageBox, QInputDialog, QLineEdit, QPushButton, QLabel, QAbstractItemView,
    QStyle, QStyleOptionViewItem, QCheckBox, QSpinBox, QDoubleSpinBox, QColorDialog, QSizePolicy, QDialog, QTextBrowser, QDialogButtonBox)
from .i18n import tr,APP_NAME,LANGUAGES,set_language,retranslate
from . import i18n, __version__
from .about import AboutDialog
from .help_content import help_html
from .preferences import settings
from .core import Database, sample, new_row, uid, identifier, statement, export_rpy, export_excel, import_excel, label_name


from .richtext import RichCellEditor, load_source, TagRenderer, OBJECT
from .characters import CharacterDialog
from .sections import SectionDialog, SectionForm
from .stage import StageDialog, KINDS
from .assets import asset_folder, copy_assets, import_font, register_fonts
from .character_ops import update_characters
from .export_options import DocumentExportDialog
from .rpy_options import RenPyExportDialog
from .projects import (create_project, remember_project, default_directory, load_heights, save_heights)


def editor_source(editor):
    return editor.source() if isinstance(editor,RichCellEditor) else editor.toPlainText()


def editor_keypress(editor,event):
    key,mods = event.key(),event.modifiers()
    if mods & Qt.KeyboardModifier.ControlModifier and key in (Qt.Key.Key_B,Qt.Key.Key_I,Qt.Key.Key_U):
        editor.wrap({Qt.Key.Key_B:'b',Qt.Key.Key_I:'i',Qt.Key.Key_U:'u'}[key])
        return True
    if key in (Qt.Key.Key_Tab,Qt.Key.Key_Backtab):
        delta = -1 if key == Qt.Key.Key_Backtab or mods & Qt.KeyboardModifier.ShiftModifier else 1
        editor.window.finish_editor(editor,'tab',delta)
        return True
    if key in (Qt.Key.Key_Return,Qt.Key.Key_Enter):
        if mods & Qt.KeyboardModifier.ShiftModifier and editor.col == 2: editor.insertPlainText('\n')
        else: editor.window.finish_editor(editor,'enter',1)
        return True
    if event.matches(QKeySequence.StandardKey.Paste):
        value = QApplication.clipboard().text()
        if '\t' in value or ('\n' in value and editor.col != 2):
            editor.window.finish_editor(editor)
            editor.window.paste_grid(value,editor.row,editor.col)
            return True
    return False


class CellEditor(QPlainTextEdit):
    def __init__(self, window, row, col, parent):
        super().__init__(parent)
        self.window, self.row, self.col = window, row, col
        self.setTabChangesFocus(False)
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)

    def wrap(self, tag):
        if self.col != 2:
            return
        cursor = self.textCursor()
        value = cursor.selectedText().replace('\u2029','\n')
        name = tag.split('=')[0]
        if tag=='font=':
            if cursor.hasSelection(): cursor.insertText(re.sub(r'\{/?font(?:=[^{}]*)?\}','',value))
            return
        insertion = '{'+tag+'}' + value + ('{/'+name+'}' if name not in ('w','p') else '')
        cursor.insertText(insertion)
        self.setTextCursor(cursor)

    def keyPressEvent(self, event):
        if not editor_keypress(self,event): super().keyPressEvent(event)


class Delegate(QStyledItemDelegate):
    def __init__(self, window):
        super().__init__(window.table)
        self.window = window

    def createEditor(self, parent, option, index):
        cls = RichCellEditor if self.window.visual and index.column() == 2 else CellEditor
        editor = cls(self.window,index.row(),index.column(),parent)
        self.window.editor = editor
        if isinstance(editor,RichCellEditor): editor.renderer.hidden=self.window.text_only
        if index.column() == 1 and self.window.role_background.isChecked():
            color = self.window.data.get('character_colors',{}).get(index.data(),'')
            if color:
                fg = self.window.table.item(index.row(),1).foreground().color().name()
                editor.setStyleSheet('background-color:'+color+';color:'+fg+';')
        editor.textChanged.connect(self.live_preview)
        return editor

    def live_preview(self):
        editor=self.sender()
        if editor is not self.window.editor or editor.row>=len(self.window.rows): return
        row = dict(self.window.rows[editor.row])
        row[('','character','text','note')[editor.col]] = editor_source(editor)
        self.window.table.item(editor.row,0).setText(statement(row,include_ids=self.window.show_ids.isChecked(),label_prefix=self.window.data.get('label_prefix','adv_')))

    def setEditorData(self, editor, index):
        value = index.data(Qt.ItemDataRole.EditRole) or ''
        if isinstance(editor,RichCellEditor): editor.set_source(value)
        else: editor.setPlainText(value)
        editor.selectAll()

    def setModelData(self, editor, model, index):
        value = editor_source(editor)
        if index.column() == 1 and value and value not in self.window.data['characters']:
            value = self.window.rows[index.row()]['character']
            self.window.statusBar().showMessage(tr('未知角色 ID：請先新增角色。'))
        model.setData(index,value)

    def eventFilter(self,editor,event):
        # Keep the selection alive while using inline formatting controls/dialogs.
        if event.type() == QEvent.Type.FocusOut:
            return False
        return super().eventFilter(editor,event)

    def destroyEditor(self, editor, index):
        if self.window.editor is editor:
            self.window.editor = None
        super().destroyEditor(editor,index)

    def paint(self, painter, option, index):
        if index.column() == 1:
            opt = QStyleOptionViewItem(option)
            self.initStyleOption(opt,index)
            row=self.window.rows[index.row()]
            if row.get('kind','dialogue')!='dialogue':
                opt.text=tr(KINDS.get(row['kind'],row['kind']))
                opt.widget.style().drawControl(QStyle.ControlElement.CE_ItemViewItem,opt,painter,opt.widget)
                return
            cid = index.data() or ''
            name = self.window.data['characters'].get(cid,tr('旁白'))
            opt.text = name + (' ('+cid+')' if cid else '')
            opt.widget.style().drawControl(QStyle.ControlElement.CE_ItemViewItem,opt,painter,opt.widget)
            return
        if index.column() != 2 or not self.window.visual or self.window.rows[index.row()].get('kind','dialogue')!='dialogue':
            return super().paint(painter,option,index)
        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt,index)
        opt.text = ''
        style = opt.widget.style()
        style.drawControl(QStyle.ControlElement.CE_ItemViewItem,opt,painter,opt.widget)
        doc = QTextDocument()
        doc.setDefaultFont(option.font)
        renderer = TagRenderer(doc,hidden=self.window.text_only)
        doc.documentLayout().registerHandler(OBJECT,renderer)
        load_source(doc,index.data() or '')
        doc.setTextWidth(option.rect.width()-8)
        painter.save()
        painter.setClipRect(option.rect)
        painter.translate(option.rect.left()+4,option.rect.top()+3)
        doc.drawContents(painter)
        painter.restore()


class Window(QMainWindow):
    def __init__(self, path=None):
        super().__init__()
        set_language(settings().value('language','zh_TW'))
        self.row_heights = {}
        self._resizing_rows = False
        self.document_title=None
        self.db = None
        self.data = sample()
        self.section_index = 0
        self.editor = None
        self.visual = True
        self.text_only = False
        self.loading = False
        self.dirty = False
        self.undo_stack, self.redo_stack = [], []
        self.resize(1440,850)
        base = QWidget()
        self.setCentralWidget(base)
        layout = QVBoxLayout(base)
        project_bar=QHBoxLayout()
        for title,callback in [(tr('新增專案'),self.new_project),(tr('開啟專案'),self.open_dialog),(tr('儲存'),self.save),(tr('另存／變更位置'),lambda:self.save(True)),(tr('專案資料夾'),self.open_project_folder),(tr('匯出 .rpy'),self.export),(tr('匯出 Word'),lambda:self.document_out('docx')),(tr('匯出 PDF'),lambda:self.document_out('pdf'))]:
            button=QPushButton(title);button.clicked.connect(callback);project_bar.addWidget(button)
        self.project_location=QLabel(tr('尚未選擇專案位置'))
        self.project_location.setProperty('project_content',True)
        self.project_location.setSizePolicy(QSizePolicy.Policy.Ignored,QSizePolicy.Policy.Preferred)
        project_bar.addWidget(self.project_location,1)
        layout.addLayout(project_bar)
        top = QHBoxLayout()
        top.addWidget(QLabel(tr('章節 / 段落')))
        self.sections = QComboBox()
        self.sections.setProperty('project_content',True)
        self.sections.currentIndexChanged.connect(self.switch_section)
        top.addWidget(self.sections,1)
        self.mode = QComboBox()
        self.mode.addItems([tr('視覺模式'),tr('原始標籤模式')])
        self.mode.currentIndexChanged.connect(self.change_mode)
        top.addWidget(self.mode)
        self.section_button = QPushButton(tr('章節／段落管理'))
        self.section_button.clicked.connect(self.manage_sections)
        top.addWidget(self.section_button)
        self.character_button = QPushButton(tr('角色管理'))
        self.character_button.clicked.connect(self.characters)
        top.addWidget(self.character_button)
        self.role_background = QCheckBox(tr('角色欄背景色'))
        self.role_background.setChecked(settings().value('role_background',True,type=bool))
        self.role_background.toggled.connect(self.toggle_role_background)
        top.addWidget(self.role_background)
        layout.addLayout(top)
        self.build_format_bar(layout)
        keyboard_help=QLabel(tr('Tab 切換欄位 · Enter 下一行 · Shift+Enter 換行 · 雙擊或直接輸入編輯 · 角色欄使用固定 ID（空白為旁白）'))
        keyboard_help.setWordWrap(True)
        layout.addWidget(keyboard_help)
        self.table = QTableWidget(0,4)
        self.table.setHorizontalHeaderLabels([tr("Ren’Py 即時預覽（唯讀）"),tr('角色名稱 / ID'),tr('台詞內容'),tr('備註')])
        self.table.setItemDelegate(Delegate(self))
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked | QAbstractItemView.EditTrigger.EditKeyPressed | QAbstractItemView.EditTrigger.AnyKeyPressed)
        self.table.setColumnWidth(0,450)
        self.table.setColumnWidth(1,120)
        self.table.setColumnWidth(2,500)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.cellDoubleClicked.connect(self.edit_stage)
        self.table.itemChanged.connect(self.changed_cell)
        self.table.installEventFilter(self)
        self.table.currentCellChanged.connect(self.cell_changed)
        self.table.verticalHeader().setMinimumSectionSize(32)
        self.table.verticalHeader().setMaximumSectionSize(2000)
        self.table.verticalHeader().sectionResized.connect(self.row_resized)
        layout.addWidget(self.table)
        footer = QHBoxLayout()
        self.add_row_button = QPushButton(tr('＋ 新增台詞'))
        self.add_row_button.setProperty('_i18n_text', '＋ 新增台詞')
        self.add_row_button.clicked.connect(self.add_row_and_edit)
        footer.addWidget(self.add_row_button)
        hint = QLabel(tr('也可以按 Enter 到下一行，Tab / Shift+Tab 左右切換欄位。'))
        hint.setProperty('_i18n_text', '也可以按 Enter 到下一行，Tab / Shift+Tab 左右切換欄位。')
        hint.setWordWrap(True)
        footer.addWidget(hint, 1)
        height_label = QLabel(tr('選取行高'))
        height_label.setProperty('_i18n_text', '選取行高')
        footer.addWidget(height_label)
        self.row_height = QSpinBox()
        self.row_height.setRange(32, 2000)
        self.row_height.setValue(100)
        self.row_height.setSuffix(' px')
        footer.addWidget(self.row_height)
        self.apply_height_button = QPushButton(tr('套用至選取行'))
        self.apply_height_button.setProperty('_i18n_text', '套用至選取行')
        self.apply_height_button.clicked.connect(self.apply_row_height)
        footer.addWidget(self.apply_height_button)
        self.reset_height_button = QPushButton(tr('自動行高'))
        self.reset_height_button.setProperty('_i18n_text', '自動行高')
        self.reset_height_button.clicked.connect(self.reset_row_height)
        footer.addWidget(self.reset_height_button)
        self.help_button = QPushButton(tr('Help · 操作說明'))
        self.help_button.setProperty('_i18n_text', 'Help · 操作說明')
        self.help_button.clicked.connect(self.show_help)
        footer.addWidget(self.help_button)
        layout.addLayout(footer)
        search = QHBoxLayout()
        self.find_text = QLineEdit()
        self.find_text.setPlaceholderText(tr('搜尋所有章節的角色、台詞及備註'))
        self.replace_text = QLineEdit()
        self.replace_text.setPlaceholderText(tr('取代文字（台詞及備註）'))
        search.addWidget(self.find_text)
        search.addWidget(self.replace_text)
        for name, callback in [(tr('尋找下一個'),self.find_next),(tr('全部取代'),self.replace_all)]:
            button = QPushButton(name)
            button.clicked.connect(callback)
            search.addWidget(button)
        layout.addLayout(search)
        self.build_menu()
        self.autosave = QTimer(self)
        self.autosave.setInterval(5000)
        self.autosave.timeout.connect(self.save_if_dirty)
        self.autosave.start()
        self.backup_timer = QTimer(self)
        self.backup_timer.setInterval(300000)
        self.backup_timer.timeout.connect(self.backup)
        self.backup_timer.start()
        if path:
            self.open_path(path)
        else:
            self.refresh()
            self.statusBar().showMessage(tr('未儲存的新專案：請按 ⌘S 選擇資料庫位置；之後每 5 秒自動儲存。'))

    def build_format_bar(self,layout):
        bar = QHBoxLayout()
        bar.addWidget(QLabel(tr('文字格式')))
        self.format_buttons = {}
        for title,tag,shortcut in [(tr('粗體 B'),'b','Ctrl+B'),(tr('斜體 I'),'i','Ctrl+I'),(tr('底線 U'),'u','Ctrl+U')]:
            button = QPushButton(title)
            button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            button.clicked.connect(lambda checked=False,t=tag:self.format_text(t))
            self.format_buttons[tag] = button
            bar.addWidget(button)
            action = QAction(self)
            action.setShortcut(shortcut)
            action.triggered.connect(lambda checked=False,t=tag:self.format_text(t))
            self.addAction(action)
        bar.addWidget(QLabel(tr('字號')))
        self.font_size = QSpinBox()
        self.font_size.setRange(8,120)
        self.font_size.setValue(24)
        self.font_size.setFixedWidth(65)
        bar.addWidget(self.font_size)
        for title,callback in [(tr('套用字號'),lambda:self.format_text('size='+str(self.font_size.value()))),(tr('文字顏色'),self.choose_text_color)]:
            button = QPushButton(title)
            button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            button.clicked.connect(callback)
            bar.addWidget(button)
        self.wait_seconds = QDoubleSpinBox()
        self.wait_seconds.setRange(0,3600)
        self.wait_seconds.setDecimals(2)
        self.wait_seconds.setValue(0.5)
        self.wait_seconds.setSuffix(' s')
        self.wait_seconds.setFixedWidth(90)
        bar.addWidget(self.wait_seconds)
        for title,callback in [(tr('插入等待'),lambda:self.format_text('w='+format(self.wait_seconds.value(),'g'))),(tr('顯示速度…'),lambda:self.custom_format('cps=20')),(tr('自訂標籤…'),lambda:self.custom_format('custom'))]:
            button = QPushButton(title)
            button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            button.clicked.connect(callback)
            bar.addWidget(button)
            if title == tr('插入等待'): self.wait_button = button
        bar.addStretch()
        layout.addLayout(bar)
        font_bar=QHBoxLayout()
        font_bar.addWidget(QLabel(tr('字體')))
        self.font_combo=QComboBox()
        self.font_combo.setProperty('project_content',True)
        self.font_combo.setMinimumWidth(190)
        self.font_combo.addItem(tr('預設字體'),'')
        self.font_combo.activated.connect(lambda index:self.format_text('font='+self.font_combo.itemData(index)))
        font_bar.addWidget(self.font_combo)
        for title,callback in [(tr('匯入字體…'),self.import_project_font),(tr('點擊後繼續'),lambda:self.format_text('w')),(tr('新增演出…'),lambda:self.add_stage('scene')),(tr('新增選項／分支…'),lambda:self.add_stage('menu'))]:
            button=QPushButton(title)
            button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            button.clicked.connect(callback)
            font_bar.addWidget(button)
            if title==tr('點擊後繼續'): self.click_wait_button=button
        self.text_only_checkbox=QCheckBox(tr('只顯示文本'))
        self.text_only_checkbox.toggled.connect(self.toggle_text_only)
        self.nvl_clear_button=QPushButton(tr('NVL 清頁'))
        self.nvl_clear_button.clicked.connect(self.add_nvl_clear)
        font_bar.addWidget(self.nvl_clear_button)
        font_bar.addWidget(self.text_only_checkbox)
        font_bar.addStretch()
        layout.addLayout(font_bar)
        options=QHBoxLayout()
        self.show_ids=QCheckBox(tr('顯示台詞 ID'))
        self.show_ids.setChecked(settings().value('show_ids',False,type=bool))
        self.show_ids.toggled.connect(self.toggle_ids)
        options.addWidget(self.show_ids)
        self.export_ids=QCheckBox(tr('RPY 包含台詞 ID'))
        self.export_ids.setChecked(settings().value('export_ids',True,type=bool))
        self.export_ids.toggled.connect(lambda enabled:settings().setValue('export_ids',enabled))
        options.addWidget(self.export_ids)
        options.addStretch()
        options.addWidget(QLabel('Language /'))
        options.addWidget(QLabel(tr('介面語言')))
        self.language_combo=QComboBox()
        self.language_combo.setProperty('project_content',True)
        for code,title in LANGUAGES.items(): self.language_combo.addItem(title,code)
        self.language_combo.setCurrentIndex(self.language_combo.findData(i18n.LANGUAGE))
        self.language_combo.currentIndexChanged.connect(self.change_language)
        options.addWidget(self.language_combo)
        layout.addLayout(options)

    def toggle_ids(self,enabled):
        self.commit()
        settings().setValue('show_ids',enabled)
        self.refresh()

    def change_language(self,index):
        self.commit()
        code=self.language_combo.itemData(index)
        settings().setValue('language',code)
        set_language(code)
        retranslate(self)
        self.statusBar().clearMessage()
        self.refresh()

    def toggle_text_only(self,enabled):
        self.commit()
        self.text_only=enabled
        if enabled:
            self.previous_text_mode=self.mode.currentIndex()
            self.mode.setCurrentIndex(0)
        else:
            self.mode.setCurrentIndex(getattr(self,'previous_text_mode',0))
        self.mode.setEnabled(not enabled)
        self.table.setColumnHidden(0,enabled)
        self.refresh()
        self.table.viewport().update()

    def refresh_fonts(self):
        current=self.font_combo.currentData()
        self.font_combo.clear();self.font_combo.addItem(tr('預設字體'),'')
        if self.db:
            missing=register_fonts(self.data,self.db.path)
            if missing: self.statusBar().showMessage(tr('缺少專案字體：')+', '.join(missing))
        else:
            from .richtext import FONT_FAMILIES
            FONT_FAMILIES.clear()
        for filename,family in self.data.get('fonts',{}).items(): self.font_combo.addItem(family,'adv_generated/fonts/'+filename)
        self.font_combo.setCurrentIndex(max(0,self.font_combo.findData(current)))
        if self.db:
            self.project_location.setText(str(self.db.path.parent))
            self.project_location.setToolTip(str(self.db.path))
        else: self.project_location.setText(tr('尚未選擇專案位置'))

    def import_project_font(self):
        if not self.db and not self.save(): return
        path,_=QFileDialog.getOpenFileName(self,tr('匯入字體（自動複製到專案素材資料夾）'),'',tr('字體 (*.ttf *.otf)'))
        if path:
            try:
                filename,family=import_font(path,self.db.path)
                self.snapshot();self.data.setdefault('fonts',{})[filename]=family
                self.refresh_fonts()
                self.font_combo.setCurrentIndex(self.font_combo.findData('adv_generated/fonts/'+filename))
                self.format_text('font=adv_generated/fonts/'+filename)
                self.statusBar().showMessage(tr('已匯入字體：')+family+tr('；匯出 Ren’Py 時會一起複製。'))
            except Exception as error: self.error(error)

    def open_project_folder(self):
        if self.db: QDesktopServices.openUrl(QUrl.fromLocalFile(str(self.db.path.parent)))

    def add_stage(self,kind='scene'):
        self.commit()
        if not self.db and not self.save(): return
        dialog=StageDialog(self.data,self.db.path,parent=self)
        dialog.kind.setCurrentIndex(dialog.kind.findData(kind))
        if dialog.exec():
            self.snapshot()
            self.data['images']=dialog.data.get('images',{})
            position=max(0,self.table.currentRow()+1)
            self.rows.insert(position,dialog.result_row)
            self.refresh();self.table.setCurrentCell(position,2)

    def add_nvl_clear(self):
        self.commit();self.snapshot()
        row=max(0,self.table.currentRow()+1)
        self.rows.insert(row,dict(new_row(),kind='nvl_clear'))
        self.refresh();self.table.setCurrentCell(row,2)
        self.table.scrollToItem(self.table.item(row,2))

    def edit_stage(self,row,col):
        if self.rows[row].get('kind','dialogue')=='dialogue': return
        self.commit()
        dialog=StageDialog(self.data,self.db.path,self.rows[row],self)
        if dialog.exec():
            self.snapshot();self.data['images']=dialog.data.get('images',{})
            self.rows[row]=dialog.result_row;self.refresh()

    def document_out(self,kind):
        self.commit()
        default_title=self.document_title or (self.db.path.stem if self.db else tr('視覺小說台詞稿'))
        options=DocumentExportDialog(default_title,self.show_ids.isChecked(),self)
        if not options.exec(): return
        title=options.title_input.text().strip()
        path,_=QFileDialog.getSaveFileName(self,tr('匯出')+' '+('Word' if kind=='docx' else 'PDF'),self.export_path(kind),kind.upper()+' (*.'+kind+')')
        if not path: return
        if not path.endswith('.'+kind): path+='.'+kind
        try:
            from .documents import export_word,export_pdf
            substitutions=[]
            if kind=='docx': export_word(self.data,path,title=title,include_ids=options.include_ids.isChecked())
            else: substitutions=export_pdf(self.data,path,self.db.path if self.db else None,title=title,include_ids=options.include_ids.isChecked())
            self.document_title=title
            self.statusBar().showMessage(tr('已匯出：')+path+(tr('（字體替代為預設：')+', '.join(substitutions)+'）' if substitutions else ''))
        except Exception as error: self.error(error)

    def choose_text_color(self):
        color = QColorDialog.getColor(QColor('#ffcc00'),self,tr('選擇文字顏色'))
        if color.isValid(): self.format_text('color='+color.name())

    def cell_changed(self,row,col,previous_row,previous_col):
        if self.editor and (self.editor.row,self.editor.col) != (row,col): self.commit()

    def toggle_role_background(self,enabled):
        settings().setValue('role_background',enabled)
        if hasattr(self,'table'):
            for row in range(len(self.rows)): self.apply_role_color(row)

    def apply_role_color(self,row):
        item = self.table.item(row,1)
        if not item: return
        enabled = self.role_background.isChecked()
        value = self.data.get('character_colors',{}).get(self.rows[row]['character'],'')
        # Item appearance must not enter the undo/history of dialogue data.
        was_loading = self.loading
        self.loading = True
        if enabled and value:
            color = QColor(value)
            item.setBackground(QBrush(color))
            luminance = .299*color.red()+.587*color.green()+.114*color.blue()
            item.setForeground(QBrush(QColor('#111111' if luminance > 145 else '#ffffff')))
        else:
            item.setData(Qt.ItemDataRole.BackgroundRole,None)
            item.setData(Qt.ItemDataRole.ForegroundRole,None)
        name = self.data['characters'].get(self.rows[row]['character'],tr('旁白'))
        item.setToolTip(name + (' · '+value if value else ''))
        self.loading = was_loading

    @property
    def rows(self):
        return self.data['sections'][self.section_index]['rows']

    def action(self, menu, title, callback, shortcut=None):
        action = QAction(title,self)
        if shortcut:
            action.setShortcut(shortcut)
        action.triggered.connect(callback)
        menu.addAction(action)
        return action

    def build_menu(self):
        menu = self.menuBar().addMenu(tr('檔案'))
        self.action(menu,tr('新增專案'),self.new_project,'Ctrl+N')
        self.action(menu,tr('開啟專案…'),self.open_dialog,'Ctrl+O')
        self.action(menu,tr('儲存'),self.save,'Ctrl+S')
        self.action(menu,tr('另存新檔…'),lambda:self.save(True),'Ctrl+Shift+S')
        self.action(menu,tr('匯出 Ren’Py…'),self.export)
        self.action(menu,tr('匯出 Excel…'),self.excel_out)
        self.action(menu,tr('匯出 Word…'),lambda:self.document_out('docx'))
        self.action(menu,tr('匯出 PDF…'),lambda:self.document_out('pdf'))
        self.action(menu,tr('匯入 Excel（取代專案）…'),self.excel_in)
        menu = self.menuBar().addMenu(tr('編輯'))
        self.action(menu,tr('復原'),self.undo,'Ctrl+Z')
        self.action(menu,tr('重做'),self.redo,'Ctrl+Shift+Z')
        self.action(menu,tr('複製表格'),self.copy_grid,'Ctrl+Shift+C')
        self.action(menu,tr('貼上表格'),self.paste_grid,'Ctrl+Shift+V')
        self.action(menu,tr('新增台詞'),self.add_row)
        self.action(menu,tr('刪除選取台詞'),self.delete_rows)
        self.action(menu,tr('上移台詞'),lambda:self.move_row(-1),'Alt+Up')
        self.action(menu,tr('下移台詞'),lambda:self.move_row(1),'Alt+Down')
        menu = self.menuBar().addMenu(tr('專案'))
        self.action(menu,tr('章節／段落管理…'),self.manage_sections)
        self.action(menu,tr('新增章節 / 段落…'),self.add_section)
        self.action(menu,tr('設定段落末尾 call…'),self.set_call)
        menu = self.menuBar().addMenu(tr('Help / 說明'))
        self.action(menu,tr('Help · 操作說明'),self.show_help)
        self.about_action = self.action(menu,tr('關於 / About'),self.show_about)
        self.about_action.setMenuRole(QAction.MenuRole.AboutRole)

    def refresh(self):
        self.loading = True
        self.section_index = min(self.section_index,len(self.data['sections'])-1)
        self.sections.blockSignals(True)
        self.sections.clear()
        for s in self.data['sections']:
            self.sections.addItem(s['chapter']+' / '+s['name']+'  ['+label_name(self.data,s['id'])+']')
        self.sections.setCurrentIndex(self.section_index)
        self.sections.blockSignals(False)
        self.refresh_fonts()
        self.table.setRowCount(len(self.rows))
        for i,row in enumerate(self.rows):
            display=row['text']
            if row.get('kind')=='menu': display += '\n'+'\n'.join('• '+c['text']+(' → '+c['target'] if not self.text_only else '') for c in row['choices'])
            for col,value in enumerate([statement(row,include_ids=self.show_ids.isChecked(),label_prefix=self.data.get('label_prefix','adv_')),row['character'],display,row['note']]):
                item = QTableWidgetItem(value)
                if col == 0 or (row.get('kind','dialogue')!='dialogue' and col in (1,2)):
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                if self.show_ids.isChecked(): item.setToolTip(tr('永久台詞 ID：')+row['id'])
                self.table.setItem(i,col,item)
            self.apply_role_color(i)
            self.table.setRowHeight(i,self.row_heights.get(row['id'],self.automatic_row_height(row)))
            self.table.setRowHidden(i,self.text_only and row.get('kind','dialogue') not in ('dialogue','menu'))
        self.loading = False
        retranslate(self)
        self.setWindowTitle(tr(APP_NAME)+' — '+(str(self.db.path.name) if self.db else tr('新專案'))+(' *' if self.dirty else ''))

    def snapshot(self):
        self.undo_stack.append(copy.deepcopy(self.data))
        self.undo_stack = self.undo_stack[-100:]
        self.redo_stack.clear()
        self.dirty = True

    def commit(self):
        if self.editor:
            self.finish_editor(self.editor)

    def finish_editor(self, editor, navigation=None, delta=1):
        row,col = editor.row,editor.col
        value = editor_source(editor)
        if col == 1 and value and value not in self.data['characters']:
            self.statusBar().showMessage(tr('未知角色 ID：請先在「專案 → 角色管理」新增角色。'))
            value = self.rows[row]['character']
        self.table.item(row,col).setText(value)
        self.table.itemDelegate().closeEditor.emit(editor,QStyledItemDelegate.EndEditHint.NoHint)
        self.editor = None
        if navigation:
            if navigation == 'enter':
                row,col = row+1,1
            else:
                col += delta
                if col > 3:
                    row,col = row+1,1
                if col < 1:
                    row,col = max(0,row-1),3
            while row < len(self.rows) and self.rows[row].get('kind','dialogue')!='dialogue': row+=1
            if row >= len(self.rows):
                self.add_row()
            self.table.setCurrentCell(row,col)
            self.table.editItem(self.table.item(row,col))

    def changed_cell(self,item):
        if self.loading or item.column() == 0 or (self.rows[item.row()].get('kind','dialogue')!='dialogue' and item.column()!=3):
            return
        key = ('','character','text','note')[item.column()]
        if self.rows[item.row()][key] == item.text():
            return
        self.snapshot()
        self.rows[item.row()][key] = item.text()
        self.table.item(item.row(),0).setText(statement(self.rows[item.row()],include_ids=self.show_ids.isChecked(),label_prefix=self.data.get('label_prefix','adv_')))
        if item.column() == 1: self.apply_role_color(item.row())
        self.setWindowTitle(self.windowTitle().rstrip(' *')+' *')

    def switch_section(self,index):
        if index < 0 or self.loading:
            return
        self.commit()
        self.section_index = index
        self.refresh()

    def change_mode(self,index):
        active = (self.editor.row,self.editor.col) if self.editor else None
        self.commit()
        self.visual = index == 0
        self.table.viewport().update()
        if active:
            self.table.setCurrentCell(*active)
            self.table.editItem(self.table.currentItem())

    def eventFilter(self,obj,event):
        from PySide6.QtCore import QEvent
        if obj is self.table and event.type() == QEvent.Type.KeyPress and not self.editor:
            row,col = self.table.currentRow(),self.table.currentColumn()
            if event.matches(QKeySequence.StandardKey.Copy):
                self.copy_grid()
                return True
            if event.matches(QKeySequence.StandardKey.Paste):
                self.paste_grid()
                return True
            if event.key() in (Qt.Key.Key_Return,Qt.Key.Key_Enter,Qt.Key.Key_Tab,Qt.Key.Key_Backtab):
                if row < 0:
                    row,col = 0,1
                elif event.key() in (Qt.Key.Key_Return,Qt.Key.Key_Enter):
                    row,col = row+1,1
                else:
                    col += -1 if event.modifiers() & Qt.KeyboardModifier.ShiftModifier or event.key() == Qt.Key.Key_Backtab else 1
                    if col > 3: row,col = row+1,1
                    if col < 1: row,col = max(0,row-1),3
                while row < len(self.rows) and self.rows[row].get('kind','dialogue')!='dialogue': row+=1
                if row >= len(self.rows): self.add_row()
                self.table.setCurrentCell(row,col)
                self.table.editItem(self.table.item(row,col))
                return True
        return super().eventFilter(obj,event)

    def project_directory(self):
        return str(self.db.path.parent) if self.db else default_directory()

    def export_path(self, extension):
        name = self.db.path.stem if self.db else tr('台詞稿')
        return str(Path(self.project_directory()) / (name + '.' + extension))

    def selected_rows(self):
        rows = sorted({i.row() for i in self.table.selectedIndexes() if not self.table.isRowHidden(i.row())})
        if not rows and self.table.currentRow() >= 0:
            rows = [self.table.currentRow()]
        return rows

    def automatic_row_height(self, row):
        return min(2000,max(80,25*(len(row.get('choices',[]))+1),18*len(statement(row,include_ids=self.show_ids.isChecked(),label_prefix=self.data.get('label_prefix','adv_')).splitlines())+12 if not self.text_only else 0))

    def persist_heights(self):
        if self.db:
            save_heights(self.db.path,self.row_heights)

    def row_resized(self, row, old_height, height):
        if self.loading or self._resizing_rows or not 0 <= row < len(self.rows): return
        selected = self.selected_rows()
        self.set_row_heights(selected if row in selected else [row], height)

    def set_row_heights(self, rows, height):
        self._resizing_rows = True
        try:
            for row in rows:
                if 0 <= row < len(self.rows):
                    self.row_heights[self.rows[row]['id']] = height
                    self.table.setRowHeight(row,height)
        finally:
            self._resizing_rows = False
        self.persist_heights()

    def apply_row_height(self):
        self.commit()
        self.set_row_heights(self.selected_rows(), self.row_height.value())

    def reset_row_height(self):
        self.commit()
        self._resizing_rows = True
        try:
            for row in self.selected_rows():
                self.row_heights.pop(self.rows[row]['id'],None)
                self.table.setRowHeight(row,self.automatic_row_height(self.rows[row]))
        finally:
            self._resizing_rows = False
        self.persist_heights()

    def add_row_and_edit(self):
        self.add_row()
        row = len(self.rows)-1
        self.table.setCurrentCell(row,1)
        self.table.scrollToItem(self.table.item(row,1))
        self.table.setFocus()
        self.table.editItem(self.table.item(row,1))

    def show_about(self):
        self.commit()
        AboutDialog(self).exec()

    def show_help(self):
        self.commit()
        dialog = QDialog(self)
        dialog.setWindowTitle(tr('Help · 操作說明')+' — '+__version__)
        dialog.resize(720,620)
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel(tr(APP_NAME)+' — '+__version__))
        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setHtml(help_html())
        layout.addWidget(browser)
        close = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        close.rejected.connect(dialog.reject)
        layout.addWidget(close)
        dialog.exec()

    def add_row(self):
        self.commit()
        self.snapshot()
        self.rows.append(new_row())
        self.refresh()

    def delete_rows(self):
        self.commit()
        selected = sorted({i.row() for i in self.table.selectedIndexes()},reverse=True)
        if selected:
            self.snapshot()
            for row in selected: del self.rows[row]
            if not self.rows: self.rows.append(new_row())
            self.refresh()

    def move_row(self,delta):
        self.commit()
        row = self.table.currentRow()
        target = row+delta
        if row >= 0 and 0 <= target < len(self.rows):
            self.snapshot()
            self.rows[row],self.rows[target] = self.rows[target],self.rows[row]
            self.refresh()
            self.table.setCurrentCell(target,1)

    def undo(self):
        if self.editor and self.editor.document().isUndoAvailable():
            self.editor.undo()
            return
        self.commit()
        if self.undo_stack:
            self.redo_stack.append(copy.deepcopy(self.data))
            self.data = self.undo_stack.pop()
            self.dirty = True
            self.refresh()

    def redo(self):
        if self.editor and self.editor.document().isRedoAvailable():
            self.editor.redo()
            return
        self.commit()
        if self.redo_stack:
            self.undo_stack.append(copy.deepcopy(self.data))
            self.data = self.redo_stack.pop()
            self.dirty = True
            self.refresh()

    def format_text(self,tag):
        if self.editor:
            self.editor.wrap(tag)
        elif self.table.currentColumn() == 2:
            self.table.editItem(self.table.currentItem())
            if self.editor: self.editor.wrap(tag)

    def custom_format(self,tag):
        value,ok = QInputDialog.getText(self,tr('Ren’Py 文字標籤'),tr('輸入標籤（例如 color=#ff0000、w=0.5）'),text=tag)
        if ok and value and not any(c in value for c in '{}\n\r'):
            self.format_text(value)

    def copy_grid(self):
        self.commit()
        selected = self.table.selectedRanges()
        if not selected: return
        area = selected[0]
        output = io.StringIO()
        writer = csv.writer(output,delimiter='\t',lineterminator='\n')
        for row in range(area.topRow(),area.bottomRow()+1):
            writer.writerow([self.table.item(row,col).text() for col in range(max(1,area.leftColumn()),area.rightColumn()+1)])
        QApplication.clipboard().setText(output.getvalue())

    def paste_grid(self,text=None,row=None,col=None):
        self.commit()
        if not isinstance(text,str): text = QApplication.clipboard().text()
        row = max(0,self.table.currentRow()) if row is None else row
        col = max(1,self.table.currentColumn()) if col is None else max(1,col)
        try:
            values = list(csv.reader(io.StringIO(text),delimiter='\t'))
            for line in values:
                if len(line) > 4-col: raise ValueError(tr('貼上欄數超過目前位置的可編輯欄數'))
                if col == 1 and line and line[0] and line[0] not in self.data['characters']:
                    raise ValueError(tr('未知角色 ID：')+line[0])
            if not values: return
            self.snapshot()
            while len(self.rows) < row+len(values): self.rows.append(new_row())
            for offset,line in enumerate(values):
                for c,value in enumerate(line,col):
                    self.rows[row+offset][('','character','text','note')[c]] = value
            self.refresh()
        except Exception as error: self.error(error)

    def find_next(self):
        self.commit()
        needle = self.find_text.text()
        if not needle: return
        cells = [(s,r,c) for s,section in enumerate(self.data['sections']) for r,row in enumerate(section['rows']) for c,key in ((1,'character'),(2,'text'),(3,'note')) if needle in row[key]]
        current = (self.section_index,self.table.currentRow(),self.table.currentColumn())
        if cells:
            s,r,c = next((x for x in cells if x > current),cells[0])
            self.section_index = s
            self.refresh()
            self.table.setCurrentCell(r,c)
            self.table.scrollToItem(self.table.item(r,c))
        self.statusBar().showMessage(tr('找到 ')+str(len(cells))+tr(' 個欄位'))

    def replace_all(self):
        self.commit()
        needle = self.find_text.text()
        if not needle: return
        self.snapshot()
        count = 0
        for section in self.data['sections']:
            for row in section['rows']:
                keys=('text','note') if row.get('kind','dialogue') in ('dialogue','menu') else ('note',)
                for choice in row.get('choices',[]):
                    count+=choice['text'].count(needle)
                    choice['text']=choice['text'].replace(needle,self.replace_text.text())
                for key in keys:
                    count += row[key].count(needle)
                    row[key] = row[key].replace(needle,self.replace_text.text())
        self.refresh()
        self.statusBar().showMessage(tr('已取代 ')+str(count)+tr(' 處（可復原）'))

    def characters(self):
        self.commit()
        dialog = CharacterDialog(self.data,self)
        if dialog.exec():
            chars,colors = dialog.values()
            self.snapshot()
            update_characters(self.data,chars,colors,dialog.renames(),dialog.modes(),dialog.narrator_mode.currentData())
            self.refresh()

    def manage_sections(self):
        self.commit()
        current_id = self.data['sections'][self.section_index]['id']
        dialog = SectionDialog(self.data,current_id,self)
        if dialog.exec():
            if dialog.data != self.data:
                self.snapshot()
                self.data = dialog.data
            self.section_index = next((i for i,s in enumerate(self.data['sections']) if s['id'] == dialog.current_id),0)
            self.refresh()

    def add_section(self):
        self.commit()
        # The form edits a draft so cancellation/validation leaves the project intact.
        draft = copy.deepcopy(self.data)
        dialog = SectionForm(draft,parent=self)
        if dialog.exec():
            self.snapshot()
            self.data = draft
            self.section_index = next(i for i,s in enumerate(self.data['sections']) if s['id'] == dialog.result_id)
            self.refresh()

    def set_call(self):
        self.commit()
        choices = [tr('（無，直接 return）')]+[s['id'] for s in self.data['sections'] if s is not self.data['sections'][self.section_index]]
        value,ok = QInputDialog.getItem(self,tr('段落流程'),tr('完成本段台詞後 call 哪個段落？'),choices,0,False)
        if ok:
            self.snapshot()
            self.data['sections'][self.section_index]['call'] = '' if value == choices[0] else value
            self.refresh()

    def error(self,error):
        QMessageBox.warning(self,tr('操作未完成'),str(error))

    def save(self,save_as=False):
        self.commit()
        path = None
        if save_as or self.db is None:
            path,_ = QFileDialog.getSaveFileName(self,tr('儲存專案'),str(self.db.path) if self.db else default_directory(),tr('ADV 專案 (*.advdb)'))
            if not path: return False
            if not path.endswith('.advdb'): path += '.advdb'
        try:
            if path:
                new_db = Database(path)
                try:
                    if self.db: copy_assets(self.data,self.db.path,path)
                    asset_folder(path).mkdir(parents=True,exist_ok=True)
                    new_db.save(self.data)
                except Exception:
                    new_db.close()
                    raise
                if self.db: self.db.close()
                self.db = new_db
                self.db.backup()
            else:
                self.db.save(self.data)
            remember_project(self.db.path)
            save_heights(self.db.path,self.row_heights)
            self.dirty = False
            self.refresh_fonts()
            self.setWindowTitle(tr(APP_NAME)+' — '+self.db.path.name)
            self.statusBar().showMessage(tr('已儲存：')+str(self.db.path))
            return True
        except Exception as error:
            self.error(error)
            return False

    def save_if_dirty(self):
        if not self.db:
            return
        if self.editor:
            editor = self.editor
            value = editor_source(editor)
            if editor.col == 1 and value and value not in self.data['characters']:
                return
            self.table.item(editor.row,editor.col).setText(value)
        if self.dirty:
            try:
                self.db.save(self.data)
                self.dirty = False
                self.setWindowTitle(tr(APP_NAME)+' — '+self.db.path.name)
                self.statusBar().showMessage(tr('已自動儲存'))
            except Exception as error:
                self.statusBar().showMessage(tr('自動儲存失敗：')+str(error))

    def backup(self):
        if self.db:
            self.save_if_dirty()
            try: self.db.backup()
            except Exception as error: self.error(error)

    def confirm_leave(self):
        self.commit()
        if not self.dirty: return True
        result = QMessageBox.question(self,tr('未儲存變更'),tr('儲存變更後再繼續？'),QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel)
        if result == QMessageBox.StandardButton.Save: return self.save()
        return result == QMessageBox.StandardButton.Discard

    def new_project(self):
        if not self.confirm_leave(): return
        folder = QFileDialog.getExistingDirectory(self,tr('選擇新專案資料夾（可建立新資料夾）'),self.project_directory())
        if not folder: return
        try:
            self.open_path(create_project(folder))
        except Exception as error:
            self.error(error)

    def open_dialog(self):
        if not self.confirm_leave(): return
        path,_ = QFileDialog.getOpenFileName(self,tr('開啟專案'),self.project_directory(),tr('ADV 專案 (*.advdb)'))
        if path: self.open_path(path)

    def open_path(self,path):
        candidate = None
        try:
            if not Path(path).is_file(): raise FileNotFoundError(str(path))
            candidate = Database(path)
            data = candidate.load()
            if not data['sections']: raise ValueError(tr('專案沒有段落'))
            from .core import validate
            validate(data)
            if self.db: self.db.close()
            self.db,self.data = candidate,data
            self.row_heights = load_heights(self.db.path)
            remember_project(self.db.path)
            self.document_title=None
            self.section_index = 0
            self.dirty = False
            self.undo_stack.clear()
            self.redo_stack.clear()
            self.refresh()
        except Exception as error:
            if candidate: candidate.close()
            self.error(error)

    def export(self):
        self.commit()
        name = (self.db.path.stem if self.db else 'dialogue') + '_renpy'
        options = RenPyExportDialog(self.project_directory(),name,self)
        if not options.exec(): return
        try:
            result = export_rpy(self.data,options.directory.text(),self.db.path if self.db else None,
                include_ids=self.export_ids.isChecked(),subfolder=options.subfolder)
            self.statusBar().showMessage(tr('已匯出至 ')+str(result))
        except Exception as error: self.error(error)

    def excel_out(self):
        self.commit()
        path,_ = QFileDialog.getSaveFileName(self,tr('匯出 Excel'),self.export_path('xlsx'),'Excel (*.xlsx)')
        if path:
            try: export_excel(self.data,path if path.endswith('.xlsx') else path+'.xlsx',self.db.path if self.db else None)
            except Exception as error: self.error(error)

    def excel_in(self):
        self.commit()
        path,_ = QFileDialog.getOpenFileName(self,tr('匯入 Excel（完整取代，可復原）'),'','Excel (*.xlsx)')
        if path:
            try:
                data = import_excel(path)
                if data.get('fonts') or data.get('images'):
                    if not self.db and not self.save(): return
                    copy_assets(data,path,self.db.path)
                self.snapshot()
                self.data = data
                self.section_index = 0
                self.refresh()
            except Exception as error: self.error(error)

    def closeEvent(self,event):
        if self.confirm_leave():
            if self.db:
                try: self.db.backup()
                except Exception as error:
                    self.error(error)
                    event.ignore()
                    return
                self.db.close()
                self.db = None
            event.accept()
        else: event.ignore()
