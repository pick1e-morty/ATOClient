import math
import os.path

from PIL.ImageDraw import Draw
from PIL import Image
from app.QMyALw.Libs.QMyALwEnum import YTcontrastTWEnum


def drawCoordinates(jpegFileAddress, specifyCoordinate):
    # 第四步 拿到那个唯一的矩形坐标 然后画图
    # 第一个参数是图片的文件地址，第二参是要画的矩形坐标 左上角的xy和宽高 转换成
    # 再开一个文件夹放这个图片 叫filter/
    parentFolderAddress, fileNamePath = os.path.split(jpegFileAddress)
    newParentFolderAddress = os.path.join(parentFolderAddress, "filter")
    newFilePath = os.path.join(
        newParentFolderAddress, fileNamePath
    )  # 新的文件地址是原文件的父级追加名为filter的文件夹
    if os.path.exists(newParentFolderAddress) is not True:  # 如果路径不存在则创建
        os.makedirs(newParentFolderAddress)
    im = Image.open(jpegFileAddress)
    draw = Draw(im)
    print(specifyCoordinate)
    # 传过来的坐标是 xywh的 需要转换一下 这个rectangle的第一个xy参数是左上角的xy和右下角的xy
    x = specifyCoordinate[0]  # 外边框十六进制红色，像素宽度3
    y = specifyCoordinate[1]
    w = specifyCoordinate[2]
    h = specifyCoordinate[3]
    x0 = x
    x1 = y
    y0 = x + w
    y1 = y + h
    draw.rectangle(((x0, x1), (y0, y1)), outline="#FF0000", width=3)
    im.save(newFilePath)


def filterAndDrawPackageCoordinates(tableDataList):
    # 需要获取txt中的坐标 处理之后再画图
    for dataList in tableDataList:
        pictureFileAddress = dataList[YTcontrastTWEnum._shipFilePath.value]  # 图片地址
        labelTxtFileAddress = dataList[
            YTcontrastTWEnum._shipCoordinatePath.value
        ]  # 相对应的坐标文本文件地址
        assemblyLineRange = dataList[
            YTcontrastTWEnum.assemblyLineRange.value
        ]  # 线体多边形坐标
        weighingPlatformRange = dataList[
            YTcontrastTWEnum.weighingPlatformRange.value
        ]  # 称台多边形坐标
        packageCoordinatesClosestToTheWeighingTable = handleCoordinates(
            labelTxtFileAddress, assemblyLineRange, weighingPlatformRange
        )  #

        if (
            packageCoordinatesClosestToTheWeighingTable
        ):  # 坐标处理完就剩一个符合条件的坐标 在图片上画下这个矩形
            drawCoordinates(
                pictureFileAddress, packageCoordinatesClosestToTheWeighingTable
            )
    # 坐标处理完
    print("处理结束")


def handleCoordinates(labelTxtFileAddress, assemblyLineRange, weighingPlatformRange):
    # 第一个参数是坐标文件地址,第二个参数是要过滤的那个线体坐标,第三个称台坐标
    # 返回距离称台坐标最近的包裹坐标xywh
    # 第一步先从文件中取出各行list 再然后转换成xywh
    # 第二步 判断包裹坐标是否存在于线体中 不存在就删除掉
    # 第三步 是判断距离，因为这个包裹虽然在线体上但它可能不会在称台上 这一步写函数判断原点距离 取出最近的那个
    # ！！！ 但注意，距离最近的那个可能不准确，因为真正给距离称台最近的那个可能没被yolo标记出来 这个靠完善模型就好了
    # 第四步 拿到那个唯一的矩形坐标 然后画图
    coordinateList = getCoordinatesInFile(
        labelTxtFileAddress
    )  # yolo标记文件中的xywh坐标列表
    assemblyLinePolygonEndPoint = getPolygonEndpoint(
        assemblyLineRange
    )  # 线体多边形坐标转一下符合规则的列表
    weighingPlatformPolygonEndPoint = [
        int(elem) for elem in weighingPlatformRange.split(",")
    ]  # 原点坐标文本转列表
    inAssemblyLineRangePackagePoint = DetermineWhetherTheCoordinatesAreInThePolygon(
        coordinateList, assemblyLinePolygonEndPoint
    )
    if len(inAssemblyLineRangePackagePoint):
        # 先排除不在线体(多边形)中的原点点(yolo矩形的中点)
        packageCoordinatesClosestToTheWeighingTable = findTheNearestPoint(
            inAssemblyLineRangePackagePoint, weighingPlatformPolygonEndPoint
        )
        # 再从这些矩形中找出距离称台原点最近的那个原点(yolo矩形的中点) 再次声明，真正距离最近的原点受yolo识别准确率所影响
        if packageCoordinatesClosestToTheWeighingTable:  # 如果这个坐标存在则返回
            return packageCoordinatesClosestToTheWeighingTable
    return None


