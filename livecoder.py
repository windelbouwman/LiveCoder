import sys, keyword, base64, traceback, io
from PyQt4.QtCore import *
from PyQt4.QtGui import *

windelpng = base64.decodestring(b'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAAXNSR0IArs4c6QAAAAZiS0dEAP8A\n/wD/oL2nkwAAAAlwSFlzAAALEwAACxMBAJqcGAAAAAd0SU1FB9sJEhMKBk7B678AAAA/SURBVFjD\n7dbBCQAgDATBi9h/y7EFA4Kf2QLCwH1S6XQu6sqoujublc8BAAAAAAAAAAB8B+zXT6YJAAAAAKYd\nWSgFQNUyijIAAAAASUVORK5CYII=\n')

class LiveCoder(QWidget):
   def __init__(self):
      super(LiveCoder, self).__init__()
      self.edit = QTextEdit()
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
      self.completer = QCompleter(keyword.kwlist)
      #self.edit.setCompleter(self.completer)
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
      #sys.stdout = myoutput
      try:
         exec(code)
      except SyntaxError as e:
         self.setError(e.msg, e.lineno)
      except:
         type, value, traceb = sys.exc_info()
         stack = traceback.extract_tb(traceb)
         fn, lineno, fun, txt = stack[-1]
         self.setError(str(value), lineno)
      else:
         self.setError()
      self.outputText.clear()
      self.outputText.setPlainText(myoutput.getvalue())
      sys.stdout = oldstdout
   def insertCompletion(self, completion):
      pass
   def keyPressEvent(self, e):
      print(e, type(e))
      e.ignore()
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
