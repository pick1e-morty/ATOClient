# coding:utf-8
import os
import sys
from PyQt5.QtCore import Qt, QRect, QUrl
from PyQt5.QtGui import QIcon, QPainter, QImage, QBrush, QColor, QFont, QDesktopServices
from PyQt5.QtWidgets import QApplication, QFrame, QStackedWidget, QHBoxLayout, QLabel, QMainWindow

from qfluentwidgets import (NavigationInterface, NavigationItemPosition, NavigationWidget, MessageBox,
                            isDarkTheme, setTheme, Theme, setThemeColor, qrouter, FluentWindow, NavigationAvatarWidget)
from qfluentwidgets import FluentIcon as FIF
from qframelesswindow import FramelessWindow, StandardTitleBar

from app.download_video_widget.dvw import DVW_Class
from app.esheet_process_widget.epw import EPW_Class
from app.utils.aboutconfig import configini


class Widget(QFrame):

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.label = QLabel(text, self)
        self.label.setAlignment(Qt.AlignCenter)
        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.addWidget(self.label, 1, Qt.AlignCenter)
        self.setObjectName(text.replace(' ', '-'))


class Window(FramelessWindow):

    def __init__(self):
        super().__init__()
        self.setTitleBar(StandardTitleBar(self))

        # use dark theme mode
        # setTheme(Theme.DARK)

        # change the theme color
        # setThemeColor('#0078d4')

        self.hBoxLayout = QHBoxLayout(self)
        self.navigationInterface = NavigationInterface(self, showMenuButton=True)
        self.stackWidget = QStackedWidget(self)

        # create sub interface
        self.epwInterface = EPW_Class(configini, self)
        self.dvwInterface = DVW_Class(self)
        self.connectWidgetSignal()

        self.settingInterface = Widget('Setting Interface', self)

        # initialize layout
        self.initLayout()

        # add items to navigation interface
        self.initNavigation()

        self.initWindow()

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

    def initLayout(self):
        self.hBoxLayout.setSpacing(0)
        self.hBoxLayout.setContentsMargins(0, self.titleBar.height(), 0, 0)
        self.hBoxLayout.addWidget(self.navigationInterface)
        self.hBoxLayout.addWidget(self.stackWidget)
        self.hBoxLayout.setStretchFactor(self.stackWidget, 1)

    def initNavigation(self):
        # enable acrylic effect
        # self.navigationInterface.setAcrylicEnabled(True)

        self.addSubInterface(self.epwInterface, FIF.DOCUMENT, '文件处理')
        self.addSubInterface(self.dvwInterface, FIF.DOWNLOAD, '下载图片')

        self.navigationInterface.addSeparator()

        # add custom widget to bottom
        self.navigationInterface.addWidget(
            routeKey='avatar',
            widget=NavigationAvatarWidget('OffLine', 'resource/Robot_black.png'),
            onClick=self.showMessageBox,
            position=NavigationItemPosition.BOTTOM,
        )

        self.addSubInterface(self.settingInterface, FIF.SETTING, 'Settings', NavigationItemPosition.BOTTOM)

        # !IMPORTANT: don't forget to set the default route key if you enable the return button
        # qrouter.setDefaultRouteKey(self.stackWidget, self.musicInterface.objectName())

        # set the maximum width
        # self.navigationInterface.setExpandWidth(300)

        self.stackWidget.currentChanged.connect(self.onCurrentInterfaceChanged)
        widget = self.stackWidget.widget(0)
        self.navigationInterface.setCurrentItem(widget.objectName())

        # always expand
        # self.navigationInterface.setCollapsible(False)

    def initWindow(self):
        self.resize(900, 700)
        self.setWindowIcon(QIcon('resource/logo.png'))
        # self.setWindowTitle('PyQt-Fluent-Widgets')
        self.titleBar.setAttribute(Qt.WA_StyledBackground)

        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

        self.setQss()

    def addSubInterface(self, interface, icon, text: str, position=NavigationItemPosition.TOP, parent=None):
        """ add sub interface """
        self.stackWidget.addWidget(interface)
        self.navigationInterface.addItem(
            routeKey=interface.objectName(),
            icon=icon,
            text=text,
            onClick=lambda: self.switchTo(interface),
            position=position,
            tooltip=text,
            parentRouteKey=parent.objectName() if parent else None
        )

    def setQss(self):
        color = 'dark' if isDarkTheme() else 'light'
        with open(f'resource/{color}/demo.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def switchTo(self, widget):
        self.stackWidget.setCurrentWidget(widget)

    def onCurrentInterfaceChanged(self, index):
        widget = self.stackWidget.widget(index)
        self.navigationInterface.setCurrentItem(widget.objectName())

        # !IMPORTANT: This line of code needs to be uncommented if the return button is enabled
        # qrouter.push(self.stackWidget, widget.objectName())

        # epw的保存机制是：当excelFile_LW中的item改变时，将excelData_TW和sameYt_TW中的数据保存到excelFile_LW中的item中
        # 如果用户删除过表格组件中的数据后，却没有ItemChanged，那main_window这边取数据的时候就会丢失最新操作的那一部分数据
        # 所以需要我这边手动保存一下
        excelFile_LW_CurrentItem = self.epwInterface.ui.excelFile_LW.currentItem()
        if excelFile_LW_CurrentItem is not None:
            excelFile_LW_ItemData = self.epwInterface.getExcelFile_LW_ItemData()
            excelFile_LW_CurrentItem.setData(Qt.UserRole, excelFile_LW_ItemData)

    def showMessageBox(self):
        w = MessageBox('正在开发', '', self)
        w.exec()


if __name__ == '__main__':
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    forms = Window()
    forms.show()
    forms.stackWidget.setCurrentIndex(1)

    __desktopPath = os.path.join(os.path.expanduser('~'), 'Desktop')
    __filePath1 = os.path.join(__desktopPath, "1127.xlsx")
    __filePath2 = os.path.join(__desktopPath, "1128.xlsx")
    # forms.addFilePathsToexcelFile_LWData([__filePath1])
    forms.epwInterface.addFilePathsToexcelFile_LWData([__filePath2, __filePath1])

    app.exec_()
