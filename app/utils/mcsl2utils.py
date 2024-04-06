#     Copyright 2024, MCSL Team, mailto:services@mcsl.com.cn
#
#     Part of "MCSL2", a simple and multifunctional Minecraft server launcher.
#
#     Licensed under the GNU General Public License, Version 3.0, with our
#     additional agreements. (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#        https://github.com/MCSLTeam/MCSL2/raw/master/LICENSE
#
################################################################################
"""
These are the built-in functions of MCSL2. They are just for solving the circular import.
"""

import enum
from types import TracebackType
from typing import Type

from PyQt5.QtCore import QRect, Qt, QSize
# import aria2p
# import psutil
# from MCSL2Lib.ProgramControllers.logController import _MCSL2Logger
from PyQt5.QtCore import QUrl, QFile
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QSizePolicy, QVBoxLayout, QWidget, QFrame, QScrollArea
from qfluentwidgets import BodyLabel, SmoothScrollArea, SmoothScrollDelegate


# MCSL2Logger = _MCSL2Logger()
# AUTHOR_SERVERS = ["18.65.216.60"]


def openWebUrl(Url):
    """打开网址"""
    QDesktopServices.openUrl(QUrl(Url))


def openLocalFile(FilePath):
    """打开本地文件(夹)"""
    QDesktopServices.openUrl(QUrl.fromLocalFile(FilePath))


def readFile(file: str):
    f = QFile(file)
    f.open(QFile.ReadOnly)
    content = str(f.readAll(), encoding="utf-8")
    f.close()
    return content


class ExceptionFilterMode(enum.Enum):
    RAISE_AND_PRINT = enum.auto()  # 过滤：弹框提示，也会抛出异常
    RAISE = enum.auto()  # 过滤：不弹框提示，但是会抛出异常
    PASS = enum.auto()  # 过滤：不弹框提示，也不抛出异常，就当做什么都没发生
    SILENT = enum.auto()  # 过滤：不弹框提示，也不抛出异常，就当做什么都没发生


def exceptionFilter(ty: Type[BaseException], value: BaseException, _traceback: TracebackType) -> ExceptionFilterMode:
    """
    过滤异常
    """
    if isinstance(value, AttributeError) and "MessageBox" in str(value):
        return ExceptionFilterMode.SILENT
    if isinstance(value, RuntimeError) and "wrapped C/C++ object of type" in str(value):
        return ExceptionFilterMode.PASS
    if isinstance(value, Exception) and "raise test" in str(value):
        return ExceptionFilterMode.RAISE
    if isinstance(value, Exception) and "pass test" in str(value):
        return ExceptionFilterMode.PASS
    if isinstance(value, Exception) and "print test" in str(value):
        return ExceptionFilterMode.RAISE_AND_PRINT
    if isinstance(value, Exception) and "RunningServerHeaderCardWidget cannot be converted to PyQt5.QtWidgets.QLayoutItem" in str(value):
        return ExceptionFilterMode.SILENT
    if isinstance(value, Exception) and "sipBadCatcherResult" in str(value):
        return ExceptionFilterMode.SILENT

    return ExceptionFilterMode.RAISE_AND_PRINT


class MCSL2SmoothScrollArea(SmoothScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        scrollAreaViewportQss = "background-color: transparent;"
        self.viewport().setStyleSheet(scrollAreaViewportQss)
        self.delegate = SmoothScrollDelegate(self, True)
        self.setFrameShape(QScrollArea.NoFrame)
        self.setAttribute(Qt.WA_StyledBackground)


class ExceptionWidget(QWidget):
    def __init__(self, traceStr):
        super().__init__()
        self.exceptionScrollArea = MCSL2SmoothScrollArea(self)
        self.exceptionScrollArea.setGeometry(QRect(50, 10, 480, 150))
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.exceptionScrollArea.sizePolicy().hasHeightForWidth()
        )
        self.exceptionScrollArea.setSizePolicy(sizePolicy)
        self.exceptionScrollArea.setMinimumSize(QSize(480, 0))
        self.exceptionScrollArea.setMaximumSize(QSize(480, 320))
        self.exceptionScrollArea.setFrameShape(QFrame.NoFrame)
        self.exceptionScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.exceptionScrollArea.setWidgetResizable(True)
        self.exceptionScrollAreaWidgetContents = QWidget()
        self.exceptionScrollAreaWidgetContents.setGeometry(QRect(0, 0, 468, 320))
        self.verticalLayout_2 = QVBoxLayout(self.exceptionScrollAreaWidgetContents)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.exceptionLabel = BodyLabel(self.exceptionScrollAreaWidgetContents)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.exceptionLabel.sizePolicy().hasHeightForWidth()
        )
        self.exceptionLabel.setSizePolicy(sizePolicy)
        self.exceptionLabel.setMinimumSize(QSize(450, 200))
        self.exceptionLabel.setMaximumSize(QSize(450, 16777215))
        self.exceptionLabel.setAlignment(Qt.AlignLeading | Qt.AlignLeft | Qt.AlignTop)
        self.exceptionLabel.setWordWrap(True)
        self.verticalLayout_2.addWidget(self.exceptionLabel)
        self.exceptionScrollArea.setWidget(self.exceptionScrollAreaWidgetContents)
        self.exceptionLabel.setText(traceStr)
