# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\Administrator\Documents\CodeProject\ATO\app\esheet_process_widget\UI\ExcelProcess.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_EPW_Widget(object):
    def setupUi(self, EPW_Widget):
        EPW_Widget.setObjectName("EPW_Widget")
        EPW_Widget.resize(1265, 925)
        self.gridLayout_6 = QtWidgets.QGridLayout(EPW_Widget)
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.fileGB = QtWidgets.QGroupBox(EPW_Widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.fileGB.sizePolicy().hasHeightForWidth())
        self.fileGB.setSizePolicy(sizePolicy)
        self.fileGB.setStyleSheet("border:0px")
        self.fileGB.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.fileGB.setObjectName("fileGB")
        self.gridLayout = QtWidgets.QGridLayout(self.fileGB)
        self.gridLayout.setObjectName("gridLayout")
        self.CustomFormat_CW = CardWidget(self.fileGB)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.CustomFormat_CW.sizePolicy().hasHeightForWidth())
        self.CustomFormat_CW.setSizePolicy(sizePolicy)
        self.CustomFormat_CW.setObjectName("CustomFormat_CW")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.CustomFormat_CW)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.shipCID_BL = BodyLabel(self.CustomFormat_CW)
        self.shipCID_BL.setObjectName("shipCID_BL")
        self.gridLayout_2.addWidget(self.shipCID_BL, 2, 0, 1, 1)
        self.scanTimeFormat_BL = BodyLabel(self.CustomFormat_CW)
        self.scanTimeFormat_BL.setAlignment(QtCore.Qt.AlignCenter)
        self.scanTimeFormat_BL.setObjectName("scanTimeFormat_BL")
        self.gridLayout_2.addWidget(self.scanTimeFormat_BL, 7, 0, 1, 3)
        self.ytCID_BL = BodyLabel(self.CustomFormat_CW)
        self.ytCID_BL.setObjectName("ytCID_BL")
        self.gridLayout_2.addWidget(self.ytCID_BL, 3, 0, 1, 1)
        self.scanTimeCID_BL = BodyLabel(self.CustomFormat_CW)
        self.scanTimeCID_BL.setObjectName("scanTimeCID_BL")
        self.gridLayout_2.addWidget(self.scanTimeCID_BL, 4, 0, 1, 1)
        self.scanTimeFormat_LE = LineEdit(self.CustomFormat_CW)
        self.scanTimeFormat_LE.setReadOnly(False)
        self.scanTimeFormat_LE.setObjectName("scanTimeFormat_LE")
        self.gridLayout_2.addWidget(self.scanTimeFormat_LE, 8, 0, 1, 3)
        self.scanTimeCID_LE = LineEdit(self.CustomFormat_CW)
        self.scanTimeCID_LE.setReadOnly(False)
        self.scanTimeCID_LE.setObjectName("scanTimeCID_LE")
        self.gridLayout_2.addWidget(self.scanTimeCID_LE, 4, 1, 1, 2)
        self.ytCID_LE = LineEdit(self.CustomFormat_CW)
        self.ytCID_LE.setReadOnly(False)
        self.ytCID_LE.setObjectName("ytCID_LE")
        self.gridLayout_2.addWidget(self.ytCID_LE, 3, 1, 1, 2)
        self.customFormat_SB = SwitchButton(self.CustomFormat_CW)
        self.customFormat_SB.setObjectName("customFormat_SB")
        self.gridLayout_2.addWidget(self.customFormat_SB, 0, 0, 1, 3)
        self.shipCID_LE = LineEdit(self.CustomFormat_CW)
        self.shipCID_LE.setReadOnly(False)
        self.shipCID_LE.setObjectName("shipCID_LE")
        self.gridLayout_2.addWidget(self.shipCID_LE, 2, 1, 1, 2)
        self.gridLayout.addWidget(self.CustomFormat_CW, 2, 0, 1, 1)
        self.TitleLabel = TitleLabel(self.fileGB)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.TitleLabel.sizePolicy().hasHeightForWidth())
        self.TitleLabel.setSizePolicy(sizePolicy)
        self.TitleLabel.setObjectName("TitleLabel")
        self.gridLayout.addWidget(self.TitleLabel, 0, 0, 1, 1)
        self.CardWidget = CardWidget(self.fileGB)
        self.CardWidget.setObjectName("CardWidget")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.CardWidget)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.excelFile_LW = ListWidget(self.CardWidget)
        self.excelFile_LW.setObjectName("excelFile_LW")
        self.gridLayout_4.addWidget(self.excelFile_LW, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.CardWidget, 1, 0, 1, 1)
        self.deleteExcelFileLWItem_PB = PushButton(self.fileGB)
        self.deleteExcelFileLWItem_PB.setObjectName("deleteExcelFileLWItem_PB")
        self.gridLayout.addWidget(self.deleteExcelFileLWItem_PB, 6, 0, 1, 1)
        self.reprocessExcelFile_PB = PushButton(self.fileGB)
        self.reprocessExcelFile_PB.setObjectName("reprocessExcelFile_PB")
        self.gridLayout.addWidget(self.reprocessExcelFile_PB, 4, 0, 1, 1)
        self.getfile_PB = PushButton(self.fileGB)
        self.getfile_PB.setObjectName("getfile_PB")
        self.gridLayout.addWidget(self.getfile_PB, 3, 0, 1, 1)
        self.gridLayout_6.addWidget(self.fileGB, 0, 0, 1, 1)
        self.shipGB = QtWidgets.QGroupBox(EPW_Widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(5)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.shipGB.sizePolicy().hasHeightForWidth())
        self.shipGB.setSizePolicy(sizePolicy)
        self.shipGB.setStyleSheet("border:0px")
        self.shipGB.setObjectName("shipGB")
        self.gridLayout_7 = QtWidgets.QGridLayout(self.shipGB)
        self.gridLayout_7.setObjectName("gridLayout_7")
        self.reverseSelectionShipID_PB = PushButton(self.shipGB)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.reverseSelectionShipID_PB.sizePolicy().hasHeightForWidth())
        self.reverseSelectionShipID_PB.setSizePolicy(sizePolicy)
        self.reverseSelectionShipID_PB.setObjectName("reverseSelectionShipID_PB")
        self.gridLayout_7.addWidget(self.reverseSelectionShipID_PB, 2, 1, 1, 1)
        self.TitleLabel_2 = TitleLabel(self.shipGB)
        self.TitleLabel_2.setObjectName("TitleLabel_2")
        self.gridLayout_7.addWidget(self.TitleLabel_2, 0, 0, 1, 1)
        self.selectAllShipID_PB = PushButton(self.shipGB)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.selectAllShipID_PB.sizePolicy().hasHeightForWidth())
        self.selectAllShipID_PB.setSizePolicy(sizePolicy)
        self.selectAllShipID_PB.setObjectName("selectAllShipID_PB")
        self.gridLayout_7.addWidget(self.selectAllShipID_PB, 2, 0, 1, 1)
        self.deleteSelectionShipID_PB = PushButton(self.shipGB)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.deleteSelectionShipID_PB.sizePolicy().hasHeightForWidth())
        self.deleteSelectionShipID_PB.setSizePolicy(sizePolicy)
        self.deleteSelectionShipID_PB.setObjectName("deleteSelectionShipID_PB")
        self.gridLayout_7.addWidget(self.deleteSelectionShipID_PB, 2, 2, 1, 1)
        self.CardWidget_3 = CardWidget(self.shipGB)
        self.CardWidget_3.setObjectName("CardWidget_3")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.CardWidget_3)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.excelData_TW = TableWidget(self.CardWidget_3)
        self.excelData_TW.setMinimumSize(QtCore.QSize(342, 0))
        self.excelData_TW.setObjectName("excelData_TW")
        self.excelData_TW.setColumnCount(3)
        self.excelData_TW.setRowCount(9)
        item = QtWidgets.QTableWidgetItem()
        self.excelData_TW.setVerticalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.excelData_TW.setVerticalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.excelData_TW.setVerticalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.excelData_TW.setVerticalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.excelData_TW.setVerticalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.excelData_TW.setVerticalHeaderItem(5, item)
        item = QtWidgets.QTableWidgetItem()
        self.excelData_TW.setVerticalHeaderItem(6, item)
        item = QtWidgets.QTableWidgetItem()
        self.excelData_TW.setVerticalHeaderItem(7, item)
        item = QtWidgets.QTableWidgetItem()
        self.excelData_TW.setVerticalHeaderItem(8, item)
        item = QtWidgets.QTableWidgetItem()
        self.excelData_TW.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.excelData_TW.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.excelData_TW.setHorizontalHeaderItem(2, item)
        self.gridLayout_3.addWidget(self.excelData_TW, 0, 0, 1, 1)
        self.gridLayout_7.addWidget(self.CardWidget_3, 1, 0, 1, 3)
        self.gridLayout_6.addWidget(self.shipGB, 0, 1, 1, 1)
        self.ytGB = QtWidgets.QGroupBox(EPW_Widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(5)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ytGB.sizePolicy().hasHeightForWidth())
        self.ytGB.setSizePolicy(sizePolicy)
        self.ytGB.setStyleSheet("border:0px")
        self.ytGB.setObjectName("ytGB")
        self.gridLayout_8 = QtWidgets.QGridLayout(self.ytGB)
        self.gridLayout_8.setObjectName("gridLayout_8")
        self.TitleLabel_3 = TitleLabel(self.ytGB)
        self.TitleLabel_3.setObjectName("TitleLabel_3")
        self.gridLayout_8.addWidget(self.TitleLabel_3, 0, 0, 1, 2)
        self.CardWidget_4 = CardWidget(self.ytGB)
        self.CardWidget_4.setObjectName("CardWidget_4")
        self.gridLayout_5 = QtWidgets.QGridLayout(self.CardWidget_4)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.sameYTCount_TW = TableWidget(self.CardWidget_4)
        self.sameYTCount_TW.setMinimumSize(QtCore.QSize(336, 0))
        self.sameYTCount_TW.setObjectName("sameYTCount_TW")
        self.sameYTCount_TW.setColumnCount(3)
        self.sameYTCount_TW.setRowCount(9)
        item = QtWidgets.QTableWidgetItem()
        self.sameYTCount_TW.setVerticalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.sameYTCount_TW.setVerticalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.sameYTCount_TW.setVerticalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.sameYTCount_TW.setVerticalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.sameYTCount_TW.setVerticalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.sameYTCount_TW.setVerticalHeaderItem(5, item)
        item = QtWidgets.QTableWidgetItem()
        self.sameYTCount_TW.setVerticalHeaderItem(6, item)
        item = QtWidgets.QTableWidgetItem()
        self.sameYTCount_TW.setVerticalHeaderItem(7, item)
        item = QtWidgets.QTableWidgetItem()
        self.sameYTCount_TW.setVerticalHeaderItem(8, item)
        item = QtWidgets.QTableWidgetItem()
        self.sameYTCount_TW.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.sameYTCount_TW.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.sameYTCount_TW.setHorizontalHeaderItem(2, item)
        self.gridLayout_5.addWidget(self.sameYTCount_TW, 0, 0, 1, 1)
        self.gridLayout_8.addWidget(self.CardWidget_4, 1, 0, 1, 3)
        self.CardWidget_2 = CardWidget(self.ytGB)
        self.CardWidget_2.setObjectName("CardWidget_2")
        self.gridLayout_9 = QtWidgets.QGridLayout(self.CardWidget_2)
        self.gridLayout_9.setObjectName("gridLayout_9")
        self.keepShipNum_SPB = SplitPushButton(self.CardWidget_2)
        self.keepShipNum_SPB.setObjectName("keepShipNum_SPB")
        self.gridLayout_9.addWidget(self.keepShipNum_SPB, 0, 1, 1, 1)
        self.VerticalSeparator = VerticalSeparator(self.CardWidget_2)
        self.VerticalSeparator.setObjectName("VerticalSeparator")
        self.gridLayout_9.addWidget(self.VerticalSeparator, 0, 2, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_9.addItem(spacerItem, 0, 4, 1, 1)
        self.BodyLabel_4 = BodyLabel(self.CardWidget_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.BodyLabel_4.sizePolicy().hasHeightForWidth())
        self.BodyLabel_4.setSizePolicy(sizePolicy)
        self.BodyLabel_4.setObjectName("BodyLabel_4")
        self.gridLayout_9.addWidget(self.BodyLabel_4, 0, 0, 1, 1)
        self.deleteUnConfiguredYT_PB = PushButton(self.CardWidget_2)
        self.deleteUnConfiguredYT_PB.setObjectName("deleteUnConfiguredYT_PB")
        self.gridLayout_9.addWidget(self.deleteUnConfiguredYT_PB, 0, 3, 1, 1)
        self.gridLayout_8.addWidget(self.CardWidget_2, 2, 0, 1, 3)
        self.selectAllYT_PB = PushButton(self.ytGB)
        self.selectAllYT_PB.setObjectName("selectAllYT_PB")
        self.gridLayout_8.addWidget(self.selectAllYT_PB, 3, 0, 1, 1)
        self.reverseSelectionYT_PB = PushButton(self.ytGB)
        self.reverseSelectionYT_PB.setObjectName("reverseSelectionYT_PB")
        self.gridLayout_8.addWidget(self.reverseSelectionYT_PB, 3, 1, 1, 1)
        self.deleteSelectionYT_PB = PushButton(self.ytGB)
        self.deleteSelectionYT_PB.setObjectName("deleteSelectionYT_PB")
        self.gridLayout_8.addWidget(self.deleteSelectionYT_PB, 3, 2, 1, 1)
        self.gridLayout_6.addWidget(self.ytGB, 0, 2, 1, 1)

        self.retranslateUi(EPW_Widget)
        QtCore.QMetaObject.connectSlotsByName(EPW_Widget)

    def retranslateUi(self, EPW_Widget):
        _translate = QtCore.QCoreApplication.translate
        EPW_Widget.setWindowTitle(_translate("EPW_Widget", "Form"))
        self.shipCID_BL.setText(_translate("EPW_Widget", "数字单号列"))
        self.scanTimeFormat_BL.setText(_translate("EPW_Widget", "扫描时间格式"))
        self.ytCID_BL.setText(_translate("EPW_Widget", "月台名称列"))
        self.scanTimeCID_BL.setText(_translate("EPW_Widget", "扫描时间列"))
        self.scanTimeFormat_LE.setText(_translate("EPW_Widget", "%Y-%m-%d %H:%M:%S"))
        self.scanTimeCID_LE.setText(_translate("EPW_Widget", "AD"))
        self.ytCID_LE.setText(_translate("EPW_Widget", "AB"))
        self.customFormat_SB.setOnText(_translate("EPW_Widget", "自定义处理格式"))
        self.customFormat_SB.setOffText(_translate("EPW_Widget", "自定义处理格式"))
        self.shipCID_LE.setText(_translate("EPW_Widget", "A"))
        self.TitleLabel.setText(_translate("EPW_Widget", "待处理文件"))
        self.deleteExcelFileLWItem_PB.setText(_translate("EPW_Widget", "删除选中文件"))
        self.reprocessExcelFile_PB.setText(_translate("EPW_Widget", "重新处理文件"))
        self.getfile_PB.setText(_translate("EPW_Widget", "添加文件"))
        self.reverseSelectionShipID_PB.setText(_translate("EPW_Widget", "反选单号"))
        self.TitleLabel_2.setText(_translate("EPW_Widget", "单号角度"))
        self.selectAllShipID_PB.setText(_translate("EPW_Widget", "全选单号"))
        self.deleteSelectionShipID_PB.setText(_translate("EPW_Widget", "删除选中单号"))
        item = self.excelData_TW.verticalHeaderItem(0)
        item.setText(_translate("EPW_Widget", "1"))
        item = self.excelData_TW.verticalHeaderItem(1)
        item.setText(_translate("EPW_Widget", "2"))
        item = self.excelData_TW.verticalHeaderItem(2)
        item.setText(_translate("EPW_Widget", "3"))
        item = self.excelData_TW.verticalHeaderItem(3)
        item.setText(_translate("EPW_Widget", "4"))
        item = self.excelData_TW.verticalHeaderItem(4)
        item.setText(_translate("EPW_Widget", "5"))
        item = self.excelData_TW.verticalHeaderItem(5)
        item.setText(_translate("EPW_Widget", "6"))
        item = self.excelData_TW.verticalHeaderItem(6)
        item.setText(_translate("EPW_Widget", "7"))
        item = self.excelData_TW.verticalHeaderItem(7)
        item.setText(_translate("EPW_Widget", "8"))
        item = self.excelData_TW.verticalHeaderItem(8)
        item.setText(_translate("EPW_Widget", "10"))
        item = self.excelData_TW.horizontalHeaderItem(0)
        item.setText(_translate("EPW_Widget", "单号"))
        item = self.excelData_TW.horizontalHeaderItem(1)
        item.setText(_translate("EPW_Widget", "扫描时间"))
        item = self.excelData_TW.horizontalHeaderItem(2)
        item.setText(_translate("EPW_Widget", "月台号"))
        self.TitleLabel_3.setText(_translate("EPW_Widget", "月台角度"))
        item = self.sameYTCount_TW.verticalHeaderItem(0)
        item.setText(_translate("EPW_Widget", "1"))
        item = self.sameYTCount_TW.verticalHeaderItem(1)
        item.setText(_translate("EPW_Widget", "2"))
        item = self.sameYTCount_TW.verticalHeaderItem(2)
        item.setText(_translate("EPW_Widget", "3"))
        item = self.sameYTCount_TW.verticalHeaderItem(3)
        item.setText(_translate("EPW_Widget", "4"))
        item = self.sameYTCount_TW.verticalHeaderItem(4)
        item.setText(_translate("EPW_Widget", "5"))
        item = self.sameYTCount_TW.verticalHeaderItem(5)
        item.setText(_translate("EPW_Widget", "6"))
        item = self.sameYTCount_TW.verticalHeaderItem(6)
        item.setText(_translate("EPW_Widget", "7"))
        item = self.sameYTCount_TW.verticalHeaderItem(7)
        item.setText(_translate("EPW_Widget", "8"))
        item = self.sameYTCount_TW.verticalHeaderItem(8)
        item.setText(_translate("EPW_Widget", "10"))
        item = self.sameYTCount_TW.horizontalHeaderItem(0)
        item.setText(_translate("EPW_Widget", "月台号"))
        item = self.sameYTCount_TW.horizontalHeaderItem(1)
        item.setText(_translate("EPW_Widget", "单号数量"))
        item = self.sameYTCount_TW.horizontalHeaderItem(2)
        item.setText(_translate("EPW_Widget", "监控通道"))
        self.keepShipNum_SPB.setProperty("text_", _translate("EPW_Widget", "20"))
        self.BodyLabel_4.setText(_translate("EPW_Widget", "保留选中月台的单号数量"))
        self.deleteUnConfiguredYT_PB.setText(_translate("EPW_Widget", "删除未配置月台"))
        self.selectAllYT_PB.setText(_translate("EPW_Widget", "全选月台"))
        self.reverseSelectionYT_PB.setText(_translate("EPW_Widget", "反选月台"))
        self.deleteSelectionYT_PB.setText(_translate("EPW_Widget", "删除选中月台"))
from qfluentwidgets import BodyLabel, CardWidget, LineEdit, ListWidget, PushButton, SplitPushButton, SwitchButton, TableWidget, TitleLabel, VerticalSeparator
