import multiprocessing
import sys
import threading
import time
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime
from multiprocessing.managers import ListProxy, ConditionProxy
from pathlib import Path
from typing import List

from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import (QApplication, QTableWidgetItem)
from UnifyNetSDK.dahua.dh_playsdk import DaHuaPlaySDK
from UnifyNetSDK.dahua.dh_playsdk_exception import DHPlaySDKException, PLAY_NO_FRAME, PLAY_OPEN_FILE_ERROR
from loguru import logger
from qfluentwidgets import MessageBox, InfoBar, InfoBarPosition

from app.download_video_widget.base_dvw import BaseDVW
from app.download_video_widget.dvw_define import DownloadArg, DevLoginAndDownloadArgStruct, DVWTableWidgetEnum
from app.download_video_widget.netsdk.dahua_async_download import dahuaDownloader
from app.download_video_widget.netsdk.haikang_async_download import HaikangDownloader
from app.download_video_widget.utils.progress_bar import PercentProgressBar
from app.esheet_process_widget.epw_define import ExcelFileListWidgetItemDataStruct
from app.utils.project_path import DVW_DOWNLOAD_FILE_SUFFIX, DVW_CONVERTED_FILE_SUFFIX, DVW_DATETIME_FORMAT, DVW_DOWNLOAD_VIDEO_PATH
from app.utils.tools import findItemTextInTableWidgetRow, AlignCenterQTableWidgetItem, removeDir


