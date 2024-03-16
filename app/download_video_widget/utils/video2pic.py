import time
from pathlib import Path

from UnifyNetSDK import DaHuaPlaySDK


def tsPic(absVideoPath: str, absPicPath: str = None):
    """
    从视频中截取一张图片,保存到指定路径.
    :param absVideoPath: 视频绝对路径
    :param absPicPath: 图片绝对路径
    :return: None
    如果第二个参数不传，那么就会在视频的同一目录下生成一个同名的jpg文件
    """
    if absPicPath is None:
        videoPath = Path(absVideoPath)
        absPicPath = str(videoPath.with_name(str(videoPath.stem) + ".jpg").absolute())
    playClient = DaHuaPlaySDK()
    nPort = playClient.getFreePort()
    playClient.openFile(nPort, absVideoPath)
    playClient.play(nPort)
    time.sleep(0.2)  # 要等dll那边把数据“填充”到port才能开始操作
    playClient.catchPic(nPort, absPicPath)
    playClient.stop(nPort)
    playClient.close(nPort)
    Path(absVideoPath).unlink()
    playClient.releasePort(nPort)
