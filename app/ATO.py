import os
import sys
import multiprocessing
from pathlib import Path

sys.path.append(str(Path(__file__).absolute().parent.parent))  # 在vscode里不会自动追加项目根目录为pythonpath

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
from app.main_window.main_window import MainWindow

if __name__ == '__main__':
    multiprocessing.freeze_support()
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    app = QApplication(sys.argv)
    forms = MainWindow()
    forms.show()
    forms.splashScreen.finish()
    # TODO 测试参数，记得改回第一个页面， 参数1,3
    forms.stackWidget.setCurrentIndex(3)

    __desktopPath = os.path.join(os.path.expanduser('~'), 'Desktop')
    testFile = os.path.join(__desktopPath, "0306.xlsx")
    __filePath2 = os.path.join(__desktopPath, "0307.xlsx")
    # forms.epwInterface.addFilePathsToexcelFile_LWData([__filePath2, __filePath1])
    forms.epwInterface.addFilePathsToexcelFile_LWData([testFile, __filePath2])

    app.exec_()
