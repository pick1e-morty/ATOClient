import datetime
import functools
import multiprocessing
import sys
import time
from datetime import timedelta
from pathlib import Path

from NetSDK.SDK_Enum import EM_USEDEV_MODE, EM_QUERY_RECORD_TYPE, EM_LOGIN_SPAC_CAP_TYPE
from NetSDK.SDK_Struct import NET_TIME, NET_RECORDFILE_INFO, NET_IN_PLAY_BACK_BY_TIME_INFO, NET_OUT_PLAY_BACK_BY_TIME_INFO, \
    C_LLONG, C_DWORD, C_LDWORD, NET_IN_LOGIN_WITH_HIGHLEVEL_SECURITY, NET_OUT_LOGIN_WITH_HIGHLEVEL_SECURITY, CB_FUNCTYPE, sys_platform, LOG_SET_PRINT_INFO
from NetSDK.SDK_Callback import fDisConnect, fHaveReConnect

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
    # print(lPlayHandle, dwTotalSize, dwDownLoadSize)
    # if dwDownLoadSize == -1:
    if dwDownLoadSize == 4294967295:
        sucessMsg = "下载成功"
        dahuaClient.sdk.StopDownload(lPlayHandle)
        logger.info(f"{dahuaClient.deviceAddress}{sucessMsg}")
        index = dahuaClient.handle_index.get(lPlayHandle)
        dahuaClient.updateDownloadStatusFun(index, sucessMsg)
    elif dwDownLoadSize == -2:
        errorMsg = dahuaClient.sdk.GetLastErrorMessage()
        logger.error(f"{dahuaClient.deviceAddress}下载失败{errorMsg}")
        index = dahuaClient.handle_index.get(lPlayHandle)
        dahuaClient.updateDownloadStatusFun(index, errorMsg)


