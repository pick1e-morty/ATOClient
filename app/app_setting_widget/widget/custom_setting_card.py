from typing import Union

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QLabel, QButtonGroup
from qfluentwidgets import (
    SettingCard,
    FluentIconBase,
    ComboBox,
    ExpandSettingCard,
    RadioButton,
    SpinBox,
    CompactSpinBox,
)


class CustomComboBoxSettingCard(SettingCard):
    """Setting card with a combo box"""

    # 所有的SettingCard都只负责发信号，具体到修改配置文件时全部统一到上层
    valueChanged = pyqtSignal(str)

    def __init__(
        self,
        icon: Union[str, QIcon, FluentIconBase],
        title,
        content=None,
        texts=None,
        parent=None,
    ):
        """
        Parameters
        ----------
        icon: str | QIcon | FluentIconBase
            the icon to be drawn

        title: str
            the title of card

        content: str
            the content of card

        texts: List[str]
            the text of items

        parent: QWidget
            parent widget
        """
        super().__init__(icon, title, content, parent)
        self.comboBox = ComboBox(self)
        self.hBoxLayout.addWidget(self.comboBox, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)
        for text in texts:
            self.comboBox.addItem(text)
        self.comboBox.setCurrentIndex(0)
        self.comboBox.currentIndexChanged.connect(self._onCurrentIndexChanged)

    def _onCurrentIndexChanged(self, index: int):
        """emit valueChanged signal"""
        self.valueChanged.emit(self.comboBox.currentText())


class CustomOptionsSettingCard(ExpandSettingCard):
    # TODO 这个暂时不能用哈，特别乱。记得用那个data，直接给上层发Qt.red这种数据，这样上层就不用做冗余判断了
    """setting card with a group of options"""

    optionChanged = pyqtSignal(str)

    def __init__(
        self,
        icon: Union[str, QIcon, FluentIconBase],
        title,
        content=None,
        texts=None,
        parent=None,
    ):
        """
        Parameters
        ----------
        icon: str | QIcon | FluentIconBase
            the icon to be drawn

        title: str
            the title of setting card

        content: str
            the content of setting card

        texts: List[str]
            the texts of radio buttons

        parent: QWidget
            parent window
        """
        super().__init__(icon, title, content, parent)
        self.texts = texts or []
        self.choiceLabel = QLabel(self)
        self.buttonGroup = QButtonGroup(self)

        self.addWidget(self.choiceLabel)

        # create buttons
        self.viewLayout.setSpacing(19)
        self.viewLayout.setContentsMargins(48, 18, 0, 18)

        button = None

        for text in texts:
            button = RadioButton(text, self.view)
            self.buttonGroup.addButton(button)
            self.viewLayout.addWidget(button)

        self._adjustViewSize()
        button.setChecked(True)
        self.choiceLabel.setText(button.text())
        self.choiceLabel.adjustSize()
        self.buttonGroup.buttonClicked.connect(self.__onButtonClicked)

    def __onButtonClicked(self, button: RadioButton):
        """button clicked slot"""
        if button.text() == self.choiceLabel.text():
            return

        self.choiceLabel.setText(button.text())
        self.choiceLabel.adjustSize()
        self.optionChanged.emit(button.text())


class CustomSpinBoxSettingCard(SettingCard):
    """Setting card with a spin box"""

    valueChanged = pyqtSignal(int)

    def __init__(
        self,
        icon: Union[str, QIcon, FluentIconBase],
        title,
        content=None,
        minNum=0,
        maxNum=100,
        parent=None,
    ):
        super().__init__(icon, title, content, parent)
        self.spinBox = SpinBox(self)
        self.spinBox.setAccelerated(True)
        self.hBoxLayout.addWidget(self.spinBox, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)
        self.spinBox.setRange(minNum, maxNum)
        self.spinBox.valueChanged.connect(self._onValueChanged)

    def _onValueChanged(self, value: int):
        """emit valueChanged signal"""
        self.valueChanged.emit(value)


class CustomCompactSpinBoxSettingCard(SettingCard):
    """Setting card with a spin box"""

    valueChanged = pyqtSignal(int)

    def __init__(
        self,
        icon: Union[str, QIcon, FluentIconBase],
        title,
        content=None,
        minNum=0,
        maxNum=100,
        parent=None,
    ):
        super().__init__(icon, title, content, parent)
        self.compactSpinBox = CompactSpinBox(self)
        self.compactSpinBox.setAccelerated(True)
        self.hBoxLayout.addWidget(self.compactSpinBox, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)
        self.compactSpinBox.setRange(minNum, maxNum)
        self.compactSpinBox.valueChanged.connect(self._onValueChanged)

    def _onValueChanged(self, value: int):
        """emit valueChanged signal"""
        self.valueChanged.emit(value)
