import multiprocessing
import sys
import threading
from datetime import timedelta
from pathlib import Path
from time import sleep

from UnifyNetSDK import DaHuaNetSDK
from UnifyNetSDK.dahua.dh_netsdk_exception import DHNetSDKException  # TODO 这个地方的导入应该是有办法统一一下的
from UnifyNetSDK.parameter import UnifyLoginArg, UnifyDownLoadByTimeArg
from loguru import logger

from app.download_video_widget.dvw_define import DevLoginAndDownloadArgStruct, DVWTableWidgetEnum
from app.download_video_widget.utils.video2pic import tsPic

dahuaClient = None


# 如果不想用全局变量这种写法就需要
# from UnifyNetSDK.haikang.hk_netsdk import HaikangNetSDK
# 这样导入模块，我包里的__init__文件做了延迟导入，所以这个类实际会被识别为一个function，从而导致直接调用类方法失效（但实例是正常的）
# 最好使用全局变量吧，不然延迟导入就没了


class StopDownloadHandleThread(threading.Thread):
    def __init__(self, downloadHandleDict, downloadHandleDictCondition, updateDownloadStatusFun):
        """
        downloadHandleDictCondition起到了一个lock的作用，锁的是downloadHandleDict
        另外，如果downloadHandleDict是空的，线程休眠，不占用资源。

        downloadHandleDict的key是下载句柄
        value是个列表，元素按顺序分别是savePath,文件保存地址;
        devIP,设备ip; iNDEX,特殊的index都是用于定位元素所在位置用的
        dvw窗体那边有个大的参数字典，设备ip用来定位key，拿到value后
        取downloadArgList[iNDEX],这个不用传整个大列表也能得到整个大列表
        一个是字典的key，另一个是列表元素的index
        """
        threading.Thread.__init__(self)
        self.producerDone = False  # 线程可以结束了的标志
        self.downloadHandleDict = downloadHandleDict  # 下载句柄字典
        self.downloadHandleDictCondition = downloadHandleDictCondition  # 下载句柄字典的锁
        self.updateDownloadStatusFun = updateDownloadStatusFun  # 统一上报下载状态的函数

    def setDone(self):
        # 生产者发出完毕信号，也就是主线程那边下载句柄传完了
        self.producerDone = True  # 控制线程关闭的标志

    # TODO 改动太多了，估计要开类了，不然海康那边的代码同步起来太费劲了

    def run(self):
        while True:
            with self.downloadHandleDictCondition:
                if not self.downloadHandleDict:  # 注意，我用了两个with condition，由于查询是个非常耗时的操作，查询的期间是不影响生产者继续添加句柄的。
                    if self.producerDone is True:  # 如果下载句柄列表为空，且生产者发出完毕信号，则跳出永真循环（线程结束）。
                        logger.info(f"{self.getName()}的StopDownloadConsumer子线程正常关闭")
                        break
                    self.downloadHandleDictCondition.wait()  # 如果下载句柄列表为空，但生产者没有发出完毕信号，则线程阻塞等待。
            for downloadHandle in list(self.downloadHandleDict.keys()):  # 迭代字典的时候不允许更改字典（下面进行了一个pop操作），所以做了个keys的副本
                # 上面取key是原子的，但是list()不是原子操作。这正好，因为由于查询是个非常耗时的操作，查询的期间是不影响生产者继续添加句柄的。就等下一批再处理呗
                downloadPos = False
                try:
                    downloadPos = dahuaClient.stopDownLoadTimer(downloadHandle)
                except DHNetSDKException as e:  # 除非把stopDownLoadTimer拆开，不然拿不到具体的信息，这块应该没什么大问题
                    logger.error(f"{downloadHandle}的stopDownLoadTimer执行失败，错误代码{type(e).__name__}")
                savePath, iNDEX, TimeoutNum = self.downloadHandleDict[downloadHandle]
                # dahua这边没有海康那个200的下载异常错误码，那我怎么知道下载失败了呢？
                # TODO 注意看   fDownLoadPosCallBack回调函数有这么一个参数
                # dwDownLoadSize; 指已经播放的大小，单位为KB，当其值为 - 1; 时表示本次回放结束，-2; 表示写文件失败
                # 那CLIENT_GetDownloadPos是不是也有相同的属性，可以返回-1，-2？
                if downloadPos is True:
                    try:
                        tsPic(absVideoPath=savePath)  # 这个也需要上报状态，先不写，因为整体使用逻辑还有点不成熟
                    except Exception as e:
                        logger.error(f"{savePath}转换失败，错误代码{type(e).__name__}\n如果tsPic那边能处理好，那这个log是不应该出现的")
                    status = "下载成功"
                    logger.success(f"下载ID {downloadHandle} {savePath} {status}")
                    self.updateDownloadStatusFun(iNDEX, status)
                    with self.downloadHandleDictCondition:  # 下载成功后就可以删掉这个句柄了
                        self.downloadHandleDict.pop(downloadHandle)
                else:
                    if TimeoutNum == 0:
                        status = "下载超时"
                        logger.error(f"下载ID {downloadHandle} {savePath} {status}")
                        self.updateDownloadStatusFun(iNDEX, status)
                        with self.downloadHandleDictCondition:  # 下载超时需要抛出句柄
                            self.downloadHandleDict.pop(downloadHandle)
                    else:
                        TimeoutNum -= 1
                        with self.downloadHandleDictCondition:
                            self.downloadHandleDict[downloadHandle] = [savePath, iNDEX, TimeoutNum]
                        logger.debug(f"下载ID {downloadHandle}，文件地址 {savePath}，下载进度 {downloadPos}，剩余超时次数 {TimeoutNum}")
            sleep(0.5)


