import os
import subprocess
from multiprocessing import Pool, cpu_count

VideoConvertFileAddress = os.path.dirname(os.path.realpath(__file__))  # 本文件路径
ATOFolderAddress = "../../../"  # 我的MainWindow所在 也是项目地址
relativeFfmpegAddress = "custom/ffmpeg.exe"
FFMPEGADDRESS = os.path.join(
    VideoConvertFileAddress, ATOFolderAddress, relativeFfmpegAddress
)


def getVidoeLength(filename):
    # 获取视频长度
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            filename,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return float(result.stdout)


def oneSecondVideoToOnePicture(pathList):
    # 一秒视频转一张图片 从这开启多进程池
    pool = Pool(processes=cpu_count())

    for path in pathList:
        pool.apply_async(oneSecondVideoToOnePictureFunc, (path,))


def oneSecondVideoToOnePictureFunc(path):
    print(FFMPEGADDRESS)
    print(os.path.abspath(FFMPEGADDRESS))
    filePathName = os.path.splitext(path)[0]
    outPath = filePathName + ".jpeg"
    command = "{} -i {} -r 1 -t 1 {} -y".format(FFMPEGADDRESS, path, outPath)
    print(command)
    result = subprocess.run(
        command, encoding="utf-8", timeout=10
    )  # 10秒超时 自动关闭子进程
    # os.system(command)


def videoSecondsPictures(pathList):
    # 视频秒数个图片 从这开启多进程池

    pass
