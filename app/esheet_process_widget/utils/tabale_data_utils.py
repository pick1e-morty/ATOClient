from datetime import datetime
from pathlib import Path
from loguru import logger
from typing import List, Union, Dict

from app.esheet_process_widget.epw_define import ExcelDataTableWidgetItemDataStruct, \
    SameYTCountTableWidgetItemDataStruct, YTCTFEnum, YTConfigDataStruct
from openpyxl import load_workbook
from openpyxl.utils.exceptions import InvalidFileException
from collections import Counter


class TableDataUtilsException(Exception):

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class DevConfigFileNotFoundError(TableDataUtilsException):
    """
    自定义异常类，用于标记设备配置文件不存在的情况
    """

    def __init__(self, message="设备配置文件不存在，整个文件路径最好是英文的且绝对不能带有空格"):
        self.message = message
        super().__init__(self.message)


class DevConfigFileInvalidError(TableDataUtilsException):
    """
    自定义异常类，用于标记设备配置文件格式不正确的情况
    """

    def __init__(self, message="设备配置文件格式错误，整个文件路径最好是英文的且绝对不能带有空格"):
        self.message = message
        super().__init__(self.message)


class FileContentIsEmptyException(TableDataUtilsException):
    """
    自定义异常类，用于标记要处理的文件是空的情况
    """

    def __init__(self, message="要处理的数据文件为空"):
        self.message = message
        super().__init__(self.message)


class DevConfigFileContentIsEmptyException(TableDataUtilsException):
    """
    自定义异常类，用于标记配置文件是空的情况
    """

    def __init__(self, message="设备配置文件为空"):
        self.message = message
        super().__init__(self.message)


class DevConfigFileContentIsInvalidException(TableDataUtilsException):
    """
    自定义异常类，用于标记配置文件中的数值有误的情况
    """

    def __init__(self, message="设备配置文件数值有误"):
        self.message = message
        super().__init__(self.message)


def is_instance_variables_has_empty(instance):
    # 判断类实例的变量有没有空的。excel中，只要用户操作过这个单元格再删除，就算是空的也会返回"None"
    for attr_name in dir(instance):
        if not attr_name.startswith('__'):  # 排除掉Python内置的特殊方法或属性
            attr_value = getattr(instance, attr_name)
            if attr_value is None or attr_value == "" or attr_value == "None":
                return True


def getExcelDataTableWidgetData(filePath: str, shipid_CID: str = None, scantime_CID: str = None, ytname_CID: str = None, scantimeformat: str = None) -> List[ExcelDataTableWidgetItemDataStruct]:
    # 返回excel表格中指定列的数据

    # [[默认格式]]
    # 单号列 = A
    # 月台号列 = AB
    # 扫描时间列 = AD
    # 扫描时间格式 = %Y-%m-%d %H:%M:%S
    shipID_CID = "A" if shipid_CID is None else shipid_CID
    scanTime_CID = "AD" if scantime_CID is None else scantime_CID
    ytName_CID = "AB" if ytname_CID is None else ytname_CID
    scanTimeFormat = "%Y-%m-%d %H:%M:%S" if scantimeformat is None else scantimeformat

    wb = load_workbook(filePath)

    ws = wb.active  # 获取当前活跃的sheet,默认是第一个sheet
    logInfoText = "\n" + shipID_CID + "列表头为:" + str(ws[shipID_CID][0].value) \
                  + "\n" + scanTime_CID + "列表头为:" + str(ws[scanTime_CID][0].value) \
                  + "\n" + ytName_CID + "列表头为:" + str(ws[ytName_CID][0].value)
    logger.info(logInfoText + "\n注意检查表头数据是否正确")

    ws.delete_rows(1)  # 删除第一行标题
    shipIDList = [cell.value for cell in ws[shipID_CID]]  # 获取单号列数据
    scanTimeList = [cell.value for cell in ws[scanTime_CID]]  # 扫描时间列数据
    ytNameList = [cell.value for cell in ws[ytName_CID]]  # 月台号列数据
    wb.close()  # 用完立即就关掉
    edtw_ItemDataList = []

    for index in range(len(shipIDList)):
        temp_ItemData = ExcelDataTableWidgetItemDataStruct()
        try:
            temp_ItemData.shipID = int(shipIDList[index]) if shipIDList[index] is not None else None
            temp_ItemData.scanTime = datetime.strptime(scanTimeList[index], scanTimeFormat) if scanTimeList[index] is not None else None
            temp_ItemData.ytName = str(ytNameList[index])  # 某列数据里可能是空的
            if is_instance_variables_has_empty(temp_ItemData):
                continue
            else:
                edtw_ItemDataList.append(temp_ItemData)
        except IndexError as errorInfo:  # 某个单元格为空，但应该不会存在这个问题的，先抓了再说吧
            logger.error(f"可能是某个单元格为空，原报错信息{errorInfo}")
            continue
        except ValueError as errorInfo:  # 一般是用户填错了列号
            logger.error(f"应该是填错了数据列号或者时间格式不对，原报错信息{errorInfo}")
            continue
    if not edtw_ItemDataList:  # 判断列表是否为空
        raise FileContentIsEmptyException(f"要处理的文件是空的，注意检查是否填错列号\n{filePath}")
    else:
        return edtw_ItemDataList


