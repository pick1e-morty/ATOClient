from pathlib import Path
from configobj import ConfigObj

# 开始读配置
__configFilePath = Path(__file__).parent.parent / "AppData/config.ini"
try:
    formsConfigDict = ConfigObj(str(__configFilePath), encoding="UTF8", file_error=True, raise_errors=True)
except OSError as e:
    errorText = f"界面配置文件不存在，整个文件路径最好是英文的且绝对不能带有空格\n{e}"
    formsConfigDict = errorText



# 123