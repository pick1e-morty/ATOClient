# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\Administrator\Documents\CodeProject\ATO\app\download_video_widget\UI\DownloadVideo.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_DVW_Widget(object):
    def setupUi(self, DVW_Widget):
        DVW_Widget.setObjectName("DVW_Widget")
        DVW_Widget.resize(1413, 925)
        self.gridLayout_5 = QtWidgets.QGridLayout(DVW_Widget)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.CardWidget = CardWidget(DVW_Widget)
        self.CardWidget.setObjectName("CardWidget")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.CardWidget)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.argsCount_TL = TitleLabel(self.CardWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.argsCount_TL.sizePolicy().hasHeightForWidth())
        self.argsCount_TL.setSizePolicy(sizePolicy)
        self.argsCount_TL.setObjectName("argsCount_TL")
        self.gridLayout_2.addWidget(self.argsCount_TL, 0, 0, 1, 1)
        self.startDownLoad_PB = PushButton(self.CardWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.startDownLoad_PB.sizePolicy().hasHeightForWidth())
        self.startDownLoad_PB.setSizePolicy(sizePolicy)
        self.startDownLoad_PB.setObjectName("startDownLoad_PB")
        self.gridLayout_2.addWidget(self.startDownLoad_PB, 0, 1, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem, 0, 2, 1, 1)
        self.downloadProgress_TW = TableWidget(self.CardWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(2)
        sizePolicy.setHeightForWidth(self.downloadProgress_TW.sizePolicy().hasHeightForWidth())
        self.downloadProgress_TW.setSizePolicy(sizePolicy)
        self.downloadProgress_TW.setMinimumSize(QtCore.QSize(500, 0))
        self.downloadProgress_TW.setObjectName("downloadProgress_TW")
        self.downloadProgress_TW.setColumnCount(3)
        self.downloadProgress_TW.setRowCount(5)
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
        self.downloadProgress_TW.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.downloadProgress_TW.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.downloadProgress_TW.setHorizontalHeaderItem(2, item)
        self.gridLayout_2.addWidget(self.downloadProgress_TW, 1, 0, 1, 3)
        self.gridLayout_5.addWidget(self.CardWidget, 0, 0, 1, 1)
        self.CardWidget_2 = CardWidget(DVW_Widget)
        self.CardWidget_2.setObjectName("CardWidget_2")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.CardWidget_2)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.reDownload_PB = PushButton(self.CardWidget_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.reDownload_PB.sizePolicy().hasHeightForWidth())
        self.reDownload_PB.setSizePolicy(sizePolicy)
        self.reDownload_PB.setObjectName("reDownload_PB")
        self.gridLayout_3.addWidget(self.reDownload_PB, 0, 1, 1, 1)
        self.TitleLabel = TitleLabel(self.CardWidget_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.TitleLabel.sizePolicy().hasHeightForWidth())
        self.TitleLabel.setSizePolicy(sizePolicy)
        self.TitleLabel.setObjectName("TitleLabel")
        self.gridLayout_3.addWidget(self.TitleLabel, 0, 0, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_3.addItem(spacerItem1, 0, 2, 1, 1)
        self.downloadError_TW = TableWidget(self.CardWidget_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(2)
        sizePolicy.setHeightForWidth(self.downloadError_TW.sizePolicy().hasHeightForWidth())
        self.downloadError_TW.setSizePolicy(sizePolicy)
        self.downloadError_TW.setObjectName("downloadError_TW")
        self.downloadError_TW.setColumnCount(2)
        self.downloadError_TW.setRowCount(5)
        item = QtWidgets.QTableWidgetItem()
        self.downloadError_TW.setVerticalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.downloadError_TW.setVerticalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.downloadError_TW.setVerticalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.downloadError_TW.setVerticalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.downloadError_TW.setVerticalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.downloadError_TW.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.downloadError_TW.setHorizontalHeaderItem(1, item)
        self.downloadError_TW.horizontalHeader().setDefaultSectionSize(110)
        self.gridLayout_3.addWidget(self.downloadError_TW, 1, 0, 1, 3)
        self.gridLayout_5.addWidget(self.CardWidget_2, 1, 0, 1, 1)
        self.CardWidget_3 = CardWidget(DVW_Widget)
        self.CardWidget_3.setObjectName("CardWidget_3")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.CardWidget_3)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.TitleLabel_2 = TitleLabel(self.CardWidget_3)
        self.TitleLabel_2.setObjectName("TitleLabel_2")
        self.gridLayout_4.addWidget(self.TitleLabel_2, 0, 0, 1, 1)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_4.addItem(spacerItem2, 0, 2, 1, 1)
        self.convert_PB = PushButton(self.CardWidget_3)
        self.convert_PB.setObjectName("convert_PB")
        self.gridLayout_4.addWidget(self.convert_PB, 0, 1, 1, 1)
        self.fileCount_TW = TableWidget(self.CardWidget_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(2)
        sizePolicy.setHeightForWidth(self.fileCount_TW.sizePolicy().hasHeightForWidth())
        self.fileCount_TW.setSizePolicy(sizePolicy)
        self.fileCount_TW.setObjectName("fileCount_TW")
        self.fileCount_TW.setColumnCount(4)
        self.fileCount_TW.setRowCount(5)
        item = QtWidgets.QTableWidgetItem()
        self.fileCount_TW.setVerticalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.fileCount_TW.setVerticalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.fileCount_TW.setVerticalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.fileCount_TW.setVerticalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.fileCount_TW.setVerticalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.fileCount_TW.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.fileCount_TW.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.fileCount_TW.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.fileCount_TW.setHorizontalHeaderItem(3, item)
        self.fileCount_TW.horizontalHeader().setCascadingSectionResizes(False)
        self.fileCount_TW.horizontalHeader().setDefaultSectionSize(110)
        self.gridLayout_4.addWidget(self.fileCount_TW, 1, 0, 1, 4)
        self.deleteAllFile_PB = PushButton(self.CardWidget_3)
        self.deleteAllFile_PB.setObjectName("deleteAllFile_PB")
        self.gridLayout_4.addWidget(self.deleteAllFile_PB, 0, 3, 1, 1)
        self.gridLayout_5.addWidget(self.CardWidget_3, 2, 0, 1, 1)
        self.CardWidget_4 = CardWidget(DVW_Widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.CardWidget_4.sizePolicy().hasHeightForWidth())
        self.CardWidget_4.setSizePolicy(sizePolicy)
        self.CardWidget_4.setObjectName("CardWidget_4")
        self.gridLayout = QtWidgets.QGridLayout(self.CardWidget_4)
        self.gridLayout.setObjectName("gridLayout")
        self.downloadStatus_TL = TitleLabel(self.CardWidget_4)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.downloadStatus_TL.sizePolicy().hasHeightForWidth())
        self.downloadStatus_TL.setSizePolicy(sizePolicy)
        self.downloadStatus_TL.setObjectName("downloadStatus_TL")
        self.gridLayout.addWidget(self.downloadStatus_TL, 0, 0, 1, 1)
        self.downloadStatus_TW = TableWidget(self.CardWidget_4)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(2)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.downloadStatus_TW.sizePolicy().hasHeightForWidth())
        self.downloadStatus_TW.setSizePolicy(sizePolicy)
        self.downloadStatus_TW.setMinimumSize(QtCore.QSize(800, 0))
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
        self.gridLayout.addWidget(self.downloadStatus_TW, 1, 0, 1, 1)
        spacerItem3 = QtWidgets.QSpacerItem(44, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem3, 1, 1, 1, 1)
        self.gridLayout_5.addWidget(self.CardWidget_4, 0, 1, 3, 1)

        self.retranslateUi(DVW_Widget)
        QtCore.QMetaObject.connectSlotsByName(DVW_Widget)

    def retranslateUi(self, DVW_Widget):
        _translate = QtCore.QCoreApplication.translate
        DVW_Widget.setWindowTitle(_translate("DVW_Widget", "Form"))
        self.argsCount_TL.setText(_translate("DVW_Widget", "设备状态"))
        self.startDownLoad_PB.setText(_translate("DVW_Widget", "开始下载"))
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
        item = self.downloadProgress_TW.horizontalHeaderItem(0)
        item.setText(_translate("DVW_Widget", "IP"))
        item = self.downloadProgress_TW.horizontalHeaderItem(1)
        item.setText(_translate("DVW_Widget", "下载进度"))
        item = self.downloadProgress_TW.horizontalHeaderItem(2)
        item.setText(_translate("DVW_Widget", "执行状态"))
        self.reDownload_PB.setText(_translate("DVW_Widget", "重新下载"))
        self.TitleLabel.setText(_translate("DVW_Widget", "下载错误"))
        item = self.downloadError_TW.verticalHeaderItem(0)
        item.setText(_translate("DVW_Widget", "1"))
        item = self.downloadError_TW.verticalHeaderItem(1)
        item.setText(_translate("DVW_Widget", "2"))
        item = self.downloadError_TW.verticalHeaderItem(2)
        item.setText(_translate("DVW_Widget", "3"))
        item = self.downloadError_TW.verticalHeaderItem(3)
        item.setText(_translate("DVW_Widget", "4"))
        item = self.downloadError_TW.verticalHeaderItem(4)
        item.setText(_translate("DVW_Widget", "5"))
        item = self.downloadError_TW.horizontalHeaderItem(0)
        item.setText(_translate("DVW_Widget", "IP"))
        item = self.downloadError_TW.horizontalHeaderItem(1)
        item.setText(_translate("DVW_Widget", "下载错误数量"))
        self.TitleLabel_2.setText(_translate("DVW_Widget", "文件数量"))
        self.convert_PB.setText(_translate("DVW_Widget", "MP4转JPG"))
        item = self.fileCount_TW.verticalHeaderItem(0)
        item.setText(_translate("DVW_Widget", "1"))
        item = self.fileCount_TW.verticalHeaderItem(1)
        item.setText(_translate("DVW_Widget", "2"))
        item = self.fileCount_TW.verticalHeaderItem(2)
        item.setText(_translate("DVW_Widget", "3"))
        item = self.fileCount_TW.verticalHeaderItem(3)
        item.setText(_translate("DVW_Widget", "4"))
        item = self.fileCount_TW.verticalHeaderItem(4)
        item.setText(_translate("DVW_Widget", "5"))
        item = self.fileCount_TW.horizontalHeaderItem(0)
        item.setText(_translate("DVW_Widget", "文件夹"))
        item = self.fileCount_TW.horizontalHeaderItem(1)
        item.setText(_translate("DVW_Widget", "预计下载数量"))
        item = self.fileCount_TW.horizontalHeaderItem(2)
        item.setText(_translate("DVW_Widget", "jpg"))
        item = self.fileCount_TW.horizontalHeaderItem(3)
        item.setText(_translate("DVW_Widget", "mp4"))
        self.deleteAllFile_PB.setText(_translate("DVW_Widget", "删除所有文件"))
        self.downloadStatus_TL.setText(_translate("DVW_Widget", "下载状态"))
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
from qfluentwidgets import CardWidget, PushButton, TableWidget, TitleLabel
