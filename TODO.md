# 做一个月台配置模板

# 下载录像
## 海康第一个总是查半天的，哦，把find关了就好了(开玩笑的哈)
## 大华是错误，network_error

# 装饰器改造
## 下载器里的execute_operation可以改造为一个装饰器，不过要重新包装一边类方法。
## 等未来想对下载器提速的时候，可以先把函数改造为一个类，上面那个装饰器也就是顺手的事了


# 冗余的生成器
## app/utils/dev_config.py生成器这层好像冗余了，本来就是个字典，传key拿值嘛。


# 性能优化
## app/picture_process_widget/ppw.py         delUnMarkImg方法
## 可以查layout所有的label，遍历label的filePath属性，不在walk的新文件列表中就给removeWidget了
## 不过没必要呀，能省几个内存呢