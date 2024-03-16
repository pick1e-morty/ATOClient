import multiprocessing
import os
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
from qfluentwidgets import MessageBox
from qfluentwidgets import FluentIcon as FIF
from configobj.validate import VdtTypeError, VdtValueError, ValidateError
from loguru import logger

from app.utils.dev_config import YtBindDevConfigGenerate, DevConfigFileNotFoundError, DevConfigFileInvalidError, DevConfigFileContentIsEmptyException, DevConfigFileContentIsInvalidException, DevConfigFileHandleErrorException
from app.utils.forms_config import getFormsConfigDict, VdtStrNotUpperError, VdtDateTimeFormatError

from app.main_window.base_main_window import BaseMainWindow
from app.esheet_process_widget.epw import EPWclass
from app.download_video_widget.dvw import DVWclass
from app.picture_process_widget.ppw import PPWclass


class MainWindow(BaseMainWindow):
    def __init__(self):
        super().__init__()
        self.loadSplashScreen()  # 开始屏幕
        self.load_devConfigGenerate()  # 载入设备配置生成器
        self.load_formsConfig()  # 载入窗体UI配置
        self.initUI()  # 初始化UI

    def load_devConfigGenerate(self):
        # 实例化并激活 月台绑定设备配置生成器
        errorMsgBox = MessageBox('错误', "设备配置文件错误", self)
        errorMsgBox.raise_()
        errorMsgBox.yesButton.setText('确定')  # 先把报错弹窗加载好
        errorMsgBox.cancelButton.setText('返回')

        try:
            self.devConfigGenerate = YtBindDevConfigGenerate()
            next(self.devConfigGenerate)  # 启动生成器,这步将执行getYtConfigFromConfigFile函数，异常也是从这个函数raise出来的
        except (DevConfigFileNotFoundError, DevConfigFileInvalidError, DevConfigFileContentIsEmptyException, DevConfigFileHandleErrorException, DevConfigFileContentIsInvalidException) as errorText:  # 设备配置文件路径是写的相对的，写在处理函数中的，可能会出现点问题吧
            logger.error(str(errorText))
            errorMsgBox.contentLabel.setText(str(errorText))
            errorMsgBox.exec()  # 这里或许能加个重启应用
            sys.exit(1)

    def load_formsConfig(self):
        # 载入窗体UI配置
        errorMsgBox = MessageBox('错误', "界面配置文件错误", self)
        errorMsgBox.raise_()
        errorMsgBox.yesButton.setText('确定')  # 先把报错弹窗加载好
        errorMsgBox.cancelButton.setText('返回')

        try:
            self.formsConfigDict = getFormsConfigDict()
        except (OSError, VdtDateTimeFormatError, VdtStrNotUpperError, VdtTypeError, VdtValueError) as errorText:
            logger.error(str(errorText))
            errorMsgBox.contentLabel.setText(str(errorText))
            errorMsgBox.exec()
            sys.exit(1)
        except ValidateError as errorText:
            errorText = f"界面配置文件中的参数有误\n这是config异常基类，意料之外的错误\n{errorText}"
            logger.error(str(errorText))
            errorMsgBox.contentLabel.setText(str(errorText))
            errorMsgBox.exec()
            sys.exit(1)

    def initUI(self):
        self.epwInterface = EPWclass(self)
        self.addSubInterface(self.epwInterface, FIF.DOCUMENT, '处理表格')
        self.dvwInterface = DVWclass(self)
        self.addSubInterface(self.dvwInterface, FIF.DOWNLOAD, '下载录像')
        self.ppwInterface = PPWclass(self)
        self.ppwInterface.addToolButtonInTitleBar(self.titleBar)
        self.addSubInterface(self.ppwInterface, FIF.PHOTO, '修改图片')
        self.connectWidgetSignal()

    def connectWidgetSignal(self):
        # 连接组件信号
        self.dvwInterface.ui.startDownLoad_PB.clicked.connect(self.dvw_startDownLoad_PB_clicked)
        self.switchToWidget.connect(self.do_afterSwitchFun)  #

    def do_afterSwitchFun(self, widget):
        # 如果navigationInterface上的某个按钮被点击
        if widget == self.ppwInterface:
            # 把toolsGroupBox显示出来
            self.showMaximized()  # 父类窗体最大化
            QApplication.processEvents()    # 立刻flush一下，不然后面的代码对整个窗体的size判断会有问题
            self.ppwInterface.toolsGroupBox.setHidden(False)
            self.ppwInterface.scanDirsAddToDirPathComboBox()    # 重新扫描一下有哪些文件夹
        else:
            # 隐藏toolsGroupBox
            self.ppwInterface.toolsGroupBox.setHidden(True)

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
    multiprocessing.freeze_support()
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    app = QApplication(sys.argv)
    forms = MainWindow()
    forms.show()
    forms.splashScreen.finish()
    forms.stackWidget.setCurrentIndex(1)

    __desktopPath = os.path.join(os.path.expanduser('~'), 'Desktop')
    testFile = os.path.join(__desktopPath, "0306.xlsx")
    __filePath2 = os.path.join(__desktopPath, "0307.xlsx")
    # forms.epwInterface.addFilePathsToexcelFile_LWData([__filePath2, __filePath1])
    forms.epwInterface.addFilePathsToexcelFile_LWData([testFile, __filePath2])

    app.exec_()
