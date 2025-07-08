import sys
from pathlib import Path

ProjectPath = Path(__file__).parent
sys.path.append(str(ProjectPath.parent))

import os
from PyQt5.QtWidgets import (
    QApplication,
    QFileDialog,
    QTableWidgetItem,
    QListWidgetItem,
    QAbstractItemView,
    QWidget,
)
from app.esheet_process_widget.epw import EPWclass

if __name__ == "__main__":  # 用于当前窗体测试
    from app.utils.forms_config import formsConfigDict

    app = QApplication(sys.argv)  # 创建GUI应用程序
    forms = EPWclass()  # 创建窗体
    __desktopPath = os.path.join(os.path.expanduser("~"), "Desktop")
    __filePath1 = os.path.join(__desktopPath, "1127.xlsx")
    __filePath2 = os.path.join(__desktopPath, "1128.xlsx")
    __filePath3 = os.path.join(__desktopPath, "1207.xlsx")
    __filePath4 = os.path.join(__desktopPath, "1208.xlsx")
    __filePath5 = os.path.join(__desktopPath, "1209.xlsx")
    __filePath6 = os.path.join(__desktopPath, "1210.xlsx")
    # forms.addFilePathsToexcelFile_LWData([__filePath1])
    forms.addFilePathsToexcelFile_LWData(
        [__filePath1, __filePath2, __filePath3, __filePath4, __filePath5, __filePath6]
    )
    forms.show()

    sys.exit(app.exec_())
# viztracer --ignore_frozen --ignore_c_function --tracer_entries 2000000 tests\test_epw.py
# vizviewer result.json
