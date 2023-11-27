import sys

from PyQt5.QtCore import QDir, pyqtSlot, Qt
from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog, QListWidgetItem, QTableWidgetItem
from app.QMyALw.Libs.DataHandling import getAllFilesUnderThePath, getFileNameInFilePath, \
    YTcontrastTWDataHandle, getPrimaryPathInPathList, listContentDeDuplication, YTContrastDataSortingProcessing, \
    getLabeTxtInMainFolder, upperOrderTop, JudgeWhetherTheConditionsAreMet
from app.QMyALw.Libs.VideoConvert import oneSecondVideoToOnePicture, videoSecondsPictures
from app.QMyALw.Libs.filterCoordinates import filterAndDrawPackageCoordinates
from app.QMyALw.Libs.getCoordinates import getPackageCoordinates
from app.QMyALw.Libs.QMyALwEnum import YTcontrastTWEnum


# TODO 用ps定位一下12个月台的线体和称台像素范围 中点和中心 矩形和四边形还有多边形
# TODO 取单号坐标的文本位置
# TODO 现在图片的坐标依然在dictoryLW里存着 哦 那单号坐标也从那取 可是那样就会调用两边取和操作了
# TODO 不对 降低耦合 YTcontractTW 的itemdata必须是路径          # emmmm  这个思路那就直接新开了个函数 代价更高了 可是逻辑更清晰了
# TODO 我们一体化数据 对函数友好一点
# TODO 如果两个下载进程 同时创建一个文件夹 那另一个会卡住，然后就不下载了 创建失败的异常抓获一个下 pass掉

