import os
import time
from ctypes import sizeof, c_int, POINTER, c_ubyte
from threading import Thread
from NetSDK.NetSDK import NetClient
from NetSDK.SDK_Callback import fDisConnect, fHaveReConnect
from NetSDK.SDK_Enum import EM_LOGIN_SPAC_CAP_TYPE, EM_USEDEV_MODE, EM_QUERY_RECORD_TYPE
from NetSDK.SDK_Struct import NET_IN_LOGIN_WITH_HIGHLEVEL_SECURITY, NET_OUT_LOGIN_WITH_HIGHLEVEL_SECURITY, NET_TIME, \
    CB_FUNCTYPE, C_LLONG, C_DWORD, C_LDWORD, NET_RECORDFILE_INFO


from app.QMyVDPw.Libs.QMyVDPwEnum import YTCETEnum, DownloadParmeterListEnum


def DisConnectCallBack(lLoginID, pchDVRIP, nDVRPort, dwUser):
    print("设备掉线" + str(pchDVRIP))


# 实现断线重连回调函数功能
def ReConnectCallBack(lLoginID, pchDVRIP, nDVRPort, dwUser):
    print("设备重新登录成功" + str(pchDVRIP))


@CB_FUNCTYPE(c_int, C_LLONG, C_DWORD, POINTER(c_ubyte), C_DWORD, C_LDWORD)
def DownLoadDataCallBack(lPlayHandle, dwDataType, pBuffer, dwBufSize, dwUser):
    # 返回下载内容的
    # buf_data = cast(pBuffer, POINTER(c_ubyte * dwBufSize)).contents
    # with open('./buffer.dav', 'ab+') as buf_file:
    #     buf_file.write(buf_data)
    return 1


@CB_FUNCTYPE(None, C_LLONG, C_DWORD, C_DWORD, c_int, NET_RECORDFILE_INFO, C_LDWORD)
def TimeDownLoadPosCallBack(lPlayHandle, dwTotalSize, dwDownLoadSize, index, recordfileinfo, dwUser):
    # 返回下载进度的
    try:
        # wnd.update_download_progress_thread(dwTotalSize, dwDownLoadSize)
        print(lPlayHandle, dwTotalSize, dwDownLoadSize, index, recordfileinfo, dwUser)
        if dwDownLoadSize == 4294967295:  # 原本这个数值应该是-1 但应该是c_dword类型转换的时候给转掉了
            print("关闭" + str(lPlayHandle) + "下载接口结果为：", str(NetClient.StopDownload(lPlayHandle)))
    except Exception as e:
        print(e)



