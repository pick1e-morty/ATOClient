import multiprocessing
import sys
import threading
from bisect import bisect_left
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime
from multiprocessing.managers import ListProxy, ConditionProxy
from pathlib import Path

from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import (QApplication, QWidget, QTableWidgetItem)
from typing import List

from UnifyNetSDK import DHPlaySDKException
from qfluentwidgets import MessageBox

from app.download_video_widget.base_dvw import BaseDVW
from app.download_video_widget.netsdk.haikang_async_download import HaikangDownloader
from app.download_video_widget.utils.progress_bar import PercentProgressBar
from app.download_video_widget.netsdk.dahua_async_download import dahuaDownloader
from app.download_video_widget.utils.video2pic import tsPic
from app.esheet_process_widget.epw_define import ExcelFileListWidgetItemDataStruct
from app.download_video_widget.dvw_define import DownloadArg, DevLoginAndDownloadArgSturct, DVWTableWidgetEnum
from loguru import logger
from app.utils.projectPath import DVW_DOWNLOAD_FILE_SUFFIX, DVW_CONVERTED_FILE_SUFFIX, DVW_DATETIME_FORMAT, DVW_DOWNLOAD_VIDEO_PATH
from app.utils.tools import findItemTextInTableWidgetRow, AlignCenterQTableWidgetItem, removeDir