def dahuaDownloader(downloadResultList, downloadResultListCondition, devArgs: DevLoginAndDownloadArgStruct):
    # 参数还要加，是否查找录像，日志保存地址，

    deviceAddress = None  # 记录下整个py文件内没有变化的ip地址，这样就不用每次都传了

    def updateDownloadStatusFun(f_iNDEX, f_status, widgetEnum: DVWTableWidgetEnum = DVWTableWidgetEnum.DOWNLOAD_STATUS_TABLE):
        """
        统一上报状态的函数,DVWTableWidgetEnum默认是下载状态表格DOWNLOAD_STATUS_TABLE，多数数据都是往这个表格上报的
        如果widgetEnum = DOWNLOAD_PROGRESS_TABLE，那f_iNDEX就是没有意义的数字
        跟下载参数downloadArg有关的都是往下载状态表格上报的
        跟sdkClient有关的都是往下载进度表格上报的，因为sdkClient是下载进度表格的单位
        """
        logger.debug(f"{widgetEnum}更新状态：{deviceAddress} {f_iNDEX} {f_status}")  # TODO UI那边又出现上报数量不对等的情况，不知道是关闭句柄线程的问题还是什么
        with downloadResultListCondition:  # 用这个log应该就能查清楚了
            downloadResultList.append([widgetEnum, deviceAddress, f_iNDEX, f_status])
            downloadResultListCondition.notify()

    def execute_operation(func, funcArgs, _sucessText, _errorText, needExit=True, widgetEnum=DVWTableWidgetEnum.DOWNLOAD_PROGRESS_TABLE):
        # TDOO 就是这里，改造为装饰器，一般情况下只需要传两个参数就好了
        # 目前都是执行的sdk的方法，且上报状态也都是发给下载进度表格的
        try:
            executeResult = func(*funcArgs)
            logger.info(f"{deviceAddress}{_sucessText}")
            updateDownloadStatusFun(0, _sucessText, widgetEnum)
            return executeResult
        except DHNetSDKException as _e:
            logger.error(f"{deviceAddress}{_errorText},{type(_e).__name__}")
            _errorStr = type(_e).__name__ + _errorText
            updateDownloadStatusFun(0, _errorStr, widgetEnum)
            if needExit:
                sys.exit(1)  # 有些方法执行后还不能立即退出。不过这个判断也很可能用不上

    global dahuaClient  # sdkClient的全局变量是避免不掉的

    easy_login_info = UnifyLoginArg()  # 初始化登陆参数
    easy_login_info.userName = devArgs.devUserName
    easy_login_info.userPassword = devArgs.devPassword
    easy_login_info.devicePort = devArgs.devPort
    easy_login_info.deviceAddress = deviceAddress = devArgs.devIP  # 先做取deviceAddress，因为下面的init也要以设备ip地址做报错根源参照

    dahuaClient = DaHuaNetSDK()
    execute_operation(dahuaClient.init, [], "初始化成功", "初始化失败")
    absLogPath = Path(__file__).absolute().parent.parent.parent
    absLogPath = absLogPath.joinpath("dh_netsdk_log/netsdk1.log")  # TODO 打包阶段时要将log统一对齐到rootPath/log文件夹下
    logger.info(f"大华netsdk的log地址为{str(absLogPath)}")
    execute_operation(dahuaClient.logopen, [str(absLogPath)], "打开日志成功", "打开日志失败")

    try:
        userID, device_info = dahuaClient.login(easy_login_info)
        sucessText = "登录成功"
        logger.info(f"{deviceAddress}{sucessText}")
        updateDownloadStatusFun(0, sucessText, widgetEnum=DVWTableWidgetEnum.DOWNLOAD_PROGRESS_TABLE)
    except DHNetSDKException as e:
        errorText = "登录失败"
        logger.error(f"{deviceAddress}{errorText},{type(e).__name__}")
        errorStr = type(e).__name__ + errorText
        updateDownloadStatusFun(0, errorStr, widgetEnum=DVWTableWidgetEnum.DOWNLOAD_PROGRESS_TABLE)
        dahuaClient.logclose()  # 这次就不上报了
        dahuaClient.cleanup()
        sys.exit(1)  # stopDownloadThread线程还没开，所以不用管

    logger.trace("登录成功的测试，打印硬盘数量", device_info.stuDeviceInfo.nDiskNum)  # 除了返回登陆句柄外的 验证真正成功登录了设备的标志

    downloadHandleDict = {}  # key是下载句柄，value是downloadArg.savePath，下载地址。iNDEX,下载参数在列表中的索引
    downloadHandleDictCondition = threading.Condition()  # 下载句柄字典的锁，线程安全
    stopDownloadThreadInstance = StopDownloadHandleThread(downloadHandleDict, downloadHandleDictCondition, updateDownloadStatusFun)
    stopDownloadThreadInstance.setName(str(devArgs.devIP))  # 给线程加个名字(以IP为单位)，查错的时候方便点
    stopDownloadThreadInstance.start()

    TimeoutNum = 20  # 传给StopDownloadHandleThread的参数，如果超过这个时间(20*sleep(0.5) = 10秒（我知道有偏差）)，就直接抛出这个下载句柄
    # 如果直接运行这个文件main函数，就不用做这个sleep，所以问题应该是出来了进程池上
    # sdk第一方的log提示 用json格式的参数进行查找录像失败
    for iNDEX, downloadArg in enumerate(devArgs.downloadArgList):
        # 查找不搞了
        # findArg = UnifyFindFileByTimeArg()  # 遍历下载参数，先查录像是否存在，然后再下载
        # findArg.channel = downloadArg.channel
        # findArg.startTime = downloadArg.downloadTime
        # findArg.stopTime = downloadArg.downloadTime + timedelta(seconds=1)
        # try:
        #     findResult = dahuaClient.syncFindFileByTime(userID, findArg)  # 这个查询最高居然可达780ms，过分。上层还是用两套代码吧，海康的查询能做异步的，那就让他异步。不然代价太高了
        #     if findResult is not True:
        #         text = findArg.getSimpleReadMsg() + "\n没有查到录像"
        #         logger.error(text)
        #         status = "没有查到录像"
        #         updateDownloadStatusFun(iNDEX, status)
        #         continue
        # except DHNetSDKException as e:
        #     text = findArg.getSimpleReadMsg() + f"\n{e}"
        #     logger.error(text)
        #     status = str(e)
        #     updateDownloadStatusFun(iNDEX, status)
        #     continue
        downloadbytimeArg = UnifyDownLoadByTimeArg()
        downloadbytimeArg.channel = downloadArg.channel
        downloadbytimeArg.saveFilePath = downloadArg.savePath
        downloadbytimeArg.startTime = downloadArg.downloadTime
        downloadbytimeArg.stopTime = downloadArg.downloadTime + timedelta(seconds=1)
        try:
            downLoadHandle = dahuaClient.asyncDownLoadByTime(userID, downloadbytimeArg)
            if downLoadHandle != 0:
                with downloadHandleDictCondition:
                    downloadHandleDict[downLoadHandle] = [downloadArg.savePath, iNDEX, TimeoutNum]
                    downloadHandleDictCondition.notify()
            else:
                text = downloadbytimeArg.getSimpleReadMsg()
                text += "\n下载句柄为空，该录像下载失败"
                logger.error(text)
                status = "下载句柄为空"
                updateDownloadStatusFun(iNDEX, status)
        except DHNetSDKException as e:
            text = downloadbytimeArg.getSimpleReadMsg() + f"\n{type(e).__name__}"
            text += "\n下载句柄为空，该录像下载失败"
            logger.error(text)
            status = str(type(e).__name__)
            updateDownloadStatusFun(iNDEX, status)

    with downloadHandleDictCondition:  # 如果没有一个下载句柄传过去的话，就需要手动解锁一下，让子线程顺利关闭
        downloadHandleDictCondition.notify()
    stopDownloadThreadInstance.setDone()
    stopDownloadThreadInstance.join(10)  # 超时10秒，
    if stopDownloadThreadInstance.is_alive():
        logger.error("StopDownloadHandleThread子线程关闭超时")

    execute_operation(dahuaClient.logout, [userID], "登出成功", "登出失败")
    execute_operation(dahuaClient.logclose, [], "关闭日志成功", "关闭日志失败")
    execute_operation(dahuaClient.cleanup, [], "SDK释放资源成功", "SDK释放资源失败")

    if stopDownloadThreadInstance.is_alive():
        threadName = stopDownloadThreadInstance.getName()
        logger.error(f"{threadName}的关闭下载句柄线程超时")
    logger.info(f"{deviceAddress}下载子进程关闭")


if __name__ == "__main__":
    from _testLoginConfig import testUserConfig

    manager = multiprocessing.Manager()
    t_downloadResultList = manager.list()
    t_downloadResultListCondition = manager.Condition()
    dahuaDownloader(t_downloadResultList, t_downloadResultListCondition, testUserConfig)
