import multiprocessing
import sys
from traceback import format_exception
from types import TracebackType
from typing import Type

from PyQt5.QtCore import Qt, pyqtSlot, QUrl, QVersionNumber
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QApplication
from configobj.validate import VdtTypeError, VdtValueError, ValidateError
from loguru import logger
from qfluentwidgets import FluentIcon as FIF, Dialog, InfoBar, InfoBarPosition, NavigationItemPosition
from qfluentwidgets import MessageBox

from app.app_setting_widget.asw import ASWclass
from app.download_video_widget.dvw import DVWclass
from app.esheet_process_widget.epw import EPWclass
from app.main_window.base_main_window import BaseMainWindow
from app.picture_process_widget.ppw import PPWclass
from app.utils.dev_config import YtBindDevConfigGenerate, DevConfigFileNotFoundError, DevConfigFileInvalidError, DevConfigFileContentIsEmptyException, DevConfigFileContentIsInvalidException, DevConfigFileHandleErrorException
from app.utils.forms_config import getFormsConfigDict, VdtStrNotUpperError, VdtDateTimeFormatError, FormsConfigWrite
from app.utils.global_var import RELEASE_URL
from app.utils.mcsl2utils import exceptionFilter, ExceptionFilterMode, ExceptionWidget
from app.utils.update_info_msgbox import UpdateInfoMsgBox
from app.utils.version_manager import VersionManager


