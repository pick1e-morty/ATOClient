import sys
from concurrent.futures.process import ProcessPoolExecutor
from concurrent.futures.thread import ThreadPoolExecutor

from PyQt5.QtWidgets import QApplication, QWidget, QTableWidgetItem, QRadioButton
from PyQt5.QtCore import Qt, pyqtSlot

from app.QMyVDPw.Libs.DaHua_cmd import MyDaHuaNetClient
# from atowidgets.QMyVDPw.custom.DownLoadVideo import DahuaClientFun
from app.QMyVDPw.Libs.testData import EPW_EDTWD
from app.QMyVDPw.Libs.DataHandling import shipHandleTWInitDataHandle, getSameIPNumList, ProcessDataForDownload
from app.QMyVDPw.Libs.QMyVDPwEnum import SHTWEnum
from multiprocessing import Process, cpu_count


# 我这次用了表格项目索引枚举

# 视频下载时长的代理组件
# 对应IP的获取   它是一个item 所以展示个用户的只是一个text  例：10.123.15.240-21 而这个item的Data则是 ip-通道-账号-密码
# 月台配置表的读取可以做一个md5判断 这样读起来就不那么费劲了
# 把接收到的月台对应IP通道 做个单独的debug日志记录吧
# 最后传给下载视频类的时候要做月台排序 那就又需要用到数据处理lib了
# 在对月台检测的时候 要判断text和上一次一样的话 就不搜索  直接setdata了   这个逻辑现在有点问题 记得修一下


# 日后要对下载时长做一个整除时间处理 现在的下载时长处理还是有DaHua那边的模块做的时间加减操作
# 也就是这边的参数根本没有对接。对于非偶数下载时长就头部多一秒-2/下载时间/+3这样
# 自动阈值的处理是默认40 如果某一IP的单号数量达到了40就多分一个进程 如果多个IP的单号数量也达到了40就先全部+1 有剩余的在加一遍
# 上面的IP数量最多，也就优先加一下
# datahandling里的 对固定时差的处理还没有做

# TODO 打包大华widget，widget独立 然后通过fire传参
# TODO 另一个分支是直接调用cmd的那个 那样信息根本没法看但起码在被pyinstaller打包后能下载视频

