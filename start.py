# -*- coding: UTF-8 -*-

import argparse
import os
import shutil
import signal

from SRM import monitor, mail


def argParser():
    """
    Set the argument parser
    """

    argparser = argparse.ArgumentParser()

    argparser.add_argument("-o", "--output", type=str,
                           help="输出位置", required=False, default="./output")
    argparser.add_argument("-i", "--interval", type=int,
                           help="监听时间间隔(毫秒)", required=False, default=5000)
    argparser.add_argument("-f", "--filter", nargs='*',
                           help="限制监听范围，为进程名(如explorer.exe)", default=[])

    # args for mailing
    argparser.add_argument("-m", "--mail", type=bool,
                           help="是否发送邮件通知", default=False)
    argparser.add_argument("-a", "--address", type=str,
                           help="邮件发送方地址", default='')
    argparser.add_argument("-n", "--name", type=str,
                           help="邮件发送方名称", default='no_reply')
    argparser.add_argument("-p", "--password", type=str,
                           help="邮件发送方密钥", default='')
    argparser.add_argument("-r", "--receiver", type=str,
                           help="邮件接收方地址", default='')

    return argparser.parse_args()


# 设定信号捕获
def onSignalInterHandler(signum, frame):
    global is_running_flag
    print("Stopping...")
    print("Data handling in progress, please wait for a while...")
    is_running_flag = False


if __name__ == '__main__':

    # Calling the parser to set inputs
    args = argParser()

    shutil.rmtree(args.output, ignore_errors=True)

    # 输出系统信息
    monitor.showSystemInfo()
    # 启动监听
    sys_monitor = monitor.SysMonitor()
    is_running_flag = True

    signal.signal(signal.SIGINT, onSignalInterHandler)

    # 开启监听线程（fake线程）
    sys_monitor.start(args.interval, args.filter)
    print("\n正在监听... 键盘敲击[CTRL+C]即可结束监听并进行统计...")
    while is_running_flag:
        import time

        time.sleep(1)

    sys_monitor.stop()
    print("监听已停止...正在导出数据...")
    sys_monitor.export(args.output)

    print("结果输出到：", os.path.abspath(args.output))

    # 设置邮件通知系统
    mail.MAIL(args).mail()