class MyDaHuaNetClient():

    def __init__(self, deviceConfigList=None, downLoadParmeterList=None):
        print("初始化MyDaHuaNetClient")
        super().__init__()
        print("执行MyDaHuaNetClient的父类构造函数")

        self.deviceConfigList = deviceConfigList
        self.downLoadParmeterList = downLoadParmeterList
        print(str(self.deviceConfigList))
        print(str(self.downLoadParmeterList))
        if self.iniNetSDK() == 1 or self.login() == 1:
            self.closeInSeconds(5)  # 初始化和登录函数 如果有一个失败则返回1 然后这边倒数指定时间退出
        else:
            self.downLoadVideos()

    def iniNetSDK(self):
        # 初始化大华的sdk
        self.loginID = C_LLONG()
        self.downLoadID = C_LLONG()
        self.m_DisConnectCallBack = fDisConnect(DisConnectCallBack)  # 文档中应该是让重写这个函数的fDisConnect
        self.m_ReConnectCallBack = fHaveReConnect(ReConnectCallBack)

        self.daHuaClient = NetClient()
        iniResult = self.daHuaClient.InitEx(self.m_DisConnectCallBack)  # 初始化SDK 并设置断线回调函数
        if iniResult == 1:
            print("初始化NetSDK成功")
        elif iniResult == 0:
            print("初始化NetSDK失败")
            print(str(self.daHuaClient.GetLastErrorMessage()))
            return 1
        self.daHuaClient.SetAutoReconnect(self.m_ReConnectCallBack)  # 设置自动重连回连函数

    def login(self):
        if not self.loginID:
            stuInParam = NET_IN_LOGIN_WITH_HIGHLEVEL_SECURITY()
            stuInParam.dwSize = sizeof(NET_IN_LOGIN_WITH_HIGHLEVEL_SECURITY)
            ip = self.deviceConfigList[YTCETEnum.IP.value]
            stuInParam.szIP = ip.encode()
            stuInParam.nPort = int(self.deviceConfigList[YTCETEnum.PORT.value])
            stuInParam.szUserName = self.deviceConfigList[YTCETEnum.USERNAME.value].encode()
            stuInParam.szPassword = self.deviceConfigList[YTCETEnum.PASSWORD.value].encode()
            stuInParam.emSpecCap = EM_LOGIN_SPAC_CAP_TYPE.TCP  # 多数参数是从列表中靠枚举索引取得
            stuInParam.pCapParam = None  # 有些需要二进制编码 还有些是从大华模块中取出来的参数
            stuOutParam = NET_OUT_LOGIN_WITH_HIGHLEVEL_SECURITY()  # 标准输出参数类型
            stuOutParam.dwSize = sizeof(NET_OUT_LOGIN_WITH_HIGHLEVEL_SECURITY)  # 指定该实例空间大小 老c语言了
            self.loginID, deviceInfo, errorMsg = self.daHuaClient.LoginWithHighLevelSecurity(stuInParam, stuOutParam)
            if self.loginID != 0:
                print(str(ip) + "登录成功")
                self.set_stream_type(self.deviceConfigList[YTCETEnum.VIDEOSTREAM.value])
            else:
                print(str(ip) + "登录失败")
                print(str(self.daHuaClient.GetLastErrorMessage()))
                return 1
        else:
            pass

    def downLoadVideos(self):
        theThread = Thread(target=self.downLoadVideosFunc)
        theThread.start()

    def downLoadVideosFunc(self):
        for index, videoParmeter in enumerate(self.downLoadParmeterList):
            # 获得通道
            channel = int(videoParmeter[DownloadParmeterListEnum.Channel.value]) - 1  # netsdk的通道是从零开始的

            # 处理文件地址
            saveFileName = videoParmeter[DownloadParmeterListEnum.FileAbsPath.value]
            print(saveFileName)
            self.makePathExists(saveFileName)

            # 处理时间
            startDateTime = videoParmeter[DownloadParmeterListEnum.StartTime.value]
            endDateTime = videoParmeter[DownloadParmeterListEnum.EndTime.value]
            startNetTime, endNetTime = self.dateTime2NetTime(startDateTime, endDateTime)

            self.downLoadID = self.daHuaClient.DownloadByTimeEx(self.loginID, channel,
                                                                int(EM_QUERY_RECORD_TYPE.ALL),
                                                                startNetTime, endNetTime, saveFileName,
                                                                TimeDownLoadPosCallBack, 0, DownLoadDataCallBack, index)
            # time.sleep(3)

            if self.downLoadID:
                print(str(saveFileName) + "下载成功")
            else:
                print(str(saveFileName) + "下载失败")
                print(str(self.daHuaClient.GetLastErrorMessage()))

        print("全部处理完毕")
        self.closeInSeconds(5)

    def dateTime2NetTime(self, startTime, endTime):
        # datetime类型实例转换大华的nettime对象实例
        startNetTime = NET_TIME()
        startNetTime.dwYear = startTime.year
        startNetTime.dwMonth = startTime.month
        startNetTime.dwDay = startTime.day
        startNetTime.dwHour = startTime.hour
        startNetTime.dwMinute = startTime.minute
        startNetTime.dwSecond = startTime.second

        endNetTime = NET_TIME()
        endNetTime.dwYear = endTime.year
        endNetTime.dwMonth = endTime.month
        endNetTime.dwDay = endTime.day
        endNetTime.dwHour = endTime.hour
        endNetTime.dwMinute = endTime.minute
        endNetTime.dwSecond = endTime.second

        return startNetTime, endNetTime

    def makePathExists(self, fileAbsPath):
        # 使路径存在
        filePath = fileAbsPath.replace("\\", "/")
        filePath = filePath.split('/')
        fileFolderPathList = filePath[:-1]  # 文件地址以/分段后 取第一个元素到倒数第二个元素 这样就把文件名给去除掉了
        fileFolderPath = "/".join(fileFolderPathList)  # 文件地址列表以/重组
        if os.path.exists(fileFolderPath) is not True:  # 如果路径不存在
            print(str(fileFolderPath) + "该路径不存在 将创建")
            try:
                os.makedirs(fileFolderPath)
            except FileExistsError:
                print(str(fileFolderPath) + "文件夹已存在")

    def set_stream_type(self, stream_type):
        # set stream type;设置码流类型
        stream_type = c_int(stream_type)
        result = self.daHuaClient.SetDeviceMode(self.loginID, int(EM_USEDEV_MODE.RECORD_STREAM_TYPE), stream_type)
        if not result:
            print('提示(prompt)' + str(self.daHuaClient.GetLastErrorMessage()))
            return 0

    def closeInSeconds(self, sec):
        pass
        # theThread = Thread(target=self.closeInSecondsFunc, args=[sec, ])
        # theThread.start()
        # time.sleep(5)
        # exit(0)

    def closeInSecondsFunc(self, sec):
        print("窗口" + str(sec) + "秒后关闭")
        second = sec - 1
        for i in range(second, -1, -1):
            print(str(i + 1))
            time.sleep(1)
        # exit(0)


if __name__ == '__main__':
    pass
