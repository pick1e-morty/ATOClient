import multiprocessing
import sys
import threading
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime
from multiprocessing.managers import ListProxy, ConditionProxy
from pathlib import Path

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (QApplication, QWidget, QTableWidgetItem)
from typing import List

from app.download_video_widget.UI.ui_DownloadVideo import Ui_DVW_Widget
from app.download_video_widget.netsdk.haikang_async_download import haikangDownloader
from app.download_video_widget.utils.progress_bar import PercentProgressBar
from app.download_video_widget.netsdk.dahua_async_download import dahuaDownloader
from app.esheet_process_widget.epw_define import ExcelFileListWidgetItemDataStruct
from app.download_video_widget.dvw_define import DownloadArg, DevLoginAndDownloadArgSturct, DVWTableWidgetEnum
from loguru import logger

# 这三个全局变量是非常重要的且极有可能变化的，我放到这里显眼一点
_downloadFileSuffix = ".mp4"
# 这个pyinstaller在6.0大版本后居然把onedir做成了一个_internal，然后将exe启动文件放到根目录的上层里去了
_downloadRootPath = Path(__file__).parent.parent.parent.parent / "pic"  # 所有我这边需要再协调一下
_downloadRootPath.mkdir(exist_ok=True)
_unifyTimeFormat = "%Y-%m-%d %H:%M:%S"


