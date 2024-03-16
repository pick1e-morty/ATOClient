from pathlib import Path
from configobj import ConfigObj
from configobj.validate import Validator, ValidateError, is_list, VdtTypeError, VdtValueError


def is_list_of_digit_strings(value):
    # 定义一个验证规则，要求"月台保留数量列表"必须是一个数字字符串列表
    # 首先检查值是否是一个列表
    if not is_list(value):
        raise VdtTypeError(f"这个参数需要是一个列表[{value}]")
    # 然后检查列表中的每个元素是否是数字字符串
    for item in value:
        if not item.isdigit():
            raise VdtValueError(f"这个参数需要是一个数字[{value}]")
    # 如果所有的检查都通过了，那么返回True
    return True


class VdtStrNotUpperError(ValidateError):
    # 自定义一个验证错误Exception类，用于raise出字符串并不全是大写字母
    def __init__(self, value):
        ValidateError.__init__(self, f"这个参数需要是大写字母[{value}]")


def is_string_all_upper(value):
    # 定义一个验证规则函数，要求value必须是一个全大写的字符串
    if not isinstance(value, str):
        raise VdtTypeError(f"这个参数需要是文本字符[{value}]")
    for i in value:
        if not i.isupper():
            raise VdtStrNotUpperError(value)
    return True


class VdtDateTimeFormatError(ValidateError):
    # 自定义一个验证错误Exception类，用于raise出字符串中的日期时间格式化代码错误
    def __init__(self, value):
        ValidateError.__init__(self, f"这段字符串中的日期时间格式化代码有误\n[{value}]")


def contains_valid_format_codes(input_string):
    format_codes = set('Y y m d H I p M S f A a B b Z z j U W w'.split())
    # 分割字符串，找到每个%后面的字母
    code_parts = input_string.split('%')
    # 检查每个代码部分是否在format_codes集合中
    for part in code_parts[1:]:  # 从第二个部分开始，因为第一个部分不包含格式代码
        if part[0] not in format_codes:
            raise VdtDateTimeFormatError(code_parts)
    return True


def getFormsConfigDict(a_configFilePath=None):
    __configFilePath = Path(__file__).parent.with_name("AppData") / "config.ini" if a_configFilePath is None else a_configFilePath
    try:
        formsConfigObj = ConfigObj(str(__configFilePath), encoding="UTF8", file_error=True, raise_errors=True)
    except OSError as errorText:
        errorText = f"界面配置文件不存在，整个文件路径最好是英文的且绝对不能带有空格\n原报错信息{errorText}"
        raise OSError(errorText)

    check_epw_config(formsConfigObj)

    return formsConfigObj


def check_dvw_config(formsConfigObj: ConfigObj):
    pass


def check_epw_config(formsConfigObj: ConfigObj):
    # 检查epw配置是否符合要求
    vtor = Validator()
    vtor.functions['list_of_digit_strings'] = is_list_of_digit_strings
    vtor.functions['is_string_all_upper'] = is_string_all_upper
    vtor.functions['contains_valid_format_codes'] = contains_valid_format_codes

    epwConfig = formsConfigObj["epw"]
    keepShipNumInYtList = epwConfig["月台保留数量列表"]
    vtor.check('list_of_digit_strings', keepShipNumInYtList)

    autoDeleteUnConfiguredYt = epwConfig["自动删除未配置月台"]
    vtor.check('boolean', autoDeleteUnConfiguredYt)

    shiID_CID = epwConfig["自定义格式"]["单号列"]
    scanTime_CID = epwConfig["自定义格式"]["扫描时间列"]
    yt_CID = epwConfig["自定义格式"]["月台号列"]
    vtor.check('is_string_all_upper', shiID_CID)
    vtor.check('is_string_all_upper', scanTime_CID)
    vtor.check('is_string_all_upper', yt_CID)

    scanTimeFormat = epwConfig["自定义格式"]["扫描时间格式"]
    vtor.check('contains_valid_format_codes', scanTimeFormat)


if __name__ == "__main__":
    pass
