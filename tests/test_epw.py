import sys
from pathlib import Path

ProjectPath = Path(__file__).parent
sys.path.append(str(ProjectPath.parent))

import os
from PyQt5.QtWidgets import (QApplication, QFileDialog, QTableWidgetItem, QListWidgetItem, QAbstractItemView, QWidget)
from app.esheet_process_widget.epw import EPW_Class

if __name__ == "__main__":  # 用于当前窗体测试
    from app.utils.aboutconfig import configini

    app = QApplication(sys.argv)  # 创建GUI应用程序
    forms = EPW_Class(configini)  # 创建窗体
    __desktopPath = os.path.join(os.path.expanduser('~'), 'Desktop')
    __filePath1 = os.path.join(__desktopPath, "1127.xlsx")
    __filePath2 = os.path.join(__desktopPath, "1128.xlsx")
    # forms.addFilePathsToexcelFile_LWData([__filePath1])
    forms.addFilePathsToexcelFile_LWData([__filePath1, __filePath2])
    forms.show()
    forms.ui.autoDeleteUnConfiguredYT_SB.setChecked(True)

    sys.exit(app.exec_())
# viztracer --ignore_frozen --ignore_c_function --tracer_entries 2000000 tests\test_epw.py
# vizviewer result.json

# 两个resizeByColumnContens特别耗时
# 还有一个主题上的setFont
# 读文件的那个希望是IO密集多一点，可以试着加一个线程池