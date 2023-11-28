import sys
from PyQt5.QtCore import pyqtSlot, QEvent
from PyQt5.QtWidgets import (QApplication, QWidget, QListWidget, QTableWidget, QAction)
from qfluentwidgets import RoundMenu, Action, MenuAnimationType

from app.esheet_process_widget.UI.ui_ExcelProcess import Ui_Form


class Init_EPW_Widget(QWidget):
    def __init__(self, config):
        super().__init__()  # 调用父类构造函数，创建窗体
        self.ui = Ui_Form()  # 创建UI对象
        self.ui.setupUi(self)  # 构造UI界面
        self.epw_config = config["epw"]
        self.initUI()

    def initUI(self):
        self.initKeepShipNum_SPB()

        # 这些是方法依赖的UI设定，不可更改
        self.ui.excelFile_LW.setSelectionMode(QListWidget.SingleSelection)  # get_FilePathInExcelFile_LW_ItemData
        self.ui.excelFile_LW.installEventFilter(self)
        self.ui.excelData_TW.installEventFilter(self)
        self.ui.sameYTCount_TW.installEventFilter(self)
        self.init_excelFile_LW_Menu()
        self.init_excelData_TW_Menu()
        self.init_sameYTCount_TW_Menu()

    def init_excelFile_LW_Menu(self):

        action_getfile = Action("添加文件")
        action_getfile.triggered.connect(lambda: self.ui.getfile_PB.click())
        action_reprocessExcelFile = Action("重新处理文件")
        action_reprocessExcelFile.triggered.connect(lambda: self.ui.reprocessExcelFile_PB.click())
        action_deleteExcelFileLWItem = Action("删除选中文件")
        action_deleteExcelFileLWItem.triggered.connect(lambda: self.ui.deleteExcelFileLWItem_PB.click())

        self.excelFile_LW_Menu = RoundMenu(parent=self)
        self.excelFile_LW_Menu.addAction(action_getfile)
        self.excelFile_LW_Menu.addAction(action_reprocessExcelFile)
        self.excelFile_LW_Menu.addAction(action_deleteExcelFileLWItem)

    def init_excelData_TW_Menu(self):
        action_selectAllShipID = Action("全选单号")
        action_selectAllShipID.triggered.connect(lambda: self.ui.selectAllShipID_PB.click())
        action_reverseSelectionShipID = Action("反选单号")
        action_reverseSelectionShipID.triggered.connect(lambda: self.ui.reverseSelectionShipID_PB.click())
        action_deleteSelectionShipID = Action("删除选中单号")
        action_deleteSelectionShipID.triggered.connect(lambda: self.ui.deleteSelectionShipID_PB.click())

        self.excelData_TW_Menu = RoundMenu(parent=self)
        self.excelData_TW_Menu.addAction(action_selectAllShipID)
        self.excelData_TW_Menu.addAction(action_reverseSelectionShipID)
        self.excelData_TW_Menu.addAction(action_deleteSelectionShipID)

    def init_sameYTCount_TW_Menu(self):
        self.sameYTCount_TW_Menu = RoundMenu(parent=self)
        self.sameYTCount_TW_Menu.addMenu(self.ui.keepShipNum_SPB.flyout)
        self.sameYTCount_TW_Menu.addSeparator()
        action_selectAllYT = Action("全选月台")
        action_selectAllYT.triggered.connect(lambda: self.ui.selectAllYT_PB.click())
        action_reverseSelectionYT = Action("反选月台")
        action_reverseSelectionYT.triggered.connect(lambda: self.ui.reverseSelectionYT_PB.click())
        action_deleteSelectionYT = Action("删除选中月台")
        action_deleteSelectionYT.triggered.connect(lambda: self.ui.deleteSelectionYT_PB.click())
        self.sameYTCount_TW_Menu.addAction(action_selectAllYT)
        self.sameYTCount_TW_Menu.addAction(action_reverseSelectionYT)
        self.sameYTCount_TW_Menu.addAction(action_deleteSelectionYT)

    def eventFilter(self, watch, event):
        if event.type() == QEvent.Type.ContextMenu:
            if watch is self.ui.excelFile_LW:
                self.excelFile_LW_Menu.exec(event.globalPos(), aniType=MenuAnimationType.DROP_DOWN)
            elif watch is self.ui.excelData_TW:
                self.excelData_TW_Menu.exec(event.globalPos(), aniType=MenuAnimationType.DROP_DOWN)
            elif watch is self.ui.sameYTCount_TW:
                self.sameYTCount_TW_Menu.exec(event.globalPos(), aniType=MenuAnimationType.DROP_DOWN)
        return super().eventFilter(watch, event)

    def initKeepShipNum_SPB(self):
        # 向月台保留下拉框中填充预定数据
        # menu = RoundMenu("月台保留单号数量", parent=self)
        menu = RoundMenu("保选月单数", parent=self)
        for num in self.epw_config["月台保留数量列表"]:
            action = QAction(str(num))
            menu.addAction(action)
        self.ui.keepShipNum_SPB.setFlyout(menu)

    # 还有这个初始化重做
    # for循环创建Action，全部连接一个共有的函数
    # 判读这个action上面带的什么数字来执行函数
    # 还有那个按钮本身也是用的这个函数，按钮默认是15
    # 这里不做trigger()连接，初始化后从menu里取所有action

    # flow组件，自己挪按钮进去吧
    # 新加了一个扫描时间格式，配置那边记得写，读excel的时候就做好类型判断

    @pyqtSlot()
    def on_newFormat_RB_clicked(self):
        # 新格式单选按钮被点击
        self.ui.shipCID_LE.setText(self.epw_config["常用格式"]["单号列"])
        self.ui.scanTimeCID_LE.setText(self.epw_config["常用格式"]["扫描时间列"])
        self.ui.ytCID_LE.setText(self.epw_config["常用格式"]["月台号列"])
        self.ui.scanTimeFormat_LE.setText(self.epw_config["常用格式"]["扫描时间格式"])

    @pyqtSlot()
    def on_oldFormat_RB_clicked(self):
        # 旧格式单选按钮被点击
        self.ui.shipCID_LE.setText(self.epw_config["其他格式"]["单号列"])
        self.ui.scanTimeCID_LE.setText(self.epw_config["其他格式"]["扫描时间列"])
        self.ui.ytCID_LE.setText(self.epw_config["其他格式"]["月台号列"])
        self.ui.scanTimeFormat_LE.setText(self.epw_config["其他格式"]["扫描时间格式"])
        self.ui.shipCID_LE.setReadOnly(False)
        self.ui.scanTimeCID_LE.setReadOnly(False)
        self.ui.ytCID_LE.setReadOnly(False)
        self.ui.scanTimeFormat_LE.setReadOnly(False)


if __name__ == "__main__":  # 用于当前窗体测试
    from app.utils.aboutconfig import configini

    app = QApplication(sys.argv)  # 创建GUI应用程序
    forms = Init_EPW_Widget(configini)  # 创建窗体
    forms.show()
    sys.exit(app.exec_())
