import multiprocessing
import sys
from pathlib import Path

from loguru import logger

from app.utils.project_path import PROJECT_ROOT_PATH

sys.path.append(str(Path(__file__).absolute().parent.parent))  # 在vscode里不会自动追加项目根目录为pythonpath

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
from app.main_window.main_window import MainWindow

logger.remove()
logger.add(sys.stdout, level="DEBUG")
logFilePath = str(PROJECT_ROOT_PATH / "main.log")
logger.add(logFilePath, encoding="utf-8", enqueue=True, rotation="500MB", compression="zip", retention="10 days")

# "main.log"：指定日志文件的路径和名称。
# encoding="utf-8"：指定日志文件的编码格式为UTF-8。
# enqueue=True：将日志消息放入队列中，以异步方式写入日志文件。
# rotation="500MB"：设置日志文件的大小限制为500MB，超过限制后将自动创建新文件进行日志轮转。
# compression="zip"：使用zip压缩算法对日志文件进行压缩。
# retention="10 days"：设置日志文件的保留时间为10天，超过时间将自动删除。

if __name__ == '__main__':
    multiprocessing.freeze_support()
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    app = QApplication(sys.argv)
    forms = MainWindow()
    forms.show()
    # __desktopPath = os.path.join(os.path.expanduser('~'), 'Desktop')
    # testFile = os.path.join(__desktopPath, "0314.xlsx")
    # __filePath2 = os.path.join(__desktopPath, "0313.xlsx")
    # forms.epwInterface.addFilePathsToexcelFile_LWData([__filePath2, testFile])
    # forms.epwInterface.addFilePathsToexcelFile_LWData([testFile])

    sys.exit(app.exec_())

# 现在的文件体积是200mb(两个sdk的dll能占100)，7z极限压缩后是50mb

# pyinstaller --noconfirm --onedir --console --icon "C:/Users/Administrator/Documents/CodeProject/ATO/app/resource/_soft_icon.ico" --clean --runtime-hook "C:/Users/Administrator/Documents/CodeProject/ATO/hook.py" --add-data "C:/Users/Administrator/Documents/CodeProject/ATO/app/AppData;AppData/" --collect-binaries "UnifyNetSDK" --add-data "C:/Users/Administrator/Documents/CodeProject/ATO/app/main_window/resource;app/main_window/resource/" --add-data "C:/Users/Administrator/Documents/CodeProject/ATO/app/app_setting_widget/resource;app/app_setting_widget/resource/"  "C:/Users/Administrator/Documents/CodeProject/ATO/app/ATO.py"
# pyinstaller --noconfirm --onedir --windowed --icon "C:/Users/Administrator/Documents/CodeProject/ATO/app/resource/_soft_icon.ico" --clean --runtime-hook "C:/Users/Administrator/Documents/CodeProject/ATO/hook.py" --add-data "C:/Users/Administrator/Documents/CodeProject/ATO/app/AppData;AppData/" --collect-binaries "UnifyNetSDK" --add-data "C:/Users/Administrator/Documents/CodeProject/ATO/app/main_window/resource;app/main_window/resource/" --add-data "C:/Users/Administrator/Documents/CodeProject/ATO/app/app_setting_widget/resource;app/app_setting_widget/resource/"  "C:/Users/Administrator/Documents/CodeProject/ATO/app/ATO.py"

# --noconfirm：不提示用户确认配置选项。
# --onedir：打包生成的可执行文件放在一个目录下。
# --console：生成控制台模式的可执行文件。
# --icon：指定应用程序的图标。
# --clean：清除之前构建的文件。
# --runtime-hook：指定运行时钩子脚本。
# --add-data：添加数据文件到打包生成的可执行文件中。
# --collect-binaries：收集依赖的二进制文件。
# --add-data：添加资源文件到打包生成的可执行文件中。


# ATO-v1.0.0_x64_Portable.7z
