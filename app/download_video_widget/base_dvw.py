import multiprocessing
import sys
import threading
from pathlib import Path
from PyQt5.QtCore import Qt, pyqtSignal, QFileSystemWatcher
from PyQt5.QtWidgets import (QApplication, QWidget, QTableWidgetItem)
from typing import List
from app.download_video_widget.UI.ui_DownloadVideo import Ui_DVW_Widget
from loguru import logger

# 这个pyinstaller在6.0大版本后居然把onedir做成了一个_internal，然后将exe启动文件放到根目录的上层里去了
_watchRootPath = Path(__file__).parent.parent.parent.parent / "pic"  # 所有我这边需要再协调一下
_watchRootPath.mkdir(exist_ok=True)


class BaseDVW(QWidget):
    """
    这边负责那个 文件数量 表格组件的功能
    """

    def __init__(self, parent=None):
        super().__init__(parent)  # 调用父类构造函数，创建窗体
        self.ui = Ui_DVW_Widget()  # 创建UI对象
        self.ui.setupUi(self)  # 构造UI界面

        self.bigDog = QFileSystemWatcher()
        self.bigDog.directoryChanged.connect(self.doBigDogShouldDo)  # 大狗只负责监控pic文件夹中有多少个子级文件夹

        self.smallDog = QFileSystemWatcher()
        self.smallDog.directoryChanged.connect(self.doSmallDogShouldDo)



        self.subDirs = set()

    def closeTheDoorAndreleaseTheDog(self):
        # 关门放狗
        self.bigDog.addPath(_watchRootPath)

    def openTheDoorAndCollectTheDog(self):
        # 开门收狗
        # 是属于中止的状态
        self.bigDog.removePaths(self.bigDog.directories())  # 删除pic根目录的监视
        self.smallDog.removePaths(self.smallDog.directories())  # 删除pic下的子级目录的监视



    def doBigDogShouldDo(self, pathChanged):
        self.curSubDir = [pathObject for pathObject in Path(pathChanged).iterdir() if pathObject.is_dir()]


    def doSmallDogShouldDo(self):
        pass


# 有几个文件夹就开几个狗
# 文件夹和文件状态都要监视的


if __name__ == '__main__':
    app = QApplication(sys.argv)  # 创建GUI应用程序
    forms = BaseDVW()  # 创建窗体
    forms.show()

    sys.exit(app.exec_())
