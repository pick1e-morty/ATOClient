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
        DVW_Widget.resize(1075, 882)
        self.startDownLoad_PB = PushButton(DVW_Widget)
        self.startDownLoad_PB.setGeometry(QtCore.QRect(30, 100, 102, 32))
        self.startDownLoad_PB.setObjectName("startDownLoad_PB")
        self.TitleLabel = TitleLabel(DVW_Widget)
        self.TitleLabel.setGeometry(QtCore.QRect(170, 40, 123, 37))
        self.TitleLabel.setObjectName("TitleLabel")
        self.downLoadStatus_TW = TableWidget(DVW_Widget)
        self.downLoadStatus_TW.setGeometry(QtCore.QRect(170, 120, 721, 431))
        self.downLoadStatus_TW.setObjectName("downLoadStatus_TW")
        self.downLoadStatus_TW.setColumnCount(6)
        self.downLoadStatus_TW.setRowCount(8)
        item = QtWidgets.QTableWidgetItem()
        self.downLoadStatus_TW.setVerticalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.downLoadStatus_TW.setVerticalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.downLoadStatus_TW.setVerticalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.downLoadStatus_TW.setVerticalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.downLoadStatus_TW.setVerticalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.downLoadStatus_TW.setVerticalHeaderItem(5, item)
        item = QtWidgets.QTableWidgetItem()
        self.downLoadStatus_TW.setVerticalHeaderItem(6, item)
        item = QtWidgets.QTableWidgetItem()
        self.downLoadStatus_TW.setVerticalHeaderItem(7, item)
        item = QtWidgets.QTableWidgetItem()
        self.downLoadStatus_TW.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.downLoadStatus_TW.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.downLoadStatus_TW.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.downLoadStatus_TW.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.downLoadStatus_TW.setHorizontalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.downLoadStatus_TW.setHorizontalHeaderItem(5, item)

        self.retranslateUi(DVW_Widget)
        QtCore.QMetaObject.connectSlotsByName(DVW_Widget)

    def retranslateUi(self, DVW_Widget):
        _translate = QtCore.QCoreApplication.translate
        DVW_Widget.setWindowTitle(_translate("DVW_Widget", "Form"))
        self.startDownLoad_PB.setText(_translate("DVW_Widget", "开始下载"))
        self.TitleLabel.setText(_translate("DVW_Widget", "下载状态"))
        item = self.downLoadStatus_TW.verticalHeaderItem(0)
        item.setText(_translate("DVW_Widget", "1"))
        item = self.downLoadStatus_TW.verticalHeaderItem(1)
        item.setText(_translate("DVW_Widget", "2"))
        item = self.downLoadStatus_TW.verticalHeaderItem(2)
        item.setText(_translate("DVW_Widget", "3"))
        item = self.downLoadStatus_TW.verticalHeaderItem(3)
        item.setText(_translate("DVW_Widget", "4"))
        item = self.downLoadStatus_TW.verticalHeaderItem(4)
        item.setText(_translate("DVW_Widget", "5"))
        item = self.downLoadStatus_TW.verticalHeaderItem(5)
        item.setText(_translate("DVW_Widget", "7"))
        item = self.downLoadStatus_TW.verticalHeaderItem(6)
        item.setText(_translate("DVW_Widget", "8"))
        item = self.downLoadStatus_TW.verticalHeaderItem(7)
        item.setText(_translate("DVW_Widget", "9"))
        item = self.downLoadStatus_TW.horizontalHeaderItem(0)
        item.setText(_translate("DVW_Widget", "IP"))
        item = self.downLoadStatus_TW.horizontalHeaderItem(1)
        item.setText(_translate("DVW_Widget", "通道"))
        item = self.downLoadStatus_TW.horizontalHeaderItem(2)
        item.setText(_translate("DVW_Widget", "月台"))
        item = self.downLoadStatus_TW.horizontalHeaderItem(3)
        item.setText(_translate("DVW_Widget", "单号"))
        item = self.downLoadStatus_TW.horizontalHeaderItem(4)
        item.setText(_translate("DVW_Widget", "扫描时间"))
        item = self.downLoadStatus_TW.horizontalHeaderItem(5)
        item.setText(_translate("DVW_Widget", "下载进度"))
from qfluentwidgets import PushButton, TableWidget, TitleLabel
