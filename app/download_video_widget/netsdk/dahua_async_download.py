import sys
import threading
from datetime import timedelta
from pathlib import Path
from time import sleep

from UnifyNetSDK import DaHuaNetSDK, DHNetSDKException, DaHuaPlaySDK
from UnifyNetSDK.parameter import UnifyLoginArg, UnifyDownLoadByTimeArg, UnifyFindFileByTimeArg
from _testLoginConfig import testUserConfig

from loguru import logger

from app.download_video_widget.utils.video2pic import tsPic

logger.remove()
logger.add(sys.stdout, level="TRACE")

dahuaClient = None


# 如果不想用全局变量这种写法就需要
# from UnifyNetSDK.haikang.hk_netsdk import HaikangNetSDK
# 这样导入模块，我包里的__init__文件做了延迟导入，所以这个类实际会被识别为一个function，从而导致直接调用类方法失效（但实例是正常的）


class StopDownloadConsumer(threading.Thread):
    def __init__(self, condition: threading.Condition, downloadHandleDict: dict):
        threading.Thread.__init__(self)
        self.done = False
        self.condition = condition
        self.downloadHandleDict = downloadHandleDict

    def producerDone(self):
        self.done = True

    def run(self):
        while True:
            if not self.downloadHandleDict:
                if self.done is True:  # 如果下载句柄列表为空，且生产者发出完毕信号，则跳出永真循环（线程结束）。
                    break
                with self.condition:  # 注意，我用了两个with condition，由于查询是个非常耗时的操作，查询的期间是不影响生产者继续添加句柄的。
                    self.condition.wait()  # 如果下载句柄列表为空，但生产者没有发出完毕信号，则线程阻塞等待。
            for downloadHandle in list(self.downloadHandleDict.keys()):     # 迭代字典的时候不允许更改字典（下面进行了一个pop操作），所以做了个keys的副本
                stopRestlt = dahuaClient.stopDownLoadTimer(downloadHandle)
                if stopRestlt is True:
                    tsPic(absVideoPath=self.downloadHandleDict[downloadHandle])
                    with self.condition:  # 下载成功后就可以删掉这个句柄了
                        self.downloadHandleDict.pop(downloadHandle)
                # 可是如果下载结果一直不为true呢，句柄就噶了，而且也不能获取对应的失败原因。print的信息很不理想
                # 如果真的存在这种情况，就需要把查询和关闭功能写到这里，然后才能获取真正失败的原因。
                # 这部分暂时不写。
            sleep(0.5)


# TODO 不管是两者的main主函还是stop子线程都需要高度定制话，
# 比如main主函的Exception的抓取
# 比如stop子线程的重构，未来肯定是要做的，所以需要两个文件
# play_ctrl可以省

def main():
    global dahuaClient
    dahuaClient = DaHuaNetSDK()
    dahuaClient.init()
    absLogPath = Path(__file__).absolute().parent
    absLogPath = absLogPath.joinpath("dh_netsdk_log/netsdk1.log")
    dahuaClient.logopen(str(absLogPath))

    easy_login_info = UnifyLoginArg()
    easy_login_info.userName = testUserConfig.devUserName
    easy_login_info.userPassword = testUserConfig.devPassword
    easy_login_info.devicePort = testUserConfig.devPort
    easy_login_info.deviceAddress = testUserConfig.devIP

    userID, device_info = dahuaClient.login(easy_login_info)
    print("硬盘数量", device_info.stuDeviceInfo.nDiskNum)

    dahuaCondition = threading.Condition()
    downloadHandleDict = {}  # key是下载句柄，value是下载地址
    stopDownInstance = StopDownloadConsumer(dahuaCondition, downloadHandleDict)
    stopDownInstance.start()

    for channel, downloadArgList in testUserConfig.downloadArgDict.items():
        for downloadArg in downloadArgList:
            findArg = UnifyFindFileByTimeArg()
            findArg.channel = channel
            findArg.startTime = downloadArg.downloadTime
            findArg.stopTime = downloadArg.downloadTime + timedelta(seconds=1)
            try:
                findResult = dahuaClient.syncFindFileByTime(userID, findArg)  # 这个查询最高居然可达780ms，过分。上层还是用两套代码吧，海康的查询能做异步的，那就让他异步。不然代价太高了
                print(f"查找录像结果为{findResult}")  # 0说明没找到
                if findResult is not True:
                    text = findArg.getSimpleReadMsg() + "\n没有查到录像"
                    logger.error(text)
                    continue
            except DHNetSDKException as e:
                text = findArg.getSimpleReadMsg() + f"\n{e}"
                logger.error(text)
                continue

            downloadbytimeArg = UnifyDownLoadByTimeArg()
            downloadbytimeArg.channel = channel
            downloadbytimeArg.saveFilePath = downloadArg.savePath
            downloadbytimeArg.startTime = downloadArg.downloadTime
            downloadbytimeArg.stopTime = downloadArg.downloadTime + timedelta(seconds=1)
            downLoadHandle = dahuaClient.asyncDownLoadByTime(userID, downloadbytimeArg)
            print(f"下载句柄{downLoadHandle}")
            if downLoadHandle != 0:
                with dahuaCondition:
                    downloadHandleDict[downLoadHandle] = downloadArg.savePath
                    dahuaCondition.notify()
            else:
                text = downloadbytimeArg.getSimpleReadMsg()
                text += "\n下载句柄为空，该录像下载失败"
                logger.error(text)

    stopDownInstance.producerDone()
    stopDownInstance.join(10)  # 超时10秒，

    dahuaClient.logout(userID)
    dahuaClient.logclose()
    dahuaClient.cleanup()


if __name__ == "__main__":
    main()
