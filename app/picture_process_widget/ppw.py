# 页面提供一个全屏按钮。哦，这个按钮就直接开出来一个dialog了
# 整个mainwindow.hide掉，然后dialog是全屏的，dialog里有一个退出按钮，可以选择画圆还是画矩形，还有颜色控制
# 先来看看label开图片的样子吧，哦，外面还有scrollArea
import sys
from pathlib import Path

from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QGridLayout, QApplication, QLabel, QScrollArea, QGroupBox
from loguru import logger
from qfluentwidgets import ScrollArea, PushButton

from app.picture_process_widget.base_ppw import BaseFullScreenPicture
from app.picture_process_widget.utils.tool_box import ToolsGroupBox
from app.picture_process_widget.utils.writeable_label import WriteableLabel

# dvw下载后的图片存放地址，ppw要从这个文件夹中取子级文件夹中的图片
picDirPath = Path(__file__).parent.parent.parent / "pic"


class PPWclass(BaseFullScreenPicture):  # TODO 这个基类的名字记得统一
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("PPW_Widget")

        self.color = Qt.black
        self.penWidth = 3
        self.savePenWidth = 3
        self.shape = "矩形"
        self.picSuffixTuple = (".jpeg", ".jpg")

        self.markedImgLabel = None

        # TODO debug阶段的代码 后期要等父类主窗体那边进入本 组件才需要最大化
        parent.showMaximized()  # 父类窗体最大化

    def addToolButtonInTitleBar(self, titleBarWidget):
        # 新功能，如果当前界面是 修改图片 就在标题栏上加几个按钮
        hBoxLayout = titleBarWidget.hBoxLayout  # 这个hBoxLayout的存在我是提前查过的，这样耦合太高。都放到主窗体的标题栏了，耦合不可能低了
        self.toolsGroupBox = ToolsGroupBox(self.picSuffixTuple, self)
        hBoxLayout.insertStretch(2, 100)  # 那个弹簧组件，spacerItem，两边各一个，把groupBox挤到中间
        hBoxLayout.insertWidget(3, self.toolsGroupBox, 0, Qt.AlignLeft)
        hBoxLayout.insertStretch(4, 100)
        self.toolsGroupBox.dirPath_CB.currentIndexChanged.connect(self.changeDirPath)
        self.toolsGroupBox.colNum_CB.currentIndexChanged.connect(self.changeColShow)
        self.toolsGroupBox.color_CB.currentIndexChanged.connect(self.changeColor)
        self.toolsGroupBox.penWidth_LE.textChanged.connect(self.changePenWidth)
        self.toolsGroupBox.shape_CB.currentIndexChanged.connect(self.changeShape)
        self.toolsGroupBox.delUnMarkImg_PB.clicked.connect(self.delUnMarkImg)
        self.toolsGroupBox.setHidden(True)  # 上面说初始化后先隐藏掉

    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def addPictureLabel(self):
        # 向scrllArea中的第一级layout，gridLayout_2中遍历添加pixmapLabel
        gb = self.toolsGroupBox
        dirPath = gb.dirPath_CB.itemData(gb.dirPath_CB.currentIndex())  # 当前选中文件夹和列数
        colNum = int(gb.colNum_CB.itemText(gb.colNum_CB.currentIndex()))
        new_width = self.scrollArea.width() // colNum  # 计算新的长度，由于窗体最大化，高度不加入计算和设置
        verScrollBar = self.scrollArea.scrollDelagate.vScrollBar
        verScrollBarWidth = verScrollBar.width() // colNum
        new_width -= verScrollBarWidth  # 减去右边滚动条的宽度

        fileList = [file for file in dirPath.iterdir() if file.is_file() and file.suffix in self.picSuffixTuple]
        self.clear_layout(self.gridLayout_2)  # 清空图片label

        self.toolsGroupBox.countingFile()  # 刷一下已标记的标签显示
        self.markedImgLabel = None  # 重置标记
        for index, filePath in enumerate(fileList):
            picLabel = WriteableLabel(palette=self, filePath=filePath, parent=self.scrollAreaWidgetContents)  # 这样写应该是不符合“规定”的。
            """因为widget的上级父类最终是它在ui上的父类，最初传的那个parent只是传递实例属性，实际上这个widget调整位置之后父类就被自动变更了。不知道我有没有说清楚
            就比如现在这个WriteableLabel的父类就不是scrollAreaWidgetContents，而是scrollAreaWidgetContents下面的一个widget。
            python没有类似c指针的变量传递方式，我不能直接修改一个变量的数值，而是会被新建变量所替换。所以我想的办法是直接把“某个父类”引用给这个labelWidget用作实例变量共享。
            还有一种安全的实现思路，就是ppwInterface做事件拦截，判左键按下的动作，取鼠标坐标下的widget是不是WriteableLabel，如果是就把ppwInterface中的三个painter所需变量赋值给这个WriteableLabel。
            但两者的代码量和逻辑复杂程度让我选择了前者。
            """
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
            logger.trace(f"保存图片{self.markedImgLabel.filePath}")
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
        # 遍历picDirPath，只取第一级的文件夹
        dirsPathList = [path for path in picDirPath.iterdir() if path.is_dir()]
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

    @pyqtSlot(int)
    def changeColor(self, index):
        self.color = self.toolsGroupBox.color_CB.itemData(index)

    @pyqtSlot(str)
    def changePenWidth(self, str):
        self.penWidth = float(str)

    @pyqtSlot(int)
    def changeShape(self, index):
        self.shape = self.toolsGroupBox.shape_CB.itemText(index)

    @pyqtSlot(bool)
    def delUnMarkImg(self, clicked):
        gb = self.toolsGroupBox
        dirPath = gb.dirPath_CB.itemData(gb.dirPath_CB.currentIndex())  # 当前选中文件夹和列数
        [file.unlink(missing_ok=True) for file in dirPath.iterdir() if file.is_file() and file.suffix == ".jpg"]

        # TODO 这步查layout所有的label，遍历label的filePath属性，不在walk的新文件列表中就给removeWidget了
        self.addPictureLabel()  # 刷新，不存在的文件要删除在界面上的label。

if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = PPWclass()
    form.show()
    sys.exit(app.exec_())
