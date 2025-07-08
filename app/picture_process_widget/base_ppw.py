# 页面提供一个全屏按钮。哦，这个按钮就直接开出来一个dialog了
# 整个mainwindow.hide掉，然后dialog是全屏的，dialog里有一个退出按钮，可以选择画圆还是画矩形，还有颜色控制
# 先来看看label开图片的样子吧，哦，外面还有scrollArea
import sys
from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (
    QWidget,
    QGridLayout,
    QApplication,
    QLabel,
    QScrollArea,
    QSpacerItem,
    QSizePolicy,
    QLayout,
)
from qfluentwidgets import ScrollArea


class BasePPW(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # self.showFullScreen()
        self.gridLayout_1 = QGridLayout(self)  # 第一级layout只装scrollArea
        self.gridLayout_1.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_1.setSpacing(0)
        self.scrollArea = ScrollArea(self)
        self.scrollArea.setStyleSheet("border:0px")
        self.scrollArea.setWidgetResizable(True)  # 我手写UI的时候这行好像不用加
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scrollAreaWidgetContents = QWidget()
        self.gridLayout_2 = QGridLayout(
            self.scrollAreaWidgetContents
        )  # 第二级layout，里面是pixmapLabel，
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setSpacing(0)
        self.gridLayout_2.setSizeConstraint(QLayout.SetFixedSize)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.gridLayout_1.addWidget(self.scrollArea, 0, 0, 1, 1)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = BasePPW()
    form.show()

    screen_resolution = QApplication.desktop().screenGeometry()
    print(screen_resolution.width())
    print(screen_resolution.height())
    screen_resolution = QApplication.desktop().availableGeometry()
    print(screen_resolution.width())
    print(screen_resolution.height())
    sys.exit(app.exec_())
