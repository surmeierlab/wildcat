import neurphys.read_abf as abf


class DataManager(object):

    def __init__(self, path, full_dataframe):
        self.path = path
        self.full_df = full_dataframe
