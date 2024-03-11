import multiprocessing
import sys
import threading
from datetime import timedelta
from pathlib import Path
from time import sleep

from UnifyNetSDK import HaikangNetSDK
from UnifyNetSDK.haikang.hk_netsdk_exception import HKNetSDKException
from UnifyNetSDK.parameter import UnifyLoginArg, UnifyDownLoadByTimeArg, UnifyFindFileByTimeArg

from loguru import logger

from app.download_video_widget.utils.video2pic import tsPic
from app.download_video_widget.dvw_define import DevLoginAndDownloadArgSturct, DVWTableWidgetEnum

logger.remove()
logger.add(sys.stdout, level="TRACE")

haikangClient = None


# 如果不想用全局变量这种写法就需要
# from UnifyNetSDK.haikang.hk_netsdk import HaikangNetSDK
# 这样导入模块，我包里的__init__文件做了延迟导入，所以这个类实际会被识别为一个function，从而导致直接调用类方法失效（但实例是正常的）
# 最好使用全局变量吧，不然延迟导入就没了


class StopDownloadHandleThread(threading.Thread):
    def __init__(self, downloadHandleDict, downloadHandleDictCondition, updateDownloadStatusFun):
        """
        downloadHandleDictCondition起到了一个lock的作用，锁的是downloadHandleDict
        另外，如果downloadHandleDict是空的，线程休眠，不消耗资源。

        downloadHandleDict的key是下载句柄
        value是个列表，元素按顺序分别是savePath,文件保存地址;
        devIP;iNDEX;设备ip和这个特殊的index都是用于定位元素所在位置用的
        dvw窗体那边有个大的参数字典，设备ip用来定位key，拿到value后
        取downloadArgList[iNDEX],这个不用传整个大列表也能得到整个大列表
        一个是字典的key，另一个是列表元素的index
        毕竟这个下载器和dvw是父子进程的关系，进程通信嘛

        发进度统一用updateDownloadStatusFun
        """
        threading.Thread.__init__(self)
        self.producerDone = False  # 线程结束的标志
        self.downloadHandleDict = downloadHandleDict  # 下载句柄字典
        self.downloadHandleDictCondition = downloadHandleDictCondition  # 下载句柄字典的锁
        self.updateDownloadStatusFun = updateDownloadStatusFun  # 统一上报下载状态的函数

    def setDone(self):
        # 生产者发出完毕信号，也就是主线程那边下载句柄传完了
        self.producerDone = True

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
                stopRestlt = haikangClient.stopDownLoadTimer(downloadHandle)
                if stopRestlt == 100:
                    savePath, iNDEX = self.downloadHandleDict[downloadHandle]
                    tsPic(absVideoPath=savePath)
                    status = "下载成功"  # 目前就实现了这么一种状态，想要其他状态就要自己写stopDownLoadTimer
                    self.updateDownloadStatusFun(iNDEX, status)
                    with self.downloadHandleDictCondition:  # 下载成功后就可以删掉这个句柄了
                        self.downloadHandleDict.pop(downloadHandle)
                # 可是如果下载结果一直不为true呢，句柄就噶了，而且也不能获取对应的失败原因。print的信息很不理想
                # 如果真的存在这种情况，就需要把查询和关闭功能写到这里，然后才能获取真正失败的原因。
                # 这部分暂时不写。
                # 不止，tsPic也是个耗时操作，如果tsPic失败了，也需要上报状态，这个也暂时不写
                # 这么看的话，上报的结构体要比我想的有些庞大。有些状态要报给 下载状态表格组件，有些状态要报给下载进度表格组件，这是两个索引，用于定位表格（那复杂度呢）

            sleep(0.5)


