import os.path
from datetime import timedelta, datetime
from tkinter import messagebox
from openpyxl import load_workbook
from openpyxl.utils.exceptions import InvalidFileException
from app.QMyVDPw.Libs.QMyVDPwEnum import YTCETEnum, SHTWEnum, DataForDownloadListEnum as DFDLE, \
    DownloadParmeterListEnum as DPLE, DownloadDurationText2TimeSec
from app.esheet_process_widget.epw_define import EDTWEnum

DataHandlingFileAddress = os.path.dirname(os.path.realpath(__file__))  # 本文件路径
relativeFILEADDRESS = "..\\..\\..\\custom\\月台配置.xlsx"  # 配置文件相对于当前文件的路径
YTconfigrationFileAddress = os.path.join(DataHandlingFileAddress, relativeFILEADDRESS)  # 合并


# 因为有两个不同层级的文件要调用这个模块 所以用的这种方法来设置相对路径


# 枚举自取 不再传了
def shipHandleTWInitDataHandle(EPW_ExcelDataTW_Data, DefaultDownLoadTimeCBText):
    # 参数为原始数据，想要添加的文本数据，文本索引，文件地址，要将文件中的数据添加到数据中的索引，文件中对比月台的位置索引
    # 单号处理表格的初始化数据追加数据  就是一个列表元素是列表的三维列表 第三维是那些文本   # 注意这个变量的花里胡哨的名称
    rows = len(EPW_ExcelDataTW_Data)
    cols = len(SHTWEnum)
    shipHandleTWSizeListTemplate = [[0 for _ in range(cols)] for _ in range(rows)]
    # 这个就是同表格大小的二维列表 所有的数据填充 都要在这个列表的规格下进行数值取代而不再有insert和append
    # 这将实现一键枚举数据换列 还有变量名我给加了序号 这个填充虽然是不需要按顺序的

    sHTWSL1 = fillExcelData(shipHandleTWSizeListTemplate, EPW_ExcelDataTW_Data)
    sHTWSL2 = fillDefaultDownloadTime(sHTWSL1, DefaultDownLoadTimeCBText)
    sHTWSL3 = addYTRelativeHCVR_IP_Channel(sHTWSL2)
    if sHTWSL3:
        return sHTWSL3
    else:
        return


def fillExcelData(SHTWSL, EPW_ExcelDataTW_Data):
    # 向模板中填充需要的原始excel数据
    for i in range(len(EPW_ExcelDataTW_Data)):
        SHTWSL[i][SHTWEnum.YT.value] = EPW_ExcelDataTW_Data[i][EDTWEnum.YT.value]
        SHTWSL[i][SHTWEnum.Folder.value] = EPW_ExcelDataTW_Data[i][EDTWEnum.ExcelFileName.value]
        SHTWSL[i][SHTWEnum.FileName.value] = EPW_ExcelDataTW_Data[i][EDTWEnum.ShipID.value]
        SHTWSL[i][SHTWEnum.DLTime.value] = EPW_ExcelDataTW_Data[i][EDTWEnum.ScanTime.value]
    return SHTWSL


def fillDefaultDownloadTime(sHTSLT, value):
    # 在初始化数据末尾添加下载时长
    for i in range(len(sHTSLT)):
        sHTSLT[i][SHTWEnum.DLDuration.value] = value  # 在模板中对枚举规定的位置替换数值 并返回
    return sHTSLT


def addYTRelativeHCVR_IP_Channel(sHTSLT):
    # 在初始化数据末尾添加月台相对应的录像机IP和通道
    # 从这开始就要处理那个月台的excel了 分化到Lib中

    configData = getYTConfigrationExcelData()
    if configData:
        returnSHTSLT = contrastYT(sHTSLT, configData)
        return returnSHTSLT


