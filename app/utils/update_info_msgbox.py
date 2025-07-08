import sys

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from qfluentwidgets import PushButton, MessageBoxBase, BodyLabel, TitleLabel


class UpdateInfoMsgBox(MessageBoxBase):
    """
    相比原来的MessageBox只是多了一个按钮，忽略本次更新按钮
    """

    ignoreSignal = pyqtSignal()

    def __init__(self, title, content, parent):
        super().__init__(parent)
        self.content = content
        self.titleLabel = TitleLabel(title, parent)
        self.contentLabel = BodyLabel(content, parent)

        self.yesButton.setText("打开更新页面")
        self.cancelButton.setText("取消")
        self.ignoreButton = PushButton("忽略本次更新", self.buttonGroup)
        self.ignoreButton.clicked.connect(self.__onIgnoreButtonClicked)

        self.viewLayout.addWidget(self.titleLabel, 0, Qt.AlignTop)
        self.viewLayout.addWidget(self.contentLabel, 0, Qt.AlignTop)
        self.buttonLayout.addWidget(self.ignoreButton, 1, Qt.AlignVCenter)

    def __onIgnoreButtonClicked(self):
        self.accept()
        self.ignoreSignal.emit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = QWidget()
    widget.show()
    uimb = UpdateInfoMsgBox("123", "456", widget)
    uimb.show()

    sys.exit(app.exec_())
