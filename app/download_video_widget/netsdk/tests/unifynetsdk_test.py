from UnifyNetSDK import HaikangNetSDK, DaHuaNetSDK
from UnifyNetSDK.parameter import UnifyLoginArg, UnifyFindFileByTimeArg, UnifyDownLoadByTimeArg

from datetime import datetime, timedelta
from pathlib import Path

# 这是两套同步下载的代码，可以改一下，只更改实例的那一行代码，测试那个非注释那个


def test_dahua_download():
    easy_login_info = UnifyLoginArg()
    easy_login_info.userName = "admin"
    easy_login_info.userPassword = "admin"
    easy_login_info.devicePort = 37777
    easy_login_info.deviceAddress = "10.10.10.10"

    dahuaClient = DaHuaNetSDK()
    dahuaClient.init()

    userID, device_info = dahuaClient.login(easy_login_info)
    print("硬盘数量", device_info.stuDeviceInfo.nDiskNum)

    两分钟前 = datetime.now() - timedelta(seconds=120)
    一分钟前 = datetime.now() - timedelta(seconds=60)

    findArg = UnifyFindFileByTimeArg()
    findArg.channel = 31
    findArg.startTime = 两分钟前
    findArg.stopTime = 一分钟前
    findResult = dahuaClient.syncFindFileByTime(userID, findArg)
    print(f"查找结果{findResult}")

    downArg = UnifyDownLoadByTimeArg()
    downArg.channel = 31
    downArg.saveFilePath = Path.cwd() / "test.mp4"
    downArg.startTime = 两分钟前
    downArg.stopTime = 一分钟前

    try:
        downLoadResult = dahuaClient.syncDownLoadByTime(userID, downArg)
        print(f"下载结果{downLoadResult}")
    except Exception as e:
        print(e)
    dahuaClient.logout(userID)
    dahuaClient.cleanup()


def test_haikang_download():
    easy_login_info = UnifyLoginArg()
    easy_login_info.userName = "admin"
    easy_login_info.userPassword = "admin"
    easy_login_info.devicePort = 8000
    easy_login_info.deviceAddress = "10.10.10.10"

    hkClient = HaikangNetSDK()
    hkClient.init()
    userID, device_info = hkClient.login(easy_login_info)
    print("硬盘数量", device_info.struDeviceV30.byDiskNum)

    两分钟前 = datetime.now() - timedelta(seconds=120)
    一分钟前 = datetime.now() - timedelta(seconds=60)

    findArg = UnifyFindFileByTimeArg()
    findArg.channel = 1
    findArg.startTime = 两分钟前
    findArg.stopTime = 一分钟前
    findResult = hkClient.syncFindFileByTime(userID, findArg)
    print(f"查找结果{findResult}")

    downArg = UnifyDownLoadByTimeArg()
    downArg.channel = 1
    downArg.saveFilePath = Path.cwd() / "test.mp4"

    downArg.startTime = 两分钟前
    downArg.stopTime = 一分钟前

    downLoadResult = hkClient.syncDownLoadByTime(userID, downArg)
    print(f"下载结果{downLoadResult}")

    hkClient.logout(userID)

    hkClient.cleanup()


if __name__ == "__main__":
    # test_dahua_download()
    test_haikang_download()
