from UnifyNetSDK import HaikangNetSDK, DaHuaNetSDK

dahua1 = DaHuaNetSDK()
dahua2 = DaHuaNetSDK()
print(dahua1 is dahua2)

haikang1 = HaikangNetSDK()
haikang2 = HaikangNetSDK()
print(haikang1 is haikang2)

import importlib


def get_class_names_in_module(module_name):
    class_names = []
    try:
        module = importlib.import_module(module_name)
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if isinstance(attr, type) and attr.__module__ == module_name and attr_name != "SingletonType":
                classinstance_1 = attr()
                classinstance_2 = attr()
                if not (classinstance_1 is classinstance_2):
                    print(f"{attr_name} not a singleton class")  # 只有模块中的类不是单例类才会被打印出来
                class_names.append(attr_name)
    except ImportError:  #
        print("无法找到指定的模块:", module_name)
    print(class_names)


get_class_names_in_module("UnifyNetSDK.parameter")
