# downloader的主流程抽象

两个downloader的框架已经成型了，目前只有stopdownloadThread需要高度定制。
主要的流程可以做个基类了

# 冗余的生成器

## app/utils/dev_config.py生成器这层好像冗余了，本来就是个字典，传key拿值嘛。

# 性能优化

app/picture_process_widget/ppw.py delUnMarkImg方法
可以查layout所有的label，遍历label的filePath属性，不在walk的新文件列表中就给removeWidget了
不过没必要呀，能省几个内存呢

# 日志优化

netsdk日志文件名要用ip来表示，不然log根本没法看

# 下载优化

1 可以选择下载前不查询录像是否存在，默认是关闭的就好
2 dvr吞下载句柄的问题
3 同时开六个紫禁城，其中有一个紫禁城并不进行下载，好像是因为他抢不到通信的权限，然后就阻塞在那里了
这个问题特别显眼的严重，我准备在子进程里开一个缓冲的list，通讯归通讯，下载归下载
那子进程里还要开一个线程是专门用来跟父进程通信的，
最高级的共享内存，次一点的queue，不过我现在打算先给一个子线程list缓冲区

# 多进程优化

    调试模式下，退出程序时报错
    Error in atexit._run_exitfuncs:
    Traceback (most recent call last):
      File "C:\Users\Administrator\AppData\Local\miniconda3\envs\ato\lib\concurrent\futures\process.py", line 102, in _python_exit
        thread_wakeup.wakeup()
      File "C:\Users\Administrator\AppData\Local\miniconda3\envs\ato\lib\concurrent\futures\process.py", line 90, in wakeup
        self._writer.send_bytes(b"")
      File "C:\Users\Administrator\AppData\Local\miniconda3\envs\ato\lib\multiprocessing\connection.py", line 183, in send_bytes
        self._check_closed()
      File "C:\Users\Administrator\AppData\Local\miniconda3\envs\ato\lib\multiprocessing\connection.py", line 136, in _check_closed
        raise OSError("handle is closed")
    OSError: handle is closed
    
    AI说
    
    这段错误提示表明在Python进程退出时，由于某些原因，与进程间通信（IPC）相关的管道或连接已经被关闭，而在atexit注册的退出函数试图访问已被关闭的管道，从而引发了OSError: handle is closed错误。
    
    根据报错信息，问题发生在concurrent.futures.process模块以及multiprocessing.connection模块，这两个模块常用于跨进程通信。在PyQt5应用中，如果您使用了多进程或多线程结合concurrent.futures或multiprocessing，当主窗口关闭（即主线程结束）时，可能没有正确地关闭或清理这些子进程或子线程。
    
    为了避免这种错误，您可以尝试以下方法：
    
    确保在关闭应用程序前正确关闭所有子进程/线程：在关闭窗口之前，显式地取消或结束所有由concurrent.futures.ProcessPoolExecutor或multiprocessing.Pool创建的子进程，并等待它们结束。
    
    使用with语句管理进程池和相关资源：通过with语句可以确保在离开作用域时自动关闭和清理资源。
    
    监听窗口关闭事件并做相应清理工作：在PyQt5中，可以重写QMainWindow.closeEvent方法来捕获窗口关闭事件，并在此事件处理器中执行必要的清理操作。
    
    在所有子线程，子进程，进程通讯器关闭后我都有做log，所以我想应该不是代码的问题吧？
    难道是调试模式的问题？开下面这个全局的except，再跑正常模式看看能不能抓到这个 OSError
    https://github.com/MCSLTeam/MCSL2/blob/10f367beaecb52c903022b72cfb7f28cdbf253d7/MCSL2Lib/windowInterface.py#L352C9-L352C24

# 软件更新的优化

requests.get没有开多线程，不过有超时两秒
还有这个更新提示的 窗口显示节点 很奇怪，我觉得应该把checkUpdate放到splashScreen里面去做

# EPW的UI显示功能提升

在单号角度和月台角度的 表格列头中显示单号数量。ui的接口写好了但是没生效，在这个文件中app/esheet_process_widget/UI/table_widget.py

