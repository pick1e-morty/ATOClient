import datetime
from pathlib import Path
from typing import Dict
from app.download_video_widget.dvw_define import DevLoginAndDownloadArgSturct, DownloadArg

import random


# 一个函数，随即返回返回7个数字的字符串
def random7():
    return "".join([str(random.randint(0, 9)) for i in range(7)])


# 一个函数，随机返回1-10天前的某一小时某一分钟某一秒，datetime类型的
def randomTime():
    return datetime.datetime.now() - datetime.timedelta(days=random.randint(1, 10), hours=random.randint(0, 23), minutes=random.randint(0, 59), seconds=random.randint(0, 59))


testUserConfig = DevLoginAndDownloadArgSturct()
testUserConfig.devType = "dahua"
testUserConfig.devIP = "10.30.15.216"
testUserConfig.devPort = 30216
testUserConfig.devUserName = "admin"
testUserConfig.devPassword = "ydfb450000"

# testUserConfig.devType = "haikang"
# testUserConfig.devIP = "10.200.15.41"
# testUserConfig.devPort = 8000
# testUserConfig.devUserName = "admin"
# testUserConfig.devPassword = "zzfb450000"
for i in range(3):
    filePath = Path(__file__).with_name(random7() + ".mp4")
    tempDownloadArg = DownloadArg(savePath=str(filePath), downloadTime=randomTime(), channel=29, ytName="YT113")
    testUserConfig.downloadArgList.append(tempDownloadArg)

if __name__ == "__main__":
    print("start")
    print(testUserConfig)
