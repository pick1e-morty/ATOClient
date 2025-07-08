from pathlib import Path

"""
本文件定义的路径最好紧跟mkdir
"""
DEBUG = False
# 开发模式下的路径些微有些不同，主要是这个项目结构需要做这个判断

PROJECT_ROOT_PATH = Path(__file__).parent.parent  # ATOClient/app 是项目根目录

if DEBUG:
    APPDATA_PATH = PROJECT_ROOT_PATH / "AppData"
    DVW_DOWNLOAD_VIDEO_PATH = PROJECT_ROOT_PATH / "pic"  # dvw下载到的文件路径
else:
    APPDATA_PATH = PROJECT_ROOT_PATH.parent / "AppData"
    DVW_DOWNLOAD_VIDEO_PATH = (
        PROJECT_ROOT_PATH.parent.parent / "pic"
    )  # dvw下载到的文件路径
DVW_DOWNLOAD_VIDEO_PATH.mkdir(exist_ok=True)  # 创建路径

DVW_DOWNLOAD_FILE_SUFFIX = ".mp4"  # dvw下载的文件后缀名
DVW_CONVERTED_FILE_SUFFIX = ".jpg"  # dvw转换的文件名后缀
DVW_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"  # dvw窗体页面需要使用的缺省 时间格式化代码
