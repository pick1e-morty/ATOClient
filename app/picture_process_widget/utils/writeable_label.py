from pathlib import Path

from PyQt5.QtCore import QPoint, QRect, Qt, pyqtSignal, QRectF, QPointF
from PyQt5.QtGui import QPixmap, QPen, QPainter
from PyQt5.QtWidgets import QLabel
from loguru import logger


class WriteableLabel(QLabel):
    markImage = pyqtSignal(QLabel)

    def __init__(self, palette, filePath, parent=None):
        super().__init__(parent)
        self.palette = palette
        self.filePath = str(filePath)
        self.startPoint = None  # 圆形或矩形的开始坐标
        self.endPoint = None
        self.drawing = False  #
        self.start = False

        self.markPixmap = QPixmap(r"C:\Users\Administrator\Documents\CodeProject\ATO\app\picture_process_widget\mark.png")
        self.markFlag = False
        self.unWriteable = False  # 不可编辑

        if Path(self.filePath).suffix == ".jpeg":
            self.markFlag = True
            self.unWriteable = True

    def savePixmap(self):
        # label这边重新读取源文件（无画质损失），对pixmap进行绘制，最终保存。

        # 真正的问题是坐标偏移，还记不记得那个等比例缩放
        self.markFlag = True
        pixmap = QPixmap(str(self.filePath))
        widthScaleFactor = pixmap.width() / self.width()
        heightScaleFactor = pixmap.height() / self.height()
        w = float((self.endPoint.x() - self.startPoint.x()) * widthScaleFactor)
        h = float((self.endPoint.y() - self.startPoint.y()) * heightScaleFactor)
        x = self.startPoint.x() * widthScaleFactor
        y = self.startPoint.y() * heightScaleFactor

        painter = QPainter(pixmap)
        painter.setPen(QPen(self.palette.color, self.palette.penWidth + widthScaleFactor))  # 设置画笔颜色和宽度,由于label被缩放了widthScaleFactor倍，所以线宽要给加回去，不然两个差别太大。
        if self.palette.shape == "矩形":
            painter.drawRect(QRectF(x, y, w, h))
        elif self.palette.shape == "圆形":
            painter.drawEllipse(QRectF(x, y, w, h))
        painter.end()
        filePath = Path(self.filePath)
        filePath.unlink(missing_ok=True)
        saveFilePath = filePath.with_suffix(".jpeg")
        saveResult = pixmap.save(str(saveFilePath), quality=100)
        logger.trace(f"图片保存结果{saveResult}")
        self.repaint()  # 把那个对号刷出来

    def paintEvent(self, event):
        super().paintEvent(event)

        if self.markFlag:
            painter = QPainter(self)
            painter.begin(self)
            painter.drawPixmap(self.rect(), self.markPixmap)
            painter.end()
        if self.drawing:
            painter = QPainter()
            painter.begin(self)
            pen = QPen(self.palette.color, self.palette.penWidth)
            painter.setPen(pen)
            if self.palette.shape == "矩形":
                painter.drawRect(QRect(self.startPoint, self.endPoint))
            elif self.palette.shape == "圆形":
                painter.drawEllipse(QRect(self.startPoint, self.endPoint))
            painter.end()
        elif self.startPoint is not None and self.endPoint is not None:  # 拖动结束后还要继续画
            painter = QPainter()
            painter.begin(self)
            pen = QPen(self.palette.color, self.palette.penWidth)
            painter.setPen(pen)
            if self.palette.shape == "矩形":
                painter.drawRect(QRect(self.startPoint, self.endPoint))
            elif self.palette.shape == "圆形":
                painter.drawEllipse(QRect(self.startPoint, self.endPoint))
            painter.end()

    def mousePressEvent(self, event):
        if not self.start and self.unWriteable is not True:
            self.startPoint = event.pos()
            self.start = True

    def mouseReleaseEvent(self, event):
        if self.drawing:
            self.drawing = False
            self.start = False
            self.markImage.emit(self)

    def mouseMoveEvent(self, event):
        if self.start:
            self.endPoint = event.pos()
            self.drawing = True
            self.repaint()
