import datetime
from enum import Enum
from typing import Dict


class DownloadArg(object):
    def __init__(
        self,
        channel: int = None,
        ytName: str = None,
        savePath: str = None,
        downloadTime: datetime.datetime = None,
    ):
        __slots__ = ["channel", "ytName", "savePath", "downloadTime", "downloadTime"]
        super().__init__()
        self.channel = channel  # 通道和月台名称只需要存储一次就行了。
        self.ytName = ytName  # 如果用字典的话，那就是key是channel，然后ytName是这个字典的一个属性，但是存储文件路径和下载时间的时候就需要用append了
        self.savePath = savePath  # 那个结构复杂度，不光存储的时候难看！解析的时候更是难看上天！不能用！
        self.downloadTime = downloadTime


class DevLoginAndDownloadArgStruct(object):
    __slots__ = [
        "devType",
        "devIP",
        "devPort",
        "devUserName",
        "devPassword",
        "downloadArgList",
    ]

    def __init__(self):
        self.devType = None  # 设备类型
        self.devIP = None  # 设备ip
        self.devPort = None  # 设备端口
        self.devUserName = None  # 用户名
        self.devPassword = None  # 密码
        self.downloadArgList = []  # 下载参数列表，元素是DownloadArg组成的

    def copy_from(self, other, keepDownloadArgListEmpty=True):
        self.devType = other.devType
        self.devIP = other.devIP
        self.devPort = other.devPort
        self.devUserName = other.devUserName
        self.devPassword = other.devPassword
        if keepDownloadArgListEmpty:
            self.downloadArgList = []
        else:
            self.downloadArgList = other.downloadArgList.copy()


class DVWTableWidgetEnum(Enum):
    """
    用于区分表格组件的枚举
    """

    DOWNLOAD_STATUS_TABLE = 0  # 下载状态表格
    DOWNLOAD_PROGRESS_TABLE = 1  # 下载进度表格


# class DownloadStatusItemTextStruct(object):
#     __slots__ = ['devIP', 'channel', 'ytName', 'filePath', 'downloadTime', 'downloadStatus']
#
#     def __init__(self):
#         self.devIP = None
#         self.channel = None
#         self.ytName = None
#         self.filePath = None
#         self.downloadTime = None
#         self.downloadStatus = None


if __name__ == "__main__":
    pass
