import sys, keyword, base64, traceback, io
from PyQt4.QtCore import *
from PyQt4.QtGui import *

windelpng = base64.decodestring(b'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAAXNSR0IArs4c6QAAAAZiS0dEAP8A\n/wD/oL2nkwAAAAlwSFlzAAALEwAACxMBAJqcGAAAAAd0SU1FB9sJEhMKBk7B678AAAA/SURBVFjD\n7dbBCQAgDATBi9h/y7EFA4Kf2QLCwH1S6XQu6sqoujublc8BAAAAAAAAAAB8B+zXT6YJAAAAAKYd\nWSgFQNUyijIAAAAASUVORK5CYII=\n')

class CodeEdit(QTextEdit):
   def __init__(self):
      super(CodeEdit, self).__init__()
      self.completer = QCompleter()
      self.completer.setWidget(self)
      self.completer.activated[str].connect(self.insertCompletion)
      self.wordModel = QStringListModel()
      self.completer.setModel(self.wordModel)
      self.symbolDict = {}
      self.wordModel.setStringList(keyword.kwlist)
   def keyPressEvent(self, e):
      if self.completer.popup().isVisible() and e.key() in [Qt.Key_Escape, Qt.Key_Return, Qt.Key_Enter]:
         e.ignore()
         return
      if e.key() == Qt.Key_Period:
         # Popup completer
         cr = self.cursorRect()
         cr.setWidth(200)
         
         tc = self.textCursor()
         tc.select(QTextCursor.WordUnderCursor)
         cursymbol = tc.selectedText()
         if cursymbol in self.symbolDict:
            words = self.symbolDict[cursymbol]
            self.wordModel.setStringList(words)
         self.completer.complete(cr)
      super(CodeEdit, self).keyPressEvent(e)
   def insertCompletion(self, completion):
      tc = self.textCursor()
      tc.insertText(completion)

class LiveCoder(QWidget):
   def __init__(self):
      super(LiveCoder, self).__init__()
      self.edit = CodeEdit()
      pm = QPixmap()
      pm.loadFromData(windelpng)
      self.setWindowIcon(QIcon(pm))
      self.setWindowTitle('LiveCoder')
      l = QVBoxLayout(self)
      l.addWidget(self.edit)
      self.edit.setFontPointSize(20)
      self.edit.setFontFamily('Courier')
      self.outputText = QTextEdit()
      self.outputText.setReadOnly(True)
      l.addWidget(self.outputText)
      self.errorText = QLabel(self.edit)
      self.errorText.setStyleSheet("QLabel { background-color : red; color : white; border-radius: 4; padding: 5}")
      self.docText = QLabel(self.edit)
      self.docText.setStyleSheet("QLabel { background-color : green; color : black; border-radius: 4; padding: 5}")
      self.docText.hide()
      # signals:
      self.edit.textChanged.connect(self.runCode)
      # Restore settings:
      self.settings = QSettings('WindelSoft', 'LiveCoder')
      if self.settings.contains("geometry"):
         self.restoreGeometry(self.settings.value("geometry"))
      if self.settings.contains("livecode"):
         code = self.settings.value("livecode")
         self.edit.setPlainText(code)
   def saveSettings(self):
      code = self.edit.toPlainText()
      self.settings.setValue('livecode', code)
      self.settings.setValue('geometry', self.saveGeometry())
   def runCode(self):
      code = self.edit.toPlainText()
      myoutput = io.StringIO()
      oldstdout = sys.stdout
      globs = {}
      locs = {}
      succes = False
      try:
         exec(code, globs, locs)
         succes = True
      except SyntaxError as e:
         self.setError(e.msg, e.lineno)
      except:
         typ, value, traceb = sys.exc_info()
         stack = traceback.extract_tb(traceb)
         fn, lineno, fun, txt = stack[-1]
         self.setError(str(value), lineno)
      else:
         self.setError()
      if succes:
         for locname in locs:
            # Pass this as completion options.
            self.edit.symbolDict[locname] = dir(locs[locname])
      self.outputText.clear()
      self.outputText.setPlainText(myoutput.getvalue())
      sys.stdout = oldstdout
   def setError(self, msg='', lineno=None):
      if msg:
         self.errorText.show()
         self.errorText.setText(msg)
         self.errorText.adjustSize()
         # Positioning:
         x, y = 140, 40
         if lineno:
            block = self.edit.document().findBlockByLineNumber(lineno)
            cursor = QTextCursor(block)
            rect = self.edit.cursorRect(cursor)
            # an error on the last line does not show, the rect is too high?
            #print(lineno, block, rect)
            # Try to center in height around the error line:
            y = rect.y() - rect.height() / 2 - self.errorText.height() / 2
            x = self.edit.width() - self.errorText.width() - 5
         self.errorText.move(QPoint(x, y))
      else:
         self.errorText.hide()

app = QApplication(sys.argv)
lc = LiveCoder()
lc.show()
app.lastWindowClosed.connect(lc.saveSettings)
app.exec_()
