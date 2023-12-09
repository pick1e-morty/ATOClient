import sys
from pathlib import Path

from PyQt5.QtCore import pyqtSlot, QEvent, QSize, Qt, QPropertyAnimation, QRect, QEasingCurve
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QApplication, QWidget, QListWidget, QTableWidget, QAction, QSizePolicy)
from qfluentwidgets import RoundMenu, Action, MenuAnimationType, SplashScreen, FlowLayout, SwitchButton

from app.esheet_process_widget.UI.ui_ExcelProcess import Ui_EPW_Widget


class Init_EPW_Widget(QWidget):
    """
    这边实现的功能
    1. 左边的ListWidget和右边两个TableWidget的右键菜单
    2. 自定义处理格式的展开收缩的动画
    3. 从配置文件中读取数据并设置到 保留指定月台中的单号数量按钮中的各个action所携带的数值，以及自定义处理格式中的四个LineEdit的默认数值
    4. 开始屏幕的加载启动（关闭方法则是两边的文件入口都有）
    """

    def __init__(self, config, parent=None):
        super().__init__(parent)  # 调用父类构造函数，创建窗体
        self.ui = Ui_EPW_Widget()  # 创建UI对象
        self.ui.setupUi(self)  # 构造UI界面

        self.epw_config = config["epw"]
        self.initUI()

    def initUI(self):
        # self.loadSplashScreen()
        self.initKeepShipNum_SPB()
        self.initCustomFormat_CW()
        # self.initFlowLayout()
        # 仅仅是美化的修改
        self.moveSwitchButtonIndicator2Right(self.ui.customFormat_SB)
        # self.moveSwitchButtonIndicator2Right(self.ui.autoDeleteUnConfiguredYT_SB)

        # 三个组件的右键菜单
        self.ui.excelFile_LW.installEventFilter(self)
        self.ui.excelData_TW.installEventFilter(self)
        self.ui.sameYTCount_TW.installEventFilter(self)
        self.init_excelFile_LW_Menu()
        self.init_excelData_TW_Menu()
        self.init_sameYTCount_TW_Menu()
        # 下面是方法依赖的UI设定，不可更改
        self.ui.excelFile_LW.setSelectionMode(QListWidget.SingleSelection)  # get_FilePathInExcelFile_LW_ItemData

    @staticmethod
    def moveSwitchButtonIndicator2Right(switchButton: SwitchButton):
        # 用于将Designer生成的SwithButton中的Indicator移动到右边，当然Designer中没有修改该属性的接口
        # 由于主题作者没有提供动态修改SwitchButton中Indicator位置的方法，所以只能自己动手了
        switchButtonLabel = switchButton.label
        switchButtonIndicator = switchButton.indicator
        switchButton.hBox.removeWidget(switchButtonLabel)
        switchButton.hBox.removeWidget(switchButtonIndicator)
        switchButton.hBox.addWidget(switchButtonLabel, 0, Qt.AlignRight)
        switchButton.hBox.addWidget(switchButtonIndicator, 0, Qt.AlignRight)

    def initFlowLayout(self):
        # 失败了，没开
        self.flowLayout = FlowLayout(self, needAni=True)

        self.flowLayout.setAnimation(250, QEasingCurve.OutQuad)
        self.flowLayout.setContentsMargins(30, 30, 30, 30)
        self.flowLayout.setVerticalSpacing(6)
        self.flowLayout.setHorizontalSpacing(6)

        self.ui.selectAllShipID_PB.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        self.ui.reverseSelectionShipID_PB.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        self.ui.deleteSelectionShipID_PB.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)

        self.ui.verticalLayout.removeWidget(self.ui.selectAllShipID_PB)
        self.ui.verticalLayout.removeWidget(self.ui.reverseSelectionShipID_PB)
        self.ui.verticalLayout.removeWidget(self.ui.deleteSelectionShipID_PB)

        self.flowLayout.addWidget(self.ui.selectAllShipID_PB)
        self.flowLayout.addWidget(self.ui.reverseSelectionShipID_PB)
        self.flowLayout.addWidget(self.ui.deleteSelectionShipID_PB)

        self.ui.verticalLayout.addLayout(self.flowLayout)

    def initCustomFormat_CW(self):
        # 初始化CustomFormat_CardWidget，隐藏其中的所有组件
        self.ui.shipCID_LE.setText(self.epw_config["自定义格式"]["单号列"])
        self.ui.scanTimeCID_LE.setText(self.epw_config["自定义格式"]["扫描时间列"])
        self.ui.ytCID_LE.setText(self.epw_config["自定义格式"]["月台号列"])
        self.ui.scanTimeFormat_LE.setText(self.epw_config["自定义格式"]["扫描时间格式"])

        self.ui.shipCID_LE.setVisible(False)
        self.ui.shipCID_BL.setVisible(False)
        self.ui.ytCID_LE.setVisible(False)
        self.ui.ytCID_BL.setVisible(False)
        self.ui.scanTimeCID_LE.setVisible(False)
        self.ui.scanTimeCID_BL.setVisible(False)
        self.ui.scanTimeFormat_LE.setVisible(False)
        self.ui.scanTimeFormat_BL.setVisible(False)

    def loadSplashScreen(self):
        # 加载启动屏幕
        logoFilePath = Path(__file__).parent.parent / "AppData/logo.png"
        self.setWindowIcon(QIcon(str(logoFilePath)))
        self.splashScreen = SplashScreen(self.windowIcon(), self)
        self.splashScreen.setTitleBar(QWidget())  # 去掉启动画面中右上角的三个窗口按钮
        formsWidth = self.size().width()
        formsHeigth = self.size().height()
        self.splashScreen.setIconSize(QSize(formsWidth // 2, formsHeigth // 2))
        self.show()
        QApplication.processEvents()

    @pyqtSlot(bool)
    def on_customFormat_SB_checkedChanged(self, isChecked):
        # 当自定义格式按钮被按下时执行该方法
        # 展开组件，向上扩展至正常展开时所占用的高度
        # 或收缩至只有一个switchButton的大小
        # 按照相对应的状态来判断是否展示Custom_CardWidget中的组件
        fourLineEditHeight = self.ui.shipCID_LE.height() + self.ui.ytCID_LE.height() + self.ui.scanTimeCID_LE.height() + self.ui.scanTimeFormat_LE.height()
        bodyLabelHeight = self.ui.scanTimeFormat_BL.height()
        verticalSpacingHeight = self.ui.CustomFormat_CW.layout().verticalSpacing() * 4
        totalHeight = fourLineEditHeight + bodyLabelHeight + verticalSpacingHeight  # 先获取正常展开时所占用的高度

        if isChecked:  # 展开组件，向上扩展至正常展开时所占用的高度
            self.expandCustom_CW_Animation = QPropertyAnimation(self.ui.CustomFormat_CW, b'geometry')
            start_geometry = self.ui.CustomFormat_CW.geometry()
            end_geometry = QRect(start_geometry.x(), start_geometry.y() - totalHeight, start_geometry.width(), start_geometry.height() + totalHeight)
            self.expandCustom_CW_Animation.setDuration(200)  # 设置动画持续时间为200毫秒
            self.expandCustom_CW_Animation.setStartValue(start_geometry)
            self.expandCustom_CW_Animation.setEndValue(end_geometry)
            self.expandCustom_CW_Animation.start()  # 启动展开动画
        else:  # 收缩组件，向下收缩
            self.collapseCustom_CW_Animation = QPropertyAnimation(self.ui.CustomFormat_CW, b'geometry')
            start_geometry = self.ui.CustomFormat_CW.geometry()
            end_geometry = QRect(start_geometry.x(), start_geometry.y() + totalHeight, start_geometry.width(), start_geometry.height() - totalHeight)
            self.collapseCustom_CW_Animation.setDuration(200)  # 设置动画持续时间为200毫秒
            self.collapseCustom_CW_Animation.setStartValue(start_geometry)
            self.collapseCustom_CW_Animation.setEndValue(end_geometry)
            self.collapseCustom_CW_Animation.start()  # 启动展开动画
        self.ui.shipCID_LE.setVisible(isChecked)
        self.ui.shipCID_BL.setVisible(isChecked)
        self.ui.ytCID_LE.setVisible(isChecked)
        self.ui.ytCID_BL.setVisible(isChecked)
        self.ui.scanTimeCID_LE.setVisible(isChecked)
        self.ui.scanTimeCID_BL.setVisible(isChecked)
        self.ui.scanTimeFormat_LE.setVisible(isChecked)
        self.ui.scanTimeFormat_BL.setVisible(isChecked)

    def init_excelFile_LW_Menu(self):
        # 初始化excel文件列表组件的右键菜单
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
        # 初始化excel数据表格组件的右键菜单
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
        # 初始化相同月台总量表格组件的右键菜单
        self.sameYTCount_TW_Menu = RoundMenu(parent=self)
        self.sameYTCount_TW_Menu.addMenu(self.ui.keepShipNum_SPB.flyout)
        self.sameYTCount_TW_Menu.addSeparator()
        action_deleteUnConfiguredYT = Action("删除未配置月台")
        action_deleteUnConfiguredYT.triggered.connect(lambda: self.ui.deleteUnConfiguredYT_PB.click())
        action_selectAllYT = Action("全选月台")
        action_selectAllYT.triggered.connect(lambda: self.ui.selectAllYT_PB.click())
        action_reverseSelectionYT = Action("反选月台")
        action_reverseSelectionYT.triggered.connect(lambda: self.ui.reverseSelectionYT_PB.click())
        action_deleteSelectionYT = Action("删除选中月台")
        action_deleteSelectionYT.triggered.connect(lambda: self.ui.deleteSelectionYT_PB.click())
        self.sameYTCount_TW_Menu.addAction(action_deleteUnConfiguredYT)
        self.sameYTCount_TW_Menu.addAction(action_selectAllYT)
        self.sameYTCount_TW_Menu.addAction(action_reverseSelectionYT)
        self.sameYTCount_TW_Menu.addAction(action_deleteSelectionYT)

    def eventFilter(self, watch, event):
        # 事件过滤器拦截ContextMenu，并启动相对应位置中预设的右键菜单
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

    # @pyqtSlot()
    # def on_getfile_PB_clicked(self):
    #     print(self.ui.CardWidget.width())
    #     print(self.ui.CustomFormat_CW.width())


if __name__ == "__main__":  # 用于当前窗体测试
    from app.utils.aboutconfig import configini

    app = QApplication(sys.argv)  # 创建GUI应用程序
    forms = Init_EPW_Widget(configini)  # 创建窗体
    forms.show()

    sys.exit(app.exec_())
