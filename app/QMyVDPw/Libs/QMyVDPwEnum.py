import os.path
from enum import Enum


# class VRCETEnum(Enum):
#     # 视频录像机配置表枚举 Video Rrcord Configuration Excel Table
#     IP = 0  # 录像机Ip
#     HTTPPort = 1  # HTTP端口
#     USERNAME = 2  # 用户名
#     PASSWORD = 3  # 密码


class YTCETEnum(Enum):
    # 月台配置表枚举 YTConfiguration Excel Table
    YTCOLUMN = 0  # 月台列
    IP = 1  # 录像机Ip
    CHANNEL = 2  # 通道
    PORT = 3  # 端口
    USERNAME = 4  # 用户名
    PASSWORD = 5  # 密码

    # ASSEMBLYLINERANGE = 7  # 流水线体范围
    # BEDPLATERANGE = 8  # 称台范围
    # BEDPLATECENTER = 9  # 称台中心


class SHTWEnum(Enum):
    # shipHandle TableWidget 枚举
    # 当然 枚举学C协定要大写，"受益"于python库的使用方式VDPwEnum.Channel这样也能很好的说明枚举
    HCVRIP = 0  # 录像机IP
    Channel = 1  # 通道
    YT = 2  # 月台
    Folder = 3  # 文件夹
    FileName = 4  # 文件名
    DLTime = 5  # 下载时间
    DLDuration = 6  # down load duration 下载时长
    _HCVRConfig = 7  # 录像机配置
    # 7有点特殊 它不显示在组件上 而是item的一个隐藏data

class DataForDownloadListEnum(Enum):
    # 用于下载的数据参数枚举
    IPText = 0          # 用于对比ip的文本
    DevicesConfig = 1   # 设备配置列表的枚举索引位置
    ShipIDs = 2         # 所有单号的列表枚举索引

class DownloadParmeterListEnum(Enum):
    # 就是ShipIDs这个列表中的列表的元素枚举索引
    Channel = 0
    StartTime =1
    EndTime = 2
    FileAbsPath = 3

class DownloadDurationText2TimeSec(Enum):
    # 下载时长文本转时间秒数 我在数据那边传的的文本的数值 并不是整数 所以这边需要做一个转换
    一秒视频 = 1
    五秒视频 = 5
    十秒视频 = 10
