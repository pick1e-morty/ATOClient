import os
from app.QMyALw.Libs.QMyALwEnum import YTcontrastTWEnum
from app.esheet_process_widget.epw_enum import EDTWEnum
from app.QMyVDPw.Libs.DataHandling import getYTConfigrationExcelData
from app.QMyVDPw.Libs.QMyVDPwEnum import YTCETEnum


def JudgeWhetherTheConditionsAreMet(tableDataList):
    newTableDataList = []

    for oneDimensionalIndex, oneDimensionalDataList in enumerate(
        tableDataList
    ):  # 用enumrate的方法同时获取坐标和数据
        state = True
        for twoDimensionalIndex, twoDimensionalDataList in enumerate(
            oneDimensionalDataList
        ):
            if (
                str(twoDimensionalDataList) != "0"
                and str(twoDimensionalDataList) != "None"
            ):
                state = True
            else:
                state = False
                break
        if state:
            newTableDataList.append(oneDimensionalDataList)

    return newTableDataList


def upperOrderTop(tableDataList):
    # 如果第一列数据不为 指定空值 则将这一行列表放到最上面
    # 可以用list的sort方法做四次排序
    tableDataList.sort(
        key=lambda elem: str(elem[YTcontrastTWEnum.shipExist.value]), reverse=True
    )
    tableDataList.sort(
        key=lambda elem: str(elem[YTcontrastTWEnum.shipCoordinateName.value]),
        reverse=True,
    )
    tableDataList.sort(
        key=lambda elem: str(elem[YTcontrastTWEnum._shipFilePath.value]), reverse=True
    )
    tableDataList.sort(
        key=lambda elem: str(elem[YTcontrastTWEnum._shipCoordinatePath.value]),
        reverse=True,
    )
    return tableDataList


def YTContrastDataSortingProcessing(
    EPW_YT_RangeList, jpegFilePathList, labelTxtPathList
):
    # 月台对照表数据排序
    # 三个列表 取元素0对比排序
    tableData = []
    for YTIndex, YTConfigList in enumerate(EPW_YT_RangeList):
        shipcopy = YTConfigList[YTcontrastTWEnum.shipCopy.value]
        for jpegIndex, jpegFIlePath in enumerate(jpegFilePathList):
            jpegFileNameExt = os.path.basename(jpegFIlePath)
            print(jpegFileNameExt)
            jpegFileName, jpegFileExt = os.path.splitext(jpegFileNameExt)
            if shipcopy == jpegFileName:
                EPW_YT_RangeList[YTIndex][
                    YTcontrastTWEnum.shipExist.value
                ] = jpegFileNameExt
                EPW_YT_RangeList[YTIndex][
                    YTcontrastTWEnum._shipFilePath.value
                ] = jpegFIlePath
        for labelIndex, labelTxtPath in enumerate(labelTxtPathList):
            labelTxtFileNameExt = os.path.basename(labelTxtPath)
            print(labelTxtFileNameExt)
            labelTxtFileName, labelTxtFileExt = os.path.splitext(labelTxtFileNameExt)
            if shipcopy == labelTxtFileName:
                EPW_YT_RangeList[YTIndex][
                    YTcontrastTWEnum.shipCoordinateName.value
                ] = labelTxtFileNameExt
                EPW_YT_RangeList[YTIndex][
                    YTcontrastTWEnum._shipCoordinatePath.value
                ] = labelTxtPath
        # if EPW_YT_RangeList[YTIndex][YTcontrastTWEnum._shipCoordinatePath.value] == 0:

        # 一轮循环下来还是找不到就给一个默认赋值 不能空着 后面不好处理
    # print(tableData)
    return EPW_YT_RangeList


def getLabeTxtInMainFolder(folderPath):
    fileAddressList = []  # 绝对文件路径列表
    for root, dirs, files in os.walk(folderPath):
        for filePath in files:  #
            fileAddress = os.path.join(root, filePath)  # 获得绝对路径
            fileAddress = fileAddress.replace("\\", "/")  # 统一路径分隔符
            fileAddressList.append(fileAddress)  #
    filePathList = []  # 新地用于收集的列表
    for fileAddress in fileAddressList:  # 获取最终的文件路径后
        fileName = os.path.splitext(fileAddress)  # 分割文件名和文件扩展名
        if fileName[1] == ".txt":  # 如果文件扩展名是三参
            filePathList.append(fileAddress)
    print(filePathList)
    return filePathList


