import sys
import os
from PyQt5 import QtCore, QtWidgets
import neurphys.read_abf as abf
# import neurphys.read_pv as rpv
from widgets.analysis_widget import AnalysisWidget
from data_manager import DataManager
import logging
import traceback
import time


class Wildcat(QtWidgets.QApplication):

    def __init__(self, sys_argv):
        super().__init__(sys_argv)

        self.main_window = MainWindow()
        self.main_window.show()


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        desktop = QtWidgets.QDesktopWidget()
        dpi = desktop.logicalDpiX()
        self.setWindowTitle("Wildcat")
        self.ratio = dpi / 96
        self.resize(1400*self.ratio, 800*self.ratio)

        self.menubar = self.menuBar()
        self.setup_file_menu()
        self.current_dir = None

        self.mdi = QtWidgets.QMdiArea()
        self.setCentralWidget(self.mdi)

    def setup_file_menu(self):
        file_menu = self.menubar.addMenu("File")

        # file_new_action = QtGui.QAction("Load ABF", self)
        # file_new_action.triggered.connect(self.new_dataviewer)
        # file_menu.addAction(file_new_action)

        load_menu = file_menu.addMenu("Open")

        load_abf_action = QtWidgets.QAction("Axon file (.abf)", self)
        load_abf_action.triggered.connect(self.load_abf)
        load_pv_action = QtWidgets.QAction("PrairieView folder", self)
        load_pv_action.triggered.connect(self.load_pv)

        load_menu.addAction(load_abf_action)
        load_menu.addAction(load_pv_action)

        close_all_action = QtWidgets.QAction('Close All Files', self)
        close_all_action.triggered.connect(self.clear_windows)

        file_menu.addAction(close_all_action)

        # export_action = QtGui.QAction("Export", self)
        # export_action.triggered.connect(self.create_export_dialog)
        # file_clear_action = QtGui.QAction("Clear workspace", self)
        # file_clear_action.triggered.connect(self.clear_workspace)
        # file_menu.addAction(export_action)
        # file_menu.addAction(file_clear_action)

    def gen_analysis_window(self, dm):
        # vpw = VoltammetryPlotWidget(dm)
        aw = AnalysisWidget(dm)
        window = QtWidgets.QMdiSubWindow()
        window.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        window.setWidget(aw)
        window.setWindowTitle(os.path.split(dm.path)[-1])
        window.setToolTip(dm.path)

        self.mdi.addSubWindow(window)
        window.resize(self.mdi.size()*0.5)
        window.show()

    def load_abf(self):
        params = {'caption': 'Select .abf file', 'directory': self.current_dir,
                  'filter': '*.abf'}
        abf_file = QtWidgets.QFileDialog().getOpenFileName(self, **params)[0]
        while any(abf_file):
            freq, rate, vmin, vmax, accepted = RecordingDialog.return_values(self)
            if not accepted:
                return
            try:
                freq = float(freq)
                rate = float(rate)
                vmin = float(vmin)
                vmax = float(vmax)
                break
            except ValueError:
                QtWidgets.QMessageBox.about(self, 'Error', 'Fix')

        if any(abf_file):
            df = abf.read_abf(abf_file)
            data_col = df.columns[0]
            for i, unit in enumerate(df.channel_units):
                if unit in ['pA', 'nA']:
                    data_col = df.columns[i]
                    data_unit = unit
                    break

            dm = DataManager(abf_file, df, data_col, data_unit,
                             freq, rate, vmin, vmax)
            self.gen_analysis_window(dm)

    def load_pv(self):
        pass

    def clear_windows(self):
        for window in self.mdi.subWindowList():
            window.close()


class RecordingDialog(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)

        freq_layout = QtWidgets.QHBoxLayout()
        freq_label = QtWidgets.QLabel('Sampling Rate (Hz):')
        self.freq_input = QtWidgets.QLineEdit('10')
        freq_layout.addWidget(freq_label)
        freq_layout.addWidget(self.freq_input)

        rate_layout = QtWidgets.QHBoxLayout()
        rate_label = QtWidgets.QLabel('Scan Rate (V/s):')
        self.rate_input = QtWidgets.QLineEdit('400')
        rate_layout.addWidget(rate_label)
        rate_layout.addWidget(self.rate_input)

        min_layout = QtWidgets.QHBoxLayout()
        min_label = QtWidgets.QLabel('Ramp Min (V):')
        self.min_input = QtWidgets.QLineEdit('-0.4')
        min_layout.addWidget(min_label)
        min_layout.addWidget(self.min_input)

        max_layout = QtWidgets.QHBoxLayout()
        max_label = QtWidgets.QLabel('Ramp Max (V):')
        self.max_input = QtWidgets.QLineEdit('1.3')
        max_layout.addWidget(max_label)
        max_layout.addWidget(self.max_input)

        buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok |
                                             QtWidgets.QDialogButtonBox.Cancel,
                                             QtCore.Qt.Horizontal, self)
        buttons.setCenterButtons(True)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout.addLayout(freq_layout)
        layout.addLayout(rate_layout)
        layout.addLayout(min_layout)
        layout.addLayout(max_layout)
        layout.addWidget(buttons)

    def change_rate(self):
        print(self.rate_input.text())

    @staticmethod
    def return_values(parent=None):
        dialog = RecordingDialog(parent)
        result = dialog.exec_()
        freq_val = dialog.freq_input.text()
        rate_val = dialog.rate_input.text()
        min_val = dialog.min_input.text()
        max_val = dialog.max_input.text()

        return freq_val, rate_val, min_val, max_val, result


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, filename='./error.log',
                        filemode='w')

    def log_uncaught_exceptions(ex_cls, ex, tb):
        logging.debug(time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime()))
        logging.debug(''.join(traceback.format_tb(tb)))
        logging.debug('{0}: {1}\n'.format(ex_cls, ex))

    sys.excepthook = log_uncaught_exceptions

    app = Wildcat(sys.argv)
    sys.exit(app.exec_())
