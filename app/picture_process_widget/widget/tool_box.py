import sys
from pathlib import Path

from PyQt5.QtCore import QRect, Qt
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import QApplication, QFrame, QHBoxLayout, QSizePolicy, QGroupBox
from qfluentwidgets import PushButton, ComboBox, BodyLabel, LineEdit


class ToolsGroupBox(QGroupBox):
    def __init__(self, picSuffixTuple, parent=None):
        super().__init__(parent)
        self.setObjectName("groupBox")
        self.picSuffixTuple = picSuffixTuple
        self.initUI()

    def initUI(self):
        self.setGeometry(QRect(40, 130, 850, 35))
        self.setStyleSheet(
            "QGroupBox { border: 1px solid transparent; }"
        )  # groupBox边框透明
        # 尺寸策略对象，设置水平和垂直拉伸为0，即不允许groupBox拉伸
        sizePolicy1 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy1)
        self.setAlignment(Qt.AlignCenter)  # 居中对齐
        self.horizontalLayout = QHBoxLayout(self)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.horizontalLayout.setContentsMargins(9, 0, 9, 0)
        self.counting_L = BodyLabel(self)  # 统计图片数量的标签
        self.counting_L.setObjectName("counting_L")
        self.counting_L.setText("总0已0未0")
        self.horizontalLayout.addWidget(self.counting_L)
        self.line_7 = QFrame(self)
        self.line_7.setObjectName("line_7")
        self.line_7.setFrameShape(QFrame.VLine)
        self.line_7.setFrameShadow(QFrame.Sunken)
        self.horizontalLayout.addWidget(self.line_7)
        self.BodyLabel_4 = BodyLabel(self)
        self.BodyLabel_4.setObjectName("BodyLabel_4")
        self.BodyLabel_4.setText("目录")
        self.horizontalLayout.addWidget(self.BodyLabel_4)
        self.dirPath_CB = ComboBox(self)
        self.dirPath_CB.setObjectName("dirPath_CB")
        self.horizontalLayout.addWidget(self.dirPath_CB)
        self.line_3 = QFrame(self)
        self.line_3.setObjectName("line_3")
        self.line_3.setFrameShape(QFrame.VLine)
        self.line_3.setFrameShadow(QFrame.Sunken)
        self.horizontalLayout.addWidget(self.line_3)
        self.BodyLabel = BodyLabel(self)
        self.BodyLabel.setObjectName("BodyLabel")
        self.BodyLabel.setText("列数")
        self.horizontalLayout.addWidget(self.BodyLabel)
        self.colNum_CB = ComboBox(self)
        self.colNum_CB.setObjectName("colNum_CB")
        self.horizontalLayout.addWidget(self.colNum_CB)
        self.line_4 = QFrame(self)
        self.line_4.setObjectName("line_4")
        self.line_4.setFrameShape(QFrame.VLine)
        self.line_4.setFrameShadow(QFrame.Sunken)
        self.horizontalLayout.addWidget(self.line_4)
        self.BodyLabel_2 = BodyLabel(self)
        self.BodyLabel_2.setObjectName("BodyLabel_2")
        self.BodyLabel_2.setText("形状")
        self.horizontalLayout.addWidget(self.BodyLabel_2)
        self.shape_CB = ComboBox(self)
        self.shape_CB.setObjectName("shape_CB")
        self.horizontalLayout.addWidget(self.shape_CB)
        self.line_8 = QFrame(self)
        self.line_8.setObjectName("line_8")
        self.line_8.setFrameShape(QFrame.VLine)
        self.line_8.setFrameShadow(QFrame.Sunken)
        self.horizontalLayout.addWidget(self.line_8)
        self.BodyLabel_6 = BodyLabel(self)
        self.BodyLabel_6.setObjectName("BodyLabel_6")
        self.BodyLabel_6.setText("线宽")
        self.horizontalLayout.addWidget(self.BodyLabel_6)
        self.penWidth_LE = LineEdit(self)
        self.penWidth_LE.setObjectName("penWidth_LE")
        self.penWidth_LE.setMaximumWidth(50)
        self.penWidth_LE.setValidator(QDoubleValidator(0.01, 99.99, 2))
        self.horizontalLayout.addWidget(self.penWidth_LE)
        self.line_5 = QFrame(self)
        self.line_5.setObjectName("line_5")
        self.line_5.setFrameShape(QFrame.VLine)
        self.line_5.setFrameShadow(QFrame.Sunken)
        self.horizontalLayout.addWidget(self.line_5)
        self.BodyLabel_3 = BodyLabel(self)
        self.BodyLabel_3.setObjectName("BodyLabel_3")
        self.BodyLabel_3.setText("颜色")
        self.horizontalLayout.addWidget(self.BodyLabel_3)
        self.color_CB = ComboBox(self)
        self.color_CB.setObjectName("color_CB")
        self.horizontalLayout.addWidget(self.color_CB)
        self.line_6 = QFrame(self)
        self.line_6.setObjectName("line_6")
        self.line_6.setFrameShape(QFrame.VLine)
        self.line_6.setFrameShadow(QFrame.Sunken)
        self.horizontalLayout.addWidget(self.line_6)
        self.delUnMarkImg_PB = PushButton(self)
        self.delUnMarkImg_PB.setObjectName("delUnMarkImg_PB")
        self.delUnMarkImg_PB.setText("删除未标记图片")
        self.horizontalLayout.addWidget(self.delUnMarkImg_PB)
        self.initColNum_CB()
        self.initShape_CB()
        self.initPenWidth_LE()
        self.initColor_CB()

    def initColNum_CB(self):
        # 向列数组合框中填充数据
        # 1，2，3，4，5，6
        self.colNum_CB.addItems(["1", "2", "3", "4", "5", "6"])
        self.colNum_CB.setCurrentIndex(3)

    def initShape_CB(self):
        # 矩形，圆形
        # 向形状组合框中填充数据
        shapeList = ["圆形", "矩形"]
        self.shape_CB.addItems(shapeList)
        self.shape_CB.setCurrentIndex(0)

    def initPenWidth_LE(self):
        self.penWidth_LE.setText("3")

    def initColor_CB(self):
        # 向颜色组合框中填充数据F
        # 黑色，红色，黄色，白色
        colorList = ["红色", "黑色", "黄色", "白色"]
        self.color_CB.addItems(colorList)
        self.color_CB.setCurrentIndex(0)

    def countingFile(self):
        zero = "0"
        dirPath = self.dirPath_CB.itemData(self.dirPath_CB.currentIndex())
        if dirPath and dirPath.exists() and dirPath.is_dir():
            if fileList := [
                file
                for file in dirPath.iterdir()
                if file.is_file() and file.suffix in self.picSuffixTuple
            ]:
                total = len(fileList)
                marked = sum(1 for p in fileList if Path(p).suffix == ".jpeg")
                unMarked = total - marked
                self.counting_L.setText(
                    f"总{total}已{marked}未{unMarked}"
                )  # 测试阶段，后面成模式了要整合为函数
            else:
                self.counting_L.setText(
                    f"总{zero}已{zero}未{zero}"
                )  # 测试阶段，后面成模式了要整合为函数
        else:
            self.counting_L.setText(
                f"总{zero}已{zero}未{zero}"
            )  # 测试阶段，后面成模式了要整合为函数


if __name__ == "__main__":
    app = QApplication(sys.argv)

    forms = ToolsGroupBox()
    forms.show()

    sys.exit(app.exec_())
