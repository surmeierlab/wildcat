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

        ## Parameters
        param_label = QtWidgets.QLabel('Paramaters:')
        param_label.setSizePolicy(size_policy)

        # fit start
        self.start_layout = QtWidgets.QHBoxLayout()
        self.start_label = QtWidgets.QLabel('Fit Start (s): ')
        self.start_label.setFixedWidth(120)
        self.start_val = QtWidgets.QLineEdit('0.0')
        self.start_val.setSizePolicy(size_policy)
        self.start_val.setFixedWidth(70)
        self.start_layout.addWidget(self.start_label)
        self.start_layout.addWidget(self.start_val)

        # fit end
        self.end_layout = QtWidgets.QHBoxLayout()
        self.end_label = QtWidgets.QLabel('Fit End (s): ')
        self.end_label.setFixedWidth(120)
        self.end_val = QtWidgets.QLineEdit()
        self.end_val.setFixedWidth(70)
        self.end_layout.addWidget(self.end_label)
        self.end_layout.addWidget(self.end_val)

        # peak delta
        self.delta_layout = QtWidgets.QHBoxLayout()
        self.delta_label = QtWidgets.QLabel('Peak Delta (# points): ')
        self.delta_label.setFixedWidth(120)
        self.delta_val = QtWidgets.QLineEdit('0')
        self.delta_val.setFixedWidth(70)
        self.delta_layout.addWidget(self.delta_label)
        self.delta_layout.addWidget(self.delta_val)

        # baseline start
        # self.bsl_start_layout = QtWidgets.QHBoxLayout()
        # self.bsl_start_label = QtWidgets.QLabel('Baseline Start: ')
        # self.bsl_start_val = QtWidgets.QLineEdit('0.0')

        # baseline end

        ## Output
        output_label = QtWidgets.QLabel('Fit Output: ')
        output_label.setSizePolicy(size_policy)
          
        # rise tau
        self.rise_layout = QtWidgets.QHBoxLayout()
        self.rise_label = QtWidgets.QLabel('Rise tau: ')
        self.rise_label.setFixedWidth(120)
        self.rise_val = QtWidgets.QLineEdit()
        self.rise_val.setSizePolicy(size_policy)
        self.rise_val.setFixedWidth(70)
        self.rise_val.setReadOnly(True)
        self.rise_layout.addWidget(self.rise_label)
        self.rise_layout.addWidget(self.rise_val)

        # decay tau
        self.decay_layout = QtWidgets.QHBoxLayout()
        self.decay_label = QtWidgets.QLabel('Decay tau: ')
        self.decay_label.setFixedWidth(120)
        self.decay_val = QtWidgets.QLineEdit()
        self.decay_val.setSizePolicy(size_policy)
        self.decay_val.setFixedWidth(70)
        self.decay_val.setReadOnly(True)
        self.decay_layout.addWidget(self.decay_label)
        self.decay_layout.addWidget(self.decay_val)

        # time to peak
        self.ttp_layout = QtWidgets.QHBoxLayout()
        self.ttp_label = QtWidgets.QLabel('Time to Peak: ')
        self.ttp_label.setFixedWidth(120)
        self.ttp_val = QtWidgets.QLineEdit()
        self.ttp_val.setSizePolicy(size_policy)
        self.ttp_val.setFixedWidth(70)
        self.ttp_val.setReadOnly(True)
        self.ttp_layout.addWidget(self.ttp_label)
        self.ttp_layout.addWidget(self.ttp_val)

        self.run_btn = QtWidgets.QPushButton('Run Fit')
        self.run_btn.clicked.connect(self.fit_transient)
        self.run_btn.setFixedWidth(200)

        left_col.addWidget(param_label)
        left_col.addLayout(self.start_layout)
        left_col.addLayout(self.end_layout)
        left_col.addLayout(self.delta_layout)
        left_col.addWidget(output_label)
        left_col.addLayout(self.rise_layout)
        left_col.addLayout(self.decay_layout)
        left_col.addLayout(self.ttp_layout)
        left_col.addWidget(self.run_btn)

        # change focus back to button after done editing
        self.start_val.editingFinished.connect(self.select_btn)
        self.end_val.editingFinished.connect(self.select_btn)
        self.delta_val.editingFinished.connect(self.select_btn)

        # plot widget
        self.pw = pg.PlotWidget()
        self.pw.plotItem.setLabel('left', 'Current (%s)' % self.dm.data_unit)
        self.plot = self.pw.plotItem.plot()
        self.fit_plot = self.pw.plotItem.plot()
        self.ttp_plot = self.pw.plotItem.plot()

        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.VLine)

        layout.addLayout(left_col)
        layout.addWidget(line)
        layout.addWidget(self.pw)

        self.dm.sigIPDataChanged.connect(self.set_plot_data)

    def select_btn(self):
        self.run_btn.setFocus()
        self.run_btn.setAutoDefault(True)

    def set_plot_data(self):
        dlen = len(self.dm.ip_data)
        stop = dlen*(1/self.dm.sampling_freq) - (1/self.dm.sampling_freq)
        self.time = np.linspace(0, stop, dlen)

        self.plot.setData(self.time, self.dm.ip_data, pen=pg.mkPen('b', width=1.5),
                          symbol='o')
        self.fit_plot.clear()
        self.ttp_plot.clear()

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

        ## TODO implement exception handling
        start_t = float(self.start_val.text())
        rise_start= np.where(self.time >= start_t)[0][0]

        # rise fit
        rise_sub_time = self.time[rise_start:peak_ix+1] 
        rise_sub = current[rise_start:peak_ix+1]
        try:
            rise_fit, rise_popt = self.fit_rise(rise_sub, rise_sub_time)
        except RuntimeError:
            rise_fit = np.full(rise_sub.size, np.nan)
            rise_popt = [np.nan, np.nan, np.nan]

        # TODO implement exception handling
        peak_delta = int(self.delta_val.text())
        end_t = float(self.end_val.text())
        fit_stop = np.where(self.time <= end_t)[0][-1]

        # decay fit
        decay_sub_time = self.time[peak_ix+peak_delta:fit_stop]
        decay_sub = current[peak_ix+peak_delta:fit_stop]
        try:
            decay_fit, decay_popt = self.fit_decay(decay_sub, decay_sub_time)
        except RuntimeError:
            decay_fit = np.full(decay_sub.size, 0) 
            decay_popt = [np.nan, np.nan, np.nan]

        # time to peak
        start_ix = np.where(np.gradient(current) > 1)[0][0]
        time_to_peak = self.time[peak_ix] - self.time[start_ix]

        # values to write to text boxes
        rise_tau = 1/rise_popt[1]
        self.rise_val.setText(f'{rise_tau:0.3f}')
        decay_tau = 1/decay_popt[1]
        self.decay_val.setText(f'{decay_tau:0.3f}')
        self.ttp_val.setText(f'{time_to_peak:0.3f}')

        # plotting fit
        full_sub_time = np.append(rise_sub_time, decay_sub_time)
        full_fit = np.append(rise_fit, decay_fit)
        self.fit_plot.setData(full_sub_time, full_fit, pen=pg.mkPen('r', width=1.5))

        # plot points used in time to peak calculation
        x = [self.time[start_ix], self.time[peak_ix]]
        y = [current[start_ix], current[peak_ix]]
        self.ttp_plot.setData(x, y, pen=None, symbol='o', symbolPen=pg.mkPen('m')
                              , symbolBrush=pg.mkBrush('m'))