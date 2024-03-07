# 页面提供一个全屏按钮。哦，这个按钮就直接开出来一个dialog了
# 整个mainwindow.hide掉，然后dialog是全屏的，dialog里有一个退出按钮，可以选择画圆还是画矩形，还有颜色控制
# 先来看看label开图片的样子吧，哦，外面还有scrollArea
import sys
from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QGridLayout, QApplication, QLabel, QScrollArea, QGroupBox
from qfluentwidgets import ScrollArea, PushButton

from app.picture_process_widget.base_ppw import BaseFullScreenPicture
from app.picture_process_widget.utils.toolBox import ToolsGroupBox


# class paletteWidget(QWidget):
#


class PPWclass(BaseFullScreenPicture):  # TODO 这个基类的名字记得统一
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("PPW_Widget")

        # TODO debug阶段的代码 后期要等父类主窗体那边进入本 组件才需要最大化
        parent.showMaximized()  # 父类窗体最大化

        self.addPic()

        # 开一个狗 监控当前combox选中的文件夹
        # 只有当用户重新 点击 修改图片按钮 的时候再跑一边videoProcess文件夹下有多少个子级文件夹

    def addToolButtonInTitleBar(self, titleBarWidget):
        # 新功能，如果当前界面是 修改图片 就在标题栏上加几个按钮
        hBoxLayout = titleBarWidget.hBoxLayout  # 这个hBoxLayout的存在我是提前查过的，这样兼容性不好
        self.toolsGroupBox = ToolsGroupBox()
        hBoxLayout.insertStretch(2, 100)  # 那个弹簧组件，spacerItem，两边各一个，把groupBox挤到中间
        hBoxLayout.insertWidget(3, self.toolsGroupBox, 0, Qt.AlignLeft)
        hBoxLayout.insertStretch(4, 100)

    def scanDirsAddToDirPathComboBox(self):
        pass

    def addPic(self):
        screen_resolution = QApplication.desktop().screenGeometry()
        new_width = screen_resolution.width() // 4
        new_height = screen_resolution.height() // 4
        verScrollBar = self.scrollArea.verticalScrollBar()
        verScrollBarWidth = verScrollBar.width() // 4 + (verScrollBar.width() % 4 != 0)
        new_width -= verScrollBarWidth

        dirPath = Path(r"C:\Users\Administrator\Documents\CodeProject\ATO\app\picture_process_widget\0307")
        self.fileList = []
        [self.fileList.append(file) for file in dirPath.iterdir() if file.is_file() and file.suffix == ".jpg"]

        for index, filePath in enumerate(self.fileList):
            picLabel = QLabel(self.scrollAreaWidgetContents)
            pixmap = QPixmap(str(filePath))
            scaled_pixmap = pixmap.scaled(new_width, new_height, Qt.KeepAspectRatio)  # 等比例缩放图片
            picLabel.setPixmap(scaled_pixmap)
            row, col = divmod(index, 4)
            self.gridLayout_2.addWidget(picLabel, row, col)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = PPWclass()
    form.show()
    sys.exit(app.exec_())
