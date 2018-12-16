from .extra import io
from PySide2 import QtCore
import numpy as np
from scipy.signal import bessel, butter, lfilter


class DataManager(QtCore.QObject):

    sigCPDataChanged = QtCore.Signal(object)
    sigIPDataChanged = QtCore.Signal(object)

    def __init__(self, path, base_df, data_column='primary', data_unit='pA',
                 sampling_freq=10, scan_rate=400, ramp_min=-0.4, ramp_max=1.3):
        super().__init__()
        self.path = path
        self.full_df = base_df
        self.data_col = data_column
        # print(self.full_df.columns)
        self.data_unit = data_unit
        self.sampling_freq = sampling_freq
        self.scan_rate = scan_rate
        self.ramp_min = ramp_min
        self.ramp_max = 1.3
        self.ramp_dur = (self.ramp_max - self.ramp_min) / self.scan_rate * 2
        self.bsl_sweeps = list(range(10, 15))
        self.ignore_sweeps = list(range(10))
        self.cp_data = None
        self.ip_data = None
        self.vms = None
        self.init_cp_len = 0

        if self.data_unit == 'pA':
            self.full_df[self.data_col] /= 1000
            self.data_unit = 'nA'

        sampling = 1/(self.full_df.time[1] - self.full_df.time[0])
        nyq = 0.5*sampling
        low = 0.125 / nyq
        high = 1000 / nyq
        order = 4
        self.b, self.a = butter(N=order, Wn=[low, high], btype='bandpass')

        if len(self.full_df.index.levels[0]) == 1:
            self.split_df = io.split_trace(self.full_df,
                                           self.ramp_dur,
                                           self.ramp_max,
                                           'channel_2')
        else:
            # TODO: confirm that if df has multiple levels, levels
            # are equivalent to only a single voltage cycle
            self.split_df = self.full_df.copy()

        self.num_sweeps = len(self.split_df.index.levels[0])
        self.update_cp_data()

        self.init_peak_ix = int(np.where(self.cp_data == self.cp_data.max())[0])
        self.bsl_sweeps = list(range(self.init_peak_ix-9, self.init_peak_ix-4))

        all_sweeps = np.arange(1, self.init_cp_len+1)
        mask = np.ones(len(all_sweeps), np.bool)
        mask[self.init_peak_ix-10:self.init_peak_ix+40] = False
        self.ignore_sweeps = list(all_sweeps[mask])

        self.update_cp_data()

    def update_cp_data(self):
        self.cp_data = self.split_df[self.data_col].unstack().values
        self.init_cp_len = self.cp_data.shape[0]
        if any(self.bsl_sweeps):
            bsl_ixs = np.array(self.bsl_sweeps) - 1
            avg = self.cp_data[bsl_ixs].mean(axis=0)
            self.cp_data -= avg

        if any(self.ignore_sweeps):
            ignore_ixs = np.array(self.ignore_sweeps) - 1
            mask = np.ones(self.cp_data.shape[0], dtype=np.bool)
            mask[ignore_ixs] = False
            self.cp_data = self.cp_data[mask]

        self.cp_data = np.apply_along_axis(lambda x: lfilter(self.b, self.a, x),
                                           1, self.cp_data)
        self.update_vms()
        self.sigCPDataChanged.emit(self)

    def update_ip_data(self, data):
        self.ip_data = data
        self.sigIPDataChanged.emit(self)

    def update_vms(self):
        npoints = self.cp_data.shape[1]
        up = np.linspace(self.ramp_min, self.ramp_max, int(npoints/2)+1)
        down = up[::-1][1:]
        self.vms = np.append(up, down)

    def change_bsl_sweeps(self, sweeps):
        self.bsl_sweeps = sweeps
        self.update_cp_data()

    def change_ignore_sweeps(self, sweeps):
        self.ignore_sweeps = sweeps
        self.update_cp_data()
