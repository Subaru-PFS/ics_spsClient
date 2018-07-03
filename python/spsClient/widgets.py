__author__ = 'alefur'
from datetime import datetime as dt
from functools import partial

from PyQt5.QtGui import QFont, QTextCursor
from PyQt5.QtWidgets import QPlainTextEdit, QLabel, QPushButton, QDialog, QGroupBox, QVBoxLayout, QGridLayout, \
    QDialogButtonBox, QDoubleSpinBox

state2color = {"WIPING": ('blue', 'white'),
               "INTEGRATING": ('yellow', 'black'),
               "READING": ('orange', 'white'),
               "EXPOSING": ('yellow', 'black'),
               "IDLE": ('green', 'white'),
               "LOADING": ('blue', 'white'),
               "LOADED": ('blue', 'white'),
               "INITIALISING": ('yellow', 'black'),
               "WARMING": ('orange', 'white'),
               "MOVING": ('orange', 'white'),
               "BUSY": ('orange', 'white'),
               "NAN": ('red', 'white'),
               "FAILED": ('red', 'white'),
               "ONLINE": ('green', 'white'),
               "OFFLINE": ('red', 'white'),
               "ON": ('green', 'white'),
               "OFF": ('red', 'white'),
               "CONNECTED": ('green', 'white'),
               "operation": ('green', 'white'),
               "simulation": ('orange', 'white'),
               "nan": ('red', 'white'),
               "undef": ('red', 'white'),
               "off": ('red', 'white'),
               "on": ('green', 'white'),
               }


class ValueGB(QGroupBox):
    def __init__(self, moduleRow, key, title, ind, fmt, fontSize=11, callNow=True, keyvar=False):

        keyvar = moduleRow.keyVarDict[key] if not moduleRow is None else keyvar
        self.keyvar = keyvar
        self.title = title
        self.fontSize = fontSize

        QGroupBox.__init__(self)
        self.setTitle('%s' % self.title)

        self.grid = QGridLayout()
        self.value = QLabel()

        self.grid.addWidget(self.value, 0, 0)
        self.setLayout(self.grid)
        self.setColor('black')

        self.cb = partial(self.updateVals, ind, fmt)
        self.keyvar.addCallback(self.cb, callNow=callNow)

    def __del__(self):
        self.keyvar.removeCallback(self.cb)

    def updateVals(self, ind, fmt, keyvar):
        values = keyvar.getValue(doRaise=False)
        values = (values,) if not isinstance(values, tuple) else values

        value = values[ind]

        try:
            strValue = fmt.format(value)
        except TypeError:
            strValue = 'nan'

        self.setText(strValue)

    def setColor(self, background, police='white'):
        if background == "red":
            bckColor = 'qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0  #f43131, stop: 1 #5e1414)'

        elif background == "green":
            bckColor = 'qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0  #45f42e, stop: 1 #195511)'

        elif background == "blue":
            bckColor = 'qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0  #3168f4, stop: 1 #14195e)'

        elif background == "yellow":
            bckColor = 'qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0  #edf431, stop: 1 #5e5b14)'

        elif background == "orange":
            bckColor = 'qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0  #f4a431, stop: 1 #5e4a14)'

        else:
            bckColor = 'qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0  #dfdfdf, stop: 1 #000000)'

        self.setStyleSheet(
            "QGroupBox {font-size: 9pt; background-color: %s ;border: 1px solid gray;border-radius: 3px;margin-top: 1ex;} " % bckColor +
            "QGroupBox::title {subcontrol-origin: margin;subcontrol-position: top center; padding: 0 3px;}")

        self.value.setStyleSheet(
            "QLabel{font-size: %ipt; qproperty-alignment: AlignCenter; color:%s;}" % (self.fontSize, police))

        return bckColor

    def setText(self, txt):
        self.value.setText(txt)
        self.customize()

    def customize(self):
        text = self.value.text()

        try:
            background, police = state2color[text]
        except KeyError:
            background, police = 'green', 'white'

        self.setColor(background=background, police=police)


class Coordinates(QGroupBox):
    posName = ['X', 'Y', 'Z', 'U', 'V', 'W']

    def __init__(self, moduleRow, key, title, fontSize=11):
        QGroupBox.__init__(self)
        self.grid = QGridLayout()

        self.widgets = [ValueGB(moduleRow, key, pos, i, '{:.5f}', fontSize) for i, pos in enumerate(Coordinates.posName)]

        for i, widget in enumerate(self.widgets):
            self.grid.addWidget(widget, 0, i)

        self.setTitle(title)
        self.setLayout(self.grid)
        self.setStyleSheet(
            "QGroupBox {font-size: 9pt; border: 1px solid #d7d4d1;border-radius: 3px;margin-top: 1ex;} " +
            "QGroupBox::title {subcontrol-origin: margin;subcontrol-position: top center; padding: 0 3px;}")


