import extra.io as io
from PyQt5 import QtCore
import numpy as np


class DataManager(object):

    sigDataChanged = QtCore.Signal(object)

    def __init__(self, path, base_df, data_column='primary',
                 scan_rate=400, ramp_min=-0.4, ramp_max=1.3):
        self.path = path
        self.full_df = base_df
        self.data_col = data_column
        self.scan_rate = scan_rate
        self.ramp_min = ramp_min
        self.ramp_max = 1.3
        self.ramp_dur = (self.ramp_max - self.ramp_min) / self.scan_rate * 2
        # self.bsl_sweeps = []
        # self.ignore_sweeps = []
        self.bsl_sweeps = [190, 191, 192, 193, 194]
        self.ignore_sweeps = list(range(1, 190))+list(range(251, 485))
        self.cp_data = None
        self.vms = None

        if len(self.full_df.index.levels[0]) == 1:
            self.split_df = io.split_trace(self.full_df,
                                           self.ramp_dur,
                                           self.ramp_max,
                                           self.data_col)
        else:
            # TODO: confirm that if df has multiple levels, levels
            # are equivalent to only a single voltage cycle
            self.split_df = self.full_df.copy()

        self.update_cp_data()

    def update_cp_data(self):
        bsl_ixs = np.array(self.bsl_sweeps) - 1
        ignore_ixs = np.array(self.ignore_sweeps) - 1

        self.cp_data = self.split_df[self.data_col].unstack().values
        avg = self.cp_data[bsl_ixs].mean(axis=0)
        self.cp_data -= avg

        mask = np.ones(self.cp_data.shape[0], dtype=np.bool)
        mask[ignore_ixs] = False
        self.cp_data = self.cp_data[mask]
        self.update_vms()

    def update_vms(self):
        npoints = self.cp_data.shape[1]
        print(npoints)
        up = np.linspace(self.ramp_min, self.ramp_max, int(npoints/2)+1)
        down = up[::-1][1:]
        self.vms = np.append(up, down)
