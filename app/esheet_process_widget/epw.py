import sys
import os
from collections import Counter
from pathlib import Path

from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import (
    QApplication,
    QFileDialog,
    QMessageBox,
    QTableWidgetItem,
    QListWidgetItem, QWidget,
)
from loguru import logger
from typing import List

from qfluentwidgets import InfoBar, InfoBarPosition, MessageBox

from app.esheet_process_widget.UI.ui_ExcelProcess import Ui_Form
from app.esheet_process_widget.utils.tabale_data_utils import getExcelDataTableWidgetData, getYtBindHCVRConfig
from app.esheet_process_widget.epw_define import SYTTWEnum, EDTWEnum, ExcelFileListWidgetItemDataStruct, SameYTCountTableWidgetItemDataStruct, ExcelDataTableWidgetItemDataStruct
from app.esheet_process_widget.init_epw import Init_EPW_Widget
from openpyxl.utils.exceptions import InvalidFileException

devConfigFilePath = Path(__file__).parent.parent / "AppData/月台配置.xlsx"

# mainwindow那边定义logger，子组件这边共用的，不过是
# 写完这个组件的功能就可以把git重置一下了，历史信息就不要保留了


class EPW_Widget(Init_EPW_Widget):
    def __init__(self, config):
        super().__init__(config)  # 调用父类构造函数，创建窗体

    # f1 添加文件的数据表格处理
    @pyqtSlot(QListWidgetItem, QListWidgetItem)
    def on_excelFile_LW_currentItemChanged(self, current, previous):
        # 当前选中的item发生变化时，触发此函数
        if previous is not None:
            # 如果上一个item不为空，就先保存
            # 从窗体中获取排序数据和相同月台数量及previousItem中excel文件路径
            in_edtw_ItemDataList = self.getDataInExcelData_TW()
            in_sytctw_ItemDataList = self.getDataInsameYTCount_TW()
            excelFilePath = previous.data(Qt.UserRole).excelFilePath
            excelFile_LW_ItemData = ExcelFileListWidgetItemDataStruct()  # 创建excelFile_LW_ItemDataStruct对象
            excelFile_LW_ItemData.edtw_ItemDataList = in_edtw_ItemDataList
            excelFile_LW_ItemData.sytctw_ItemDataList = in_sytctw_ItemDataList
            excelFile_LW_ItemData.excelFilePath = excelFilePath
            previous.setData(Qt.UserRole, excelFile_LW_ItemData)
        if current is not None:
            # 如果当前item不为空，就加载
            self.clearEPW_WidgetText()  # 清空EPW窗体中所有的Text数据，防止数据混乱
            self.loadExcelFile_LW_ItemData(current.data(Qt.UserRole))
        else:
            # 如果当前item为空，就清空EPW窗体中所有的Text数据
            self.clearEPW_WidgetText()

    @pyqtSlot()
    def loadExcelFile_LW_ItemData(self, excelFile_LW_ItemData: ExcelFileListWidgetItemDataStruct):
        # 从excelFile_LW_ItemData中获取数据，加载到窗体中
        self.loadExcelData_TW(excelFile_LW_ItemData.edtw_ItemDataList)
        self.loadsameYTCount_TW(excelFile_LW_ItemData.sytctw_ItemDataList)

    @pyqtSlot()
    def loadExcelData_TW(self, edtw_ItemDataList: List[ExcelDataTableWidgetItemDataStruct]):
        # 加载excel数据表格组件数据

        self.ui.excelData_TW.setRowCount(len(edtw_ItemDataList))

        for index in range(len(edtw_ItemDataList)):
            item = QTableWidgetItem(str(edtw_ItemDataList[index].shipID))
            item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            col = EDTWEnum.ShipID.value
            self.ui.excelData_TW.setItem(index, col, item)

            item = QTableWidgetItem(str(edtw_ItemDataList[index].ytName))
            item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            col = EDTWEnum.YT.value
            self.ui.excelData_TW.setItem(index, col, item)

            item = QTableWidgetItem(str(edtw_ItemDataList[index].scanTime))
            item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            col = EDTWEnum.ScanTime.value
            self.ui.excelData_TW.setItem(index, col, item)

    @pyqtSlot()
    def loadsameYTCount_TW(self, sytctw_ItemDataList: List[SameYTCountTableWidgetItemDataStruct]):
        # 加载相同月台数量窗体数据
        self.ui.sameYTCount_TW.setRowCount(len(sytctw_ItemDataList))

        for index in range(len(sytctw_ItemDataList)):
            item = QTableWidgetItem(str(sytctw_ItemDataList[index].ytName))
            item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            col = SYTTWEnum.YT.value
            self.ui.sameYTCount_TW.setItem(index, col, item)

            item = QTableWidgetItem(str(sytctw_ItemDataList[index].shipCount))
            item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            col = SYTTWEnum.Count.value
            self.ui.sameYTCount_TW.setItem(index, col, item)

            item = QTableWidgetItem(str(sytctw_ItemDataList[index].devChannel))
            item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            col = SYTTWEnum.Channel.value
            self.ui.sameYTCount_TW.setItem(index, col, item)

    def getDataInExcelData_TW(self) -> List[ExcelDataTableWidgetItemDataStruct]:
        # 按照格式定义存放excelData_TW中的所有数据
        rowCount = self.ui.excelData_TW.rowCount()
        in_edtw_ItemDataList = []
        for index in range(rowCount):
            temp_edtw_ItemData = ExcelDataTableWidgetItemDataStruct()
            temp_edtw_ItemData.shipID = self.ui.excelData_TW.item(index, EDTWEnum.ShipID.value).text()
            temp_edtw_ItemData.ytName = self.ui.excelData_TW.item(index, EDTWEnum.YT.value).text()
            temp_edtw_ItemData.scanTime = self.ui.excelData_TW.item(index, EDTWEnum.ScanTime.value).text()
            in_edtw_ItemDataList.append(temp_edtw_ItemData)
        return in_edtw_ItemDataList

    def getDataInSameYTCount_TW(self) -> List[ExcelDataTableWidgetItemDataStruct]:
        # 按照格式定义存放sameYTCount_TW中的所有数据
        rowCount = self.ui.sameYTCount_TW.rowCount()
        in_syttlw_ItemDataList = []
        for index in range(rowCount):
            temp_syttlw_ItemData = ExcelDataTableWidgetItemDataStruct()
            temp_syttlw_ItemData.shipID = self.ui.sameYTCount_TW.item(index, SYTTWEnum.YT.value).text()
            temp_syttlw_ItemData.ytName = self.ui.sameYTCount_TW.item(index, SYTTWEnum.Count.value).text()
            temp_syttlw_ItemData.scanTime = self.ui.sameYTCount_TW.item(index, SYTTWEnum.Channel.value).text()
            in_syttlw_ItemDataList.append(temp_syttlw_ItemData)
        return in_syttlw_ItemDataList

    @pyqtSlot()
    def clearEPW_WidgetText(self):
        # 清空EPW窗体中的文本数据
        self.ui.excelData_TW.clearContents()
        self.ui.excelData_TW.setRowCount(0)
        self.ui.sameYTCount_TW.clearContents()
        self.ui.sameYTCount_TW.setRowCount(0)

    @pyqtSlot()
    def on_getfile_PB_clicked(self):
        # 添加文件按钮被点击
        # 获取文件名列表
        curPath = os.path.join(os.path.expanduser("~"), "Desktop")
        dlgTitle = "请选择要处理的Excel"
        filt = "文档(*.xlsx *.xls);;所有(*.*)"
        filePathList, filtUsed = QFileDialog.getOpenFileNames(self, dlgTitle, curPath, filt)
        # 如果列表不为空，则添加数据到暂存表中
        if filePathList:
            self.addFilePathsToexcelFile_LWData(filePathList)

    def addFilePathsToexcelFile_LWData(self, filePathList: List[str]):
        """
        添加文件路径到excelFile_LW中
        """
        for filePath in filePathList:
            fileName = os.path.basename(filePath)  # 获取文件名
            existexcelFile_LWItem = self.ui.excelFile_LW.findItems(fileName, Qt.MatchExactly)  # 查找预添加的文件名称是否已经存在
            if existexcelFile_LWItem:
                # inaItemDatafileAddress = self.getInexcelFile_LWaddedAppointFileAdress(fileName)  # 找到这个同名文件地址
                # loggerWaringText = "文件名重复,如要替换请先删除列表中的同名数据\n已存在于列表中的同名文件绝对地址为：\n" + str(inaItemDatafileAddress) + "\n当前重复文件名称的绝对文件地址为：\n" + str(filePath)
                loggerWaringText = f"{fileName}文件名重复，请在修改文件名称后重新尝试添加"
                InfoBar.warning(title='警告', content=loggerWaringText, orient=Qt.Horizontal, isClosable=True, position=InfoBarPosition.TOP_LEFT, duration=10000, parent=self)
                logger.warning(loggerWaringText)
            else:
                excelFile_LW_ItemData = self.handleExcelFileData2ItemData(filePath)
                if excelFile_LW_ItemData is not None:
                    aItem = QListWidgetItem(fileName)
                    aItem.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                    aItem.setData(Qt.UserRole, excelFile_LW_ItemData)
                    self.ui.excelFile_LW.addItem(aItem)

    def getSameYTCountTableWidgetData(self, edtw_ItemDataList: List[ExcelDataTableWidgetItemDataStruct]) -> List[SameYTCountTableWidgetItemDataStruct]:
        # 处理getExcelDataTableWidgetData返回的数据
        # 得到 相同月台的单号总量和月台通道配置

        ytNameList = [edtw_ItemData.ytName for edtw_ItemData in edtw_ItemDataList]
        counter = Counter(ytNameList)  # 字典子类用于统计可哈希对象数量
        sameYTCount = list(counter.most_common())  # 最大值顺序，顺便转成list

        # 这里拿到了单号总量和月台通道配置，应该新开一个list

        sytctw_ItemDataList = []
        try:
            # 判断文件是否存在
            config_generate = getYtBindHCVRConfig(devConfigFilePath)
            next(config_generate)  # 启动生成器
            for yt, shipCount in sameYTCount:
                temp_ItemDataList = SameYTCountTableWidgetItemDataStruct()
                temp_ItemDataList.ytName = yt
                temp_ItemDataList.shipCount = shipCount
                temp_ItemDataList.devChannel = config_generate.send(yt)  # 向生成器发送月台名称
                next(config_generate)  # 驱动生成器执行到ytName = yield，以便接收下一个月台名称
                sytctw_ItemDataList.append(temp_ItemDataList)
            config_generate.close()  # 手动关闭生成器
            return sytctw_ItemDataList
        except InvalidFileException:
            loggerErrorText = f"设备配置文件格式错误，请检查文件是否为xlsx或xls\n{devConfigFilePath}"
            MessageBox('错误', loggerErrorText, self).exec_()
            logger.warning(loggerErrorText)
            return
        except FileNotFoundError:
            loggerErrorText = f"设备配置文件不存在，请检查文件路径\n{devConfigFilePath}"
            MessageBox('错误', loggerErrorText, self).exec_()
            logger.warning(loggerErrorText)
            return

    def handleExcelFileData2ItemData(self, filePath: str) -> ExcelFileListWidgetItemDataStruct:
        """
        获取excel文件的指定行列数据，并返回excelFile_LW_ItemDataStruct
        return excelFile_LW_ItemData:excelFileListWidgetItemDataStruct
        """
        logger.info("本次处理的Excel文件地址为:" + filePath)
        shipidCID = self.ui.shipCID_LE.text()  # 单号数据列 column
        scantimeCID = self.ui.scanCID_LE.text()  # 扫描时间列
        ytCID = self.ui.ytCID_LE.text()  # 月台号列
        try:
            # 这个地方获取的是中间的那个表格组件的数据，
            edtw_ItemDataList = getExcelDataTableWidgetData(filePath, shipidCID, scantimeCID, ytCID)
        except InvalidFileException:
            loggerErrorText = f"文件格式错误\n{filePath}"
            MessageBox('错误', loggerErrorText, self).exec_()
            logger.warning(loggerErrorText)
            return
        except FileNotFoundError:
            loggerErrorText = f"文件不存在\n{filePath}"
            MessageBox('错误', loggerErrorText, self).exec_()
            logger.warning(loggerErrorText)
            return

        sytctw_ItemDataList = self.getSameYTCountTableWidgetData(edtw_ItemDataList)  # 处理excel文件中二维列表数据
        if sytctw_ItemDataList is None:
            return
        excelFile_LW_ItemData = ExcelFileListWidgetItemDataStruct()  # 保存数据
        excelFile_LW_ItemData.edtw_ItemDataList = edtw_ItemDataList
        excelFile_LW_ItemData.sytctw_ItemDataList = sytctw_ItemDataList
        excelFile_LW_ItemData.excelFilePath = filePath
        return excelFile_LW_ItemData  # 返回excelFile_LW_ItemDataStruct对象

    def getInexcelFile_LWaddedAppointFileAdress(self, fileName: str) -> str:
        # 获取在excelFile_LW组件中已经添加过的指定的文件地址
        FindedItem = self.ui.excelFile_LW.findItems(fileName, Qt.MatchExactly)
        excelFile_LW_ItemData = FindedItem[0].data(Qt.UserRole)
        inaItemDatafilePath = excelFile_LW_ItemData.excelFilePath
        return inaItemDatafilePath

    @pyqtSlot()
    def on_reprocessExcelFile_PB_clicked(self):
        print("123")


if __name__ == "__main__":  # 用于当前窗体测试
    from app.utils.aboutconfig import configini

    app = QApplication(sys.argv)  # 创建GUI应用程序
    forms = EPW_Widget(configini)  # 创建窗体
    forms.show()
    desktopPath = os.path.join(os.path.expanduser('~'), 'Desktop')
    __filePath = os.path.join(desktopPath, "test.xlsx")
    forms.addFilePathsToexcelFile_LWData([__filePath])
    sys.exit(app.exec_())