class DVWclass(BaseDVW):
    """
    本身一个主进程
    开一个接收并处理 下载子进程发送过来的数据的 线程
    开一个负责启动 下载子进程 的线程，下载子进程中开一个负责关闭下载句柄的线程

    """
    downloadStatusChange = pyqtSignal(list)
    downloadStatusDone = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)  # 调用父类构造函数，创建窗体

        # formsConfigDict = parent.formsConfigDict  # dvw界面暂时没有配置
        # self.dvw_config = formsConfigDict["dvw"]  # 后期要做下载进程数量和是否在下载前进行查找操作
        self.devConfigGenerate = parent.devConfigGenerate  # 因为加载设备配置生成器需要读取一个文件，所以由父类统一初始化并激活之后再下发给子类，更重要的是主窗体那边负责exception的报错弹窗
        # TODO 可以考虑 formsConfigDict 和 devConfigGenerate 用传参的方式，因为现在两个 变量 的生成不是那么复杂了

        # 从init这里做实例变量声明根本就是个错误，很容易就把初始化给忘了

        self.classifyDownloadArgsByDevIP = {}  # 把下载参数按照ip分类，因为最终下载时是以ip为单位的
        self.classifyDownloadArgsIndexByFolder = {}  # 将classifyDownloadArgsByDevIP按照文件夹分类，方便跟本地的文件夹进行对比，以得到downloadErrorArgs
        self.downloadErrorArgs = {}  # 收集下载错误的下载参数，和classifyDownloadArgsByDevIP是相同结构的
        self.remkDirWithDownloadErrorArgs = set()  # 用于记录需要重新创建的文件夹，在文件下载完成之后的空档期用户是有可能删除所有文件夹的。1 “下载器没有权限创建文件夹”，2 遍历downloadErrorArgs取文件夹列表性能上不划算，几乎相当于下载器中每次做个文件夹是否存在的检查了。所以创建这个变量

        # self.beforeDownloadErrorFlag = ["初始化失败", "登陆失败"]
        # 如果子进程上报的设备状态在这个列表中就表明设备登陆失败了，就需要把整个key_ip中的downloadArgs_value都加到self.downloadErrorArgs中
        # 这个想法很不错，不过dvrSDK有太多不可控的情况发生，以我目前的能力无法准确无误的识别SDK的错误，在这个分支里这个方法被弃用了
        self.manager: multiprocessing.Manager = None  # 进程通信对象管理器
        self.downloadResultList: ListProxy = None  # 从manager拿的进程通信列表对象，它的方法定义在multiprocess.managers.BaseListProxy
        self.downloadResultListCondition: ConditionProxy = None  # 负责downloadResultList的进程安全同步和非空任务事件通知
        self.getDownloadResultThreadInstance = None  # getDownloadResultThread是从downloadResultList中不断拿结果并发信号的线程
        self.downloadDone: bool = False  # 一个关闭标志，用来关getDownloadResultThread的
        self.ipRowIndexIndownloadProgress_TW = {}  # 这个变量是用来存储ip所在行的索引的，用来更新进度条的
        self.startDownloadThreadInstance = None  # 负责开进程池的线程,startDownloadThread
        self.totalDownloadCount = None  # 下载总量，用来更新 下载进度 标签
        self.downloadedCount = None  # 下载成功的数量。 　只能从那个线程中进行更改。也是用来更新 下载进度 标签
        self.downloadArgsNumInFolderDict = {}  # 从文件夹的角度统计下载参数的数量，也就是每个文件夹下应有文件数量.这是fileCount_TW要用的变量，取自下载前
        self.downloadStatusChange.connect(self.updateDownloadStatusUI)  # 这个信号也是getDownloadResultThread发出来的
        self.downloadStatusDone.connect(self.do_downloadStatusDone)  # 由于 下载线程是一个多线程，而下载结束后需要进行一些UI上的改动，故需要线程发送下载完成的信号，然后由槽函数负责更新UI

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
                    devArgStruct = DevLoginAndDownloadArgStruct()  # 一个用来判断，一个用来指向数据结构
                    devArgStruct.devType = devConfig.devType  # 如果数据类实例不存在，就新建一个，然后指向这个数据类实例
                    devArgStruct.devIP = devConfig.devIP
                    devArgStruct.devPort = devConfig.devPort
                    devArgStruct.devUserName = devConfig.devUserName
                    devArgStruct.devPassword = devConfig.devPassword

                v_channel = devConfig.devChannel
                downloadArg = DownloadArg(savePath=filePath, downloadTime=scanTime, ytName=v_ytName, channel=v_channel)  # 月台名和通道是冗余的存储，但不这么写的话，解析和存储的复杂度
                devArgStruct.downloadArgList.append(downloadArg)  # 如果数据类实例存在，那就直接改呗
                self.classifyDownloadArgsByDevIP[devConfig.devIP] = devArgStruct  # 这里重新改一下字典的value，应该也不算什么大事，不然就得写重复代码了

        self.classifyDownloadArgsIndexByFolder = {}  # # 将classifyDownloadArgsByDevIP按照文件夹分类，不复制下载参数，而是取下载参数在classifyDownloadArgsByDevIP中的索引
        for devIP, devArgStruct in self.classifyDownloadArgsByDevIP.items():
            for downloadArgIndex, downloadArg in enumerate(devArgStruct.downloadArgList):
                savePath = Path(downloadArg.savePath)
                folderName = str(savePath.parent.stem)  # 获取文件夹名称
                fileName = str(savePath.stem)  # 获取文件名称
                dirDict = self.classifyDownloadArgsIndexByFolder.get(folderName, {})  # 尝试取出已有的 文件夹字典
                dirDict[fileName] = [devIP, downloadArgIndex]  # 这一步就已经把同文件夹下的相同单号给过滤掉了，但如果其他参数不相同就很头疼了，比如一个单号有两次三超的扫描时间记录
                self.classifyDownloadArgsIndexByFolder[folderName] = dirDict
        """
        {   # classifyDownloadArgsIndexByFolder结构示例
            '0318': {'shipID': ['10.10.10.11', 6], 'shipID': ['10.10.10.12', 23]},
            '0320': {'shipID': ['10.10.10.12', 7]},
            '0313': {'shipID': ['10.10.10.13', 1]}
        }
        """

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
            devArgStruct = self.classifyDownloadArgsByDevIP.get(key_devIP)  # 按照ip拿DevLoginAndDownloadArgStruct
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

        elif widgetEnum == DVWTableWidgetEnum.DOWNLOAD_PROGRESS_TABLE:
            deviceStatus = downloadStatus
            # 把deviceStatus放到 downloadProgress_TW 的第三列上
            aItem = AlignCenterQTableWidgetItem(str(deviceStatus))
            self.ui.downloadProgress_TW.setItem(rowIndexIndownloadProgress_TW, 2, aItem)
        self.ui.downloadStatus_TW.resizeColumnsToContents()  # 调整列宽
        self.ui.downloadStatus_TW.updateSelectedRows()  # 刷新主题显示状态
        self.ui.downloadProgress_TW.resizeColumnsToContents()  # 调整列宽
        self.ui.downloadProgress_TW.updateSelectedRows()  # 刷新主题显示状态

    def startDownloadThread(self, downloadArgs):
        """
        负责开启进程池的线程，最大进程数量要做参数化的(UI那边要限制最多是cpu_count个)
        """

        ipNum = len(downloadArgs.keys())
        if ipNum >= 8:
            maxWorkers = 8  # 大于8个ip就开8个进程池，不然就开对应数量的就好了
        else:
            maxWorkers = ipNum
        with ProcessPoolExecutor(max_workers=maxWorkers) as executor:
            for devIP, devArgStruct in downloadArgs.items():
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

        self.downloadStatusDone.emit(True)

    def handleDownloadList(self, eflw_ItemDataList: List[ExcelFileListWidgetItemDataStruct]):
        # 点击开始下载按钮后的第一个执行的方法
        self.classifyArg(eflw_ItemDataList)
        self.beforeDownload(self.classifyDownloadArgsByDevIP)  # 其实这一步里就已经开始下载了

    def beforeDownload(self, downloadArgs):
        # 分类之后填充几个组件     显示下载总量
        self.ui.downloadProgress_TW.clearContents()
        self.ui.downloadProgress_TW.setRowCount(0)
        self.ui.downloadStatus_TW.clearContents()
        self.ui.downloadStatus_TW.setRowCount(0)
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
        self.startDownloadThreadInstance = threading.Thread(target=self.startDownloadThread, args=[downloadArgs, ])  #
        self.startDownloadThreadInstance.start()

    @pyqtSlot()
    def on_reDownload_PB_clicked(self):
        # 重新下载按钮被按下

        for folderName in self.remkDirWithDownloadErrorArgs:  # 先创建文件夹，主下载按钮的文件夹创建在classifyArg中，
            pathObject = Path(DVW_DOWNLOAD_VIDEO_PATH / folderName)  # 而重新下载前用户是有可能删除文件夹的，我这里稍微的确保一下文件夹的存在
            pathObject.mkdir(exist_ok=True)  # 我当然知道如果真的想保证文件夹路径存在就应该在下载器中实现这个功能
        self.beforeDownload(self.downloadErrorArgs)  # 可这样会浪费多少时间性能资源，下载器还是个多进程的，指不定整上个什么查不出来的bug

    @pyqtSlot(bool)
    def do_downloadStatusDone(self, done):
        if done:
            logger.info("自动执行mp4转jpg程序")
            self.on_convert_PB_clicked()  # 自动执行一次mp4转jpg
            logger.info("收集缺失文件信息")
            self.afterDownload()  # 这是下载步骤结束后要做的操作，最核心的功能是核对下载文件数量是否匹配

    @pyqtSlot()
    def on_convert_PB_clicked(self):
        # MP4转JPG按钮被按下
        # 遍历整个pic文件夹及其所有子文件夹中的mp4文件，全部转换为jpg文件
        fileList = [pathObject for pathObject in Path(DVW_DOWNLOAD_VIDEO_PATH).rglob("*") if pathObject.is_file()]
        mp4FileList = [pathObject for pathObject in fileList if pathObject.suffix == DVW_DOWNLOAD_FILE_SUFFIX]
        for filePath in mp4FileList:
            relative_path = str(filePath.relative_to(DVW_DOWNLOAD_VIDEO_PATH.parent))
            absPicPath = str(filePath.with_name(str(filePath.stem) + ".jpg").absolute())
            playClient = None
            nPort = None
            playResult = False
            openResult = False
            try:
                playClient = DaHuaPlaySDK()
                nPort = playClient.getFreePort()
                openResult = playClient.openFile(nPort, filePath)
                playResult = playClient.play(nPort)
                time.sleep(0.2)  # 要等dll那边把数据“填充”到port才能开始操作
                playClient.catchPic(nPort, absPicPath)
            except PLAY_OPEN_FILE_ERROR:
                InfoBar.error(title='错误', content=f"{relative_path}文件打开失败，已自动删除", orient=Qt.Horizontal, isClosable=True, position=InfoBarPosition.TOP_LEFT, duration=3000, parent=self.ui.fileCount_TW)
                logger.error(f"{filePath}的mp4文件打开失败，已自动删除")
            except PLAY_NO_FRAME:
                InfoBar.error(title='错误', content=f"{relative_path}文件没有有效帧，已自动删除", orient=Qt.Horizontal, isClosable=True, position=InfoBarPosition.TOP_LEFT, duration=3000, parent=self.ui.fileCount_TW)
                logger.error(f"{filePath}的mp4文件没有有效帧，已自动删除")
            except DHPlaySDKException as e:
                InfoBar.error(title='错误', content=f"{relative_path}文件转换失败，错误代码{type(e).__name__}，已自动删除", orient=Qt.Horizontal, isClosable=True, position=InfoBarPosition.TOP_LEFT, duration=3000, parent=self.ui.fileCount_TW)
                logger.error(f"{filePath}转换失败，错误代码{type(e).__name__}")
            finally:
                if playClient and nPort:
                    if playResult:
                        playClient.stop(nPort)
                    if openResult:
                        playClient.close(nPort)
                    playClient.releasePort(nPort)
                try:
                    Path(filePath).unlink()
                except Exception as e:
                    logger.error(f"{filePath}自动删除失败，错误代码{type(e).__name__}")
                    InfoBar.error(title='错误', content=f"{filePath}自动删除失败，错误代码{str(e)}", orient=Qt.Horizontal, isClosable=True, position=InfoBarPosition.TOP_LEFT, duration=3000, parent=self.ui.fileCount_TW)
        QApplication.processEvents()

    @pyqtSlot()
    def on_deleteAllFile_PB_clicked(self):
        # 删除所有文件按钮被按下
        # 删除指定目录下的所有文件和子目录，但保留目录本身
        def tryRemoveDir():
            try:
                removeDir(DVW_DOWNLOAD_VIDEO_PATH)
            except Exception as e:
                errorText = f"删除失败，错误代码{str(e)}"
                InfoBar.error(title='提示', content=errorText, orient=Qt.Horizontal, isClosable=True, position=InfoBarPosition.TOP_LEFT, duration=5000, parent=self.ui.fileCount_TW)
                logger.error(errorText)

        errorMsgBox = MessageBox('确认', "是否要清空pic文件夹中的所有子级文件夹和文件？", self)
        errorMsgBox.yesSignal.connect(tryRemoveDir)
        errorMsgBox.raise_()
        errorMsgBox.yesButton.setText('确定')
        errorMsgBox.cancelButton.setText('取消')
        errorMsgBox.exec()

    def afterDownload(self):
        self.downloadErrorArgs = {}  # 收集下载错误的下载参数，和classifyDownloadArgsByDevIP是相同结构的
        self.remkDirWithDownloadErrorArgs = set()  # 用于记录需要重新创建的文件夹，在文件下载完成之后的空档期用户是有可能删除所有文件夹的。1 “下载器没有权限创建文件夹”，2 遍历downloadErrorArgs取文件夹列表性能上不划算，几乎相当于下载器中每次做个文件夹是否存在的检查了。所以创建这个变量
        # 下载完成后执行的方法，
        # localDirsList和classifyDownloadArgsIndexByFolder是相同的结构，不过它的dirDict[fileName]的内容是个空列表
        # 如果localDirsList含有classifyDownloadArgsIndexByFolder中相同fileName就表示这个文件下载成功了，需要想办法在classifyDownloadArgsIndexByFolder中移除这个fileName
        # 如果不含有这个fileName就表示这个文件下载失败了，需要保留相关参数以供后期进行重新下载
        localDirsDict = {}
        for first_level_dir in Path(DVW_DOWNLOAD_VIDEO_PATH).iterdir():
            if not first_level_dir.is_dir():
                continue
            for second_level_file in first_level_dir.iterdir():  # 遍历日期目录下的文件夹
                if second_level_file.is_file() and second_level_file.suffix == DVW_CONVERTED_FILE_SUFFIX:  # 只有文件且后缀为.jpg才算下载成功（我会在统计前做一个mp4转jpg的操作，程序走到这还是存在mp4文件的话就说明这个mp4文件有问题（转换失败），那就的重新下载了）
                    folderName = first_level_dir.stem  # 文件夹名称
                    fileName = second_level_file.stem  # 文件名称
                    dirDict = localDirsDict.get(folderName, {})  # 尝试取出已有的 文件夹字典
                    dirDict[fileName] = []
                    localDirsDict[folderName] = dirDict
        # 上面取本地数据，下面对比内存数据
        for folderName, folderContent in localDirsDict.items():
            if folderName not in self.classifyDownloadArgsIndexByFolder:
                continue  # 跳过classifyDownloadArgsIndexByFolder中不存在的文件夹。
            for fileName in list(folderContent.keys()):  # 在指定文件夹中删除指定的文件名索引
                if fileName in self.classifyDownloadArgsIndexByFolder[folderName]:  # 检查文件名是否在该文件夹的分类下载参数索引中
                    del self.classifyDownloadArgsIndexByFolder[folderName][fileName]  # 如果是，则从索引中删除该文件名
        # 移除所有内容为空的文件夹
        self.classifyDownloadArgsIndexByFolder = {folder: content for folder, content in self.classifyDownloadArgsIndexByFolder.items() if content}
        # 第三步，把self.classifyDownloadArgsIndexByFolder按照ip分类并写入到self.downloadErrorArgs中
        for folderName, folderContent in self.classifyDownloadArgsIndexByFolder.items():
            self.remkDirWithDownloadErrorArgs.add(folderName)  # 这里不用集合也行，因为上面的folderName已经用字典的key特性去重过了
            for fileName, fileContent in folderContent.items():
                devIP, downloadArgList_index = fileContent
                try:
                    devArgStruct = self.classifyDownloadArgsByDevIP.get(devIP)  # 按照ip拿DevLoginAndDownloadArgStruct
                except IndexError:
                    logger.error(f"{devIP}的DevLoginAndDownloadArgStruct不存在,这是不应该发生的，说明程序有BUG，很严重！")
                    continue
                downloadArg = devArgStruct.downloadArgList[downloadArgList_index]  # 一次只能存一个downloadArg
                error_DevArgStruct = self.downloadErrorArgs.get(devIP, None)  #
                if error_DevArgStruct is None:
                    error_DevArgStruct = DevLoginAndDownloadArgStruct()  # 如果数据类实例不存在，就新建一个数据类实例
                    error_DevArgStruct.copy_from(devArgStruct, keepDownloadArgListEmpty=True)
                error_DevArgStruct.downloadArgList.append(downloadArg)  # 添加下载参数
                self.downloadErrorArgs[devIP] = error_DevArgStruct
        # 第四步，把self.downloadErrorArgs的下载参数数量更新到UI中
        self.ui.downloadError_TW.clearContents()  # 先清空下载错误表格组件
        self.ui.downloadError_TW.setRowCount(0)
        for devIP, devArgStruct in self.downloadErrorArgs.items():
            self.ui.downloadError_TW.insertRow(0)
            errorNum = len(devArgStruct.downloadArgList)
            ipItem = AlignCenterQTableWidgetItem(str(devIP))  # 将ip和错误数量写入表格组件
            self.ui.downloadError_TW.setItem(0, 0, ipItem)
            errorNumItem = AlignCenterQTableWidgetItem(str(errorNum))
            self.ui.downloadError_TW.setItem(0, 1, errorNumItem)
        QApplication.processEvents()
        InfoBar.warning(title='提示', content="缺失文件统计完成", orient=Qt.Horizontal, isClosable=True, position=InfoBarPosition.TOP_LEFT, duration=1000, parent=self.ui.downloadError_TW)


if __name__ == "__main__":  # 用于当前窗体测试
    # 这边真想单独测试的话需要填充下载数据，还是有设备配置生成器的初始化和激活。
    # 那个窗体的ini给个空值就行
    app = QApplication(sys.argv)
    forms = DVWclass()
    forms.show()
    sys.exit(app.exec_())