class DVWclass(BaseDVW):
    """
    本身一个主进程
    开一个接收并处理 下载子进程发送过来的数据的 线程
    开一个负责启动 下载子进程 的线程，下载子进程中开一个负责关闭下载句柄的线程

    """
    downloadStatusChange = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)  # 调用父类构造函数，创建窗体

        # formsConfigDict = parent.formsConfigDict  # dvw界面暂时没有配置
        # self.dvw_config = formsConfigDict["dvw"]  # 后期要做下载进程数量和是否在下载前进行查找操作
        self.devConfigGenerate = parent.devConfigGenerate  # 因为加载设备配置生成器需要读取一个文件，所以由父类统一初始化并激活之后再下发给子类，更重要的是主窗体那边负责exception的报错弹窗
        # TODO 可以考虑 formsConfigDict 和 devConfigGenerate 用传参的方式，因为现在两个 变量 的生成不是那么复杂了

        # 从init这里做实例变量声明根本就是个错误，很容易就把初始化给忘了

        self.classifyDownloadArgsByDevIP = {}  # 把下载参数按照ip分类，因为最终下载时是以ip为单位的
        self.downloadErrorArgs = {}  # 收集下载错误的下载参数，和classifyDownloadArgsByDevIP是相同结构的
        self.beforeDownloadErrorFlag = ["初始化失败", "登陆失败"]  # 如果子进程上报的设备状态在这个列表中就表明设备登陆失败了，就需要把整个key_ip中的downloadArgs_value都加到self.downloadErrorArgs中
        self.manager: multiprocessing.Manager = None  # 进程通信对象管理器
        self.downloadResultList: ListProxy = None  # 从manager拿的进程通信列表对象，它的方法定义在multiprocess.managers.BaseListProxy
        self.downloadResultListCondition: ConditionProxy = None  # 负责downloadResultList的进程安全同步和非空任务事件通知
        self.getDownloadResultThreadInstance = None  # getDownloadResultThread是从downloadResultList中不断拿结果并发信号的线程
        self.downloadDone: bool = None  # 一个关闭标志，用来关getDownloadResultThread的
        self.ipRowIndexIndownloadProgress_TW = {}  # 这个变量是用来存储ip所在行的索引的，用来更新进度条的
        self.startDownloadThreadInstance = None  # 负责开进程池的线程,startDownloadThread
        self.totalDownloadCount = None  # 下载总量，用来更新 下载进度 标签
        self.downloadedCount = None  # 下载成功的数量。 　只能从那个线程中进行更改。也是用来更新 下载进度 标签
        self.downloadArgsNumInFolderDict = {}  # 从文件夹的角度统计下载参数的数量，也就是每个文件夹下应有文件数量
        self.downloadStatusChange.connect(self.updateDownloadStatusUI)  # 这个信号也是getDownloadResultThread发出来的

    def classifyArg(self, eflw_ItemDataList: List[ExcelFileListWidgetItemDataStruct]):
        """
        下载时是以ip为单位的，所以这个方法就是进行一个以ip进行分类存储的操作，结果在classifyDownloadArgsByDevIP
        """
        self.classifyDownloadArgsByDevIP = {}  # 数值初始化
        self.downloadArgsNumInFolderDict = {}  # 数值初始化，从文件夹的角度统计下载参数的数量，也就是每个文件夹下应有文件数量
        for eflw_ItemData in eflw_ItemDataList:
            folderName = Path(eflw_ItemData.excelFilePath).stem
            Path(DVW_DOWNLOAD_VIDEO_PATH / folderName).mkdir(exist_ok=True)  # downloader貌似没能力创建文件夹
            self.downloadArgsNumInFolderDict[folderName] = len(eflw_ItemData.edtw_ItemDataList)  # 从文件夹的角度统计下载参数的数量，也就是每个文件夹下应有文件数量
            for edtw_ItemData in eflw_ItemData.edtw_ItemDataList:
                fileName = (str(edtw_ItemData.shipID) + DVW_DOWNLOAD_FILE_SUFFIX)  # 单号加统一的文件后缀名mp4
                filePath = str(DVW_DOWNLOAD_VIDEO_PATH / folderName / fileName)

                scanTime = datetime.strptime(str(edtw_ItemData.scanTime), DVW_DATETIME_FORMAT)  # 上层传来的时间数值是str类型的

                v_ytName = edtw_ItemData.ytName
                devConfig = self.devConfigGenerate.send(v_ytName)  # 传月台名，拿对应的设备配置数据类实例
                if devConfig is None:  # 只有能拿到配置的月台才会进行后续处理
                    continue  # 且是必须存在的，所以未配置月台的筛选过程就放到dvw这边了
                devArgStruct = isDevIpExist = self.classifyDownloadArgsByDevIP.get(devConfig.devIP, None)
                if isDevIpExist is None:  # 我存了两个变量名
                    devArgStruct = DevLoginAndDownloadArgSturct()  # 一个用来判断，一个用来指向数据结构
                    devArgStruct.devType = devConfig.devType  # 如果数据类实例不存在，就新建一个，然后指向这个数据类实例
                    devArgStruct.devIP = devConfig.devIP
                    devArgStruct.devPort = devConfig.devPort
                    devArgStruct.devUserName = devConfig.devUserName
                    devArgStruct.devPassword = devConfig.devPassword

                v_channel = devConfig.devChannel
                downloadArg = DownloadArg(savePath=filePath, downloadTime=scanTime, ytName=v_ytName, channel=v_channel)  # 月台名和通道是冗余的存储，但不这么写的话，解析和存储的复杂度
                devArgStruct.downloadArgList.append(downloadArg)  # 如果数据类实例存在，那就直接改呗
                self.classifyDownloadArgsByDevIP[devConfig.devIP] = devArgStruct  # 这里重新改一下字典的value，应该也不算什么大事，不然就得写重复代码了

    def getDownloadResultThread(self):
        """
        线程不断的读取用于子进程通信的manager().list()，读到了就发送信号，信号再连槽函数，槽函数负责更改窗体
        读不到就等（阻塞，省电doge）
        之所以不用Event是因为我进行了一个clear操作，虽然clear方法是进程安全(由manager保障)的原子操作方法(内置方法保障)，但list没有提供 复制列表的 原子操作的 方法。
        我把列表的副本拿下来，然后把锁丢掉，这样我更改窗体的耗时操作就不会影响到子进程后续对通信列表的append操作
        这样这个函数代码的逻辑操作需要确保我拿list副本的时候是进程安全的，所以用了contidion，没内容还能阻塞一下
        """

        while True:
            with self.downloadResultListCondition:  # 查和改的操作都要在锁下进行。如果某个对列表的操作不在锁下，就不能保证是进程安全的了，python随时有可能把权限交出去
                if not self.downloadResultList:
                    if self.downloadDone is True:
                        logger.info("getDownloadResultThread子线程正常关闭")
                        break
                    self.downloadResultListCondition.wait()
                result_List = self.downloadResultList[:]
                self.downloadResultList[:] = []  # ListProxy没有提供clear方法。它的方法定义在multiprocess.managers.BaseListProxy
            for resultStruct in result_List:  # 这一步是极有可能存在速度瓶颈的，应该创一个独立缓冲区来保存下载结果，然后慢慢地让窗体更新数据。毕竟生产者(进程池)有8个，而消费者(窗体更新UI)只有一个。
                self.downloadStatusChange.emit(resultStruct)  # 如果堵在这会很严重，不仅子进程下载结果发不过来，连下载进度都会被推迟。如果把阻塞都删掉呢？

    def updateDownloadStatusUI(self, resultList):
        """
        负责更新下载状态UI的槽函数。
        """
        widgetEnum, key_devIP, downloadArgList_index, downloadStatus = resultList  # 子进程那边发来一个列表内含四个元素，依次为要操作的组件枚举，设备ip，下载参数索引，上报状态
        try:  # 这样很聪明，避免了进程通信大数据的耗时传递
            devArgStruct = self.classifyDownloadArgsByDevIP.get(key_devIP)  # 按照ip拿DevLoginAndDownloadArgSturct
            downloadArg = devArgStruct.downloadArgList[downloadArgList_index]  # 在按照索引取出其他需要显示的数据
        except KeyError:
            logText = f"意外情况,子进程下载器那边传回来一个在classifyDownloadArgsByDevIP中查不到的设备ip{key_devIP},下载参数列表索引{downloadArgList_index},下载状态{downloadStatus}"
            logger.error(logText)
            return

        try:
            rowIndexIndownloadProgress_TW = self.ipRowIndexIndownloadProgress_TW[key_devIP]  # 这个变量是用来存储ip所在行的索引的，用来更新进度条的
        except KeyError:
            logText = f"意外情况,子进程下载器那边传回来一个在ipRowIndexIndownloadProgress_TW中查不到的设备ip{key_devIP},下载参数列表索引{downloadArgList_index},设备状态{downloadStatus}"
            logger.error(logText)
            return

        if widgetEnum == DVWTableWidgetEnum.DOWNLOAD_STATUS_TABLE:
            itemTextList = [key_devIP, downloadArg.channel, downloadArg.ytName]  # 把所有要显示在tableWidget组件上的文本整合到列表中，一个for就能显示上去了
            savePath = Path(downloadArg.savePath)
            relative_path = savePath.relative_to(DVW_DOWNLOAD_VIDEO_PATH.parent)  # 缩短一下路径。 TODO 这里应该是可以用PROJECT_ROOT_PATH代替的
            itemTextList.extend([relative_path, downloadArg.downloadTime, downloadStatus])
            self.ui.downloadStatus_TW.insertRow(0)  # 新来的数据都显示在新建的第一行
            for col_index, itemText in enumerate(itemTextList):
                aItem = QTableWidgetItem(str(itemText))
                aItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.ui.downloadStatus_TW.setItem(0, col_index, aItem)
            # 下面是对ipCount_TW的界面更新，更新进度条。还有下载总量统计
            if downloadStatus == "下载成功":
                progressItemWidget = self.ui.downloadProgress_TW.cellWidget(rowIndexIndownloadProgress_TW, 1)
                progressItemWidget.addOne()
                self.downloadedCount += 1
                self.ui.downloadStatus_TL.setText(f"下载进度-({self.downloadedCount}/{self.totalDownloadCount})")
            else:  # downloadStatus != "下载成功"
                self.downloadErrorArgs[key_devIP] = downloadArg  # 收集下载错误的下载参数
                __tableWidget = self.ui.downloadError_TW  # 太长了，缩短一下
                row, isRowExist = findItemTextInTableWidgetRow(self.ui.downloadError_TW, str(key_devIP))  # 查找 对应行 是否已存在
                if isRowExist:
                    errorNumItem = __tableWidget.item(row, 1)  # 行已经存在
                    errorNum = int(errorNumItem.text()) + 1
                    __tableWidget.setItem(row, 1, errorNum)  # 错误数量加1，更新错误数量列的数据
                else:
                    devIP_Item = AlignCenterQTableWidgetItem(str(key_devIP))  # 行不存在，初始化两列数据
                    __tableWidget.setItem(row, 0, devIP_Item)  # 文件夹名称
                    errorNum = 1
                    errorNum_Item = AlignCenterQTableWidgetItem(str(errorNum))
                    __tableWidget.setItem(row, 1, errorNum_Item)  # 错误数量

        elif widgetEnum == DVWTableWidgetEnum.DOWNLOAD_PROGRESS_TABLE:
            deviceStatus = downloadStatus
            if deviceStatus in self.beforeDownloadErrorFlag:  # 如果子进程上报的设备状态在这个列表中就表明设备登陆失败了，
                self.downloadErrorArgs[key_devIP] = devArgStruct  # 就需要把整个key_ip中的downloadArgs_value都加到self.downloadErrorArgs中

            # 把deviceStatus放到 downloadProgress_TW 的第三列上
            aItem = AlignCenterQTableWidgetItem(str(deviceStatus))
            self.ui.downloadProgress_TW.setItem(rowIndexIndownloadProgress_TW, 2, aItem)
        self.ui.downloadStatus_TW.resizeColumnsToContents()  # 调整列宽
        self.ui.downloadStatus_TW.updateSelectedRows()  # 刷新主题显示状态
        self.ui.downloadProgress_TW.resizeColumnsToContents()  # 调整列宽
        self.ui.downloadProgress_TW.updateSelectedRows()  # 刷新主题显示状态

    def startDownloadThread(self):
        """
        负责开启进程池的线程，最大进程数量要做参数化的(UI那边要限制最多是cpu_count个)
        """

        ipNum = len(self.classifyDownloadArgsByDevIP.keys())
        if ipNum >= 8:
            maxWorkers = 8  # 大于8个ip就开8个进程池，不然就开对应数量的就好了
        else:
            maxWorkers = ipNum

        with ProcessPoolExecutor(max_workers=maxWorkers) as executor:
            for devIP, devArgStruct in self.classifyDownloadArgsByDevIP.items():
                if devArgStruct.devType == "dahua":
                    executor.submit(dahuaDownloader, self.downloadResultList, self.downloadResultListCondition, devArgStruct)
                elif devArgStruct.devType == "haikang":
                    executor.submit(HaikangDownloader, self.downloadResultList, self.downloadResultListCondition, devArgStruct)
                else:
                    logger.error(f"未知设备类型{devArgStruct.devType}")

        with self.downloadResultListCondition:  # 如果没有一个下载结果传过去的话，就需要手动解锁一下，让子线程顺利关闭
            self.downloadResultListCondition.notify()
        self.downloadDone = True  # 开启关闭标志，getDownloadResultThreadInstance线程可以关了
        self.getDownloadResultThreadInstance.join(10)  # 没关的话再等10秒
        if self.getDownloadResultThreadInstance.is_alive():
            logger.error("getDownloadResultThread子线程关闭超时")

        self.manager.shutdown()  # 上面关完了，管理器也需要关
        logger.info("multiprocessing.Manager已关闭")

    def handleDownloadList(self, eflw_ItemDataList: List[ExcelFileListWidgetItemDataStruct]):
        # 点击开始下载按钮后的第一个执行的方法
        self.classifyArg(eflw_ItemDataList)
        self.beforeDownload(self.classifyDownloadArgsByDevIP)

    def beforeDownload(self, downloadArgs):
        # 分类之后填充几个组件     显示下载总量
        self.ui.downloadProgress_TW.clearContents()
        self.ui.downloadProgress_TW.setRowCount(0)
        self.ui.downloadStatus_TW.clearContents()
        self.ui.downloadStatus_TW.setRowCount(0)
        self.downloadErrorArgs = {}  # 收集下载错误的下载参数，和classifyDownloadArgsByDevIP是相同结构的
        self.downloadedCount = 0  # 下载成功的数量，初始化
        self.totalDownloadCount = 0  # 所有ip加一块的下载总量
        self.ipRowIndexIndownloadProgress_TW = {}  # 这个变量是用来存储ip所在行的索引的，用来更新进度条的
        self.ui.downloadProgress_TW.setRowCount(len(downloadArgs.keys()))
        row = 0
        for devIP, devArgStruct in downloadArgs.items():  # 设置ui，下载进度表格中插入进度条组件
            inIp_count = len(devArgStruct.downloadArgList)  # 每个ip单独的下载数量
            self.totalDownloadCount += inIp_count
            aItem = AlignCenterQTableWidgetItem(str(devIP))  # 1整个下载流程中有很多变量可以进行且需要多次统一初始化处理
            self.ui.downloadProgress_TW.setItem(row, 0, aItem)  # 2可以把它们放到一个方法中
            self.ipRowIndexIndownloadProgress_TW[devIP] = row  # 3这个UI的初始化处理也不应该放在这里，最好也放到一个方法里
            aItemWidget = PercentProgressBar()  # 设置第二列单元格为 带百分比的进度条
            aItemWidget.setMaximum(inIp_count)
            self.ui.downloadProgress_TW.setCellWidget(row, 1, aItemWidget)
            row += 1  # 换行
        self.ui.downloadStatus_TL.setText(f"下载状态-(0/{self.totalDownloadCount})")  # 设置ui，更新下载状态标签文本

        for folderName, fileNum in self.downloadArgsNumInFolderDict.items():  # 设置ui，填充 文件数量表格 中的 预下载数量列 中的数据
            row, isRowExist = findItemTextInTableWidgetRow(self.ui.fileCount_TW, folderName)  # 查找 对应行 是否已存在
            if not isRowExist:
                folderNameItem = AlignCenterQTableWidgetItem(str(folderName))  # 文件夹名称
                self.ui.fileCount_TW.setItem(row, 0, folderNameItem)
            fileNumItem = AlignCenterQTableWidgetItem(str(fileNum))  # 文件数量
            self.ui.fileCount_TW.setItem(row, 1, fileNumItem)

        """
        开个进程通信的list和确保list进程安全的condition。
        开一个不断从上面那个list中拿结果得线程
        再开一个启动下载的进程池的线程
        """
        self.manager = multiprocessing.Manager()
        self.downloadResultList = self.manager.list()
        self.downloadResultListCondition = self.manager.Condition()
        self.downloadDone = False  # 初始化线程关闭标志
        self.getDownloadResultThreadInstance = threading.Thread(target=self.getDownloadResultThread)  #
        self.getDownloadResultThreadInstance.start()
        self.startDownloadThreadInstance = threading.Thread(target=self.startDownloadThread)  #
        self.startDownloadThreadInstance.start()

    @pyqtSlot()
    def on_reDownload_PB_clicked(self):
        # 重新下载按钮被按下
        self.beforeDownload(self.downloadErrorArgs)

    @pyqtSlot()
    def on_convert_PB_clicked(self):
        # MP4转JPG按钮被按下
        # 遍历整个pic文件夹及其所有子文件夹中的mp4文件，全部转换为jpg文件
        fileList = [pathObject for pathObject in Path(DVW_DOWNLOAD_VIDEO_PATH).rglob("*") if pathObject.is_file()]
        mp4FileList = [pathObject for pathObject in fileList if pathObject.suffix == DVW_DOWNLOAD_FILE_SUFFIX]
        for filePath in mp4FileList:
            try:
                tsPic(filePath)
            except DHPlaySDKException as e:
                logger.error(f"{filePath}转换失败，错误代码{str(e)}")

    @pyqtSlot()
    def on_deleteAllFile_PB_clicked(self):
        # 删除所有文件按钮被按下
        # 删除指定目录下的所有文件和子目录，但保留目录本身
        errorMsgBox = MessageBox('确认', "是否要清空pic文件夹中的所有子级文件夹和文件？", self)
        errorMsgBox.yesSignal.connect(lambda: removeDir(DVW_DOWNLOAD_VIDEO_PATH))
        errorMsgBox.raise_()
        errorMsgBox.yesButton.setText('确定')
        errorMsgBox.cancelButton.setText('取消')
        errorMsgBox.exec()


if __name__ == "__main__":  # 用于当前窗体测试
    # 这边真想单独测试的话需要填充下载数据，还是有设备配置生成器的初始化和激活。
    # 那个窗体的ini给个空值就行
    app = QApplication(sys.argv)
    forms = DVWclass()
    forms.show()
    sys.exit(app.exec_())
