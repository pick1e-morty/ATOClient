from bisect import bisect_left
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableWidgetItem, QTableWidget
import shutil
from pathlib import Path


def is_instance_variables_has_empty(instance):
    # 判断类实例的变量有没有空的。excel中，只要用户操作过这个单元格再删除，就算是空的也会返回"None"
    for attr_name in dir(instance):
        if not attr_name.startswith('__'):  # 排除掉Python内置的特殊方法或属性
            attr_value = getattr(instance, attr_name)
            if attr_value is None or attr_value == "" or attr_value == "None":
                return True
    return False


def is_empty(var):
    # 有时候也需要只判断一个变量是否为空值
    if var is None or var == "" or var == "None":
        return True
    return False


def findItemTextInTableWidgetRow(tableWidget: QTableWidget, itemText: str, col: int = 0) -> [int, bool]:
    """
    表格组件。要查找的item文本。要排序的列，默认是第一列
    用于更新tabelwidget同行项目其他列中的数据
    因为功能目标唯一性，速度肯定比QTabeleWidget.findItems的遍历整个表格速度快很多
    返回的第一值是行数
    返回的第二值是行是否已经存在
    """
    if tableWidget.rowCount():  # 如果表格不是空行
        textInColDict = {}
        for i in range(tableWidget.rowCount()):
            tableWidgetItem = tableWidget.item(i, col)
            if tableWidgetItem is not None:
                text = tableWidgetItem.text()
                textInColDict[text] = i
        if itemText in textInColDict.keys():  # 取出整列的数据
            row = textInColDict[itemText]  # 先查 文本是否已经存在
            return row, True
        else:
            itemTextList = list(textInColDict.keys())  # 如果不存在
            itemTextList.append(itemText)
            itemTextList.sort()  # 就找到这个 文本 按照顺序所应该存在的位置(行)
            row = itemTextList.index(itemText)
            tableWidget.insertRow(row)
    else:
        row = 0
        tableWidget.insertRow(row)
    return row, False


class AlignCenterQTableWidgetItem(QTableWidgetItem):
    # 目前对tabelwidgetItem没什么特殊的要求，就是每次都要做水平垂直居中。次数太多了，就开个类吧
    def __init__(self, *args):
        super().__init__(*args)
        self.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)


def removeDir(dir_path: [str, Path]):
    # 删除指定目录下的所有文件和子目录，但保留目录本身
    dir_path = Path(dir_path)
    if dir_path.exists() and dir_path.is_dir():  # 检查目录是否存在
        # 遍历目录中的所有文件和子目录
        for item in dir_path.iterdir():
            if item.is_dir():
                # 使用shutil.rmtree删除子目录及其内容
                shutil.rmtree(str(item))
            else:
                # 删除文件
                item.unlink()