def findTheNearestPoint(inAssemblyLineRangePackagePoint, weighingPlatformRange):
    # 第一参是包裹坐标中心存在于多边形线体中的xywh坐标列表
    # 第二参是称台的中心点
    # 还是先从包裹的xywh中求中心 然后找出距离称台中心最近的那一个点
    thePoint = 0
    for pointIndex, packagePoint in enumerate(inAssemblyLineRangePackagePoint):
        x = packagePoint[0]
        y = packagePoint[1]
        w = packagePoint[2]
        h = packagePoint[3]

        x1 = x + w / 2  # xCenter
        x2 = y + h / 2  # yCenter
        y1 = weighingPlatformRange[0]
        y2 = weighingPlatformRange[1]  # 一个数学公式 求极坐标上两个原点的距离
        # pointDistance = round(math.sqrt((x1 - y1) ** 2 + (x2 - y2) ** 2))
        pointDistance = round(
            math.sqrt(math.pow((y1 - x1), 2) + math.pow((y2 - x2), 2))
        )
        inAssemblyLineRangePackagePoint[pointIndex].append(
            pointDistance
        )  # 把距离追加到相应坐标列表的末尾

    # 从大到小对这个列表的第五个元素(下标为4)进行正向排序，这样距离最近的原点就是第一个列表了
    inAssemblyLineRangePackagePoint.sort(
        key=lambda element: element[4]
    )  # 排序，根据第五个元素(下标为4)进行正向排序
    thePoint = inAssemblyLineRangePackagePoint[0][
        :4
    ]  # 取出这个列表中的第一个坐标行 下标5是原点所以不用取
    print(inAssemblyLineRangePackagePoint)
    return thePoint


def getPolygonEndpoint(pointText):
    # 格式转换一下
    # 508,719-346,46-333,1-502,1-1088,717
    # [[508,719],[346,46],[333,1],[502,1],[1088,717]
    polygonEndPointList = []
    pointTextList = pointText.split("-")
    for pointcomma in pointTextList:
        pointSplitCommaList = pointcomma.split(",")
        polygonEndPointList.append([int(elem) for elem in pointSplitCommaList])
    return polygonEndPointList


def DetermineWhetherTheCoordinatesAreInThePolygon(coordinateList, assemblyLineRange):
    # 第一个参数包裹的xywh坐标，第二个参数是流水线体多边形坐标
    # 第二步 判断包裹坐标是否存在于线体中 返回存在于线体中的包裹xywh坐标
    inAssemblyLineRangePackagePoint = []
    for packageCoordinate in coordinateList:
        x = packageCoordinate[0]  # 取包裹坐标的xywh
        y = packageCoordinate[1]
        w = packageCoordinate[2]
        h = packageCoordinate[3]
        packageCenterX = x + round(w / 2)  # 包裹矩形的中心x
        print(packageCenterX)
        packageCenterY = y + round(h / 2)  # 中心y
        print(packageCenterY)
        packageRectangularCenter = [packageCenterX, packageCenterY]
        if isPoiWithinSimplePoly(
            packageRectangularCenter, assemblyLineRange
        ):  # ctrlC过来的 判断一个原点是否在多边形中
            inAssemblyLineRangePackagePoint.append(
                packageCoordinate
            )  # 如果为真则把这个原点的xywh坐标添加到新列表中
    print(inAssemblyLineRangePackagePoint)  # 这一步收集原点用处不大
    return inAssemblyLineRangePackagePoint


