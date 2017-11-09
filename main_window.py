import sys
import os
from PyQt5 import QtCore, QtGui, QtWidgets
import neurphys.read_abf as abf
import neurphys.read_pv as rpv
from widgets.voltammetry_plot_widget import VoltammetryPlotWidget


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

        # export_action = QtGui.QAction("Export", self)
        # export_action.triggered.connect(self.create_export_dialog)
        # file_clear_action = QtGui.QAction("Clear workspace", self)
        # file_clear_action.triggered.connect(self.clear_workspace)
        # file_menu.addAction(export_action)
        # file_menu.addAction(file_clear_action)

    def gen_analysis_window(self, filepath, base_df):
        vpw = VoltammetryPlotWidget()
        window = QtWidgets.QMdiSubWindow()
        window.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        window.setWidget(vpw)
        window.setWindowTitle(os.path.split(filepath)[-1])
        window.setToolTip(filepath)

        self.mdi.addSubWindow(window)
        window.resize(self.mdi.size()*0.5)
        window.show()

    def load_abf(self):
        params = {'caption': 'Select .abf file', 'directory': self.current_dir,
                  'filter': '*.abf'}
        abf_file = QtWidgets.QFileDialog().getOpenFileName(self, **params)[0]
        if any(abf_file):
            df = abf.read_abf(abf_file)
            self.gen_analysis_window(abf_file, df)

    def load_pv(self):
        pass


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())
