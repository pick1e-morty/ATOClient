import sys

from PyQt5.QtWidgets import QHBoxLayout, QLabel, QWidget
from qfluentwidgets import ProgressBar


class PercentProgressBar(QWidget):
    """
    可以显示百分比的进度条
    用水平Layout组合了ProgressBar和QLabel
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.progressBar = ProgressBar(self)
        self.percentLabel = QLabel(self)
        self.layout.addWidget(self.progressBar)
        self.layout.addWidget(self.percentLabel)
        self.progressBar.valueChanged.connect(self.drawPercent)
        self.drawPercent()  # 手动绘制一次

    def setMaximum(self, value):
        self.progressBar.setMaximum(value)

    def setValue(self, value):
        self.progressBar.setValue(value)

    def addOne(self):
        value = self.progressBar.value() + 1
        self.progressBar.setValue(value)

    def value(self):
        return self.progressBar.value()

    def drawPercent(self):
        maxNum = self.progressBar.maximum()
        value = self.progressBar.value()
        self.percentLabel.setText(f"{value}/{maxNum}")


if __name__ == "__main__":
    from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QApplication, QVBoxLayout
    from qfluentwidgets import ProgressBar, PushButton

    print(123)
    app = QApplication(sys.argv)
    w = QWidget()

    layout = QVBoxLayout()
    ppb = PercentProgressBar(w)

    addPB = PushButton(w)
    addPB.clicked.connect(ppb.addOne)
    layout.addWidget(ppb)
    layout.addWidget(addPB)
    w.setLayout(layout)
    print(ppb.getValue())

    w.show()
    sys.exit(app.exec_())
