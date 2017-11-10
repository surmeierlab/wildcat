import sys
from PyQt5 import QtCore, QtWidgets, QtGui
import numpy as np
from widgets.colorplot import ColorPlot


class ColorPlotWidget(QtWidgets.QWidget):

    def __init__(self, dm=None):
        super().__init__()
        self.dm = dm
        layout = QtWidgets.QVBoxLayout(self)

        self.colorplot = ColorPlot(self.dm)
        self.tab_widget = QtWidgets.QTabWidget()
        self.plot_tab = self.setup_plot_tab()
        self.tab_widget.addTab(self.plot_tab, 'Plots')

        layout.addWidget(self.colorplot)
        layout.addWidget(self.tab_widget)

    def setup_plot_tab(self):
        plot_tab = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(plot_tab)

        left_col = QtWidgets.QVBoxLayout()
        sweeps = list(range(1, self.dm.num_sweeps+1))
        bsl_button = QtWidgets.QPushButton('Baseline Sweeps')
        bsl_popup = ListPopup(self, 'Baseline Sweeps', sweeps)
        bsl_button.clicked.connect(lambda: self.toggle_popup(bsl_button, bsl_popup))
        ignore_button = QtWidgets.QPushButton('Ignore Sweeps')
        ignore_popup = ListPopup(self, 'Ignore Sweeps', sweeps)
        ignore_button.clicked.connect(lambda: self.toggle_popup(ignore_button, ignore_popup))

        left_col.addWidget(bsl_button)
        left_col.addWidget(ignore_button)

        right_col = QtWidgets.QVBoxLayout()
        auto_btn = QtWidgets.QPushButton('Auto Z')
        auto_btn.clicked.connect(self.colorplot.auto_range)
        peak_btn = QtWidgets.QPushButton('Find peak')
        peak_btn.clicked.connect(self.colorplot.find_peak)

        right_col.addWidget(peak_btn)
        right_col.addWidget(auto_btn)

        layout.addLayout(left_col)
        layout.addLayout(right_col)

        return plot_tab

    def toggle_popup(self, button, popup):
        if popup.isVisible():
            popup.hide()
        else:
            popup.show()
            popup.set_position(button)


class ListPopup(QtWidgets.QDialog):

    def __init__(self, parent, title, items):
        super().__init__(parent)
        self.setWindowTitle(title)
        layout = QtWidgets.QVBoxLayout(self)
        label = QtWidgets.QLabel('Select sweeps:')

        self.table = QtWidgets.QTableWidget()
        self.table.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)

        if len(items) >= 200:
            nrows = 20
            self.table.setFixedHeight(700)
        else:
            nrows = 10
            self.table.setFixedHeight(350)
        ncols = -1 * (-1 * len(items) // nrows)

        self.table.setColumnCount(ncols)
        cellw = 50
        [self.table.setColumnWidth(i, cellw) for i in range(ncols)]
        self.table.setFixedWidth(cellw+cellw*ncols)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setVisible(False)
        self.table.itemSelectionChanged.connect(self.changed)

        for col in range(ncols):
            for row in range(nrows):
                try:
                    item = QtWidgets.QTableWidgetItem(str(items[row+col*nrows]))
                    if self.table.rowCount() <= row:
                        self.table.insertRow(row)
                    item.setTextAlignment(QtCore.Qt.AlignCenter)
                    self.table.setItem(row, col, item)
                except IndexError:
                    break

        layout.addWidget(label)
        layout.addWidget(self.table)

        # self.show()

    def set_position(self, widget):
        point = widget.rect().topLeft()
        global_point = widget.mapToGlobal(point)
        move_to = global_point - QtCore.QPoint(self.width(), self.height()/2)
        self.move(move_to)

    def changed(self):
        items = sorted([int(item.text()) for item in self.table.selectedItems()])
        print(items)


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    ex = ColorPlotWidget()
    ex.show()
    sys.exit(app.exec_())
