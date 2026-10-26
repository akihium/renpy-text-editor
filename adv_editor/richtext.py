"""Ren'Py source <-> editable Qt rich text, with lossless opaque tag objects."""
from __future__ import annotations
from .i18n import tr
from .platform_fonts import document_font_family
import re
from PySide6.QtCore import QObject, QSizeF, Qt
from PySide6.QtGui import (QColor, QFont, QFontMetricsF, QTextCharFormat, QTextCursor,
                          QTextFormat, QPyTextObject)
from PySide6.QtWidgets import QTextEdit

TOKEN = int(QTextFormat.Property.UserProperty) + 1
OBJECT = int(QTextFormat.ObjectTypes.UserObject) + 1
FONT_FILE = TOKEN + 1
FONT_FAMILIES = {}


def token_label(raw):
    inner = raw[1:-1]
    if inner.startswith(('w=', 'p=')):
        return tr('等待 ') + inner.split('=',1)[1] + 's'
    if inner in ('w','p'):
        return tr('點擊後繼續')
    if inner.startswith('cps='):
        return tr('速度 ') + inner[4:] + tr(' 字/s')
    if inner == '/cps':
        return tr('速度結束')
    return (tr('結束：') + inner[1:]) if inner.startswith('/') else (tr('標籤：') + inner)


class TagRenderer(QPyTextObject):
    def __init__(self,parent=None,hidden=False):
        super().__init__(parent)
        self.hidden=hidden

    def intrinsicSize(self, doc, pos, fmt):
        if self.hidden: return QSizeF(0,0)
        metrics = QFontMetricsF(doc.defaultFont())
        return QSizeF(metrics.horizontalAdvance('（'+token_label(fmt.property(TOKEN))+'）')+10, metrics.height()+6)

    def drawObject(self, painter, rect, doc, pos, fmt):
        if self.hidden: return
        painter.save()
        painter.setPen(QColor('#58697c'))
        painter.setBrush(QColor('#e8edf3'))
        painter.drawRoundedRect(rect.adjusted(1,1,-1,-1),4,4)
        painter.setFont(doc.defaultFont())
        painter.drawText(rect,Qt.AlignmentFlag.AlignCenter,'（'+token_label(fmt.property(TOKEN))+'）')
        painter.restore()


def insert_token(cursor, raw):
    fmt = QTextCharFormat()
    fmt.setObjectType(OBJECT)
    fmt.setProperty(TOKEN,raw)
    cursor.insertText('\ufffc',fmt)


def style_format(styles):
    fmt = QTextCharFormat()
    if styles.get('b'): fmt.setFontWeight(QFont.Weight.Bold)
    if styles.get('i'): fmt.setFontItalic(True)
    if styles.get('u'): fmt.setFontUnderline(True)
    if styles.get('color'): fmt.setForeground(QColor(styles['color']))
    if styles.get('size'): fmt.setFontPointSize(float(styles['size']))
    if styles.get('font'):
        fmt.setProperty(FONT_FILE,styles['font'])
        fmt.setFontFamilies([FONT_FAMILIES.get(styles['font'],document_font_family())])
    return fmt


def load_source(document, source):
    document.clear()
    cursor = QTextCursor(document)
    styles, stack = {}, []
    for part in re.split(r'(\{\{|\{[^{}\n]*\})',source):
        if not part: continue
        if part == '{{':
            cursor.insertText('{',style_format(styles))
            continue
        if part.startswith('{') and part.endswith('}'):
            inner = part[1:-1]
            name, _, value = inner.partition('=')
            supported = (name == 'font' and bool(value)) or name in ('b','i','u') or (name == 'color' and bool(re.fullmatch(r'#[0-9a-fA-F]{6}',value))) or (name == 'size' and value.isdigit() and int(value)>0)
            if supported:
                stack.append((name,dict(styles)))
                styles[name] = value if value else True
                continue
            if inner.startswith('/') and stack and stack[-1][0] == inner[1:]:
                _,styles = stack.pop()
                continue
            insert_token(cursor,part)
        else:
            cursor.insertText(part,style_format(styles))
    document.setModified(False)
    document.clearUndoRedoStacks()


def format_tags(fmt):
    tags = []
    if fmt.property(FONT_FILE): tags.append('font='+fmt.property(FONT_FILE))
    if fmt.fontWeight() >= QFont.Weight.Bold: tags.append('b')
    if fmt.fontItalic(): tags.append('i')
    if fmt.fontUnderline(): tags.append('u')
    if fmt.fontPointSize(): tags.append('size='+str(int(fmt.fontPointSize())))
    if fmt.hasProperty(QTextFormat.Property.ForegroundBrush): tags.append('color='+fmt.foreground().color().name())
    return tags


