import sys
import pyqtgraph as pg
from PyQt5 import QtGui, QtWidgets
import numpy as np
from scipy.optimize import curve_fit


class KineticsWidget(QtWidgets.QWidget):

    def __init__(self, dm=None):
        super().__init__()
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')

        self.dm = dm

        layout = QtWidgets.QHBoxLayout(self)

        # column of values
        left_col = QtWidgets.QVBoxLayout()
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed,
                                            QtWidgets.QSizePolicy.Fixed)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)

        # rise tau
        self.rise_layout = QtWidgets.QHBoxLayout()
        self.rise_label = QtWidgets.QLabel('Rise tau: ')
        self.rise_val = QtWidgets.QLineEdit('test')
        self.rise_val.setSizePolicy(size_policy)
        self.rise_val.setFixedWidth(100)
        self.rise_val.setReadOnly(True)
        self.rise_layout.addWidget(self.rise_label)
        self.rise_layout.addWidget(self.rise_val)

        run_btn = QtWidgets.QPushButton('Run Fit')

        left_col.addLayout(self.rise_layout)
        left_col.addWidget(run_btn)

        # plot widget
        self.pw = pg.PlotWidget()
        self.pw.plotItem.setLabel('left', 'Current (%s)' % self.dm.data_unit)
        self.plot = self.pw.plotItem.plot()

        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.VLine)

        layout.addLayout(left_col)
        layout.addWidget(line)
        layout.addWidget(self.pw)

        self.dm.sigIPDataChanged.connect(self.set_plot_data)

    def set_plot_data(self):
        dlen = len(self.dm.ip_data)
        stop = dlen*(1/self.dm.sampling_freq) - (1/self.dm.sampling_freq)
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
