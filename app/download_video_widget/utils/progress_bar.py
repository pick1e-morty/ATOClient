from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel
from qfluentwidgets import ProgressBar


class PercentProgressBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.progressBar = ProgressBar(self)
        self.percentLabel = QLabel(self)
        self.layout.addWidget(self.progressBar)
        self.layout.addWidget(self.percentLabel)
        self.progressBar.valueChanged.connect(self.drawPercent)
        self.drawPercent()

    def setMaximum(self, value):
        self.progressBar.setMaximum(value)

    def setValue(self, value):
        self.progressBar.setValue(value)

    def drawPercent(self):
        self.percentLabel.setText(self.progressBar.valText())