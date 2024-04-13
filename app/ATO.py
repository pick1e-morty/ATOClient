import os
import sys
import multiprocessing
from pathlib import Path

from loguru import logger

sys.path.append(str(Path(__file__).absolute().parent.parent))  # 在vscode里不会自动追加项目根目录为pythonpath

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
from app.main_window.main_window import MainWindow

logger.remove()
logger.add(sys.stdout, level="TRACE")

if __name__ == '__main__':
    multiprocessing.freeze_support()
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    app = QApplication(sys.argv)
    forms = MainWindow()
    forms.show()
    forms.stackWidget.setCurrentIndex(1)

    # __desktopPath = os.path.join(os.path.expanduser('~'), 'Desktop')
    # testFile = os.path.join(__desktopPath, "0314.xlsx")
    # __filePath2 = os.path.join(__desktopPath, "0313.xlsx")
    # forms.epwInterface.addFilePathsToexcelFile_LWData([__filePath2, testFile])
    # forms.epwInterface.addFilePathsToexcelFile_LWData([testFile])

    sys.exit(app.exec_())

# 现在的文件体积是200mb(两个sdk的dll能占100)，7z极限压缩后是50mb

# pyinstaller --noconfirm --onedir --console --clean
# --runtime-hook "C:/Users/Administrator/Documents/CodeProject/ATO/hook.py"
# --add-data "C:/Users/Administrator/Documents/CodeProject/ATO/app/AppData;AppData/"
# --collect-binaries "UnifyNetSDK"  # 这个参数的对象居然是模块
# "C:/Users/Administrator/Documents/CodeProject/ATO/app/ATO.py"

# C:\Users\Administrator\Documents\CodeProject\ATO\app\AppData\soft_icon.ico
# pyinstaller --noconfirm --onedir --contents-directory . --console --clean --runtime-hook "C:/Users/Administrator/Documents/CodeProject/ATO/hook.py" --add-data "C:/Users/Administrator/Documents/CodeProject/ATO/app/AppData;AppData/" --collect-binaries "UnifyNetSDK"  "C:/Users/Administrator/Documents/CodeProject/ATO/app/ATO.py"
# pyinstaller --noconfirm --onedir --contents-directory . --console --clean --runtime-hook "C:/Users/Administrator/Documents/CodeProject/ATO/hook.py" --add-data "C:/Users/Administrator/Documents/CodeProject/ATO/app/AppData;AppData/" --collect-binaries "UnifyNetSDK" -i "C:\Users\Administrator\Documents\CodeProject\ATO\app\AppData\soft_icon.ico" "C:/Users/Administrator/Documents/CodeProject/ATO/app/ATO.py"
