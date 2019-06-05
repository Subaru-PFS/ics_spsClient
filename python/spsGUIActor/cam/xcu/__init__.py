__author__ = 'alefur'

from spsGUIActor.cam.xcu.cooler import CoolerPanel
from spsGUIActor.cam.xcu.gatevalve import GVPanel
from spsGUIActor.cam.xcu.gauge import GaugePanel
from spsGUIActor.cam.xcu.ionpump import IonpumpPanel
from spsGUIActor.cam.xcu.motors import MotorsPanel
from spsGUIActor.cam.xcu.turbo import TurboPanel
from spsGUIActor.control import ControlDialog
from spsGUIActor.modulerow import ModuleRow
from spsGUIActor.widgets import Controllers, ValueMRow


class XcuRow(ModuleRow):
    def __init__(self, camRow):
        self.camRow = camRow
        ModuleRow.__init__(self, module=camRow.module,
                           actorName='xcu_%s%i' % (camRow.arm, camRow.module.smId), actorLabel='XCU')

        self.pressure = ValueMRow(self, 'pressure', 'Pressure(Torr)', 0, '{:g}', controllerName='PCM')
        self.controllers = Controllers(self)

    @property
    def widgets(self):
        return [self.pressure]

    def setOnline(self):
        ModuleRow.setOnline(self)
        self.camRow.setOnline()

    def heartBeat(self):
        self.camRow.heartBeat()

    def createDialog(self, tabWidget):
        self.controlDialog = XcuDialog(self, tabWidget)


class XcuDialog(ControlDialog):
    def __init__(self, xcuRow, tabWidget):
        self.moduleRow = xcuRow
        self.tabWidget = tabWidget

        self.topbar = self.createTopbar()
        self.topbar.insertWidget(0, self.moduleRow.actorStatus)

        self.GVPanel = GVPanel(self)
        self.turboPanel = TurboPanel(self)
        self.gaugePanel = GaugePanel(self)
        self.coolerPanel = CoolerPanel(self)
        self.motorsPanel = MotorsPanel(self)
        self.ionpumpPanel = IonpumpPanel(self)

        for name, tab in self.virtualTabs.items():
            self.tabWidget.addTab(tab, name)

    @property
    def cmdBuffer(self):
        return self.moduleRow.camRow.controlDialog.cmdBuffer

    @property
    def pannels(self):
        return list(self.virtualTabs.values())

    @property
    def virtualTabs(self):
        return dict(Gatevalve=self.GVPanel, Turbo=self.turboPanel, Cooler=self.coolerPanel, Gauge=self.gaugePanel,
                    Motors=self.motorsPanel, Ionpump=self.ionpumpPanel)
