import sys

from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout

from app.app_setting_widget.widget.setting_interface import SettingInterface


class ASWclass(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)  # 调用父类构造函数，创建窗体

        self.setObjectName("ASW_Widget")
        self.hBoxLayout = QHBoxLayout(self)
        self.settingInterface = SettingInterface(self)
        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.hBoxLayout.addWidget(self.settingInterface)

if __name__ == "__main__":  # 用于当前窗体测试
    app = QApplication(sys.argv)  # 创建GUI应用程序
    forms = ASWclass()  # 创建窗体
    forms.show()
    sys.exit(app.exec_())
