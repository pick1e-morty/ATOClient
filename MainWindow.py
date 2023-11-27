from multiprocessing import freeze_support

from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import pyqtSlot
from app.QMyMWmw.ui_MainWindow import Ui_MainWindow
import sys


# TODO 把Enum换成字典
# TODO 把videoprocess文件夹的位置提到项目的上一个层级
# 修复进程池运行转换的bug 并尝试找到多进程启动主窗体的原因 找到原因了
# https://stackoverflow.com/questions/13922597/multiprocessing-freeze-support
# bug分支 yolo框架没用子线程 会导致主窗口无响应
# 大华的sdk 一个进程中我init了 我日常将会init两次 所以需要提供接口 别在一个init链式调用了 把接口放出来，让用户操作
# 一个隐藏的隐患 就是大华下载回调失败 但是这个句柄并没有被关闭
# https://docs.python.org/zh-cn/3/library/concurrent.futures.html
# 是不是可以把那个视频转换的多进程也换成这个高级抽象的processPoolExecutor
# TODO 那个过滤坐标的算法还有很大的提升空间

class QmyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()  # 调用父类构造函数，创建窗体
        self.ui = Ui_MainWindow()  # 创建UI对象
        self.ui.setupUi(self)  # 构造UI界面
        self.ui.EPStackPb.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(0))  # 按钮跳转层叠界面
        self.ui.VDPStackPb.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(1))
        self.ui.PLStackPb.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(2))
        self.ui.ALStackPb.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(3))
        self.ui.EPStackPb.click()

    @pyqtSlot()
    def on_iniShipPB_clicked(self):  # 父组件对两个子组件的数据传输架个桥
        EPW_ExcelDataTW_Data = self.ui.EPW.getAllOfExcelFileData()  # 组件内部方法
        if len(EPW_ExcelDataTW_Data):
            self.ui.VDPW.iniWidget(EPW_ExcelDataTW_Data)  # 取放操作

    @pyqtSlot()
    def on_ALWiniWidgetPB_clicked(self):
        EPW_ExcelDataTW_Data = self.ui.EPW.getAllOfExcelFileData()  # 组件内部方法
        if len(EPW_ExcelDataTW_Data):
            self.ui.ALW.iniWidget(EPW_ExcelDataTW_Data)  # 取放操作


if __name__ == "__main__":  # 用于当前窗体测试
    freeze_support()
    app = QApplication(sys.argv)  # 创建GUI应用程序
    form = QmyMainWindow()  # 创建窗体
    form.show()
    print(sys.path)
    sys.exit(app.exec_())
