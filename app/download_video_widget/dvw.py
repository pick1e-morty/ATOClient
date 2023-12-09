import sys
from pathlib import Path

from PyQt5.QtCore import pyqtSlot, QEvent, QSize, Qt, QPropertyAnimation, QRect, QEasingCurve
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QApplication, QWidget, QListWidget, QTableWidget, QAction, QSizePolicy)
from qfluentwidgets import RoundMenu, Action, MenuAnimationType, SplashScreen, FlowLayout
from typing import Tuple, List

from app.download_video_widget.UI.ui_DownloadVideo import Ui_DVW_Widget
from app.esheet_process_widget.epw_define import ExcelDataTableWidgetItemDataStruct, ExcelFileListWidgetItemDataStruct


class DVW_Class(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)  # 调用父类构造函数，创建窗体
        self.ui = Ui_DVW_Widget()  # 创建UI对象
        self.ui.setupUi(self)  # 构造UI界面

    # 首先我这边要拿到所有单号时间月台
    # 然后按照月台(监控通道)分类，以监控通道为单位开始下载
    # 这是一个很大的列表
    def addDownloadList(self, eflw_ItemDataList: List[ExcelFileListWidgetItemDataStruct]):
        # 处理上层数据
        classifyByYT = {}
        # 先按照月台对所有单号进行分类
        # 分类的同时获取到最终的保存文件路径
        rootPath = Path(__file__).parent.parent
        for eflw_ItemData in eflw_ItemDataList:
            folderName = Path(eflw_ItemData.excelFilePath).stem
            for edtw_ItemData in eflw_ItemData.edtw_ItemDataList:
                filePath = str(rootPath / folderName / (str(edtw_ItemData.shipID) + ".jpg"))
                scanTime = edtw_ItemData.scanTime
                ytName = edtw_ItemData.ytName
                classifyByYT[ytName] = classifyByYT.get(ytName, []) + [[filePath, scanTime]]
        # 然后就可以月台匹配设备配置了

        classifyByDevIP = {}
        for ytName, path_time in classifyByYT.items():
            # 先拿配置
            pass


if __name__ == "__main__":  # 用于当前窗体测试
    from app.utils.aboutconfig import configini

    app = QApplication(sys.argv)  # 创建GUI应用程序
    forms = DVW_Class()  # 创建窗体

    # forms.addFilePathsToexcelFile_LWData([__filePath1])
    forms.show()

    sys.exit(app.exec_())
