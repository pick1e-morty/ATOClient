from enum import Enum


class DownloadParameterDataStruct(object):
    # EPW窗体中，ExcelDataTableWidget的item数据结构体
    # 中间那个表格组件
    __slots__ = ['shipID', 'ytName', 'scanTime']  # 禁止添加其他的实例变量

    def __init__(self, shipID: int = None, scanTime: datetime.datetime = None, ytName: str = None):
        self.shipID = shipID
        self.ytName = ytName
        self.scanTime = scanTime



# 最终传给SDK的


# 需要先按照月台取一边，然后才能和需要按照设备IP再进行一次分类

# 登陆需要参数，固定不可变
self.devIP = devIP
self.devType = devType
self.devPort = devPort
self.devUserName = devUserName
self.devPassword = devPassword
# 下载需要参数，这是一个list
self.devChannel = devChannel        # 通道
self.saveFilePath =saveFilePath # 保存文件路径，拿基准路径(pics)加文件名作为子级文件夹，最后加单号.jpg
self.downloadTime =downloadTime # 下载时间



