import datetime
from pathlib import Path
from typing import Dict


class DownloadArg(object):
    def __init__(self, savePath: str = None, downloadTime: datetime.datetime = None):
        self.savePath = savePath
        self.downloadTime = downloadTime


class DevLoginAndDownloadArgSturct(object):
    __slots__ = ['devType', 'devIP', 'devPort', 'devUserName', 'devPassword', 'downloadArgDict']

    def __init__(self):
        self.devType = None  # 设备类型
        self.devIP = None  # 设备ip
        self.devPort = None  # 设备端口
        self.devUserName = None
        self.devPassword = None
        # self.downloadArg = Dict[int, DownloadArg]  # {channel:DownloadArg}
        # 上面这样的typing是有问题的，会导致这个属性不能修改，readonly？
        self.downloadArgDict = {}  # {channel:DownloadArg}


import random


# 一个函数，随即返回返回7个数字的字符串
def random7():
    return "".join([str(random.randint(0, 9)) for i in range(7)])


# 一个函数，随机返回1-10天前的某一小时某一分钟某一秒，datetime类型的
def randomTime():
    return datetime.datetime.now() - datetime.timedelta(days=random.randint(1, 10), hours=random.randint(0, 23), minutes=random.randint(0, 59), seconds=random.randint(0, 59))


# 生成下载参数
genDownloadArg = {}
for i in range(10):
    filePath = Path(__file__).with_name(random7() + ".mp4")
    tempDownloadArg = DownloadArg(str(filePath), randomTime())
    genDownloadArg[29] = genDownloadArg.get(29, []) + [tempDownloadArg]
    # filePath = Path(__file__).with_name(random7())
    # tempDownloadArg = DownloadArg(str(filePath), randomTime())
    # genDownloadArg[25] = genDownloadArg.get(25, []) + [tempDownloadArg]

testUserConfig = DevLoginAndDownloadArgSturct()
testUserConfig.devType = "dahua"
testUserConfig.devIP = "10.30.15.216"
testUserConfig.devPort = 80
testUserConfig.devUserName = "admin"
testUserConfig.devPassword = "ydfb450000"

# testUserConfig.devType = "haikang"
# testUserConfig.devIP = "10.200.15.41"
# testUserConfig.devPort = 8000
# testUserConfig.devUserName = "admin"
# testUserConfig.devPassword = "zzfb450000"
testUserConfig.downloadArgDict = genDownloadArg

if __name__ == "__main__":
    print("start")
    print(testUserConfig)
