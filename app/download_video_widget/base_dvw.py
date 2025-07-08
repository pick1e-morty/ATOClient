import multiprocessing
import sys
import threading
import time
from pathlib import Path
from PyQt5.QtCore import Qt, pyqtSignal, QFileSystemWatcher
from PyQt5.QtWidgets import QApplication, QWidget, QTableWidgetItem
from typing import List
from app.download_video_widget.UI.ui_DownloadVideo import Ui_DVW_Widget
from loguru import logger

from app.utils.project_path import (
    DVW_DOWNLOAD_VIDEO_PATH,
    DVW_DOWNLOAD_FILE_SUFFIX,
    DVW_CONVERTED_FILE_SUFFIX,
)
from app.utils.tools import findItemTextInTableWidgetRow, AlignCenterQTableWidgetItem


class BaseDVW(QWidget):
    """
    这边负责那个 文件数量 表格组件的功能
    """

    def __init__(self, parent=None):
        super().__init__(parent)  # 调用父类构造函数，创建窗体
        self.ui = Ui_DVW_Widget()  # 创建UI对象
        self.ui.setupUi(self)  # 构造UI界面
        self.bigDog = (
            QFileSystemWatcher()
        )  # 因为业务逻辑繁杂，故使用两个QFileSystemWatcher以保证槽函数代码逻辑简单通顺
        self.bigDog.directoryChanged.connect(
            self.doBigDogShouldDo
        )  # 大狗只负责监控pic文件夹中有多少个子级文件夹
        self.smallDog = QFileSystemWatcher()
        self.smallDog.directoryChanged.connect(
            self.doSmallDogShouldDo
        )  # 小狗负责监测各子级文件夹中的文件数量
        self.subDirs = set()  # 保存上一轮的pic子级文件夹。集合类型
        self.watcherIswatch = False  # 判断两只小狗是否已经进入状态，避免重复添加

    def closeTheDoorAndreleaseTheDog(self):
        # 关门放狗，添加pic路径，并激活一次大狗的槽函数
        if not self.watcherIswatch:
            logger.trace("开启bigDog和smallDog的文件夹监视")
            self.ui.fileCount_TW.clearContents()
            self.ui.fileCount_TW.setRowCount(0)  # 清空表格数据
            QApplication.processEvents()  # 上一步需要立即执行。不然会被qt的事件机制给合并掉，会影响后续代码的判断
            self.bigDog.addPath(str(DVW_DOWNLOAD_VIDEO_PATH))
            self.doBigDogShouldDo(str(DVW_DOWNLOAD_VIDEO_PATH))
            self.watcherIswatch = True

    def openTheDoorAndCollectTheDog(self):
        # 开门收狗，停止两个监视的工作，清空表格及初始化其他相关变量。
        if self.watcherIswatch:
            self.bigDog.removePaths(self.bigDog.directories())  # 删除pic根目录的监视
            self.smallDog.removePaths(
                self.smallDog.directories()
            )  # 删除pic下的子级目录的监视
            self.ui.fileCount_TW.clearContents()
            self.ui.fileCount_TW.setRowCount(0)
            self.subDirs = set()
            logger.trace("已停止bigDog和smallDog的文件夹监视")
            self.watcherIswatch = False

    def doBigDogShouldDo(self, pathChanged):
        curSubDir = {
            pathObject
            for pathObject in Path(pathChanged).iterdir()
            if pathObject.is_dir()
        }  # 遍历pic路径下有多少个子级文件夹
        deletePaths = [
            str(pathObject) for pathObject in list(self.subDirs - curSubDir)
        ]  # 要删除的路径
        addPaths = [
            str(pathObject) for pathObject in list(curSubDir - self.subDirs)
        ]  # 要添加的路径
        if deletePaths:
            self.smallDog.removePaths(
                deletePaths
            )  # 如果欲删除路径不为空，则从小狗中删除该路径
            for pathObject in deletePaths:
                dirName = Path(pathObject).stem  # 取路径最后一级
                findedItems = self.ui.fileCount_TW.findItems(
                    dirName, Qt.MatchExactly
                )  # 先查到这个这个文件夹所在表格中的行
                if findedItems:
                    findedItem = findedItems[0]
                    row = findedItem.row()
                    self.ui.fileCount_TW.removeRow(row)  # 然后删除
                else:
                    logger.error(f"{pathObject}要删除这个路径，但是没查到item呀")
        if addPaths:
            self.smallDog.addPaths(
                addPaths
            )  # 如果欲添加的路径不为空，则全部加到小狗中，并逐个激活小狗的槽函数
            for pathObject in addPaths:
                self.doSmallDogShouldDo(pathObject)
        self.subDirs = curSubDir  # 保存本次文件夹信息

    def doSmallDogShouldDo(self, pathChanged):
        if not Path(
            pathChanged
        ).exists():  # QFileSystemWatcher不支持反应文件夹在被修改时的状态
            logger.trace(
                "如果某个文件夹被删除了，本槽函数还是会被先于大狗的槽函数激活，所以作此判断。路径不存在的删除由大狗负责"
            )
            return  # 如果某个文件夹被删除了，本槽函数还是会被先于大狗的槽函数激活，所以作此判断。路径不存在的删除由大狗负责
        fileList = [
            pathObject
            for pathObject in Path(pathChanged).iterdir()
            if pathObject.is_file()
        ]  # 遍历激活路径
        mp4FileList = [
            pathObject
            for pathObject in fileList
            if pathObject.suffix == DVW_DOWNLOAD_FILE_SUFFIX
        ]  # 取mp4后缀文件路径
        jpgFileList = [
            pathObject
            for pathObject in fileList
            if pathObject.suffix == DVW_CONVERTED_FILE_SUFFIX
        ]  # 取jpg后缀文件路径
        dirName = Path(pathChanged).stem  # 取路径最后一级
        jpgFileCount = len(jpgFileList)
        mp4FileCount = len(mp4FileList)
        row, isRowExist = findItemTextInTableWidgetRow(
            self.ui.fileCount_TW, dirName
        )  # 查找 对应行 是否已存在
        if not isRowExist:
            dirNameItem = AlignCenterQTableWidgetItem(str(dirName))  # 文件夹名称
            self.ui.fileCount_TW.setItem(row, 0, dirNameItem)
            expectDownloadNumItem = AlignCenterQTableWidgetItem(
                str("已存在")
            )  # 预计下载数量
            self.ui.fileCount_TW.setItem(row, 1, expectDownloadNumItem)

        # 预计文件数量那行不用动，col指定为0，2，3
        jpg_Item = AlignCenterQTableWidgetItem(str(jpgFileCount))  # jpg文件数量
        self.ui.fileCount_TW.setItem(row, 2, jpg_Item)

        mp4_Item = AlignCenterQTableWidgetItem(str(mp4FileCount))  # mp4文件数量
        self.ui.fileCount_TW.setItem(row, 3, mp4_Item)
        self.ui.fileCount_TW.resizeColumnsToContents()  # 调整列宽
        self.ui.fileCount_TW.updateSelectedRows()  # 刷新主题显示状态


if __name__ == "__main__":
    app = QApplication(sys.argv)  # 创建GUI应用程序
    forms = BaseDVW()  # 创建窗体
    forms.show()
    forms.closeTheDoorAndreleaseTheDog()
    sys.exit(app.exec_())
