import extra.io as io
from PyQt5 import QtCore


class DataManager(object):

    sigDataChanged = QtCore.Signal(object)

    def __init__(self, path, base_df, data_column):
        self.path = path
        self.full_df = base_df
        self.data_col = data_column

        if len(self.full_df.index.levels[0]) == 1:
            self.split_df = io.split_trace(self.full_df,
                                           channel=self.data_col)
