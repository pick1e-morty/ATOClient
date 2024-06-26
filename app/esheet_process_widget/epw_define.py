import datetime
from enum import Enum
from typing import List


class EDTWEnum(Enum):
    # excel数据表格组件枚举 ExcelDataTableWidget
    ShipID = 0  # 单号列
    ScanTime = 1  # 扫描时间
    YT = 2  # 月台


class ExcelDataTableWidgetItemDataStruct(object):
    # EPW窗体中，ExcelDataTableWidget的item数据结构体
    # 中间那个表格组件
    __slots__ = ['shipID', 'ytName', 'scanTime']  # 禁止添加其他的实例变量

    def __init__(self, shipID: int = None, scanTime: datetime.datetime = None, ytName: str = None):
        self.shipID = shipID
        self.ytName = ytName
        self.scanTime = scanTime


class SYTTWEnum(Enum):
    # sameYTCount表格组件枚举 SameYTCountTableWidget
    YT = 0  # 月台名称
    Count = 1  # 单号数量
    Channel = 2  # 设备通道


class SameYTCountTableWidgetItemDataStruct(object):
    # EPW窗体中，sameYTCountTableWidget的item数据结构体
    # 最右边那个表格组件
    __slots__ = ['ytName', 'shipCount', 'devChannel']

    def __init__(self, ytName: str = None, shipCount: int = None, devChannel: List = None):
        self.ytName = ytName  # 月台名称
        self.shipCount = shipCount  # 单号总量
        self.devChannel = devChannel  # 整体设备配置，一个list存完了


class ExcelFileListWidgetItemDataStruct(object):
    # EPW窗体中，excelFileLW的Item数据结构体
    # 最左边的那个listWidget存取所有的数据
    __slots__ = ['edtw_ItemDataList', 'sytctw_ItemDataList', 'excelFilePath']

    def __init__(self, edtw_ItemDataList: List[ExcelDataTableWidgetItemDataStruct] = None,
                 sytctw_ItemDataList: List[SameYTCountTableWidgetItemDataStruct] = None, excelFilePath: str = None):
        self.edtw_ItemDataList = edtw_ItemDataList  # 排序后的数据
        self.sytctw_ItemDataList = sytctw_ItemDataList  # 相同月台数量
        self.excelFilePath = excelFilePath  # excel文件路径


class YTCTFEnum(Enum):
    # 月台配置表枚举 YTConfiguration Table File
    YT = 'A'  # 月台号
    devType = 'B'  # 设备厂商
    devIP = 'C'  # 设备ip
    devChannel = 'D'  # 通道
    devPort = 'E'  # 端口
    devUserName = 'F'  # 用户名
    devPassword = 'G'  # 密码

    # ASSEMBLYLINERANGE = 7  # 流水线体范围
    # BEDPLATERANGE = 8  # 称台范围
    # BEDPLATECENTER = 9  # 称台中心


class YTConfigDataStruct(object):
    # 从excel表中取配置用YTCTFEnum，在软件内部层全部只需要用YTConfigDataStruct。
    __slots__ = ['yt', 'devType', 'devIP', 'devChannel', 'devPort', 'devUserName', 'devPassword']

    def __init__(self, yt: str = None, devType: str = None, devIP: str = None,
                 devChannel: int = None, devPort: int = None, devUserName: str = None,
                 devPassword: str = None):
        self.yt = yt
        self.devType = devType
        self.devIP = devIP
        self.devChannel = devChannel
        self.devPort = devPort
        self.devUserName = devUserName
        self.devPassword = devPassword
