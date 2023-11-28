import sys
import os
from collections import Counter
from pathlib import Path

from PyQt5.QtCore import Qt, pyqtSlot, QEvent
from PyQt5.QtWidgets import (
    QApplication,
    QFileDialog,
    QMessageBox,
    QTableWidgetItem,
    QListWidgetItem, QWidget, QListWidget,
)
from configobj import ConfigObj
from loguru import logger
from typing import List

from app.esheet_process_widget.UI.ui_ExcelProcess import Ui_Form
from app.esheet_process_widget.utils.tabale_data_utils import getExcelDataTableWidgetData, getYtBindHCVRConfig
from app.esheet_process_widget.epw_define import SYTTWEnum, EDTWEnum, ExcelFileListWidgetItemDataStruct, SameYTCountTableWidgetItemDataStruct, ExcelDataTableWidgetItemDataStruct

from openpyxl.utils.exceptions import InvalidFileException


class Init_EPW_Widget(QWidget):
    def __init__(self, config):
        super().__init__()  # 调用父类构造函数，创建窗体
        self.ui = Ui_Form()  # 创建UI对象
        self.ui.setupUi(self)  # 构造UI界面
        self.epw_config = config["epw"]
        self.initUI()

    def initUI(self):
        self.initKeepShipNum_CB()

        # 这些是方法依赖的UI设定，不可更改
        self.ui.excelFile_LW.setSelectionMode(QListWidget.SingleSelection)  # get_FilePathInExcelFile_LW_ItemData



    def initKeepShipNum_CB(self):
        # 向月台保留下拉框中填充预定数据
        for num in self.epw_config["月台保留数量列表"]:
            self.ui.keepShipNum_CB.addItem(str(num))
            self.ui.keepShipNum_CB.setText("15")

    @pyqtSlot()
    def on_newFormat_RB_clicked(self):
        # 新格式单选按钮被点击
        self.ui.shipCID_LE.setText(self.epw_config["新格式"]["单号列"])
        self.ui.scanCID_LE.setText(self.epw_config["新格式"]["扫描时间列"])
        self.ui.ytCID_LE.setText(self.epw_config["新格式"]["月台号列"])

    @pyqtSlot()
    def on_oldFormat_RB_clicked(self):
        # 旧格式单选按钮被点击
        self.ui.shipCID_LE.setText(self.epw_config["旧格式"]["单号列"])
        self.ui.scanCID_LE.setText(self.epw_config["旧格式"]["扫描时间列"])
        self.ui.ytCID_LE.setText(self.epw_config["旧格式"]["月台号列"])


if __name__ == "__main__":  # 用于当前窗体测试
    from app.utils.aboutconfig import configini

    app = QApplication(sys.argv)  # 创建GUI应用程序
    forms = Init_EPW_Widget(configini)  # 创建窗体
    forms.show()
    sys.exit(app.exec_())
