import sys

from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QWidget, QLabel, QApplication
from qfluentwidgets import (
    FluentIcon as FIF,
    ScrollArea,
    PrimaryPushSettingCard,
    HyperlinkCard,
)
from qfluentwidgets import SettingCardGroup, SwitchSettingCard, ExpandLayout

from app.app_setting_widget.widget.custom_setting_card import (
    CustomComboBoxSettingCard,
    CustomOptionsSettingCard,
    CustomSpinBoxSettingCard,
    CustomCompactSpinBoxSettingCard,
)
from app.utils.global_var import YEAR, AUTHOR, VERSION, FEEDBACK_URL, HELP_URL
from app.utils.project_path import PROJECT_ROOT_PATH


class SettingInterface(ScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scrollWidget = QWidget()
        self.scrollWidget.setObjectName("scrollWidget")

        self.expandLayout = ExpandLayout(self.scrollWidget)
        self.expandLayout.setObjectName("expandLayout")

        # setting label
        self.settingLabel = QLabel(self.tr("设置 (暂未实现)"), self)
        self.settingLabel.setObjectName("settingLabel")

        # 表格处理
        self.epwGroup = SettingCardGroup("表格处理", self.scrollWidget)
        self.autoDeleteUnConfiguredYTCard = SwitchSettingCard(
            FIF.DELETE,
            "自动删除未配置月台",
            "在设备配置文件未完全完善前尽量不要开启",
            configItem=None,
            parent=self.epwGroup,
        )

        # 下载录像
        self.dvwGroup = SettingCardGroup("下载录像", self.scrollWidget)
        self.checkVideoExistedCard = SwitchSettingCard(
            FIF.SEARCH,
            "下载录像前检查录像是否存在",
            "由于某些厂商SDK没有提供异步查询，如果开启本功能后可能导致每个文件下载时长提高500ms左右，但可提供更为详细的下载记录（不建议启用此选项）",
            configItem=None,
            parent=self.dvwGroup,
        )
        self.autoConvertFormatCard = SwitchSettingCard(
            FIF.IMAGE_EXPORT,
            "自动转换格式",
            "在程序下载结束之后会自动执行一次文件格式转换",
            configItem=None,
            parent=self.dvwGroup,
        )

        # 标记图片
        self.ppwGroup = SettingCardGroup("标记图片", self.scrollWidget)
        self.colLabelNumCard = CustomCompactSpinBoxSettingCard(
            FIF.LAYOUT,
            "每行显示的图片数量",
            "最少1个，最大6个",
            minNum=1,
            maxNum=6,
            parent=self.ppwGroup,
        )
        self.penShapeCard = CustomComboBoxSettingCard(
            FIF.EDIT,
            "画笔形状",
            "标记时的默认画笔形状",
            texts=["圆形", "矩形"],
            parent=self.ppwGroup,
        )
        self.penWidthCard = CustomSpinBoxSettingCard(
            FIF.UNIT,
            "画笔宽度",
            "标记时的默认画笔宽度,最小为1，最大为100",
            minNum=1,
            maxNum=100,
            parent=self.ppwGroup,
        )
        self.penColorCard = CustomOptionsSettingCard(
            FIF.BACKGROUND_FILL,
            "画笔颜色",
            "标记时的默认画笔颜色",
            texts=["红色", "绿色", "蓝色", "黄色", "紫色", "黑色", "白色"],
            parent=self.ppwGroup,
        )

        # 软件更新
        self.updateSoftwareGroup = SettingCardGroup("软件更新", self.scrollWidget)
        self.updateOnStartUpCard = SwitchSettingCard(
            FIF.UPDATE,
            "在应用程序启动时检查更新",
            "新版本将更加稳定并拥有更多功能（建议启用此选项）",
            configItem=None,
            parent=self.updateSoftwareGroup,
        )

        # 关于
        self.aboutGroup = SettingCardGroup("关于", self.scrollWidget)
        self.helpCard = HyperlinkCard(
            HELP_URL,
            "打开帮助页面",
            FIF.HELP,
            "教程",
            "发现新功能并了解有关 ATO 的使用技巧",
            self.aboutGroup,
        )
        self.feedbackCard = PrimaryPushSettingCard(
            "提供反馈",
            FIF.FEEDBACK,
            "提供反馈",
            "通过提供反馈帮助我们改进 ATO",
            self.aboutGroup,
        )
        self.aboutCard = PrimaryPushSettingCard(
            "检查更新",
            FIF.INFO,
            "关于",
            f"© 版权所有 {YEAR}, {AUTHOR}. 当前版本 {VERSION}",
            self.aboutGroup,
        )
        self.__initWidget()  # 初始化组件
        self.__connectSignalToSlot()  # 链接组件信号到槽函数

    def __initWidget(self):
        # 初始化组件
        self.resize(1000, 800)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 120, 0, 20)  # 设置视窗边距
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)

        theme = "light"
        hlPath = PROJECT_ROOT_PATH / "app_setting_widget"
        with open(
            f"{str(hlPath)}/resource/qss/{theme}/setting_interface.qss",
            encoding="utf-8",
        ) as f:
            self.setStyleSheet(f.read())

        self.__initLayout()  # 初始化布局

    def __initLayout(self):
        # 初始化布局
        self.settingLabel.move(60, 63)
        self.epwGroup.addSettingCard(self.autoDeleteUnConfiguredYTCard)

        self.dvwGroup.addSettingCard(self.checkVideoExistedCard)
        self.dvwGroup.addSettingCard(self.autoConvertFormatCard)

        self.ppwGroup.addSettingCard(self.colLabelNumCard)
        self.ppwGroup.addSettingCard(self.penShapeCard)
        self.ppwGroup.addSettingCard(self.penWidthCard)
        self.ppwGroup.addSettingCard(self.penColorCard)

        self.updateSoftwareGroup.addSettingCard(self.updateOnStartUpCard)

        self.aboutGroup.addSettingCard(self.helpCard)
        self.aboutGroup.addSettingCard(self.feedbackCard)
        self.aboutGroup.addSettingCard(self.aboutCard)

        # add setting card group to layout
        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(60, 10, 60, 0)
        self.expandLayout.addWidget(self.epwGroup)
        self.expandLayout.addWidget(self.dvwGroup)
        self.expandLayout.addWidget(self.ppwGroup)
        self.expandLayout.addWidget(self.updateSoftwareGroup)
        self.expandLayout.addWidget(self.aboutGroup)

    def __connectSignalToSlot(self):
        # 链接组件信号到槽函数
        self.feedbackCard.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl(FEEDBACK_URL))
        )
        # self.autoDeleteUnConfiguredYTCard.checkedChanged.connect()
        # self.updateOnStartUpCard.checkedChanged.connect()
        pass

    def __initSettingCardWidgetValue(self):
        # 主题作者将settingCard的数值初始化指定为了他自己实现的QConfig
        # 我暂时不想用他那个，他那个json的格式，可能还不能加注释！
        # 所有组件初始化要我自己对接，比如我需要手动在这里设置SwitchButton的Value
        pass


if __name__ == "__main__":
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_DontCreateNativeWidgetSiblings)

    w = SettingInterface()
    w.show()

    app.exec_()
