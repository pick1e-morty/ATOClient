import multiprocessing
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QWidget, QListWidgetItem, QTableWidgetItem)
from typing import List

from app.download_video_widget.UI.ui_DownloadVideo import Ui_DVW_Widget
from app.download_video_widget.utils.progress_bar import PercentProgressBar
# from app.download_video_widget.netsdk.dahua_async_download import dahuaDownloader
from app.esheet_process_widget.epw_define import ExcelFileListWidgetItemDataStruct
from app.download_video_widget.dvw_define import DownloadArg, DevLoginAndDownloadArgSturct


class DVWclass(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)  # 调用父类构造函数，创建窗体
        self.classifyByDevIP = None
        self.ui = Ui_DVW_Widget()  # 创建UI对象
        self.ui.setupUi(self)  # 构造UI界面

        # formsConfigDict = parent.formsConfigDict  # dvw界面暂时没有配置
        # self.dvw_config = formsConfigDict["dvw"]
        self.devConfigGenerate = parent.devConfigGenerate

    def classifyArg(self, eflw_ItemDataList: List[ExcelFileListWidgetItemDataStruct]):
        # TODO 下面两个分类可以做到一个for里，但那样的复杂度和时间消耗貌似
        # classifyByYT = {}
        self.classifyByDevIP = {}
        # 先按照月台对所有单号进行分类
        rootPath = Path(__file__).parent.parent
        for eflw_ItemData in eflw_ItemDataList:
            folderName = Path(eflw_ItemData.excelFilePath).stem
            for edtw_ItemData in eflw_ItemData.edtw_ItemDataList:
                # 分类的同时获取到最终的保存文件路径
                filePath = str(rootPath / folderName / (str(edtw_ItemData.shipID) + ".jpg"))
                scanTime = edtw_ItemData.scanTime
                v_ytName = edtw_ItemData.ytName
                devConfig = self.devConfigGenerate.send(v_ytName)
                if devConfig is None:  # 只有能拿到配置的月台才会进行后续处理
                    continue  # 且是必须存在的，所以未配置月台的筛选过程就放到dvw这边了
                devArgStruct = isDevIpExist = self.classifyByDevIP.get(devConfig.devIP, None)
                if isDevIpExist is None:  # 我存了两个变量名
                    devArgStruct = DevLoginAndDownloadArgSturct()  # 一个用来判断，一个用来指向数据结构
                    devArgStruct.devType = devConfig.devType  # 如果数据类实例不存在，就新建一个，然后指向这个数据类实例
                    devArgStruct.devIP = devConfig.devIP
                    devArgStruct.devPort = devConfig.devPort
                    devArgStruct.devUserName = devConfig.devUserName
                    devArgStruct.devPassword = devConfig.devPassword

                v_channel = devConfig.devChannel
                downloadArg = DownloadArg(savePath=filePath, downloadTime=scanTime, ytName=v_ytName, channel=v_channel)
                devArgStruct.downloadArgList.append(downloadArg)  # 如果数据类实例存在，那就直接改呗
                self.classifyByDevIP[devConfig.devIP] = devArgStruct  # 重新改一下字典的value，应该也不算什么大事，不然就得写重复代码了

    def startDownload(self):
        # 下载进度      拖家带口全部传进去

        downloadResult = multiprocessing.Queue()

        with ProcessPoolExecutor() as executor:
            for devIP, devArgStruct in self.classifyByDevIP.items():
                print(devIP, devArgStruct.downloadArg.keys(), devArgStruct.devType)
                if devArgStruct.devType == "dahua":
                    pass
                    # dahuaDownloader
                elif devArgStruct.devType == "haikang":
                    pass

    def addDownloadList(self, eflw_ItemDataList: List[ExcelFileListWidgetItemDataStruct]):
        # 处理上层数据
        self.classifyArg(eflw_ItemDataList)
        # 分类之后填充几个组件     显示下载总量
        row = 0
        Count = 0  #
        self.ui.ipCount_TW.clear()
        for devIP, devArgStruct in self.classifyByDevIP.items():
            print(devArgStruct.downloadArgList)
            inIp_count = len(devArgStruct.downloadArgList)
            Count += inIp_count
            aItem = QTableWidgetItem(str(devIP))
            aItem.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.ui.ipCount_TW.setItem(row, 0, aItem)

            aItemWidget = PercentProgressBar()  # 设置第二列单元格为 带百分比的进度条
            aItemWidget.setMaximum(inIp_count)
            self.ui.ipCount_TW.setCellWidget(row, 1, aItemWidget)

            # aItem = QTableWidgetItem(str(inIp_count))
            # aItem.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            # self.ui.ipCount_TW.setItem(row, 1, aItem)
            row += 1  # 换行
        self.ui.argsCount_TL.setText(f"下载进度 (共{Count}个)")


if __name__ == "__main__":  # 用于当前窗体测试

    app = QApplication(sys.argv)  # 创建GUI应用程序
    forms = DVWclass()  # 创建窗体

    # forms.addFilePathsToexcelFile_LWData([__filePath1])
    forms.show()

    sys.exit(app.exec_())
