import sys
import pyqtgraph as pg
from PyQt5 import QtWidgets
import numpy as np
from scipy.optimize import curve_fit


class KineticsWidget(QtWidgets.QWidget):

    def __init__(self, dm=None):
        super().__init__()
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')

        self.dm = dm

        layout = QtWidgets.QHBoxLayout(self)
        self.pw = pg.PlotWidget()
        self.plot = self.pw.plotItem.plot()

        run_btn = QtWidgets.QPushButton('Run Fit')
        layout.addWidget(run_btn)
        layout.addWidget(self.pw)

        self.dm.sigIPDataChanged.connect(self.set_plot_data)

    def set_plot_data(self):
        dlen = len(self.dm.ip_data)
        stop = dlen*(1/self.dm.scan_rate) - (1/self.dm.scan_rate)
        x = np.linspace(0, stop, dlen)
        self.plot.setData(x, self.dm.ip_data, pen=pg.mkPen('b', width=1.5),
                          symbol='o')

    def fit_decay(self, subset, time):
        def eq(x, a, b, c):
            return a*np.exp(-x*b) + c

        guess = [1, 1e-3, 0]

        popt, pcov = curve_fit(eq, time, subset, p0=guess)

        fit = eq(time, *popt)

        return fit, popt

    def fit_rise(self, subset, time):
        def eq(x, a, b, c):
            return a*(1-np.exp(-x*b)) + c

        guess = [1, 1e-3, 0]

        popt, pcov = curve_fit(eq, time, subset, p0=guess)

        fit = eq(time, *popt)

        return fit, popt
