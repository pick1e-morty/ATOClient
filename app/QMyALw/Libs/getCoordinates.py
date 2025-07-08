import os
import shutil
import sys

from app.QMyALw.Libs.yolov5 import detect
from pathlib import Path

PROJECT_NAME = "exp"


getCoordinatesFileAddress = os.path.dirname(os.path.realpath(__file__))  # 本文件路径
ATOFolderAddress = "../../../"  # 我的MainWindow所在 也是项目地址
ROOT = os.path.join(getCoordinatesFileAddress, ATOFolderAddress)
print(1, ROOT)
ROOT = os.path.realpath(ROOT)
print(2, ROOT)


# FILE = Path(__file__).resolve()
# ROOT = FILE.parents[0]  # YOLOv5 root directory
# if str(ROOT) not in sys.path:
#     sys.path.append(str(ROOT))  # add ROOT to PATH
# ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  # relative
# print(1,ROOT)


# 函数这边是确保训练结果要在相应的文件夹里 数据集那边重新跑 然后标注那边需要找到他的标记方法 是相对于图片大小的浮点坐标
# 比例 标注对象相比图片所占的比例 中心点2 宽高
# 预览图片不会自动关闭
def getPackageCoordinates(confidence, IOU, NMS, saveResult, viewResult, path_list):
    # 获取包裹坐标 参数依次分别为 置信度，交并化，非极大值抑制，保存预测结果，结果预览，文件列表

    modelPath = os.path.join(ROOT, "custom/exp3.pt")
    yaml = os.path.join(ROOT, "custom/coco128.yaml")

    afterRemoveExistingExpPaths = clearFolder(path_list)
    for folderPath in afterRemoveExistingExpPaths:
        detect.run(
            weights=modelPath,  # model.pt path(s)
            source=folderPath,  # 文件地址
            data=yaml,  # dataset.yaml path
            imgsz=(
                640,
                640,
            ),  # 送进网络中图片的resize大小 不会改变inputFile和outFile的尺寸 我有想法要重新训练720大小的模型
            conf_thres=confidence,  # 置信度
            iou_thres=IOU,  # 交并化
            max_det=1000,  # maximum detections per image
            view_img=viewResult,  # show results
            save_txt=True,  # save results to *.txt
            save_conf=False,  # save confidences in --save-txt labels
            save_crop=False,  # save cropped prediction boxes
            nosave=not saveResult,  # do not save images/videos
            agnostic_nms=NMS,  # class-agnostic NMS
            augment=True,  # augmented inference
            update=False,  # update all models
            project=folderPath,  # save results to project/name
            name=PROJECT_NAME,  # save results to project/name
            exist_ok=True,  # existing project/name ok, do not increment
            line_thickness=3,  # bounding box thickness (pixels)
        )


def clearFolder(folderPathList):
    # 文件件路径列表 对这个文件夹下的exp进行检测 如果不为空则删除
    for folderPath in folderPathList:
        # 搜字符串中有没有PROJECT_NAME 有的话 删除这个目录 然后把他弹出去
        # PathList = folderPath.split("/")
        if folderPath.count(PROJECT_NAME):
            shutil.rmtree(folderPath)
            folderPathList.pop(folderPathList.index(folderPath))
    return folderPathList
