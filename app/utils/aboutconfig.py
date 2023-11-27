from pathlib import Path
from configobj import ConfigObj

# 开始读配置
__configFilePath = Path(__file__).parent.parent / "AppData/config.ini"
configini = ConfigObj(str(__configFilePath), encoding="UTF8")
