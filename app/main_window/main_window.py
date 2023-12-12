import os
import sys
from pathlib import Path

from PyQt5.QtCore import Qt, QRect, QUrl, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QWidget
from qfluentwidgets import SplashScreen, MessageBox
from qfluentwidgets import FluentIcon as FIF
from app.main_window.base_main_window import BaseMainWindow


class MainWindow(BaseMainWindow):
    def __init__(self):
        super().__init__()
        self.loadSplashScreen()

    def start_init(self):
        self.epwInterface = EPWclass(self)
        self.dvwInterface = DVWclass(self)
        self.addSubInterface(self.epwInterface, FIF.DOCUMENT, '文件处理')
        self.addSubInterface(self.dvwInterface, FIF.DOWNLOAD, '下载图片')

        self.connectWidgetSignal()

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

    def connectWidgetSignal(self):
        # 连接组件信号
        self.dvwInterface.ui.startDownLoad_PB.clicked.connect(self.dvw_startDownLoad_PB_clicked)

    def dvw_startDownLoad_PB_clicked(self):
        # 当 下载页面 中的 开始下载按钮 被点击时，触发这个函数
        # 两个组件之间的数值传递，
        # 遍历excelFile_LW中的所有item，取出每个item的数据
        excelFileListWidgetItemDataStructList = []
        for i in range(self.epwInterface.ui.excelFile_LW.count()):
            # TODO 这里还没做判空呢
            excelFile_LW_ItemData = self.epwInterface.ui.excelFile_LW.item(i).data(Qt.UserRole)
            excelFileListWidgetItemDataStructList.append(excelFile_LW_ItemData)
        self.dvwInterface.addDownloadList(excelFileListWidgetItemDataStructList)


if __name__ == '__main__':
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    app = QApplication(sys.argv)
    forms = MainWindow()

    from app.utils.dev_config import devConfigGenerate
    from app.utils.forms_config import formsConfigDict

    errorText = devConfigGenerate if isinstance(devConfigGenerate, str) else ""
    errorText = formsConfigDict if isinstance(formsConfigDict, str) else ""
    if len(errorText) != 0:
        msgBox = MessageBox('错误', errorText, forms)
        msgBox.raise_()
        msgBox.yesButton.setText('确定')
        msgBox.cancelButton.setText('返回')
        msgBox.exec()  # 这里或许能加个重启应用
        exit(1)

    from app.esheet_process_widget.epw import EPWclass
    from app.download_video_widget.dvw import DVWclass

    forms.start_init()
    forms.show()
    forms.splashScreen.finish()
    forms.stackWidget.setCurrentIndex(1)

    __desktopPath = os.path.join(os.path.expanduser('~'), 'Desktop')
    __filePath1 = os.path.join(__desktopPath, "1127.xlsx")
    __filePath2 = os.path.join(__desktopPath, "1128.xlsx")
    # forms.addFilePathsToexcelFile_LWData([__filePath1])
    forms.epwInterface.addFilePathsToexcelFile_LWData([__filePath2, __filePath1])

    app.exec_()
