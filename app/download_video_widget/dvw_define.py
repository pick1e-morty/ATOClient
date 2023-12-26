import datetime
from typing import Dict


class DownloadArg(object):
    def __init__(self, savePath: str = None, downloadTime: datetime.datetime = None):
        self.savePath = savePath
        self.downloadTime = downloadTime


class DevLoginAndDownloadArgSturct(object):
    __slots__ = ['devType', 'devIP', 'devPort', 'devUserName', 'devPassword', 'downloadArg']

    def __init__(self):
        self.devType = None  # 设备类型
        self.devIP = None  # 设备ip
        self.devPort = None  # 设备端口
        self.devUserName = None
        self.devPassword = None
        # self.downloadArg = Dict[int, DownloadArg]  # {channel:DownloadArg}
        # 上面这样的typing是有问题的，会导致这个属性不能修改，readonly？
        self.downloadArg = {}  # {channel:DownloadArg}