# TODO 以后再写tableWidget记得 text是一维列表，data是另一维列表 两个列表的数据位置要相对应
# TODO 好多注释没打 ，然后 多余的函数记得清除掉 有的方法是可以合并的
class QmyAutoLabel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)  # 调用父类构造函数，创建窗体
        self.ui = Ui_ALWC()  # 创建UI对象
        self.ui.setupUi(self)  # 构造UI界面

    @pyqtSlot()
    def on_startFilteringPB_clicked(self):
        # 开始过滤按钮被点击
        # 从YTcontrastTW中取出表格数据 然后判断那些行是完全满足过滤条件的
        tableDataList1 = self.getDataInYTcontrastTW()
        tableDataList3 = JudgeWhetherTheConditionsAreMet(tableDataList1)
        if len(tableDataList3):  # 如果不为空 开始过滤
            filterAndDrawPackageCoordinates(tableDataList3)
        print(tableDataList3)

    @pyqtSlot()
    def on_getPackageCoordinatesPB_clicked(self):
        # 获取包裹坐标按钮被点击
        # 这边从组件上取下来需要的数值 然后就都交给DataHandling模块了
        if self.ui.jpegRB.isChecked():
            confidence = self.ui.confidenceDSB.value()
            IOU = self.ui.IOUDSB.value()
            NMS = self.ui.NMSCHB.isChecked()
            saveResult = self.ui.saveResultCHB.isChecked()
            viewResult = self.ui.viewResultCHB.isChecked()

            folderList = self.getItemData2FolderListInDirectoryLW()
            getPackageCoordinates(confidence, IOU, NMS, saveResult, viewResult, folderList)
        print("结束 跳出")

    def getItemData2FolderListInDirectoryLW(self):
        path_list = self.getItemDataInDirectoryLW()
        # 需要先得到不同的文件夹列表
        if path_list:
            folderList = []
            for filePath in path_list:
                # 例：C:\Users\admin\Documents\ATO\videoprocess\1.12\432307690088072.jpeg
                pathList = filePath.split("/")[:-1]  # 上层函数将保证路径分隔符是 /
                folderPath = "/".join(pathList)
                folderList.append(folderPath)
            folderPathList = list(set(folderList))
            return folderPathList

    @pyqtSlot()
    def on_fullCoreConversionPB_clicked(self):
        # 满核转换按钮被点击
        if self.ui.davRB.isChecked():
            state = self.ui.videoDurationCB.currentIndex()
            pathList = self.getItemDataInDirectoryLW()
            # 两种状态 一个直接转 另一个还要检测时长做正则匹配duration字段
            # 然后他们需要文件路径
            if len(pathList):  # 如果列表不为空
                if state == 0:  # 一秒视频转一张图片
                    oneSecondVideoToOnePicture(pathList)
                elif state == 1:  # 于时长相对秒数图片
                    videoSecondsPictures(pathList)

    @pyqtSlot()
    def on_jpegRB_clicked(self):  # 这两个单选框 在两者切换时直接把数据给清除掉了
        self.clearDirectoryLW_clearYTcontrastTWshipExistColumn()

    @pyqtSlot()
    def on_davRB_clicked(self):  # 这两个单选框 在两者切换时直接把数据给清除掉了
        self.clearDirectoryLW_clearYTcontrastTWshipExistColumn()

    def clearDirectoryLW_clearYTcontrastTWshipExistColumn(self):
        # 清除列表组件和月台对照表的实存单号列第二列
        self.ui.directoryLW.clear()  # 清数据
        tableData = self.getDataInYTcontrastTW()  # 取数据
        if len(tableData):
            for index in range(len(tableData)):  # 改数据
                tableData[index][YTcontrastTWEnum.shipExist.value] = ""
            self.setDataToYTcontrastTW(tableData)  # 放数据

    def iniWidget(self, EPW_ExcelDataTW_Data):
        # 初始化一些组件 # 从EPW获取数据 然后这边处理一下 得到单号和月台 之后放入线体范围
        YTContrastTableData = YTcontrastTWDataHandle(EPW_ExcelDataTW_Data)
        if self.ui.jpegRB.isChecked():
            # 如果图片单选按钮被选中 获取文件夹表格上的文件路径 处理出来文件夹路径 然后拼接projectName 如果是一个文件夹就
            # 把里面的txt取出来 这又是一个大列表 表格上的数据都到齐后(记得EPW) 然后再进入一个函数 先对三列数据进行sort
            # 然后开始for的三列列表append append玩之后如果有优化的话就是pop 可是弹不得 正序循环下会影响迭代
            # 另一种可优化方法是 从文件夹中取出图片文件时 把jpeg同级的exp下的labels的txt给取出来
            # 这样就是小列表对小列表 那按照这个思路EPW那边也可以这样做 单号按照文件夹进行分别列表存储
            # [103,103.jpeg][103,103.txt][103,12,231,123]
            txtPathList = []
            jpegFilePathList = self.getItemDataInDirectoryLW()
            if jpegFilePathList:
                folderPathList = self.getItemData2FolderListInDirectoryLW()
                if folderPathList:
                    for folderPath in folderPathList:
                        txtPathList = txtPathList + getLabeTxtInMainFolder(folderPath)
                    tableData = YTContrastDataSortingProcessing(YTContrastTableData, jpegFilePathList, txtPathList)
                    self.setDataToYTcontrastTW(tableData)
                    QApplication.processEvents()

        tableDataList1 = self.getDataInYTcontrastTW()
        # 传给函数给排个循序 并给出有多少行满足条件
        tableDataList2 = upperOrderTop(tableDataList1)
        self.setDataToYTcontrastTW(tableDataList2)  # 你这么写要挨打的
        tableDataList3 = JudgeWhetherTheConditionsAreMet(tableDataList2)
        self.ui.meetTheFilteringConditionsLE.setText(str(len(tableDataList3)))

        # if tableData: # 都处理玩在放置
        #     self.setDataToYTcontrastTW(tableData)

        # VDP是一个函数全部处理完 在设置的 可是实存单号的匹配  放在选择文件夹之后

    def getDataInYTcontrastTW(self):
        # 获取月台对照表上的数据 值得注意的是 如果单元格内容为None或者一切空白不过if的 都会设置为“”(空) 终于能所见即所得
        # 定义这个返回的
        tableWidgetRow = self.ui.YTcontrastTW.rowCount()  # 按照set的说法 二维列表全匹
        tableWidgetColumn = self.ui.YTcontrastTW.columnCount()
        excelDataTWValueList = [[0 for _ in range(len(YTcontrastTWEnum))] for _ in
                                range(tableWidgetRow)]  # 提前推出来相对行数的列表数量
        for row in range(tableWidgetRow):
            for column in range(tableWidgetColumn):
                itemData = self.ui.YTcontrastTW.item(row, column)  # 二维遍历 取单元格项目
                if itemData:  # 不为空则将text记下 这个应该用不到隐藏Data
                    if column == YTcontrastTWEnum.shipExist.value:  # 这里的两个if支队指定列进行data判断
                        excelDataTWValueList[row][column] = itemData.text()
                        excelDataTWValueList[row][YTcontrastTWEnum._shipFilePath.value] = itemData.data(Qt.UserRole)
                    elif column == YTcontrastTWEnum.shipCoordinateName.value:
                        excelDataTWValueList[row][column] = itemData.text()
                        excelDataTWValueList[row][YTcontrastTWEnum._shipCoordinatePath.value] = itemData.data(
                            Qt.UserRole)
                    else:
                        excelDataTWValueList[row][column] = itemData.text()  # 这个获取使用的append没有根据枚举索引
                # else:  # 为空就相应位置为空
                #     excelDataTWValueList[row].append("")
        return excelDataTWValueList

    def setDataToYTcontrastTW(self, ListData):
        # 设置数据到YTcontrastTW表格组件中  二维列表全匹
        self.ui.YTcontrastTW.clearContents()  # 还是清理一下好
        self.SetTheNumberOfTableRowsAndMaintainTheMaximumNumberOfRows(len(ListData))
        for oneDimensionalIndex, oneDimensionalDataList in enumerate(ListData):  # 用enumrate的方法同时获取坐标和数据
            for twoDimensionalIndex, twoDimensionalDataList in enumerate(oneDimensionalDataList):
                if twoDimensionalIndex == YTcontrastTWEnum._shipFilePath.value:
                    ItemText = oneDimensionalDataList[YTcontrastTWEnum.shipExist.value]
                    ItemData = twoDimensionalDataList
                    aItem = QTableWidgetItem(str(ItemText))
                    aItem.setData(Qt.UserRole, ItemData)
                    aItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                    self.ui.YTcontrastTW.setItem(oneDimensionalIndex, YTcontrastTWEnum.shipExist.value, aItem)
                elif twoDimensionalIndex == YTcontrastTWEnum._shipCoordinatePath.value:
                    ItemText = oneDimensionalDataList[YTcontrastTWEnum.shipCoordinateName.value]
                    ItemData = twoDimensionalDataList
                    aItem = QTableWidgetItem(str(ItemText))
                    aItem.setData(Qt.UserRole, ItemData)
                    aItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                    self.ui.YTcontrastTW.setItem(oneDimensionalIndex, YTcontrastTWEnum.shipCoordinateName.value, aItem)
                else:
                    aItem = QTableWidgetItem(str(twoDimensionalDataList))
                    aItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)  # 设置项目垂直水平对齐
                    self.ui.YTcontrastTW.setItem(oneDimensionalIndex, twoDimensionalIndex, aItem)
        self.ui.YTcontrastTW.resizeColumnsToContents()  # 调整列宽

    def SetTheNumberOfTableRowsAndMaintainTheMaximumNumberOfRows(self, rowCount):
        # 设置月台列数 并保持最大列数 先取当前表格列数 对照表最大列数表 如果不大于参数就设置列数为参数
        currentRowCount = self.ui.YTcontrastTW.rowCount()
        if currentRowCount < rowCount:
            self.ui.YTcontrastTW.setRowCount(rowCount)

    @pyqtSlot()
    def on_getExistingDirectoryPB_clicked(self):
        # 获取文件夹按钮被点击
        cur_dir = QDir.currentPath()  # 获取当前文件夹路径 最终锁定在ato下的videoprocess中
        dir_path = QFileDialog.getExistingDirectory(self, '选择文件夹', cur_dir)
        if dir_path:  # 开启对话框，如果不为空
            self.getFileName_setFileName2DirectoryLW(dir_path)

    def getFileName_setFileName2DirectoryLW(self, dir_path):
        # 获取文件名然后显示在directoryListWidget上
        extension = None
        if self.ui.davRB.isChecked():  # 两者最大的区别就是dav不用将数据写入YTcontrastTW中
            extension = ".dav"
        elif self.ui.jpegRB.isChecked():
            extension = ".jpeg"
        result = self.getFilePathsAndPathRemoveDuplication(dir_path, extension)
        if result:
            self.setFileNameDataToDirectoryLW(result)  # 取列表组件中绝对文件路径 设置到月台对照表中
        else:
            print("出错了")

    def getFilePathsAndPathRemoveDuplication(self, dirPath, extension):
        # 获取文件路径和路径去重 一参是要获取文件的路径，二参是文件扩展名过滤
        includeSubfolders = self.ui.includeSubfoldersCHB.isChecked()  # 是否获取dirPath下的子级文件夹
        fileAddressList = getAllFilesUnderThePath(dirPath, includeSubfolders, extension)
        if fileAddressList:
            currentDirectoryTWItemData = self.getItemTextDataInDirectoryLW()  # 获取组件上的文本然后传给去重函数
            listAfterDeDuplication = listContentDeDuplication(currentDirectoryTWItemData, fileAddressList)
            fileAddressDataList = getPrimaryPathInPathList(listAfterDeDuplication, dirPath)  # 获取指定的路径格式
            return fileAddressDataList
        else:
            return 0  # 一次只能选择一个 所以是不会有重复的

    def getItemDataInDirectoryLW(self):
        # 只获取项目的data也就是绝对文件路径列表 不这样的话 其它方法调用起来还要处理一下才能用 麻烦
        currentRowCount = self.ui.directoryLW.count()
        if currentRowCount:
            listData = []
            for row in range(currentRowCount):  # 遍历收集返回
                listData.append(self.ui.directoryLW.item(row).data(Qt.UserRole))
            return listData

    def getItemTextDataInDirectoryLW(self):
        # 便利列表组件所有行 获取项目上的文本 还有下面的数据 取消self.filePathList的策略，所有的文件路径全部都从LW这边取出
        # 因为算法的特殊性 这边需要一个二维列表 0位元素是itemText 1位元素是文件绝对路径
        currentRowCount = self.ui.directoryLW.count()
        listData = [[] for _ in range(currentRowCount)]
        for row in range(currentRowCount):  # 遍历收集返回 但二维
            listData[row].append(self.ui.directoryLW.item(row).text())
            listData[row].append(self.ui.directoryLW.item(row).data(Qt.UserRole))
        return listData

    def setFileName2YTcontrastTW(self, filePathList):
        # 设置文件名称到月台对照表格的指定列
        self.SetTheNumberOfTableRowsAndMaintainTheMaximumNumberOfRows(len(filePathList))
        for row, filePath in enumerate(filePathList):
            fileName = getFileNameInFilePath(filePath)  # 从文件路径中获取文件名称带扩展名
            aItem = QTableWidgetItem()
            aItem.setText(fileName)  # 设置项目名
            aItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)  # 设置项目垂直水平对齐
            self.ui.YTcontrastTW.setItem(row, YTcontrastTWEnum.shipExist.value, aItem)  # 在指定单号存在枚举列中添加项目
        self.ui.YTcontrastTW.resizeColumnsToContents()

    def setFileNameDataToDirectoryLW(self, DataList):
        # 设置DirectoryLW的text和data
        self.ui.directoryLW.clear()
        # 设置文件名到文件夹列表上 索引0做item的text，索引1做item的隐藏data
        for fileName, filePath in DataList:
            aItem = QListWidgetItem()  # 设置初始化项目
            aItem.setText(fileName)  # 设置项目名
            aItem.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)  # 水平左对齐，垂直中心对齐
            aItem.setData(Qt.UserRole, filePath)  # 设置项目数据
            self.ui.directoryLW.addItem(aItem)  # 向组件中添加项目


if __name__ == "__main__":  # 用于当前窗体测试
    from ui_AutoLabel import Ui_ALWC

    app = QApplication(sys.argv)  # 创建GUI应用程序
    form = QmyAutoLabel()  # 创建窗体
    form.show()
    sys.exit(app.exec_())
else:
    from app.QMyALw.ui_AutoLabel import Ui_ALWC
