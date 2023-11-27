import sys

from PyQt5.QtWidgets import QApplication, QWidget


class QmyPictureLabel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)  # 调用父类构造函数，创建窗体
        self.ui = Ui_PLWC()  # 创建UI对象
        self.ui.setupUi(self)  # 构造UI界面


if __name__ == "__main__":  # 用于当前窗体测试
    from ui_PictureLabel import Ui_PLWC

    app = QApplication(sys.argv)  # 创建GUI应用程序
    form = QmyPictureLabel()  # 创建窗体
    form.show()
    sys.exit(app.exec_())
else:
    from app.QMyPLw.ui_PictureLabel import Ui_PLWC