class MainWindow(BaseMainWindow):
    def __init__(self):
        super().__init__()

        # self.oldHook = sys.excepthook     # logger还需要适配
        # sys.excepthook = self.catchExceptions

        self.loadSplashScreen()  # 开始屏幕
        self.load_devConfigGenerate()  # 载入设备配置生成器
        self.load_formsConfig()  # 载入窗体UI配置
        self.initUI()  # 初始化UI
        self.init_Navigation()  # 刷新navigation的UI显示

        self.splashScreen.finish()

        self.mainwindow_config = self.formsConfigDict["mainwindow"]

        if self.mainwindow_config["检查更新"]:
            ignoreVersion = self.mainwindow_config["忽略版本号"]
            self.versionManager = VersionManager(ignoreVersion)
            self.checkUpdate()

    def checkUpdate(self):
        try:
            remoteVer = self.versionManager.getLatestVersionMethod()
        except Exception as e:
            logger.error(e)
            InfoBar.error('更新提示', '检查更新失败，请检查网络连接', duration=1500, position=InfoBarPosition.TOP, parent=self)
            return

        remoteVersion, _suffixIndex = QVersionNumber.fromString(remoteVer[1:])  # 这个[1:]是在过滤版本号中的那个v字符
        localVersion, _suffixIndex = QVersionNumber.fromString(self.versionManager.currentVersion[1:])
        ignoreVersion, _suffixIndex = QVersionNumber.fromString(self.versionManager.ignoreVersion[1:])

        if remoteVersion == ignoreVersion:
            # 远程仓库版本等于要忽略的版本，没有新版本
            InfoBar.info('更新提示', f'已忽略 {remoteVer} 版本更新', duration=1500, position=InfoBarPosition.TOP, parent=self)
        elif localVersion == remoteVersion:
            # 本地版本大于等于远程版本号，说明本地版本是最新的
            InfoBar.success('更新提示', '当前已是最新版本', duration=1500, position=InfoBarPosition.TOP, parent=self)
        else:
            newVersion, releaseTitle, releaseInfo = self.versionManager.getUpdateReleaseInfo()
            updateMsgBox = UpdateInfoMsgBox(releaseTitle, releaseInfo, self)
            updateMsgBox.accepted.connect(lambda: QDesktopServices.openUrl(QUrl(RELEASE_URL)))  # 跳转到更新页面
            updateMsgBox.ignoreSignal.connect(lambda: self.write_ignore_version2Configini(newVersion))  # 写入忽略版本号到配置文件
            updateMsgBox.raise_()
            updateMsgBox.exec()

    def write_ignore_version2Configini(self, version):
        # 写入忽略版本号到配置文件
        formsConfigWriteObj = FormsConfigWrite()  # 这个写法很不优雅，用完就关的妥协
        try:
            formsConfigWriteObj.change_mainwindow_ignore_version(version)
        except ValueError as e:
            logger.error(str(e))

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
        self.addSubInterface(self.epwInterface, FIF.DOCUMENT, '表格处理')
        self.dvwInterface = DVWclass(self)
        self.addSubInterface(self.dvwInterface, FIF.DOWNLOAD, '下载录像')
        self.ppwInterface = PPWclass(self)
        self.ppwInterface.addToolButtonInTitleBar(self.titleBar)
        self.addSubInterface(self.ppwInterface, FIF.PHOTO, '标记图片')
        self.aswInterface = ASWclass(self)
        self.addSubInterface(self.aswInterface, FIF.SETTING, '设置', NavigationItemPosition.BOTTOM)
        self.connectWidgetSignal()

    def init_Navigation(self):
        # 两个版本的界面导航栏初始化，这个是项目结构不够完美的产物。
        widget = self.stackWidget.widget(0)
        self.navigationInterface.setCurrentItem(widget.objectName())
        self.stackWidget.setCurrentIndex(0)

    def connectWidgetSignal(self):
        # 连接组件信号
        self.dvwInterface.ui.startDownLoad_PB.clicked.connect(self.dvw_startDownLoad_PB_clicked)
        self.switchToWidget.connect(self.do_afterSwitchFun)  #

    def do_afterSwitchFun(self, InterFaceWidget):
        # 当navigationInterface上的某个按钮被点击
        if InterFaceWidget == self.ppwInterface:
            # 把toolsGroupBox显示出来
            self.showMaximized()  # 父类窗体最大化
            QApplication.processEvents()  # 立刻flush一下，不然后面的代码对整个窗体的size判断会有问题
            self.ppwInterface.toolsGroupBox.setHidden(False)
            self.ppwInterface.scanDirsAddToDirPathComboBox()  # 重新扫描一下有哪些文件夹
        else:
            # 隐藏toolsGroupBox
            self.ppwInterface.toolsGroupBox.setHidden(True)
        if InterFaceWidget == self.dvwInterface:
            self.dvwInterface.closeTheDoorAndreleaseTheDog()  # 持续刷新 文件数量 表格组件。会立即扫描一次pic及其子级文件中的文件数量
        else:
            self.dvwInterface.openTheDoorAndCollectTheDog()  # 停止刷新

        # epw的保存机制是：当excelFile_LW中的currentSelectItem改变时，将excelData_TW和sameYt_TW中的数据保存到excelFile_LW中的item中
        # 如果用户改动过表格组件中的数据后，却没有ItemChanged，那main_window这边取数据的时候就会丢失最新操作的那一部分数据
        # 所以需要我这边手动保存一下

        # TODO 这里做一个检测是否 修改的标志，如果没改的话还要来回存放就浪费资源了(还可能会卡顿)
        excelFile_LW_CurrentItem = self.epwInterface.ui.excelFile_LW.currentItem()
        if excelFile_LW_CurrentItem is not None:
            self.epwInterface.saveTableDataToListWidgetItemData(excelFile_LW_CurrentItem)

    @pyqtSlot()
    def dvw_startDownLoad_PB_clicked(self):
        # 当 下载页面 中的 开始下载按钮 被点击时，触发这个函数
        # 两个组件之间的数值传递，
        # 遍历excelFile_LW中的所有item，取出每个item的数据
        excelFileListWidgetItemDataStructList = []
        for i in range(self.epwInterface.ui.excelFile_LW.count()):
            excelFile_LW_ItemData = self.epwInterface.ui.excelFile_LW.item(i).data(Qt.UserRole)
            if excelFile_LW_ItemData.edtw_ItemDataList:  # 判断列表组件中的数据是否为空
                excelFileListWidgetItemDataStructList.append(excelFile_LW_ItemData)
        if excelFileListWidgetItemDataStructList:
            self.dvwInterface.handleDownloadList(excelFileListWidgetItemDataStructList)

    def catchExceptions(self, ty: Type[BaseException], value: BaseException, _traceback: TracebackType):
        """
        全局捕获异常，并弹窗显示
        :param ty: 异常的类型
        :param value: 异常的对象
        :param _traceback: 异常的traceback
        """
        # 过滤部分异常
        mode = exceptionFilter(ty, value, _traceback)

        if mode == ExceptionFilterMode.SILENT:
            return

        if mode == ExceptionFilterMode.PASS:
            logger.info(f"忽略了异常: {ty} {value} {_traceback}")
            return

        elif mode == ExceptionFilterMode.RAISE:
            logger.error(msg=f"捕捉到异常: {ty} {value} {_traceback}")
            return self.oldHook(ty, value, _traceback)

        elif mode == ExceptionFilterMode.RAISE_AND_PRINT:
            tracebackString = "".join(format_exception(ty, value, _traceback))
            logger.error(msg=tracebackString)
            exceptionWidget = ExceptionWidget(tracebackString)
            box = Dialog(self.tr("MCSL2 发生未经处理的异常"), content=self.tr("如果有能力可自行解决，无法解决请积极反馈！"), parent=None, )
            box.titleBar.show()
            box.setTitleBarVisible(False)
            box.yesButton.setText(self.tr("确认并复制到剪切板"))
            box.cancelButton.setText(self.tr("知道了"))
            del box.contentLabel
            box.textLayout.addWidget(exceptionWidget.exceptionScrollArea)
            box.yesSignal.connect(lambda: QApplication.clipboard().setText(tracebackString))
            box.yesSignal.connect(box.deleteLater)
            box.cancelSignal.connect(box.deleteLater)
            box.yesSignal.connect(exceptionWidget.deleteLater)
            box.cancelSignal.connect(exceptionWidget.deleteLater)
            box.exec()
            return self.oldHook(ty, value, _traceback)


if __name__ == '__main__':
    multiprocessing.freeze_support()
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    app = QApplication(sys.argv)
    forms = MainWindow()
    forms.show()
    sys.exit(app.exec_())
