from pathlib import Path
import sys
from PyQt5.QtWidgets import QWidget, QApplication
from loguru import logger
from typing import Union, Dict

from qfluentwidgets import MessageBox, Dialog

from app.esheet_process_widget.epw_define import YTCTFEnum, YTConfigDataStruct
from openpyxl import load_workbook
from openpyxl.utils.exceptions import InvalidFileException

from app.utils.tools import is_instance_variables_has_empty


class DevConfigFileNotFoundError(Exception):
    """
    自定义异常类，用于标记设备配置文件不存在的情况
    """

    def __init__(self, message="设备配置文件不存在，整个文件路径最好是英文的且绝对不能带有空格"):
        self.message = message
        super().__init__(self.message)


class DevConfigFileInvalidError(Exception):
    """
    自定义异常类，用于标记设备配置文件格式不正确的情况
    """

    def __init__(self, message="设备配置文件格式错误，整个文件路径最好是英文的且绝对不能带有空格"):
        self.message = message
        super().__init__(self.message)


class DevConfigFileContentIsEmptyException(Exception):
    """
    自定义异常类，用于标记配置文件是空的情况
    """

    def __init__(self, message="设备配置文件为空"):
        self.message = message
        super().__init__(self.message)


class DevConfigFileContentIsInvalidException(Exception):
    """
    自定义异常类，用于标记配置文件中的数值有误的情况
    """

    def __init__(self, message="设备配置文件数值有误"):
        self.message = message
        super().__init__(self.message)


def getYtConfigFromConfigFile(devConfigFilePath: Union[Path, str] = None) -> Dict[str, YTConfigDataStruct]:
    # 从配置文件中读取月台配置
    devConfigFilePath = Path(__file__).parent.parent / "AppData/月台配置.xlsx" if devConfigFilePath is None else devConfigFilePath
    # 如果用户没传地址，就用缺省的
    try:
        wb = load_workbook(str(devConfigFilePath))  # 打开配置文件
    except InvalidFileException:
        raise DevConfigFileInvalidError(f"设备配置文件格式错误或文件路径有误，确保文件格式为xlsx或xls及文件路径中不能含有空格\n{str(devConfigFilePath)}")
    except FileNotFoundError:
        raise DevConfigFileNotFoundError(f"设备配置文件不存在，确保文件格式为xlsx或xls及文件路径中不能含有空格\n{str(devConfigFilePath)}")
    ws = wb.active  # 获取活动表，如果用户改变了默认的激活表，那这里也是会出错的地方，到时候会报配置文件为空
    ws.delete_rows(1)  # 删除第一行标题
    ytList = [cell.value for cell in ws[YTCTFEnum.YT.value]]  # 月台列数据
    devTypeList = [cell.value for cell in ws[YTCTFEnum.devType.value]]  # 设备类型列数据
    devIPList = [cell.value for cell in ws[YTCTFEnum.devIP.value]]  # 设备IP列数据
    devChannelList = [cell.value for cell in ws[YTCTFEnum.devChannel.value]]  # 设备通道列数据
    devPortList = [cell.value for cell in ws[YTCTFEnum.devPort.value]]  # 设备端口列数据
    devUserNameList = [cell.value for cell in ws[YTCTFEnum.devUserName.value]]  # 设备用户名列数据
    devPasswordList = [cell.value for cell in ws[YTCTFEnum.devPassword.value]]  # 设备密码列数据
    wb.close()  # 用完就关
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
            raise DevConfigFileContentIsInvalidException(f"可能是某个单元格为空，原报错信息\n{errorInfo}")
        except ValueError as errorInfo:  # 配置表中数值有误，应该是填错位置了
            logger.error(f"应该是配置信息填错位置了，原报错信息{errorInfo}")
            raise DevConfigFileContentIsInvalidException(f"应该是配置信息填错位置了，原报错信息\n{errorInfo}")

    if ytConfigList:  # 判断列表是否为空
        return ytConfigList
    else:
        raise DevConfigFileContentIsEmptyException(f"设备配置文件是空的，注意检查是否填错格式\n{devConfigFilePath}")


def YtBindDevConfigGenerate():
    # 这是一个生成器，用于获取月台绑定的设备配置信息
    # 上层用send发送月台索引到这，查到之后把配置yield出去
    ytBindConfigDict = getYtConfigFromConfigFile()  # 读取设备配置表
    while True:
        ytName = yield
        ytConfig = ytBindConfigDict.get(ytName, None)
        yield ytConfig


try:
    devConfigGenerate = YtBindDevConfigGenerate()  # 全局变量保活
    next(devConfigGenerate)  # 启动生成器
except (DevConfigFileNotFoundError, DevConfigFileInvalidError, DevConfigFileContentIsEmptyException, DevConfigFileContentIsInvalidException) as ErrorText:  # 设备配置文件路径是写的相对的，写在处理函数中的，可能会出现点问题吧
    logger.error(str(ErrorText))
    devConfigGenerate = str(ErrorText)
