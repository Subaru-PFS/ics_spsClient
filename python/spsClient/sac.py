__author__ = 'alefur'
from PyQt5.QtWidgets import QComboBox
from spsClient.modulerow import ModuleRow
from spsClient.widgets import ValueGB, CommandsGB, ControlDialog, ControlPanel, DoubleSpinBoxGB, CmdButton, CustomedCmd


class SacRow(ModuleRow):
    def __init__(self, aitModule):
        ModuleRow.__init__(self, module=aitModule, actorName='sac', actorLabel='SAC')

        self.state = ValueGB(self, 'metaFSM', '', 0, '{:s}')
        self.substate = ValueGB(self, 'metaFSM', '', 1, '{:s}')

        self.pentaPosition = ValueGB(self, 'lsPenta', 'Penta', 2, '{:.3f}')
        self.detectorPosition = ValueGB(self, 'lsDetector', 'Detector', 2, '{:.3f}')

    @property
    def customWidgets(self):

        widgets = [self.state, self.substate, self.pentaPosition, self.detectorPosition]

        try:
            widgets += self.controlDialog.customWidgets
        except AttributeError:
            pass

        return widgets

    def showDetails(self):
        self.controlDialog = SacDialog(self)
        self.controlDialog.show()


class MoveCmd(CustomedCmd):
    limits = dict(penta=(-450, 450),
                  detector=(0, 12))

    def __init__(self, controlPanel, stage):
        CustomedCmd.__init__(self, controlPanel, buttonLabel='MOVE')

        self.stage = stage
        l_bound, u_bound = MoveCmd.limits[stage]

        self.combo = QComboBox()
        self.combo.addItems(['abs', 'rel'])

        self.distSpinbox = DoubleSpinBoxGB('Dist', l_bound, u_bound, 3)

        self.addWidget(self.combo, 0, 1)
        self.addWidget(self.distSpinbox, 0, 2)

    def buildCmd(self):
        reference = '' if self.combo.currentText() == 'rel' else self.combo.currentText()
        cmdStr = 'sac move %s=%.2f %s' % (self.stage, self.distSpinbox.getValue(), reference)

        return cmdStr


class Looptime(ValueGB):
    def __init__(self, ccdCmd):
        self.ccdCmd = ccdCmd
        ValueGB.__init__(self, ccdCmd.controlPanel.moduleRow, 'looptime', '', 0, '{:.2f}')

    def setText(self, txt):
        if float(txt) > 0:
            self.ccdCmd.stopLoop.setVisible(True)
            self.ccdCmd.startLoop.setVisible(False)
        else:
            self.ccdCmd.stopLoop.setVisible(False)
            self.ccdCmd.startLoop.setVisible(True)


class ExposeCmd(CustomedCmd):
    def __init__(self, controlPanel):
        CustomedCmd.__init__(self, controlPanel, buttonLabel='EXPOSE')

        self.combo = QComboBox()
        self.combo.addItems(['object', 'background'])

        self.exptime = DoubleSpinBoxGB('exptime', 0, 300, 2)

        self.addWidget(self.combo, 0, 1)
        self.addWidget(self.exptime, 0, 2)

    def buildCmd(self):
        exptype = 'expose' if self.combo.currentText() == 'object' else 'background'
        cmdStr = 'sac ccd %s exptime=%.2f' % (exptype, self.exptime.getValue())

        return cmdStr


class StageCommands(CommandsGB):
    def __init__(self, controlPanel, stage):
        CommandsGB.__init__(self, controlPanel)
        self.initButton = CmdButton(controlPanel=controlPanel, label='INIT', cmdStr='sac stages %s init' % stage)

        self.moveCmd = MoveCmd(controlPanel=controlPanel, stage=stage)

        self.grid.addWidget(self.initButton, 0, 0)
        self.grid.addLayout(self.moveCmd, 1, 0, 1, 3)

    @property
    def buttons(self):
        return [self.initButton, self.moveCmd.button]


class StagePanel(ControlPanel):
    def __init__(self, controlDialog, stage):
        label = stage.capitalize()
        ControlPanel.__init__(self, controlDialog, '%s Stage' % stage.capitalize())

        self.state = ValueGB(self.moduleRow, 'ls%s' % label, '', 0, '{:s}')
        self.substate = ValueGB(self.moduleRow, 'ls%s' % label, '', 1, '{:s}')
        self.position = ValueGB(self.moduleRow, 'ls%s' % label, 'Position', 2, '{:.3f}')

        self.commands = StageCommands(self, stage)

        self.grid.addWidget(self.state, 0, 0)
        self.grid.addWidget(self.substate, 0, 1)
        self.grid.addWidget(self.position, 0, 2)

        self.grid.addWidget(self.commands, 0, 3, 3, 3)

    @property
    def customWidgets(self):
        return [self.grid.itemAt(i).widget() for i in range(self.grid.count())] + self.commands.buttons


class CcdCommands(CommandsGB):
    def __init__(self, controlPanel):
        CommandsGB.__init__(self, controlPanel)

        self.connectButton = CmdButton(controlPanel=controlPanel, label='CONNECT', cmdStr='sac ccd connect')
        self.exposeCmd = ExposeCmd(controlPanel=controlPanel)
        self.startLoop = CmdButton(controlPanel=controlPanel, label='START LOOP', cmdStr='sac ccd loop start')
        self.stopLoop = CmdButton(controlPanel=controlPanel, label='STOP LOOP', cmdStr='sac ccd loop stop')
        self.looptime = Looptime(self)

        self.grid.addWidget(self.connectButton, 0, 0)
        self.grid.addLayout(self.exposeCmd, 1, 0, 1, 3)
        self.grid.addWidget(self.startLoop, 2, 0)
        self.grid.addWidget(self.stopLoop, 2, 0)

    @property
    def buttons(self):
        return [self.connectButton, self.exposeCmd.button, self.startLoop, self.stopLoop]


class CcdPanel(ControlPanel):
    def __init__(self, controlDialog):
        ControlPanel.__init__(self, controlDialog, 'CCD')

        self.state = ValueGB(self.moduleRow, 'ccd', '', 0, '{:s}')
        self.substate = ValueGB(self.moduleRow, 'ccd', '', 1, '{:s}')

        self.commands = CcdCommands(self)

        self.grid.addWidget(self.state, 0, 0)
        self.grid.addWidget(self.substate, 0, 1)

        self.grid.addWidget(self.commands, 0, 2, 3, 3)

    @property
    def customWidgets(self):
        return [self.grid.itemAt(i).widget() for i in range(self.grid.count())] + self.commands.buttons


class SacDialog(ControlDialog):
    def __init__(self, sacRow):
        ControlDialog.__init__(self, moduleRow=sacRow)

        self.detectorPanel = StagePanel(self, 'detector')
        self.pentaPanel = StagePanel(self, 'penta')
        self.ccdPanel = CcdPanel(self)

        self.grid.addWidget(self.detectorPanel, 0, 0)
        self.grid.addWidget(self.pentaPanel, 1, 0)
        self.grid.addWidget(self.ccdPanel, 2, 0)

    @property
    def customWidgets(self):
        return self.detectorPanel.customWidgets + self.pentaPanel.customWidgets, self.ccdPanel.customWidgets