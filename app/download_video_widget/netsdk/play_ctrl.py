# 用pyqt的文件监视器
import sys
import time
from pathlib import Path

from PyQt5.QtCore import Qt, QFileInfo, QFileSystemWatcher, QObject, QCoreApplication
from PyQt5.QtWidgets import QApplication, QWidget
from UnifyNetSDK import DaHuaPlaySDK


class VideoTsPic(QObject):
    """
    监视外部videoprocess文件夹，过滤到mp4文件就开始转换
    """

    start = None
    stop = None

    # 开始暂停转换的flag，子进程不关，仅pass转换功能

    def __init__(self, path):
        super().__init__()
        self.direcWatchDog = QFileSystemWatcher()
        self.direcWatchDog.addPath(path)
        self.direcWatchDog.directoryChanged.connect(self.do_directoryChanged)
        print("小狗启动")
        self.preFileNum = 0

    def do_directoryChanged(self, path):
        curfileList = set()
        dirPath = Path(path)
        [curfileList.add(file) for file in dirPath.iterdir() if file.is_file() and file.suffix == ".mp4"]
        time.sleep(2)
        # 先获取mp4文件列表
        for filePath in curfileList:
            dstFilePath = filePath.with_name(str(filePath.stem) + ".jpg").absolute()
            self.tsPic(str(filePath), str(dstFilePath))
            filePath.unlink()
            print("文件已删除")

    def tsPic(self, absVideoPath, absPicPath):
        playClient = DaHuaPlaySDK()
        nPort = playClient.getFreePort()
        playClient.openFile(nPort, absVideoPath)
        playClient.play(nPort)
        time.sleep(0.1)
        playClient.catchPic(nPort, absPicPath)
        playClient.stop(nPort)
        playClient.close(nPort)
        playClient.releasePort(nPort)


if __name__ == "__main__":
    app = QCoreApplication(sys.argv)
    path = str(Path(__file__).parent)
    cVar = VideoTsPic(path)
    sys.exit(app.exec_())
