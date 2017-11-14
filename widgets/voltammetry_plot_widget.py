import sys
import pyqtgraph as pg
from widgets.colorplot_widget import ColorPlotWidget
from PyQt5 import QtWidgets
import numpy as np


class VoltammetryPlotWidget(QtWidgets.QWidget):

    def __init__(self, dm=None):
        super().__init__()
        self.setStyleSheet('background-color: white;')
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')

        self.dm = dm

        layout = QtWidgets.QHBoxLayout(self)

        self.cpw = ColorPlotWidget(self.dm)
        self.colorplot = self.cpw.colorplot

        self.pw = pg.GraphicsLayoutWidget()

        self.iplot = self.pw.addPlot(row=0, col=0, title='Current vs. Time')
        self.vplot = self.pw.addPlot(row=1, col=0, title="Voltammogram")
        self.peak_txt = pg.TextItem()
        # self.imin_text = pg.TextItem()
        self.iplot.addItem(self.peak_txt)
        # self.iplot.addItem(self.imin_text)
        # self.iplot_txt.setPos(0, 0)
        self.iplot.plot()
        self.vplot.plot()

        layout.addWidget(self.pw)
        layout.addWidget(self.cpw)

        self.colorplot.row_marker.sigPositionChanged.connect(self.update_iplot)
        self.colorplot.col_marker.sigPositionChanged.connect(self.update_vplot)
        self.dm.sigDataChanged.connect(lambda:
                                       self.update_iplot(self.colorplot.row_marker))
        self.dm.sigDataChanged.connect(lambda:
                                       self.update_vplot(self.colorplot.col_marker))
        self.colorplot.find_peak()

    def update_iplot(self, marker):
        """Updates current plot when row marker position is changed"""
        ix = int(marker.value())
        item = self.iplot.listDataItems()[0]
        try:
            data = self.colorplot.data[:, ix]
            item.setData(data, pen=pg.mkPen('b', width=1.5))
            ixmax = np.argmax(data)
            ixmin = np.argmin(data)
            if abs(data[ixmax]) >= abs(data[ixmin]):
                peak_ix = ixmax
                anchor_y = 1
            else:
                peak_ix = ixmin
                anchor_y = 0
            html = '''<span style="color: #000000; font-size: 12pt;">
                      Peak = {:0.2f}</span>'''.format(data[peak_ix])
            self.peak_txt.setHtml(html)
            self.peak_txt.setPos(peak_ix, data[peak_ix])
            self.peak_txt.setAnchor((0, anchor_y))

        except IndexError:
            pass

    def update_vplot(self, marker):
        """Updates voltammogram plot when column marker position is changed"""
        ix = int(marker.value())
        item = self.vplot.listDataItems()[0]
        try:
            data = self.colorplot.data[ix, :]
            item.setData(x=self.dm.vms, y=data, pen=pg.mkPen('b', width=1.5))
        except IndexError:
            pass


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ex = VoltammetryPlotWidget()
    ex.show()
    sys.exit(app.exec_())
