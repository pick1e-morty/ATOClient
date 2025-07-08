import time
from pathlib import Path

from UnifyNetSDK import DaHuaPlaySDK
from UnifyNetSDK.dahua.dh_playsdk_exception import DHPlaySDKException
from loguru import logger


def tsPic(absVideoPath: [str, Path], absPicPath: str = None):
    """
    从视频中截取一张图片,保存到指定路径.
    :param absVideoPath: 视频绝对路径
    :param absPicPath: 图片绝对路径
    :return: None
    如果第二个参数不传，那么就会在视频的同一目录下生成一个同名的jpg文件


    这是downloader要用的视频转换函数，是下载完成后紧跟的一个函数
    ！如果函数转换失败将不会删除源文件，因为downloader的某些数据传输并没有通过 “正规途径” 传送给我，也就是dvr还没把数据传完！
    我这边又因为协议的问题不能识别到数据是否传输完成，而此时就进行视频转化肯定是失败的，这是就不能删除源文件了
    仅当函数执行成功，且转化成功，才会删除源文件

    """
    if absPicPath is None:
        videoPath = Path(absVideoPath)
        absPicPath = str(videoPath.with_name(str(videoPath.stem) + ".jpg").absolute())
    logger.info(f"开始转换视频 {absVideoPath}，图片输出路径为 {absPicPath}")
    playClient = None
    nPort = None
    playResult = False
    openResult = False
    catchPicResult = False
    stopResult = False
    closeResult = False
    releaseResult = False
    try:
        playClient = DaHuaPlaySDK()
        nPort = playClient.getFreePort()
        openResult = playClient.openFile(nPort, absVideoPath)
        playResult = playClient.play(nPort)
        time.sleep(0.2)  # 要等dll那边把数据“填充”到port才能开始操作
        catchPicResult = playClient.catchPic(nPort, absPicPath)
        stopResult = playClient.stop(nPort)
        closeResult = playClient.close(nPort)
        releaseResult = playClient.releasePort(nPort)
    except DHPlaySDKException as e:
        logger.error(
            f"{absVideoPath}转换失败，源文件已保留，错误代码{type(e).__name__}"
        )
        if playClient and nPort:
            if playResult and not stopResult:
                playClient.stop(nPort)
            if openResult and not closeResult:
                playClient.close(nPort)
            playClient.releasePort(nPort)
    else:
        try:
            Path(absVideoPath).unlink()
            logger.success(f"{absVideoPath}转换成功，源文件已删除")
        except Exception as e:
            logger.error(f"{absVideoPath}自动删除失败，错误代码{type(e).__name__}")
