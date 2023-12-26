import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from PyQt5.QtWidgets import (QApplication, QWidget)
from typing import List

from app.download_video_widget.UI.ui_DownloadVideo import Ui_DVW_Widget
from app.esheet_process_widget.epw_define import ExcelFileListWidgetItemDataStruct
from app.download_video_widget.dvw_define import DownloadArg, DevLoginAndDownloadArgSturct


class DVWclass(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)  # 调用父类构造函数，创建窗体
        self.ui = Ui_DVW_Widget()  # 创建UI对象
        self.ui.setupUi(self)  # 构造UI界面

        # formsConfigDict = parent.formsConfigDict  # dvw界面暂时没有配置
        # self.dvw_config = formsConfigDict["dvw"]
        self.devConfigGenerate = parent.devConfigGenerate

    def addDownloadList(self, eflw_ItemDataList: List[ExcelFileListWidgetItemDataStruct]):
        # 处理上层数据
        classifyByYT = {}
        # 先按照月台对所有单号进行分类
        rootPath = Path(__file__).parent.parent
        for eflw_ItemData in eflw_ItemDataList:
            folderName = Path(eflw_ItemData.excelFilePath).stem
            for edtw_ItemData in eflw_ItemData.edtw_ItemDataList:
                # 分类的同时获取到最终的保存文件路径
                filePath = str(rootPath / folderName / (str(edtw_ItemData.shipID) + ".jpg"))
                scanTime = edtw_ItemData.scanTime
                downloadArg = DownloadArg(filePath, scanTime)
                ytName = edtw_ItemData.ytName
                classifyByYT[ytName] = classifyByYT.get(ytName, []) + [downloadArg]
        # 然后按照IP合并,这一步就可以月台匹配设备配置了
        classifyByDevIP = {}
        for ytName, downloadArgs in classifyByYT.items():
            devConfig = self.devConfigGenerate.send(ytName)
            if devConfig is None:  # 只有能拿到配置的月台才会进行后续处理，我上面那个for循环已经吃过一次资源了
                continue  # 且是必须存在的，所以未配置月台的筛选过程就放到dvw这边了
            isDevIpExist = classifyByDevIP.get(devConfig.devIP)
            if isDevIpExist is None:
                devArgStruct = DevLoginAndDownloadArgSturct()
                devArgStruct.devType = devConfig.devType
                devArgStruct.devIP = devConfig.devIP
                devArgStruct.devPort = devConfig.devPort
                devArgStruct.devUserName = devConfig.devUserName
                devArgStruct.devPassword = devConfig.devPassword
                devArgStruct.downloadArg[devConfig.devChannel] = downloadArgs  # 相同月台就是相同通道，我这一次加的downloadArgs就是这整个channel所有的downloadArg
                classifyByDevIP[devConfig.devIP] = devArgStruct
            else:
                # 相同的ip但是不同的通道(月台)，只需要把现在这个通道下的下载参数追加到之前的那个downloadArg字典中就可以了
                isDevIpExist.downloadArg[devConfig.devChannel] = downloadArgs
        print(classifyByDevIP)
        # TODO 上面两个分类可以做到一个for里，但那样的复杂度和时间消耗



        # TODO 先开视频转图片的子进程
        # TODO 然后开cpu_count数量的进程池
        # 不管怎样，用map交接任务
        with ProcessPoolExecutor() as executor:
            for devIP, devArgStruct in classifyByDevIP.items():
                print(devIP, devArgStruct, devArgStruct.devType)
                if devArgStruct.devType == "dahua":
                    pass
                elif devArgStruct.devType == "haikang":
                    pass







if __name__ == "__main__":  # 用于当前窗体测试

    app = QApplication(sys.argv)  # 创建GUI应用程序
    forms = DVWclass()  # 创建窗体

    # forms.addFilePathsToexcelFile_LWData([__filePath1])
    forms.show()

    sys.exit(app.exec_())
