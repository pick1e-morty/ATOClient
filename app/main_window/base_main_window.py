# coding:utf-8
import sys
from pathlib import Path

from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QFrame, QStackedWidget, QHBoxLayout, QLabel, QWidget
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import (NavigationInterface, NavigationItemPosition, MessageBox,
                            isDarkTheme, NavigationAvatarWidget, SplashScreen)
from qframelesswindow import FramelessWindow, StandardTitleBar


class Widget(QFrame):

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.label = QLabel(text, self)
        self.label.setAlignment(Qt.AlignCenter)
        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.addWidget(self.label, 1, Qt.AlignCenter)
        self.setObjectName(text.replace(' ', '-'))


class BaseMainWindow(FramelessWindow):
    switchToWidget = pyqtSignal(QWidget)  # 用于发送navigationInterface所点击的组件，没用stackWidget.currentChanged，就是为了点一次发一次，槽函数那边要实现刷新之类的操作

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
        self.settingInterface = Widget('Setting Interface', self)

        # initialize layout
        self.initLayout()

        # add items to navigation interface
        self.initNavigation()

        self.initWindow()

    def initLayout(self):
        self.hBoxLayout.setSpacing(0)
        self.hBoxLayout.setContentsMargins(0, self.titleBar.height(), 0, 0)
        self.hBoxLayout.addWidget(self.navigationInterface)
        self.hBoxLayout.addWidget(self.stackWidget)
        self.hBoxLayout.setStretchFactor(self.stackWidget, 1)

    def initNavigation(self):
        # enable acrylic effect
        # self.navigationInterface.setAcrylicEnabled(True)

        self.navigationInterface.addSeparator()

        # add custom widget to bottom
        self.navigationInterface.addWidget(
            routeKey='avatar',
            widget=NavigationAvatarWidget('OffLine', str(Path(__file__).parent / "resource/Robot_black.png")),
            onClick=self.showMessageBox,
            position=NavigationItemPosition.BOTTOM,
        )

        self.addSubInterface(self.settingInterface, FIF.SETTING, 'Settings', NavigationItemPosition.BOTTOM)

        # !IMPORTANT: don't forget to set the default route key if you enable the return button
        # qrouter.setDefaultRouteKey(self.stackWidget, self.musicInterface.objectName())

        # set the maximum width
        self.navigationInterface.setExpandWidth(150)

        self.stackWidget.currentChanged.connect(self.onCurrentInterfaceChanged)
        widget = self.stackWidget.widget(0)
        self.navigationInterface.setCurrentItem(widget.objectName())

        # always expand
        # self.navigationInterface.setCollapsible(False)

    def initWindow(self):
        self.setWindowIcon(QIcon('resource/logo.png'))
        # self.setWindowTitle('PyQt-Fluent-Widgets')
        self.titleBar.setAttribute(Qt.WA_StyledBackground)

        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.resize(w // 2 + 200, h)
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

        # self.setQss()

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
        self.switchToWidget.emit(widget)

    def onCurrentInterfaceChanged(self, index):
        widget = self.stackWidget.widget(index)
        self.navigationInterface.setCurrentItem(widget.objectName())

        # !IMPORTANT: This line of code needs to be uncommented if the return button is enabled
        # qrouter.push(self.stackWidget, widget.objectName())

    def loadSplashScreen(self):
        # 加载启动屏幕
        logoFilePath = Path(__file__).parent / "resource/logo.png"
        self.setWindowIcon(QIcon(str(logoFilePath)))
        self.splashScreen = SplashScreen(self.windowIcon(), self)
        formsWidth = self.size().width()
        formsHeigth = self.size().height()
        self.splashScreen.setIconSize(QSize(formsWidth // 2, formsHeigth // 2))
        self.show()
        QApplication.processEvents()

    def showMessageBox(self):
        w = MessageBox('developing', '', self)
        w.exec()


if __name__ == '__main__':
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    forms = BaseMainWindow()
    forms.show()
    forms.stackWidget.setCurrentIndex(1)
    app.exec_()

# 把主题作者写的导航窗体demo作为我窗体的base，我继承一下
#