def getSameYTCountTableWidgetData(edtw_ItemDataList: List[ExcelDataTableWidgetItemDataStruct]) -> List[SameYTCountTableWidgetItemDataStruct]:
    # 处理getExcelDataTableWidgetData返回的数据
    # 得到 相同月台的单号总量和月台通道配置

    ytNameList = [edtw_ItemData.ytName for edtw_ItemData in edtw_ItemDataList]
    counter = Counter(ytNameList)  # 字典子类用于统计可哈希对象数量
    sameYTCount = counter.most_common()  # 最大值顺序

    # 这里拿到了单号总量和月台通道配置，应该新开一个list

    sytctw_ItemDataList = []
    # config_generate = YtBindDevConfigGenerate()   # 已经做全局保活了，这边就不开了
    for yt, shipCount in sameYTCount:
        temp_ItemDataList = SameYTCountTableWidgetItemDataStruct()
        temp_ItemDataList.ytName = yt
        temp_ItemDataList.shipCount = shipCount
        temp_ItemDataList.devChannel = __config_generate.send(yt)  # 向生成器发送月台名称
        next(__config_generate)  # 驱动生成器执行到ytName = yield，以便接收下一个月台名称
        sytctw_ItemDataList.append(temp_ItemDataList)
    return sytctw_ItemDataList


def getYtConfigFromConfigFile(devConfigFilePath: Union[Path, str] = None) -> Dict[str, YTConfigDataStruct]:
    # 从配置文件中读取月台配置
    devConfigFilePath = Path(__file__).parent.parent.parent / "AppData/月台配置.xlsx" if devConfigFilePath is None else devConfigFilePath
    # 如果用户没传地址，就用缺省的
    try:
        wb = load_workbook(str(devConfigFilePath))  # 打开配置文件
    except InvalidFileException:
        raise DevConfigFileInvalidError(f"设备配置文件格式错误或文件路径有误，确保文件格式为xlsx或xls及文件路径中不能含有空格\n{str(devConfigFilePath)}")
    except FileNotFoundError:
        raise DevConfigFileNotFoundError(f"设备配置文件不存在，确保文件格式为xlsx或xls及文件路径中不能含有空格\n{str(devConfigFilePath)}")
    ws = wb.active  # 获取活动表
    ws.delete_rows(1)  # 删除第一行标题
    ytList = [cell.value for cell in ws[YTCTFEnum.YT.value]]  # 月台列数据
    devTypeList = [cell.value for cell in ws[YTCTFEnum.devType.value]]  # 设备类型列数据
    devIPList = [cell.value for cell in ws[YTCTFEnum.devIP.value]]  # 设备IP列数据
    devChannelList = [cell.value for cell in ws[YTCTFEnum.devChannel.value]]  # 设备通道列数据
    devPortList = [cell.value for cell in ws[YTCTFEnum.devPort.value]]  # 设备端口列数据
    devUserNameList = [cell.value for cell in ws[YTCTFEnum.devUserName.value]]  # 设备用户名列数据
    devPasswordList = [cell.value for cell in ws[YTCTFEnum.devPassword.value]]  # 设备密码列数据
    wb.close()  # 关闭配置文件
    ytConfigList = {}
    for index in range(len(ytList)):
        temp_ytConfig = YTConfigDataStruct()
        try:
            temp_ytConfig.yt = str(ytList[index])
            temp_ytConfig.devType = str(devTypeList[index])
            temp_ytConfig.devIP = str(devIPList[index])
            # int方法不能接None，所以要提前判断一下，如果是None就让is_instance_variables_has_empty去处理
            temp_ytConfig.devChannel = int(devChannelList[index]) if devChannelList[index] is not None else None
            temp_ytConfig.devPort = int(devPortList[index]) if devPortList[index] is not None else None
            temp_ytConfig.devUserName = str(devUserNameList[index])
            temp_ytConfig.devPassword = str(devPasswordList[index])
            if is_instance_variables_has_empty(temp_ytConfig):  # 跳过有空值的配置行
                continue
            else:
                ytConfigList[temp_ytConfig.yt] = temp_ytConfig
        except IndexError as errorInfo:  # 某个单元格为空，但应该不会存在这个问题的，先抓了再说吧
            logger.error(f"可能是某个单元格为空，原报错信息{errorInfo}")
            continue
        except ValueError as errorInfo:  # 配置表中数值有误，应该是填错位置了
            logger.error(f"应该是配置信息填错位置了，原报错信息{errorInfo}")
            continue

    if ytConfigList:  # 判断列表是否为空
        return ytConfigList
    else:
        raise DevConfigFileContentIsEmptyException(f"设备配置文件是空的，注意检查是否填错格式\n{filePath}")


def YtBindDevConfigGenerate():
    # 获取月台绑定的HCVR设备配置信息
    ytBindConfigDict = getYtConfigFromConfigFile()  # 读取设备配置表
    while True:
        ytName = yield
        try:
            temp_ytConfig = ytBindConfigDict[ytName]
            dev_ip_channel = f"{temp_ytConfig.devIP}-{str(temp_ytConfig.devChannel)}"
        except KeyError:
            dev_ip_channel = "未配置"
        yield dev_ip_channel


__config_generate = YtBindDevConfigGenerate()  # 全局变量保活
next(__config_generate)  # 启动生成器

if __name__ == "__main__":
    __devConfigFilePath = Path(__file__).parent.parent.parent / "AppData/月台配置.xlsx"
    print(getYtConfigFromConfigFile(__devConfigFilePath))
    pass