def getCoordinatesInFile(labelTxtFileAddress):
    # 第一步先从文件中取出各行list 再然后转换成xywh
    # 参数是坐标文件
    # 返回以xywh组成列表 第一是从文件中取出来，第二是坐标转换，原图片坐标比例，转像素坐标
    coordinateList = []
    with open(labelTxtFileAddress, mode="r") as f:
        textList = f.readlines()
    for lineText in textList:
        lineText = lineText.replace("\n", "")
        lineTextList = lineText.split(" ")
        xcenter = round(eval(lineTextList[1]) * 1280)
        ycenter = round(eval(lineTextList[2]) * 720)
        w = round(eval(lineTextList[3]) * 1280)
        h = round(eval(lineTextList[4]) * 720)
        x = round(xcenter - w / 2)
        y = round(ycenter - h / 2)
        coordinateList.append([x, y, w, h])

    return coordinateList


def isPoiWithinBox(poi, sbox, toler=0.0001):
    # sbox=[[x1,y1],[x2,y2]]
    # 不考虑在边界上，需要考虑就加等号
    if (
        poi[0] > sbox[0][0]
        and poi[0] < sbox[1][0]
        and poi[1] > sbox[0][1]
        and poi[1] < sbox[1][1]
    ):
        return True
    if toler > 0:
        pass
    return False


# 射线与边是否有交点
def isRayIntersectsSegment(poi, s_poi, e_poi):  # [x,y] [lng,lat]
    if s_poi[1] == e_poi[1]:  # 排除与射线平行、重合，线段首尾端点重合的情况
        return False
    if s_poi[1] > poi[1] and e_poi[1] > poi[1]:
        return False
    if s_poi[1] < poi[1] and e_poi[1] < poi[1]:
        return False
    if s_poi[1] == poi[1] and e_poi[1] > poi[1]:
        return False
    if e_poi[1] == poi[1] and s_poi[1] > poi[1]:
        return False
    if s_poi[0] < poi[0] and e_poi[1] < poi[1]:
        return False
    xseg = e_poi[0] - (e_poi[0] - s_poi[0]) * (e_poi[1] - poi[1]) / (
        e_poi[1] - s_poi[1]
    )  # 求交
    if xseg < poi[0]:
        return False
    return True


def isPoiWithinSimplePoly(poi, simPoly, tolerance=0.0001):
    # 点；多边形数组；容限
    # simPoly=[[x1,y1],[x2,y2],……,[xn,yn],[x1,y1]]
    # 如果simPoly=[[x1,y1],[x2,y2],……,[xn,yn]] i循环到终点后还需要判断[xn,yx]和[x1,y1]
    # 先判断点是否在外包矩形内
    if not isPoiWithinBox(poi, [[0, 0], [1280, 720]], tolerance):
        return False

    polylen = len(simPoly)
    sinsc = 0  # 交点个数
    for i in range(polylen - 1):
        s_poi = simPoly[i]
        e_poi = simPoly[i + 1]
        if isRayIntersectsSegment(poi, s_poi, e_poi):
            sinsc += 1

    return True if sinsc % 2 == 1 else False


if __name__ == "__main__":
    # packageCoordinatesClosestToTheWeighingTable = handleCoordinates(
    #     r"C:\Users\admin\Documents\ATO\videoprocess\1.16\462193852960702.jpeg",
    #     "508,719-346,46-333,1-502,1-1088,717", "620,382")
    packageCoordinatesClosestToTheWeighingTable = handleCoordinates(
        r"C:\Users\admin\Documents\ATO\videoprocess\1.20\exp\labels\318218657832622.txt",
        "773,719-640,60-717,55-1042,356-1280,720",
        "811,432",
    )
    # if packageCoordinatesClosestToTheWeighingTable:
    drawCoordinates(
        r"C:\Users\admin\Documents\ATO\videoprocess\1.20\318218657832622.jpeg",
        packageCoordinatesClosestToTheWeighingTable,
    )