def getAllFilesUnderThePath(folderPath, includeSubfolders, extension):
    # 获取一参路径下所以的同级文件路径，如果二参为True则获取包括子文件夹的文件路径，三参是文件扩展名过滤
    # 返回的是一个列表 元素是绝对文件路径列表
    fileAddressList = []  # 绝对文件路径列表
    if includeSubfolders is True:  # 获取包括所有子级文件名
        # 获取向下一级的文件夹 然后逐个获取 没有二级
        for oneLevelpath in os.listdir(folderPath):
            absOneLevelpath = os.path.join(folderPath, oneLevelpath)
            if os.path.isdir(absOneLevelpath):  # 仅向下延伸一层    #注意拼合路径
                for twoLevelpath in os.listdir(
                    absOneLevelpath
                ):  # listdir返回的是当前层级的路径名称
                    absTwoLevelpath = os.path.join(absOneLevelpath, twoLevelpath)
                    if os.path.isfile(absTwoLevelpath):
                        fileAddress = absTwoLevelpath.replace(
                            "\\", "/"
                        )  # 统一路径分隔符
                        fileAddressList.append(fileAddress)  #
            elif os.path.isfile(
                absOneLevelpath
            ):  # 当前路径下的文件也要添加 一般不会存在 但
                fileAddress = absOneLevelpath.replace("\\", "/")  # 统一路径分隔符
                fileAddressList.append(fileAddress)  #

    elif includeSubfolders is False:  # 获取本级所有文件名
        for filePath in os.listdir(
            folderPath
        ):  # 上面那个文件列表是walk给的 然而这个本级的函数会返回本级文件夹和文件
            filePath = os.path.join(folderPath, filePath)
            if os.path.isfile(filePath):  # 所以还需要做一个isfile的判断
                filePath = filePath.replace("\\", "/")
                fileAddressList.append(filePath)
    filePathList = []  # 新地用于收集的列表
    for fileAddress in fileAddressList:  # 获取最终的文件路径后
        fileName = os.path.splitext(fileAddress)  # 分割文件名和文件扩展名
        if fileName[1] == extension:  # 如果文件扩展名是三参
            filePathList.append(fileAddress)
    print(filePathList)
    return filePathList


def getPrimaryPathInPathList(pathLists, folderPath):
    # 获得指定路径层级到文件名结尾
    # pathLists C:\Users\admin\Desktop\三超\三超标注\4280336676303.jpeg
    # folderPath 三超标注
    # 局部变量名为 primayPathEnd 结果是 三超标注\4280336676303.jpeg
    # 另外pathLists长这样
    # [[None,"文件地址"],[None,"文件地址"],["primaryPathEnd","文件地址"]]
    #
    for index, pathList in enumerate(pathLists):
        if pathList[0] is None:  # 索引0位是存储primayPathEnd的
            primaryPath = os.path.split(folderPath)[
                -1
            ]  # 从这个abspath中取出 本级路径字符串
            # C:/Users/admin/Documents/ATO/atowidgets/QMyALw 取出 QMyAlw
            FilePathList = pathList[1].split("/")  # 遍历所有文件路径 并分割各层级
            PriFilepath = FilePathList[
                FilePathList.index(primaryPath) :
            ]  # 从上面的文件层级列表中找到指定路径的索引位置
            primaryPathEnd = "/".join(PriFilepath)  # 截取出来后 再用路径分割符合并
            pathLists[index][0] = primaryPathEnd  # 最后把原来的None替换为
    return pathLists


def listContentDeDuplication(listOne, listTwo):
    # 一参是一个二维列表，内容为列表当前的数据，索引0是primaryPathEnd 索引1是绝对文件路径
    # 二参是一个一维列表，内容是刚获取到的绝对文件路径
    # 因为是二维对一维所以手动去重
    if not listOne:  # 如果listOne为空 说明组件上面还没有信息
        for element in listTwo:  # 既然listOne为空 那就直接用了吧
            listOne.append(
                [None, element]
            )  # 这不仅是一个去重函数 也需要把数据做下格式返回出去
        return listOne

    for index, listOneData in enumerate(listOne):
        # listOneData 是这样的['Desktop/1.dav', 'C:/Users/admin/Desktop/1.dav']
        filePath1 = listOneData[1]
        if listTwo.count(
            filePath1
        ):  # 用list的count方法检测第二列表中有没有这个相同的路径
            listTwo.pop(
                listTwo.index(filePath1)
            )  # 如果不为零说明存在，找到索引然后弹出
    for element in listTwo:  # 第二个列表去重后就可以按格式添加进第一个列表中了
        listOne.append([None, element])
    return listOne


