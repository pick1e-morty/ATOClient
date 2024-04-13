import sys

from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel, QApplication

import app.resource.resource  # type: ignore

# 随便创建一个weidget，然后把 resource中的ppw/mark.png放到界面中的label中

app = QApplication(sys.argv)
label = QLabel()
pixmap = QPixmap(":/ppw/mark.png")
label.setPixmap(pixmap)
# label.setText("123")
# ":/icons/Icons/Python_icon.ico"
# icon = QPixmap("Icons/Python_icon.ico")

label.show()
sys.exit(app.exec_())
