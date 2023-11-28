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
    QListWidgetItem, QWidget,
)
from loguru import logger
from typing import List

from qfluentwidgets import InfoBar, InfoBarPosition, MessageBox, InfoBarIcon

from app.esheet_process_widget.UI.ui_ExcelProcess import Ui_Form
from app.esheet_process_widget.utils.tabale_data_utils import getExcelDataTableWidgetData, getYtBindHCVRConfig, DevConfigFileNotFoundError, DevConfigFileInvalidError, FileContenIsEmptyException, \
    getSameYTCountTableWidgetData
from app.esheet_process_widget.epw_define import SYTTWEnum, EDTWEnum, ExcelFileListWidgetItemDataStruct, SameYTCountTableWidgetItemDataStruct, ExcelDataTableWidgetItemDataStruct
from app.esheet_process_widget.init_epw import Init_EPW_Widget
from openpyxl.utils.exceptions import InvalidFileException


# mainwindow那边定义logger，子组件这边共用的，不过是没有独立的作用域标记了，但文件地址也能说明问题了


class EPW_Widget(Init_EPW_Widget):
    def __init__(self, config):
        super().__init__(config)  # 调用父类构造函数，创建窗体
        self.setAcceptDrops(True)  # 开启拖拽

    @pyqtSlot(QListWidgetItem, QListWidgetItem)
    def on_excelFile_LW_currentItemChanged(self, current, previous):
        # 当前选中的item发生变化时，触发此函数
        if previous is not None:
            # 如果上一个item不为空，就先保存
            # 从窗体中获取排序数据和相同月台数量及previousItem中excel文件路径
            # 由于我重写了该方法，所以此时界面上的数据还没有改变，
            # 下面两个方法是从界面上取得的数值，而非从curItem或preItem
            in_edtw_ItemDataList = self.getDataInExcelData_TW()
            in_sytctw_ItemDataList = self.getDataInSameYTCount_TW()
            # 但curItem, preItem确实改变了，而excelFilePath又没有放到界面上
            # 所以需要一些稍微“另类”的方法来获取到这个excelFilePath
            # 更加符合直觉的方法应该是QAbstractItemView.selectionChanged(selected, deselected)
            excelFilePath = self.get_FilePathInExcelFile_LW_ItemData()
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
    def get_FilePathInExcelFile_LW_ItemData(self):
        # 获取当前选中的item中的excelFilePath数据
        # 确保excelFile_LW是单选的
        # 因on_excelFile_LW_currentItemChanged处理逻辑而使用selectedItems
        curItemDataFilePath = self.ui.excelFile_LW.selectedItems()[0].data(Qt.UserRole).excelFilePath
        return curItemDataFilePath

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
        self.ui.excelData_TW.resizeColumnsToContents()  # 调整列宽

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
        self.ui.sameYTCount_TW.resizeColumnsToContents()  # 调整列宽

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

    def getDataInSameYTCount_TW(self) -> List[SameYTCountTableWidgetItemDataStruct]:
        # 按照格式定义存放sameYTCount_TW中的所有数据
        rowCount = self.ui.sameYTCount_TW.rowCount()
        in_syttlw_ItemDataList = []
        for index in range(rowCount):
            temp_syttlw_ItemData = SameYTCountTableWidgetItemDataStruct()
            temp_syttlw_ItemData.ytName = self.ui.sameYTCount_TW.item(index, SYTTWEnum.YT.value).text()
            temp_syttlw_ItemData.shipCount = self.ui.sameYTCount_TW.item(index, SYTTWEnum.Count.value).text()
            temp_syttlw_ItemData.devChannel = self.ui.sameYTCount_TW.item(index, SYTTWEnum.Channel.value).text()
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
                try:
                    excelFile_LW_ItemData = self.handleExcelFileData2ItemData(filePath)
                except FileContenIsEmptyException:  # 要处理的excel文件是空的,应该是选错文件了，或者输错了列号了
                    loggerErrorText = f"文件是空的，注意检查是否填错数据列号或选错文件\n{filePath}"
                    MessageBox('错误', loggerErrorText, self).exec_()
                    logger.warning(loggerErrorText)
                except InvalidFileException:
                    loggerErrorText = f"文件格式错误，确保文件格式为xlsx或xls及文件路径中不能含有空格\n{filePath}"
                    MessageBox('错误', loggerErrorText, self).exec_()
                    logger.warning(loggerErrorText)
                except FileNotFoundError:
                    loggerErrorText = f"文件不存在，注意文件路径中不能含有空格\n{filePath}"
                    MessageBox('错误', loggerErrorText, self).exec_()
                    logger.warning(loggerErrorText)
                except DevConfigFileNotFoundError as ErrorText:  # 设备配置文件路径是写的相对的，写在处理函数中的，可能会出现点问题吧
                    MessageBox('错误', str(ErrorText), self).exec_()
                    logger.warning(str(ErrorText))
                except DevConfigFileInvalidError as ErrorText:  # 设备配置文件格式不合法，非xlsx，xls或文件名中有空格。
                    MessageBox('错误', str(ErrorText), self).exec_()
                    logger.warning(str(ErrorText))
                else:
                    aItem = QListWidgetItem(fileName)
                    aItem.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                    aItem.setData(Qt.UserRole, excelFile_LW_ItemData)
                    self.ui.excelFile_LW.addItem(aItem)
        # 全部添加完毕后，选中excelFile_LW最后一个项目
        self.ui.excelFile_LW.setCurrentRow(self.ui.excelFile_LW.count() - 1)

    def handleExcelFileData2ItemData(self, filePath: str) -> ExcelFileListWidgetItemDataStruct:
        """
        获取excel文件的指定行列数据，并返回excelFile_LW_ItemDataStruct
        return excelFile_LW_ItemData:excelFileListWidgetItemDataStruct
        """
        logger.info("本次处理的Excel文件地址为:" + filePath)
        shipidCID = self.ui.shipCID_LE.text()  # 单号数据列 column
        scantimeCID = self.ui.scanCID_LE.text()  # 扫描时间列
        ytCID = self.ui.ytCID_LE.text()  # 月台号列
        edtw_ItemDataList = getExcelDataTableWidgetData(filePath, shipidCID, scantimeCID, ytCID)  # 获取excel文件中的数据，这个部分要放到中间的表格组件中
        sytctw_ItemDataList = getSameYTCountTableWidgetData(edtw_ItemDataList)  # 从上一步函数的返回值中获取相同月台表格组件中的数据
        excelFile_LW_ItemData = ExcelFileListWidgetItemDataStruct()  # 统一保存
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
        # 重新处理文件按钮被点击,
        selectedItems = self.ui.excelFile_LW.selectedItems()  # 获取List组件中选中的项目
        if selectedItems:
            selectedItem = selectedItems[0]
            selectedItemText = selectedItem.text()
            filePath = self.get_FilePathInExcelFile_LW_ItemData()
            excelFile_LW_ItemData = self.handleExcelFileData2ItemData(filePath)
            self.clearEPW_WidgetText()
            self.loadExcelFile_LW_ItemData(excelFile_LW_ItemData)
            InfoBar.success(title='成功', content=f"已重新加载{selectedItemText}", orient=Qt.Horizontal, isClosable=True, position=InfoBarPosition.TOP_LEFT, duration=1000, parent=self)
        else:
            InfoBar.warning(title='警告', content="未选中任何项目", orient=Qt.Horizontal, isClosable=True, position=InfoBarPosition.TOP_LEFT, duration=1000, parent=self)

    @pyqtSlot()
    def on_deleteExcelFileLWItem_PB_clicked(self):
        # 删除选中文件按钮点击
        selectedItems = self.ui.excelFile_LW.selectedItems()  # 获取List组件中选中的项目
        if selectedItems:
            selectedItem = selectedItems[0]
            selectedItemText = selectedItem.text()
            selectedItemRow = self.ui.excelFile_LW.row(selectedItems[0])
            self.ui.excelFile_LW.takeItem(selectedItemRow)
            InfoBar.success(title='成功', content=f"已删除{selectedItemText}", orient=Qt.Horizontal, isClosable=True, position=InfoBarPosition.TOP_LEFT, duration=1000, parent=self)
            self.ui.excelFile_LW.setCurrentRow(self.ui.excelFile_LW.count() - 1)
        else:
            InfoBar.warning(title='警告', content="未选中任何项目", orient=Qt.Horizontal, isClosable=True, position=InfoBarPosition.TOP_LEFT, duration=1000, parent=self)

    @pyqtSlot(QEvent)
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    @pyqtSlot(QEvent)
    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            filePaths = [url.toLocalFile() for url in event.mimeData().urls()]
            logger.debug(f"拖拽接收到的文件列表为{str(filePaths)}")
            self.addFilePathsToexcelFile_LWData(filePaths)
            event.accept()
        else:
            event.ignore()


if __name__ == "__main__":  # 用于当前窗体测试
    from app.utils.aboutconfig import configini

    app = QApplication(sys.argv)  # 创建GUI应用程序
    forms = EPW_Widget(configini)  # 创建窗体
    forms.show()

    # TODO 有个方法能立即处理现有的事件队列，忘了
    # 那个生成器可以一直保留着(不然我看处理速度好像有点慢，这是一个优化点。没必要一个文件还需要读一次配置，浪费资源时间)，excel文件记得关

    __desktopPath = os.path.join(os.path.expanduser('~'), 'Desktop')
    __filePath1 = os.path.join(__desktopPath, "1127.xlsx")
    __filePath2 = os.path.join(__desktopPath, "1128.xlsx")
    forms.addFilePathsToexcelFile_LWData([__filePath1, __filePath2])
    sys.exit(app.exec_())
