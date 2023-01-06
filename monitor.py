import psutil
import common
import threading
import time
from collections import defaultdict
import datetime
import exporter
import platform


def showSystemInfo():
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()

    print("======== CPU =======")
    print("CPU 核心数: %d" % psutil.cpu_count(logical=False))
    print("CPU 线程数: %d" % psutil.cpu_count())
    print()
    print("======== MEM =======")
    print("总计内存  : %0.2f GB" % common.trans_B2GB(mem.total))
    print("已用内存  : %0.2f GB" % common.trans_B2GB(mem.used))
    print("可用内存  : %0.2f GB" % common.trans_B2GB(mem.available))

    if platform.system() != "Windows":
        print()
        print("======== SWAP =======")
        print("交换空间  : %0.2f GB" % common.trans_B2GB(swap.total))
        print("已用空间  : %0.2f GB" % common.trans_B2GB(swap.used))
        print("可用空间  : %0.2f GB" % common.trans_B2GB(swap.free))


class ProcessMonitor:
    '''
    进程监视器，根据进程名归并，即将子进程并入父进程计算
    '''

    def __init__(self, process_name: str) -> None:
        self.__process_name = process_name
        self.__pids = []
        self.__is_running = False
        self.__thread = None
        self.__interval = 10000  # 默认10秒一次
        self.__thread = threading.Thread(target=self.__monitorThread)

        # 统计信息
        self.__statistic = {}
        self.__clearStatistic()

    def start(self, interval):
        # print("start")
        self.__is_running = True
        self.__interval = interval
        self.__thread.start()

    def stop(self):
        self.__is_running = False

    def wait(self):
        self.__thread.join()

    def setPidSet(self, pids: set):
        self.__pids = pids

    def getStatistic(self):
        return self.__statistic

    def __monitorThread(self):
        while(self.__is_running):
            pid_num = 0
            cpu_loaded = 0.0
            mem = 0.0
            io = 0.0

            for pid in self.__pids:
                # TODO 丑陋的代码优化
                try:
                    process = psutil.Process(pid=pid)
                    if(process.name() != self.__process_name):
                        # 认为pid被复用了
                        continue
                except psutil.NoSuchProcess as e:
                    continue
                pid_num += 1
                # 合并统计各个信息
                cpu_loaded += process.cpu_percent()
                mem += common.trans_B2MB(process.memory_info().rss)
                io += common.trans_B2MB(process.io_counters().write_bytes)

            if pid_num == 0:
                # 所有都结束了
                self.__statistic["END_TIME"] = datetime.datetime.now()
                self.__pids.clear()

            self.__recordStat(cpu_loaded, mem, io)
            time.sleep(self.__interval/1000)

    def __clearStatistic(self):
        self.__statistic.clear()
        self.__statistic["Time"] = []
        self.__statistic["CPU"] = []
        self.__statistic["MEM"] = []
        self.__statistic["IO"] = []
        self.__statistic["START_TIME"] = datetime.datetime.now()
        self.__statistic["END_TIME"] = None

    def __recordStat(self, cpu, mem, io):
        self.__statistic["Time"].append(datetime.datetime.now())
        self.__statistic["CPU"].append(cpu)
        self.__statistic["MEM"].append(mem)
        self.__statistic["IO"].append(io)


class SysMonitor:
    def __init__(self) -> None:
        self.__is_running = False
        self.__interval = 1000
        self.__thread = None
        self.__process_map = defaultdict(ProcessMonitor)  # 存放各种进程管理器

    def start(self, interval, filter=set()):
        self.__is_running = True
        self.__interval = interval
        self.__thread = threading.Thread(
            target=self.__threadFunc, args=(set(filter),))
        self.__thread.start()

    def export(self, data_path):
        import os
        os.makedirs(data_path, exist_ok=True)
        exporter.export(self.__process_map, data_path)

    def stop(self):
        self.__is_running = False
        self.__thread.join()

    def __threadFunc(self, filter):
        '''
        子线程函数，用于扫描系统所有的进程，并且归类。再将进程分发给子进程进行监听
        '''
        # 开启子进程
        while(self.__is_running):
            for process_name, ids in self.__getProcessesInfo().items():
                if(len(filter) > 0 and process_name not in filter):
                    continue
                self.__distributeProcessName(process_name, ids)

            time.sleep(self.__interval/1000)

        # 取消所有线程和子进程
        for _, pm in self.__process_map.items():
            pm.stop()
        for _, pm in self.__process_map.items():
            pm.wait()

    def __getProcessesInfo(self):
        process_info = defaultdict(set)
        for pid in psutil.pids():
            try:
                process = psutil.Process(pid)
                process_info[process.name()].add(pid)
            except psutil.NoSuchProcess as e:
                print("warn:", pid, "has been exit")
                continue
        return process_info

    def __distributeProcessName(self, process_name: str, ids: set):
        if process_name not in self.__process_map:
            # 新的进程
            self.__process_map[process_name] = ProcessMonitor(process_name)
            self.__process_map.get(process_name).setPidSet(ids)
            self.__process_map[process_name].start(self.__interval)

        self.__process_map.get(process_name).setPidSet(ids)

    def __processMonitorFunc(self):
        while(self.__is_running):
            pass
        # 取消所有监听
