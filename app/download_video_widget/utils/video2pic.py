import time
from pathlib import Path

from UnifyNetSDK import DaHuaPlaySDK
from UnifyNetSDK.dahua.dh_playsdk_exception import PLAY_NO_FRAME, DHPlaySDKException, PLAY_OPEN_FILE_ERROR
from loguru import logger


def tsPic(absVideoPath: [str, Path], absPicPath: str = None):
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

    playClient = None
    nPort = None
    playResult = False
    openResult = False
    try:
        playClient = DaHuaPlaySDK()
        nPort = playClient.getFreePort()
        openResult = playClient.openFile(nPort, absVideoPath)
        playResult = playClient.play(nPort)
        time.sleep(0.2)  # 要等dll那边把数据“填充”到port才能开始操作
        playClient.catchPic(nPort, absPicPath)
    except PLAY_OPEN_FILE_ERROR:
        logger.error(f"{absVideoPath}的mp4文件打开失败，已自动删除")
    except PLAY_NO_FRAME:
        logger.error(f"{absVideoPath}的mp4文件没有有效帧，已自动删除")
    except DHPlaySDKException as e:
        logger.error(f"{absVideoPath}转换失败，错误代码{type(e).__name__}")
    finally:
        if playClient and nPort:
            if playResult:
                playClient.stop(nPort)
            if openResult:
                playClient.close(nPort)
            playClient.releasePort(nPort)
        try:
            Path(absVideoPath).unlink()
        except Exception as e:
            logger.error(f"{absVideoPath}自动删除失败，错误代码{type(e).__name__}")
