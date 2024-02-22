import datetime
from typing import Dict


class DownloadArg(object):
    def __init__(self, channel: int = None, ytName: str = None, savePath: str = None, downloadTime: datetime.datetime = None):
        __slots__ = ['channel', 'ytName', 'savePath', 'downloadTime', 'downloadTime']
        super().__init__()
        self.channel = channel      # 通道和月台名称只需要存储一次就行了。
        self.ytName = ytName        # 如果用字典的话，那就是key是channel，然后ytName是这个字典的一个属性，但是存储文件路径和下载时间的时候就需要用append了
        self.savePath = savePath    # 那个结构复杂度，不光存储的时候难看！解析的时候更是难看上天！不能用！
        self.downloadTime = downloadTime


class DevLoginAndDownloadArgSturct(object):
    __slots__ = ['devType', 'devIP', 'devPort', 'devUserName', 'devPassword', 'downloadArgList']

    def __init__(self):
        self.devType = None  # 设备类型
        self.devIP = None  # 设备ip
        self.devPort = None  # 设备端口
        self.devUserName = None
        self.devPassword = None
        self.downloadArgList = []


if __name__ == "__main__":
    pass
