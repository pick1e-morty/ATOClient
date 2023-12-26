import sys
import threading

# from pathlib import Path
# sys.path.append(str(Path(__file__).resolve().parent.parent))
from datetime import timedelta
from pathlib import Path
from time import sleep

from UnifyNetSDK import HaikangNetSDK, HKNetSDKException
from UnifyNetSDK.parameter import UnifyLoginArg, UnifyDownLoadByTimeArg, UnifyFindFileByTimeArg
from _testLoginConfig import testUserConfig

from loguru import logger

logger.remove()
logger.add(sys.stdout, level="TRACE")

haikangClient = None


# 如果不想用全局变量这种写法就需要
# 这样导入模块，我包里的__init__文件做了延迟导入，所以这个类实际会被识别为一个function，从而导致直接调用类方法失效（但实例是正常的）
# from UnifyNetSDK.haikang.hk_netsdk import HaikangNetSDK


class StopDownloadConsumer(threading.Thread):
    def __init__(self, condition: threading.Condition, downloadHandleList: list):
        threading.Thread.__init__(self)
        self.done = False
        self.condition = condition
        self.downloadHandleList = downloadHandleList

    def producerDone(self):
        self.done = True

    def run(self):
        while True:
            if not self.downloadHandleList:
                if self.done is True:  # 如果下载句柄列表为空，且生产者发出完毕信号，则跳出永真循环。
                    break
                with self.condition:  # 注意，我用了两个with condition，由于查询是个非常耗时的操作，查询的期间是不影响生产者继续添加句柄的。
                    self.condition.wait()  # 如果下载句柄列表为空，且生产者没有发出完毕信号，则线程阻塞等待。
            for downloadHandle in self.downloadHandleList:
                stopRestlt = haikangClient.stopDownLoadTimer(downloadHandle)
                if stopRestlt == 100:
                    with self.condition:  # 下载成功后就可以删掉这个句柄了
                        self.downloadHandleList.pop(self.downloadHandleList.index(downloadHandle))
                # 可是如果下载结果一直不为true呢，句柄就噶了，而且也不能获取对应的失败原因。print的信息很不理想
                # 如果真的存在这种情况，就需要把查询和关闭功能写到这里，然后才能获取真正失败的原因。
                # 这部分暂时不写。
            sleep(0.5)


def main():
    global haikangClient
    haikangClient = HaikangNetSDK()
    haikangClient.init()
    absLogPath = Path(__file__).absolute().with_name('hk_netsdk_log')
    haikangClient.logopen(absLogPath)

    easy_login_info = UnifyLoginArg()
    easy_login_info.userName = testUserConfig.devUserName
    easy_login_info.userPassword = testUserConfig.devPassword
    easy_login_info.devicePort = testUserConfig.devPort
    easy_login_info.deviceAddress = testUserConfig.devIP

    userID, device_info = haikangClient.login(easy_login_info)
    print("硬盘数量", device_info.struDeviceV30.byDiskNum)

    haikangCondition = threading.Condition()
    downloadHandleList = []
    stopDownInstance = StopDownloadConsumer(haikangCondition, downloadHandleList)
    stopDownInstance.start()

    for channel, downloadArgList in testUserConfig.downloadArgDict.items():
        for downloadArg in downloadArgList:
            findArg = UnifyFindFileByTimeArg()
            findArg.channel = channel
            findArg.startTime = downloadArg.downloadTime
            findArg.stopTime = downloadArg.downloadTime + timedelta(seconds=1)
            try:
                findResult = haikangClient.syncFindFileByTime(userID, findArg)  # 这个查询最高居然可达780ms，过分。上层还是用两套代码吧，海康的查询能做异步的，那就让他异步。不然代价太高了
                print(f"查找录像结果为{findResult}")  # 0说明没找到
                if findResult is not True:
                    text = findArg.getSimpleReadMsg() + "\n没有查到录像"
                    logger.error(text)
                    continue
            except HKNetSDKException as e:
                text = findArg.getSimpleReadMsg() + f"\n{e}"
                logger.error(text)
                continue

            downloadbytimeArg = UnifyDownLoadByTimeArg()
            downloadbytimeArg.channel = channel
            downloadbytimeArg.saveFilePath = downloadArg.savePath
            downloadbytimeArg.startTime = downloadArg.downloadTime
            downloadbytimeArg.stopTime = downloadArg.downloadTime + timedelta(seconds=1)
            downLoadHandle = haikangClient.asyncDownLoadByTime(userID, downloadbytimeArg)
            print(f"下载句柄{downLoadHandle}")
            if downLoadHandle != -1:  # 海康规定下载函数返回的不是-1，就是成功了
                with haikangCondition:
                    downloadHandleList.append(downLoadHandle)
                    haikangCondition.notify()
            else:
                text = downloadbytimeArg.getSimpleReadMsg()
                text += "\n下载句柄为空，该录像下载失败"
                logger.error(text)

    stopDownInstance.producerDone()
    stopDownInstance.join(10)  # 超时10秒，

    haikangClient.logout(userID)
    haikangClient.logclose()
    haikangClient.cleanup()


if __name__ == "__main__":
    main()
