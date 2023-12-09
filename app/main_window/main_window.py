from pathlib import Path

from app.main_window.base_main_window import BaseMainWindow

# coding:utf-8
import os
import sys
from PyQt5.QtCore import Qt, QRect, QUrl, QSize
from PyQt5.QtGui import QIcon, QPainter, QImage, QBrush, QColor, QFont, QDesktopServices
from PyQt5.QtWidgets import QApplication, QFrame, QStackedWidget, QHBoxLayout, QLabel, QMainWindow, QWidget

from qfluentwidgets import (NavigationInterface, NavigationItemPosition, NavigationWidget, MessageBox,
                            isDarkTheme, setTheme, Theme, setThemeColor, qrouter, FluentWindow, NavigationAvatarWidget, SplashScreen)
from qfluentwidgets import FluentIcon as FIF
from qframelesswindow import FramelessWindow, StandardTitleBar


from app.utils.dev_config import *


class MainWindow(BaseMainWindow):

    def __init__(self):
        super().__init__()
        # 打开启动页面

        # 加载两个配置文件
        # 不成功就炸
        self.loadSplashScreen()
        try:
            from app.utils.dev_config import devConfigGenerate
        except (DevConfigFileNotFoundError, DevConfigFileInvalidError, DevConfigFileContentIsEmptyException, DevConfigFileContentIsInvalidException) as ErrorText:  # 设备配置文件路径是写的相对的，写在处理函数中的，可能会出现点问题吧
            msgBox = MessageBox('错误', str(ErrorText), self)
            msgBox.yesButton.setText('重试')
            msgBox.cancelButton.setText('退出')
            msgBox.exec_()
            exit(1)
        from app.utils.forms_config import configini

        # 这个messagebox要显示在splashScreen上面


        # 两种方案，config自己开窗体。固定大小，系统桌面全高，窗体至桌面中心，宽度是桌面的三分之二。不显示启动页面
        # config的报错msgBox独立界面，启动页面也是独立的
        from app.download_video_widget.dvw import DVW_Class
        from app.esheet_process_widget.epw import EPW_Class
        self.epwInterface = EPW_Class(self)
        self.dvwInterface = DVW_Class(self)
        self.addSubInterface(self.epwInterface, FIF.DOCUMENT, '文件处理')
        self.addSubInterface(self.dvwInterface, FIF.DOWNLOAD, '下载图片')

        self.connectWidgetSignal()

    def loadSplashScreen(self):
        # 加载启动屏幕
        logoFilePath = Path(__file__).parent / "resource/logo.png"
        self.setWindowIcon(QIcon(str(logoFilePath)))
        self.splashScreen = SplashScreen(self.windowIcon(), self)
        self.splashScreen.setTitleBar(QWidget())  # 去掉启动画面中右上角的三个窗口按钮
        formsWidth = self.size().width()
        formsHeigth = self.size().height()
        self.splashScreen.setIconSize(QSize(formsWidth // 2, formsHeigth // 2))
        self.show()
        QApplication.processEvents()

    def connectWidgetSignal(self):
        # 连接组件信号
        self.dvwInterface.ui.startDownLoad_PB.clicked.connect(self.dvw_startDownLoad_PB_clicked)

    def dvw_startDownLoad_PB_clicked(self):
        # 当 下载页面 中的 开始下载按钮 被点击时，触发这个函数
        # 两个组件之间的数值传递，
        # 遍历excelFile_LW中的所有item，取出每个item的数据
        excelFileListWidgetItemDataStructList = []
        for i in range(self.epwInterface.ui.excelFile_LW.count()):
            excelFile_LW_ItemData = self.epwInterface.ui.excelFile_LW.item(i).data(Qt.UserRole)
            excelFileListWidgetItemDataStructList.append(excelFile_LW_ItemData)
        self.dvwInterface.addDownloadList(excelFileListWidgetItemDataStructList)


if __name__ == '__main__':
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)

    forms = MainWindow()
    forms.show()
    forms.splashScreen.finish()
    forms.stackWidget.setCurrentIndex(1)

    __desktopPath = os.path.join(os.path.expanduser('~'), 'Desktop')
    __filePath1 = os.path.join(__desktopPath, "1127.xlsx")
    __filePath2 = os.path.join(__desktopPath, "1128.xlsx")
    # forms.addFilePathsToexcelFile_LWData([__filePath1])
    forms.epwInterface.addFilePathsToexcelFile_LWData([__filePath2, __filePath1])

    app.exec_()
