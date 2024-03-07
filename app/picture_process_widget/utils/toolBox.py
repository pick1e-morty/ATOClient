import sys

from PyQt5.QtCore import QRect, Qt
from PyQt5.QtWidgets import QApplication, QFrame, QHBoxLayout, QSizePolicy, QGroupBox
from qfluentwidgets import PushButton, ComboBox, BodyLabel


class ToolsGroupBox(QGroupBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName(u"groupBox")
        self.initUI()

    def initUI(self):
        self.setGeometry(QRect(100, 260, 644, 34))
        self.setStyleSheet("QGroupBox { border: 1px solid transparent; }")  # groupBox边框透明
        # 尺寸策略对象，设置水平和垂直拉伸为0，即不允许groupBox拉伸
        sizePolicy1 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy1)
        self.setAlignment(Qt.AlignCenter)  # 居中对齐
        self.horizontalLayout = QHBoxLayout(self)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(9, 0, 9, 0)
        self.BodyLabel_4 = BodyLabel(self)
        self.BodyLabel_4.setObjectName(u"BodyLabel_4")
        self.BodyLabel_4.setText("目录")
        self.horizontalLayout.addWidget(self.BodyLabel_4)
        self.dirPath_CB = ComboBox(self)
        self.dirPath_CB.setObjectName(u"dirPath_CB")
        self.horizontalLayout.addWidget(self.dirPath_CB)
        self.line_3 = QFrame(self)
        self.line_3.setObjectName(u"line_3")
        self.line_3.setFrameShape(QFrame.VLine)
        self.line_3.setFrameShadow(QFrame.Sunken)
        self.horizontalLayout.addWidget(self.line_3)
        self.BodyLabel = BodyLabel(self)
        self.BodyLabel.setObjectName(u"BodyLabel")
        self.BodyLabel.setText("列数")
        self.horizontalLayout.addWidget(self.BodyLabel)
        self.colNum_CB = ComboBox(self)
        self.colNum_CB.setObjectName(u"colNum_CB")
        self.horizontalLayout.addWidget(self.colNum_CB)
        self.line_4 = QFrame(self)
        self.line_4.setObjectName(u"line_4")
        self.line_4.setFrameShape(QFrame.VLine)
        self.line_4.setFrameShadow(QFrame.Sunken)
        self.horizontalLayout.addWidget(self.line_4)
        self.BodyLabel_2 = BodyLabel(self)
        self.BodyLabel_2.setObjectName(u"BodyLabel_2")
        self.BodyLabel_2.setText("形状")
        self.horizontalLayout.addWidget(self.BodyLabel_2)
        self.shape_CB = ComboBox(self)
        self.shape_CB.setObjectName(u"shape_CB")
        self.horizontalLayout.addWidget(self.shape_CB)
        self.line_5 = QFrame(self)
        self.line_5.setObjectName(u"line_5")
        self.line_5.setFrameShape(QFrame.VLine)
        self.line_5.setFrameShadow(QFrame.Sunken)
        self.horizontalLayout.addWidget(self.line_5)
        self.BodyLabel_3 = BodyLabel(self)
        self.BodyLabel_3.setObjectName(u"BodyLabel_3")
        self.BodyLabel_3.setText("颜色")
        self.horizontalLayout.addWidget(self.BodyLabel_3)
        self.color_CB = ComboBox(self)
        self.color_CB.setObjectName(u"color_CB")
        self.horizontalLayout.addWidget(self.color_CB)
        self.line_6 = QFrame(self)
        self.line_6.setObjectName(u"line_6")
        self.line_6.setFrameShape(QFrame.VLine)
        self.line_6.setFrameShadow(QFrame.Sunken)
        self.horizontalLayout.addWidget(self.line_6)
        self.delUnMarkImg_PB = PushButton(self)
        self.delUnMarkImg_PB.setObjectName(u"delUnMarkImg_PB")
        self.delUnMarkImg_PB.setText("删除未标记图片")
        self.horizontalLayout.addWidget(self.delUnMarkImg_PB)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    forms = ToolsGroupBox()
    forms.show()

    sys.exit(app.exec_())