class DahuaDownloader(object):

    def __init__(self, downloadResultList, downloadResultListCondition, devArgs: DevLoginAndDownloadArgSturct):
        self.downloadResultList = downloadResultList
        self.downloadResultListCondition = downloadResultListCondition
        self.devArgs = devArgs

        self.deviceAddress = self.devArgs.devIP

        self.sdk = NetClient()
        self.sdk.InitEx()
        time.sleep(3)

        global dahuaClient
        dahuaClient = self

        absLogPath = Path(__file__).parent
        absLogPath = absLogPath.joinpath("dh_netsdk_log/netsdk1.log")  # TODO 打包阶段时要将log统一对齐到rootPath/log文件夹下
        self.logopen(absLogPath)
        self.login()

        self.handle_index = {}

        self.startDownload()

        self.logout()
        self.logclose()
        self.cleanup()

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
            errorMsg = self.sdk.GetLastErrorMessage()
            logger.error(f"{self.deviceAddress}登陆失败{errorMsg}")
            self.updateDownloadStatusFun(0, errorMsg, DVWTableWidgetEnum.DOWNLOAD_PROGRESS_TABLE)
            sys.exit(1)
        else:
            sucessMsg = "登录成功"
            logger.info(f"{self.deviceAddress}{sucessMsg}")
            self.updateDownloadStatusFun(0, sucessMsg, DVWTableWidgetEnum.DOWNLOAD_PROGRESS_TABLE)

    def logopen(self, absLogPath):
        log_info = LOG_SET_PRINT_INFO()
        log_info.dwSize = sizeof(LOG_SET_PRINT_INFO)
        log_info.bSetFilePath = True
        log_info.szLogFilePath = str(absLogPath).encode('gbk')
        log_info.bSetFileNum = True  # 设置log数量仅保留一个，默认大小是10240kb
        log_info.nFileNum = 1
        logopenResult = self.sdk.LogOpen(log_info)
        if logopenResult != 1:
            errorMsg = self.sdk.GetLastErrorMessage()
            logger.error(f"{self.deviceAddress}打开日志失败{errorMsg}")
            self.updateDownloadStatusFun(0, errorMsg, DVWTableWidgetEnum.DOWNLOAD_PROGRESS_TABLE)
        else:
            sucessMsg = "打开日志成功"
            logger.info(f"{self.deviceAddress}{sucessMsg}")
            self.updateDownloadStatusFun(0, sucessMsg, DVWTableWidgetEnum.DOWNLOAD_PROGRESS_TABLE)

    def logclose(self):
        logcloseResult = self.sdk.LogClose()
        if logcloseResult != 1:
            errorMsg = self.sdk.GetLastErrorMessage()
            logger.error(f"{self.deviceAddress}关闭日志失败{errorMsg}")
            self.updateDownloadStatusFun(0, errorMsg, DVWTableWidgetEnum.DOWNLOAD_PROGRESS_TABLE)
        else:
            sucessMsg = "关闭日志成功"
            logger.info(f"{self.deviceAddress}{sucessMsg}")
            self.updateDownloadStatusFun(0, sucessMsg, DVWTableWidgetEnum.DOWNLOAD_PROGRESS_TABLE)

    def startDownload(self):
        time.sleep(3)
        for iNDEX, downloadArg in enumerate(self.devArgs.downloadArgList):
            time.sleep(1)
            # self.sdk.set_stream_type(0)  # 主码流
            startTime = downloadArg.downloadTime
            endTime = downloadArg.downloadTime + timedelta(seconds=1)
            startDateTime = self.datetime2NetTime(startTime)
            endDateTime = self.datetime2NetTime(endTime)
            nchannel = downloadArg.channel
            save_file_name = downloadArg.savePath

            downloadID = self.sdk.DownloadByTimeEx(self.loginID, nchannel, int(EM_QUERY_RECORD_TYPE.ALL),
                                                   startDateTime, endDateTime, save_file_name,
                                                   TimeDownLoadPosCallBack, 0,
                                                   DownLoadDataCallBack, 0)
            if not downloadID:
                text = f"{downloadID}{save_file_name}下载句柄为空，该录像下载失败"
                logger.error(text)
                status = "下载句柄为空"
                self.updateDownloadStatusFun(iNDEX, status)
                continue
            elif downloadID in self.handle_index.keys():
                # 如果这个句柄已经存在于我的副本中，就说明dvr内部已经释放了这个句柄了
                # 此时我不能在关闭这个句柄，中间的小小时差会让我手动关闭本次刚拿到却还没开始传输的下载句柄
                self.handle_index[downloadID] = iNDEX  # 这个是冗余的，是为了获取最大时效性。
                index = self.handle_index.get(downloadID)
                # self.updateDownloadStatusFun(index, "被DVR自动关闭了")
                logger.warning(f"{downloadID}{save_file_name}被DVR自动关闭了")

            print(downloadID, save_file_name)
            self.handle_index[downloadID] = iNDEX
            print(self.handle_index)
        time.sleep(3)

    def logout(self):
        result = self.sdk.Logout(self.loginID)
        if result == 0:
            errorMsg = self.sdk.GetLastErrorMessage()
            logger.error(f"{self.deviceAddress}登出失败{errorMsg}")
            self.updateDownloadStatusFun(0, errorMsg, DVWTableWidgetEnum.DOWNLOAD_PROGRESS_TABLE)
        else:
            sucessMsg = "登出成功"
            logger.info(f"{self.deviceAddress}{sucessMsg}")
            self.updateDownloadStatusFun(0, sucessMsg, DVWTableWidgetEnum.DOWNLOAD_PROGRESS_TABLE)

    def cleanup(self):
        self.sdk.Cleanup()

    def datetime2NetTime(self, v_datetime: datetime.datetime):
        nettime = NET_TIME()
        nettime.dwYear = v_datetime.year
        nettime.dwMonth = v_datetime.month
        nettime.dwDay = v_datetime.day
        nettime.dwHour = v_datetime.hour
        nettime.dwMinute = v_datetime.minute
        nettime.dwSecond = v_datetime.second
        return nettime


if __name__ == '__main__':
    from _testLoginConfig import testUserConfig

    manager = multiprocessing.Manager()
    t_downloadResultList = manager.list()
    t_downloadResultListCondition = manager.Condition()
    DahuaDownloader(t_downloadResultList, t_downloadResultListCondition, testUserConfig)
