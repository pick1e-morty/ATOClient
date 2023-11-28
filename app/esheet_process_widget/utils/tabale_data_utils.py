from pathlib import Path

from loguru import logger
from openpyxl import load_workbook
from typing import Iterable, List, Union

from app.esheet_process_widget.epw_define import EDTWEnum, ExcelDataTableWidgetItemDataStruct, \
    SameYTCountTableWidgetItemDataStruct, SYTTWEnum
from PyQt5.QtWidgets import QMessageBox
from openpyxl import load_workbook
from openpyxl.utils.exceptions import InvalidFileException

# from ProjectPath import YtBindHCVTFilePath
from app.QMyVDPw.Libs.QMyVDPwEnum import YTCETEnum
from collections import Counter


class TableDataUtilsException(Exception):

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class DevConfigFileNotFoundError(TableDataUtilsException):
    """
    自定义异常类，用于处理设备配置文件不存在的情况
    """

    def __init__(self, message="设备配置文件不存在，整个文件路径最好是英文的且绝对不能带有空格"):
        self.message = message
        super().__init__(self.message)


class DevConfigFileInvalidError(TableDataUtilsException):
    """
    自定义异常类，用于处理设备配置文件不存在的情况
    """

    def __init__(self, message="设备配置文件格式错误，整个文件路径最好是英文的且绝对不能带有空格"):
        self.message = message
        super().__init__(self.message)


class FileContenIsEmptyException(TableDataUtilsException):
    """
    自定义异常类，用于处理设备配置文件不存在的情况
    """

    def __init__(self, message="要处理的数据文件为空"):
        self.message = message
        super().__init__(self.message)


def getExcelDataTableWidgetData(filePath, shipidCID, scantimeCID, ytnameCID):
    """
    返回excel表格中指定列的数据
    """
    wb = load_workbook(filePath)

    ws = wb.active  # 获取当前活跃的sheet,默认是第一个sheet
    logInfoText = "\n" + shipidCID + "列表头为:" + str(ws[shipidCID][0].value) \
                  + "\n" + scantimeCID + "列表头为:" + str(ws[scantimeCID][0].value) \
                  + "\n" + ytnameCID + "列表头为:" + str(ws[ytnameCID][0].value)
    logger.info(logInfoText + "\n注意检查表头数据是否正确")

    ws.delete_rows(1)  # 删除第一行标题
    shipID = [cell.value for cell in ws[shipidCID]]  # 获取单号列数据
    scanTime = [cell.value for cell in ws[scantimeCID]]  # 扫描时间列数据
    ytName = [cell.value for cell in ws[ytnameCID]]  # 月台号列数据

    edtw_ItemDataList = []

    def is_empty(var):
        return var is None or var == "" or var == "None"

    for index in range(len(shipID)):
        temp_ItemData = ExcelDataTableWidgetItemDataStruct()
        try:
            temp_ItemData.shipID = str(shipID[index])
            temp_ItemData.scanTime = str(scanTime[index])  # 某列数据里可能是空的
            temp_ItemData.ytName = str(ytName[index])
            if is_empty(temp_ItemData.shipID) or is_empty(temp_ItemData.scanTime) or is_empty(temp_ItemData.ytName):
                continue
            else:
                edtw_ItemDataList.append(temp_ItemData)
        except IndexError:
            continue
    if not edtw_ItemDataList:   # 判断列表是否为空
        raise FileContenIsEmptyException
    else:
        return edtw_ItemDataList