def contrastYT(sHTSLT, configData):
    # 对比inidata中YTGlobalIndex列和ConfigData的fileYTIndex中的数据如果对的上 就插入在inidata中iniDataYTIndex数据列中
    preDataText = None
    preDataList = None
    # 先对月台拍个序 然后这边就可以做个优化的操作
    # 也就是上一个匹配的文本直接用到现在这个文本上
    sHTSLT.sort(key=lambda elem: elem[SHTWEnum.YT.value])

    for DLI, dataList in enumerate(sHTSLT):
        sHTSLTYTText = dataList[SHTWEnum.YT.value]
        for configList in configData:
            configDataYTText = configList[YTCETEnum.YTCOLUMN.value]  # 遍历两个表格 分别对比指定索引下的文本是否相同
            if sHTSLTYTText == configDataYTText:  # 相同就给初始化数据追加一个相对应的配置列表
                sHTSLT[DLI][SHTWEnum.HCVRIP.value] = configList[YTCETEnum.IP.value]  # 数据收集表的指定枚举列赋值为配置列表的指定枚举列
                sHTSLT[DLI][SHTWEnum.Channel.value] = configList[YTCETEnum.CHANNEL.value]
                sHTSLT[DLI][SHTWEnum._HCVRConfig.value] = configList
        if sHTSLT[DLI][SHTWEnum.HCVRIP.value] == 0:  # 注意这个0并不安全 万一这个位置被提前改变就完蛋了
            sHTSLT[DLI][SHTWEnum.HCVRIP.value] = '未找到'
            sHTSLT[DLI][SHTWEnum.Channel.value] = '未找到'
    sHTSLT.sort(key=lambda elem: elem[SHTWEnum.HCVRIP.value])  # 最后对IP排个序
    # 但是现在通道并不是按照循序的 如果想要对通道排序且IP循序不变 就需要想EPw的三维排序的那套操作
    # 但月台的顺序是从大到小的 而且现在数量也小 我就先不写了 要写的话EPw那套直接改成个函数得了
    return sHTSLT


def getYTConfigrationExcelData():
    fileAdress = YTconfigrationFileAddress
    configData = []
    if fileAdress:
        print("本次处理的Excel文件地址为:" + str(fileAdress))
        # 获取四个指定行列
        try:
            # 加载excel文件
            wb = load_workbook(fileAdress)
            ws = wb.active  # 激活这个workbook
            ws.delete_rows(1)  # 删除标题 注意他这个索引不是从零开始的
            for rowData in ws.values:
                configData.append(list(rowData))
        except InvalidFileException:
            messagebox.showinfo("文件格式错误", "只支持xlsx")
            print("文件格式错误" + str(fileAdress))
            return
        except FileNotFoundError:  # 因为pyqt的弹窗都需要父组件，那太浪费了
            messagebox.showinfo("Excel文件不存在", str(fileAdress))
            print("文件查找错误" + str(fileAdress))
            return
        filterValue(configData, None)
    else:
        return None
    print(configData)
    return configData


def filterValue(data, value):  # 对列表过滤指定数据 我发现Excel中总是爱出现None，万一数量多的话太影响性能
    for Index, element in enumerate(data):
        valueNum = element.count(value)
        if valueNum != 0:
            data.pop(Index)

    return data


# ------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------
# 这个分割线以下都是另一个组件需要用到的函数

def getSameIPNumList(tableData):
    allIPList = []
    for ListData in tableData:  # 统计所有指定索引元素
        iP_ChannelList = ListData[SHTWEnum.HCVRIP.value]
        # print(iP_ChannelList)
        ip = iP_ChannelList.split('-')[0]
        allIPList.append(ip)

    iPCount = {}  # 统计相同元素出现的次数
    for ip in allIPList:
        if ip in iPCount:
            iPCount[ip] = iPCount[ip] + 1
        # print(ip)
        else:
            iPCount[ip] = 1
    print(iPCount)

    dictlist = []  # 字典转列表
    for keys, value in iPCount.items():
        temp = [keys, value]
        dictlist.append(temp)

    return dictlist


# ### ------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------
# 这个分割线以下都是另一个功能

