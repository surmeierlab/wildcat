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
        self.time = None
        

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
        self.rise_val = QtWidgets.QLineEdit()
        self.rise_val.setSizePolicy(size_policy)
        self.rise_val.setFixedWidth(100)
        self.rise_val.setReadOnly(True)
        self.rise_layout.addWidget(self.rise_label)
        self.rise_layout.addWidget(self.rise_val)

        # decay tau
        self.decay_layout = QtWidgets.QHBoxLayout()
        self.decay_label = QtWidgets.QLabel('Decay tau: ')
        self.decay_val = QtWidgets.QLineEdit()
        self.decay_val.setSizePolicy(size_policy)
        self.decay_val.setFixedWidth(100)
        self.decay_val.setReadOnly(True)
        self.decay_layout.addWidget(self.decay_label)
        self.decay_layout.addWidget(self.decay_val)

        run_btn = QtWidgets.QPushButton('Run Fit')
        run_btn.clicked.connect(self.fit_transient)

        left_col.addLayout(self.rise_layout)
        left_col.addLayout(self.decay_layout)
        left_col.addWidget(run_btn)

        # plot widget
        self.pw = pg.PlotWidget()
        self.pw.plotItem.setLabel('left', 'Current (%s)' % self.dm.data_unit)
        self.plot = self.pw.plotItem.plot()
        self.fit_plot = self.pw.plotItem.plot()

        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.VLine)

        layout.addLayout(left_col)
        layout.addWidget(line)
        layout.addWidget(self.pw)

        self.dm.sigIPDataChanged.connect(self.set_plot_data)

    def set_plot_data(self):
        dlen = len(self.dm.ip_data)
        stop = dlen*(1/self.dm.sampling_freq) - (1/self.dm.sampling_freq)
        self.time = np.linspace(0, stop, dlen)

        self.plot.setData(self.time, self.dm.ip_data, pen=pg.mkPen('b', width=1.5),
                          symbol='o')
        self.fit_plot.clear()

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

    def fit_transient(self):
        ## TODO implement baselining 

        current = self.dm.ip_data
        peak_ix = np.argmax(current)

        ## TODO implement rise start setting
        rise_start = peak_ix - 5 

        # rise fit
        rise_sub_time = self.time[rise_start:peak_ix+1] 
        rise_sub = current[rise_start:peak_ix+1]
        try:
            rise_fit, rise_popt = self.fit_rise(rise_sub, rise_sub_time)
        except RuntimeError:
            rise_fit = np.full(rise_sub.size, 0)
            rise_popt = [1, 1, 1]

        # TODO implement decay start setting and fit stop
        decay_start = 0
        fit_stop = peak_ix + 20

        # decay fit
        decay_sub_time = self.time[peak_ix+decay_start:fit_stop]
        decay_sub = current[peak_ix+decay_start:fit_stop]
        try:
            decay_fit, decay_popt = self.fit_decay(decay_sub, decay_sub_time)
        except RuntimeError:
            decay_fit = np.full(decay_sub.size, 0) 
            decay_popt = [1, 1, 1]

        # values to write to text boxes
        rise_tau = 1/rise_popt[1]
        self.rise_val.setText(f'{rise_tau:0.3f}')
        decay_tau = 1/decay_popt[1]
        self.decay_val.setText(f'{decay_tau:0.3f}')

        # plotting fit
        full_sub_time = np.append(rise_sub_time, decay_sub_time)
        full_fit = np.append(rise_fit, decay_fit)
        self.fit_plot.setData(full_sub_time, full_fit, pen=pg.mkPen('r', width=1.5))





