# 页面提供一个全屏按钮。哦，这个按钮就直接开出来一个dialog了
# 整个mainwindow.hide掉，然后dialog是全屏的，dialog里有一个退出按钮，可以选择画圆还是画矩形，还有颜色控制
# 先来看看label开图片的样子吧，哦，外面还有scrollArea
import sys

from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QLabel

from app.picture_process_widget.base_ppw import BasePPW
from app.picture_process_widget.widget.tool_box import ToolsGroupBox
from app.picture_process_widget.widget.writeable_label import WriteableLabel
from app.utils.project_path import DVW_DOWNLOAD_VIDEO_PATH


class PPWclass(BasePPW):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("PPW_Widget")

        self.color = Qt.red
        self.penWidth = 3
        self.savePenWidth = 3
        self.shape = "圆形"
        self.picSuffixTuple = (".jpeg", ".jpg")

        self.markedImgLabel = None

    def addToolButtonInTitleBar(self, titleBarWidget):
        # 新功能，如果当前界面是 修改图片 就在标题栏上加几个按钮
        hBoxLayout = (
            titleBarWidget.hBoxLayout
        )  # 这个hBoxLayout的存在我是提前查过的，这样耦合太高。都放到主窗体的标题栏了，耦合不可能低了
        self.toolsGroupBox = ToolsGroupBox(self.picSuffixTuple, self)
        hBoxLayout.insertStretch(
            2, 100
        )  # 那个弹簧组件，spacerItem，两边各一个，把groupBox挤到中间
        hBoxLayout.insertWidget(3, self.toolsGroupBox, 0, Qt.AlignLeft)
        hBoxLayout.insertStretch(4, 100)
        self.toolsGroupBox.dirPath_CB.currentIndexChanged.connect(self.changeDirPath)
        self.toolsGroupBox.colNum_CB.currentIndexChanged.connect(self.changeColShow)
        self.toolsGroupBox.delUnMarkImg_PB.clicked.connect(self.delUnMarkImg)
        self.toolsGroupBox.setHidden(True)  # 上面说初始化后先隐藏掉

    def clearPictureLabel(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def addPictureLabel(self):
        # 向scrllArea中的第一级layout，gridLayout_2中遍历添加pixmapLabel
        gb = self.toolsGroupBox
        dirPath = gb.dirPath_CB.itemData(
            gb.dirPath_CB.currentIndex()
        )  # 当前选中文件夹和列数
        colNum = int(gb.colNum_CB.itemText(gb.colNum_CB.currentIndex()))
        new_width = (
            self.scrollArea.width() // colNum
        )  # 计算新的长度，由于窗体最大化，高度不加入计算和设置
        verScrollBar = self.scrollArea.scrollDelagate.vScrollBar
        verScrollBarWidth = verScrollBar.width() // colNum
        new_width -= verScrollBarWidth  # 减去右边滚动条的宽度

        self.clearPictureLabel(self.gridLayout_2)  # 清空图片label
        self.toolsGroupBox.countingFile()  # 刷一下已标记的标签显示
        if (
            not dirPath
        ):  # 因为在 删除未标记图片 时，如果此操作使文件夹为空，删除未标记图片 方法就会直接删除这个文件夹及其所在dirPath_CB中的item
            return  # 此举会导致dirPath_CB触发itemChanged，从而导致本方法addPictureLabel被触发，故作此判断。
        fileList = [
            file
            for file in dirPath.iterdir()
            if file.is_file() and file.suffix in self.picSuffixTuple
        ]

        self.markedImgLabel = None  # 重置标记
        for index, filePath in enumerate(fileList):
            picLabel = WriteableLabel(
                getPaletteMethod=self.getPalette,
                filePath=filePath,
                parent=self.scrollAreaWidgetContents,
            )  # 这样写应该是不符合“规定”的。
            picLabel.markImage.connect(self.do_markImage)
            pixmap = QPixmap(str(filePath))
            scaled_pixmap = pixmap.scaledToWidth(new_width)
            picLabel.setPixmap(scaled_pixmap)
            row, col = divmod(index, colNum)
            self.gridLayout_2.addWidget(picLabel, row, col)

    @pyqtSlot(QLabel)
    def do_markImage(self, label):
        if self.markedImgLabel is None:
            self.markedImgLabel = label
        elif self.markedImgLabel == label:  # 这说明用户重绘了，这时候不需要保存
            pass
        else:
            self.markedImgLabel.savePixmap()
            self.toolsGroupBox.countingFile()  # 刷一下已标记的标签显示
            self.markedImgLabel = label
            # 上面附一层标记成功的，半透明的标记成功图标
            # self.markedImgLabel.setStyleSheet("color: rgb(0, 255, 127);background-color: rgb(255, 255, 127);")

    def keyPressEvent(self, event):  # 按空格也表示保存
        if event.key() == Qt.Key_Space:
            if self.markedImgLabel is not None:
                self.markedImgLabel.savePixmap()
                self.toolsGroupBox.countingFile()

    def scanDirsAddToDirPathComboBox(self):
        # DVW_DOWNLOAD_VIDEO_PATH，只取第一级的文件夹
        dirsPathList = [
            path for path in DVW_DOWNLOAD_VIDEO_PATH.iterdir() if path.is_dir()
        ]
        # 取末级路径 .stem，作为comboBox的item文本，整体路径作为item的data
        self.toolsGroupBox.dirPath_CB.clear()
        self.clearPictureLabel(self.gridLayout_2)  # 清空图片label
        self.toolsGroupBox.countingFile()  # 刷新文件标记状态
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

    def getPalette(self) -> (str, str, str):
        color = self.toolsGroupBox.color_CB.currentText()
        penWidth = self.toolsGroupBox.penWidth_LE.text()
        shape = self.toolsGroupBox.shape_CB.currentText()
        return color, penWidth, shape

    @pyqtSlot(bool)
    def delUnMarkImg(self, clicked):
        dirPath = self.toolsGroupBox.dirPath_CB.itemData(
            self.toolsGroupBox.dirPath_CB.currentIndex()
        )  # 当前选中文件夹和列数
        if dirPath:
            [
                file.unlink(missing_ok=True)
                for file in dirPath.iterdir()
                if file.is_file() and file.suffix == ".jpg"
            ]
            if not len(
                [file for file in dirPath.iterdir()]
            ):  # 判断文件夹是否为空，然后删除这个文件夹的item
                self.toolsGroupBox.dirPath_CB.removeItem(
                    self.toolsGroupBox.dirPath_CB.currentIndex()
                )
                dirPath.rmdir()
                return
            # TODO 这步查layout所有的label，遍历label的filePath属性，不在walk的新文件列表中就给removeWidget了
            self.addPictureLabel()  # 刷新，不存在的文件要删除在界面上的label。


if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = PPWclass()
    form.show()
    sys.exit(app.exec_())
