import threading

from loguru import logger


class StatusReportThread(threading.Thread):
    # 状态上报的线程
    """
    downloadResultList是一个进程通信的列表，是由mulutiprocess.manager.list创建的代理对象。
    downloadResultListCondition顾名思义就是保证的downloadResultList操作同步的condition。
    因为我开了多个进程，所以downloadResultListCondition会非常抢手，所以我有创建了一个statusReportList，作为临时的 数据发送缓冲区。
    相比较downloadResultListCondition时statusReportListCondition是更容易拿到的。 这样在子进程中的阻塞时间就会减少，对吗？你觉得我这个思路是对的吗？可取吗？有没有更好的思路？



    本来这个类是没必要存在的，但是那个线程的getName貌似没有更好的办法了
    当然，尽早统一，对项目结构更好
    """

    def __init__(self, statusReportList, statusReportListCondition, downloadResultList, downloadResultListCondition):
        super().__init__()
        self.downloadResultList = downloadResultList  # 进程通信的list
        self.downloadResultListCondition = downloadResultListCondition

        self.statusReportList = statusReportList  # 线程同步的列表
        self.statusReportListCondition = statusReportListCondition  # 线程同步的condition

        self.producerDone = False  # 线程可以结束了的标志

    def setDone(self):
        # 生产者发出完毕信号，也就是主线程那边下载句柄传完了
        self.producerDone = True

    def run(self):

        while True:
            with self.statusReportListCondition:  # 这个锁只是为了 检空 的等待
                if not self.statusReportList:
                    if self.producerDone is True:  # 状态列表是空的，且 状态生成结束标志 为真，就说明可以结束了
                        logger.info(f"{self.getName()}的statusReportThread子线程正常关闭")
                        break
                    self.statusReportListCondition.wait()  # 列表是空的，但状态生成结束标志为假，则线程阻塞等待，不消耗资源，没有sleep

            with self.downloadResultListCondition:  # 上面那个wait被解锁后，就说明已经有状态要发送了
                with self.statusReportListCondition:  # 然后开始拿大锁，再拿小锁(小锁应该好拿，也要确保同步)
                    self.downloadResultList.extend(self.statusReportList)  # statusReportList的结构[widgetEnum, deviceAddress, f_iNDEX, f_status]
                    self.statusReportList.clear()
                    self.downloadResultListCondition.notify()

