import sys
import os
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed

from PyQt5.QtCore import Qt, pyqtSlot, QEvent, QItemSelectionModel, pyqtSignal
from PyQt5.QtWidgets import QApplication, QFileDialog, QTableWidgetItem, QListWidgetItem, QAbstractItemView
from loguru import logger
from typing import List
from qfluentwidgets import InfoBar, InfoBarPosition, MessageBox
from app.esheet_process_widget.utils.tabale_data_utils import getExcelDataTableWidgetData, FileContentIsEmptyException, getSameYTCountTableWidgetData
from app.esheet_process_widget.epw_define import SYTTWEnum, EDTWEnum, ExcelFileListWidgetItemDataStruct, SameYTCountTableWidgetItemDataStruct, ExcelDataTableWidgetItemDataStruct
from app.esheet_process_widget.base_epw import Base_EPW_Widget
from openpyxl.utils.exceptions import InvalidFileException


# mainwindow那边定义logger，子组件这边共用的，不过是没有独立的作用域标记了，但文件地址也能说明问题了


class EPWclass(Base_EPW_Widget):
    showErrorMsgBox = pyqtSignal(str, str)  # 多线程函数里有个需要弹窗的步骤，需要用个信号显示

    def __init__(self, parent=None):
        super().__init__(parent)  # 调用父类构造函数，创建窗体
        self.setAcceptDrops(True)  # 开启拖拽
        self.init_ui()

        self.showErrorMsgBox.connect(self.showMessageBox)  # 多线程函数里有个需要弹窗的步骤，需要用个信号来调槽函数显示

    def init_ui(self):
        self.connect_keepShipNum_SPB_Action()

    @pyqtSlot(QListWidgetItem, QListWidgetItem)
    def on_excelFile_LW_currentItemChanged(self, current, previous):
        # 用户选择不同的项目触发该方法
        if previous is not None:
            # 如果上一个item不为空，就先保存
            excelFile_LW_ItemData = self.getExcelFile_LW_ItemData()
            previous.setData(Qt.UserRole, excelFile_LW_ItemData)
        if current is not None:
            # 如果当前item不为空，就加载
            self.clearEPW_WidgetText()  # 清空EPW窗体中所有的Text数据，防止数据混乱
            self.loadExcelFile_LW_ItemData(current.data(Qt.UserRole))
        else:
            # 如果当前item为空，就清空EPW窗体中所有的Text数据
            self.clearEPW_WidgetText()

    def getExcelFile_LW_ItemData(self):
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
        return excelFile_LW_ItemData

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
        self.ui.excelData_TW.updateSelectedRows()  # 刷新主题显示状态

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
        self.ui.sameYTCount_TW.updateSelectedRows()  # 刷新主题显示状态

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
        # 添加文件按钮被点击，获取文件名列表
        curPath = os.path.join(os.path.expanduser("~"), "Desktop")
        dlgTitle = "请选择要处理的Excel"
        filt = "文档(*.xlsx *.xls);;所有(*.*)"
        filePathList, filtUsed = QFileDialog.getOpenFileNames(self, dlgTitle, curPath, filt)
        if filePathList:
            self.addFilePathsToexcelFile_LWData(filePathList)

    def addFilePathsToexcelFile_LWData(self, filePathList: List[str]):
        """
        添加excel文件路径到excelFile_LW中，将excel文件中的数据处理后添加到组件item的data中
        """

        repeatFileNameList = []
        allowFilePathList = []

        excelFile_LW_RowCount = self.ui.excelFile_LW.count()
        for filePath in filePathList:
            fileName = os.path.basename(filePath)  # 获取文件名
            existexcelFile_LWItem = self.ui.excelFile_LW.findItems(fileName, Qt.MatchExactly)  # 查找预添加的文件名称是否已经存在
            if existexcelFile_LWItem:
                repeatFileNameList.append(fileName)
            else:
                allowFilePathList.append(filePath)

        # 多线程开始处理文件
        self.thredPoolProcessingFiles(allowFilePathList)

        #
        for fileName in repeatFileNameList:
            # inaItemDatafileAddress = self.getInexcelFile_LWaddedAppointFileAdress(fileName)  # 找到这个同名文件地址
            # loggerWaringText = "文件名重复,如要替换请先删除列表中的同名数据\n已存在于列表中的同名文件绝对地址为：\n" + str(inaItemDatafileAddress) + "\n当前重复文件名称的绝对文件地址为：\n" + str(filePath)
            loggerWaringText = f"{fileName}文件名重复，请在修改文件名称后重新尝试添加"
            InfoBar.warning(title='警告', content=loggerWaringText, orient=Qt.Horizontal, isClosable=True,
                            position=InfoBarPosition.TOP_LEFT, duration=10000, parent=self)
            logger.warning(loggerWaringText)

        # 全部添加完毕后，判断是否新增项目。如果比处理文件之前的总数要多，就选中excelFile_LW最后一个项目
        if self.ui.excelFile_LW.count() > excelFile_LW_RowCount:
            self.ui.excelFile_LW.setCurrentRow(self.ui.excelFile_LW.count() - 1)
            InfoBar.success(title='成功', content="处理完成", orient=Qt.Horizontal, isClosable=True,
                            position=InfoBarPosition.TOP_LEFT, duration=1000, parent=self)

    def thredPoolProcessingFiles(self, allowFilePathList):
        def subFun(filePath):
            inThreadExcelFile_LW_ItemData = self.handleExcelFileData2ItemData(filePath)
            inThreadFileName = os.path.basename(filePath)  # 获取文件名
            return inThreadFileName, inThreadExcelFile_LW_ItemData

        with ThreadPoolExecutor() as executor:  # 3.8的max_workers 的默认值已改为 min(32, os.cpu_count() + 4)
            futures = {executor.submit(subFun, filePath) for filePath in allowFilePathList}
            for future in as_completed(futures):
                try:
                    result = future.result()
                    fileName, excelFile_LW_ItemData = result
                    if excelFile_LW_ItemData:
                        aItem = QListWidgetItem(fileName)
                        aItem.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                        aItem.setData(Qt.UserRole, excelFile_LW_ItemData)
                        self.ui.excelFile_LW.addItem(aItem)
                        QApplication.processEvents()
                except Exception as e:
                    print(f"An error occurred while processing a file: {e}")

    def handleExcelFileData2ItemData(self, filePath: str) -> ExcelFileListWidgetItemDataStruct:
        # 获取excel文件的指定行列数据，并返回excelFile_LW_ItemDataStruct
        logger.info("本次处理的Excel文件地址为:" + filePath)
        if self.ui.customFormat_SB.isChecked():
            shipid_CID = self.ui.shipCID_LE.text()  # 单号数据列
            scanTime_CID = self.ui.scanTimeCID_LE.text()  # 扫描时间列
            yt_CID = self.ui.ytCID_LE.text()  # 月台号列
            scanTimeFormat_CID = self.ui.scanTimeFormat_LE.text()  # 扫描时间的处理格式
        else:
            shipid_CID = scanTime_CID = yt_CID = scanTimeFormat_CID = None
        try:
            edtw_ItemDataList = getExcelDataTableWidgetData(filePath, shipid_CID, scanTime_CID, yt_CID, scanTimeFormat_CID)  # 用户没选自定义列号就用函数中缺省的列号
            sytctw_ItemDataList = getSameYTCountTableWidgetData(edtw_ItemDataList)  # 从上一步函数的返回值中获取相同月台表格组件中的数据
        except FileContentIsEmptyException:  # 要处理的excel文件是空的,应该是选错文件了，或者输错了列号了
            loggerErrorText = f"文件是空的，注意检查是否填错数据列号或选错文件\n{filePath}"
            # MessageBox('错误', loggerErrorText, self).exec_()
            self.showErrorMsgBox.emit("错误", loggerErrorText)
            logger.warning(loggerErrorText)
        except InvalidFileException:
            loggerErrorText = f"文件格式错误或文件路径有误，确保文件格式为xlsx或xls及文件路径中不能含有空格\n{filePath}"
            # MessageBox('错误', loggerErrorText, self).exec_()
            self.showErrorMsgBox.emit("错误", loggerErrorText)
            logger.warning(loggerErrorText)
        except FileNotFoundError:
            loggerErrorText = f"文件不存在，注意文件路径中不能含有空格\n{filePath}"
            # MessageBox('错误', loggerErrorText, self).exec_()
            self.showErrorMsgBox.emit("错误", loggerErrorText)
            logger.warning(loggerErrorText)
        else:
            excelFile_LW_ItemData = ExcelFileListWidgetItemDataStruct()  # 统一保存
            excelFile_LW_ItemData.edtw_ItemDataList = edtw_ItemDataList
            excelFile_LW_ItemData.sytctw_ItemDataList = sytctw_ItemDataList
            excelFile_LW_ItemData.excelFilePath = filePath
            return excelFile_LW_ItemData

    @pyqtSlot(str, str)
    def showMessageBox(self, title, text):  # 多线程函数里有个需要弹窗的步骤，需要用个槽函数来显示
        MessageBox(title, text, self).show()  # 主题作者不知道设置了什么，就算不用exec_也可以屏蔽用户对界面的操作，而不用阻塞事件循环，很棒!

    def getInexcelFile_LWaddedAppointFileAdress(self, fileName: str) -> str:
        # 获取在excelFile_LW组件中已经添加过的指定的文件地址
        FindedItem = self.ui.excelFile_LW.findItems(fileName, Qt.MatchExactly)
        excelFile_LW_ItemData = FindedItem[0].data(Qt.UserRole)
        inItemDatafilePath = excelFile_LW_ItemData.excelFilePath
        return inItemDatafilePath

    @pyqtSlot()
    def on_reprocessExcelFile_PB_clicked(self):
        # 重新处理文件按钮被点击,
        selectedItems = self.ui.excelFile_LW.selectedItems()  # 获取List组件中选中的项目
        if selectedItems:
            selectedItem = selectedItems[0]
            selectedItemText = selectedItem.text()
            filePath = self.get_FilePathInExcelFile_LW_ItemData()  # 拿到这个项目保存的文件地址
            excelFile_LW_ItemData = self.handleExcelFileData2ItemData(filePath)  # 通过内部方法直接得到ExcelFileListWidgetItemDataStruct
            if excelFile_LW_ItemData:  # 这里的写法跳过了文件名重复判断和ListWidgetItem.setData()
                self.clearEPW_WidgetText()  # 因为切项目的时候会自动保存
                self.loadExcelFile_LW_ItemData(excelFile_LW_ItemData)
                InfoBar.success(title='成功', content=f"已重新加载{selectedItemText}", orient=Qt.Horizontal, isClosable=True,
                                position=InfoBarPosition.TOP_LEFT, duration=1000, parent=self)
            else:
                InfoBar.error(title='错误', content=f"重新加载{selectedItemText}失败", orient=Qt.Horizontal, isClosable=True,
                              position=InfoBarPosition.TOP_LEFT, duration=1000, parent=self)
        else:
            InfoBar.warning(title='警告', content="未选中任何项目", orient=Qt.Horizontal, isClosable=True,
                            position=InfoBarPosition.TOP_LEFT, duration=1000, parent=self)

    @pyqtSlot()
    def on_deleteExcelFileLWItem_PB_clicked(self):
        # 删除选中文件按钮点击
        selectedItems = self.ui.excelFile_LW.selectedItems()  # 获取List组件中选中的项目
        if selectedItems:
            selectedItem = selectedItems[0]
            selectedItemText = selectedItem.text()
            selectedItemRow = self.ui.excelFile_LW.row(selectedItems[0])
            self.ui.excelFile_LW.takeItem(selectedItemRow)
            InfoBar.success(title='成功', content=f"已删除{selectedItemText}", orient=Qt.Horizontal, isClosable=True,
                            position=InfoBarPosition.TOP_LEFT, duration=1000, parent=self)
            self.ui.excelFile_LW.setCurrentRow(self.ui.excelFile_LW.count() - 1)
        else:
            InfoBar.warning(title='警告', content="未选中任何项目", orient=Qt.Horizontal, isClosable=True,
                            position=InfoBarPosition.TOP_LEFT, duration=1000, parent=self)

    @pyqtSlot(QEvent)
    def dragEnterEvent(self, event):
        # 允许拖拽url进入
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    @pyqtSlot(QEvent)
    def dropEvent(self, event):
        # 允许用户通过拖拽添加要处理的excel文件
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            filePaths = [url.toLocalFile() for url in event.mimeData().urls()]
            logger.debug(f"拖拽接收到的文件列表为{str(filePaths)}")
            self.addFilePathsToexcelFile_LWData(filePaths)
            event.accept()
        else:
            event.ignore()

    @pyqtSlot()
    def on_keepShipNum_SPB_clicked(self):
        # 保留选中月台中指定数量的单号按钮被点击
        keepNum = self.ui.keepShipNum_SPB.text()
        self.keepAppointNumShipIDInYt(int(keepNum))  # 向删除函数传入按钮上的数值

    def connect_keepShipNum_SPB_Action(self):
        # 连接按钮中的菜单中的action触发信号到内部函数中
        def getNum(checked: bool):
            keepNum = int(self.sender().text())
            self.keepAppointNumShipIDInYt(keepNum)

        # action.triggered.connect(lambda: self.keepAppointNumShipIDInYt(int(action.text())))
        # 如果这么连接函数就会导致所有action传参都是最后一个keepNum，记得以前就是这么传的呀，无奈用了这种方法
        for action in self.ui.keepShipNum_SPB.flyout.menuActions():
            action.triggered.connect(getNum)

    def keepAppointNumShipIDInYt(self, keepNum: int):
        # 在选中月台中仅保留指定数量的单号
        selectedRows = self.ui.sameYTCount_TW.selectionModel().selectedRows(SYTTWEnum.YT.value)
        if not selectedRows:
            InfoBar.warning(title='警告', content="未选中任何月台", orient=Qt.Horizontal, isClosable=True,
                            position=InfoBarPosition.TOP, duration=1000, parent=self.ui.sameYTCount_TW)
            return
        deleteShipIdNumDict = {}
        for modelIndex in selectedRows:
            row = modelIndex.row()  # 用QModelIndex更规矩一点
            ytName = self.ui.sameYTCount_TW.item(row, SYTTWEnum.YT.value).text()  # 我晓得modelIndex指的我现在要取的item
            shipCount = int(self.ui.sameYTCount_TW.item(row, SYTTWEnum.Count.value).text())
            if shipCount > keepNum:  # 同月台的单号总量大于想要保留的数量才需要删
                deleteNum = shipCount - keepNum
                deleteShipIdNumDict[ytName] = deleteNum
        # 上面取到了要删除的月台中的单号数量和月台名称
        ytNameDict = {}
        for row in range(self.ui.excelData_TW.rowCount()):  # 全取行数后做切片和取中判行数，我选了前者
            ytName = self.ui.excelData_TW.item(row, EDTWEnum.YT.value).text()
            ytNameDict[ytName] = ytNameDict.get(ytName, []) + [row]

        rows_to_delete = []  # 创建一个列表用来存储准备删除的行号
        for ytName in deleteShipIdNumDict.keys():  # ytNameDict存的是所有的yt行数，我这里只需要拿deleteNum个行数进行删除
            rows_to_delete.extend(ytNameDict[ytName][:deleteShipIdNumDict[ytName]])
        rows_to_delete.sort(reverse=True)  # 倒序删除不会影响index
        for row in rows_to_delete:
            self.ui.excelData_TW.removeRow(row)
        self.afterDelete_RecalculateSameYTCountTableWidgetData()
        InfoBar.success(title='成功', content=f"已保留指定数量月台中的单号数量", orient=Qt.Horizontal, isClosable=True,
                        position=InfoBarPosition.TOP, duration=1000, parent=self.ui.sameYTCount_TW)

    def afterDelete_RecalculateSameYTCountTableWidgetData(self):
        # 由于整个EPW只有删除的操作，在删除操作完成之后重新计算相同月台表格的数据
        # 不用重新匹配设备配置，我只是改变了单号数量

        ytNameList = [self.ui.excelData_TW.item(row, EDTWEnum.YT.value).text() for row in
                      range(self.ui.excelData_TW.rowCount())]
        sameYTCount = Counter(ytNameList)  # 字典子类用于统计可哈希对象数量
        # 更新sameYTCount_TW的单号总量列数据，
        for row in range(self.ui.sameYTCount_TW.rowCount() - 1, -1, -1):
            yTNameInRow = self.ui.sameYTCount_TW.item(row, SYTTWEnum.YT.value).text()
            newCount = sameYTCount[yTNameInRow]
            if newCount == 0:
                self.ui.sameYTCount_TW.removeRow(row)
            else:
                item = QTableWidgetItem(str(sameYTCount[yTNameInRow]))
                item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                self.ui.sameYTCount_TW.setItem(row, SYTTWEnum.Count.value, item)
        self.ui.excelData_TW.updateSelectedRows()
        self.ui.sameYTCount_TW.updateSelectedRows()

    @pyqtSlot()
    def on_selectAllShipID_PB_clicked(self):
        # 全选单号被按下
        self.ui.excelData_TW.selectAll()
        InfoBar.success(title='成功', content=f"已全选单号", orient=Qt.Horizontal, isClosable=True,
                        position=InfoBarPosition.TOP, duration=1000, parent=self.ui.excelData_TW)

    @pyqtSlot()
    def on_selectAllYT_PB_clicked(self):
        # 全选月台被按下
        self.ui.sameYTCount_TW.selectAll()
        InfoBar.success(title='成功', content=f"已全选月台", orient=Qt.Horizontal, isClosable=True,
                        position=InfoBarPosition.TOP, duration=1000, parent=self.ui.sameYTCount_TW)

    @pyqtSlot()
    def on_reverseSelectionShipID_PB_clicked(self):
        # 反选单号按钮被按下
        self.ui.excelData_TW.setSelectionBehavior(QAbstractItemView.SelectRows)
        selectionModel = self.ui.excelData_TW.selectionModel()
        for row in range(self.ui.excelData_TW.rowCount()):
            item = self.ui.excelData_TW.item(row, 0)
            modelIndex = self.ui.excelData_TW.indexFromItem(item)
            if item.isSelected():
                selectionModel.select(modelIndex, QItemSelectionModel.Deselect | QItemSelectionModel.Rows)
            else:
                selectionModel.select(modelIndex, QItemSelectionModel.Select | QItemSelectionModel.Rows)
        self.ui.excelData_TW.updateSelectedRows()
        InfoBar.success(title='成功', content=f"已反选单号", orient=Qt.Horizontal, isClosable=True,
                        position=InfoBarPosition.TOP, duration=1000, parent=self.ui.excelData_TW)

    @pyqtSlot()
    def on_reverseSelectionYT_PB_clicked(self):
        # 反选月台按钮被按下
        selectionModel = self.ui.sameYTCount_TW.selectionModel()
        for row in range(self.ui.sameYTCount_TW.rowCount()):
            item = self.ui.sameYTCount_TW.item(row, 0)
            modelIndex = self.ui.sameYTCount_TW.indexFromItem(item)
            if item.isSelected():
                selectionModel.select(modelIndex, QItemSelectionModel.Deselect | QItemSelectionModel.Rows)
            else:
                selectionModel.select(modelIndex, QItemSelectionModel.Select | QItemSelectionModel.Rows)
        self.ui.sameYTCount_TW.updateSelectedRows()
        InfoBar.success(title='成功', content=f"已反选月台", orient=Qt.Horizontal, isClosable=True,
                        position=InfoBarPosition.TOP, duration=1000, parent=self.ui.sameYTCount_TW)

    @pyqtSlot()
    def on_deleteSelectionShipID_PB_clicked(self):
        # 删除单号按钮被按下
        selectItems = self.ui.excelData_TW.selectionModel().selectedRows(SYTTWEnum.YT.value)
        if selectItems:
            for modelIndex in reversed(selectItems):
                self.ui.excelData_TW.removeRow(modelIndex.row())  # 倒序删除不会影响index
            self.afterDelete_RecalculateSameYTCountTableWidgetData()
            InfoBar.success(title='成功', content=f"已删除选中单号", orient=Qt.Horizontal, isClosable=True,
                            position=InfoBarPosition.TOP, duration=1000, parent=self.ui.excelData_TW)
        else:
            InfoBar.warning(title='警告', content="未选中任何行", orient=Qt.Horizontal, isClosable=True,
                            position=InfoBarPosition.TOP, duration=1000, parent=self.ui.excelData_TW)

    @pyqtSlot()
    def on_deleteSelectionYT_PB_clicked(self):
        # 删除月台按钮被按下
        selectItems = self.ui.sameYTCount_TW.selectionModel().selectedRows(SYTTWEnum.YT.value)
        if not selectItems:
            InfoBar.warning(title='警告', content="未选中任何月台", orient=Qt.Horizontal, isClosable=True,
                            position=InfoBarPosition.TOP, duration=1000, parent=self.ui.sameYTCount_TW)
            return
        ytNameList = []
        for modelIndex in selectItems:
            delete_YtName = self.ui.sameYTCount_TW.itemFromIndex(modelIndex).text()
            ytNameList.append(delete_YtName)
        self.deleteExcelData_TW_ItemByYTName(ytNameList)
        InfoBar.success(title='成功', content=f"已删除选中月台", orient=Qt.Horizontal, isClosable=True,
                        position=InfoBarPosition.TOP, duration=1000, parent=self.ui.sameYTCount_TW)

    def deleteExcelData_TW_ItemByYTName(self, ytNameList: List[str]):
        # 删除excelData_TW中指定月台的数据
        # 做月台名称和行号的映射，value是个list，存放行数
        ytNameDict = {}
        for row in range(self.ui.excelData_TW.rowCount()):
            ytName = self.ui.excelData_TW.item(row, EDTWEnum.YT.value).text()
            ytNameDict[ytName] = ytNameDict.get(ytName, []) + [row]

        rows_to_delete = []  # 创建一个列表用来存储准备删除的行号
        for ytName in ytNameList:
            rows_to_delete.extend(ytNameDict[ytName])
        rows_to_delete.sort(reverse=True)  # 倒序删除不会影响index
        for row in rows_to_delete:
            self.ui.excelData_TW.removeRow(row)
        self.afterDelete_RecalculateSameYTCountTableWidgetData()

    @pyqtSlot(bool)
    def on_deleteUnConfiguredYT_PB_clicked(self, isChecked):
        # 删除未配置月台按钮被按下
        unConfiguredYtNameList = []
        for row in range(self.ui.sameYTCount_TW.rowCount()):
            channelText = self.ui.sameYTCount_TW.item(row, SYTTWEnum.Channel.value).text()
            if channelText == "未配置":
                unConfiguredYtNameList.append(self.ui.sameYTCount_TW.item(row, SYTTWEnum.YT.value).text())
        if unConfiguredYtNameList:
            self.deleteExcelData_TW_ItemByYTName(unConfiguredYtNameList)
            InfoBar.success(title='成功', content=f"已删除未配置月台", orient=Qt.Horizontal, isClosable=True,
                            position=InfoBarPosition.TOP, duration=1000, parent=self.ui.sameYTCount_TW)


if __name__ == "__main__":  # 用于当前窗体测试

    app = QApplication(sys.argv)  # 创建GUI应用程序
    forms = EPWclass()  # 创建窗体
    __desktopPath = os.path.join(os.path.expanduser('~'), 'Desktop')
    __filePath1 = os.path.join(__desktopPath, "1127.xlsx")
    __filePath2 = os.path.join(__desktopPath, "1128.xlsx")
    # forms.addFilePathsToexcelFile_LWData([__filePath1])
    forms.addFilePathsToexcelFile_LWData([__filePath2, __filePath1])
    forms.show()

    sys.exit(app.exec_())
