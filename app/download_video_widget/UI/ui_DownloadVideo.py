# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\Administrator\Documents\CodeProject\ATO\app\download_video_widget\UI\DownloadVideo.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_DVW_Widget(object):
    def setupUi(self, DVW_Widget):
        DVW_Widget.setObjectName("DVW_Widget")
        DVW_Widget.resize(1330, 738)
        self.gridLayout = QtWidgets.QGridLayout(DVW_Widget)
        self.gridLayout.setObjectName("gridLayout")
        self.startDownLoad_PB = PushButton(DVW_Widget)
        self.startDownLoad_PB.setObjectName("startDownLoad_PB")
        self.gridLayout.addWidget(self.startDownLoad_PB, 0, 0, 1, 1)
        self.argsCount_TL = TitleLabel(DVW_Widget)
        self.argsCount_TL.setObjectName("argsCount_TL")
        self.gridLayout.addWidget(self.argsCount_TL, 0, 1, 1, 1)
        self.splitter = QtWidgets.QSplitter(DVW_Widget)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.downloadStatus_TW = TableWidget(self.splitter)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(3)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.downloadStatus_TW.sizePolicy().hasHeightForWidth())
        self.downloadStatus_TW.setSizePolicy(sizePolicy)
        self.downloadStatus_TW.setObjectName("downloadStatus_TW")
        self.downloadStatus_TW.setColumnCount(6)
        self.downloadStatus_TW.setRowCount(8)
        item = QtWidgets.QTableWidgetItem()
        self.downloadStatus_TW.setVerticalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.downloadStatus_TW.setVerticalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.downloadStatus_TW.setVerticalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.downloadStatus_TW.setVerticalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.downloadStatus_TW.setVerticalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.downloadStatus_TW.setVerticalHeaderItem(5, item)
        item = QtWidgets.QTableWidgetItem()
        self.downloadStatus_TW.setVerticalHeaderItem(6, item)
        item = QtWidgets.QTableWidgetItem()
        self.downloadStatus_TW.setVerticalHeaderItem(7, item)
        item = QtWidgets.QTableWidgetItem()
        self.downloadStatus_TW.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.downloadStatus_TW.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.downloadStatus_TW.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.downloadStatus_TW.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.downloadStatus_TW.setHorizontalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.downloadStatus_TW.setHorizontalHeaderItem(5, item)
        self.downloadProgress_TW = TableWidget(self.splitter)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.downloadProgress_TW.sizePolicy().hasHeightForWidth())
        self.downloadProgress_TW.setSizePolicy(sizePolicy)
        self.downloadProgress_TW.setObjectName("downloadProgress_TW")
        self.downloadProgress_TW.setColumnCount(3)
        self.downloadProgress_TW.setRowCount(6)
        item = QtWidgets.QTableWidgetItem()
        self.downloadProgress_TW.setVerticalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.downloadProgress_TW.setVerticalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.downloadProgress_TW.setVerticalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.downloadProgress_TW.setVerticalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.downloadProgress_TW.setVerticalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.downloadProgress_TW.setVerticalHeaderItem(5, item)
        item = QtWidgets.QTableWidgetItem()
        self.downloadProgress_TW.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.downloadProgress_TW.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.downloadProgress_TW.setHorizontalHeaderItem(2, item)
        self.gridLayout.addWidget(self.splitter, 1, 1, 1, 1)

        self.retranslateUi(DVW_Widget)
        QtCore.QMetaObject.connectSlotsByName(DVW_Widget)

    def retranslateUi(self, DVW_Widget):
        _translate = QtCore.QCoreApplication.translate
        DVW_Widget.setWindowTitle(_translate("DVW_Widget", "Form"))
        self.startDownLoad_PB.setText(_translate("DVW_Widget", "开始下载"))
        self.argsCount_TL.setText(_translate("DVW_Widget", "下载进度 (共0个)"))
        item = self.downloadStatus_TW.verticalHeaderItem(0)
        item.setText(_translate("DVW_Widget", "1"))
        item = self.downloadStatus_TW.verticalHeaderItem(1)
        item.setText(_translate("DVW_Widget", "2"))
        item = self.downloadStatus_TW.verticalHeaderItem(2)
        item.setText(_translate("DVW_Widget", "3"))
        item = self.downloadStatus_TW.verticalHeaderItem(3)
        item.setText(_translate("DVW_Widget", "4"))
        item = self.downloadStatus_TW.verticalHeaderItem(4)
        item.setText(_translate("DVW_Widget", "5"))
        item = self.downloadStatus_TW.verticalHeaderItem(5)
        item.setText(_translate("DVW_Widget", "7"))
        item = self.downloadStatus_TW.verticalHeaderItem(6)
        item.setText(_translate("DVW_Widget", "8"))
        item = self.downloadStatus_TW.verticalHeaderItem(7)
        item.setText(_translate("DVW_Widget", "9"))
        item = self.downloadStatus_TW.horizontalHeaderItem(0)
        item.setText(_translate("DVW_Widget", "IP"))
        item = self.downloadStatus_TW.horizontalHeaderItem(1)
        item.setText(_translate("DVW_Widget", "通道"))
        item = self.downloadStatus_TW.horizontalHeaderItem(2)
        item.setText(_translate("DVW_Widget", "月台"))
        item = self.downloadStatus_TW.horizontalHeaderItem(3)
        item.setText(_translate("DVW_Widget", "文件路径"))
        item = self.downloadStatus_TW.horizontalHeaderItem(4)
        item.setText(_translate("DVW_Widget", "下载时间"))
        item = self.downloadStatus_TW.horizontalHeaderItem(5)
        item.setText(_translate("DVW_Widget", "下载状态"))
        item = self.downloadProgress_TW.verticalHeaderItem(0)
        item.setText(_translate("DVW_Widget", "1"))
        item = self.downloadProgress_TW.verticalHeaderItem(1)
        item.setText(_translate("DVW_Widget", "2"))
        item = self.downloadProgress_TW.verticalHeaderItem(2)
        item.setText(_translate("DVW_Widget", "3"))
        item = self.downloadProgress_TW.verticalHeaderItem(3)
        item.setText(_translate("DVW_Widget", "4"))
        item = self.downloadProgress_TW.verticalHeaderItem(4)
        item.setText(_translate("DVW_Widget", "5"))
        item = self.downloadProgress_TW.verticalHeaderItem(5)
        item.setText(_translate("DVW_Widget", "7"))
        item = self.downloadProgress_TW.horizontalHeaderItem(0)
        item.setText(_translate("DVW_Widget", "IP"))
        item = self.downloadProgress_TW.horizontalHeaderItem(1)
        item.setText(_translate("DVW_Widget", "下载进度"))
        item = self.downloadProgress_TW.horizontalHeaderItem(2)
        item.setText(_translate("DVW_Widget", "执行状态"))
from qfluentwidgets import PushButton, TableWidget, TitleLabel