class CommandsGB(QGroupBox):
    def __init__(self, controlPannel):
        self.controlPannel= controlPannel
        QGroupBox.__init__(self)
        self.grid = QGridLayout()

        self.setTitle('Commands')
        self.setLayout(self.grid)
        self.setStyleSheet(
            "QGroupBox {font-size: 9pt; border: 1px solid #d7d4d1;border-radius: 3px;margin-top: 1ex;} " +
            "QGroupBox::title {subcontrol-origin: margin;subcontrol-position: top center; padding: 0 3px;}")

    @property
    def widgets(self):
        return []


class ControlPannel(QGroupBox):
    def __init__(self, controlDialog, title):
        QGroupBox.__init__(self)
        self.controlDialog = controlDialog
        self.grid = QGridLayout()
        self.setLayout(self.grid)

        self.setTitle(title)
        self.setCheckable(True)

        self.clicked.connect(self.showHide)

    @property
    def moduleRow(self):
        return self.controlDialog.moduleRow

    @property
    def customWidgets(self):
        return [self.grid.itemAt(i).widget() for i in range(self.grid.count())]

    def showHide(self):
        bool = True if self.isChecked() else False

        for widget in self.customWidgets:
            widget.setVisible(bool)


class ControlDialog(QDialog):
    def __init__(self, moduleRow, title=False):
        title = moduleRow.actorLabel if not title else title
        QDialog.__init__(self, parent=moduleRow.mwindow.spsClient)

        self.vbox = QVBoxLayout()
        self.grid = QGridLayout()
        self.cmdBuffer = dict()

        self.moduleRow = moduleRow

        buttonBox = QDialogButtonBox(QDialogButtonBox.Apply | QDialogButtonBox.Discard)
        buttonBox.button(QDialogButtonBox.Apply).clicked.connect(self.sendCommands)
        buttonBox.button(QDialogButtonBox.Discard).clicked.connect(self.cancelCommands)

        self.vbox.addLayout(self.grid)
        self.vbox.addWidget(buttonBox)

        self.setLayout(self.vbox)
        self.setVisible(True)
        self.setWindowTitle(title)

    def addCommand(self, button, cmdStr):
        self.cmdBuffer[button] = cmdStr

    def clearCommand(self, button):
        self.cmdBuffer.pop(button, None)

    def sendCommands(self):
        for button, cmdStr in self.cmdBuffer.items():
            self.moduleRow.mwindow.sendCommand(fullCmd=cmdStr)
            button.setChecked(0)

        self.cmdBuffer.clear()

    def cancelCommands(self):
        self.cmdBuffer.clear()


class DoubleSpinBoxGB(QGroupBox):
    def __init__(self, title, vmin, vmax, decimals):

        QGroupBox.__init__(self)
        self.setTitle('%s' % title)

        self.grid = QGridLayout()
        self.value = QDoubleSpinBox()
        self.value.setValue(0)
        self.value.setDecimals(decimals)
        self.value.setRange(vmin, vmax)
        self.grid.addWidget(self.value, 0, 0)

        self.setLayout(self.grid)

    def setValue(self, value):
        self.value.setValue(value)

    def getValue(self):
        return float(self.value.value())


class CmdButton(QPushButton):
    def __init__(self, controlPannel, label):
        self.controlPannel = controlPannel
        QPushButton.__init__(self, label)
        self.setCheckable(True)
        self.clicked.connect(self.getCommand)
        self.setEnabled(False)

    @property
    def controlDialog(self):
        return self.controlPannel.controlDialog

    def getCommand(self):
        pass


class LogArea(QPlainTextEdit):
    def __init__(self):
        QPlainTextEdit.__init__(self)
        self.logArea = QPlainTextEdit()
        self.setMaximumBlockCount(10000)
        self.setReadOnly(True)

        self.setStyleSheet("background-color: black;color:white;")
        self.setFont(QFont("Monospace", 8))

    def newLine(self, line):
        self.insertPlainText("\n%s  %s" % (dt.now().strftime("%H:%M:%S.%f"), line))
        self.moveCursor(QTextCursor.End)
        self.ensureCursorVisible()

    def trick(self, qlineedit):
        self.newLine(qlineedit.text())