def getSameYTCountTableWidgetData(edtw_ItemDataList: List[ExcelDataTableWidgetItemDataStruct]) -> List[SameYTCountTableWidgetItemDataStruct]:
    # 处理getExcelDataTableWidgetData返回的数据
    # 得到 相同月台的单号总量和月台通道配置

    ytNameList = [edtw_ItemData.ytName for edtw_ItemData in edtw_ItemDataList]
    counter = Counter(ytNameList)  # 字典子类用于统计可哈希对象数量
    sameYTCount = list(counter.most_common())  # 最大值顺序，顺便转成list

    # 这里拿到了单号总量和月台通道配置，应该新开一个list

    sytctw_ItemDataList = []
    devConfigFilePath = Path(__file__).parent.parent.parent / "AppData/月台配置.xlsx"
    try:
        # 判断文件是否存在
        config_generate = getYtBindHCVRConfig(devConfigFilePath)
        next(config_generate)  # 启动生成器
        for yt, shipCount in sameYTCount:
            temp_ItemDataList = SameYTCountTableWidgetItemDataStruct()
            temp_ItemDataList.ytName = yt
            temp_ItemDataList.shipCount = shipCount
            temp_ItemDataList.devChannel = config_generate.send(yt)  # 向生成器发送月台名称
            next(config_generate)  # 驱动生成器执行到ytName = yield，以便接收下一个月台名称
            sytctw_ItemDataList.append(temp_ItemDataList)
        config_generate.close()  # 手动关闭生成器
        return sytctw_ItemDataList
    except InvalidFileException:
        raise DevConfigFileInvalidError(f"设备配置文件不存在，请检查文件路径\n{devConfigFilePath}")
    except FileNotFoundError:
        raise DevConfigFileNotFoundError(f"设备配置文件格式错误，确保文件格式为xlsx或xls及文件路径中不能含有空格\n{devConfigFilePath}")


def getYtBindHCVRConfig(devConfigFilePath: Union[Path, str]):
    # 获取月台绑定的HCVR设备配置信息
    devConfigFilePath = str(devConfigFilePath)
    YtBindConfig = getYtConfigFromConfigFile(devConfigFilePath)  # 读取设备配置表
    if YtBindConfig:
        # 先建立一个设备配置的月台索引列表
        YtBindConfigIndexList = [i[YTCETEnum.YTCOLUMN.value] for i in YtBindConfig]

        while True:
            ytName = yield
            录像机IP和通道 = "未配置"
            if ytName in YtBindConfigIndexList:
                # 然后这个月台名称在YtBindConfigIndexList中，
                月台相对应的配置索引 = YtBindConfigIndexList.index(ytName)
                # 则将在YtBindConfig中取出这个月台的索引
                录像机IP = YtBindConfig[月台相对应的配置索引][YTCETEnum.IP.value]
                if 录像机IP:
                    录像机通道 = YtBindConfig[月台相对应的配置索引][YTCETEnum.CHANNEL.value]
                    录像机IP和通道 = str(录像机IP) + "-" + str(录像机通道)
            logger.trace("月台号" + str(ytName) + "绑定的HCVR设备为：" + str(录像机IP和通道))
            yield 录像机IP和通道
            # 最终弹出该月台号的指定列配置信息


def getYtConfigFromConfigFile(filePath: str):
    # 从配置文件中读取月台配置

    configDataList = []
    wb = load_workbook(filePath)  # 打开配置文件
    ws = wb.active  # 获取活动表
    ws.delete_rows(1)  # 删除第一行标题

    # 取ws的最大行数
    maxRow = ws.max_row

    # 取最大列数，就是YTCETEnum的长度
    maxCol = len(YTCETEnum)

    # 从excel表格中取出maxrow行maxcol列的数据
    for row in range(1, maxRow):
        rowDataList = []
        for col in range(1, maxCol + 1):  # 这个
            rowDataList.append(ws.cell(row=row, column=col).value)
        else:  # 如果for中有break，则else不执行
            # logger.debug("从配置文件中读取到的月台配置信息为：" + str(rowDataList))
            configDataList.append(rowDataList)
    logger.trace("从配置文件中读取到的月台配置信息为：" + str(configDataList))
    return configDataList


if __name__ == "__main__":
    # getYtConfigFromConfigFile()
    pass