class DVWclass(QWidget):
    downloadStatusChange = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)  # 调用父类构造函数，创建窗体
        self.ui = Ui_DVW_Widget()  # 创建UI对象
        self.ui.setupUi(self)  # 构造UI界面

        # formsConfigDict = parent.formsConfigDict  # dvw界面暂时没有配置
        # self.dvw_config = formsConfigDict["dvw"]  # 后期要做下载进程数量和是否在下载前进行查找操作
        self.devConfigGenerate = parent.devConfigGenerate  # 因为加载设备配置生成器需要读取一个文件，所以由父类统一初始化并激活之后再下发给子类，更重要的是主窗体那边负责exception的报错弹窗

        self.classifyDownloadArgsByDevIP = None  # 把下载参数按照ip分类，因为最终下载时是以ip为单位的
        self.manager: multiprocessing.Manager = None  # 进程通信对象管理器
        self.downloadResultList: ListProxy = None  # 从manager拿的进程通信列表对象，它的方法定义在multiprocess.managers.BaseListProxy
        self.downloadResultListCondition: ConditionProxy = None  # 负责downloadResultList的进程安全同步和非空任务事件通知
        self.getDownloadResultThreadInstance = None  # getDownloadResultThread是从downloadResultList中不断拿结果并发信号的线程
        self.downloadDone: bool = None  # 一个关闭标志，用来关getDownloadResultThread的
        self.downloadStatusChange.connect(self.updateDownloadStatusUI)  # 这个信号也是getDownloadResultThread发出来的
        self.ipRowIndexIndownloadProgress_TW = {}  # 这个变量是用来存储ip所在行的索引的，用来更新进度条的

        self.startDownloadThreadInstance = None  # 负责开进程池的线程,startDownloadThread

    def classifyArg(self, eflw_ItemDataList: List[ExcelFileListWidgetItemDataStruct]):
        """
        下载时是以ip为单位的，所以这个方法就是进行一个以ip进行分类存储的操作，结果在classifyDownloadArgsByDevIP
        """
        self.classifyDownloadArgsByDevIP = {}
        for eflw_ItemData in eflw_ItemDataList:
            folderName = Path(eflw_ItemData.excelFilePath).stem
            Path(_downloadRootPath / folderName).mkdir(exist_ok=True)  # downloader貌似没能力创建文件夹

            for edtw_ItemData in eflw_ItemData.edtw_ItemDataList:
                fileName = (str(edtw_ItemData.shipID) + _downloadFileSuffix)  # 单号加统一的文件后缀名mp4
                filePath = str(_downloadRootPath / folderName / fileName)

                scanTime = datetime.strptime(str(edtw_ItemData.scanTime), _unifyTimeFormat)  # 上层传来的时间数值是str类型的

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
        widgetEnum, key_devIP, downloadArgList_index, downloadStatus = resultList  # 子进程那边发来一个列表内含四个元素，依次为要操作的组件枚举，设备ip，下载参数索引，下载状态
        if widgetEnum == DVWTableWidgetEnum.DOWNLOAD_STATUS_TABLE:
            itemTextList = [key_devIP]  # 把所有要显示在tableWidget组件上的文本整合到列表中，一个for就能显示上去了
            try:
                devArgStruct = self.classifyDownloadArgsByDevIP.get(key_devIP)  # 按照ip拿DevLoginAndDownloadArgSturct
                downloadArg = devArgStruct.downloadArgList[downloadArgList_index]  # 在按照索引取出其他需要显示的数据
                itemTextList.append(downloadArg.channel)  # 这样很聪明，避免了进程通信大数据的耗时传递
                itemTextList.append(downloadArg.ytName)
                itemTextList.append(downloadArg.savePath)
                itemTextList.append(downloadArg.downloadTime)
                itemTextList.append(downloadStatus)
            except KeyError:
                logText = f"意外中的情况，这是不应该发生的\n下载器那边传回来一个查不到的设备ip{key_devIP},下载参数列表索引{downloadArgList_index},下载状态{downloadStatus}"
                logger.error(logText)

            self.ui.downloadStatus_TW.insertRow(0)  # 新来的数据都显示在新建的第一行
            for col_index, itemText in enumerate(itemTextList):
                aItem = QTableWidgetItem(str(itemText))
                aItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.ui.downloadStatus_TW.setItem(0, col_index, aItem)
            self.ui.downloadStatus_TW.resizeColumnsToContents()  # 调整列宽
            self.ui.downloadStatus_TW.updateSelectedRows()  # 刷新主题显示状态

            # 下面是对ipCount_TW的界面更新，更新进度条
            if downloadStatus == "下载成功":
                try:
                    row = self.ipRowIndexIndownloadProgress_TW[key_devIP]  # 这个变量是用来存储ip所在行的索引的，用来更新进度条的
                    progressItemWidget = self.ui.downloadProgress_TW.cellWidget(row, 1)
                    progressItemWidget.addOne()
                except KeyError:
                    logText = f"意外中的情况，这是不应该发生的\n下载器那边传回来一个查不到的设备ip{key_devIP},下载参数列表索引{downloadArgList_index},下载状态{downloadStatus}"
                    logger.error(logText)
                self.ui.downloadProgress_TW.resizeColumnsToContents()  # 调整列宽
                self.ui.downloadProgress_TW.updateSelectedRows()  # 刷新主题显示状态
        elif widgetEnum == DVWTableWidgetEnum.DOWNLOAD_PROGRESS_TABLE:
            # 把downloadStatus放到 downloadProgress_TW 的第三列上
            try:
                row = self.ipRowIndexIndownloadProgress_TW[key_devIP]  # 这个变量是用来存储ip所在行的索引的，用来更新进度条的
                aItem = QTableWidgetItem(str(downloadStatus))
                aItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.ui.downloadProgress_TW.setItem(row, 2, aItem)
            except KeyError:
                logText = f"意外中的情况，这是不应该发生的\n下载器那边传回来一个查不到的设备ip{key_devIP},下载参数列表索引{downloadArgList_index},下载状态{downloadStatus}"
                logger.error(logText)
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
                    executor.submit(haikangDownloader, self.downloadResultList, self.downloadResultListCondition, devArgStruct)
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

    def startDownload(self):
        """
        这个方法貌似冗余了
        开个进程通信的list和确保list进程安全的condition。
        开一个不断从上面那个list中拿结果得线程
        再开一个开启进程池的进程池
        """
        self.manager = multiprocessing.Manager()
        self.downloadResultList = self.manager.list()
        self.downloadResultListCondition = self.manager.Condition()
        self.downloadDone = False  # 初始化线程关闭标志
        self.getDownloadResultThreadInstance = threading.Thread(target=self.getDownloadResultThread)  #
        self.getDownloadResultThreadInstance.start()
        self.startDownloadThreadInstance = threading.Thread(target=self.startDownloadThread)  #
        self.startDownloadThreadInstance.start()

    def addDownloadList(self, eflw_ItemDataList: List[ExcelFileListWidgetItemDataStruct]):
        # 点击开始下载按钮后的第一个执行的方法
        self.classifyArg(eflw_ItemDataList)
        # 分类之后填充几个组件     显示下载总量
        self.ui.downloadProgress_TW.clearContents()
        self.ui.downloadProgress_TW.setRowCount(0)
        self.ui.downloadStatus_TW.clearContents()
        self.ui.downloadStatus_TW.setRowCount(0)
        row = 0
        downloadArgsCount = 0  # 所有ip加一块的下载总量
        self.ipRowIndexIndownloadProgress_TW = {}  # 这个变量是用来存储ip所在行的索引的，用来更新进度条的
        self.ui.downloadProgress_TW.setRowCount(len(self.classifyDownloadArgsByDevIP.keys()))
        for devIP, devArgStruct in self.classifyDownloadArgsByDevIP.items():
            inIp_count = len(devArgStruct.downloadArgList)  # 每个ip单独的下载数量
            downloadArgsCount += inIp_count
            aItem = QTableWidgetItem(str(devIP))
            aItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.ui.downloadProgress_TW.setItem(row, 0, aItem)
            self.ipRowIndexIndownloadProgress_TW[devIP] = row

            aItemWidget = PercentProgressBar()  # 设置第二列单元格为 带百分比的进度条
            aItemWidget.setMaximum(inIp_count)
            self.ui.downloadProgress_TW.setCellWidget(row, 1, aItemWidget)
            row += 1  # 换行
        self.ui.argsCount_TL.setText(f"下载进度 (共{downloadArgsCount}个)")

        self.startDownload()


if __name__ == "__main__":  # 用于当前窗体测试
    # 这边真想单独测试的话需要填充下载数据，还是有设备配置生成器的初始化和激活。
    # 那个窗体的ini给个空值就行
    app = QApplication(sys.argv)
    forms = DVWclass()
    forms.show()
    sys.exit(app.exec_())
