from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QTableWidget
from qfluentwidgets import TableWidget


class CustomTableWidget(TableWidget):
    rowCountChangedSignal = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)

    @pyqtSlot(int, int)
    def rowCountChanged(self, oldCount, newCount):
        print("rowCountChanged")
        super().rowCountChanged(oldCount, newCount)
        self.rowCountChangedSignal.emit(newCount)

    def rowResized(self, row, oldHeight, newHeight):
        print("rowResized")
        super().rowResized(row, oldHeight, newHeight)
