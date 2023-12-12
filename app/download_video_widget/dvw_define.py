import datetime


class DownloadArg(object):
    def __init__(self, savePath: str = None, downloadTime: datetime.datetime = None):
        self.savePath = savePath
        self.downloadTime = downloadTime


class DevLoginAndDownloadArgSturct(object):
    __slots__ = ['devType', 'devPort', 'devUserName', 'devPassword', 'downloadArg']

    def __init__(self):
        self.devType = None
        self.devPort = None
        self.devUserName = None
        self.devPassword = None
        self.downloadArg = {}
