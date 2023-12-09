def is_instance_variables_has_empty(instance):
    # 判断类实例的变量有没有空的。excel中，只要用户操作过这个单元格再删除，就算是空的也会返回"None"
    for attr_name in dir(instance):
        if not attr_name.startswith('__'):  # 排除掉Python内置的特殊方法或属性
            attr_value = getattr(instance, attr_name)
            if attr_value is None or attr_value == "" or attr_value == "None":
                return True
    return False
