import sys
import pyqtgraph as pg
from heatmap_widget import HeatmapWidget
from PyQt5 import QtWidgets, QtGui
import numpy as np


class VoltammetryPlotWidget(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()
        self.setStyleSheet('background-color: white;')
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')

        layout = QtWidgets.QHBoxLayout(self)

        self.hmw = HeatmapWidget()
        self.heatmap = self.hmw.heatmap

        self.pw = pg.GraphicsLayoutWidget()

        self.iplot = self.pw.addPlot(row=0, col=0, title='Current vs. Time')
        self.vplot = self.pw.addPlot(row=1, col=0, title="Voltammogram")
        self.iplot.plot()
        self.vplot.plot()

        layout.addWidget(self.pw)
        layout.addWidget(self.hmw)

        self.heatmap.row_marker.sigPositionChanged.connect(self.update_iplot)
        self.heatmap.col_marker.sigPositionChanged.connect(self.update_vplot)

        up = np.linspace(-0.4, 1.3, int(171/2)+1)
        down = up[::-1][1:]
        self.vms = np.append(up, down)

        self.heatmap.find_peak()

    def update_iplot(self, marker):
        """Updates current plot when row marker position is changed"""
        ix = int(marker.value())
        item = self.iplot.listDataItems()[0]
        try:
            data = self.heatmap.data[:, ix]
            item.setData(data, pen=pg.mkPen('b', width=1.5))
        except IndexError:
            pass

    def update_vplot(self, marker):
        """Updates voltammogram plot when column marker position is changed"""
        ix = int(marker.value())
        item = self.vplot.listDataItems()[0]
        try:
            data = self.heatmap.data[ix, :]
            item.setData(x=self.vms, y=data, pen=pg.mkPen('b', width=1.5))
        except IndexError:
            pass



if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ex = VoltammetryPlotWidget()
    ex.show()
    sys.exit(app.exec_())

