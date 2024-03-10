# 页面提供一个全屏按钮。哦，这个按钮就直接开出来一个dialog了
# 整个mainwindow.hide掉，然后dialog是全屏的，dialog里有一个退出按钮，可以选择画圆还是画矩形，还有颜色控制
# 先来看看label开图片的样子吧，哦，外面还有scrollArea
import sys
from pathlib import Path

from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QGridLayout, QApplication, QLabel, QScrollArea, QGroupBox
from qfluentwidgets import ScrollArea, PushButton

from app.picture_process_widget.base_ppw import BaseFullScreenPicture
from app.picture_process_widget.utils.toolBox import ToolsGroupBox

# dvw下载后的图片存放地址，ppw要从这个文件夹中取子级文件夹中的图片
picDirPath = Path(__file__).parent.parent.parent / "pic"


class PPWclass(BaseFullScreenPicture):  # TODO 这个基类的名字记得统一
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("PPW_Widget")

        # TODO debug阶段的代码 后期要等父类主窗体那边进入本 组件才需要最大化
        parent.showMaximized()  # 父类窗体最大化

    def addToolButtonInTitleBar(self, titleBarWidget):
        # 新功能，如果当前界面是 修改图片 就在标题栏上加几个按钮
        hBoxLayout = titleBarWidget.hBoxLayout  # 这个hBoxLayout的存在我是提前查过的，这样耦合太高。都放到主窗体的标题栏了，耦合不可能低了
        self.toolsGroupBox = ToolsGroupBox()
        hBoxLayout.insertStretch(2, 100)  # 那个弹簧组件，spacerItem，两边各一个，把groupBox挤到中间
        hBoxLayout.insertWidget(3, self.toolsGroupBox, 0, Qt.AlignLeft)
        hBoxLayout.insertStretch(4, 100)
        self.toolsGroupBox.dirPath_CB.currentIndexChanged.connect(self.changeDirPath)
        self.toolsGroupBox.colNum_CB.currentIndexChanged.connect(self.changeColShow)

    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def addPictureLabel(self):
        # 向scrllArea中的第一级layout，gridLayout_2中遍历添加pixmapLabel
        gb = self.toolsGroupBox
        dirPath = gb.dirPath_CB.itemData(gb.dirPath_CB.currentIndex())
        colNum = int(gb.colNum_CB.itemText(gb.colNum_CB.currentIndex()))

        screen_resolution = QApplication.desktop().screenGeometry()
        new_width = screen_resolution.width() // colNum
        new_height = screen_resolution.height() // colNum
        verScrollBar = self.scrollArea.verticalScrollBar()
        # TODO 想办法取一下主题scrollArea的滚动条宽度，用减法常数。虽然现在原生的效果很不错
        # 搞好了就可以开始思考怎么画圈了
        verScrollBarWidth = verScrollBar.width() // colNum + (verScrollBar.width() % 4 != 0)
        navigationInterface = self.parent().parent().navigationInterface  # 因为本组件最终会被添加到QStackedWidget，上二级才是最顶级的组件。不知道这里未来会不会出问题。
        navigationInterfaceWidth = (navigationInterface.width() // colNum) + (navigationInterface.width() % 4 != 0)
        new_width -= (verScrollBarWidth + navigationInterfaceWidth)  # 减去主窗体左边导航栏的宽度和右边滚动条的宽度

        self.fileList = []
        [self.fileList.append(file) for file in dirPath.iterdir() if file.is_file() and file.suffix == ".jpg"]
        self.clear_layout(self.gridLayout_2)

        for index, filePath in enumerate(self.fileList):
            picLabel = QLabel(self.scrollAreaWidgetContents)
            pixmap = QPixmap(str(filePath))
            scaled_pixmap = pixmap.scaled(new_width, new_height, Qt.KeepAspectRatio)  # 等比例缩放图片
            picLabel.setPixmap(scaled_pixmap)
            row, col = divmod(index, colNum)
            self.gridLayout_2.addWidget(picLabel, row, col)

    def scanDirsAddToDirPathComboBox(self):
        # 遍历picDirPath，只取第一级的文件夹
        dirsPathList = [path for path in picDirPath.iterdir() if path.is_dir()]
        print(dirsPathList)
        # 取末级路径 .stem，作为comboBox的item文本，整体路径作为item的data
        self.toolsGroupBox.dirPath_CB.clear()
        dirsPathList = sorted(dirsPathList)  # 带个顺序
        for dirPath in dirsPathList:
            stem = dirPath.stem
            absDirPath = dirPath.absolute()
            self.toolsGroupBox.dirPath_CB.addItem(stem, userData=absDirPath)

    @pyqtSlot(int)
    def changeDirPath(self, index):
        self.addPictureLabel()

    @pyqtSlot(int)
    def changeColShow(self, index):
        self.addPictureLabel()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = PPWclass()
    form.show()
    sys.exit(app.exec_())