class QmyVideoDownloadProcess(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)  # 调用父类构造函数，创建窗体
        self.ui = Ui_VDPWC()  # 创建UI对象
        self.ui.setupUi(self)  # 构造UI界面
        self.on_singleProcessRB_toggled()

    @pyqtSlot()
    def on_singleProcessRB_toggled(self):
        # 单进程单选按钮触发信号
        # 隐藏按钮
        state = self.ui.singleProcessRB.isChecked()  # 布局的setEnable是无效的
        childrens = self.ui.processQuantityConfigurationGB.findChildren(QWidget)  # 查找进程数量配置组里的所有子Widget组件
        if state:  # 判断单选按钮是否被选中
            for child in childrens:  # 我的单选按钮没有继承 所以用的简单的type
                if type(child) != QRadioButton:  # 遍历这个Widget组件列表 如果ch不是单选按钮就隐藏掉
                    child.setVisible(False)

        # 隐藏coreNumTW表格中的单个IP可用进程数量列
        self.ui.coreNumTW.setColumnCount(2)

    @pyqtSlot()
    def on_manualAssignmentRB_toggled(self):
        # 手动分配单选按钮触发信号
        # 按钮是否可见
        state = self.ui.manualAssignmentRB.isChecked()  # 布局的setEnable是无效的
        pQCGBchildrens = self.ui.processQuantityConfigurationGB.findChildren(QWidget)  # 查找进程数量配置组里的所有子Widget组件
        jTHLWidgetList = []
        for widgetIndex in range(self.ui.judgmentThresholdHL.count()):  # 取布局组件索引
            jTHLWidgetList.append(
                self.ui.judgmentThresholdHL.itemAt(widgetIndex).widget())  # 通过布局索引获取相应的widget并添加到jTHLWidgetList布局组件列表中
        if state:  # 设置组件框中所有组件可见 但除了 judgmentThresholdHL 这个布局下的Widget
            for child in pQCGBchildrens:  # 遍历组件框中所有组件
                if child not in jTHLWidgetList:  # 如果这个组件不在jTHLWidgetList布局下则指定可见
                    child.setVisible(True)
                else:  # 在的话就隐藏掉
                    child.setVisible(False)
        self.radioButtonChangedReIniWidget()

    @pyqtSlot()
    def on_automaticThresholdRB_toggled(self):
        # 自动阈值单选按钮触发信号
        state = self.ui.automaticThresholdRB.isChecked()
        childrens = self.ui.processQuantityConfigurationGB.findChildren(QWidget)  # 查找进程数量配置组里的所有子Widget组件
        if state:  # 将组件组中的所有Widget设置可见
            for child in childrens:
                child.setVisible(True)

        self.radioButtonChangedReIniWidget()

    def radioButtonChangedReIniWidget(self):
        # 单选按钮状态切换重置组件
        self.iniCoreNumLE()  # 重新初始化核心数量编辑框
        self.ui.minimumQuantityThresholdLE.setText("40")  # 重新初始化自动阈值的最小单号数量行编辑框
        self.reIniCoreNumTWSetCoreNumTWThirdColumn2Zero()  #

    def reIniCoreNumTWSetCoreNumTWThirdColumn2Zero(self):
        # 因为单选按钮被点击 所以初始化coreNumTW的第三列数据为0
        self.ui.coreNumTW.setColumnCount(3)
        self.ui.coreNumTW.setHorizontalHeaderItem(2, QTableWidgetItem("单台录像机可用进程数量"))
        rows = self.ui.coreNumTW.rowCount()  # 直接用内置方法开出第三列 然后设置表头
        for rowIndex in range(rows):  # 取行数后遍历每一行 并设置第三列数据为字符串0
            self.ui.coreNumTW.setItem(rowIndex, 2, QTableWidgetItem("0"))
        self.ui.coreNumTW.resizeColumnsToContents()  # 根据内容长度重置单元格宽度尺寸

    def iniWidget(self, EPW_ExcelDataTW_Data):
        # 就像方法名 这个地方的级别是组件 同组件都要在下级里解决
        print(EPW_ExcelDataTW_Data)
        self.iniShipHandleTW(EPW_ExcelDataTW_Data)
        self.iniCoreNUmTW()
        self.iniCoreNumLE()

    @pyqtSlot()
    def on_downLoadVideoPB_clicked(self):
        sHTWV = self.getShipHandleTWValue()
        dataForDownLoad = ProcessDataForDownload(sHTWV)
        print(dataForDownLoad)
        self.threadPoolDownload(dataForDownLoad)

    def threadPoolDownload(self, downloadParameters):
        # 多线程下载 现在已废弃，因为netsdk的init是类函数这将会影响整个进程 按照我现在的写法也就是一个进程中 netsdk初始化了四边
        # 当然 把接口提供出来 让用户调用一次就行了 不过我选择多进程，刚好可能会提点速度吧
        with ThreadPoolExecutor(8) as executor:
            for IpText, deviceConfig, downLoadParmeterList in downloadParameters:
                # print(IpText)
                # print(deviceConfig)
                # print(downLoadParmeterList)
                executor.submit(self.createDaHuaNetClientFunc, deviceConfig, downLoadParmeterList)

    def processPoolDownload(self, downloadParameters):
        with ProcessPoolExecutor() as p:
            pass

    @staticmethod
    def createDaHuaNetClientFunc(deviceConfig, downLoadParmeterList):
        MyDaHuaNetClient(deviceConfig, downLoadParmeterList)

    def getShipHandleTWValue(self):
        # 遍历整个tableWidget 然后存成List
        tableWidgetRow = self.ui.shipHandleTW.rowCount()
        tableWidgetColumn = self.ui.shipHandleTW.columnCount()
        excelDataTWValueList = [[] for _ in range(tableWidgetRow)]
        # 创建一个空的二维列表 然后用坐标的方式进行填充
        for row in range(tableWidgetRow):
            for column in range(tableWidgetColumn):
                itemData = self.ui.shipHandleTW.item(row, column)
                if itemData:
                    excelDataTWValueList[row].append(itemData.text())
            HCVRIP_Data = self.ui.shipHandleTW.item(row, SHTWEnum.HCVRIP.value)  # 这个获取使用的append没有根据枚举索引
            excelDataTWValueList[row].append(HCVRIP_Data.data(Qt.UserRole))  # 索引行的末尾我手动添加了藏在第一列文本下的数据
        print("从ExcelDataTW中获取到以下数据列表：" + str(excelDataTWValueList))
        return excelDataTWValueList

    def iniCoreNumLE(self):
        # 初始化核心数量总数 编辑框
        cpuCount = cpu_count()
        self.ui.coreNumLE.setText(str(cpuCount))

    def iniShipHandleTW(self, EPW_ExcelDataTW_Data):
        # 初始化shiphandle表格组件
        # 其实应该按照列的方式 也就是枚举的索引值严格独立循环赋值 但做起来好像有点困难
        # 还是拿性能当借口吧 但真要那么做 那枚举才是真正的一键控制 性能性能性能
        defaultDownloadTimeText = self.ui.defaultDownloadDurationCB.currentText()  # 获取当前默认下载时间组合框的文本
        tableData = shipHandleTWInitDataHandle(EPW_ExcelDataTW_Data, defaultDownloadTimeText)  # 进行数据自定义
        if tableData:
            self.setDataToshipHandleTW(tableData)  # 自定义组件填充方法

    def iniCoreNUmTW(self):
        # 初始化核心数量配置表格
        tableData = self.getShipHandleTWValue()
        sameIPNumCount = getSameIPNumList(tableData)
        self.setDataToCoreNumTW(sameIPNumCount)
        # self.reIniCoreNumTWSetThirdColumn2Zero()    # 默认被选中的是单进程按钮 所以不用做这个第三列的数据初始化

    def setDataToCoreNumTW(self, ListData):
        # 设置数据到shipHandleTW表格组件中
        self.ui.coreNumTW.clearContents()  # 还是清理一下好
        print("初始化coreNumTW组件的数据为：" + str(ListData))
        self.ui.coreNumTW.setRowCount(len(ListData))
        for oneDimensionalIndex, oneDimensionalDataList in enumerate(ListData):  # 用enumrate的方法同时获取坐标和数据
            for twoDimensionalIndex, twoDimensionalDataList in enumerate(oneDimensionalDataList):
                aItem = QTableWidgetItem(str(twoDimensionalDataList))
                aItem.setFlags(Qt.NoItemFlags)
                aItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)  # 设置项目垂直水平对齐
                self.ui.coreNumTW.setItem(oneDimensionalIndex, twoDimensionalIndex, aItem)
        self.ui.coreNumTW.resizeColumnsToContents()  # 调整列宽

    def setDataToshipHandleTW(self, ListData):
        # 设置数据到shipHandleTW表格组件中
        self.ui.shipHandleTW.clearContents()  # 还是清理一下好
        print("初始化shipHandleTw组件的数据为：" + str(ListData))
        self.ui.shipHandleTW.setRowCount(len(ListData))
        for oneDimensionalIndex, oneDimensionalDataList in enumerate(ListData):  # 用enumrate的方法同时获取坐标和数据
            for twoDimensionalIndex, twoDimensionalDataList in enumerate(oneDimensionalDataList):
                if twoDimensionalIndex == SHTWEnum._HCVRConfig.value and type(twoDimensionalDataList) == list:
                    itemText = oneDimensionalDataList[SHTWEnum.HCVRIP.value]
                    itemData = twoDimensionalDataList
                    aItem = QTableWidgetItem(str(itemText))
                    aItem.setData(Qt.UserRole, itemData)
                    aItem.setTextAlignment((Qt.AlignHCenter | Qt.AlignVCenter))
                    self.ui.shipHandleTW.setItem(oneDimensionalIndex, SHTWEnum.HCVRIP.value, aItem)
                else:
                    aItem = QTableWidgetItem(str(twoDimensionalDataList))
                    aItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)  # 设置项目垂直水平对齐
                    self.ui.shipHandleTW.setItem(oneDimensionalIndex, twoDimensionalIndex, aItem)

        self.ui.shipHandleTW.resizeColumnsToContents()  # 调整列宽


if __name__ == "__main__":  # 用于当前窗体测试
    from ui_VideoDownloadProcess import Ui_VDPWC

    app = QApplication(sys.argv)  # 创建GUI应用程序
    form = QmyVideoDownloadProcess()  # 创建窗体
    form.iniWidget(EPW_EDTWD)  # 测试数据
    form.show()
    sys.exit(app.exec_())
else:
    from app.QMyVDPw.ui_VideoDownloadProcess import Ui_VDPWC