def dump_source(document):
    result,active = [],[]
    def transition(tags):
        nonlocal active
        shared = 0
        while shared < min(len(active),len(tags)) and active[shared] == tags[shared]: shared += 1
        result.extend('{/'+tag.split('=')[0]+'}' for tag in reversed(active[shared:]))
        result.extend('{'+tag+'}' for tag in tags[shared:])
        active = tags
    block = document.begin()
    while block.isValid():
        iterator = block.begin()
        while not iterator.atEnd():
            fragment = iterator.fragment()
            fmt = fragment.charFormat()
            if fmt.objectType() == OBJECT:
                transition([])
                result.append(fmt.property(TOKEN))
            else:
                transition(format_tags(fmt))
                result.append(fragment.text().replace('{','{{').replace('\u2028','\n'))
            iterator += 1
        block = block.next()
        if block.isValid(): result.append('\n')
    transition([])
    return ''.join(result)


class RichCellEditor(QTextEdit):
    def __init__(self,window,row,col,parent):
        super().__init__(parent)
        self.window,self.row,self.col = window,row,col
        self.renderer = TagRenderer(self)
        self.document().documentLayout().registerHandler(OBJECT,self.renderer)
        self.setAcceptRichText(False)
        self.setTabChangesFocus(False)
        self.original = ''
        self.initial_source = dump_source(self.document())

    def set_source(self,source):
        self.original = source
        self.blockSignals(True)
        load_source(self.document(),source)
        self.initial_source = dump_source(self.document())
        self.blockSignals(False)

    def source(self):
        value = dump_source(self.document())
        return self.original if value == self.initial_source else value

    def wrap(self,tag):
        cursor = self.textCursor()
        name,_,value = tag.partition('=')
        fmt = QTextCharFormat()
        if name == 'b': fmt.setFontWeight(QFont.Weight.Normal if cursor.charFormat().fontWeight() >= QFont.Weight.Bold else QFont.Weight.Bold)
        elif name == 'i': fmt.setFontItalic(not cursor.charFormat().fontItalic())
        elif name == 'u': fmt.setFontUnderline(not cursor.charFormat().fontUnderline())
        elif name == 'font':
            if value:
                fmt.setProperty(FONT_FILE,value)
                fmt.setFontFamilies([FONT_FAMILIES.get(value,document_font_family())])
            else:
                # Explicit empty property suppresses inherited font overrides.
                fmt.setProperty(FONT_FILE,'')
                fmt.setFontFamilies([self.document().defaultFont().family()])
        elif name == 'size' and value.isdigit() and int(value)>0: fmt.setFontPointSize(int(value))
        elif name == 'color' and QColor(value).isValid(): fmt.setForeground(QColor(value))
        else:
            cursor.beginEditBlock()
            # Inserting a command preserves selected text; paired custom tags wrap it.
            if name in ('w','p'):
                cursor.setPosition(cursor.selectionEnd())
                insert_token(cursor,'{'+tag+'}')
            else:
                start,end = cursor.selectionStart(),cursor.selectionEnd()
                cursor.setPosition(end)
                insert_token(cursor,'{/'+name+'}')
                cursor.setPosition(start)
                insert_token(cursor,'{'+tag+'}')
            cursor.endEditBlock()
            self.setTextCursor(cursor)
            return
        cursor.mergeCharFormat(fmt)
        if not cursor.hasSelection(): self.mergeCurrentCharFormat(fmt)
        self.setTextCursor(cursor)

    def insertFromMimeData(self,data):
        # Keep editor-owned formatting and tokens, and never accept arbitrary HTML.
        if data.hasFormat('application/x-adv-renpy'):
            cursor = self.textCursor()
            temporary = QTextEdit()
            load_source(temporary.document(),bytes(data.data('application/x-adv-renpy')).decode('utf-8'))
            from PySide6.QtGui import QTextDocumentFragment
            cursor.insertFragment(QTextDocumentFragment(temporary.document()))
        else:
            self.insertPlainText(data.text())

    def createMimeDataFromSelection(self):
        from PySide6.QtCore import QMimeData
        from PySide6.QtGui import QTextDocument
        doc = QTextDocument()
        QTextCursor(doc).insertFragment(self.textCursor().selection())
        mime = QMimeData()
        mime.setData('application/x-adv-renpy',dump_source(doc).encode('utf-8'))
        mime.setText(self.textCursor().selectedText().replace('\u2029','\n'))
        return mime

    def keyPressEvent(self,event):
        if not self.textCursor().hasSelection() and self.currentCharFormat().objectType() == OBJECT:
            fmt = QTextCharFormat(self.currentCharFormat())
            fmt.setObjectType(QTextFormat.ObjectTypes.NoObject)
            fmt.clearProperty(TOKEN)
            self.setCurrentCharFormat(fmt)
        from .gui import editor_keypress
        if not editor_keypress(self,event): super().keyPressEvent(event)
