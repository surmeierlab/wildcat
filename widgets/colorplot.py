import sys
import pyqtgraph as pg
import numpy as np
import pandas as pd
from PyQt5 import QtWidgets, QtGui


class ColorPlot(pg.PlotWidget):

    def __init__(self):
        super().__init__()
        self.data = pd.read_csv('./dev/voltam_data.csv').values.T
        # self.data = np.array([[0, 1, 2], [3, 4, 5], [6, 7, 8]])

        self.dmin = self.data.min()
        self.dmax = self.data.max()
        self.plt = self.plotItem

        # colors from cmap file
        rgbs = np.loadtxt('./dev/voltam_color.csv', delimiter=',')
        alphas = np.full((len(rgbs), 1), 1.0)
        self.colors = np.append(rgbs, alphas, axis=1)

        # set up colorbar
        self.cbar = pg.GradientEditorItem(orientation='right')
        self.cbar.tickSize = 0
        pos = np.linspace(0, 1, len(self.colors))
        self.cbar.setColorMap(pg.ColorMap(pos, self.colors))

        # set up colorbar axis
        cbar_ax = pg.AxisItem('right')
        self.cbar_vb = pg.ViewBox()
        self.plt.scene().addItem(self.cbar_vb)
        self.plt.layout.addItem(self.cbar, 2, 3)
        self.plt.layout.addItem(cbar_ax, 2, 4)
        cbar_ax.linkToView(self.cbar_vb)

        self.cbar_vb.setGeometry(self.plt.vb.sceneBoundingRect())
        self.plt.vb.setMouseEnabled(False, False)
        self.plt.setMenuEnabled(False)
        self.cbar_vb.setRange(yRange=(self.dmin, self.dmax))

        # set up image item
        self.im = pg.ImageItem(self.data)
        pos = np.linspace(self.dmin, self.dmax, len(self.colors))
        cmap = pg.ColorMap(pos, self.colors)
        lut = cmap.getLookupTable(self.dmin, self.dmax, self.data.size)
        self.im.setLookupTable(lut)
        self.plt.vb.addItem(self.im)
        self.plt.vb.setLimits(xMin=-1, xMax=self.data.shape[0]+1, yMin=-1, yMax=self.data.shape[1]+1)

        # add marker to plot vb
        self.row_marker = pg.InfiniteLine(angle=0, pen=pg.mkPen('b', width=2.0), movable=True)
        self.col_marker = pg.InfiniteLine(pen=pg.mkPen('g', width=2.0), movable=True)
        self.plt.vb.addItem(self.row_marker)
        self.plt.vb.addItem(self.col_marker)
        self.row_marker.setBounds((0, self.data.shape[1]))
        self.col_marker.setBounds((0, self.data.shape[0]))
        # self.find_peak()
        # self.marker.sigDragged.connect(self.marker_moved)

        # connect cbar_vb for when Y axis changes
        self.cbar_vb.sigYRangeChanged.connect(self.update_levels)
        self._update_views()
        self.plt.vb.sigResized.connect(self._update_views)

    def _update_views(self):
        self.cbar_vb.setGeometry(self.plt.vb.sceneBoundingRect())
        self.cbar_vb.linkedViewChanged(self.plt.vb, self.cbar_vb.XAxis)

    def update_levels(self, vb):
        """Updates heatmap levels based on changes in the colorbar axis
        and the associated viewbox"""
        _, yrange = vb.viewRange()
        self.im.setImage(levels=yrange)

    def marker_moved(self, marker):
        ix = int(marker.value())
        try:
            dmin = self.data[ix, :].min()
            dmax = self.data[ix, :].max()
        except IndexError:
            pass

    def auto_range(self):
        self.cbar_vb.setRange(yRange=(self.dmin, self.dmax))

    def find_peak(self):
        # note that np.where() technically returns (row, col)
        # ImageItem displays each row as essentially a column
        # e.g. for a 3x3 matrix, [0, 0] is the bottom left corner
        # and [2, 2] is the top right corner
        col, row = np.where(self.data == self.data.max())
        self.col_marker.setValue(col)
        self.row_marker.setValue(row)

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    ex = ColorPlot()
    ex.show()
    sys.exit(app.exec_())
