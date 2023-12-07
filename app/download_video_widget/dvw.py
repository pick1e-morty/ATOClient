import sys
from pathlib import Path

from PyQt5.QtCore import pyqtSlot, QEvent, QSize, Qt, QPropertyAnimation, QRect, QEasingCurve
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QApplication, QWidget, QListWidget, QTableWidget, QAction, QSizePolicy)
from qfluentwidgets import RoundMenu, Action, MenuAnimationType, SplashScreen, FlowLayout

from app.download_video_widget.UI.ui_DownloadVideo import Ui_Form


class Init_DVW_Widget(QWidget):
    """
    这边实现的功能
    1. 左边的ListWidget和右边两个TableWidget的右键菜单
    2. 自定义处理格式的展开收缩的动画
    3. 从配置文件中读取数据并设置到 保留指定月台中的单号数量按钮中的各个action所携带的数值，以及自定义处理格式中的四个LineEdit的默认数值
    4. 开始屏幕的加载启动（关闭方法则是两边的文件入口都有）
    """

    def __init__(self):
        super().__init__()  # 调用父类构造函数，创建窗体
        self.ui = Ui_Form()  # 创建UI对象
        self.ui.setupUi(self)  # 构造UI界面



if __name__ == "__main__":  # 用于当前窗体测试
    from app.utils.aboutconfig import configini

    app = QApplication(sys.argv)  # 创建GUI应用程序
    forms = Init_DVW_Widget()  # 创建窗体

    # forms.addFilePathsToexcelFile_LWData([__filePath1])
    forms.show()

    sys.exit(app.exec_())
