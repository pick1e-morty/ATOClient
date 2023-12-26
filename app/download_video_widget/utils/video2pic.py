import time
from pathlib import Path

from UnifyNetSDK import DaHuaPlaySDK


def tsPic(absVideoPath, absPicPath=None):
    if absPicPath is None:
        videoPath = Path(absVideoPath)
        absPicPath = str(videoPath.with_name(str(videoPath.stem) + ".jpg").absolute())
    playClient = DaHuaPlaySDK()
    nPort = playClient.getFreePort()
    playClient.openFile(nPort, absVideoPath)
    playClient.play(nPort)
    time.sleep(0.1)     # 要等dll那边把数据“填充”到port才能开始操作
    playClient.catchPic(nPort, absPicPath)
    playClient.stop(nPort)
    playClient.close(nPort)
    Path(absVideoPath).unlink()
    playClient.releasePort(nPort)