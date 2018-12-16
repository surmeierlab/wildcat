import sys
from PySide2 import QtWidgets
from .voltammetry_plot_widget import VoltammetryPlotWidget
from .kinetics_widget import KineticsWidget


class AnalysisWidget(QtWidgets.QWidget):

    def __init__(self, dm):
        super().__init__()
        self.dm = dm

        self.kw = KineticsWidget(self.dm)
        self.vpw = VoltammetryPlotWidget(self.dm)

        layout = QtWidgets.QHBoxLayout(self)
        self.tab_widget = QtWidgets.QTabWidget()
        self.tab_widget.addTab(self.vpw, 'Voltammetry Plots')
        self.tab_widget.addTab(self.kw, 'Kinetics')

        layout.addWidget(self.tab_widget)
