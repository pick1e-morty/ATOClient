# 做一个月台配置模板

# 查找录像的问题

海康第一个总是查半天的，哦，把find关了就好了(开玩笑的哈)
大华是错误，network_error
不行呀，关了查找，下载还是network_error,看来跟find没关系啊

# 装饰器改造

下载器里的execute_operation可以改造为一个装饰器，不过要重新包装一边类方法。
等未来想对下载器提速(StopDownloadHandleThread的优化空间很大)的时候，
可以先把函数改造为一个类，上面那个装饰器也就是顺手的事了

# 冗余的生成器

## app/utils/dev_config.py生成器这层好像冗余了，本来就是个字典，传key拿值嘛。

# 性能优化

app/picture_process_widget/ppw.py delUnMarkImg方法
可以查layout所有的label，遍历label的filePath属性，不在walk的新文件列表中就给removeWidget了
不过没必要呀，能省几个内存呢

# 资源存放优化

app/picture_process_widget/utils/writeable_label.py markImgFilePath
这个用于标记的图片暂时先不放入qrc中，我现在就这一个图片文件，
另外pyinstaller也会对资源文件进行一次包装加密什么的，
而且我有预感，我后面还要加图片，来回的套这个qrc是很繁琐的。

# 日志优化

netsdk日志文件名要用ip来表示，不然log根本没法看

# 下载优化

# 可以选择下载前不查询录像是否存在，默认是关闭的就好

# appdata中的资源文件的合并

首先是AppData要向上提一级
要在ato的root根目录下
