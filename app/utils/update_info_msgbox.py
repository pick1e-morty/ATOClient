import sys

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QSizePolicy
from qfluentwidgets import PushButton, MessageBox


class UpdateInfoMsgBox(MessageBox):
    """
    相比原来的MessageBox只是多了一个按钮，忽略本次更新按钮
    """
    ignoreButtonClicked = pyqtSignal(bool)

    def __init__(self, *args):
        super().__init__(*args)
        self.ignoreUpdateButton = PushButton('忽略本次更新', self.buttonGroup)
        self.ignoreUpdateButton.clicked.connect(self._do_ignoreUpdateButtonClicked)
        self.ignoreUpdateButton.setMinimumWidth(110)
        self.buttonLayout.addWidget(self.ignoreUpdateButton, 1, Qt.AlignVCenter)

    def _do_ignoreUpdateButtonClicked(self):
        self.accept()
        self.ignoreButtonClicked.emit(True)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = QWidget()
    widget.show()
    uimb = UpdateInfoMsgBox('123', '456', widget)
    uimb.show()
    uimb.ignoreUpdateButton.adjustSize()

    sys.exit(app.exec_())