def ProcessDataForDownload(sHTWV):
    # 列表第一列元素是配置表 第二列也是一个列表 存的是好多单号
    # 第一列从相同IP中划分获取
    #
    dataIntegration = []
    IpSet = set()
    [IpSet.add(listData[SHTWEnum.HCVRIP.value]) for listData in sHTWV if
     listData[SHTWEnum.HCVRIP.value] not in IpSet and listData[SHTWEnum.HCVRIP.value] != "未找到"]

    # IP独一集合 另外不统计IPtext为 未找到; 夭寿啦 做in判断居然比一并add速度要快 这个内存的写入和读取？
    [dataIntegration.append([IPText, [], []]) for IPText in IpSet]
    # 配合IP集合做个一层初始化 这样写好处是非常大的 因为这个列表最大是五维 就算判断行首的IPText也是一个二维元素
    # 这是我想了好久的结构 应该只能这么写了
    # list = [
    #     ["text1", [], [[], [], []]],
    #     ["text2", [], [[], [], []]],
    #     ["text3", [], [[], [], []]],
    # ]
    IpSet = list(IpSet)  # 集合转列表 推出index功能

    for listData in sHTWV:  #
        IpText = listData[SHTWEnum.HCVRIP.value]
        # 得到这个列表的IP文本值 然后获取到大一统中这个文本所在的位置 把配置列表和单号数据添加进去
        if IpText == "未找到":  # 返回的列表是要直接传给DaHua模块的 找不到设备配置的单号就不要统计处理了
            continue
        IpListIndex = IpSet.index(IpText)  # 得到当前IP文本所在数据整合列表中的位置

        if not len(dataIntegration[IpListIndex][DFDLE.DevicesConfig.value]):  # 如果当前列表中的
            # list = [
            #     ["text1", [这个位置], [[], [], []]],
            #     ["text2", [], [[], [], []]],
            #     ["text3", [], [[], [], []]],
            # ]
            # 是空的 就把新的数据给填充进去 if比add 所以
            HCVRConfig = processDevicesConfigList(listData[SHTWEnum._HCVRConfig.value])
            dataIntegration[IpListIndex][DFDLE.DevicesConfig.value] = HCVRConfig
        DownloadParmeterList = processDownloadParmeterList(listData)
        dataIntegration[IpListIndex][DFDLE.ShipIDs.value].append(DownloadParmeterList)
        # 之后再把处理过的单号配置列表添加到
        # list = [
        #     ["text1", [设备配置列表], [[这个地方], [], []]],
        #     ["text2", [], [[], [], []]],
        #     ["text3", [], [[], [], []]],
        # ]
    return dataIntegration


def processDevicesConfigList(HCVRConfig):
    videoStreamText = HCVRConfig[YTCETEnum.VIDEOSTREAM.value]
    if videoStreamText == "主码流":
        HCVRConfig[YTCETEnum.VIDEOSTREAM.value] = 0
    elif videoStreamText == "辅码流":
        HCVRConfig[YTCETEnum.VIDEOSTREAM.value] = 1
    else:
        print("视频码流配置错误")
    return HCVRConfig


def processDownloadParmeterList(sHTWV_element):
    # 这个element是大列表的其中一个元素
    channel = sHTWV_element[SHTWEnum.Channel.value]
    folder = sHTWV_element[SHTWEnum.Folder.value]
    fileName = sHTWV_element[SHTWEnum.FileName.value]
    downloadTime = sHTWV_element[SHTWEnum.DLTime.value]
    downloadDuration = sHTWV_element[SHTWEnum.DLDuration.value]
    # 按照枚举索引取出需要用到的数据
    # 因为我只传过来了一个下载时长的中文 所以规范的转换一下 就是从枚举里面取出秒数
    downloadDarationEnumParmeter = DownloadDurationText2TimeSec[downloadDuration]
    downloadDurationTimeSec = eval(str(downloadDarationEnumParmeter) + ".value")
    theFormer = downloadDurationTimeSec // 2
    # 这两个时间的处理 一秒和五秒是有差别的 配置五秒的时候记得再看一下这个地方 会是多少
    theLatter = downloadDurationTimeSec // 2 + 1
    inidatatime = datetime.strptime(downloadTime, "%Y-%m-%d %H:%M:%S")
    # 转换时间类型后再进行加减操作 防止发生出现11:24:60 这个不存在的秒数
    theFormerSecTime = timedelta(seconds=theFormer)
    theLatterSecTime = timedelta(seconds=theLatter)
    startTime = inidatatime - theFormerSecTime
    endTime = inidatatime + theLatterSecTime
    currentPath = os.path.abspath(os.curdir)
    parentPath = os.path.join(currentPath, "videoprocess")
    fileName = fileName + ".dav"
    fileAbsPath = os.path.join(parentPath, folder, fileName)
    # 整合数据列表 按照枚举索引取 最后按照枚举索引存 我发现这样规定后 有的糖都不能吃了
    downLoadParmeterList = [0 for i in range(len(DPLE))]
    downLoadParmeterList[DPLE.Channel.value] = channel
    downLoadParmeterList[DPLE.StartTime.value] = startTime
    downLoadParmeterList[DPLE.EndTime.value] = endTime
    downLoadParmeterList[DPLE.FileAbsPath.value] = fileAbsPath
    return downLoadParmeterList
