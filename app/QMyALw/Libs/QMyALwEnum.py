from enum import Enum


class YTcontrastTWEnum(Enum):
    shipExist = 0
    shipCoordinateName = 1
    shipCopy = 2
    YT = 3
    assemblyLineRange = 4  # 流水线范围
    weighingPlatformRange = 5  # 称台范围
    _shipFilePath = 6  # 作为第一列项目隐藏的Data jpeg的绝对文件地址
    _shipCoordinatePath = 7  #  作为第二列项目隐藏的Data Labeltxt的绝对文件路径