def getFileNameInFilePath(fileAddress):
    # 从路径下取出文件名和文件扩展名
    fileAddressList = fileAddress.split("/")  # 上级函数将保证路径只包含/路径分隔符
    filePath = fileAddressList[-1]  # ["C:/Users/admin/Desktop","1.dav"]
    return filePath


def YTcontrastTWDataHandle(EPW_ExcelDataTW_Data):
    # 参数为EPW原始数据和月台配置表的文件地址
    YTcontrastTWListSizeTemplate = [
        [0 for _ in range(len(YTcontrastTWEnum))]
        for _ in range(len(EPW_ExcelDataTW_Data))
    ]
    # 创建一个和月台对照表枚举数列相等大小的列表大小模板
    # 然后像VDPw一样先填充excel数据,然后添加月台相对应的范围参数
    tableDataList1 = fillExclData(YTcontrastTWListSizeTemplate, EPW_ExcelDataTW_Data)
    tableDataList2 = addYTRelativeRangeParameter(tableDataList1)
    return tableDataList2


def addYTRelativeRangeParameter(tableDataList1):
    # getYTConfigrationExcelData这个函数用的是VDP的 完全相同 不写轮子 了
    configData = getYTConfigrationExcelData()
    tableDataList = contrastYT(tableDataList1, configData)
    # 这个对比月台的函数需要ALw定制一下 然后 我要的是YT；线体范围；称台范围 上面函数全给了
    # 我这边对照月台肯定要数据处理一下
    return tableDataList


def contrastYT(tableDataList, configData):
    # 从配置表中找到相对应的月台后 取
    tableDataList.sort(key=lambda elem: elem[YTcontrastTWEnum.YT.value])
    # 传过来的数据先排个序
    for DLI, dataList in enumerate(tableDataList):
        dataListYTText = dataList[YTcontrastTWEnum.YT.value]
        for configList in configData:
            configDataYTText = configList[YTCETEnum.YTCOLUMN.value]
            if dataListYTText == configDataYTText:
                tableDataList[DLI][YTcontrastTWEnum.assemblyLineRange.value] = (
                    configList[YTCETEnum.ASSEMBLYLINERANGE.value]
                )
                tableDataList[DLI][YTcontrastTWEnum.weighingPlatformRange.value] = (
                    configList[YTCETEnum.BEDPLATERANGE.value]
                )
        if tableDataList[DLI][YTcontrastTWEnum.assemblyLineRange.value] == 0:
            tableDataList[DLI][YTcontrastTWEnum.assemblyLineRange.value] = "未找到"
            tableDataList[DLI][YTcontrastTWEnum.weighingPlatformRange.value] = "未找到"
            # 取两个列表的YT文本 对上了 就取列表相对应位置的元素
            # VDPw这个还做了一个IP排序 这边没用到就不用了
    return tableDataList


def fillExclData(YTcontrastTWListSizeTemplate, EPW_ExcelDataTW_Data):
    # 相对应的位置填充上EPW的原始数据
    for i in range(len(EPW_ExcelDataTW_Data)):
        YTcontrastTWListSizeTemplate[i][YTcontrastTWEnum.shipCopy.value] = (
            EPW_ExcelDataTW_Data[i][EDTWEnum.ShipID.value]
        )
        YTcontrastTWListSizeTemplate[i][YTcontrastTWEnum.YT.value] = (
            EPW_ExcelDataTW_Data[i][EDTWEnum.YT.value]
        )
        # 单号和月台
    return YTcontrastTWListSizeTemplate


if __name__ == "__main__":
    getAllFilesUnderThePath(
        r"C:\Users\admin\Documents\ATO\QMyWidgets\QMyALw", False, "dav"
    )

# 先用那什么库试一下
