import multiprocessing
import os
import sys
from pathlib import Path

from PyQt5.QtCore import Qt, QRect, QUrl, QSize, QPoint
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QSpacerItem, QSizePolicy
from configobj.validate import VdtTypeError, VdtValueError, ValidateError
from qfluentwidgets import SplashScreen, MessageBox, ProgressBar, NavigationItemPosition, PushButton
from qfluentwidgets import FluentIcon as FIF
from app.main_window.base_main_window import BaseMainWindow
from loguru import logger

from app.main_window.main_window import MainWindow
from app.picture_process_widget.ppw import PPWclass

if __name__ == '__main__':
    multiprocessing.freeze_support()
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    app = QApplication(sys.argv)
    forms = MainWindow()

    errorMsgBox = MessageBox('错误', "初始化", forms)
    errorMsgBox.raise_()
    errorMsgBox.yesButton.setText('确定')  # 先把报错弹窗加载好
    errorMsgBox.cancelButton.setText('返回')

    # 实例化并激活 月台绑定设备配置生成器
    from app.utils.dev_config import YtBindDevConfigGenerate, DevConfigFileNotFoundError, DevConfigFileInvalidError, DevConfigFileContentIsEmptyException, DevConfigFileContentIsInvalidException, DevConfigFileHandleErrorException

    title = "设备配置文件错误"
    errorMsgBox.titleLabel.setText(title)  # 更改 错误弹窗 的标题
    try:
        forms.devConfigGenerate = YtBindDevConfigGenerate()
        next(forms.devConfigGenerate)  # 启动生成器,这步将执行getYtConfigFromConfigFile函数，异常也是从这个函数raise出来的
    except (DevConfigFileNotFoundError, DevConfigFileInvalidError, DevConfigFileContentIsEmptyException, DevConfigFileHandleErrorException, DevConfigFileContentIsInvalidException) as errorText:  # 设备配置文件路径是写的相对的，写在处理函数中的，可能会出现点问题吧
        logger.error(str(errorText))
        errorMsgBox.contentLabel.setText(str(errorText))
        errorMsgBox.exec()  # 这里或许能加个重启应用
        exit(1)
    # 月台绑定设备配置生成器 代码结束

    # 获取界面配置字典
    from app.utils.forms_config import getFormsConfigDict, VdtStrNotUpperError, VdtDateTimeFormatError

    title = "界面配置文件错误"
    errorMsgBox.titleLabel.setText(title)  # 更改 错误弹窗 的标题
    try:
        forms.formsConfigDict = getFormsConfigDict()
    except (OSError, VdtDateTimeFormatError, VdtStrNotUpperError, VdtTypeError, VdtValueError) as errorText:
        logger.error(str(errorText))
        errorMsgBox.contentLabel.setText(str(errorText))
        errorMsgBox.exec()
        exit(1)
    except ValidateError as errorText:
        errorText = f"界面配置文件中的参数有误\n这是config异常基类，意料之外的错误\n{errorText}"
        logger.error(str(errorText))
        errorMsgBox.contentLabel.setText(str(errorText))
        errorMsgBox.exec()
        exit(1)
    # 获取界面配置字典 代码结束
    from esheet_process_widget.epw import EPWclass  # 这两个类用到了上面的 设备配置生成器 和 界面配置字典
    from download_video_widget.dvw import DVWclass  # 所以要在上面try完了之后才能导入
    forms.start_init()
    forms.show()
    forms.splashScreen.finish()
    # TODO 测试参数，记得改回第一个页面， 参数1
    forms.stackWidget.setCurrentIndex(3)

    __desktopPath = os.path.join(os.path.expanduser('~'), 'Desktop')
    testFile = os.path.join(__desktopPath, "0306.xlsx")
    __filePath2 = os.path.join(__desktopPath, "0307.xlsx")
    # forms.epwInterface.addFilePathsToexcelFile_LWData([__filePath2, __filePath1])
    # forms.epwInterface.addFilePathsToexcelFile_LWData([testFile, __filePath2])

    app.exec_()
