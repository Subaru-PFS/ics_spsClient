__author__ = 'alefur'
import spsClient.styles as styles
from PyQt5.QtWidgets import QProgressBar
from spsClient.control import ControlDialog
from spsClient.enu.bia import BiaPanel
from spsClient.enu.rexm import RexmPanel
from spsClient.enu.shutters import ShuttersPanel
from spsClient.enu.slit import SlitPanel
from spsClient.modulerow import ModuleRow
from spsClient.widgets import ValueGB


class ElapsedTime(QProgressBar):
    def __init__(self, enuRow):
        QProgressBar.__init__(self)
        self.setFormat('EXPOSING \r\n' + '%p%')
        self.enuRow = enuRow
        self.enuRow.keyVarDict['elapsedTime'].addCallback(self.updateBar, callNow=False)
        self.enuRow.keyVarDict['bshFSM'].addCallback(self.hideBar)

        self.setFixedSize(100, 45)

    def setExptime(self, exptime):
        self.setRange(0, exptime)

    def updateBar(self, keyvar):
        try:
            val = keyvar.getValue()
        except ValueError:
            val = 0

        self.setValue(val)

    def hideBar(self, keyvar):
        try:
            state, substate = keyvar.getValue()
            if substate == 'EXPOSING':
                self.enuRow.addElaspedTime()
                self.enuRow.substate.hide()
                self.show()
            else:
                raise ValueError

        except ValueError:
            self.resetValue()

    def resetValue(self):
        self.hide()
        self.setValue(0)
        self.enuRow.substate.show()


class EnuRow(ModuleRow):
    def __init__(self, specModule):
        ModuleRow.__init__(self, module=specModule, actorName='enu_sm%i' % specModule.smId, actorLabel='ENU')

        self.state = ValueGB(self, 'metaFSM', '', 0, '{:s}', fontSize=styles.bigFont)
        self.substate = ValueGB(self, 'metaFSM', '', 1, '{:s}', fontSize=styles.bigFont)

        self.rexm = ValueGB(self, 'rexm', 'Red Resolution', 0, '{:s}', fontSize=styles.bigFont)
        self.slit = ValueGB(self, 'slitLocation', 'FCA_Position', 0, '{:s}', fontSize=styles.bigFont)
        self.shutters = ValueGB(self, 'shutters', 'SHA_Position', 0, '{:s}', fontSize=styles.bigFont)
        self.bia = ValueGB(self, 'bia', 'BIA_State', 0, '{:s}', fontSize=styles.bigFont)
        self.elapsedTime = ElapsedTime(self)

        self.keyVarDict['integratingTime'].addCallback(self.setExptime, callNow=False)

        self.controlDialog = EnuDialog(self)

    @property
    def customWidgets(self):
        return [self.state, self.substate, self.rexm, self.slit, self.shutters, self.bia]

    def setExptime(self, keyvar):
        try:
            exptime = keyvar.getValue()
        except ValueError:
            return

        self.elapsedTime.setExptime(exptime)

    def addElaspedTime(self):

        self.module.grid.addWidget(self.elapsedTime, self.lineNB, 2)

    def removeWidget(self, widget):
        self.state.show()
        self.module.grid.removeWidget(widget)
        widget.deleteLater()


class EnuDialog(ControlDialog):
    def __init__(self, enuRow):
        ControlDialog.__init__(self, moduleRow=enuRow, title='Entrance Unit SM%i' % enuRow.module.smId)

        self.slitPanel = SlitPanel(self)
        self.shuttersPanel = ShuttersPanel(self)
        self.biaPanel = BiaPanel(self)
        self.rexmPanel = RexmPanel(self)

        self.tabWidget.addTab(self.slitPanel, 'FCA')
        self.tabWidget.addTab(self.shuttersPanel, 'SHUTTERS')
        self.tabWidget.addTab(self.biaPanel, 'BIA')
        self.tabWidget.addTab(self.rexmPanel, 'RDA')

    @property
    def customWidgets(self):
        return [self.reload] + self.slitPanel.allWidgets + self.shuttersPanel.allWidgets \
               + self.biaPanel.allWidgets + self.rexmPanel.allWidgets
