import argparse
import os
import shutil
import signal

from SRM import monitor


# 设定信号捕获
def onSignalInterHandler(signum, frame):
    global is_running_flag
    print("正在停止...(整理数据中，可能需要等待一段时间)")
    is_running_flag = False


if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-o", "--output", type=str,
                           help="输出位置", required=False, default="./output")
    argparser.add_argument("-i", "--interval", type=int,
                           help="监听时间间隔(毫秒)", required=False, default=5000)
    argparser.add_argument("-f", "--filter", nargs='*',
                           help="限制监听范围，为进程名(如explorer.exe)", default=[])

    args = argparser.parse_args()

    shutil.rmtree(args.output, ignore_errors=True)

    # 输出系统信息
    monitor.showSystemInfo()
    # 启动监听
    sys_monitor = monitor.SysMonitor()
    is_running_flag = True

    signal.signal(signal.SIGINT, onSignalInterHandler)

    # 开启监听线程（fake线程）
    sys_monitor.start(args.interval, args.filter)
    print("\n正在监听... 键盘敲击[Ctrt+c]即可结束统计...")
    while is_running_flag:
        import time

        time.sleep(1)

    sys_monitor.stop()
    print("监听已停止...正在导出数据...")
    sys_monitor.export(args.output)

    print("结果输出到：", os.path.abspath(args.output))