def haikangDownloader(downloadResultList, downloadResultListCondition, devArgs: DevLoginAndDownloadArgSturct):
    # 参数还要加，是否查找录像，日志保存地址，

    deviceAddress = None  # 记录下整个py文件内没有变化的ip地址，这样就不用每次都传了

    def updateDownloadStatusFun(f_iNDEX, f_status, widgetEnum: DVWTableWidgetEnum = DVWTableWidgetEnum.DOWNLOAD_STATUS_TABLE):
        """
        统一上报状态的函数,DVWTableWidgetEnum默认是下载状态表格DOWNLOAD_STATUS_TABLE，多数数据都是往这个表格上报的
        如果widgetEnum = DOWNLOAD_PROGRESS_TABLE，那f_iNDEX就是没有意义的数字
        跟下载参数downloadArg有关的都是往下载状态表格上报的
        跟sdkClient有关的都是往下载进度表格上报的，因为sdkClient是下载进度表格的单位
        """

        downloadResultList.append([widgetEnum, deviceAddress, f_iNDEX, f_status])
        with downloadResultListCondition:
            downloadResultListCondition.notify()

    def execute_operation(func, funcArgs, sucessText, errorText, widgetEnum=DVWTableWidgetEnum.DOWNLOAD_PROGRESS_TABLE):
        # 目前都是执行的sdk的方法，且上报状态也都是发给下载进度表格的
        try:
            executeResult = func(*funcArgs)
            logger.info(f"{deviceAddress}{sucessText}")
            updateDownloadStatusFun(0, sucessText, widgetEnum)
            return executeResult
        except HKNetSDKException as e:
            logger.error(f"{deviceAddress}{errorText},{e}")
            errorStr = str(e) + errorText
            updateDownloadStatusFun(0, errorStr, widgetEnum)
            sys.exit(1)

    global haikangClient  # sdkClient的全局变量是避免不掉的

    easy_login_info = UnifyLoginArg()  # 初始化登陆参数
    easy_login_info.userName = devArgs.devUserName
    easy_login_info.userPassword = devArgs.devPassword
    easy_login_info.devicePort = devArgs.devPort
    easy_login_info.deviceAddress = deviceAddress = devArgs.devIP  # 先做取deviceAddress，因为下面的init也要以设备ip地址做报错根源参照

    haikangClient = HaikangNetSDK()
    execute_operation(haikangClient.init, [], "初始化成功", "初始化失败")
    absLogPath = Path(__file__).absolute().parent
    absLogPath = absLogPath.joinpath("hk_netsdk_log")  # TODO 打包阶段时要将log统一对齐到rootPath/log文件夹下
    execute_operation(haikangClient.logopen, [str(absLogPath)], "打开日志成功", "打开日志失败")

    userID, device_info = execute_operation(haikangClient.login, [easy_login_info], "登录成功", "登录失败")
    # if userID == 0:
    #     logger.error("登录失败")
    #     sys.exit(1)
    print("硬盘数量", device_info.struDeviceV30.byDiskNum)  # 除了返回登陆句柄外的 验证真正成功登录了设备的标志

    downloadHandleDict = {}  # key是下载句柄，value是downloadArg.savePath，下载地址。iNDEX,下载参数在列表中的索引
    downloadHandleDictCondition = threading.Condition()  # 下载句柄字典的锁，线程安全
    stopDownloadThreadInstance = StopDownloadHandleThread(downloadHandleDict, downloadHandleDictCondition, updateDownloadStatusFun)
    stopDownloadThreadInstance.setName(str(devArgs.devIP))  # 给线程加个名字(以IP为单位)，查错的时候方便点
    stopDownloadThreadInstance.start()


    # TODO 海康应该没这个问题吧
    # logger.error("下载主进程休眠5秒")
    # sleep(5)  # TODD  休眠5秒，然后才能正常的进行录像查找，从第一个查找失败到第四个查找成功，最短时间是5秒，我不清楚原因
    # 如果直接运行这个文件main函数，就不用做这个sleep，所以问题应该是出来了进程池上
    # sdk第一方的log提示 用json格式的参数进行查找录像失败
    for iNDEX, downloadArg in enumerate(devArgs.downloadArgList):
        findArg = UnifyFindFileByTimeArg()  # 遍历下载参数，先查录像是否存在，然后再下载
        findArg.channel = downloadArg.channel
        findArg.startTime = downloadArg.downloadTime
        findArg.stopTime = downloadArg.downloadTime + timedelta(seconds=1)
        try:
            findResult = haikangClient.syncFindFileByTime(userID, findArg)  # 这个查询最高居然可达780ms，过分。上层还是用两套代码吧，海康的查询能做异步的，那就让他异步。不然代价太高了
            if findResult is not True:
                text = findArg.getSimpleReadMsg() + "\n没有查到录像"
                logger.error(text)
                status = "没有查到录像"
                updateDownloadStatusFun(iNDEX, status)
                continue
        except HKNetSDKException as e:
            text = findArg.getSimpleReadMsg() + f"\n{e}"
            logger.error(text)
            status = str(e)
            updateDownloadStatusFun(iNDEX, status)
            continue
        downloadbytimeArg = UnifyDownLoadByTimeArg()
        downloadbytimeArg.channel = downloadArg.channel
        downloadbytimeArg.saveFilePath = downloadArg.savePath
        downloadbytimeArg.startTime = downloadArg.downloadTime
        downloadbytimeArg.stopTime = downloadArg.downloadTime + timedelta(seconds=1)
        downLoadHandle = haikangClient.asyncDownLoadByTime(userID, downloadbytimeArg)

        if downLoadHandle != -1:
            with downloadHandleDictCondition:
                downloadHandleDict[downLoadHandle] = [downloadArg.savePath, iNDEX]
                downloadHandleDictCondition.notify()
        else:
            text = downloadbytimeArg.getSimpleReadMsg()
            text += "\n下载句柄为空，该录像下载失败"
            logger.error(text)
            status = "下载句柄为空"
            updateDownloadStatusFun(iNDEX, status)

    with downloadHandleDictCondition:  # 如果没有一个下载句柄传过去的话，就需要手动解锁一下，让子线程顺利关闭
        downloadHandleDictCondition.notify()
    stopDownloadThreadInstance.setDone()
    stopDownloadThreadInstance.join(10)  # 超时10秒，
    if stopDownloadThreadInstance.is_alive():
        logger.error("StopDownloadHandleThread子线程关闭超时")

    execute_operation(haikangClient.logout, [userID], "登出成功", "登出失败")
    execute_operation(haikangClient.logclose, [], "关闭日志成功", "关闭日志失败")
    execute_operation(haikangClient.cleanup, [], "SDK释放资源成功", "SDK释放资源失败")

    if stopDownloadThreadInstance.is_alive():
        threadName = stopDownloadThreadInstance.getName()
        logger.error(f"{threadName}的关闭下载句柄线程超时")


if __name__ == "__main__":
    from _testLoginConfig import testUserConfig

    manager = multiprocessing.Manager()
    t_downloadResultList = manager.list()
    t_downloadResultListCondition = manager.Condition()
    haikangDownloader(t_downloadResultList, t_downloadResultListCondition, testUserConfig)
