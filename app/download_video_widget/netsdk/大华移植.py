import datetime
import functools
import sys
from datetime import timedelta

from NetSDK.NetSDK import NetClient
from NetSDK.SDK_Enum import EM_LOGIN_SPAC_CAP_TYPE, EM_QUERY_RECORD_TYPE
from NetSDK.SDK_Struct import *
from UnifyNetSDK.dahua.dh_netsdk_exception import DHNetSDKException
from UnifyNetSDK.dahua.dh_netsdk_exception import ErrorCode
from ctypes import sizeof

from loguru import logger

from app.download_video_widget.dvw_define import DevLoginAndDownloadArgSturct, DVWTableWidgetEnum

dahuaClient = None


@CB_FUNCTYPE(c_int, C_LLONG, C_DWORD, POINTER(c_ubyte), C_DWORD, C_LDWORD)
def DownLoadDataCallBack(lPlayHandle, dwDataType, pBuffer, dwBufSize, dwUser):
    return 1


@CB_FUNCTYPE(None, C_LLONG, C_DWORD, C_DWORD, c_int, NET_RECORDFILE_INFO, C_LDWORD)
def TimeDownLoadPosCallBack(lPlayHandle, dwTotalSize, dwDownLoadSize, index, recordfileinfo, dwUser):
    if dwDownLoadSize == -1:
        dahuaClient.StopDownload(lPlayHandle)
        logger.success("下载成功")
    elif dwDownLoadSize == -2:
        logger.error("下载失败")


class dahuaDownloaderdahuaDownloader():

    def __init__(self, downloadResultList, downloadResultListCondition, devArgs: DevLoginAndDownloadArgSturct):
        self.downloadResultList = downloadResultList
        self.downloadResultListCondition = downloadResultListCondition
        self.devArgs = devArgs

        self.deviceAddress = self.devArgs.devIP

        self.sdk = NetClient()
        self.sdk.InitEx()
        global dahuaClient
        dahuaClient = self.sdk
        self.login()

    def updateDownloadStatusFun(self, f_iNDEX, f_status, widgetEnum: DVWTableWidgetEnum = DVWTableWidgetEnum.DOWNLOAD_STATUS_TABLE):
        """
        统一上报状态的函数,DVWTableWidgetEnum默认是下载状态表格DOWNLOAD_STATUS_TABLE，多数数据都是往这个表格上报的
        如果widgetEnum = DOWNLOAD_PROGRESS_TABLE，那f_iNDEX就是没有意义的数字
        跟下载参数downloadArg有关的都是往下载状态表格上报的
        跟sdkClient有关的都是往下载进度表格上报的，因为sdkClient是下载进度表格的单位
        """
        self.downloadResultList.append([widgetEnum, self.deviceAddress, f_iNDEX, f_status])
        with self.downloadResultListCondition:
            self.downloadResultListCondition.notify()

    def updateStatusDecorator(self, sucessText, errorText, widgetEnum=DVWTableWidgetEnum.DOWNLOAD_PROGRESS_TABLE):
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    executeResult = func(*args, **kwargs)
                    logger.info(f"{self.deviceAddress}{sucessText}")
                    self.updateDownloadStatusFun(0, sucessText, widgetEnum)
                    return executeResult
                except DHNetSDKException as e:
                    logger.error(f"{self.deviceAddress}{errorText},{e}")
                    errorStr = str(e) + errorText
                    self.updateDownloadStatusFun(0, errorStr, widgetEnum)
                    sys.exit(1)

            return wrapper

        return decorator

    @updateStatusDecorator("登录成功", "登录失败")
    def login(self):
        stuInParam = NET_IN_LOGIN_WITH_HIGHLEVEL_SECURITY()
        stuInParam.dwSize = sizeof(NET_IN_LOGIN_WITH_HIGHLEVEL_SECURITY)
        stuInParam.szIP = self.devArgs.devIP.encode()
        stuInParam.nPort = self.devArgs.devPort
        stuInParam.szUserName = self.devArgs.devUserName.encode()
        stuInParam.szPassword = self.devArgs.devPassword.encode()
        stuInParam.emSpecCap = EM_LOGIN_SPAC_CAP_TYPE.TCP
        stuInParam.pCapParam = None

        stuOutParam = NET_OUT_LOGIN_WITH_HIGHLEVEL_SECURITY()
        stuOutParam.dwSize = sizeof(NET_OUT_LOGIN_WITH_HIGHLEVEL_SECURITY)

        self.loginID, device_info, error_msg = self.sdk.LoginWithHighLevelSecurity(stuInParam, stuOutParam)
        if self.loginID == 0:
            errorIndex = self.sdk.GetLastError()
            errorText = ErrorCode[errorIndex]
            logger.error(f"{errorIndex} {errorText}")
            raise DHNetSDKException(errorIndex, errorText)

    @updateStatusDecorator("打开日志成功", "打开日志失败")
    def logopen(self, absLogPath):

        log_info = LOG_SET_PRINT_INFO()
        log_info.dwSize = sizeof(LOG_SET_PRINT_INFO)
        log_info.bSetFilePath = True
        log_info.szLogFilePath = str(absLogPath).encode('gbk')
        log_info.bSetFileNum = True  # 设置log数量仅保留一个，默认大小是10240kb
        log_info.nFileNum = 1
        self.sdk.LogOpen(log_info)

    @updateStatusDecorator("关闭日志成功", "关闭日志失败")
    def logclose(self):
        self.sdk.LogClose()

    def startDownload(self):
        for iNDEX, downloadArg in enumerate(self.devArgs.downloadArgList):
            # self.sdk.set_stream_type(0)  # 主码流
            startTime = downloadArg.downloadTime
            endTime = downloadArg.downloadTime + timedelta(seconds=1)
            startDateTime = self.datetime2NetTime(startTime)
            enddateTime = self.datetime2NetTime(endTime)
            nchannel = downloadArg.channel
            save_file_name = downloadArg.savePath

            downloadID = self.sdk.DownloadByTimeEx(self.loginID, nchannel, int(EM_QUERY_RECORD_TYPE.ALL),
                                                   startDateTime, enddateTime, save_file_name,
                                                   TimeDownLoadPosCallBack, 0,
                                                   DownLoadDataCallBack, 0)

    @updateStatusDecorator("登出成功", "登出失败")
    def logout(self):
        pass

    @updateStatusDecorator("释放资源成功", "释放资源失败")
    def cleanup(self):

        pass

    def datetime2NetTime(self, v_datetime: datetime.datetime):
        nettime = NET_TIME()
        nettime.dwYear = v_datetime.year
        nettime.dwMonth = v_datetime.month
        nettime.dwDay = v_datetime.day
        nettime.dwHour = v_datetime.hour
        nettime.dwMinute = v_datetime.minute
        nettime.dwSecond = v_datetime.second
        return nettime
